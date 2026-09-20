# -*- coding: utf-8 -*-

"""
MAVI AI STUDIO
GENERATION WIRING TEST
"""

from __future__ import annotations

import json
import sys


# ---------------------------------------------------------------------------
# GENERATION SERVICE
# ---------------------------------------------------------------------------

from core.generation_service import (
    get_generation_service,
    generation_status,
    generation_available,
)


# ---------------------------------------------------------------------------
# PRODUCTION FACTORY
# ---------------------------------------------------------------------------

try:
    from core.production_factory import (
        get_production_factory,
        get_production_status,
        production_ready,
        generation_available as factory_generation_available,
    )
except ModuleNotFoundError:
    from production_factory import (
        get_production_factory,
        get_production_status,
        production_ready,
        generation_available as factory_generation_available,
    )


# ---------------------------------------------------------------------------
# PRODUCTION SERVICE
# ---------------------------------------------------------------------------

try:
    from core.production_service import (
        get_production_service,
        production_status,
        production_ready as service_production_ready,
        generation_available as service_generation_available,
    )
except ModuleNotFoundError:
    from production_service import (
        get_production_service,
        production_status,
        production_ready as service_production_ready,
        generation_available as service_generation_available,
    )


PASS = 0
FAIL = 0


def ok(label: str, value: object = "") -> None:
    global PASS

    PASS += 1

    if value == "":
        print(f"[ OK ] {label}")
    else:
        print(f"[ OK ] {label}: {value}")


def fail(label: str, error: object = "") -> None:
    global FAIL

    FAIL += 1

    if error == "":
        print(f"[FAIL] {label}")
    else:
        print(f"[FAIL] {label}: {error}")


def show_status(title: str, data: dict) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)

    print(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )


def main() -> int:

    print()
    print("=" * 72)
    print("MAVI AI STUDIO • GENERATION WIRING TEST")
    print("=" * 72)
    print()

    print(
        "Python:",
        sys.version.split()[0],
    )

    # -----------------------------------------------------------------------
    # GENERATION SERVICE
    # -----------------------------------------------------------------------

    try:

        generation_service = get_generation_service()

        if generation_service is None:
            raise RuntimeError(
                "Generation Service oluşturulamadı."
            )

        ok(
            "MaviGenerationService"
        )

    except Exception as exc:

        fail(
            "MaviGenerationService",
            exc,
        )

        return 1

    # -----------------------------------------------------------------------
    # GENERATION BACKEND
    # -----------------------------------------------------------------------

    try:

        backend = generation_service.get_backend()

        if backend is None:

            fail(
                "Generation backend bulunamadı."
            )

        else:

            backend_name = getattr(
                backend,
                "NAME",
                backend.__class__.__name__,
            )

            ok(
                "Generation Backend",
                backend_name,
            )

            if (
                backend_name
                == "stable-audio-3-tflite"
            ):
                ok(
                    "Local Stable Audio 3 seçildi."
                )

    except Exception as exc:

        fail(
            "Generation backend kontrolü",
            exc,
        )

    # -----------------------------------------------------------------------
    # GENERATION AVAILABILITY
    # -----------------------------------------------------------------------

    try:

        available = generation_available()

        if available:
            ok(
                "Generation Service AVAILABLE"
            )
        else:
            fail(
                "Generation Service UNAVAILABLE"
            )

    except Exception as exc:

        fail(
            "Generation availability",
            exc,
        )

    # -----------------------------------------------------------------------
    # GENERATION STATUS
    # -----------------------------------------------------------------------

    try:

        status = generation_status()

        if isinstance(status, dict):

            show_status(
                "GENERATION SERVICE STATUS",
                status,
            )

            ok(
                "Generation status okunuyor."
            )

        else:

            fail(
                "Generation status dict değil."
            )

    except Exception as exc:

        fail(
            "Generation status",
            exc,
        )

    # -----------------------------------------------------------------------
    # PRODUCTION FACTORY
    # -----------------------------------------------------------------------

    try:

        factory = get_production_factory()

        if factory is None:
            raise RuntimeError(
                "Production Factory oluşturulamadı."
            )

        ok(
            "MaviProductionFactory"
        )

    except Exception as exc:

        fail(
            "MaviProductionFactory",
            exc,
        )

        return 1

    # -----------------------------------------------------------------------
    # FACTORY BACKEND
    # -----------------------------------------------------------------------

    try:

        factory_backend = (
            factory.generation_backend
        )

        if factory_backend is None:

            fail(
                "Factory generation backend boş."
            )

        else:

            name = getattr(
                factory_backend,
                "NAME",
                factory_backend.__class__.__name__,
            )

            ok(
                "Factory Backend",
                name,
            )

            if (
                name
                == "stable-audio-3-tflite"
            ):

                ok(
                    "Factory Local Stable Audio 3 kullanıyor."
                )

    except Exception as exc:

        fail(
            "Factory backend kontrolü",
            exc,
        )

    # -----------------------------------------------------------------------
    # FACTORY → GENERATION SERVICE
    # -----------------------------------------------------------------------

    try:

        factory_service = (
            factory.generation_service
        )

        if (
            factory_service
            is generation_service
        ):

            ok(
                "Factory → Generation Service bağlantısı"
            )

        else:

            fail(
                "Factory farklı Generation Service kullanıyor."
            )

    except Exception as exc:

        fail(
            "Factory service bağlantısı",
            exc,
        )

    # -----------------------------------------------------------------------
    # FACTORY GENERATION
    # -----------------------------------------------------------------------

    try:

        available = factory_generation_available()

        if available:

            ok(
                "Factory Generation AVAILABLE"
            )

        else:

            fail(
                "Factory Generation UNAVAILABLE"
            )

    except Exception as exc:

        fail(
            "Factory generation availability",
            exc,
        )

    # -----------------------------------------------------------------------
    # PRODUCTION SERVICE
    # -----------------------------------------------------------------------

    try:

        production_service = (
            get_production_service()
        )

        if production_service is None:

            raise RuntimeError(
                "Production Service oluşturulamadı."
            )

        ok(
            "MaviProductionService"
        )

    except Exception as exc:

        fail(
            "MaviProductionService",
            exc,
        )

        production_service = None

    # -----------------------------------------------------------------------
    # PRODUCTION SERVICE BACKEND
    # -----------------------------------------------------------------------

    if production_service is not None:

        try:

            service_backend = (
                production_service.generation_backend
            )

            if service_backend is None:

                fail(
                    "Production Service backend boş."
                )

            else:

                name = getattr(
                    service_backend,
                    "NAME",
                    service_backend.__class__.__name__,
                )

                ok(
                    "Production Service Backend",
                    name,
                )

                if (
                    name
                    == "stable-audio-3-tflite"
                ):

                    ok(
                        "Production Service Local Stable Audio 3 kullanıyor."
                    )

        except Exception as exc:

            fail(
                "Production Service backend",
                exc,
            )

    # -----------------------------------------------------------------------
    # PRODUCTION SERVICE → FACTORY
    # -----------------------------------------------------------------------

    if production_service is not None:

        try:

            if (
                production_service.factory
                is factory
            ):

                ok(
                    "Production Service → Factory bağlantısı"
                )

            else:

                fail(
                    "Production Service farklı Factory kullanıyor."
                )

        except Exception as exc:

            fail(
                "Production Service Factory bağlantısı",
                exc,
            )

    # -----------------------------------------------------------------------
    # PRODUCTION SERVICE GENERATION
    # -----------------------------------------------------------------------

    if production_service is not None:

        try:

            available = (
                service_generation_available()
            )

            if available:

                ok(
                    "Production Service Generation AVAILABLE"
                )

            else:

                fail(
                    "Production Service Generation UNAVAILABLE"
                )

        except Exception as exc:

            fail(
                "Production Service generation availability",
                exc,
            )

    # -----------------------------------------------------------------------
    # PRODUCTION STATUS
    # -----------------------------------------------------------------------

    try:

        status = production_status()

        if isinstance(status, dict):

            show_status(
                "PRODUCTION SERVICE STATUS",
                status,
            )

            ok(
                "Production status okunuyor."
            )

        else:

            fail(
                "Production status dict değil."
            )

    except Exception as exc:

        fail(
            "Production status",
            exc,
        )

    # -----------------------------------------------------------------------
    # READINESS
    # -----------------------------------------------------------------------

    try:

        ready_factory = production_ready()
        ready_service = service_production_ready()

        print()
        print(
            "FACTORY READY :",
            ready_factory,
        )

        print(
            "SERVICE READY :",
            ready_service,
        )

        if ready_factory:
            ok(
                "Production Factory READY"
            )
        else:
            fail(
                "Production Factory READY değil."
            )

        if ready_service:
            ok(
                "Production Service READY"
            )
        else:
            fail(
                "Production Service READY değil."
            )

    except Exception as exc:

        fail(
            "Production readiness",
            exc,
        )

    # -----------------------------------------------------------------------
    # FINAL
    # -----------------------------------------------------------------------

    print()
    print("=" * 72)
    print("SONUÇ")
    print("=" * 72)

    print(
        f"PASSED : {PASS}"
    )

    print(
        f"FAILED : {FAIL}"
    )

    print()

    if FAIL == 0:

        print(
            "GENERATION WIRING PASSED."
        )

        print(
            "Local Stable Audio 3 → "
            "Generation Service → "
            "Production Factory → "
            "Production Service bağlantısı hazır."
        )

        return 0

    print(
        "GENERATION WIRING FAILED."
    )

    print(
        "Gerçek üretim testi başlatılmamalı."
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())