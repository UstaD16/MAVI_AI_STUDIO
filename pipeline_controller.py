# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
PIPELINE CONTROLLER
v0.4
============================================================

Prod. By Ufuk Akdoğan

TEK production controller.

Mimari:

    GUI / MAVI CHAT
            |
            v
    Producer Brain
            |
            v
      ProducerIntent
            |
            v
    PipelineController
            |
            v
       AI Runtime
            |
            v
       AI Engine
            |
            v
     Real Generation
            |
            v
   Stable Audio 3 TFLite
            |
            v
     Quality / Mix
            |
            v
        Master
            |
            v
       Final WAV

ÖNEMLİ:

- Controller SES ÜRETMEZ.
- Brain SES ÜRETMEZ.
- Fake audio yok.
- Procedural placeholder yok.
- Kaynak varsayılan olarak korunur.
- Tek aktif production job vardır.
- Uzun kaynaklar continuity katmanına bırakılır.
- Runtime eski imzayla çalışıyorsa geriye dönük uyumluluk korunur.
"""

from __future__ import annotations

import inspect
import json
import threading
import time

from dataclasses import (
    asdict,
    dataclass,
    field,
)

from pathlib import Path

from typing import (
    Any,
    Callable,
    Dict,
    Optional,
)


# ============================================================
# BRAIN
# ============================================================

from ai.brain import (
    ProducerIntent,
    brain,
    producer_intent_to_dict,
    validate_producer_intent,
)


# ============================================================
# AI RUNTIME
# ============================================================

from ai.runtime import (
    AIRuntime,
    RuntimeEvent,
    RuntimeEventType,
)


# ============================================================
# CONFIG
# ============================================================

try:
    import config

except Exception as exc:

    config = None
    CONFIG_ERROR = exc

else:

    CONFIG_ERROR = None


# ============================================================
# CONSTANTS
# ============================================================

CONTROLLER_VERSION = "0.4"

DEFAULT_SECONDS = 30.0

DEFAULT_SEED = 314159

DEFAULT_STEPS = 8

DEFAULT_THREADS = 4

DEFAULT_CFG = 1.0

DEFAULT_INIT_NOISE_LEVEL = 0.20

MAX_SINGLE_GENERATION_SECONDS = 120.0

DEFAULT_TIMEOUT = 1800

FAKE_AUDIO_ALLOWED = False

PROCEDURAL_AUDIO_ALLOWED = False

PLACEHOLDER_AUDIO_ALLOWED = False


# ============================================================
# ERRORS
# ============================================================

class PipelineControllerError(
    Exception
):
    """Controller temel hatası."""


class PipelineControllerBusy(
    PipelineControllerError
):
    """Başka production çalışıyor."""


class PipelineControllerInputError(
    PipelineControllerError
):
    """Pipeline input hatası."""


class PipelineControllerIntentError(
    PipelineControllerError
):
    """Producer intent hatası."""


# ============================================================
# CONTROLLER EVENT
# ============================================================

@dataclass
class PipelineControllerEvent:

    event_type: str

    stage: str = ""

    state: str = ""

    progress: float = 0.0

    message: str = ""

    source_path: str = ""

    result: Any = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    timestamp: float = field(
        default_factory=time.time
    )

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        result = self.result

        if hasattr(
            result,
            "as_dict",
        ):

            try:

                result = result.as_dict()

            except Exception:

                pass

        return {
            "event_type": self.event_type,
            "stage": self.stage,
            "state": self.state,
            "progress": self.progress,
            "message": self.message,
            "source_path": self.source_path,
            "result": result,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


# ============================================================
# CALLBACK
# ============================================================

ControllerCallback = Callable[
    [PipelineControllerEvent],
    None,
]


# ============================================================
# JOB
# ============================================================

@dataclass
class PipelineJob:

    job_id: str

    source_path: str

    command: str

    seconds: float

    seed: int

    steps: int

    threads: int

    cfg: float

    init_noise_level: float

    started_at: float = field(
        default_factory=time.time
    )

    finished_at: float = 0.0

    status: str = "QUEUED"

    stage: str = "SOURCE"

    progress: float = 0.0

    message: str = ""

    result: Any = None

    error: str = ""

    intent: Optional[
        Dict[str, Any]
    ] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        result = self.result

        if hasattr(
            result,
            "as_dict",
        ):

            try:

                result = result.as_dict()

            except Exception:

                pass

        return {
            "job_id": self.job_id,
            "source_path": self.source_path,
            "command": self.command,
            "seconds": self.seconds,
            "seed": self.seed,
            "steps": self.steps,
            "threads": self.threads,
            "cfg": self.cfg,
            "init_noise_level": (
                self.init_noise_level
            ),
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "stage": self.stage,
            "progress": self.progress,
            "message": self.message,
            "result": result,
            "error": self.error,
            "intent": self.intent,
            "metadata": self.metadata,
        }


# ============================================================
# HELPERS
# ============================================================

def _new_job_id() -> str:

    return (
        "MAVI-"
        + time.strftime(
            "%Y%m%d-%H%M%S"
        )
        + "-"
        + f"{int(time.time() * 1000) % 100000:05d}"
    )


def _safe_float(
    value: Any,
    default: float,
) -> float:

    try:

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return float(
            default
        )


def _safe_int(
    value: Any,
    default: int,
) -> int:

    try:

        return int(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return int(
            default
        )


# ============================================================
# PATH VALIDATION
# ============================================================

def validate_source_path(
    source_path: str | Path,
) -> Path:

    path = (
        Path(
            source_path
        )
        .expanduser()
        .resolve()
    )

    if not path.exists():

        raise PipelineControllerInputError(
            (
                "Kaynak müzik bulunamadı: "
                f"{path}"
            )
        )

    if not path.is_file():

        raise PipelineControllerInputError(
            (
                "Kaynak yol bir dosya değil: "
                f"{path}"
            )
        )

    supported = getattr(
        config,
        "SUPPORTED_AUDIO_EXTENSIONS",
        (
            ".wav",
            ".mp3",
            ".flac",
            ".ogg",
            ".m4a",
            ".aac",
            ".wma",
        ),
    )

    supported = tuple(
        str(item).lower()
        for item in supported
    )

    if (
        path.suffix.lower()
        not in supported
    ):

        raise PipelineControllerInputError(
            (
                "Desteklenmeyen audio uzantısı: "
                f"{path.suffix}"
            )
        )

    return path


# ============================================================
# COMMAND VALIDATION
# ============================================================

def validate_command(
    command: str,
) -> str:

    value = str(
        command
        or ""
    ).strip()

    if not value:

        raise PipelineControllerInputError(
            "MAVI production komutu boş."
        )

    return value


# ============================================================
# CONTROLLER
# ============================================================

class PipelineController:

    def __init__(
        self,
        callback: Optional[
            ControllerCallback
        ] = None,
    ) -> None:

        self.callback = callback

        self._lock = threading.RLock()

        self._runtime = AIRuntime(
            callback=self._runtime_event
        )

        self._job: Optional[
            PipelineJob
        ] = None

        self._last_job: Optional[
            PipelineJob
        ] = None

    # ========================================================
    # CALLBACK
    # ========================================================

    def set_callback(
        self,
        callback: Optional[
            ControllerCallback
        ],
    ) -> None:

        self.callback = callback

    # ========================================================
    # EMIT
    # ========================================================

    def emit(
        self,
        event: PipelineControllerEvent,
    ) -> None:

        callback = self.callback

        if callback is None:

            return

        try:

            callback(
                event
            )

        except Exception:

            pass

    # ========================================================
    # RUNTIME EVENT
    # ========================================================

    def _runtime_event(
        self,
        event: RuntimeEvent,
    ) -> None:

        with self._lock:

            job = self._job

            source_path = (
                job.source_path
                if job is not None
                else ""
            )

            job_id = (
                job.job_id
                if job is not None
                else ""
            )

            if job is not None:

                if event.stage:

                    job.stage = (
                        event.stage
                    )

                job.progress = max(
                    0.0,
                    min(
                        1.0,
                        _safe_float(
                            event.progress,
                            job.progress,
                        ),
                    ),
                )

                if event.message:

                    job.message = (
                        event.message
                    )

                if (
                    event.event_type
                    == RuntimeEventType.STARTED
                ):

                    job.status = "RUNNING"

                elif (
                    event.event_type
                    == RuntimeEventType.PROGRESS
                ):

                    job.status = "RUNNING"

                elif (
                    event.event_type
                    == RuntimeEventType.RESULT
                ):

                    job.status = "COMPLETE"

                    job.progress = 1.0

                    job.result = (
                        event.result
                    )

                elif (
                    event.event_type
                    == RuntimeEventType.ERROR
                ):

                    job.status = "FAILED"

                    job.error = (
                        event.message
                        or "Runtime hatası."
                    )

                    job.result = (
                        event.result
                    )

                elif (
                    event.event_type
                    == RuntimeEventType.STOPPED
                ):

                    job.status = "STOPPED"

                    job.error = (
                        event.message
                        or "Production durduruldu."
                    )

                    job.result = (
                        event.result
                    )

                elif (
                    event.event_type
                    == RuntimeEventType.FINISHED
                ):

                    if (
                        job.status
                        not in {
                            "COMPLETE",
                            "FAILED",
                            "STOPPED",
                        }
                    ):

                        state = str(
                            event.state
                            or ""
                        ).upper()

                        if state == "COMPLETE":

                            job.status = (
                                "COMPLETE"
                            )

                            job.progress = 1.0

                        elif state == "STOPPED":

                            job.status = (
                                "STOPPED"
                            )

                        else:

                            job.status = (
                                "FAILED"
                            )

                    job.finished_at = (
                        time.time()
                    )

                    if (
                        event.result is not None
                    ):

                        job.result = (
                            event.result
                        )

                    self._last_job = job

        controller_event = (
            PipelineControllerEvent(
                event_type=(
                    event.event_type
                ),
                stage=(
                    event.stage
                    or (
                        job.stage
                        if job is not None
                        else ""
                    )
                ),
                state=event.state,
                progress=event.progress,
                message=event.message,
                source_path=source_path,
                result=event.result,
                metadata={
                    **(
                        event.metadata
                        or {}
                    ),
                    "job_id": job_id,
                },
            )
        )

        self.emit(
            controller_event
        )

        if (
            event.event_type
            == RuntimeEventType.FINISHED
        ):

            with self._lock:

                self._job = None

    # ========================================================
    # CONFIGURATION
    # ========================================================

    @staticmethod
    def validate_configuration() -> None:

        if config is None:

            raise PipelineControllerError(
                (
                    "config.py yüklenemedi: "
                    f"{CONFIG_ERROR}"
                )
            )

        if (
            getattr(
                config,
                "REQUIRE_REAL_GENERATION",
                True,
            )
            is not True
        ):

            raise PipelineControllerError(
                "REQUIRE_REAL_GENERATION kapalı."
            )

        if getattr(
            config,
            "ALLOW_FAKE_AUDIO",
            True,
        ):

            raise PipelineControllerError(
                "Fake audio izinli."
            )

        if getattr(
            config,
            "ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO",
            True,
        ):

            raise PipelineControllerError(
                "Procedural placeholder audio izinli."
            )

    # ========================================================
    # BRAIN PARSE
    # ========================================================

    @staticmethod
    def parse_production_intent(
        command: str,
    ) -> ProducerIntent:

        intent = brain.parse(
            command
        )

        valid, errors = (
            validate_producer_intent(
                intent
            )
        )

        if not valid:

            raise PipelineControllerIntentError(
                "; ".join(
                    errors
                )
            )

        return intent

    # ========================================================
    # RUNTIME SIGNATURE
    # ========================================================

    def _runtime_start_parameters(
        self,
        job: PipelineJob,
        intent: ProducerIntent,
    ) -> Dict[str, Any]:

        parameters: Dict[
            str,
            Any,
        ] = {
            "source_path": Path(
                job.source_path
            ),
            "command": job.command,
            "seconds": job.seconds,
            "seed": job.seed,
            "steps": job.steps,
            "threads": job.threads,
            "cfg": job.cfg,
            "init_noise_level": (
                job.init_noise_level
            ),
        }

        # ----------------------------------------------------
        # Runtime hangi parametreleri kabul ediyor?
        # ----------------------------------------------------

        try:

            signature = inspect.signature(
                self._runtime.start
            )

            parameter_names = set(
                signature.parameters.keys()
            )

        except Exception:

            parameter_names = set()

        # ----------------------------------------------------
        # Structured Brain payload.
        #
        # Runtime bunu destekliyorsa gerçek intent
        # doğrudan aşağı katmana aktarılır.
        # Desteklemiyorsa eski Runtime bozulmaz.
        # ----------------------------------------------------

        payload = (
            brain.production_payload(
                intent
            )
        )

        if "intent" in parameter_names:

            parameters[
                "intent"
            ] = intent

        if "producer_intent" in parameter_names:

            parameters[
                "producer_intent"
            ] = intent

        if "intent_payload" in parameter_names:

            parameters[
                "intent_payload"
            ] = payload

        if "production_payload" in parameter_names:

            parameters[
                "production_payload"
            ] = payload

        # ----------------------------------------------------
        # Renewal request runtime tarafından destekleniyorsa
        # doğrudan geçirilir.
        # ----------------------------------------------------

        if (
            intent.intent_type
            == "renew"
        ):

            try:

                renewal_request = (
                    brain.to_renewal_request(
                        intent
                    )
                )

            except Exception:

                renewal_request = None

            if (
                renewal_request is not None
                and "renewal_request"
                in parameter_names
            ):

                parameters[
                    "renewal_request"
                ] = renewal_request

        # ----------------------------------------------------
        # Eski Runtime sürümlerinde tanınmayan
        # structured parametreleri temizle.
        # ----------------------------------------------------

        if parameter_names:

            allowed = (
                parameter_names
                - {
                    "self"
                }
            )

            parameters = {
                key: value
                for key, value
                in parameters.items()
                if key in allowed
            }

        return parameters

    # ========================================================
    # BUSY
    # ========================================================

    @property
    def busy(
        self,
    ) -> bool:

        return bool(
            self._runtime.running
        )

    # ========================================================
    # CURRENT JOB
    # ========================================================

    def current_job(
        self,
    ) -> Optional[
        PipelineJob
    ]:

        with self._lock:

            return self._job

    # ========================================================
    # LAST JOB
    # ========================================================

    def last_job(
        self,
    ) -> Optional[
        PipelineJob
    ]:

        with self._lock:

            return self._last_job

    # ========================================================
    # START
    # ========================================================

    def start(
        self,
        source_path: str | Path,
        command: str,
        *,
        seconds: float = DEFAULT_SECONDS,
        seed: int = DEFAULT_SEED,
        steps: int = DEFAULT_STEPS,
        threads: int = DEFAULT_THREADS,
        cfg: float = DEFAULT_CFG,
        init_noise_level: float = (
            DEFAULT_INIT_NOISE_LEVEL
        ),
    ) -> PipelineJob:

        self.validate_configuration()

        source = validate_source_path(
            source_path
        )

        production_command = (
            validate_command(
                command
            )
        )

        # ----------------------------------------------------
        # Brain burada devreye girer.
        # ----------------------------------------------------

        intent = (
            self.parse_production_intent(
                production_command
            )
        )

        # ----------------------------------------------------
        # Play / pause / stop production pipeline'ına
        # source generation olarak giremez.
        # ----------------------------------------------------

        if intent.intent_type in {
            "chat",
            "play",
            "pause",
            "stop",
            "help",
            "unknown",
        }:

            raise PipelineControllerIntentError(
                (
                    "Bu komut production job başlatmak "
                    f"için uygun değil: "
                    f"{intent.intent_type}"
                )
            )

        final_seconds = (
            _safe_float(
                seconds,
                DEFAULT_SECONDS,
            )
        )

        if final_seconds <= 0:

            final_seconds = (
                DEFAULT_SECONDS
            )

        if (
            final_seconds
            > MAX_SINGLE_GENERATION_SECONDS
        ):

            raise PipelineControllerInputError(
                (
                    "Tek generation süresi "
                    "120 saniyeyi geçemez. "
                    "Uzun kayıtlar continuity "
                    "katmanından işlenir."
                )
            )

        final_seed = _safe_int(
            seed,
            DEFAULT_SEED,
        )

        final_steps = max(
            1,
            _safe_int(
                steps,
                DEFAULT_STEPS,
            ),
        )

        final_threads = max(
            1,
            _safe_int(
                threads,
                DEFAULT_THREADS,
            ),
        )

        final_cfg = _safe_float(
            cfg,
            DEFAULT_CFG,
        )

        final_noise = max(
            0.0,
            min(
                1.0,
                _safe_float(
                    init_noise_level,
                    DEFAULT_INIT_NOISE_LEVEL,
                ),
            ),
        )

        intent_dict = (
            producer_intent_to_dict(
                intent
            )
        )

        production_payload = (
            brain.production_payload(
                intent
            )
        )

        job_metadata = {
            "controller_version": (
                CONTROLLER_VERSION
            ),
            "real_generation": True,
            "fake_audio": False,
            "procedural_audio": False,
            "placeholder_audio": False,
            "brain_version": (
                intent.metadata.get(
                    "parser",
                    "local-producer-brain-v0.2",
                )
            ),
            "intent_type": (
                intent.intent_type
            ),
            "confidence": (
                intent.confidence
            ),
            "instrument_count": len(
                intent.instruments
            ),
            "instruments": list(
                intent.instruments
            ),
            "instrument_actions": dict(
                intent.instrument_actions
            ),
            "instrument_strength": dict(
                intent.instrument_strength
            ),
            "dance_family": (
                intent.dance_family
            ),
            "regional_request": (
                intent.regional_request
            ),
            "preserve_source": (
                intent.preserve_source
            ),
            "preserve_melody": (
                intent.preserve_melody
            ),
            "preserve_tempo": (
                intent.preserve_tempo
            ),
            "preserve_key": (
                intent.preserve_key
            ),
            "preserve_structure": (
                intent.preserve_structure
            ),
            "preserve_rhythm_identity": (
                intent.preserve_rhythm_identity
            ),
            "preserve_regional_identity": (
                intent.preserve_regional_identity
            ),
            "wants_natural_sound": (
                intent.wants_natural_sound
            ),
            "wants_cleanup": (
                intent.wants_cleanup
            ),
            "production_payload": (
                production_payload
            ),
        }

        with self._lock:

            if self._runtime.running:

                raise PipelineControllerBusy(
                    (
                        "MAVI şu anda başka "
                        "bir production çalıştırıyor."
                    )
                )

            job = PipelineJob(
                job_id=_new_job_id(),
                source_path=str(
                    source
                ),
                command=production_command,
                seconds=final_seconds,
                seed=final_seed,
                steps=final_steps,
                threads=final_threads,
                cfg=final_cfg,
                init_noise_level=final_noise,
                status="QUEUED",
                stage="SOURCE",
                progress=0.0,
                intent=intent_dict,
                metadata=job_metadata,
            )

            self._job = job

        # ====================================================
        # SOURCE EVENT
        # ====================================================

        self.emit(
            PipelineControllerEvent(
                event_type=(
                    RuntimeEventType.STARTED
                ),
                stage="SOURCE",
                state="IDLE",
                progress=0.0,
                message=(
                    intent.response_hint
                ),
                source_path=str(
                    source
                ),
                metadata={
                    "job_id": job.job_id,
                    "intent": intent_dict,
                    "production_payload": (
                        production_payload
                    ),
                },
            )
        )

        # ====================================================
        # RUNTIME START
        # ====================================================

        runtime_parameters = (
            self._runtime_start_parameters(
                job,
                intent,
            )
        )

        started = False

        try:

            started = bool(
                self._runtime.start(
                    **runtime_parameters
                )
            )

        except TypeError:
            """
            Eski Runtime imzası varsa structured
            parametrelerden dolayı production düşmez.
            """

            fallback_parameters = {
                "source_path": source,
                "command": production_command,
                "seconds": final_seconds,
                "seed": final_seed,
                "steps": final_steps,
                "threads": final_threads,
                "cfg": final_cfg,
                "init_noise_level": final_noise,
            }

            started = bool(
                self._runtime.start(
                    **fallback_parameters
                )
            )

        except Exception as exc:

            with self._lock:

                job.status = "FAILED"

                job.error = (
                    f"{type(exc).__name__}: {exc}"
                )

                job.finished_at = (
                    time.time()
                )

                self._last_job = job

                self._job = None

            raise PipelineControllerError(
                (
                    "AI runtime production başlatılamadı: "
                    f"{exc}"
                )
            ) from exc

        if not started:

            with self._lock:

                job.status = "FAILED"

                job.error = (
                    "Runtime production başlatılamadı."
                )

                job.finished_at = (
                    time.time()
                )

                self._last_job = job

                self._job = None

            raise PipelineControllerError(
                "AI runtime production başlatamadı."
            )

        return job

    # ========================================================
    # STOP
    # ========================================================

    def stop(
        self,
    ) -> bool:

        stopped = bool(
            self._runtime.stop()
        )

        if stopped:

            self.emit(
                PipelineControllerEvent(
                    event_type=(
                        RuntimeEventType.STOPPED
                    ),
                    stage="RUNTIME",
                    state="STOPPED",
                    progress=0.0,
                    message=(
                        "MAVI production durduruldu."
                    ),
                    metadata={
                        "real_generation": True,
                    },
                )
            )

        return stopped

    # ========================================================
    # WAIT
    # ========================================================

    def wait(
        self,
        timeout: Optional[
            float
        ] = None,
    ) -> Optional[
        PipelineJob
    ]:

        result = (
            self._runtime.wait(
                timeout=timeout
            )
        )

        with self._lock:

            job = (
                self._job
                or self._last_job
            )

            if job is None:

                return self._last_job

            if result is not None:

                job.result = result

                success = bool(
                    getattr(
                        result,
                        "success",
                        False,
                    )
                )

                state = str(
                    getattr(
                        result,
                        "state",
                        "",
                    )
                    or ""
                ).upper()

                if success:

                    job.status = "COMPLETE"

                    job.stage = "COMPLETE"

                    job.progress = 1.0

                    job.error = ""

                elif state == "STOPPED":

                    job.status = "STOPPED"

                    job.stage = "STOPPED"

                else:

                    job.status = "FAILED"

                    job.stage = "FAILED"

                    job.error = str(
                        getattr(
                            result,
                            "error",
                            "",
                        )
                        or "Production başarısız."
                    )

            if job.status in {
                "COMPLETE",
                "FAILED",
                "STOPPED",
            }:

                if not job.finished_at:

                    job.finished_at = (
                        time.time()
                    )

                self._last_job = job

            return job

    # ========================================================
    # POLL
    # ========================================================

    def poll(
        self,
        max_events: int = 50,
    ) -> list[
        RuntimeEvent
    ]:

        return self._runtime.poll(
            max_events=max_events
        )

    # ========================================================
    # STATUS
    # ========================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        with self._lock:

            current = self._job

            last = self._last_job

        runtime_status = (
            self._runtime.status()
        )

        brain_status = {
            "engine": "MAVI PRODUCER BRAIN",
            "version": "0.2",
            "memory_count": len(
                brain.memory
            ),
        }

        return {
            "controller_version": (
                CONTROLLER_VERSION
            ),
            "busy": self.busy,
            "runtime": runtime_status,
            "brain": brain_status,
            "current_job": (
                current.as_dict()
                if current is not None
                else None
            ),
            "last_job": (
                last.as_dict()
                if last is not None
                else None
            ),
            "policy": {
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
                "placeholder_audio": False,
            },
        }

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
    ) -> None:

        with self._lock:

            if self._runtime.running:

                raise PipelineControllerBusy(
                    (
                        "Çalışan production "
                        "resetlenemez."
                    )
                )

            self._job = None

            self._last_job = None

        self._runtime.reset()

    # ========================================================
    # SYNC RUN
    # ========================================================

    def run_sync(
        self,
        source_path: str | Path,
        command: str,
        *,
        seconds: float = DEFAULT_SECONDS,
        seed: int = DEFAULT_SEED,
        steps: int = DEFAULT_STEPS,
        threads: int = DEFAULT_THREADS,
        cfg: float = DEFAULT_CFG,
        init_noise_level: float = (
            DEFAULT_INIT_NOISE_LEVEL
        ),
        timeout: Optional[
            float
        ] = None,
    ) -> PipelineJob:

        job = self.start(
            source_path=source_path,
            command=command,
            seconds=seconds,
            seed=seed,
            steps=steps,
            threads=threads,
            cfg=cfg,
            init_noise_level=(
                init_noise_level
            ),
        )

        self.wait(
            timeout=timeout
        )

        with self._lock:

            return (
                self._last_job
                or self._job
                or job
            )


# ============================================================
# GLOBAL CONTROLLER
# ============================================================

pipeline_controller = (
    PipelineController()
)


# ============================================================
# PUBLIC API
# ============================================================

def start_pipeline(
    source_path: str | Path,
    command: str,
    **kwargs: Any,
) -> PipelineJob:

    return pipeline_controller.start(
        source_path=source_path,
        command=command,
        **kwargs,
    )


def run_pipeline(
    source_path: str | Path,
    command: str,
    **kwargs: Any,
) -> PipelineJob:

    return pipeline_controller.run_sync(
        source_path=source_path,
        command=command,
        **kwargs,
    )


def stop_pipeline() -> bool:

    return pipeline_controller.stop()


def pipeline_status() -> Dict[str, Any]:

    return pipeline_controller.status()


def set_pipeline_callback(
    callback: Optional[
        ControllerCallback
    ],
) -> None:

    pipeline_controller.set_callback(
        callback
    )


def get_current_pipeline_job() -> Optional[
    PipelineJob
]:

    return pipeline_controller.current_job()


def get_last_pipeline_job() -> Optional[
    PipelineJob
]:

    return pipeline_controller.last_job()


# ============================================================
# MAVI CHAT ENTRY
# ============================================================

def execute_mavi_production(
    source_path: str | Path,
    command: str,
    *,
    seconds: float = DEFAULT_SECONDS,
    seed: int = DEFAULT_SEED,
    steps: int = DEFAULT_STEPS,
    threads: int = DEFAULT_THREADS,
    cfg: float = DEFAULT_CFG,
    init_noise_level: float = (
        DEFAULT_INIT_NOISE_LEVEL
    ),
) -> PipelineJob:

    """
    MAVI Chat ana production giriş noktası.

    Örnek:

        "davul ve zurna ekle"

        "bas gitar ekle"

        "eski kaydı toparla, sol klarnet ekle"

        "zurna sert, yumuşat"

        "bu parçayı bozma, sadece davul ve bas gitar ekle"

    Komut önce Producer Brain'den geçer.
    """

    return pipeline_controller.start(
        source_path=source_path,
        command=command,
        seconds=seconds,
        seed=seed,
        steps=steps,
        threads=threads,
        cfg=cfg,
        init_noise_level=(
            init_noise_level
        ),
    )


# ============================================================
# CLI
# ============================================================

def main() -> int:

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "MAVI AI Studio Pipeline Controller"
        )
    )

    parser.add_argument(
        "--status",
        action="store_true",
    )

    parser.add_argument(
        "--source",
        default="",
    )

    parser.add_argument(
        "--command",
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
        "--init-noise-level",
        type=float,
        default=DEFAULT_INIT_NOISE_LEVEL,
    )

    args = parser.parse_args()

    if args.status:

        print(
            json.dumps(
                pipeline_status(),
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        return 0

    if not args.source:

        print(
            "Source gerekli."
        )

        return 1

    if not args.command:

        print(
            "Command gerekli."
        )

        return 1

    try:

        job = run_pipeline(
            source_path=args.source,
            command=args.command,
            seconds=args.seconds,
            seed=args.seed,
            steps=args.steps,
            threads=args.threads,
            cfg=args.cfg,
            init_noise_level=(
                args.init_noise_level
            ),
        )

        print(
            json.dumps(
                job.as_dict(),
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        return (
            0
            if job.status == "COMPLETE"
            else 1
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
                    "real_generation": True,
                    "fake_audio": False,
                    "procedural_audio": False,
                    "placeholder_audio": False,
                },
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        return 1


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )