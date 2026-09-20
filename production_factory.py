# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from core.generation_service import (
    get_generation_service,
)


@dataclass
class ProductionComponents:
    generation_service: Any
    generation_backend: Any


class MaviProductionFactory:

    VERSION = "1.0"

    DEFAULT_QUALITY_THRESHOLD = 0.72
    DEFAULT_REALISM_THRESHOLD = 0.68
    DEFAULT_MAX_ATTEMPTS = 3

    def __init__(
        self,
        analyzer: Any = None,
        generation_backend: Any = None,
        generation_service: Any = None,
        quality_threshold: float = DEFAULT_QUALITY_THRESHOLD,
        realism_threshold: float = DEFAULT_REALISM_THRESHOLD,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    ) -> None:

        self.analyzer = analyzer

        self.requested_generation_backend = (
            generation_backend
        )

        self.generation_service = (
            generation_service
        )

        self.generation_backend = None

        self.quality_threshold = float(
            quality_threshold
        )

        self.realism_threshold = float(
            realism_threshold
        )

        self.max_attempts = max(
            1,
            int(max_attempts),
        )

        self.components: Dict[str, Any] = {}

        self.initialized = False

    # ------------------------------------------------------------------
    # GENERATION SERVICE
    # ------------------------------------------------------------------

    def create_generation_service(self):

        if self.generation_service is not None:
            return self.generation_service

        self.generation_service = (
            get_generation_service()
        )

        return self.generation_service

    # ------------------------------------------------------------------
    # GENERATION BACKEND
    # ------------------------------------------------------------------

    def create_generation_backend(self):

        service = (
            self.create_generation_service()
        )

        if service is None:
            self.generation_backend = None
            return None

        requested = (
            self.requested_generation_backend
        )

        if requested is not None:

            try:
                service.set_backend(
                    requested
                )
            except Exception:
                pass

        try:
            backend = service.get_backend()
        except Exception:
            backend = None

        self.generation_backend = backend

        return backend

    # ------------------------------------------------------------------
    # AVAILABILITY
    # ------------------------------------------------------------------

    def generation_available(self) -> bool:

        backend = self.generation_backend

        if backend is None:
            return False

        try:
            return bool(
                backend.is_available()
            )
        except Exception:
            return False

    # ------------------------------------------------------------------
    # BUILD
    # ------------------------------------------------------------------

    def create_all(self) -> Dict[str, Any]:

        self.create_generation_service()
        self.create_generation_backend()

        self.components = {
            "analyzer": self.analyzer,
            "generation_service": (
                self.generation_service
            ),
            "generation_backend": (
                self.generation_backend
            ),
        }

        self.initialized = True

        return dict(
            self.components
        )

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:

        if not self.initialized:
            self.create_all()

        generation_status = {}

        if self.generation_service is not None:

            try:
                generation_status = dict(
                    self.generation_service.get_status()
                    or {}
                )
            except Exception:
                generation_status = {}

        return {
            "factory_version": self.VERSION,
            "initialized": self.initialized,
            "generation_available": (
                self.generation_available()
            ),
            "real_audio_required": True,
            "fake_audio": False,
            "procedural_fallback": False,
            "quality_threshold": (
                self.quality_threshold
            ),
            "realism_threshold": (
                self.realism_threshold
            ),
            "max_attempts": (
                self.max_attempts
            ),
            "generation": generation_status,
            "components": {
                key: value is not None
                for key, value
                in self.components.items()
            },
        }

    def production_ready(self) -> bool:

        if not self.initialized:
            self.create_all()

        return self.generation_available()


# ----------------------------------------------------------------------
# SINGLETON
# ----------------------------------------------------------------------

_FACTORY: Optional[
    MaviProductionFactory
] = None


def get_production_factory(
    reset: bool = False,
    **kwargs: Any,
) -> MaviProductionFactory:

    global _FACTORY

    if (
        _FACTORY is None
        or reset
    ):

        _FACTORY = MaviProductionFactory(
            **kwargs
        )

        _FACTORY.create_all()

    return _FACTORY


def create_production_components(
    **kwargs: Any,
) -> Dict[str, Any]:

    factory = MaviProductionFactory(
        **kwargs
    )

    return factory.create_all()


def get_production_status() -> Dict[str, Any]:

    return (
        get_production_factory()
        .get_status()
    )


def production_ready() -> bool:

    return (
        get_production_factory()
        .production_ready()
    )


def generation_available() -> bool:

    return (
        get_production_factory()
        .generation_available()
    )


MAVI_PRODUCTION_FACTORY_INFO = {

    "version":
        MaviProductionFactory.VERSION,

    "centralized":
        True,

    "generation_service":
        True,

    "generation_backend":
        True,

    "real_audio_required":
        True,

    "fake_audio":
        False,

    "procedural_fallback":
        False,

    "local_first":
        True,

}


__all__ = [

    "MaviProductionFactory",

    "get_production_factory",

    "create_production_components",

    "get_production_status",

    "production_ready",

    "generation_available",

    "MAVI_PRODUCTION_FACTORY_INFO",

]