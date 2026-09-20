# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
EXECUTE REAL GENERATION
v0.1
============================================================

Prod. By Ufuk Akdoğan

Prepared generation JSON -> Stable Audio 3 TFLite Runner.

BU DOSYA:
- yalnızca gerçek generation başlatır
- fake audio üretmez
- procedural audio üretmez
- placeholder audio üretmez
- başarısız backend durumunu gizlemez

Akış:

    prepared_generation.json
            |
            v
    execute_generation.py
            |
            v
    stable_audio_runner.py
            |
            v
    Stable Audio 3 TFLite
            |
            v
    Gerçek WAV
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


# ============================================================
# PATHS
# ============================================================

ROOT = (
    Path(__file__)
    .resolve()
    .parent
)

WORKER_PYTHON = (
    ROOT
    / ".worker_venv"
    / "Scripts"
    / "python.exe"
)

RUNNER = (
    ROOT
    / "stable_audio_runner.py"
)

DEFAULT_PREPARED = (
    ROOT
    / "output"
    / "prepared_generation.json"
)

DEFAULT_RESULT = (
    ROOT
    / "output"
    / "generation_result.json"
)


# ============================================================
# CONSTANTS
# ============================================================

VERSION = "0.1"

DEFAULT_TIMEOUT = 1800


# ============================================================
# ERRORS
# ============================================================

class ExecuteGenerationError(Exception):
    """Generation execution temel hatası."""


class ExecuteGenerationConfigError(
    ExecuteGenerationError
):
    """Generation executor yapılandırma hatası."""


class ExecuteGenerationProcessError(
    ExecuteGenerationError
):
    """Generation process hatası."""


class ExecuteGenerationOutputError(
    ExecuteGenerationError
):
    """Generation output hatası."""


# ============================================================
# DATA
# ============================================================

@dataclass
class ExecutionResult:

    success: bool

    output: str = ""

    result_file: str = ""

    returncode: int = -1

    elapsed_seconds: float = 0.0

    stdout: str = ""

    stderr: str = ""

    error: str = ""

    metadata: Dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(
        self,
    ) -> None:

        if self.metadata is None:

            self.metadata = {}

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "success": self.success,
            "output": self.output,
            "result_file": self.result_file,
            "returncode": self.returncode,
            "elapsed_seconds": self.elapsed_seconds,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "metadata": self.metadata,
        }


# ============================================================
# PREPARED REQUEST
# ============================================================

class PreparedRequest:

    def __init__(
        self,
        payload: Dict[str, Any],
    ) -> None:

        if not isinstance(
            payload,
            dict,
        ):

            raise ExecuteGenerationError(
                "Prepared generation JSON object olmalı."
            )

        self.payload = payload

        self.prompt = str(
            payload.get(
                "prompt",
                "",
            )
        ).strip()

        self.negative_prompt = str(
            payload.get(
                "negative_prompt",
                "",
            )
        ).strip()

        self.output = str(
            payload.get(
                "output",
                "",
            )
        ).strip()

        if not self.output:

            metadata = payload.get(
                "metadata",
                {},
            )

            if isinstance(
                metadata,
                dict,
            ):

                self.output = str(
                    metadata.get(
                        "output",
                        "",
                    )
                ).strip()

        self.seconds = float(
            payload.get(
                "seconds",
                30.0,
            )
        )

        self.seed = payload.get(
            "seed",
            None,
        )

        if self.seed is not None:

            self.seed = int(
                self.seed
            )

        self.dit = str(
            payload.get(
                "dit",
                "sm-music",
            )
        ).strip()

        self.decoder = str(
            payload.get(
                "decoder",
                "same-s",
            )
        ).strip()

        self.init_audio = str(
            payload.get(
                "init_audio",
                payload.get(
                    "source_path",
                    "",
                ),
            )
            or ""
        ).strip()

        self.init_noise_level = payload.get(
            "init_noise_level",
            None,
        )

        if self.init_noise_level is not None:

            self.init_noise_level = float(
                self.init_noise_level
            )

        self.inpaint_range = str(
            payload.get(
                "inpaint_range",
                "",
            )
            or ""
        ).strip()

        self.cfg = float(
            payload.get(
                "cfg",
                1.0,
            )
        )

        self.steps = int(
            payload.get(
                "steps",
                8,
            )
        )

        self.threads = int(
            payload.get(
                "threads",
                4,
            )
        )

        self.source = str(
            payload.get(
                "source",
                payload.get(
                    "source_path",
                    "",
                ),
            )
            or ""
        ).strip()

        self.mode = str(
            payload.get(
                "mode",
                "audio-to-audio",
            )
        ).strip()

        self.instruments = payload.get(
            "instruments",
            [],
        )

        self.preservation = float(
            payload.get(
                "preservation",
                0.90,
            )
        )

    def validate(
        self,
    ) -> None:

        if not self.prompt:

            raise ExecuteGenerationError(
                "Prepared prompt boş."
            )

        if not self.output:

            raise ExecuteGenerationError(
                (
                    "Prepared output yolu bulunamadı."
                )
            )

        if not (
            20.0
            <= self.seconds
            <= 120.0
        ):

            raise ExecuteGenerationError(
                (
                    "Generation süresi "
                    "20-120 saniye arasında olmalı."
                )
            )

        if self.steps < 1:

            raise ExecuteGenerationError(
                "Steps en az 1 olmalı."
            )

        if self.threads < 1:

            raise ExecuteGenerationError(
                "Threads en az 1 olmalı."
            )

        if self.cfg <= 0:

            raise ExecuteGenerationError(
                "CFG 0'dan büyük olmalı."
            )

        if self.init_noise_level is not None:

            if not (
                0.0
                < self.init_noise_level
                <= 1.0
            ):

                raise ExecuteGenerationError(
                    "Init noise level 0-1 arasında olmalı."
                )

        output_path = (
            Path(
                self.output
            )
            .expanduser()
            .resolve()
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.output = str(
            output_path
        )

        if self.init_audio:

            source_path = (
                Path(
                    self.init_audio
                )
                .expanduser()
                .resolve()
            )

            if not source_path.exists():

                raise ExecuteGenerationError(
                    (
                        "Init audio bulunamadı: "
                        f"{source_path}"
                    )
                )

            if not source_path.is_file():

                raise ExecuteGenerationError(
                    (
                        "Init audio dosya değil: "
                        f"{source_path}"
                    )
                )

            self.init_audio = str(
                source_path
            )

        if self.source:

            source_path = (
                Path(
                    self.source
                )
                .expanduser()
                .resolve()
            )

            if source_path.exists():

                self.source = str(
                    source_path
                )

    def runner_command(
        self,
    ) -> list[str]:

        command = [
            str(
                WORKER_PYTHON
            ),
            str(
                RUNNER
            ),

            "--prompt",
            self.prompt,

            "--output",
            self.output,

            "--seconds",
            str(
                self.seconds
            ),

            "--dit",
            self.dit,

            "--decoder",
            self.decoder,

            "--steps",
            str(
                self.steps
            ),

            "--threads",
            str(
                self.threads
            ),

            "--cfg",
            str(
                self.cfg
            ),
        ]

        if self.seed is not None:

            command.extend(
                [
                    "--seed",
                    str(
                        self.seed
                    ),
                ]
            )

        if self.negative_prompt:

            command.extend(
                [
                    "--negative-prompt",
                    self.negative_prompt,
                ]
            )

        if self.init_audio:

            command.extend(
                [
                    "--init-audio",
                    self.init_audio,
                ]
            )

            if self.init_noise_level is not None:

                command.extend(
                    [
                        "--init-noise-level",
                        str(
                            self.init_noise_level
                        ),
                    ]
                )

        if self.inpaint_range:

            command.extend(
                [
                    "--inpaint-range",
                    self.inpaint_range,
                ]
            )

        return command


# ============================================================
# LOADER
# ============================================================

def load_prepared_request(
    path: Path,
) -> PreparedRequest:

    if not path.exists():

        raise ExecuteGenerationError(
            (
                "Prepared generation dosyası "
                f"bulunamadı: {path}"
            )
        )

    try:

        payload = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )

    except OSError as exc:

        raise ExecuteGenerationError(
            (
                "Prepared generation okunamadı: "
                f"{exc}"
            )
        ) from exc

    except json.JSONDecodeError as exc:

        raise ExecuteGenerationError(
            (
                "Prepared generation JSON geçersiz: "
                f"{exc}"
            )
        ) from exc

    request = PreparedRequest(
        payload
    )

    request.validate()

    return request


# ============================================================
# PROCESS EXECUTOR
# ============================================================

class GenerationExecutor:

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:

        self.timeout = max(
            1,
            int(
                timeout
            ),
        )

    def run(
        self,
        request: PreparedRequest,
    ) -> ExecutionResult:

        if not WORKER_PYTHON.exists():

            raise ExecuteGenerationConfigError(
                (
                    "Worker Python bulunamadı: "
                    f"{WORKER_PYTHON}"
                )
            )

        if not RUNNER.exists():

            raise ExecuteGenerationConfigError(
                (
                    "Stable Audio runner bulunamadı: "
                    f"{RUNNER}"
                )
            )

        command = request.runner_command()

        started = (
            time.perf_counter()
        )

        try:

            process = subprocess.run(
                command,
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

            return ExecutionResult(
                success=False,
                output=request.output,
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
                error=(
                    f"Generation timeout "
                    f"({self.timeout} saniye)."
                ),
                metadata={
                    "command": command,
                    "real_generation": True,
                    "fake_audio": False,
                    "procedural_audio": False,
                },
            )

        except OSError as exc:

            elapsed = (
                time.perf_counter()
                - started
            )

            return ExecutionResult(
                success=False,
                output=request.output,
                returncode=-1,
                elapsed_seconds=round(
                    elapsed,
                    3,
                ),
                error=(
                    f"Process başlatılamadı: "
                    f"{exc}"
                ),
                metadata={
                    "command": command,
                    "real_generation": True,
                    "fake_audio": False,
                    "procedural_audio": False,
                },
            )

        elapsed = (
            time.perf_counter()
            - started
        )

        output_path = (
            Path(
                request.output
            )
            .expanduser()
            .resolve()
        )

        output_exists = (
            output_path.exists()
            and output_path.is_file()
            and output_path.stat().st_size > 0
        )

        success = (
            process.returncode == 0
            and output_exists
        )

        if not success:

            error = (
                "Stable Audio generation başarısız."
            )

            if (
                process.returncode == 0
                and not output_exists
            ):

                error = (
                    "Stable Audio başarılı "
                    "dönüş verdi ancak WAV output "
                    "oluşmadı."
                )

            return ExecutionResult(
                success=False,
                output=(
                    str(output_path)
                    if output_exists
                    else ""
                ),
                returncode=process.returncode,
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
                error=error,
                metadata={
                    "command": command,
                    "real_generation": True,
                    "fake_audio": False,
                    "procedural_audio": False,
                },
            )

        output_info = (
            inspect_wav(
                output_path
            )
        )

        return ExecutionResult(
            success=True,
            output=str(
                output_path
            ),
            returncode=process.returncode,
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
            metadata={
                "command": command,
                "request_mode": request.mode,
                "source": request.source,
                "source_preservation": (
                    request.preservation
                ),
                "instruments": request.instruments,
                "negative_prompt": (
                    request.negative_prompt
                ),
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
                "placeholder_audio": False,
                "output_info": output_info,
            },
        )


# ============================================================
# WAV INSPECTOR
# ============================================================

def inspect_wav(
    path: Path,
) -> Dict[str, Any]:

    if not path.exists():

        raise ExecuteGenerationOutputError(
            (
                "Output WAV bulunamadı: "
                f"{path}"
            )
        )

    try:

        import wave

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

            duration = (
                frames / sample_rate
                if sample_rate > 0
                else 0.0
            )

    except Exception as exc:

        raise ExecuteGenerationOutputError(
            (
                "Output WAV okunamadı: "
                f"{exc}"
            )
        ) from exc

    if channels <= 0:

        raise ExecuteGenerationOutputError(
            "Output WAV channel sayısı geçersiz."
        )

    if sample_rate <= 0:

        raise ExecuteGenerationOutputError(
            "Output WAV sample rate geçersiz."
        )

    if frames <= 0:

        raise ExecuteGenerationOutputError(
            "Output WAV frame sayısı geçersiz."
        )

    if duration <= 0:

        raise ExecuteGenerationOutputError(
            "Output WAV süresi geçersiz."
        )

    return {
        "path": str(
            path
        ),
        "channels": channels,
        "sample_rate": sample_rate,
        "sample_width": sample_width,
        "frames": frames,
        "duration_seconds": duration,
        "size_bytes": path.stat().st_size,
    }


# ============================================================
# SAVE RESULT
# ============================================================

def save_execution_result(
    result: ExecutionResult,
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


# ============================================================
# CLI
# ============================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "MAVI AI Studio real generation executor"
        )
    )

    parser.add_argument(
        "--prepared",
        type=str,
        default=str(
            DEFAULT_PREPARED
        ),
    )

    parser.add_argument(
        "--result",
        type=str,
        default=str(
            DEFAULT_RESULT
        ),
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
    )

    return parser


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    parser = (
        build_parser()
    )

    args = parser.parse_args()

    try:

        prepared_path = (
            Path(
                args.prepared
            )
            .expanduser()
            .resolve()
        )

        result_path = (
            Path(
                args.result
            )
            .expanduser()
            .resolve()
        )

        request = load_prepared_request(
            prepared_path
        )

        print()
        print(
            "============================================================"
        )
        print(
            "MAVI AI STUDIO"
        )
        print(
            "REAL GENERATION"
        )
        print(
            "============================================================"
        )
        print()

        print(
            f"MODE    : {request.mode}"
        )

        print(
            f"SECONDS : {request.seconds}"
        )

        print(
            f"DiT     : {request.dit}"
        )

        print(
            f"DECODER : {request.decoder}"
        )

        print(
            f"OUTPUT  : {request.output}"
        )

        if request.init_audio:

            print(
                f"SOURCE  : {request.init_audio}"
            )

        print()

        result = GenerationExecutor(
            timeout=args.timeout
        ).run(
            request
        )

        save_execution_result(
            result,
            result_path,
        )

        print(
            "============================================================"
        )

        if result.success:

            print(
                "REAL GENERATION: SUCCESS"
            )

            print()

            print(
                f"OUTPUT: {result.output}"
            )

            print(
                f"TIME  : "
                f"{result.elapsed_seconds:.2f}s"
            )

            output_info = (
                result.metadata.get(
                    "output_info",
                    {},
                )
            )

            if output_info:

                print(
                    f"DURATION: "
                    f"{output_info.get('duration_seconds', 0):.2f}s"
                )

                print(
                    f"SAMPLE RATE: "
                    f"{output_info.get('sample_rate', 0)}"
                )

        else:

            print(
                "REAL GENERATION: FAILED"
            )

            print()

            print(
                f"ERROR: {result.error}"
            )

            if result.stderr:

                print()
                print(
                    "STDERR:"
                )

                print(
                    result.stderr[-5000:]
                )

        print()

        print(
            f"RESULT JSON: {result_path}"
        )

        print(
            "============================================================"
        )
        print()

        return (
            0
            if result.success
            else 1
        )

    except Exception as exc:

        result = ExecutionResult(
            success=False,
            returncode=-1,
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

        try:

            save_execution_result(
                result,
                Path(
                    args.result
                )
                .expanduser()
                .resolve(),
            )

        except Exception:

            pass

        print()
        print(
            "REAL GENERATION: FAILED"
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