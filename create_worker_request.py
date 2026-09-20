# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
WORKER REQUEST BUILDER
v0.1
============================================================

Prod. By Ufuk Akdoğan

MAVI'nin gerçek Stable Audio worker'ına göndereceği
generation request JSON dosyasını oluşturur.

BU DOSYA:
- audio üretmez
- model çalıştırmaz
- fake/procedural audio üretmez
- yalnızca güvenli request hazırlar

Özellikle source-preserving audio-to-audio yenileme için
kullanılabilir.
"""

from __future__ import annotations

import argparse
import json
import os

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional


# ============================================================
# CONSTANTS
# ============================================================

VERSION = "0.1"

DEFAULT_SECONDS = 30.0
DEFAULT_SAMPLE_RATE = 48000

DEFAULT_DIT = "sm-music"
DEFAULT_DECODER = "same-s"

DEFAULT_CFG = 1.0
DEFAULT_STEPS = 8
DEFAULT_THREADS = 4

DEFAULT_SEED = 314159


# ============================================================
# ERRORS
# ============================================================

class WorkerRequestError(Exception):
    """Request builder temel hatası."""


# ============================================================
# DATA
# ============================================================

@dataclass
class WorkerRequest:

    prompt: str

    output: str

    seconds: float = DEFAULT_SECONDS

    duration: float = DEFAULT_SECONDS

    sample_rate: int = DEFAULT_SAMPLE_RATE

    seed: Optional[int] = DEFAULT_SEED

    dit: str = DEFAULT_DIT

    decoder: str = DEFAULT_DECODER

    init_audio: str = ""

    init_noise_level: Optional[float] = None

    inpaint_range: str = ""

    negative_prompt: str = ""

    cfg: float = DEFAULT_CFG

    steps: int = DEFAULT_STEPS

    threads: int = DEFAULT_THREADS

    source: str = ""

    mode: str = "text-to-audio"

    metadata: Dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:

        self.prompt = str(
            self.prompt
        ).strip()

        self.output = str(
            self.output
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

        self.dit = str(
            self.dit
        ).strip()

        self.decoder = str(
            self.decoder
        ).strip()

        self.init_audio = str(
            self.init_audio
        ).strip()

        self.inpaint_range = str(
            self.inpaint_range
        ).strip()

        self.negative_prompt = str(
            self.negative_prompt
        ).strip()

        self.cfg = float(
            self.cfg
        )

        self.steps = int(
            self.steps
        )

        self.threads = max(
            1,
            int(
                self.threads
            ),
        )

        self.source = str(
            self.source
        ).strip()

        self.mode = str(
            self.mode
        ).strip()

        if self.seed is not None:

            self.seed = int(
                self.seed
            )

        if self.init_noise_level is not None:

            self.init_noise_level = float(
                self.init_noise_level
            )

        if self.metadata is None:

            self.metadata = {}

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


# ============================================================
# PROMPT POLICY
# ============================================================

class PromptPolicy:

    BASE_NEGATIVE = (
        "keyboard organ timbre, "
        "toy keyboard, "
        "arcade sound, "
        "8-bit sound, "
        "video game music, "
        "cheap synthesizer, "
        "plastic artificial instruments, "
        "over-quantized performance, "
        "excessive compression, "
        "EDM production, "
        "electronic lead, "
        "synthetic zurna, "
        "synthetic clarinet, "
        "fake acoustic instrument"
    )

    @classmethod
    def build_negative(
        cls,
        custom: str = "",
    ) -> str:

        custom = str(
            custom
        ).strip()

        if not custom:

            return cls.BASE_NEGATIVE

        return (
            cls.BASE_NEGATIVE
            + ", "
            + custom
        )


# ============================================================
# SOURCE VALIDATION
# ============================================================

class SourceValidator:

    SUPPORTED = {
        ".wav",
        ".mp3",
        ".flac",
        ".ogg",
        ".m4a",
        ".aac",
        ".wma",
    }

    def validate(
        self,
        source: str,
    ) -> Path:

        if not source:

            raise WorkerRequestError(
                "Source yolu boş."
            )

        path = (
            Path(
                source
            )
            .expanduser()
            .resolve()
        )

        if not path.exists():

            raise WorkerRequestError(
                (
                    "Source bulunamadı: "
                    f"{path}"
                )
            )

        if not path.is_file():

            raise WorkerRequestError(
                (
                    "Source dosya değil: "
                    f"{path}"
                )
            )

        if (
            path.suffix.lower()
            not in self.SUPPORTED
        ):

            raise WorkerRequestError(
                (
                    "Desteklenmeyen source formatı: "
                    f"{path.suffix}"
                )
            )

        return path


# ============================================================
# OUTPUT VALIDATION
# ============================================================

class OutputValidator:

    def validate(
        self,
        output: str,
    ) -> Path:

        if not output:

            raise WorkerRequestError(
                "Output yolu boş."
            )

        path = (
            Path(
                output
            )
            .expanduser()
            .resolve()
        )

        if path.suffix.lower() != ".wav":

            path = path.with_suffix(
                ".wav"
            )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path


# ============================================================
# REQUEST BUILDER
# ============================================================

class WorkerRequestBuilder:

    def __init__(
        self,
    ) -> None:

        self.source_validator = (
            SourceValidator()
        )

        self.output_validator = (
            OutputValidator()
        )

    # --------------------------------------------------------
    # TEXT REQUEST
    # --------------------------------------------------------

    def text_to_audio(
        self,
        prompt: str,
        output: str,
        seconds: float = DEFAULT_SECONDS,
        seed: Optional[int] = DEFAULT_SEED,
        steps: int = DEFAULT_STEPS,
        threads: int = DEFAULT_THREADS,
        cfg: float = DEFAULT_CFG,
        dit: str = DEFAULT_DIT,
        decoder: str = DEFAULT_DECODER,
    ) -> WorkerRequest:

        final_output = (
            self.output_validator.validate(
                output
            )
        )

        request = WorkerRequest(
            prompt=prompt,
            output=str(
                final_output
            ),
            seconds=seconds,
            duration=seconds,
            sample_rate=DEFAULT_SAMPLE_RATE,
            seed=seed,
            dit=dit,
            decoder=decoder,
            steps=steps,
            threads=threads,
            cfg=cfg,
            mode="text-to-audio",
            negative_prompt=(
                PromptPolicy.build_negative()
            ),
            metadata={
                "request_type": "text_to_audio",
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
            },
        )

        validate_request(
            request
        )

        return request

    # --------------------------------------------------------
    # AUDIO RENEWAL REQUEST
    # --------------------------------------------------------

    def audio_to_audio(
        self,
        prompt: str,
        source: str,
        output: str,
        seconds: float,
        seed: Optional[int] = DEFAULT_SEED,
        init_noise_level: float = 0.20,
        steps: int = DEFAULT_STEPS,
        threads: int = DEFAULT_THREADS,
        cfg: float = DEFAULT_CFG,
        dit: str = DEFAULT_DIT,
        decoder: str = DEFAULT_DECODER,
    ) -> WorkerRequest:

        source_path = (
            self.source_validator.validate(
                source
            )
        )

        output_path = (
            self.output_validator.validate(
                output
            )
        )

        request = WorkerRequest(
            prompt=prompt,
            output=str(
                output_path
            ),
            seconds=float(
                seconds
            ),
            duration=float(
                seconds
            ),
            sample_rate=DEFAULT_SAMPLE_RATE,
            seed=seed,
            dit=dit,
            decoder=decoder,
            init_audio=str(
                source_path
            ),
            init_noise_level=float(
                init_noise_level
            ),
            steps=steps,
            threads=threads,
            cfg=cfg,
            source=str(
                source_path
            ),
            mode="audio-to-audio",
            negative_prompt=(
                PromptPolicy.build_negative()
            ),
            metadata={
                "request_type": "audio_to_audio",
                "source_preservation": (
                    0.90
                ),
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
            },
        )

        validate_request(
            request
        )

        return request

    # --------------------------------------------------------
    # INPAINT
    # --------------------------------------------------------

    def inpaint(
        self,
        prompt: str,
        source: str,
        output: str,
        seconds: float,
        inpaint_range: str,
        seed: Optional[int] = DEFAULT_SEED,
        steps: int = DEFAULT_STEPS,
        threads: int = DEFAULT_THREADS,
        cfg: float = DEFAULT_CFG,
    ) -> WorkerRequest:

        source_path = (
            self.source_validator.validate(
                source
            )
        )

        output_path = (
            self.output_validator.validate(
                output
            )
        )

        request = WorkerRequest(
            prompt=prompt,
            output=str(
                output_path
            ),
            seconds=float(
                seconds
            ),
            duration=float(
                seconds
            ),
            sample_rate=DEFAULT_SAMPLE_RATE,
            seed=seed,
            dit=DEFAULT_DIT,
            decoder=DEFAULT_DECODER,
            init_audio=str(
                source_path
            ),
            inpaint_range=str(
                inpaint_range
            ).strip(),
            steps=steps,
            threads=threads,
            cfg=cfg,
            source=str(
                source_path
            ),
            mode="inpaint",
            negative_prompt=(
                PromptPolicy.build_negative()
            ),
            metadata={
                "request_type": "inpaint",
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
            },
        )

        validate_request(
            request
        )

        return request


# ============================================================
# REQUEST VALIDATOR
# ============================================================

def validate_request(
    request: WorkerRequest,
) -> None:

    if not request.prompt:

        raise WorkerRequestError(
            "Prompt boş."
        )

    if not request.output:

        raise WorkerRequestError(
            "Output boş."
        )

    if not (
        20.0
        <= request.seconds
        <= 120.0
    ):

        raise WorkerRequestError(
            "Generation süresi 20-120 saniye arasında olmalı."
        )

    if request.sample_rate <= 0:

        raise WorkerRequestError(
            "Sample rate geçersiz."
        )

    if request.steps < 1:

        raise WorkerRequestError(
            "Steps en az 1 olmalı."
        )

    if request.cfg <= 0:

        raise WorkerRequestError(
            "CFG 0'dan büyük olmalı."
        )

    if request.threads < 1:

        raise WorkerRequestError(
            "Threads en az 1 olmalı."
        )

    if request.init_noise_level is not None:

        if not (
            0.0
            < request.init_noise_level
            <= 1.0
        ):

            raise WorkerRequestError(
                "Init noise level 0-1 arasında olmalı."
            )

    if request.init_audio:

        source_path = (
            Path(
                request.init_audio
            )
            .expanduser()
            .resolve()
        )

        if not source_path.exists():

            raise WorkerRequestError(
                (
                    "Init audio bulunamadı: "
                    f"{source_path}"
                )
            )

    if request.inpaint_range:

        parts = (
            request.inpaint_range.split(
                ","
            )
        )

        if len(parts) != 2:

            raise WorkerRequestError(
                (
                    "Inpaint range "
                    "'START,END' olmalı."
                )
            )

        try:

            start = float(
                parts[0].strip()
            )

            end = float(
                parts[1].strip()
            )

        except ValueError as exc:

            raise WorkerRequestError(
                "Inpaint range sayısal olmalı."
            ) from exc

        if not (
            0.0
            <= start
            < end
            <= request.seconds
        ):

            raise WorkerRequestError(
                (
                    "Inpaint range geçersiz: "
                    f"{request.inpaint_range}"
                )
            )


# ============================================================
# JSON
# ============================================================

def save_request(
    request: WorkerRequest,
    path: Path,
) -> Path:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            request.as_dict(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return path


def load_request(
    path: Path,
) -> WorkerRequest:

    if not path.exists():

        raise WorkerRequestError(
            (
                "Request dosyası bulunamadı: "
                f"{path}"
            )
        )

    try:

        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError as exc:

        raise WorkerRequestError(
            (
                "Request JSON geçersiz: "
                f"{exc}"
            )
        ) from exc

    if not isinstance(
        payload,
        dict,
    ):

        raise WorkerRequestError(
            "Request JSON object olmalı."
        )

    request = WorkerRequest(
        prompt=payload.get(
            "prompt",
            "",
        ),
        output=payload.get(
            "output",
            "",
        ),
        seconds=payload.get(
            "seconds",
            DEFAULT_SECONDS,
        ),
        duration=payload.get(
            "duration",
            payload.get(
                "seconds",
                DEFAULT_SECONDS,
            ),
        ),
        sample_rate=payload.get(
            "sample_rate",
            DEFAULT_SAMPLE_RATE,
        ),
        seed=payload.get(
            "seed",
            None,
        ),
        dit=payload.get(
            "dit",
            DEFAULT_DIT,
        ),
        decoder=payload.get(
            "decoder",
            DEFAULT_DECODER,
        ),
        init_audio=payload.get(
            "init_audio",
            "",
        ),
        init_noise_level=payload.get(
            "init_noise_level",
            None,
        ),
        inpaint_range=payload.get(
            "inpaint_range",
            "",
        ),
        negative_prompt=payload.get(
            "negative_prompt",
            "",
        ),
        cfg=payload.get(
            "cfg",
            DEFAULT_CFG,
        ),
        steps=payload.get(
            "steps",
            DEFAULT_STEPS,
        ),
        threads=payload.get(
            "threads",
            DEFAULT_THREADS,
        ),
        source=payload.get(
            "source",
            "",
        ),
        mode=payload.get(
            "mode",
            "text-to-audio",
        ),
        metadata=payload.get(
            "metadata",
            {},
        ),
    )

    validate_request(
        request
    )

    return request


# ============================================================
# CLI
# ============================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "MAVI AI Studio worker request builder"
        )
    )

    parser.add_argument(
        "--mode",
        choices=[
            "text",
            "renewal",
            "inpaint",
        ],
        default="text",
    )

    parser.add_argument(
        "--prompt",
        required=True,
    )

    parser.add_argument(
        "--source",
        default="",
    )

    parser.add_argument(
        "--output",
        required=True,
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
        "--init-noise-level",
        type=float,
        default=0.20,
    )

    parser.add_argument(
        "--inpaint-range",
        default="",
    )

    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
    )

    parser.add_argument(
        "--threads",
        type=int,
        default=int(
            os.getenv(
                "MAVI_STABLE_AUDIO_THREADS",
                DEFAULT_THREADS,
            )
        ),
    )

    parser.add_argument(
        "--cfg",
        type=float,
        default=DEFAULT_CFG,
    )

    parser.add_argument(
        "--request",
        default="",
        help="Oluşturulacak JSON request dosyası.",
    )

    return parser


def main() -> int:

    parser = (
        build_parser()
    )

    args = parser.parse_args()

    builder = (
        WorkerRequestBuilder()
    )

    try:

        if args.mode == "text":

            request = (
                builder.text_to_audio(
                    prompt=args.prompt,
                    output=args.output,
                    seconds=args.seconds,
                    seed=args.seed,
                    steps=args.steps,
                    threads=args.threads,
                    cfg=args.cfg,
                )
            )

        elif args.mode == "renewal":

            if not args.source:

                raise WorkerRequestError(
                    (
                        "renewal modu için "
                        "--source gerekli."
                    )
                )

            request = (
                builder.audio_to_audio(
                    prompt=args.prompt,
                    source=args.source,
                    output=args.output,
                    seconds=args.seconds,
                    seed=args.seed,
                    init_noise_level=(
                        args.init_noise_level
                    ),
                    steps=args.steps,
                    threads=args.threads,
                    cfg=args.cfg,
                )
            )

        else:

            if not args.source:

                raise WorkerRequestError(
                    (
                        "inpaint modu için "
                        "--source gerekli."
                    )
                )

            if not args.inpaint_range:

                raise WorkerRequestError(
                    (
                        "inpaint modu için "
                        "--inpaint-range gerekli."
                    )
                )

            request = (
                builder.inpaint(
                    prompt=args.prompt,
                    source=args.source,
                    output=args.output,
                    seconds=args.seconds,
                    inpaint_range=(
                        args.inpaint_range
                    ),
                    seed=args.seed,
                    steps=args.steps,
                    threads=args.threads,
                    cfg=args.cfg,
                )
            )

        print(
            json.dumps(
                request.as_dict(),
                ensure_ascii=False,
                indent=2,
            )
        )

        if args.request:

            save_request(
                request,
                Path(
                    args.request
                ),
            )

            print()
            print(
                f"Request yazıldı: {args.request}"
            )

        return 0

    except Exception as exc:

        print(
            (
                f"{type(exc).__name__}: "
                f"{exc}"
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