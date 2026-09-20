# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
GENERATION PREPARATION
v0.1
============================================================

Prod. By Ufuk Akdoğan

Gerçek Stable Audio generation öncesi kaynak müzikten alınan
bilgileri güvenli bir generation request'e dönüştürür.

BU DOSYA:
- audio üretmez
- generation başlatmaz
- fake/procedural audio üretmez
- kaynak müziği değiştirmez
- yalnızca generation hazırlığı yapar

Öncelik:
1. Kaynak korunumu
2. Tempo korunumu
3. Tonal kimlik korunumu
4. Yapısal korunumu
5. Yöresel karakter
6. Seçilen enstrümanlar
7. Doğal akustik icra
"""

from __future__ import annotations

import json
import sys

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# LOCAL IMPORTS
# ============================================================

ROOT = (
    Path(__file__)
    .resolve()
    .parent
)

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )


# ============================================================
# SAFE IMPORT HELPERS
# ============================================================

try:

    import config

except Exception as exc:

    config = None
    CONFIG_IMPORT_ERROR = exc

else:

    CONFIG_IMPORT_ERROR = None


try:

    from core.renewal import (
        RenewalPlan,
        build_generation_payload,
        create_renewal_plan,
        validate_renewal_plan,
    )

except Exception:

    RenewalPlan = Any
    build_generation_payload = None
    create_renewal_plan = None
    validate_renewal_plan = None


try:

    from core.models import (
        MusicDNA,
        RenewalRequest,
        SourceAudio,
        AudioFeatures,
        RegionalIdentity,
    )

except Exception:

    MusicDNA = Any
    RenewalRequest = Any
    SourceAudio = Any
    AudioFeatures = Any
    RegionalIdentity = Any


# ============================================================
# CONSTANTS
# ============================================================

VERSION = "0.1"

DEFAULT_SECONDS = 30.0

MAX_GENERATION_SECONDS = 120.0

DEFAULT_SEED = 314159

DEFAULT_STEPS = 8

DEFAULT_THREADS = 4

DEFAULT_CFG = 1.0

DEFAULT_NOISE_LEVEL = 0.20


# ============================================================
# ERRORS
# ============================================================

class GenerationPreparationError(Exception):
    """Generation preparation temel hatası."""


class GenerationPreparationInputError(
    GenerationPreparationError
):
    """Generation hazırlık girdisi geçersiz."""


# ============================================================
# DATA
# ============================================================

@dataclass
class PreparedGeneration:

    prompt: str

    negative_prompt: str

    seconds: float

    duration: float

    sample_rate: int

    seed: int

    steps: int

    threads: int

    cfg: float

    dit: str

    decoder: str

    source_path: str = ""

    init_audio: str = ""

    init_noise_level: float = DEFAULT_NOISE_LEVEL

    mode: str = "audio-to-audio"

    instruments: List[str] = None  # type: ignore[assignment]

    preservation: float = 0.90

    metadata: Dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(
        self,
    ) -> None:

        if self.instruments is None:

            self.instruments = []

        if self.metadata is None:

            self.metadata = {}

        self.prompt = str(
            self.prompt
        ).strip()

        self.negative_prompt = str(
            self.negative_prompt
        ).strip()

        self.source_path = str(
            self.source_path
        ).strip()

        self.init_audio = str(
            self.init_audio
        ).strip()

        self.seconds = float(
            self.seconds
        )

        self.duration = float(
            self.duration
        )

        self.sample_rate = int(
            self.sample_rate
        )

        self.seed = int(
            self.seed
        )

        self.steps = int(
            self.steps
        )

        self.threads = int(
            self.threads
        )

        self.cfg = float(
            self.cfg
        )

        self.init_noise_level = float(
            self.init_noise_level
        )

        self.preservation = float(
            self.preservation
        )

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


# ============================================================
# PROMPT BUILDER
# ============================================================

class GenerationPrompt:

    @staticmethod
    def _clean(
        value: Any,
    ) -> str:

        return (
            str(
                value or ""
            )
            .replace(
                "\n",
                " ",
            )
            .strip()
        )

    @classmethod
    def build(
        cls,
        command: str,
        music_dna: Any = None,
        regional: Any = None,
        renewal_plan: Any = None,
    ) -> str:

        command_text = cls._clean(
            command
        )

        pieces: List[str] = []

        # ----------------------------------------------------
        # PRIMARY REQUEST
        # ----------------------------------------------------

        if command_text:

            pieces.append(
                command_text
            )

        # ----------------------------------------------------
        # DNA
        # ----------------------------------------------------

        if music_dna is not None:

            tempo = getattr(
                music_dna,
                "tempo",
                None,
            )

            key = getattr(
                music_dna,
                "key",
                "",
            )

            mode = getattr(
                music_dna,
                "mode",
                "",
            )

            structure = getattr(
                music_dna,
                "structure",
                "",
            )

            character_tags = getattr(
                music_dna,
                "character_tags",
                [],
            )

            if tempo:

                pieces.append(
                    (
                        f"maintain approximately "
                        f"{float(tempo):.1f} BPM"
                    )
                )

            if key:

                pieces.append(
                    (
                        f"preserve tonal center {cls._clean(key)}"
                    )
                )

            if mode:

                pieces.append(
                    (
                        f"preserve mode {cls._clean(mode)}"
                    )
                )

            if structure:

                pieces.append(
                    (
                        f"preserve musical structure "
                        f"{cls._clean(structure)}"
                    )
                )

            if character_tags:

                if isinstance(
                    character_tags,
                    (list, tuple),
                ):

                    tags = ", ".join(
                        cls._clean(tag)
                        for tag in character_tags
                        if cls._clean(tag)
                    )

                else:

                    tags = cls._clean(
                        character_tags
                    )

                if tags:

                    pieces.append(
                        (
                            "retain original musical character: "
                            f"{tags}"
                        )
                    )

        # ----------------------------------------------------
        # REGIONAL
        # ----------------------------------------------------

        if regional is not None:

            dance = getattr(
                regional,
                "dance_family",
                "",
            )

            region = getattr(
                regional,
                "region",
                "",
            )

            identity = getattr(
                regional,
                "identity",
                "",
            )

            if dance:

                pieces.append(
                    (
                        f"preserve {cls._clean(dance)} "
                        "dance character"
                    )
                )

            if region:

                pieces.append(
                    (
                        f"preserve {cls._clean(region)} "
                        "regional character"
                    )
                )

            if identity:

                pieces.append(
                    cls._clean(
                        identity
                    )
                )

        # ----------------------------------------------------
        # RENEWAL
        # ----------------------------------------------------

        instruments: List[str] = []

        if renewal_plan is not None:

            plan_instruments = getattr(
                renewal_plan,
                "instruments",
                [],
            )

            if isinstance(
                plan_instruments,
                (list, tuple),
            ):

                for instrument in plan_instruments:

                    name = getattr(
                        instrument,
                        "name",
                        instrument,
                    )

                    name = cls._clean(
                        name
                    )

                    if name:

                        instruments.append(
                            name
                        )

            preservation = getattr(
                renewal_plan,
                "source_preservation",
                None,
            )

            if preservation is not None:

                try:

                    preservation_text = (
                        f"preserve the source identity "
                        f"at least {float(preservation):.2f}"
                    )

                    pieces.append(
                        preservation_text
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    pass

        if instruments:

            unique = []

            for instrument in instruments:

                if instrument not in unique:

                    unique.append(
                        instrument
                    )

            pieces.append(
                (
                    "use realistic acoustic performance "
                    "for the selected instruments: "
                    + ", ".join(unique)
                )
            )

        # ----------------------------------------------------
        # REALISM
        # ----------------------------------------------------

        pieces.extend(
            [
                "human live-performance feel",
                "natural dynamics",
                "natural timing variations",
                "realistic acoustic instrument tone",
                "organic ensemble interaction",
                "controlled arrangement changes only",
                "do not change the original melody",
                "do not change the original rhythmic identity",
                "do not arbitrarily reharmonize",
                "do not arbitrarily transpose",
            ]
        )

        # ----------------------------------------------------
        # FINAL
        # ----------------------------------------------------

        return (
            ", ".join(
                piece
                for piece in pieces
                if piece
            )
        )


# ============================================================
# NEGATIVE PROMPT
# ============================================================

class NegativePrompt:

    BASE = (
        "organ, keyboard, toy keyboard, "
        "arcade music, video game music, "
        "8-bit, chiptune, "
        "cheap synthesizer, "
        "plastic synthetic instruments, "
        "electronic lead, EDM, "
        "artificial quantization, "
        "robotic timing, "
        "excessive compression, "
        "overprocessed sound, "
        "fake acoustic instruments, "
        "synthetic zurna, "
        "synthetic clarinet, "
        "synthetic davul"
    )

    @classmethod
    def build(
        cls,
        extra: str = "",
    ) -> str:

        extra = str(
            extra or ""
        ).strip()

        if not extra:

            return cls.BASE

        return (
            cls.BASE
            + ", "
            + extra
        )


# ============================================================
# DURATION
# ============================================================

def normalize_seconds(
    seconds: Optional[float],
) -> float:

    if seconds is None:

        seconds = DEFAULT_SECONDS

    seconds = float(
        seconds
    )

    if seconds <= 0:

        raise GenerationPreparationInputError(
            "Generation süresi 0'dan büyük olmalı."
        )

    seconds = min(
        seconds,
        MAX_GENERATION_SECONDS,
    )

    return seconds


# ============================================================
# INSTRUMENT EXTRACTION
# ============================================================

def extract_instruments(
    renewal_plan: Any = None,
) -> List[str]:

    if renewal_plan is None:

        return []

    values = getattr(
        renewal_plan,
        "instruments",
        [],
    )

    if not isinstance(
        values,
        (list, tuple),
    ):

        return []

    result: List[str] = []

    for value in values:

        name = getattr(
            value,
            "name",
            value,
        )

        name = (
            str(
                name
                or ""
            )
            .strip()
        )

        if (
            name
            and name not in result
        ):

            result.append(
                name
            )

    return result


# ============================================================
# PRESERVATION
# ============================================================

def extract_preservation(
    renewal_plan: Any = None,
) -> float:

    if renewal_plan is None:

        return 0.90

    values = [
        "source_preservation",
        "preservation",
        "preservation_ratio",
    ]

    for name in values:

        value = getattr(
            renewal_plan,
            name,
            None,
        )

        if value is None:
            continue

        try:

            return max(
                0.0,
                min(
                    1.0,
                    float(
                        value
                    ),
                ),
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

    return 0.90


# ============================================================
# PREPARER
# ============================================================

class GenerationPreparer:

    def __init__(
        self,
    ) -> None:

        self.default_sample_rate = (
            48000
        )

        if config is not None:

            self.default_sample_rate = int(
                getattr(
                    config,
                    "DEFAULT_SAMPLE_RATE",
                    48000,
                )
            )

    def prepare(
        self,
        command: str,
        output: str,
        source: str = "",
        seconds: Optional[float] = None,
        seed: int = DEFAULT_SEED,
        steps: int = DEFAULT_STEPS,
        threads: int = DEFAULT_THREADS,
        cfg: float = DEFAULT_CFG,
        dit: str = "sm-music",
        decoder: str = "same-s",
        init_noise_level: float = DEFAULT_NOISE_LEVEL,
        music_dna: Any = None,
        regional: Any = None,
        renewal_plan: Any = None,
        negative_prompt: str = "",
    ) -> PreparedGeneration:

        if not command or not str(
            command
        ).strip():

            raise GenerationPreparationInputError(
                "Generation command boş."
            )

        if not output:

            raise GenerationPreparationInputError(
                "Generation output yolu boş."
            )

        output_path = (
            Path(
                output
            )
            .expanduser()
            .resolve()
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        source_path = ""

        if source:

            source_file = (
                Path(
                    source
                )
                .expanduser()
                .resolve()
            )

            if not source_file.exists():

                raise GenerationPreparationInputError(
                    (
                        "Source bulunamadı: "
                        f"{source_file}"
                    )
                )

            if not source_file.is_file():

                raise GenerationPreparationInputError(
                    (
                        "Source dosya değil: "
                        f"{source_file}"
                    )
                )

            source_path = str(
                source_file
            )

        final_seconds = normalize_seconds(
            seconds
        )

        instruments = extract_instruments(
            renewal_plan
        )

        preservation = extract_preservation(
            renewal_plan
        )

        prompt = GenerationPrompt.build(
            command=command,
            music_dna=music_dna,
            regional=regional,
            renewal_plan=renewal_plan,
        )

        final_negative = NegativePrompt.build(
            negative_prompt
        )

        mode = (
            "audio-to-audio"
            if source_path
            else "text-to-audio"
        )

        return PreparedGeneration(
            prompt=prompt,
            negative_prompt=final_negative,
            seconds=final_seconds,
            duration=final_seconds,
            sample_rate=self.default_sample_rate,
            seed=int(seed),
            steps=max(
                1,
                int(steps),
            ),
            threads=max(
                1,
                int(threads),
            ),
            cfg=max(
                0.01,
                float(cfg),
            ),
            dit=str(
                dit
            ),
            decoder=str(
                decoder
            ),
            source_path=source_path,
            init_audio=source_path,
            init_noise_level=max(
                0.001,
                min(
                    1.0,
                    float(
                        init_noise_level
                    ),
                ),
            ),
            mode=mode,
            instruments=instruments,
            preservation=preservation,
            metadata={
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
                "placeholder_audio": False,
                "source_preservation": preservation,
                "instrument_count": len(
                    instruments
                ),
            },
        )


# ============================================================
# JSON
# ============================================================

def save_prepared_generation(
    prepared: PreparedGeneration,
    path: str | Path,
) -> Path:

    target = (
        Path(
            path
        )
        .expanduser()
        .resolve()
    )

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    target.write_text(
        json.dumps(
            prepared.as_dict(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return target


def load_prepared_generation(
    path: str | Path,
) -> PreparedGeneration:

    target = (
        Path(
            path
        )
        .expanduser()
        .resolve()
    )

    if not target.exists():

        raise GenerationPreparationError(
            (
                "Prepared generation bulunamadı: "
                f"{target}"
            )
        )

    payload = json.loads(
        target.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        payload,
        dict,
    ):

        raise GenerationPreparationError(
            "Prepared generation JSON object olmalı."
        )

    return PreparedGeneration(
        prompt=payload.get(
            "prompt",
            "",
        ),
        negative_prompt=payload.get(
            "negative_prompt",
            "",
        ),
        seconds=payload.get(
            "seconds",
            DEFAULT_SECONDS,
        ),
        duration=payload.get(
            "duration",
            DEFAULT_SECONDS,
        ),
        sample_rate=payload.get(
            "sample_rate",
            48000,
        ),
        seed=payload.get(
            "seed",
            DEFAULT_SEED,
        ),
        steps=payload.get(
            "steps",
            DEFAULT_STEPS,
        ),
        threads=payload.get(
            "threads",
            DEFAULT_THREADS,
        ),
        cfg=payload.get(
            "cfg",
            DEFAULT_CFG,
        ),
        dit=payload.get(
            "dit",
            "sm-music",
        ),
        decoder=payload.get(
            "decoder",
            "same-s",
        ),
        source_path=payload.get(
            "source_path",
            "",
        ),
        init_audio=payload.get(
            "init_audio",
            "",
        ),
        init_noise_level=payload.get(
            "init_noise_level",
            DEFAULT_NOISE_LEVEL,
        ),
        mode=payload.get(
            "mode",
            "audio-to-audio",
        ),
        instruments=payload.get(
            "instruments",
            [],
        ),
        preservation=payload.get(
            "preservation",
            0.90,
        ),
        metadata=payload.get(
            "metadata",
            {},
        ),
    )


# ============================================================
# SIMPLE PUBLIC API
# ============================================================

def prepare_generation(
    command: str,
    output: str,
    source: str = "",
    seconds: Optional[float] = None,
    seed: int = DEFAULT_SEED,
    steps: int = DEFAULT_STEPS,
    threads: int = DEFAULT_THREADS,
    cfg: float = DEFAULT_CFG,
    dit: str = "sm-music",
    decoder: str = "same-s",
    init_noise_level: float = DEFAULT_NOISE_LEVEL,
    music_dna: Any = None,
    regional: Any = None,
    renewal_plan: Any = None,
    negative_prompt: str = "",
) -> PreparedGeneration:

    return GenerationPreparer().prepare(
        command=command,
        output=output,
        source=source,
        seconds=seconds,
        seed=seed,
        steps=steps,
        threads=threads,
        cfg=cfg,
        dit=dit,
        decoder=decoder,
        init_noise_level=init_noise_level,
        music_dna=music_dna,
        regional=regional,
        renewal_plan=renewal_plan,
        negative_prompt=negative_prompt,
    )


def prepared_to_worker_payload(
    prepared: PreparedGeneration,
) -> Dict[str, Any]:

    payload = prepared.as_dict()

    payload.update(
        {
            "output": (
                payload.get(
                    "source_path",
                    "",
                )
                if False
                else ""
            ),
        }
    )

    # Worker output path ayrı tutulur.
    # PreparedGeneration'ın output alanı olmaması
    # bilinçli olarak korunur.
    return payload


# ============================================================
# DEMO-SAFE CLI
# ============================================================

def build_parser() -> Any:

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Prepare a real MAVI Stable Audio generation request"
        )
    )

    parser.add_argument(
        "--prompt",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    parser.add_argument(
        "--source",
        default="",
    )

    parser.add_argument(
        "--seconds",
        type=float,
        default=DEFAULT_SECONDS,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
    )

    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
    )

    parser.add_argument(
        "--threads",
        type=int,
        default=DEFAULT_THREADS,
    )

    parser.add_argument(
        "--cfg",
        type=float,
        default=DEFAULT_CFG,
    )

    parser.add_argument(
        "--dit",
        default="sm-music",
    )

    parser.add_argument(
        "--decoder",
        default="same-s",
    )

    parser.add_argument(
        "--init-noise-level",
        type=float,
        default=DEFAULT_NOISE_LEVEL,
    )

    parser.add_argument(
        "--negative-prompt",
        default="",
    )

    parser.add_argument(
        "--result",
        default="",
    )

    return parser


def main() -> int:

    parser = build_parser()

    args = parser.parse_args()

    try:

        prepared = prepare_generation(
            command=args.prompt,
            output=args.output,
            source=args.source,
            seconds=args.seconds,
            seed=args.seed,
            steps=args.steps,
            threads=args.threads,
            cfg=args.cfg,
            dit=args.dit,
            decoder=args.decoder,
            init_noise_level=args.init_noise_level,
            negative_prompt=args.negative_prompt,
        )

        payload = (
            prepared.as_dict()
        )

        # output path request'e metadata ile eklenir.
        payload[
            "output"
        ] = str(
            Path(
                args.output
            )
            .expanduser()
            .resolve()
        )

        print(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
        )

        if args.result:

            prepared.metadata[
                "output"
            ] = str(
                Path(
                    args.output
                )
                .expanduser()
                .resolve()
            )

            save_prepared_generation(
                prepared,
                Path(
                    args.result
                ),
            )

        return 0

    except Exception as exc:

        print(
            json.dumps(
                {
                    "success": False,
                    "error": (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),
                    "real_generation": True,
                    "fake_audio": False,
                    "procedural_audio": False,
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )