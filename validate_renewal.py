# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
RENEWAL VALIDATION
v0.1
============================================================

Prod. By Ufuk Akdoğan

Gerçek audio-to-audio renewal sonrasında kaynak ve üretilen
kaydı karşılaştırır.

Kontrol eder:
- dosya geçerliliği
- süre
- sample rate
- kanal sayısı
- clipping
- silence
- RMS / peak
- enerji
- BPM yaklaşımı
- kaynak/çıktı süre farkı
- kaynak korunumu

BU DOSYA:
- audio üretmez
- generation başlatmaz
- fake/procedural audio üretmez
"""

from __future__ import annotations

import json
import math
import sys
import wave

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional


# ============================================================
# CONSTANTS
# ============================================================

VERSION = "0.1"

CLIP_THRESHOLD = 0.999

SILENCE_RMS_THRESHOLD = 0.001

MAX_DURATION_ERROR_SECONDS = 2.0

MIN_SOURCE_CORRELATION = 0.05

MIN_RENEWAL_SCORE = 0.25


# ============================================================
# ERRORS
# ============================================================

class RenewalValidationError(Exception):
    """Renewal validation temel hatası."""


# ============================================================
# METRICS
# ============================================================

@dataclass
class WavMetrics:

    path: str

    sample_rate: int

    channels: int

    frames: int

    duration_seconds: float

    rms: float

    peak: float

    clipping_ratio: float

    silence_ratio: float

    energy: float

    zero_crossing_rate: float

    mean: float

    dc_offset: float

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


@dataclass
class RenewalValidation:

    success: bool

    score: float

    source: WavMetrics

    renewed: WavMetrics

    duration_difference: float

    sample_rate_match: bool

    channel_match: bool

    duration_match: bool

    source_not_silent: bool

    renewed_not_silent: bool

    clipping_ok: bool

    energy_preserved: bool

    correlation: float

    warnings: list[str]

    errors: list[str]

    metadata: Dict[str, Any]

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


# ============================================================
# WAV READER
# ============================================================

class SimpleWavReader:

    def read(
        self,
        path: Path,
    ) -> tuple[
        int,
        int,
        int,
        list[float],
    ]:

        if not path.exists():

            raise RenewalValidationError(
                (
                    "WAV bulunamadı: "
                    f"{path}"
                )
            )

        if not path.is_file():

            raise RenewalValidationError(
                (
                    "WAV dosya değil: "
                    f"{path}"
                )
            )

        try:

            with wave.open(
                str(path),
                "rb",
            ) as wav:

                channels = (
                    wav.getnchannels()
                )

                sample_width = (
                    wav.getsampwidth()
                )

                sample_rate = (
                    wav.getframerate()
                )

                frames = (
                    wav.getnframes()
                )

                raw = wav.readframes(
                    frames
                )

        except Exception as exc:

            raise RenewalValidationError(
                (
                    "WAV okunamadı: "
                    f"{exc}"
                )
            ) from exc

        if channels <= 0:

            raise RenewalValidationError(
                "WAV channel değeri geçersiz."
            )

        if sample_rate <= 0:

            raise RenewalValidationError(
                "WAV sample rate geçersiz."
            )

        if sample_width not in (
            1,
            2,
            3,
            4,
        ):

            raise RenewalValidationError(
                (
                    "Desteklenmeyen sample width: "
                    f"{sample_width}"
                )
            )

        samples = (
            self._decode(
                raw,
                sample_width,
            )
        )

        # Stereo / multi-channel veriyi tek kanala indir.
        if channels > 1:

            mono: list[float] = []

            total_frames = len(samples) // channels

            for frame_index in range(
                total_frames
            ):

                start = (
                    frame_index
                    * channels
                )

                values = samples[
                    start:
                    start + channels
                ]

                mono.append(
                    sum(values)
                    / len(values)
                )

            samples = mono

        duration = (
            frames / sample_rate
        )

        return (
            sample_rate,
            channels,
            frames,
            samples,
        )

    def _decode(
        self,
        raw: bytes,
        sample_width: int,
    ) -> list[float]:

        if sample_width == 1:

            return [
                (
                    byte - 128
                )
                / 128.0
                for byte in raw
            ]

        if sample_width == 2:

            values: list[float] = []

            for index in range(
                0,
                len(raw) - 1,
                2,
            ):

                value = int.from_bytes(
                    raw[
                        index:
                        index + 2
                    ],
                    byteorder="little",
                    signed=True,
                )

                values.append(
                    value / 32768.0
                )

            return values

        if sample_width == 3:

            values = []

            for index in range(
                0,
                len(raw) - 2,
                3,
            ):

                b0 = raw[index]
                b1 = raw[index + 1]
                b2 = raw[index + 2]

                value = (
                    b0
                    | (b1 << 8)
                    | (b2 << 16)
                )

                if value & 0x800000:

                    value -= 1 << 24

                values.append(
                    value / 8388608.0
                )

            return values

        values = []

        for index in range(
            0,
            len(raw) - 3,
            4,
        ):

            value = int.from_bytes(
                raw[
                    index:
                    index + 4
                ],
                byteorder="little",
                signed=True,
            )

            values.append(
                value / 2147483648.0
            )

        return values


# ============================================================
# SIGNAL ANALYZER
# ============================================================

class SignalAnalyzer:

    def __init__(
        self,
        sample_limit: int = 250_000,
    ) -> None:

        self.sample_limit = max(
            10_000,
            int(
                sample_limit
            ),
        )

    def _reduce(
        self,
        samples: list[float],
    ) -> list[float]:

        if len(samples) <= self.sample_limit:

            return samples

        step = max(
            1,
            math.ceil(
                len(samples)
                / self.sample_limit
            ),
        )

        return samples[
            ::step
        ]

    def rms(
        self,
        samples: list[float],
    ) -> float:

        if not samples:
            return 0.0

        mean_square = (
            sum(
                sample * sample
                for sample in samples
            )
            / len(samples)
        )

        return math.sqrt(
            max(
                0.0,
                mean_square,
            )
        )

    def peak(
        self,
        samples: list[float],
    ) -> float:

        if not samples:
            return 0.0

        return max(
            abs(sample)
            for sample in samples
        )

    def clipping_ratio(
        self,
        samples: list[float],
    ) -> float:

        if not samples:
            return 0.0

        clipped = sum(
            1
            for sample in samples
            if abs(sample)
            >= CLIP_THRESHOLD
        )

        return (
            clipped
            / len(samples)
        )

    def silence_ratio(
        self,
        samples: list[float],
    ) -> float:

        if not samples:
            return 1.0

        silent = sum(
            1
            for sample in samples
            if abs(sample)
            <= SILENCE_RMS_THRESHOLD
        )

        return (
            silent
            / len(samples)
        )

    def mean(
        self,
        samples: list[float],
    ) -> float:

        if not samples:
            return 0.0

        return (
            sum(samples)
            / len(samples)
        )

    def zcr(
        self,
        samples: list[float],
    ) -> float:

        if len(samples) < 2:
            return 0.0

        crossings = 0

        previous = samples[0]

        for current in samples[1:]:

            if (
                (
                    previous < 0
                    and current >= 0
                )
                or
                (
                    previous >= 0
                    and current < 0
                )
            ):

                crossings += 1

            previous = current

        return (
            crossings
            / (len(samples) - 1)
        )

    def autocorrelation(
        self,
        samples: list[float],
        max_lag: int = 4000,
    ) -> float:

        if len(samples) < 2:
            return 0.0

        data = samples[
            : min(
                len(samples),
                self.sample_limit,
            )
        ]

        mean = (
            sum(data)
            / len(data)
        )

        centered = [
            value - mean
            for value in data
        ]

        energy = sum(
            value * value
            for value in centered
        )

        if energy <= 0:
            return 0.0

        lag = min(
            max_lag,
            len(centered) // 2,
        )

        best = 0.0

        for current_lag in range(
            1,
            lag,
            max(
                1,
                lag // 80,
            ),
        ):

            correlation = 0.0

            stop = (
                len(centered)
                - current_lag
            )

            for index in range(
                stop
            ):

                correlation += (
                    centered[index]
                    * centered[
                        index
                        + current_lag
                    ]
                )

            correlation /= energy

            if correlation > best:

                best = correlation

        return max(
            0.0,
            min(
                1.0,
                best,
            ),
        )

    def estimate_bpm(
        self,
        samples: list[float],
        sample_rate: int,
    ) -> Optional[float]:

        if (
            sample_rate <= 0
            or len(samples) < sample_rate
        ):

            return None

        data = self._reduce(
            samples
        )

        # Energy envelope.
        frame_size = max(
            256,
            int(
                sample_rate
                * 0.05
            ),
        )

        envelope: list[float] = []

        for start in range(
            0,
            len(data),
            frame_size,
        ):

            frame = data[
                start:
                start + frame_size
            ]

            if not frame:
                break

            energy = math.sqrt(
                sum(
                    x * x
                    for x in frame
                )
                / len(frame)
            )

            envelope.append(
                energy
            )

        if len(envelope) < 8:

            return None

        # Difference envelope.
        differences = [
            max(
                0.0,
                envelope[index]
                - envelope[index - 1],
            )
            for index in range(
                1,
                len(envelope),
            )
        ]

        if not differences:

            return None

        # Frame time is approximately 50 ms.
        frame_seconds = 0.05

        best_bpm = None
        best_score = -1.0

        # Turkish folk / dance practical range.
        for bpm in [
            float(value)
            for value in range(
                50,
                221,
                2,
            )
        ]:

            beat_interval = (
                60.0
                / bpm
            )

            lag = max(
                1,
                round(
                    beat_interval
                    / frame_seconds
                ),
            )

            if lag >= len(
                differences
            ):
                continue

            score = 0.0

            count = 0

            for index in range(
                lag,
                len(differences),
            ):

                score += (
                    differences[index]
                    * differences[
                        index - lag
                    ]
                )

                count += 1

            if count:

                score /= count

                if score > best_score:

                    best_score = score
                    best_bpm = bpm

        return best_bpm


# ============================================================
# METRIC BUILDER
# ============================================================

class MetricsBuilder:

    def __init__(
        self,
    ) -> None:

        self.reader = (
            SimpleWavReader()
        )

        self.analyzer = (
            SignalAnalyzer()
        )

    def build(
        self,
        path: Path,
    ) -> WavMetrics:

        (
            sample_rate,
            channels,
            frames,
            samples,
        ) = self.reader.read(
            path
        )

        reduced = (
            self.analyzer._reduce(
                samples
            )
        )

        rms = (
            self.analyzer.rms(
                reduced
            )
        )

        peak = (
            self.analyzer.peak(
                reduced
            )
        )

        clipping = (
            self.analyzer.clipping_ratio(
                reduced
            )
        )

        silence = (
            self.analyzer.silence_ratio(
                reduced
            )
        )

        mean = (
            self.analyzer.mean(
                reduced
            )
        )

        zcr = (
            self.analyzer.zcr(
                reduced
            )
        )

        energy = (
            rms * rms
        )

        return WavMetrics(
            path=str(
                path
            ),
            sample_rate=sample_rate,
            channels=channels,
            frames=frames,
            duration_seconds=(
                frames / sample_rate
            ),
            rms=rms,
            peak=peak,
            clipping_ratio=clipping,
            silence_ratio=silence,
            energy=energy,
            zero_crossing_rate=zcr,
            mean=mean,
            dc_offset=abs(
                mean
            ),
        )


# ============================================================
# CORRELATION
# ============================================================

class SourceCorrelation:

    def calculate(
        self,
        source: Path,
        renewed: Path,
        sample_limit: int = 120_000,
    ) -> float:

        reader = (
            SimpleWavReader()
        )

        _, _, _, source_samples = (
            reader.read(
                source
            )
        )

        _, _, _, renewed_samples = (
            reader.read(
                renewed
            )
        )

        if not source_samples:

            return 0.0

        if not renewed_samples:

            return 0.0

        limit = min(
            len(source_samples),
            len(renewed_samples),
            sample_limit,
        )

        if limit < 1000:

            return 0.0

        # Uniformly sample the two signals.
        source_step = (
            len(source_samples)
            / limit
        )

        renewed_step = (
            len(renewed_samples)
            / limit
        )

        x: list[float] = []
        y: list[float] = []

        for index in range(
            limit
        ):

            source_index = min(
                len(source_samples) - 1,
                int(
                    index
                    * source_step
                ),
            )

            renewed_index = min(
                len(renewed_samples) - 1,
                int(
                    index
                    * renewed_step
                ),
            )

            x.append(
                source_samples[
                    source_index
                ]
            )

            y.append(
                renewed_samples[
                    renewed_index
                ]
            )

        mean_x = (
            sum(x)
            / len(x)
        )

        mean_y = (
            sum(y)
            / len(y)
        )

        numerator = 0.0

        denominator_x = 0.0
        denominator_y = 0.0

        for index in range(
            len(x)
        ):

            dx = (
                x[index]
                - mean_x
            )

            dy = (
                y[index]
                - mean_y
            )

            numerator += (
                dx * dy
            )

            denominator_x += (
                dx * dx
            )

            denominator_y += (
                dy * dy
            )

        denominator = math.sqrt(
            denominator_x
            * denominator_y
        )

        if denominator <= 0:

            return 0.0

        return max(
            -1.0,
            min(
                1.0,
                numerator
                / denominator,
            ),
        )


# ============================================================
# VALIDATOR
# ============================================================

class RenewalValidator:

    def __init__(
        self,
    ) -> None:

        self.metrics = (
            MetricsBuilder()
        )

        self.correlation = (
            SourceCorrelation()
        )

    def validate(
        self,
        source: str | Path,
        renewed: str | Path,
    ) -> RenewalValidation:

        source_path = (
            Path(
                source
            )
            .expanduser()
            .resolve()
        )

        renewed_path = (
            Path(
                renewed
            )
            .expanduser()
            .resolve()
        )

        source_metrics = (
            self.metrics.build(
                source_path
            )
        )

        renewed_metrics = (
            self.metrics.build(
                renewed_path
            )
        )

        duration_difference = abs(
            source_metrics.duration_seconds
            - renewed_metrics.duration_seconds
        )

        sample_rate_match = (
            source_metrics.sample_rate
            == renewed_metrics.sample_rate
        )

        channel_match = (
            source_metrics.channels
            == renewed_metrics.channels
        )

        duration_match = (
            duration_difference
            <= MAX_DURATION_ERROR_SECONDS
        )

        source_not_silent = (
            source_metrics.rms
            > SILENCE_RMS_THRESHOLD
        )

        renewed_not_silent = (
            renewed_metrics.rms
            > SILENCE_RMS_THRESHOLD
        )

        clipping_ok = (
            renewed_metrics.clipping_ratio
            < 0.005
        )

        source_energy = max(
            1e-12,
            source_metrics.energy,
        )

        renewed_energy = (
            renewed_metrics.energy
        )

        energy_ratio = (
            renewed_energy
            / source_energy
        )

        energy_preserved = (
            0.20
            <= energy_ratio
            <= 5.0
        )

        correlation_value = (
            self.correlation.calculate(
                source_path,
                renewed_path,
            )
        )

        warnings: list[str] = []
        errors: list[str] = []

        # ----------------------------------------------------
        # WARNINGS
        # ----------------------------------------------------

        if not sample_rate_match:

            warnings.append(
                (
                    "Sample rate değişmiş: "
                    f"{source_metrics.sample_rate} -> "
                    f"{renewed_metrics.sample_rate}"
                )
            )

        if not channel_match:

            warnings.append(
                (
                    "Kanal sayısı değişmiş: "
                    f"{source_metrics.channels} -> "
                    f"{renewed_metrics.channels}"
                )
            )

        if not duration_match:

            errors.append(
                (
                    "Duration farkı fazla: "
                    f"{duration_difference:.2f}s"
                )
            )

        if not source_not_silent:

            errors.append(
                "Kaynak kayıt sessiz veya çok düşük."
            )

        if not renewed_not_silent:

            errors.append(
                "Renewal çıktısı sessiz veya çok düşük."
            )

        if not clipping_ok:

            errors.append(
                (
                    "Renewal çıktısında aşırı clipping: "
                    f"{renewed_metrics.clipping_ratio:.4f}"
                )
            )

        if not energy_preserved:

            warnings.append(
                (
                    "Enerji değişimi yüksek: "
                    f"ratio={energy_ratio:.3f}"
                )
            )

        if (
            correlation_value
            < MIN_SOURCE_CORRELATION
        ):

            warnings.append(
                (
                    "Kaynak/renewal waveform korelasyonu "
                    "çok düşük. Bu değer müziğin aynı kalmasını "
                    "tek başına kanıtlamaz."
                )
            )

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        score = 1.0

        if not sample_rate_match:
            score -= 0.10

        if not channel_match:
            score -= 0.10

        if not duration_match:
            score -= 0.35

        if not source_not_silent:
            score -= 0.25

        if not renewed_not_silent:
            score -= 0.25

        if not clipping_ok:
            score -= 0.30

        if not energy_preserved:
            score -= 0.15

        # Korelasyon yardımcı sinyaldir.
        if correlation_value > 0:

            correlation_bonus = min(
                0.10,
                correlation_value
                * 0.10,
            )

            score += correlation_bonus

        score = max(
            0.0,
            min(
                1.0,
                score,
            ),
        )

        # ----------------------------------------------------
        # FINAL
        # ----------------------------------------------------

        success = (
            score
            >= MIN_RENEWAL_SCORE
            and len(errors) == 0
        )

        metadata = {
            "source": str(
                source_path
            ),
            "renewed": str(
                renewed_path
            ),
            "energy_ratio": energy_ratio,
            "source_rms": source_metrics.rms,
            "renewed_rms": renewed_metrics.rms,
            "source_peak": source_metrics.peak,
            "renewed_peak": renewed_metrics.peak,
            "source_silence_ratio": (
                source_metrics.silence_ratio
            ),
            "renewed_silence_ratio": (
                renewed_metrics.silence_ratio
            ),
            "waveform_correlation": (
                correlation_value
            ),
            "real_audio": True,
            "fake_audio": False,
            "procedural_audio": False,
        }

        return RenewalValidation(
            success=success,
            score=round(
                score,
                4,
            ),
            source=source_metrics,
            renewed=renewed_metrics,
            duration_difference=round(
                duration_difference,
                4,
            ),
            sample_rate_match=sample_rate_match,
            channel_match=channel_match,
            duration_match=duration_match,
            source_not_silent=source_not_silent,
            renewed_not_silent=renewed_not_silent,
            clipping_ok=clipping_ok,
            energy_preserved=energy_preserved,
            correlation=round(
                correlation_value,
                5,
            ),
            warnings=warnings,
            errors=errors,
            metadata=metadata,
        )


# ============================================================
# REPORT
# ============================================================

def save_validation(
    validation: RenewalValidation,
    path: Path,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            validation.as_dict(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def print_validation(
    validation: RenewalValidation,
) -> None:

    print()
    print(
        "============================================================"
    )
    print(
        "MAVI AI STUDIO"
    )
    print(
        "RENEWAL VALIDATION"
    )
    print(
        "============================================================"
    )

    print(
        "STATUS : "
        + (
            "PASS"
            if validation.success
            else "REJECT"
        )
    )

    print(
        f"SCORE  : {validation.score:.4f}"
    )

    print(
        f"CORR   : {validation.correlation:.5f}"
    )

    print(
        f"TIME Δ : {validation.duration_difference:.3f}s"
    )

    print()

    print(
        "SOURCE"
    )

    print(
        f"  Duration : "
        f"{validation.source.duration_seconds:.2f}s"
    )

    print(
        f"  RMS      : "
        f"{validation.source.rms:.6f}"
    )

    print(
        f"  Peak     : "
        f"{validation.source.peak:.6f}"
    )

    print()

    print(
        "RENEWED"
    )

    print(
        f"  Duration : "
        f"{validation.renewed.duration_seconds:.2f}s"
    )

    print(
        f"  RMS      : "
        f"{validation.renewed.rms:.6f}"
    )

    print(
        f"  Peak     : "
        f"{validation.renewed.peak:.6f}"
    )

    print(
        f"  Clipping : "
        f"{validation.renewed.clipping_ratio:.6f}"
    )

    if validation.warnings:

        print()
        print(
            "WARNINGS"
        )

        for warning in validation.warnings:

            print(
                f"  - {warning}"
            )

    if validation.errors:

        print()
        print(
            "ERRORS"
        )

        for error in validation.errors:

            print(
                f"  - {error}"
            )

    print(
        "============================================================"
    )
    print()


# ============================================================
# CLI
# ============================================================

def build_parser() -> Any:

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Validate MAVI renewal output"
        )
    )

    parser.add_argument(
        "--source",
        required=True,
    )

    parser.add_argument(
        "--renewed",
        required=True,
    )

    parser.add_argument(
        "--result",
        default="",
    )

    return parser


def main() -> int:

    parser = (
        build_parser()
    )

    args = parser.parse_args()

    validator = (
        RenewalValidator()
    )

    try:

        validation = (
            validator.validate(
                source=args.source,
                renewed=args.renewed,
            )
        )

        print_validation(
            validation
        )

        if args.result:

            save_validation(
                validation,
                Path(
                    args.result
                ),
            )

        return (
            0
            if validation.success
            else 1
        )

    except Exception as exc:

        print()
        print(
            "RENEWAL VALIDATION ERROR"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )