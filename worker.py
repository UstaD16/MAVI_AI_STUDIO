# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
REAL AUDIO WORKER
v0.2
============================================================

Prod. By Ufuk Akdoğan

Main MAVI uygulamasından bağımsız gerçek audio worker.

Akış:

    worker.py
        ↓
    stable_audio_runner.py
        ↓
    Stable Audio 3 TFLite
        ↓
    WAV

Kurallar:

- Fake audio yok.
- Procedural audio yok.
- Placeholder audio yok.
- Generator command environment üzerinden çalışmaz.
- Gerçek Stable Audio 3 runner kullanılır.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import wave

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent

RUNNER = (
    ROOT
    / "stable_audio_runner.py"
)

STABLE_AUDIO_ROOT = (
    ROOT
    / "third_party"
    / "stable-audio-3"
    / "optimized"
    / "tflite"
)

WORKER_VENV = (
    STABLE_AUDIO_ROOT
    / ".venv"
)

WORKER_PYTHON = (
    WORKER_VENV
    / "Scripts"
    / "python.exe"
)

SA3_BAT = (
    STABLE_AUDIO_ROOT
    / "sa3.bat"
)


# ============================================================
# CONSTANTS
# ============================================================

WORKER_VERSION = "0.2"

DEFAULT_TIMEOUT = 1800

DEFAULT_SECONDS = 30.0

DEFAULT_SAMPLE_RATE = 48000

DEFAULT_SEED = 314159

DEFAULT_STEPS = 8

DEFAULT_THREADS = 4

DEFAULT_CFG = 1.0

DEFAULT_INIT_NOISE_LEVEL = 0.70

FAKE_AUDIO_ALLOWED = False

PROCEDURAL_AUDIO_ALLOWED = False

PLACEHOLDER_AUDIO_ALLOWED = False


# ============================================================
# ERRORS
# ============================================================

class WorkerError(Exception):
    pass


class WorkerConfigError(
    WorkerError
):
    pass


class WorkerGenerationError(
    WorkerError
):
    pass


class WorkerOutputError(
    WorkerError
):
    pass


class WorkerTimeoutError(
    WorkerError
):
    pass


# ============================================================
# REQUEST
# ============================================================

@dataclass
class GenerationRequest:

    prompt: str

    output: str

    seconds: float = DEFAULT_SECONDS

    duration: float = DEFAULT_SECONDS

    sample_rate: int = DEFAULT_SAMPLE_RATE

    seed: int = DEFAULT_SEED

    steps: int = DEFAULT_STEPS

    threads: int = DEFAULT_THREADS

    cfg: float = DEFAULT_CFG

    dit: str = "sm-music"

    decoder: str = "same-s"

    source: str = ""

    init_audio: str = ""

    init_noise_level: float = (
        DEFAULT_INIT_NOISE_LEVEL
    )

    negative_prompt: str = ""

    mode: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(
        self,
    ) -> None:

        self.prompt = str(
            self.prompt or ""
        ).strip()

        self.output = str(
            self.output or ""
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

        self.steps = max(
            1,
            int(
                self.steps
            ),
        )

        self.threads = max(
            1,
            int(
                self.threads
            ),
        )

        self.cfg = float(
            self.cfg
        )

        self.dit = str(
            self.dit or "sm-music"
        ).strip()

        self.decoder = str(
            self.decoder or "same-s"
        ).strip()

        self.source = str(
            self.source or ""
        ).strip()

        self.init_audio = str(
            self.init_audio
            or self.source
        ).strip()

        self.init_noise_level = float(
            self.init_noise_level
        )

        self.negative_prompt = str(
            self.negative_prompt or ""
        ).strip()

        self.mode = str(
            self.mode or ""
        ).strip()

        if not self.mode:

            self.mode = (
                "audio-to-audio"
                if self.init_audio
                else "text-to-audio"
            )

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


# ============================================================
# RESULT
# ============================================================

@dataclass
class GenerationResult:

    success: bool = False

    output: str = ""

    returncode: int = -1

    elapsed_seconds: float = 0.0

    stdout: str = ""

    stderr: str = ""

    command: List[str] = field(
        default_factory=list
    )

    error: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


# ============================================================
# ENVIRONMENT
# ============================================================

class WorkerEnvironment:

    def __init__(
        self,
    ) -> None:

        self.root = ROOT

        self.runner = (
            RUNNER
        )

        self.stable_audio_root = (
            STABLE_AUDIO_ROOT
        )

        self.worker_python = (
            WORKER_PYTHON
        )

        self.sa3_bat = (
            SA3_BAT
        )

        self.timeout = (
            DEFAULT_TIMEOUT
        )

    def validate(
        self,
    ) -> None:

        if not self.runner.exists():

            raise WorkerConfigError(
                (
                    "stable_audio_runner.py "
                    f"bulunamadı: {self.runner}"
                )
            )

        if not self.worker_python.exists():

            raise WorkerConfigError(
                (
                    "Worker Python bulunamadı: "
                    f"{self.worker_python}"
                )
            )

        if not self.sa3_bat.exists():

            raise WorkerConfigError(
                (
                    "sa3.bat bulunamadı: "
                    f"{self.sa3_bat}"
                )
            )

    def status(
        self,
    ) -> Dict[str, Any]:

        runner_ok = (
            self.runner.exists()
            and self.runner.is_file()
        )

        python_ok = (
            self.worker_python.exists()
            and self.worker_python.is_file()
        )

        sa3_ok = (
            self.sa3_bat.exists()
            and self.sa3_bat.is_file()
        )

        return {
            "worker_version": WORKER_VERSION,
            "ready": (
                runner_ok
                and python_ok
                and sa3_ok
            ),
            "runner": str(
                self.runner
            ),
            "runner_available": runner_ok,
            "worker_python": str(
                self.worker_python
            ),
            "worker_python_available": python_ok,
            "sa3_bat": str(
                self.sa3_bat
            ),
            "sa3_available": sa3_ok,
            "stable_audio_root": str(
                self.stable_audio_root
            ),
            "timeout_seconds": (
                self.timeout
            ),
            "python": sys.executable,
            "python_version": sys.version,
            "real_generation_required": True,
            "fake_audio": False,
            "procedural_audio": False,
            "placeholder_audio": False,
        }


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_request(
    request: GenerationRequest,
) -> None:

    if not request.prompt:

        raise WorkerGenerationError(
            "Generation prompt boş."
        )

    if not request.output:

        raise WorkerGenerationError(
            "Generation output yolu boş."
        )

    if not (
        1.0
        <= request.seconds
        <= 120.0
    ):

        raise WorkerGenerationError(
            "Generation süresi 1-120 saniye arasında olmalı."
        )

    if request.sample_rate <= 0:

        raise WorkerGenerationError(
            "Sample rate geçersiz."
        )

    if request.steps <= 0:

        raise WorkerGenerationError(
            "Steps geçersiz."
        )

    if request.threads <= 0:

        raise WorkerGenerationError(
            "Threads geçersiz."
        )

    if request.cfg <= 0:

        raise WorkerGenerationError(
            "CFG geçersiz."
        )

    output = (
        Path(
            request.output
        )
        .expanduser()
        .resolve()
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    request.output = str(
        output
    )

    if request.init_audio:

        source = (
            Path(
                request.init_audio
            )
            .expanduser()
            .resolve()
        )

        if not source.exists():

            raise WorkerGenerationError(
                (
                    "Init audio bulunamadı: "
                    f"{source}"
                )
            )

        if not source.is_file():

            raise WorkerGenerationError(
                (
                    "Init audio dosya değil: "
                    f"{source}"
                )
            )

        request.init_audio = str(
            source
        )

        request.source = str(
            source
        )

        request.mode = (
            "audio-to-audio"
        )


# ============================================================
# COMMAND BUILDER
# ============================================================

class StableAudioCommandBuilder:

    def build(
        self,
        request: GenerationRequest,
        environment: WorkerEnvironment,
    ) -> List[str]:

        validate_request(
            request
        )

        environment.validate()

        command = [
            str(
                environment.worker_python
            ),
            str(
                environment.runner
            ),

            "--prompt",
            request.prompt,

            "--output",
            request.output,

            "--seconds",
            str(
                request.seconds
            ),

            "--seed",
            str(
                request.seed
            ),

            "--steps",
            str(
                request.steps
            ),

            "--threads",
            str(
                request.threads
            ),

            "--cfg",
            str(
                request.cfg
            ),

            "--dit",
            request.dit,

            "--decoder",
            request.decoder,
        ]

        if request.negative_prompt:

            command.extend(
                [
                    "--negative-prompt",
                    request.negative_prompt,
                ]
            )

        if request.init_audio:

            command.extend(
                [
                    "--init-audio",
                    request.init_audio,

                    "--init-noise-level",
                    str(
                        request.init_noise_level
                    ),
                ]
            )

        return command


# ============================================================
# OUTPUT VALIDATOR
# ============================================================

class WorkerOutputValidator:

    def validate(
        self,
        output: str,
    ) -> Dict[str, Any]:

        path = (
            Path(
                output
            )
            .expanduser()
            .resolve()
        )

        if not path.exists():

            raise WorkerOutputError(
                (
                    "Stable Audio output üretmedi: "
                    f"{path}"
                )
            )

        if not path.is_file():

            raise WorkerOutputError(
                (
                    "Generator output dosya değil: "
                    f"{path}"
                )
            )

        if path.stat().st_size <= 0:

            raise WorkerOutputError(
                (
                    "Generator output boş: "
                    f"{path}"
                )
            )

        if path.suffix.lower() != ".wav":

            raise WorkerOutputError(
                (
                    "Generator output WAV değil: "
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

                sample_rate = (
                    wav.getframerate()
                )

                frames = (
                    wav.getnframes()
                )

                sample_width = (
                    wav.getsampwidth()
                )

        except Exception as exc:

            raise WorkerOutputError(
                (
                    "WAV doğrulanamadı: "
                    f"{exc}"
                )
            ) from exc

        if channels < 1:

            raise WorkerOutputError(
                "WAV channels geçersiz."
            )

        if sample_rate < 1:

            raise WorkerOutputError(
                "WAV sample rate geçersiz."
            )

        if frames < 1:

            raise WorkerOutputError(
                "WAV frame sayısı geçersiz."
            )

        duration = (
            frames
            / sample_rate
        )

        return {
            "path": str(path),
            "size_bytes": (
                path.stat().st_size
            ),
            "channels": channels,
            "sample_rate": sample_rate,
            "sample_width": sample_width,
            "frames": frames,
            "duration_seconds": duration,
        }


# ============================================================
# PROCESS
# ============================================================

class GeneratorProcess:

    def __init__(
        self,
        timeout: int,
    ) -> None:

        self.timeout = max(
            1,
            int(timeout),
        )

    def execute(
        self,
        command: Sequence[str],
        output: str,
    ) -> GenerationResult:

        started = (
            time.perf_counter()
        )

        try:

            process = subprocess.run(
                list(
                    command
                ),
                cwd=str(
                    ROOT
                ),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
                check=False,
            )

        except subprocess.TimeoutExpired as exc:

            elapsed = (
                time.perf_counter()
                - started
            )

            return GenerationResult(
                success=False,
                output=output,
                returncode=-2,
                elapsed_seconds=round(
                    elapsed,
                    3,
                ),
                stdout=(
                    exc.stdout
                    if isinstance(
                        exc.stdout,
                        str,
                    )
                    else ""
                ),
                stderr=(
                    exc.stderr
                    if isinstance(
                        exc.stderr,
                        str,
                    )
                    else ""
                ),
                command=list(
                    command
                ),
                error=(
                    "Stable Audio worker timeout."
                ),
            )

        except OSError as exc:

            elapsed = (
                time.perf_counter()
                - started
            )

            return GenerationResult(
                success=False,
                output=output,
                returncode=-1,
                elapsed_seconds=round(
                    elapsed,
                    3,
                ),
                command=list(
                    command
                ),
                error=(
                    "Worker başlatılamadı: "
                    f"{exc}"
                ),
            )

        elapsed = (
            time.perf_counter()
            - started
        )

        success = (
            process.returncode == 0
        )

        return GenerationResult(
            success=success,
            output=output,
            returncode=(
                process.returncode
            ),
            elapsed_seconds=round(
                elapsed,
                3,
            ),
            stdout=(
                process.stdout
                or ""
            ),
            stderr=(
                process.stderr
                or ""
            ),
            command=list(
                command
            ),
            error=(
                ""
                if success
                else
                "Stable Audio gerçek generation başarısız."
            ),
        )


# ============================================================
# REAL AUDIO WORKER
# ============================================================

class RealAudioWorker:

    def __init__(
        self,
        environment: Optional[
            WorkerEnvironment
        ] = None,
    ) -> None:

        self.environment = (
            environment
            or WorkerEnvironment()
        )

        self.command_builder = (
            StableAudioCommandBuilder()
        )

        self.validator = (
            WorkerOutputValidator()
        )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    def status(
        self,
    ) -> Dict[str, Any]:

        return self.environment.status()

    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:

        validate_request(
            request
        )

        self.environment.validate()

        command = (
            self.command_builder.build(
                request,
                self.environment,
            )
        )

        process = (
            GeneratorProcess(
                self.environment.timeout
            )
        )

        result = process.execute(
            command=command,
            output=request.output,
        )

        result.metadata.update(
            {
                "worker_version": WORKER_VERSION,
                "mode": request.mode,
                "prompt": request.prompt,
                "seconds": request.seconds,
                "source": request.source,
                "init_audio": request.init_audio,
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
                "placeholder_audio": False,
            }
        )

        if not result.success:

            return result

        try:

            info = (
                self.validator.validate(
                    request.output
                )
            )

        except WorkerOutputError as exc:

            result.success = False
            result.error = str(
                exc
            )

            return result

        result.output = str(
            info["path"]
        )

        result.metadata[
            "output_info"
        ] = info

        return result


# ============================================================
# JSON
# ============================================================

def request_from_payload(
    payload: Dict[str, Any],
) -> GenerationRequest:

    if not isinstance(
        payload,
        dict,
    ):

        raise WorkerError(
            "Request JSON object olmalı."
        )

    return GenerationRequest(
        prompt=payload.get(
            "prompt",
            "",
        ),
        output=payload.get(
            "output",
            payload.get(
                "output_path",
                "",
            ),
        ),
        seconds=payload.get(
            "seconds",
            payload.get(
                "duration",
                DEFAULT_SECONDS,
            ),
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
        source=payload.get(
            "source",
            payload.get(
                "source_path",
                "",
            ),
        ),
        init_audio=payload.get(
            "init_audio",
            payload.get(
                "source",
                "",
            ),
        ),
        init_noise_level=payload.get(
            "init_noise_level",
            DEFAULT_INIT_NOISE_LEVEL,
        ),
        negative_prompt=payload.get(
            "negative_prompt",
            "",
        ),
        mode=payload.get(
            "mode",
            "",
        ),
        metadata=payload.get(
            "metadata",
            {},
        ),
    )


def load_json_request(
    path: Path,
) -> GenerationRequest:

    if not path.exists():

        raise WorkerError(
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

        raise WorkerError(
            (
                "Request JSON geçersiz: "
                f"{exc}"
            )
        ) from exc

    return request_from_payload(
        payload
    )


def save_result(
    path: Path,
    result: GenerationResult,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            result.as_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )


# ============================================================
# CLI
# ============================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "MAVI AI Studio real Stable Audio worker"
        )
    )

    parser.add_argument(
        "--status",
        action="store_true",
    )

    parser.add_argument(
        "--request",
        default="",
    )

    parser.add_argument(
        "--prompt",
        default="",
    )

    parser.add_argument(
        "--output",
        default="",
    )

    parser.add_argument(
        "--seconds",
        type=float,
        default=DEFAULT_SECONDS,
    )

    parser.add_argument(
        "--duration",
        type=float,
        default=DEFAULT_SECONDS,
    )

    parser.add_argument(
        "--sample-rate",
        type=int,
        default=DEFAULT_SAMPLE_RATE,
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
        "--source",
        default="",
    )

    parser.add_argument(
        "--init-audio",
        default="",
    )

    parser.add_argument(
        "--init-noise-level",
        type=float,
        default=DEFAULT_INIT_NOISE_LEVEL,
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


def request_from_args(
    args: argparse.Namespace,
) -> GenerationRequest:

    return GenerationRequest(
        prompt=args.prompt,
        output=args.output,
        seconds=args.seconds,
        duration=args.duration,
        sample_rate=args.sample_rate,
        seed=args.seed,
        steps=args.steps,
        threads=args.threads,
        cfg=args.cfg,
        dit=args.dit,
        decoder=args.decoder,
        source=args.source,
        init_audio=args.init_audio,
        init_noise_level=(
            args.init_noise_level
        ),
        negative_prompt=(
            args.negative_prompt
        ),
    )


# ============================================================
# GLOBAL WORKER
# ============================================================

worker = RealAudioWorker()


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    parser = build_parser()

    args = parser.parse_args()

    if args.status:

        print(
            json.dumps(
                worker.status(),
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        return 0

    try:

        if args.request:

            request = load_json_request(
                Path(
                    args.request
                )
            )

        else:

            request = request_from_args(
                args
            )

        result = worker.generate(
            request
        )

    except Exception as exc:

        result = GenerationResult(
            success=False,
            error=(
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
            metadata={
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
                "placeholder_audio": False,
            },
        )

    print(
        json.dumps(
            result.as_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )

    if args.result:

        try:

            save_result(
                Path(
                    args.result
                )
                .expanduser()
                .resolve(),
                result,
            )

        except Exception as exc:

            print(
                (
                    "Result dosyası yazılamadı: "
                    f"{exc}"
                ),
                file=sys.stderr,
            )

            return 1

    return (
        0
        if result.success
        else 1
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )