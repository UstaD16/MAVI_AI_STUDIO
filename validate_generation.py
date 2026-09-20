# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
GENERATION VALIDATION
v0.1
============================================================

Prod. By Ufuk Akdoğan

Gerçek Stable Audio generation çıktısını doğrular.

Kontroller:
- WAV geçerliliği
- süre
- sample rate
- kanal sayısı
- dosya boyutu
- silence
- peak
- clipping
- RMS
- DC offset
- duration hedefi

Bu dosya:
- generation başlatmaz
- audio üretmez
- fake audio üretmez
- procedural audio üretmez
- placeholder audio üretmez
"""

from __future__ import annotations

import argparse
import json
import math
import wave

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List


# ============================================================
# CONSTANTS
# ============================================================

VERSION = "0.1"

CLIP_THRESHOLD = 0.999

SILENCE_SAMPLE_THRESHOLD = 0.001

MAX_DC_OFFSET = 0.03

MIN_RMS = 0.003

MIN_ACTIVE_RATIO = 0.08

DEFAULT_DURATION_TOLERANCE = 2.0


# ============================================================
# ERRORS
# ============================================================

class GenerationValidationError(
    Exception
):
    """Generation validation temel hatası."""


# ============================================================
# METRICS
# ============================================================

@dataclass
class GenerationMetrics:

    path: str

    valid: bool

    sample_rate: int

    channels: int

    sample_width: int

    frames: int

    duration_seconds: float

    file_size_bytes: int

    rms: float

    peak: float

    clipping_ratio: float

    silence_ratio: float

    active_ratio: float

    dc_offset: float

    zero_crossing_rate: float

    energy: float

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


@dataclass
class GenerationValidationResult:

    success: bool

    score: float

    output: GenerationMetrics

    target_seconds: float

    duration_difference: float

    duration_match: bool

    sample_rate_match: bool

    channels_valid: bool

    not_silent: bool

    clipping_ok: bool

    dc_ok: bool

    active_enough: bool

    errors: List[str]

    warnings: List[str]

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

class WavReader:

    def read(
        self,
        path: Path,
    ) -> tuple[
        int,
        int,
        int,
        int,
        int,
        bytes,
    ]:

        if not path.exists():

            raise GenerationValidationError(
                (
                    "Generation output bulunamadı: "
                    f"{path}"
                )
            )

        if not path.is_file():

            raise GenerationValidationError(
                (
                    "Generation output dosya değil: "
                    f"{path}"
                )
            )

        try:

            with wave.open(
                str(path),
                "rb",
            ) as wav:

                channels = wav.getnchannels()
                sample_width = wav.getsampwidth()
                sample_rate = wav.getframerate()
                frames = wav.getnframes()

                raw = wav.readframes(
                    frames
                )

        except Exception as exc:

            raise GenerationValidationError(
                (
                    "WAV açılamadı: "
                    f"{exc}"
                )
            ) from exc

        return (
            channels,
            sample_width,
            sample_rate,
            frames,
            len(raw),
            raw,
        )


# ============================================================
# PCM DECODER
# ============================================================

class PCMDecoder:

    def decode(
        self,
        raw: bytes,
        sample_width: int,
    ) -> List[float]:

        if not raw:

            return []

        if sample_width == 1:

            return [
                (
                    byte - 128
                )
                / 128.0
                for byte in raw
            ]

        if sample_width == 2:

            values: List[float] = []

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

                value = (
                    raw[index]
                    | (
                        raw[index + 1]
                        << 8
                    )
                    | (
                        raw[index + 2]
                        << 16
                    )
                )

                if value & 0x800000:

                    value -= (
                        1 << 24
                    )

                values.append(
                    value / 8388608.0
                )

            return values

        if sample_width == 4:

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

        raise GenerationValidationError(
            (
                "Desteklenmeyen sample width: "
                f"{sample_width}"
            )
        )


# ============================================================
# SIGNAL ANALYZER
# ============================================================

class SignalAnalyzer:

    def __init__(
        self,
        max_samples: int = 250_000,
    ) -> None:

        self.max_samples = max(
            10_000,
            int(
                max_samples
            ),
        )

    def reduce(
        self,
        samples: List[float],
    ) -> List[float]:

        if len(samples) <= self.max_samples:

            return samples

        step = max(
            1,
            math.ceil(
                len(samples)
                / self.max_samples
            ),
        )

        return samples[
            ::step
        ]

    def rms(
        self,
        samples: List[float],
    ) -> float:

        if not samples:

            return 0.0

        total = sum(
            value * value
            for value in samples
        )

        return math.sqrt(
            total
            / len(samples)
        )

    def peak(
        self,
        samples: List[float],
    ) -> float:

        if not samples:

            return 0.0

        return max(
            abs(value)
            for value in samples
        )

    def clipping_ratio(
        self,
        samples: List[float],
    ) -> float:

        if not samples:

            return 0.0

        clipped = sum(
            1
            for value in samples
            if abs(value)
            >= CLIP_THRESHOLD
        )

        return (
            clipped
            / len(samples)
        )

    def silence_ratio(
        self,
        samples: List[float],
    ) -> float:

        if not samples:

            return 1.0

        silent = sum(
            1
            for value in samples
            if abs(value)
            <= SILENCE_SAMPLE_THRESHOLD
        )

        return (
            silent
            / len(samples)
        )

    def active_ratio(
        self,
        samples: List[float],
    ) -> float:

        return max(
            0.0,
            min(
                1.0,
                1.0
                - self.silence_ratio(
                    samples
                ),
            ),
        )

    def mean(
        self,
        samples: List[float],
    ) -> float:

        if not samples:

            return 0.0

        return (
            sum(samples)
            / len(samples)
        )

    def zero_crossing_rate(
        self,
        samples: List[float],
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


# ============================================================
# METRICS BUILDER
# ============================================================

class MetricsBuilder:

    def __init__(
        self,
    ) -> None:

        self.reader = WavReader()

        self.decoder = PCMDecoder()

        self.analyzer = (
            SignalAnalyzer()
        )

    def build(
        self,
        path: Path,
    ) -> GenerationMetrics:

        (
            channels,
            sample_width,
            sample_rate,
            frames,
            raw_size,
            raw,
        ) = self.reader.read(
            path
        )

        if sample_rate <= 0:

            raise GenerationValidationError(
                "Sample rate geçersiz."
            )

        samples = (
            self.decoder.decode(
                raw,
                sample_width,
            )
        )

        reduced = (
            self.analyzer.reduce(
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

        active = (
            self.analyzer.active_ratio(
                reduced
            )
        )

        dc = abs(
            self.analyzer.mean(
                reduced
            )
        )

        zcr = (
            self.analyzer.zero_crossing_rate(
                reduced
            )
        )

        duration = (
            frames / sample_rate
        )

        return GenerationMetrics(
            path=str(
                path
            ),
            valid=True,
            sample_rate=sample_rate,
            channels=channels,
            sample_width=sample_width,
            frames=frames,
            duration_seconds=duration,
            file_size_bytes=path.stat().st_size,
            rms=rms,
            peak=peak,
            clipping_ratio=clipping,
            silence_ratio=silence,
            active_ratio=active,
            dc_offset=dc,
            zero_crossing_rate=zcr,
            energy=rms * rms,
        )


# ============================================================
# VALIDATOR
# ============================================================

class GenerationValidator:

    def __init__(
        self,
    ) -> None:

        self.metrics_builder = (
            MetricsBuilder()
        )

    def validate(
        self,
        output: str | Path,
        target_seconds: float,
        target_sample_rate: int = 48000,
        duration_tolerance: float = DEFAULT_DURATION_TOLERANCE,
    ) -> GenerationValidationResult:

        output_path = (
            Path(
                output
            )
            .expanduser()
            .resolve()
        )

        if target_seconds <= 0:

            raise GenerationValidationError(
                "Target duration geçersiz."
            )

        metrics = (
            self.metrics_builder.build(
                output_path
            )
        )

        duration_difference = abs(
            metrics.duration_seconds
            - float(
                target_seconds
            )
        )

        duration_match = (
            duration_difference
            <= float(
                duration_tolerance
            )
        )

        sample_rate_match = (
            metrics.sample_rate
            == int(
                target_sample_rate
            )
        )

        channels_valid = (
            metrics.channels
            in {
                1,
                2,
            }
        )

        not_silent = (
            metrics.rms
            >= MIN_RMS
            and metrics.active_ratio
            >= MIN_ACTIVE_RATIO
        )

        clipping_ok = (
            metrics.clipping_ratio
            <= 0.005
        )

        dc_ok = (
            metrics.dc_offset
            <= MAX_DC_OFFSET
        )

        errors: List[str] = []

        warnings: List[str] = []

        if not duration_match:

            errors.append(
                (
                    "Duration hedefle uyuşmuyor: "
                    f"hedef={target_seconds:.2f}s, "
                    f"çıktı={metrics.duration_seconds:.2f}s"
                )
            )

        if not sample_rate_match:

            warnings.append(
                (
                    "Sample rate hedefle uyuşmuyor: "
                    f"hedef={target_sample_rate}, "
                    f"çıktı={metrics.sample_rate}"
                )
            )

        if not channels_valid:

            errors.append(
                (
                    "Geçersiz kanal sayısı: "
                    f"{metrics.channels}"
                )
            )

        if not not_silent:

            errors.append(
                (
                    "Generation çıktısı sessiz veya "
                    "çok düşük seviyeli."
                )
            )

        if not clipping_ok:

            errors.append(
                (
                    "Aşırı clipping: "
                    f"{metrics.clipping_ratio:.6f}"
                )
            )

        if not dc_ok:

            warnings.append(
                (
                    "DC offset yüksek: "
                    f"{metrics.dc_offset:.6f}"
                )
            )

        if metrics.peak > 0.9999:

            warnings.append(
                (
                    "Peak 0 dBFS sınırına çok yakın."
                )
            )

        if metrics.silence_ratio > 0.92:

            warnings.append(
                (
                    "Çıktının büyük bölümü sessiz."
                )
            )

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        score = 1.0

        if not duration_match:
            score -= 0.30

        if not sample_rate_match:
            score -= 0.05

        if not channels_valid:
            score -= 0.20

        if not not_silent:
            score -= 0.35

        if not clipping_ok:
            score -= 0.30

        if not dc_ok:
            score -= 0.10

        score = max(
            0.0,
            min(
                1.0,
                score,
            ),
        )

        success = (
            len(errors) == 0
            and score >= 0.60
        )

        metadata = {
            "validation_version": VERSION,
            "target_seconds": (
                target_seconds
            ),
            "target_sample_rate": (
                target_sample_rate
            ),
            "duration_tolerance": (
                duration_tolerance
            ),
            "real_generation": True,
            "fake_audio": False,
            "procedural_audio": False,
            "placeholder_audio": False,
        }

        return GenerationValidationResult(
            success=success,
            score=round(
                score,
                4,
            ),
            output=metrics,
            target_seconds=float(
                target_seconds
            ),
            duration_difference=round(
                duration_difference,
                4,
            ),
            duration_match=duration_match,
            sample_rate_match=sample_rate_match,
            channels_valid=channels_valid,
            not_silent=not_silent,
            clipping_ok=clipping_ok,
            dc_ok=dc_ok,
            active_enough=(
                metrics.active_ratio
                >= MIN_ACTIVE_RATIO
            ),
            errors=errors,
            warnings=warnings,
            metadata=metadata,
        )


# ============================================================
# REPORT
# ============================================================

def save_result(
    result: GenerationValidationResult,
    path: Path,
) -> Path:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            result.as_dict(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return path


def print_result(
    result: GenerationValidationResult,
) -> None:

    print()
    print(
        "============================================================"
    )
    print(
        "MAVI AI STUDIO"
    )
    print(
        "GENERATION VALIDATION"
    )
    print(
        "============================================================"
    )

    print(
        "STATUS : "
        + (
            "PASS"
            if result.success
            else "REJECT"
        )
    )

    print(
        f"SCORE  : {result.score:.4f}"
    )

    print(
        f"OUTPUT : {result.output.path}"
    )

    print(
        f"TIME   : "
        f"{result.output.duration_seconds:.2f}s"
    )

    print(
        f"RATE   : "
        f"{result.output.sample_rate} Hz"
    )

    print(
        f"CHANNEL: "
        f"{result.output.channels}"
    )

    print(
        f"RMS    : "
        f"{result.output.rms:.6f}"
    )

    print(
        f"PEAK   : "
        f"{result.output.peak:.6f}"
    )

    print(
        f"CLIP   : "
        f"{result.output.clipping_ratio:.6f}"
    )

    print(
        f"SILENCE: "
        f"{result.output.silence_ratio:.6f}"
    )

    print(
        f"ACTIVE : "
        f"{result.output.active_ratio:.6f}"
    )

    if result.errors:

        print()
        print(
            "ERRORS"
        )

        for error in result.errors:

            print(
                f"  - {error}"
            )

    if result.warnings:

        print()
        print(
            "WARNINGS"
        )

        for warning in result.warnings:

            print(
                f"  - {warning}"
            )

    print(
        "============================================================"
    )
    print()


# ============================================================
# CLI
# ============================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Validate MAVI Stable Audio generation output"
        )
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    parser.add_argument(
        "--target-seconds",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--target-sample-rate",
        type=int,
        default=48000,
    )

    parser.add_argument(
        "--duration-tolerance",
        type=float,
        default=DEFAULT_DURATION_TOLERANCE,
    )

    parser.add_argument(
        "--result",
        default="",
    )

    return parser


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    parser = build_parser()

    args = parser.parse_args()

    try:

        result = (
            GenerationValidator().validate(
                output=args.output,
                target_seconds=args.target_seconds,
                target_sample_rate=args.target_sample_rate,
                duration_tolerance=args.duration_tolerance,
            )
        )

        print_result(
            result
        )

        if args.result:

            save_result(
                result,
                Path(
                    args.result
                )
                .expanduser()
                .resolve(),
            )

        return (
            0
            if result.success
            else 1
        )

    except Exception as exc:

        print()
        print(
            "GENERATION VALIDATION ERROR"
        )
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()

        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )