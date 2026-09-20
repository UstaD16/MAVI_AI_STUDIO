# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
STABLE AUDIO 3 TFLITE RUNNER
v0.1
============================================================

Prod. By Ufuk Akdoğan

MAVI AI Studio -> gerçek Stable Audio 3 TFLite CLI köprüsü.

Windows / CPU yolu:

    Stable Audio 3
        optimized/tflite
            sa3.bat
                scripts/sa3_tflite.py
                    LiteRT / XNNPACK
                        WAV

Desteklenen işlemler:

- text-to-audio
- audio-to-audio
- inpainting
- negatif prompt
- CFG
- seed
- gerçek WAV output

FAKE / PROCEDURAL / PLACEHOLDER AUDIO YOKTUR.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# CONSTANTS
# ============================================================

RUNNER_VERSION = "0.1"

ENV_STABLE_AUDIO_3_DIR = (
    "MAVI_STABLE_AUDIO_3_DIR"
)

ENV_STABLE_AUDIO_CLI = (
    "MAVI_STABLE_AUDIO_CLI"
)

ENV_STABLE_AUDIO_THREADS = (
    "MAVI_STABLE_AUDIO_THREADS"
)

DEFAULT_THREADS = 4

DEFAULT_DIT = "sm-music"
DEFAULT_DECODER = "same-s"

SUPPORTED_DIT = (
    "sm-music",
    "sm-sfx",
    "medium",
)

SUPPORTED_DECODER = (
    "same-s",
    "same-l",
)

MIN_SECONDS = 20.0
MAX_SECONDS = 120.0


# ============================================================
# ERRORS
# ============================================================

class StableAudioRunnerError(
    Exception
):
    """Runner temel hatası."""


class StableAudioCliNotFound(
    StableAudioRunnerError
):
    """sa3.bat bulunamadı."""


class StableAudioRunError(
    StableAudioRunnerError
):
    """Stable Audio CLI çalıştırma hatası."""


class StableAudioOutputError(
    StableAudioRunnerError
):
    """Stable Audio output hatası."""


# ============================================================
# REQUEST
# ============================================================

@dataclass
class StableAudioRunRequest:

    prompt: str

    output: str

    seconds: float = 30.0

    seed: Optional[int] = None

    dit: str = DEFAULT_DIT

    decoder: str = DEFAULT_DECODER

    init_audio: str = ""

    init_noise_level: Optional[float] = None

    inpaint_range: str = ""

    negative_prompt: str = ""

    cfg: float = 1.0

    steps: int = 8

    threads: int = DEFAULT_THREADS

    source: str = ""

    metadata: Dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(
        self,
    ) -> None:

        self.prompt = str(
            self.prompt
        ).strip()

        self.output = str(
            self.output
        ).strip()

        self.seconds = float(
            self.seconds
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
# RESULT
# ============================================================

@dataclass
class StableAudioRunResult:

    success: bool

    output: str = ""

    elapsed_seconds: float = 0.0

    returncode: int = -1

    cli_path: str = ""

    dit: str = ""

    decoder: str = ""

    seconds: float = 0.0

    seed: Optional[int] = None

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

        return asdict(
            self
        )


# ============================================================
# CLI DISCOVERY
# ============================================================

class StableAudioCliLocator:

    def __init__(
        self,
    ) -> None:

        self.env_root = (
            os.getenv(
                ENV_STABLE_AUDIO_3_DIR,
                "",
            ).strip()
        )

        self.env_cli = (
            os.getenv(
                ENV_STABLE_AUDIO_CLI,
                "",
            ).strip()
        )

    # --------------------------------------------------------
    # CANDIDATES
    # --------------------------------------------------------

    def candidates(
        self,
    ) -> List[Path]:

        candidates: List[Path] = []

        if self.env_cli:

            candidates.append(
                Path(
                    self.env_cli
                ).expanduser()
            )

        if self.env_root:

            root = (
                Path(
                    self.env_root
                ).expanduser()
            )

            candidates.extend(
                [
                    root / "sa3.bat",
                    root
                    / "optimized"
                    / "tflite"
                    / "sa3.bat",
                ]
            )

        home = Path.home()

        desktop = (
            home
            / "Desktop"
        )

        desktop_candidates = [
            desktop
            / "stable-audio-3"
            / "optimized"
            / "tflite"
            / "sa3.bat",

            desktop
            / "stable_audio_3"
            / "optimized"
            / "tflite"
            / "sa3.bat",

            desktop
            / "stable-audio-3"
            / "tflite"
            / "sa3.bat",
        ]

        candidates.extend(
            desktop_candidates
        )

        cwd = Path.cwd()

        candidates.extend(
            [
                cwd / "sa3.bat",
                cwd
                / "optimized"
                / "tflite"
                / "sa3.bat",
                cwd
                / "stable-audio-3"
                / "optimized"
                / "tflite"
                / "sa3.bat",
            ]
        )

        return candidates

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    def recursive_desktop_search(
        self,
    ) -> Optional[Path]:

        desktop = (
            Path.home()
            / "Desktop"
        )

        if not desktop.exists():
            return None

        # Known official filename.
        try:

            matches = list(
                desktop.glob(
                    "**/optimized/tflite/sa3.bat"
                )
            )

        except OSError:

            return None

        if matches:

            # Prefer repository names.
            preferred = [
                item
                for item in matches
                if "stable-audio-3"
                in str(item).lower()
            ]

            if preferred:
                return preferred[0]

            return matches[0]

        return None

    # --------------------------------------------------------
    # LOCATE
    # --------------------------------------------------------

    def locate(
        self,
    ) -> Path:

        for candidate in self.candidates():

            try:

                resolved = (
                    candidate.expanduser().resolve()
                )

            except OSError:

                continue

            if (
                resolved.exists()
                and resolved.is_file()
                and resolved.name.lower()
                == "sa3.bat"
            ):

                return resolved

        recursive = (
            self.recursive_desktop_search()
        )

        if recursive:

            return recursive.resolve()

        raise StableAudioCliNotFound(
            (
                "Stable Audio 3 TFLite "
                "sa3.bat bulunamadı.\n"
                f"Environment ile açıkça belirtebilirsiniz: "
                f"{ENV_STABLE_AUDIO_3_DIR}"
            )
        )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_request(
    request: StableAudioRunRequest,
) -> Path:

    if not request.prompt:

        raise StableAudioRunError(
            "Prompt boş."
        )

    if request.seconds < MIN_SECONDS:

        raise StableAudioRunError(
            (
                "Stable Audio 3 TFLite için "
                f"minimum önerilen süre {MIN_SECONDS:.0f}s."
            )
        )

    if request.seconds > MAX_SECONDS:

        raise StableAudioRunError(
            (
                "Tek generation maksimum "
                f"{MAX_SECONDS:.0f}s."
            )
        )

    if request.dit not in SUPPORTED_DIT:

        raise StableAudioRunError(
            (
                f"Geçersiz DiT: {request.dit}"
            )
        )

    if request.decoder not in SUPPORTED_DECODER:

        raise StableAudioRunError(
            (
                f"Geçersiz decoder: {request.decoder}"
            )
        )

    if (
        request.dit == "medium"
        and request.decoder != "same-l"
    ):

        request.decoder = "same-l"

    if (
        request.dit != "medium"
        and request.decoder == "same-l"
    ):

        request.decoder = "same-s"

    if request.steps < 1:

        raise StableAudioRunError(
            "Steps en az 1 olmalı."
        )

    if request.cfg <= 0:

        raise StableAudioRunError(
            "CFG 0'dan büyük olmalı."
        )

    if (
        request.init_noise_level is not None
        and not (
            0.0
            < request.init_noise_level
            <= 1.0
        )
    ):

        raise StableAudioRunError(
            "init-noise-level 0 ile 1 arasında olmalı."
        )

    if request.inpaint_range:

        if not request.init_audio:

            raise StableAudioRunError(
                (
                    "Inpainting için "
                    "--init-audio gerekli."
                )
            )

        parts = (
            request.inpaint_range.split(
                ","
            )
        )

        if len(parts) != 2:

            raise StableAudioRunError(
                (
                    "Inpaint aralığı "
                    "'START,END' biçiminde olmalı."
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

            raise StableAudioRunError(
                "Inpaint aralığı sayısal olmalı."
            ) from exc

        if not (
            0.0
            <= start
            < end
            <= request.seconds
        ):

            raise StableAudioRunError(
                (
                    "Geçersiz inpaint aralığı: "
                    f"{start},{end}"
                )
            )

    if request.init_audio:

        init_path = (
            Path(
                request.init_audio
            )
            .expanduser()
            .resolve()
        )

        if not init_path.exists():

            raise StableAudioRunError(
                (
                    "Init audio bulunamadı: "
                    f"{init_path}"
                )
            )

        if not init_path.is_file():

            raise StableAudioRunError(
                (
                    "Init audio dosya değil: "
                    f"{init_path}"
                )
            )

        request.init_audio = str(
            init_path
        )

    output_path = (
        Path(
            request.output
        )
        .expanduser()
        .resolve()
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    request.output = str(
        output_path
    )

    return output_path


# ============================================================
# COMMAND
# ============================================================

class StableAudioCommand:

    def build(
        self,
        cli_path: Path,
        request: StableAudioRunRequest,
    ) -> List[str]:

        command: List[str] = [
            "cmd.exe",
            "/d",
            "/c",
            str(
                cli_path
            ),

            "--prompt",
            request.prompt,

            "--dit",
            request.dit,

            "--decoder",
            request.decoder,

            "--seconds",
            str(
                request.seconds
            ),

            "--steps",
            str(
                request.steps
            ),

            "--threads",
            str(
                request.threads
            ),

            "--out",
            request.output,
        ]

        if request.seed is not None:

            command.extend(
                [
                    "--seed",
                    str(
                        request.seed
                    ),
                ]
            )

        if request.init_audio:

            command.extend(
                [
                    "--init-audio",
                    request.init_audio,
                ]
            )

            if (
                request.init_noise_level
                is not None
            ):

                command.extend(
                    [
                        "--init-noise-level",
                        str(
                            request.init_noise_level
                        ),
                    ]
                )

        if request.inpaint_range:

            command.extend(
                [
                    "--inpaint-range",
                    request.inpaint_range,
                ]
            )

        if request.negative_prompt:

            command.extend(
                [
                    "--negative-prompt",
                    request.negative_prompt,
                ]
            )

        if request.cfg != 1.0:

            command.extend(
                [
                    "--cfg",
                    str(
                        request.cfg
                    ),
                ]
            )

        return command


# ============================================================
# OUTPUT VALIDATOR
# ============================================================

def validate_output(
    path: Path,
) -> Dict[str, Any]:

    if not path.exists():

        raise StableAudioOutputError(
            (
                "Stable Audio çıktı üretmedi: "
                f"{path}"
            )
        )

    if not path.is_file():

        raise StableAudioOutputError(
            (
                "Stable Audio çıktısı dosya değil: "
                f"{path}"
            )
        )

    size = (
        path.stat().st_size
    )

    if size <= 0:

        raise StableAudioOutputError(
            (
                "Stable Audio çıktı dosyası boş."
            )
        )

    wav_info = {
        "size_bytes": size,
        "extension": (
            path.suffix.lower()
        ),
    }

    # WAV header / duration verification.
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

            duration = (
                frames / sample_rate
                if sample_rate
                else 0.0
            )

            wav_info.update(
                {
                    "channels": channels,
                    "sample_rate": sample_rate,
                    "frames": frames,
                    "duration_seconds": duration,
                }
            )

    except Exception as exc:

        raise StableAudioOutputError(
            (
                "Output WAV doğrulanamadı: "
                f"{exc}"
            )
        ) from exc

    return wav_info


# ============================================================
# RUNNER
# ============================================================

class StableAudioRunner:

    def __init__(
        self,
    ) -> None:

        self.locator = (
            StableAudioCliLocator()
        )

        self.command_builder = (
            StableAudioCommand()
        )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    def status(
        self,
    ) -> Dict[str, Any]:

        cli_path = None

        try:

            cli_path = (
                self.locator.locate()
            )

        except StableAudioCliNotFound:
            pass

        return {
            "runner_version": (
                RUNNER_VERSION
            ),
            "python": sys.executable,
            "python_version": (
                sys.version
            ),
            "platform": sys.platform,
            "cli_found": (
                cli_path is not None
            ),
            "cli_path": (
                str(cli_path)
                if cli_path
                else ""
            ),
            "dit": DEFAULT_DIT,
            "decoder": DEFAULT_DECODER,
            "fake_audio": False,
            "procedural_audio": False,
            "real_generation": True,
        }

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    def run(
        self,
        request: StableAudioRunRequest,
    ) -> StableAudioRunResult:

        output_path = validate_request(
            request
        )

        cli_path = (
            self.locator.locate()
        )

        command = (
            self.command_builder.build(
                cli_path,
                request,
            )
        )

        started = (
            time.perf_counter()
        )

        try:

            process = subprocess.run(
                command,
                cwd=str(
                    cli_path.parent
                ),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

        except OSError as exc:

            elapsed = (
                time.perf_counter()
                - started
            )

            return StableAudioRunResult(
                success=False,
                elapsed_seconds=round(
                    elapsed,
                    3,
                ),
                cli_path=str(
                    cli_path
                ),
                dit=request.dit,
                decoder=request.decoder,
                seconds=request.seconds,
                seed=request.seed,
                error=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

        elapsed = (
            time.perf_counter()
            - started
        )

        if process.returncode != 0:

            return StableAudioRunResult(
                success=False,
                output=str(
                    output_path
                ),
                elapsed_seconds=round(
                    elapsed,
                    3,
                ),
                returncode=(
                    process.returncode
                ),
                cli_path=str(
                    cli_path
                ),
                dit=request.dit,
                decoder=request.decoder,
                seconds=request.seconds,
                seed=request.seed,
                stdout=(
                    process.stdout
                    or ""
                ),
                stderr=(
                    process.stderr
                    or ""
                ),
                error=(
                    "Stable Audio 3 CLI "
                    "başarısız oldu."
                ),
                metadata={
                    "command": command,
                },
            )

        try:

            output_info = (
                validate_output(
                    output_path
                )
            )

        except StableAudioOutputError as exc:

            return StableAudioRunResult(
                success=False,
                output=str(
                    output_path
                ),
                elapsed_seconds=round(
                    elapsed,
                    3,
                ),
                returncode=(
                    process.returncode
                ),
                cli_path=str(
                    cli_path
                ),
                dit=request.dit,
                decoder=request.decoder,
                seconds=request.seconds,
                seed=request.seed,
                stdout=(
                    process.stdout
                    or ""
                ),
                stderr=(
                    process.stderr
                    or ""
                ),
                error=str(
                    exc
                ),
                metadata={
                    "command": command,
                },
            )

        return StableAudioRunResult(
            success=True,
            output=str(
                output_path
            ),
            elapsed_seconds=round(
                elapsed,
                3,
            ),
            returncode=(
                process.returncode
            ),
            cli_path=str(
                cli_path
            ),
            dit=request.dit,
            decoder=request.decoder,
            seconds=request.seconds,
            seed=request.seed,
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
                "output": output_info,
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
                "placeholder_audio": False,
            },
        )


# ============================================================
# JSON
# ============================================================

def request_from_dict(
    payload: Dict[str, Any],
) -> StableAudioRunRequest:

    return StableAudioRunRequest(
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
            30.0,
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
            1.0,
        ),
        steps=payload.get(
            "steps",
            8,
        ),
        threads=payload.get(
            "threads",
            DEFAULT_THREADS,
        ),
        source=payload.get(
            "source",
            "",
        ),
        metadata=payload.get(
            "metadata",
            {},
        ),
    )


def load_request(
    path: Path,
) -> StableAudioRunRequest:

    try:

        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except OSError as exc:

        raise StableAudioRunnerError(
            (
                "Request dosyası okunamadı: "
                f"{exc}"
            )
        ) from exc

    except json.JSONDecodeError as exc:

        raise StableAudioRunnerError(
            (
                "Request JSON geçersiz: "
                f"{exc}"
            )
        ) from exc

    if not isinstance(
        payload,
        dict,
    ):

        raise StableAudioRunnerError(
            "Request JSON object olmalı."
        )

    return request_from_dict(
        payload
    )


def save_result(
    path: Path,
    result: StableAudioRunResult,
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
        ),
        encoding="utf-8",
    )


# ============================================================
# CLI
# ============================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "MAVI Stable Audio 3 TFLite runner"
        )
    )

    parser.add_argument(
        "--request",
        type=str,
        default="",
    )

    parser.add_argument(
        "--prompt",
        type=str,
        default="",
    )

    parser.add_argument(
        "--output",
        type=str,
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
        default=None,
    )

    parser.add_argument(
        "--dit",
        type=str,
        default=DEFAULT_DIT,
    )

    parser.add_argument(
        "--decoder",
        type=str,
        default=DEFAULT_DECODER,
    )

    parser.add_argument(
        "--init-audio",
        type=str,
        default="",
    )

    parser.add_argument(
        "--init-noise-level",
        type=float,
        default=None,
    )

    parser.add_argument(
        "--inpaint-range",
        type=str,
        default="",
    )

    parser.add_argument(
        "--negative-prompt",
        type=str,
        default="",
    )

    parser.add_argument(
        "--cfg",
        type=float,
        default=1.0,
    )

    parser.add_argument(
        "--steps",
        type=int,
        default=8,
    )

    parser.add_argument(
        "--threads",
        type=int,
        default=int(
            os.getenv(
                ENV_STABLE_AUDIO_THREADS,
                DEFAULT_THREADS,
            )
        ),
    )

    parser.add_argument(
        "--source",
        type=str,
        default="",
    )

    parser.add_argument(
        "--result",
        type=str,
        default="",
    )

    parser.add_argument(
        "--status",
        action="store_true",
    )

    return parser


def request_from_args(
    args: argparse.Namespace,
) -> StableAudioRunRequest:

    return StableAudioRunRequest(
        prompt=args.prompt,
        output=args.output,
        seconds=args.seconds,
        seed=args.seed,
        dit=args.dit,
        decoder=args.decoder,
        init_audio=args.init_audio,
        init_noise_level=(
            args.init_noise_level
        ),
        inpaint_range=(
            args.inpaint_range
        ),
        negative_prompt=(
            args.negative_prompt
        ),
        cfg=args.cfg,
        steps=args.steps,
        threads=args.threads,
        source=args.source,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    parser = build_parser()

    args = parser.parse_args()

    runner = (
        StableAudioRunner()
    )

    if args.status:

        print(
            json.dumps(
                runner.status(),
                ensure_ascii=False,
                indent=2,
            )
        )

        return 0

    try:

        if args.request:

            request = load_request(
                Path(
                    args.request
                )
            )

        else:

            request = request_from_args(
                args
            )

        result = runner.run(
            request
        )

        print(
            json.dumps(
                result.as_dict(),
                ensure_ascii=False,
                indent=2,
            )
        )

        if args.result:

            save_result(
                Path(
                    args.result
                ),
                result,
            )

        return (
            0
            if result.success
            else 1
        )

    except Exception as exc:

        payload = {
            "success": False,
            "output": "",
            "elapsed_seconds": 0.0,
            "returncode": -1,
            "cli_path": "",
            "dit": "",
            "decoder": "",
            "seconds": 0.0,
            "seed": None,
            "stdout": "",
            "stderr": "",
            "error": (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
            "metadata": {
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
                "placeholder_audio": False,
            },
        }

        print(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
        )

        if args.result:

            save_result(
                Path(
                    args.result
                ),
                StableAudioRunResult(
                    success=False,
                    error=str(
                        exc
                    ),
                    metadata=payload[
                        "metadata"
                    ],
                ),
            )

        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )