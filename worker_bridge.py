# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
WORKER BRIDGE
v0.2
============================================================

Prod. By Ufuk Akdoğan

Main Python 3.14 engine ile gerçek Stable Audio worker
arasındaki tek köprü.

Amaç:
- Worker'ı tek noktadan yönetmek
- JSON request göndermek
- stdout / stderr toplamak
- Gerçek WAV çıktısını doğrulamak
- Worker başarısızsa başarısız dönmek
- Fake / procedural / placeholder audio üretmemek
"""

from __future__ import annotations

import json
import os
import subprocess
import threading
import time

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent

WORKER_SCRIPT = (
    ROOT / "worker.py"
)

STABLE_AUDIO_RUNNER = (
    ROOT / "stable_audio_runner.py"
)

DEFAULT_WORKER_PYTHON = (
    ROOT
    / ".worker_venv"
    / "Scripts"
    / "python.exe"
)


# ============================================================
# CONSTANTS
# ============================================================

BRIDGE_VERSION = "0.2"

DEFAULT_TIMEOUT = 1800

DEFAULT_POLL_SECONDS = 0.25

ALLOWED_OUTPUT_EXTENSIONS = (
    ".wav",
)

FAKE_AUDIO_ALLOWED = False

PROCEDURAL_AUDIO_ALLOWED = False

PLACEHOLDER_AUDIO_ALLOWED = False


# ============================================================
# ERRORS
# ============================================================

class WorkerBridgeError(Exception):
    pass


class WorkerUnavailable(
    WorkerBridgeError
):
    pass


class WorkerRequestError(
    WorkerBridgeError
):
    pass


class WorkerExecutionError(
    WorkerBridgeError
):
    pass


class WorkerOutputError(
    WorkerBridgeError
):
    pass


# ============================================================
# RESULT
# ============================================================

@dataclass
class WorkerResult:

    success: bool = False

    output: str = ""

    returncode: int = -1

    elapsed_seconds: float = 0.0

    stdout: str = ""

    stderr: str = ""

    error: str = ""

    request: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "success": self.success,
            "output": self.output,
            "returncode": self.returncode,
            "elapsed_seconds": (
                self.elapsed_seconds
            ),
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "request": self.request,
            "metadata": self.metadata,
        }


# ============================================================
# CONFIG
# ============================================================

def _env(
    name: str,
    default: str = "",
) -> str:

    return os.getenv(
        name,
        default,
    ).strip()


def resolve_worker_python() -> Path:

    configured = _env(
        "MAVI_WORKER_PYTHON"
    )

    candidates = []

    if configured:

        candidates.append(
            Path(configured)
        )

    candidates.extend(
        [
            DEFAULT_WORKER_PYTHON,
        ]
    )

    for candidate in candidates:

        try:

            path = (
                candidate
                .expanduser()
                .resolve()
            )

            if (
                path.exists()
                and path.is_file()
            ):

                return path

        except Exception:

            continue

    raise WorkerUnavailable(
        (
            "Worker Python bulunamadı. "
            f"Beklenen yol: {DEFAULT_WORKER_PYTHON}"
        )
    )


# ============================================================
# WORKER SCRIPT
# ============================================================

def resolve_worker_script() -> Path:

    configured = _env(
        "MAVI_WORKER_SCRIPT"
    )

    candidates = []

    if configured:

        candidates.append(
            Path(configured)
        )

    candidates.extend(
        [
            WORKER_SCRIPT,
            STABLE_AUDIO_RUNNER,
        ]
    )

    for candidate in candidates:

        try:

            path = (
                candidate
                .expanduser()
                .resolve()
            )

            if (
                path.exists()
                and path.is_file()
            ):

                return path

        except Exception:

            continue

    raise WorkerUnavailable(
        (
            "Worker script bulunamadı. "
            f"Beklenen ana dosya: {WORKER_SCRIPT}"
        )
    )


# ============================================================
# REQUEST
# ============================================================

class WorkerRequest:

    def __init__(
        self,
        *,
        prompt: str,
        output: str,
        seconds: float,
        sample_rate: int = 48000,
        seed: int = 314159,
        steps: int = 8,
        threads: int = 4,
        cfg: float = 1.0,
        dit: str = "sm-music",
        decoder: str = "same-s",
        source: str = "",
        init_audio: str = "",
        init_noise_level: float = 0.20,
        negative_prompt: str = "",
        mode: str = "audio-to-audio",
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        self.prompt = str(
            prompt or ""
        ).strip()

        self.output = str(
            output or ""
        ).strip()

        self.seconds = float(
            seconds
        )

        self.sample_rate = int(
            sample_rate
        )

        self.seed = int(
            seed
        )

        self.steps = int(
            steps
        )

        self.threads = max(
            1,
            int(
                threads
            ),
        )

        self.cfg = float(
            cfg
        )

        self.dit = str(
            dit
            or "sm-music"
        ).strip()

        self.decoder = str(
            decoder
            or "same-s"
        ).strip()

        self.source = str(
            source
            or ""
        ).strip()

        self.init_audio = str(
            init_audio
            or self.source
        ).strip()

        self.init_noise_level = float(
            init_noise_level
        )

        self.negative_prompt = str(
            negative_prompt
            or ""
        ).strip()

        self.mode = str(
            mode
            or (
                "audio-to-audio"
                if self.init_audio
                else "text-to-audio"
            )
        ).strip()

        self.metadata = (
            metadata
            or {}
        )

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "prompt": self.prompt,
            "output": self.output,
            "seconds": self.seconds,
            "sample_rate": self.sample_rate,
            "seed": self.seed,
            "steps": self.steps,
            "threads": self.threads,
            "cfg": self.cfg,
            "dit": self.dit,
            "decoder": self.decoder,
            "source": self.source,
            "init_audio": self.init_audio,
            "init_noise_level": (
                self.init_noise_level
            ),
            "negative_prompt": (
                self.negative_prompt
            ),
            "mode": self.mode,
            "metadata": self.metadata,
        }


# ============================================================
# VALIDATION
# ============================================================

def validate_request(
    request: WorkerRequest,
) -> None:

    if not request.prompt:

        raise WorkerRequestError(
            "Worker prompt boş."
        )

    if not request.output:

        raise WorkerRequestError(
            "Worker output boş."
        )

    if not (
        20.0
        <= request.seconds
        <= 120.0
    ):

        raise WorkerRequestError(
            "Worker süresi 20-120 saniye arasında olmalı."
        )

    if request.sample_rate <= 0:

        raise WorkerRequestError(
            "Sample rate geçersiz."
        )

    if request.steps <= 0:

        raise WorkerRequestError(
            "Steps geçersiz."
        )

    if request.cfg <= 0:

        raise WorkerRequestError(
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

            raise WorkerRequestError(
                (
                    "Init audio bulunamadı: "
                    f"{source}"
                )
            )

        if not source.is_file():

            raise WorkerRequestError(
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
# OUTPUT VALIDATION
# ============================================================

def validate_output(
    output: str | Path,
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
                "Worker output bulunamadı: "
                f"{path}"
            )
        )

    if not path.is_file():

        raise WorkerOutputError(
            (
                "Worker output dosya değil: "
                f"{path}"
            )
        )

    if path.stat().st_size <= 0:

        raise WorkerOutputError(
            (
                "Worker output boş: "
                f"{path}"
            )
        )

    if path.suffix.lower() not in (
        ALLOWED_OUTPUT_EXTENSIONS
    ):

        raise WorkerOutputError(
            (
                "Worker output WAV olmalı: "
                f"{path}"
            )
        )

    import wave

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

            duration = (
                frames / sample_rate
                if sample_rate > 0
                else 0.0
            )

    except Exception as exc:

        raise WorkerOutputError(
            (
                "Worker WAV doğrulanamadı: "
                f"{exc}"
            )
        ) from exc

    if channels <= 0:

        raise WorkerOutputError(
            "WAV kanal bilgisi geçersiz."
        )

    if sample_rate <= 0:

        raise WorkerOutputError(
            "WAV sample rate geçersiz."
        )

    if frames <= 0:

        raise WorkerOutputError(
            "WAV frame bilgisi geçersiz."
        )

    if duration <= 0:

        raise WorkerOutputError(
            "WAV süresi geçersiz."
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
# BRIDGE
# ============================================================

class WorkerBridge:

    def __init__(
        self,
        *,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:

        self.timeout = max(
            1,
            int(timeout),
        )

        self._lock = (
            threading.RLock()
        )

        self._process: Optional[
            subprocess.Popen
        ] = None

        self._stop_event = (
            threading.Event()
        )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    def status(
        self,
    ) -> Dict[str, Any]:

        worker_python = ""

        worker_python_ok = False

        worker_error = ""

        try:

            path = (
                resolve_worker_python()
            )

            worker_python = str(
                path
            )

            worker_python_ok = True

        except Exception as exc:

            worker_error = str(
                exc
            )

        worker_script = ""

        worker_script_ok = False

        script_error = ""

        try:

            path = (
                resolve_worker_script()
            )

            worker_script = str(
                path
            )

            worker_script_ok = True

        except Exception as exc:

            script_error = str(
                exc
            )

        return {
            "bridge_version": BRIDGE_VERSION,
            "ready": (
                worker_python_ok
                and worker_script_ok
            ),
            "worker_python": (
                worker_python
            ),
            "worker_python_ok": (
                worker_python_ok
            ),
            "worker_error": (
                worker_error
            ),
            "worker_script": (
                worker_script
            ),
            "worker_script_ok": (
                worker_script_ok
            ),
            "script_error": (
                script_error
            ),
            "real_generation": True,
            "fake_audio": False,
            "procedural_audio": False,
            "placeholder_audio": False,
        }

    # --------------------------------------------------------
    # COMMAND
    # --------------------------------------------------------

    def build_command(
        self,
        request: WorkerRequest,
    ) -> List[str]:

        validate_request(
            request
        )

        python_path = (
            resolve_worker_python()
        )

        script_path = (
            resolve_worker_script()
        )

        command = [
            str(python_path),
            str(script_path),
            "--prompt",
            request.prompt,
            "--output",
            request.output,
            "--seconds",
            str(
                request.seconds
            ),
            "--sample-rate",
            str(
                request.sample_rate
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

    # --------------------------------------------------------
    # STOP
    # --------------------------------------------------------

    def stop(
        self,
    ) -> None:

        self._stop_event.set()

        with self._lock:

            process = self._process

        if process is None:

            return

        try:

            if process.poll() is None:

                process.terminate()

                try:

                    process.wait(
                        timeout=5
                    )

                except subprocess.TimeoutExpired:

                    process.kill()

        except Exception:

            pass

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    def run(
        self,
        request: WorkerRequest,
    ) -> WorkerResult:

        self._stop_event.clear()

        validate_request(
            request
        )

        command = (
            self.build_command(
                request
            )
        )

        started = (
            time.perf_counter()
        )

        process: Optional[
            subprocess.Popen
        ] = None

        try:

            process = subprocess.Popen(
                command,
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            with self._lock:

                self._process = process

            try:

                stdout, stderr = (
                    process.communicate(
                        timeout=self.timeout
                    )
                )

            except subprocess.TimeoutExpired:

                self.stop()

                stdout, stderr = (
                    process.communicate()
                )

                elapsed = (
                    time.perf_counter()
                    - started
                )

                return WorkerResult(
                    success=False,
                    output="",
                    returncode=-2,
                    elapsed_seconds=round(
                        elapsed,
                        3,
                    ),
                    stdout=(
                        stdout
                        or ""
                    ),
                    stderr=(
                        stderr
                        or ""
                    ),
                    error=(
                        "Worker timeout."
                    ),
                    request=request.as_dict(),
                    metadata={
                        "command": command,
                        "real_generation": True,
                    },
                )

            elapsed = (
                time.perf_counter()
                - started
            )

            returncode = (
                process.returncode
            )

            if self._stop_event.is_set():

                return WorkerResult(
                    success=False,
                    output="",
                    returncode=returncode,
                    elapsed_seconds=round(
                        elapsed,
                        3,
                    ),
                    stdout=(
                        stdout
                        or ""
                    ),
                    stderr=(
                        stderr
                        or ""
                    ),
                    error=(
                        "Worker durduruldu."
                    ),
                    request=request.as_dict(),
                    metadata={
                        "command": command,
                        "real_generation": True,
                    },
                )

            if returncode != 0:

                return WorkerResult(
                    success=False,
                    output="",
                    returncode=returncode,
                    elapsed_seconds=round(
                        elapsed,
                        3,
                    ),
                    stdout=(
                        stdout
                        or ""
                    ),
                    stderr=(
                        stderr
                        or ""
                    ),
                    error=(
                        "Worker process başarısız."
                    ),
                    request=request.as_dict(),
                    metadata={
                        "command": command,
                        "real_generation": True,
                    },
                )

            try:

                info = (
                    validate_output(
                        request.output
                    )
                )

            except WorkerOutputError as exc:

                return WorkerResult(
                    success=False,
                    output="",
                    returncode=returncode,
                    elapsed_seconds=round(
                        elapsed,
                        3,
                    ),
                    stdout=(
                        stdout
                        or ""
                    ),
                    stderr=(
                        stderr
                        or ""
                    ),
                    error=str(
                        exc
                    ),
                    request=request.as_dict(),
                    metadata={
                        "command": command,
                        "real_generation": True,
                    },
                )

            return WorkerResult(
                success=True,
                output=str(
                    info["path"]
                ),
                returncode=returncode,
                elapsed_seconds=round(
                    elapsed,
                    3,
                ),
                stdout=(
                    stdout
                    or ""
                ),
                stderr=(
                    stderr
                    or ""
                ),
                request=request.as_dict(),
                metadata={
                    "command": command,
                    "output_info": info,
                    "real_generation": True,
                    "fake_audio": False,
                    "procedural_audio": False,
                    "placeholder_audio": False,
                },
            )

        except OSError as exc:

            elapsed = (
                time.perf_counter()
                - started
            )

            return WorkerResult(
                success=False,
                output="",
                returncode=-1,
                elapsed_seconds=round(
                    elapsed,
                    3,
                ),
                error=(
                    "Worker başlatılamadı: "
                    f"{exc}"
                ),
                request=request.as_dict(),
                metadata={
                    "command": command,
                    "real_generation": True,
                },
            )

        except Exception as exc:

            elapsed = (
                time.perf_counter()
                - started
            )

            return WorkerResult(
                success=False,
                output="",
                returncode=-1,
                elapsed_seconds=round(
                    elapsed,
                    3,
                ),
                error=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
                request=request.as_dict(),
                metadata={
                    "command": command,
                    "real_generation": True,
                },
            )

        finally:

            with self._lock:

                self._process = None


# ============================================================
# GLOBAL
# ============================================================

bridge = WorkerBridge()


# ============================================================
# PUBLIC API
# ============================================================

def worker_status() -> Dict[str, Any]:

    return bridge.status()


def run_worker(
    *,
    prompt: str,
    output: str,
    seconds: float = 30.0,
    sample_rate: int = 48000,
    seed: int = 314159,
    steps: int = 8,
    threads: int = 4,
    cfg: float = 1.0,
    dit: str = "sm-music",
    decoder: str = "same-s",
    source: str = "",
    init_audio: str = "",
    init_noise_level: float = 0.20,
    negative_prompt: str = "",
    mode: str = "audio-to-audio",
    metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> WorkerResult:

    request = WorkerRequest(
        prompt=prompt,
        output=output,
        seconds=seconds,
        sample_rate=sample_rate,
        seed=seed,
        steps=steps,
        threads=threads,
        cfg=cfg,
        dit=dit,
        decoder=decoder,
        source=source,
        init_audio=init_audio,
        init_noise_level=init_noise_level,
        negative_prompt=negative_prompt,
        mode=mode,
        metadata=(
            metadata
            or {}
        ),
    )

    return bridge.run(
        request
    )


def stop_worker() -> None:

    bridge.stop()


# ============================================================
# JSON REQUEST
# ============================================================

def run_worker_request(
    request_data: Dict[str, Any],
) -> WorkerResult:

    if not isinstance(
        request_data,
        dict,
    ):

        raise WorkerRequestError(
            "Worker request dict olmalı."
        )

    return run_worker(
        prompt=str(
            request_data.get(
                "prompt",
                "",
            )
        ),
        output=str(
            request_data.get(
                "output",
                request_data.get(
                    "output_path",
                    "",
                ),
            )
        ),
        seconds=float(
            request_data.get(
                "seconds",
                30.0,
            )
        ),
        sample_rate=int(
            request_data.get(
                "sample_rate",
                48000,
            )
        ),
        seed=int(
            request_data.get(
                "seed",
                314159,
            )
        ),
        steps=int(
            request_data.get(
                "steps",
                8,
            )
        ),
        threads=int(
            request_data.get(
                "threads",
                4,
            )
        ),
        cfg=float(
            request_data.get(
                "cfg",
                1.0,
            )
        ),
        dit=str(
            request_data.get(
                "dit",
                "sm-music",
            )
        ),
        decoder=str(
            request_data.get(
                "decoder",
                "same-s",
            )
        ),
        source=str(
            request_data.get(
                "source",
                request_data.get(
                    "source_path",
                    "",
                ),
            )
        ),
        init_audio=str(
            request_data.get(
                "init_audio",
                "",
            )
        ),
        init_noise_level=float(
            request_data.get(
                "init_noise_level",
                0.20,
            )
        ),
        negative_prompt=str(
            request_data.get(
                "negative_prompt",
                "",
            )
        ),
        mode=str(
            request_data.get(
                "mode",
                "audio-to-audio",
            )
        ),
        metadata=request_data.get(
            "metadata",
            {},
        ),
    )


# ============================================================
# CLI
# ============================================================

def main() -> int:

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "MAVI AI Studio Worker Bridge"
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
        "--source",
        default="",
    )

    parser.add_argument(
        "--seconds",
        type=float,
        default=30.0,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=314159,
    )

    args = parser.parse_args()

    if args.status:

        print(
            json.dumps(
                worker_status(),
                ensure_ascii=False,
                indent=2,
            )
        )

        return 0

    if args.request:

        request_path = (
            Path(
                args.request
            )
            .expanduser()
            .resolve()
        )

        if not request_path.exists():

            print(
                json.dumps(
                    {
                        "success": False,
                        "error": (
                            "Request JSON bulunamadı."
                        ),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )

            return 1

        try:

            payload = json.loads(
                request_path.read_text(
                    encoding="utf-8"
                )
            )

            result = run_worker_request(
                payload
            )

        except Exception as exc:

            print(
                json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"{type(exc).__name__}: "
                            f"{exc}"
                        ),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )

            return 1

    else:

        if not args.prompt:

            print(
                json.dumps(
                    {
                        "success": False,
                        "error": (
                            "Prompt gerekli."
                        ),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )

            return 1

        if not args.output:

            print(
                json.dumps(
                    {
                        "success": False,
                        "error": (
                            "Output gerekli."
                        ),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )

            return 1

        result = run_worker(
            prompt=args.prompt,
            output=args.output,
            seconds=args.seconds,
            seed=args.seed,
            source=args.source,
        )

    print(
        json.dumps(
            result.as_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )

    return (
        0
        if result.success
        else 1
    )


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )