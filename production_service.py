# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
import time
import wave

from production_factory import get_production_factory


# ============================================================================
# REQUEST
# ============================================================================

@dataclass
class ProductionRequest:
    source_file: str | Path
    output_file: str | Path | None = None

    user_command: str = ""

    style: str = "Turkish Folk Dance"
    region: str = ""

    instruments: list[str] = field(
        default_factory=list
    )

    renewal_strength: float = 0.35

    analysis: Optional[dict[str, Any]] = None

    prompt: str = ""
    negative_prompt: str = ""

    duration: Optional[float] = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# RESULT
# ============================================================================

@dataclass
class ProductionResult:
    success: bool

    output_path: Optional[Path] = None

    provider: str = ""
    model: str = ""
    status: str = ""

    duration: float = 0.0
    sample_rate: int = 0
    generation_time: float = 0.0

    error: Optional[str] = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# AUDIO -> WAV
# ============================================================================

def _write_audio_to_wav(
    audio: Any,
    output_path: Path,
    sample_rate: int,
) -> Path:

    import numpy as np

    if audio is None:
        raise RuntimeError(
            "Generation Service audio verisi döndürmedi."
        )

    if isinstance(audio, tuple):
        audio = audio[0]

    arr = np.asarray(
        audio,
        dtype=np.float32,
    )

    if arr.size == 0:
        raise RuntimeError(
            "Generation Service boş audio verisi döndürdü."
        )

    if arr.ndim == 0:
        raise RuntimeError(
            "Generation Service audio verisi geçersiz."
        )

    if (
        arr.ndim == 2
        and arr.shape[0] in (1, 2)
        and arr.shape[1] > arr.shape[0]
    ):
        arr = arr.T

    if arr.ndim == 1:
        arr = arr[:, None]

    if arr.ndim != 2:
        raise RuntimeError(
            f"Desteklenmeyen audio boyutu: {arr.shape}"
        )

    arr = np.nan_to_num(
        arr,
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )

    arr = np.clip(
        arr,
        -1.0,
        1.0,
    )

    pcm = (
        arr * 32767.0
    ).astype(
        np.int16
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with wave.open(
        str(output_path),
        "wb",
    ) as wf:

        wf.setnchannels(
            int(pcm.shape[1])
        )

        wf.setsampwidth(2)

        wf.setframerate(
            int(sample_rate or 44100)
        )

        wf.writeframes(
            pcm.tobytes()
        )

    if (
        not output_path.exists()
        or output_path.stat().st_size <= 0
    ):
        raise RuntimeError(
            "WAV yazıldı ancak çıktı dosyası oluşmadı."
        )

    return output_path.resolve()


# ============================================================================
# PRODUCTION SERVICE
# ============================================================================

class MaviProductionService:

    VERSION = "1.4"

    DEFAULT_INSTRUMENTS = [
        "Davul",
        "Zurna",
        "Bas Gitar",
        "Sol Klarnet",
    ]

    def __init__(self):

        self.factory = (
            get_production_factory()
        )

        self.generation_service = None
        self.generation_backend = None

        self.initialized = False
        self.last_result = None

        self.initialize()

    # ========================================================================
    # INITIALIZE
    # ========================================================================

    def initialize(self) -> bool:

        try:

            self.generation_service = (
                self.factory.create_generation_service()
            )

            self.generation_backend = (
                self.factory.create_generation_backend()
            )

            self.initialized = bool(
                self.generation_service
                and self.generation_backend
            )

            return self.initialized

        except Exception:

            self.generation_service = None
            self.generation_backend = None
            self.initialized = False

            return False

    # ========================================================================
    # GENERATION STATUS
    # ========================================================================

    def generation_available(self) -> bool:

        if not self.initialized:
            self.initialize()

        if self.generation_service is None:
            return False

        try:

            return bool(
                self.generation_service.is_available()
            )

        except Exception:

            try:

                status = (
                    self.generation_service.status()
                )

                return bool(
                    status.get(
                        "available",
                        status.get(
                            "ready",
                            False,
                        ),
                    )
                )

            except Exception:

                return bool(
                    self.generation_backend
                )

    def is_ready(self) -> bool:

        if not self.initialized:
            self.initialize()

        if (
            self.generation_service is None
            or self.generation_backend is None
        ):
            return False

        return self.generation_available()

    # ========================================================================
    # STATUS
    # ========================================================================

    def status(self) -> dict:

        backend_name = ""

        backend = self.generation_backend

        if backend:

            backend_name = getattr(
                backend,
                "NAME",
                "",
            )

            if not backend_name:
                backend_name = getattr(
                    backend,
                    "name",
                    "",
                )

            if not backend_name:
                backend_name = getattr(
                    backend,
                    "provider_name",
                    "",
                )

            if not backend_name:
                backend_name = getattr(
                    backend,
                    "PROVIDER_NAME",
                    "",
                )

        return {
            "service":
                "MaviProductionService",

            "version":
                self.VERSION,

            "initialized":
                self.initialized,

            "ready":
                self.is_ready(),

            "generation_available":
                self.generation_available(),

            "backend":
                backend_name,

            "real_only":
                True,
        }

    # ========================================================================
    # DEFAULT OUTPUT
    # ========================================================================

    def _default_output(
        self,
        source_file: Path,
    ) -> Path:

        root = (
            Path.home()
            / "Desktop"
            / "MAVI'NİN MÜZİKLERİ"
            / "Üretilen"
        )

        root.mkdir(
            parents=True,
            exist_ok=True,
        )

        return (
            root
            / f"{source_file.stem}_renewed.wav"
        )

    # ========================================================================
    # PROMPT
    # ========================================================================

    def _build_prompt(
        self,
        request: ProductionRequest,
    ) -> str:

        if request.prompt.strip():
            return request.prompt.strip()

        instruments = (
            request.instruments
            or self.DEFAULT_INSTRUMENTS
        )

        return (
            "Faithful renewal of the original "
            "Turkish folk dance music. "
            "Preserve the original melody, "
            "rhythm, phrasing, tempo and structure. "
            "Realistic acoustic performance with "
            f"{', '.join(instruments)}. "
            "Natural human musicianship, organic "
            "dynamics and authentic folk character. "
            "The original musical identity must "
            "remain dominant."
        )

    # ========================================================================
    # NEGATIVE PROMPT
    # ========================================================================

    def _build_negative_prompt(
        self,
        request: ProductionRequest,
    ) -> str:

        if request.negative_prompt.strip():
            return request.negative_prompt.strip()

        return (
            "EDM, chiptune, 8-bit, arcade music, "
            "random melody, unrelated melody, "
            "unrelated rhythm, plastic MIDI, "
            "toy sound, synthetic game sound, "
            "cheap synth, robotic performance, "
            "genre replacement, melody replacement, "
            "random arrangement"
        )

    # ========================================================================
    # NORMALIZE
    # ========================================================================

    def _normalize_request(
        self,
        request: ProductionRequest,
    ) -> ProductionRequest:

        if not request.instruments:
            request.instruments = list(
                self.DEFAULT_INSTRUMENTS
            )

        request.renewal_strength = max(
            0.05,
            min(
                0.60,
                float(
                    request.renewal_strength
                ),
            ),
        )

        request.source_file = (
            Path(
                request.source_file
            ).resolve()
        )

        if request.output_file:

            request.output_file = (
                Path(
                    request.output_file
                ).resolve()
            )

        else:

            request.output_file = (
                self._default_output(
                    request.source_file
                )
            )

        request.prompt = (
            self._build_prompt(
                request
            )
        )

        request.negative_prompt = (
            self._build_negative_prompt(
                request
            )
        )

        return request

    # ========================================================================
    # MATERIALIZE REAL GENERATION
    # ========================================================================

    def _materialize_generation_result(
        self,
        generation_result: Any,
        output: Path,
    ) -> Path:

        # ------------------------------------------------------------
        # A) Generation Service bir dosya verdiyse
        # ------------------------------------------------------------

        generated_output = getattr(
            generation_result,
            "output_path",
            None,
        )

        if generated_output:

            generated_path = Path(
                generated_output
            )

            if (
                generated_path.exists()
                and generated_path.is_file()
                and generated_path.stat().st_size > 0
            ):

                output.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                if (
                    generated_path.resolve()
                    != output.resolve()
                ):

                    output.write_bytes(
                        generated_path.read_bytes()
                    )

                return output.resolve()

        # ------------------------------------------------------------
        # B) Generation Service gerçek audio array verdiyse
        # ------------------------------------------------------------

        audio = getattr(
            generation_result,
            "audio",
            None,
        )

        if audio is None:

            raise RuntimeError(
                "Generation Service gerçek audio "
                "verisini döndürmedi."
            )

        sample_rate = int(
            getattr(
                generation_result,
                "sample_rate",
                44100,
            )
            or 44100
        )

        return _write_audio_to_wav(
            audio=audio,
            output_path=output,
            sample_rate=sample_rate,
        )

    # ========================================================================
    # REAL RENEWAL
    # ========================================================================

    def renew(
        self,
        request: ProductionRequest | None = None,
        **kwargs,
    ) -> ProductionResult:

        started = time.time()

        if request is None:

            request = ProductionRequest(
                **kwargs
            )

        request = (
            self._normalize_request(
                request
            )
        )

        source = Path(
            request.source_file
        )

        output = Path(
            request.output_file
        )

        # ------------------------------------------------------------
        # SOURCE CHECK
        # ------------------------------------------------------------

        if not source.exists():

            result = ProductionResult(
                success=False,
                output_path=output,
                error=(
                    f"Kaynak dosyası bulunamadı: "
                    f"{source}"
                ),
                generation_time=(
                    time.time()
                    - started
                ),
            )

            self.last_result = result

            return result

        # ------------------------------------------------------------
        # SERVICE CHECK
        # ------------------------------------------------------------

        if not self.is_ready():
            self.initialize()

        if (
            self.generation_service is None
            or self.generation_backend is None
        ):

            result = ProductionResult(
                success=False,
                output_path=output,
                error=(
                    "Gerçek Generation Service "
                    "oluşturulamadı."
                ),
                generation_time=(
                    time.time()
                    - started
                ),
            )

            self.last_result = result

            return result

        # ------------------------------------------------------------
        # GENERATION REQUEST
        # ------------------------------------------------------------

        generation_request = {
            "source_file":
                str(source),

            "source_path":
                str(source),

            "prompt":
                request.prompt,

            "negative_prompt":
                request.negative_prompt,

            "instruments":
                list(
                    request.instruments
                ),

            "instrument":
                (
                    request.instruments[0]
                    if request.instruments
                    else ""
                ),

            "role":
                "renewal",

            "section":
                "full",

            "style":
                request.style,

            "region":
                request.region,

            "renewal_strength":
                request.renewal_strength,

            "strength":
                request.renewal_strength,

            "analysis":
                request.analysis,

            "duration":
                request.duration,

            "metadata":
                {
                    **dict(
                        request.metadata
                    ),

                    "requested_output":
                        str(output),

                    "source_file":
                        str(source),
                },

            "user_command":
                request.user_command,
        }

        # ------------------------------------------------------------
        # REAL GENERATION
        # ------------------------------------------------------------

        try:

            generation_result = (
                self.generation_service.generate_one(
                    generation_request
                )
            )

        except Exception as exc:

            result = ProductionResult(
                success=False,
                output_path=output,
                error=str(exc),
                generation_time=(
                    time.time()
                    - started
                ),
            )

            self.last_result = result

            return result

        # ------------------------------------------------------------
        # READ RESULT
        # ------------------------------------------------------------

        success = bool(
            getattr(
                generation_result,
                "success",
                False,
            )
        )

        provider = str(
            getattr(
                generation_result,
                "provider",
                "",
            )
            or ""
        )

        model = str(
            getattr(
                generation_result,
                "model",
                "",
            )
            or ""
        )

        duration = float(
            getattr(
                generation_result,
                "duration",
                0.0,
            )
            or 0.0
        )

        sample_rate = int(
            getattr(
                generation_result,
                "sample_rate",
                44100,
            )
            or 44100
        )

        generation_time = float(
            getattr(
                generation_result,
                "generation_time",
                0.0,
            )
            or (
                time.time()
                - started
            )
        )

        error = getattr(
            generation_result,
            "error",
            None,
        )

        # ------------------------------------------------------------
        # MATERIALIZE REAL WAV
        # ------------------------------------------------------------

        if success:

            try:

                output = (
                    self._materialize_generation_result(
                        generation_result,
                        output,
                    )
                )

            except Exception as exc:

                result = ProductionResult(
                    success=False,
                    output_path=output,
                    provider=provider,
                    model=model,
                    status="failed",
                    duration=duration,
                    sample_rate=sample_rate,
                    generation_time=
                        generation_time,
                    error=(
                        "Gerçek audio üretildi fakat "
                        "final WAV oluşturulamadı: "
                        f"{exc}"
                    ),
                )

                self.last_result = result

                return result

        # ------------------------------------------------------------
        # FINAL FILE GATE
        # ------------------------------------------------------------

        if (
            success
            and output.exists()
            and output.is_file()
            and output.stat().st_size > 0
        ):

            actual_duration = duration

            try:

                with wave.open(
                    str(output),
                    "rb",
                ) as wf:

                    frames = (
                        wf.getnframes()
                    )

                    actual_rate = (
                        wf.getframerate()
                    )

                    if actual_rate:

                        sample_rate = (
                            actual_rate
                        )

                        actual_duration = (
                            frames
                            / float(
                                actual_rate
                            )
                        )

            except Exception:

                pass

            result = ProductionResult(
                success=True,

                output_path=(
                    output.resolve()
                ),

                provider=provider,
                model=model,

                status="completed",

                duration=actual_duration,

                sample_rate=sample_rate,

                generation_time=
                    generation_time,

                metadata={
                    "source":
                        str(source),

                    "instruments":
                        list(
                            request.instruments
                        ),

                    "prompt":
                        request.prompt,

                    "negative_prompt":
                        request.negative_prompt,

                    "renewal_strength":
                        request.renewal_strength,

                    "real_audio":
                        True,
                },
            )

            self.last_result = result

            return result

        # ------------------------------------------------------------
        # FAILURE
        # ------------------------------------------------------------

        if not error:

            error = (
                "Gerçek üretim başarısız oldu "
                "ve WAV çıktısı oluşmadı."
            )

        result = ProductionResult(
            success=False,
            output_path=output,
            provider=provider,
            model=model,
            status="failed",
            duration=duration,
            sample_rate=sample_rate,
            generation_time=
                generation_time,
            error=error,
        )

        self.last_result = result

        return result

    # ========================================================================
    # COMPATIBILITY
    # ========================================================================

    def process(
        self,
        request: ProductionRequest,
    ) -> ProductionResult:

        return self.renew(
            request
        )

    def get_last_result(
        self,
    ) -> Optional[ProductionResult]:

        return self.last_result


# ============================================================================
# SINGLETON
# ============================================================================

_PRODUCTION_SERVICE = (
    MaviProductionService()
)


def get_production_service(
    force_new: bool = False,
) -> MaviProductionService:

    global _PRODUCTION_SERVICE

    if (
        force_new
        or _PRODUCTION_SERVICE is None
    ):

        _PRODUCTION_SERVICE = (
            MaviProductionService()
        )

    return _PRODUCTION_SERVICE


def production_service_status() -> dict:

    return (
        get_production_service()
        .status()
    )


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    "ProductionRequest",
    "ProductionResult",
    "MaviProductionService",
    "get_production_service",
    "production_service_status",
]