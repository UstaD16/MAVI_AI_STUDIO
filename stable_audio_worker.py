# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
STABLE AUDIO WORKER ADAPTER
v0.1
============================================================

Prod. By Ufuk Akdoğan

Gerçek yerel Stable Audio backend'i için adapter.

Mimari:

    MAVI AI Studio (Python 3.14)
            │
            │ subprocess / JSON
            ▼
    stable_audio_worker.py (Python 3.13)
            │
            ▼
    Stable Audio / local model
            │
            ▼
    Gerçek WAV

Bu dosya:
- fake audio üretmez
- procedural audio üretmez
- tone/test/sample üretmez
- başarısız backend durumunda sessizce başka bir modele
  geçmez
- çıktı dosyasını doğrular

Backend kullanılabilir değilse açık şekilde hata döndürür.

Gerçek Stable Audio Python API'si ortamdan yüklenir.
Bu sayede ana MAVI Python 3.14 ortamı ile worker Python 3.13
ortamı birbirinden bağımsız kalır.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import os
import sys
import traceback

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional


# ============================================================
# CONFIG
# ============================================================

VERSION = "0.1"

ENV_STABLE_AUDIO_MODULE = (
    "MAVI_STABLE_AUDIO_MODULE"
)

ENV_STABLE_AUDIO_CLASS = (
    "MAVI_STABLE_AUDIO_CLASS"
)

ENV_STABLE_AUDIO_FUNCTION = (
    "MAVI_STABLE_AUDIO_FUNCTION"
)

ENV_MODEL_PATH = (
    "MAVI_STABLE_AUDIO_MODEL"
)

ENV_DEVICE = (
    "MAVI_STABLE_AUDIO_DEVICE"
)

ENV_DEFAULT_SECONDS = (
    "MAVI_STABLE_AUDIO_SECONDS"
)

ENV_DEFAULT_SAMPLE_RATE = (
    "MAVI_STABLE_AUDIO_SAMPLE_RATE"
)

DEFAULT_SECONDS = 30.0
DEFAULT_SAMPLE_RATE = 48000


# ============================================================
# ERRORS
# ============================================================

class StableAudioWorkerError(
    Exception
):
    """Stable Audio worker temel hatası."""


class StableAudioConfigurationError(
    StableAudioWorkerError
):
    """Backend yapılandırma hatası."""


class StableAudioImportError(
    StableAudioWorkerError
):
    """Stable Audio backend import hatası."""


class StableAudioGenerationError(
    StableAudioWorkerError
):
    """Stable Audio generation hatası."""


class StableAudioOutputError(
    StableAudioWorkerError
):
    """Generation output hatası."""


# ============================================================
# REQUEST
# ============================================================

@dataclass
class StableAudioRequest:

    prompt: str

    output: str

    seconds: float = DEFAULT_SECONDS

    duration: float = DEFAULT_SECONDS

    sample_rate: int = DEFAULT_SAMPLE_RATE

    seed: int = 0

    source: str = ""

    model: str = ""

    device: str = ""

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

        self.duration = float(
            self.duration
        )

        self.sample_rate = int(
            self.sample_rate
        )

        self.seed = int(
            self.seed
        )

        self.source = str(
            self.source
        ).strip()

        self.model = str(
            self.model
        ).strip()

        self.device = str(
            self.device
        ).strip()

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
class StableAudioResult:

    success: bool

    output: str = ""

    backend: str = ""

    model: str = ""

    device: str = ""

    sample_rate: int = 0

    duration_seconds: float = 0.0

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
# ENVIRONMENT CONFIG
# ============================================================

class StableAudioConfig:

    def __init__(
        self,
    ) -> None:

        self.module_name = (
            os.getenv(
                ENV_STABLE_AUDIO_MODULE,
                "",
            ).strip()
        )

        self.class_name = (
            os.getenv(
                ENV_STABLE_AUDIO_CLASS,
                "",
            ).strip()
        )

        self.function_name = (
            os.getenv(
                ENV_STABLE_AUDIO_FUNCTION,
                "",
            ).strip()
        )

        self.model_path = (
            os.getenv(
                ENV_MODEL_PATH,
                "",
            ).strip()
        )

        self.device = (
            os.getenv(
                ENV_DEVICE,
                "",
            ).strip()
        )

        seconds_text = (
            os.getenv(
                ENV_DEFAULT_SECONDS,
                "",
            ).strip()
        )

        sample_rate_text = (
            os.getenv(
                ENV_DEFAULT_SAMPLE_RATE,
                "",
            ).strip()
        )

        self.default_seconds = (
            DEFAULT_SECONDS
        )

        self.default_sample_rate = (
            DEFAULT_SAMPLE_RATE
        )

        if seconds_text:

            try:

                self.default_seconds = float(
                    seconds_text
                )

            except ValueError:
                pass

        if sample_rate_text:

            try:

                self.default_sample_rate = int(
                    sample_rate_text
                )

            except ValueError:
                pass

    def status(
        self,
    ) -> Dict[str, Any]:

        return {
            "worker_version": VERSION,
            "module": self.module_name,
            "class": self.class_name,
            "function": self.function_name,
            "model": self.model_path,
            "device": self.device,
            "default_seconds": (
                self.default_seconds
            ),
            "default_sample_rate": (
                self.default_sample_rate
            ),
            "fake_audio": False,
            "procedural_audio": False,
        }


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_request(
    request: StableAudioRequest,
) -> Path:

    if not request.prompt:

        raise StableAudioGenerationError(
            "Prompt boş."
        )

    if not request.output:

        raise StableAudioGenerationError(
            "Output yolu boş."
        )

    if request.seconds <= 0:

        raise StableAudioGenerationError(
            "Seconds 0'dan büyük olmalı."
        )

    if request.duration <= 0:

        raise StableAudioGenerationError(
            "Duration 0'dan büyük olmalı."
        )

    if request.sample_rate <= 0:

        raise StableAudioGenerationError(
            "Sample rate geçersiz."
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
# OUTPUT VALIDATION
# ============================================================

def validate_output(
    path: Path,
) -> Path:

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

    if path.stat().st_size <= 0:

        raise StableAudioOutputError(
            (
                "Stable Audio çıktısı boş: "
                f"{path}"
            )
        )

    if path.suffix.lower() != ".wav":

        raise StableAudioOutputError(
            (
                "MAVI Stable Audio adapter yalnızca "
                f"WAV çıktı kabul eder: {path}"
            )
        )

    return path


# ============================================================
# WAV INFORMATION
# ============================================================

def read_wav_info(
    path: Path,
) -> Dict[str, Any]:

    try:

        import wave

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

            duration = (
                frames / sample_rate
                if sample_rate > 0
                else 0.0
            )

            return {
                "channels": channels,
                "sample_width": sample_width,
                "sample_rate": sample_rate,
                "frames": frames,
                "duration_seconds": (
                    duration
                ),
                "size_bytes": (
                    path.stat().st_size
                ),
            }

    except Exception as exc:

        raise StableAudioOutputError(
            (
                "WAV doğrulanamadı: "
                f"{exc}"
            )
        ) from exc


# ============================================================
# BACKEND LOADER
# ============================================================

class StableAudioBackendLoader:

    def __init__(
        self,
        config: StableAudioConfig,
    ) -> None:

        self.config = config

    def import_module(
        self,
    ) -> Any:

        if not self.config.module_name:

            raise StableAudioConfigurationError(
                (
                    f"{ENV_STABLE_AUDIO_MODULE} "
                    "tanımlı değil."
                )
            )

        try:

            return importlib.import_module(
                self.config.module_name
            )

        except Exception as exc:

            raise StableAudioImportError(
                (
                    "Stable Audio backend "
                    f"yüklenemedi: {exc}"
                )
            ) from exc

    def load_callable(
        self,
    ) -> Any:

        module = (
            self.import_module()
        )

        if self.config.function_name:

            function = getattr(
                module,
                self.config.function_name,
                None,
            )

            if function is None:

                raise StableAudioConfigurationError(
                    (
                        "Stable Audio function bulunamadı: "
                        f"{self.config.function_name}"
                    )
                )

            if not callable(function):

                raise StableAudioConfigurationError(
                    (
                        "Stable Audio function "
                        "callable değil."
                    )
                )

            return function

        if self.config.class_name:

            cls = getattr(
                module,
                self.config.class_name,
                None,
            )

            if cls is None:

                raise StableAudioConfigurationError(
                    (
                        "Stable Audio class bulunamadı: "
                        f"{self.config.class_name}"
                    )
                )

            try:

                if self.config.model_path:

                    instance = cls(
                        model=self.config.model_path
                    )

                else:

                    instance = cls()

            except TypeError:

                try:

                    instance = cls()

                except Exception as exc:

                    raise StableAudioConfigurationError(
                        (
                            "Stable Audio class "
                            "başlatılamadı: "
                            f"{exc}"
                        )
                    ) from exc

            except Exception as exc:

                raise StableAudioConfigurationError(
                    (
                        "Stable Audio class "
                        "başlatılamadı: "
                        f"{exc}"
                    )
                ) from exc

            if not callable(instance):

                raise StableAudioConfigurationError(
                    "Stable Audio instance callable değil."
                )

            return instance

        raise StableAudioConfigurationError(
            (
                f"{ENV_STABLE_AUDIO_FUNCTION} "
                f"veya {ENV_STABLE_AUDIO_CLASS} "
                "tanımlanmalı."
            )
        )


# ============================================================
# CALL ADAPTER
# ============================================================

class StableAudioCallAdapter:

    PARAMETER_ALIASES = {
        "prompt": (
            "prompt",
            "text",
            "description",
            "caption",
        ),
        "output": (
            "output",
            "output_path",
            "outfile",
            "path",
            "filename",
        ),
        "seconds": (
            "seconds",
            "duration",
            "duration_seconds",
            "length",
        ),
        "sample_rate": (
            "sample_rate",
            "sampling_rate",
            "sr",
        ),
        "seed": (
            "seed",
            "random_seed",
        ),
        "source": (
            "source",
            "source_path",
            "input",
            "input_path",
        ),
        "model": (
            "model",
            "model_path",
        ),
        "device": (
            "device",
        ),
    }

    def _find_argument(
        self,
        name: str,
        parameters: Dict[str, inspect.Parameter],
    ) -> Optional[str]:

        for candidate in (
            self.PARAMETER_ALIASES.get(
                name,
                (),
            )
        ):

            if candidate in parameters:

                return candidate

        return None

    def call(
        self,
        backend: Any,
        request: StableAudioRequest,
    ) -> Any:

        try:

            signature = inspect.signature(
                backend
            )

            parameters = {
                name: parameter
                for name, parameter
                in signature.parameters.items()
            }

        except (
            TypeError,
            ValueError,
        ):

            return backend(
                request.prompt
            )

        values = {
            "prompt": request.prompt,
            "output": request.output,
            "seconds": request.seconds,
            "sample_rate": request.sample_rate,
            "seed": request.seed,
            "source": request.source,
            "model": request.model,
            "device": request.device,
        }

        kwargs: Dict[str, Any] = {}

        positional_only = []

        for logical_name, value in values.items():

            argument_name = (
                self._find_argument(
                    logical_name,
                    parameters,
                )
            )

            if argument_name is None:
                continue

            parameter = parameters[
                argument_name
            ]

            if (
                parameter.kind
                == inspect.Parameter.POSITIONAL_ONLY
            ):

                positional_only.append(
                    value
                )

            else:

                kwargs[
                    argument_name
                ] = value

        if positional_only:

            return backend(
                *positional_only,
                **kwargs,
            )

        if kwargs:

            return backend(
                **kwargs
            )

        # Son güvenli callable biçimi:
        return backend(
            request.prompt
        )


# ============================================================
# OUTPUT EXTRACTION
# ============================================================

class GenerationOutputResolver:

    OUTPUT_KEYS = (
        "output",
        "output_path",
        "path",
        "file",
        "filename",
        "wav",
        "wav_path",
    )

    def resolve(
        self,
        raw_result: Any,
        requested_output: Path,
    ) -> Path:

        # Generator doğrudan Path döndürdü.
        if isinstance(
            raw_result,
            Path,
        ):

            return raw_result.resolve()

        # Generator string döndürdü.
        if isinstance(
            raw_result,
            str,
        ):

            return Path(
                raw_result
            ).expanduser().resolve()

        # Generator dict döndürdü.
        if isinstance(
            raw_result,
            dict,
        ):

            for key in self.OUTPUT_KEYS:

                value = raw_result.get(
                    key
                )

                if isinstance(
                    value,
                    str,
                ):

                    return (
                        Path(
                            value
                        )
                        .expanduser()
                        .resolve()
                    )

                if isinstance(
                    value,
                    Path,
                ):

                    return value.resolve()

        # Backend çıktıyı doğrudan istenen yola yazmış olabilir.
        if requested_output.exists():

            return requested_output.resolve()

        raise StableAudioOutputError(
            (
                "Stable Audio backend çalıştı ancak "
                "çıktı yolu belirlenemedi."
            )
        )


# ============================================================
# WORKER ENGINE
# ============================================================

class StableAudioWorker:

    def __init__(
        self,
        configuration: Optional[
            StableAudioConfig
        ] = None,
    ) -> None:

        self.config = (
            configuration
            or StableAudioConfig()
        )

        self.loader = (
            StableAudioBackendLoader(
                self.config
            )
        )

        self.adapter = (
            StableAudioCallAdapter()
        )

        self.output_resolver = (
            GenerationOutputResolver()
        )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    def status(
        self,
    ) -> Dict[str, Any]:

        payload = (
            self.config.status()
        )

        payload.update(
            {
                "python": sys.executable,
                "python_version": (
                    sys.version
                ),
                "platform": sys.platform,
                "backend_ready": (
                    bool(
                        self.config.module_name
                        and (
                            self.config.function_name
                            or self.config.class_name
                        )
                    )
                ),
            }
        )

        return payload

    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    def generate(
        self,
        request: StableAudioRequest,
    ) -> StableAudioResult:

        requested_output = validate_request(
            request
        )

        if not self.config.module_name:

            raise StableAudioConfigurationError(
                (
                    "Stable Audio module yapılandırılmamış.\n"
                    f"Environment: "
                    f"{ENV_STABLE_AUDIO_MODULE}"
                )
            )

        backend = (
            self.loader.load_callable()
        )

        started = (
            __import__(
                "time"
            ).perf_counter()
        )

        try:

            raw_result = (
                self.adapter.call(
                    backend,
                    request,
                )
            )

        except Exception as exc:

            elapsed = (
                __import__(
                    "time"
                ).perf_counter()
                - started
            )

            raise StableAudioGenerationError(
                (
                    "Stable Audio generation başarısız.\n"
                    f"{type(exc).__name__}: {exc}\n"
                    f"Süre: {elapsed:.2f}s"
                )
            ) from exc

        output_path = (
            self.output_resolver.resolve(
                raw_result,
                requested_output,
            )
        )

        output_path = (
            validate_output(
                output_path
            )
        )

        # Eğer backend başka bir isim ürettiyse,
        # ana MAVI pipeline'ının beklediği output'a taşı.
        if output_path != requested_output:

            requested_output.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            try:

                import shutil

                shutil.copy2(
                    output_path,
                    requested_output,
                )

            except OSError as exc:

                raise StableAudioOutputError(
                    (
                        "Stable Audio çıktısı "
                        "istenen output'a kopyalanamadı: "
                        f"{exc}"
                    )
                ) from exc

            output_path = requested_output

        wav_info = (
            read_wav_info(
                output_path
            )
        )

        elapsed = (
            __import__(
                "time"
            ).perf_counter()
            - started
        )

        return StableAudioResult(
            success=True,
            output=str(
                output_path
            ),
            backend=(
                self.config.module_name
            ),
            model=(
                request.model
                or self.config.model_path
            ),
            device=(
                request.device
                or self.config.device
            ),
            sample_rate=int(
                wav_info[
                    "sample_rate"
                ]
            ),
            duration_seconds=float(
                wav_info[
                    "duration_seconds"
                ]
            ),
            metadata={
                "elapsed_seconds": round(
                    elapsed,
                    3,
                ),
                "channels": (
                    wav_info[
                        "channels"
                    ]
                ),
                "frames": (
                    wav_info[
                        "frames"
                    ]
                ),
                "size_bytes": (
                    wav_info[
                        "size_bytes"
                    ]
                ),
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
            },
        )


# ============================================================
# PAYLOAD
# ============================================================

def request_from_dict(
    payload: Dict[str, Any],
) -> StableAudioRequest:

    return StableAudioRequest(
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
            0,
        ),
        source=payload.get(
            "source",
            "",
        ),
        model=payload.get(
            "model",
            "",
        ),
        device=payload.get(
            "device",
            "",
        ),
        metadata=payload.get(
            "metadata",
            {},
        ),
    )


def load_request(
    path: Path,
) -> StableAudioRequest:

    if not path.exists():

        raise StableAudioWorkerError(
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

        raise StableAudioWorkerError(
            (
                "Request JSON okunamadı: "
                f"{exc}"
            )
        ) from exc

    if not isinstance(
        payload,
        dict,
    ):

        raise StableAudioWorkerError(
            "Request JSON object olmalı."
        )

    return request_from_dict(
        payload
    )


def save_result(
    path: Path,
    result: StableAudioResult,
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
            "MAVI AI Studio Stable Audio worker"
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
        default=0,
    )

    parser.add_argument(
        "--source",
        type=str,
        default="",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="",
    )

    parser.add_argument(
        "--device",
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
) -> StableAudioRequest:

    return StableAudioRequest(
        prompt=args.prompt,
        output=args.output,
        seconds=args.seconds,
        duration=args.duration,
        sample_rate=args.sample_rate,
        seed=args.seed,
        source=args.source,
        model=args.model,
        device=args.device,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    parser = (
        build_parser()
    )

    args = parser.parse_args()

    worker = (
        StableAudioWorker()
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if args.status:

        print(
            json.dumps(
                worker.status(),
                ensure_ascii=False,
                indent=2,
            )
        )

        return 0

    # --------------------------------------------------------
    # REQUEST
    # --------------------------------------------------------

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

        result = worker.generate(
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

        return 0

    except Exception as exc:

        error_payload = {
            "success": False,
            "output": "",
            "backend": "",
            "model": "",
            "device": "",
            "sample_rate": 0,
            "duration_seconds": 0.0,
            "error": (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
            "metadata": {
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
                "traceback": (
                    traceback.format_exc()
                ),
            },
        }

        print(
            json.dumps(
                error_payload,
                ensure_ascii=False,
                indent=2,
            )
        )

        if args.result:

            Path(
                args.result
            ).write_text(
                json.dumps(
                    error_payload,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )