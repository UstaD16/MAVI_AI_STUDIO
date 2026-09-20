"""
MAVI AI STUDIO
PROJECT INTEGRITY CHECK

Bu dosya uygulamayı çalıştırmaz.
Sadece proje modüllerinin birbirleriyle uyumlu şekilde
import edilebildiğini ve temel nesnelerin oluşturulabildiğini kontrol eder.

Çalıştırma:
    python check_project.py
"""

from __future__ import annotations

import importlib
import sys
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================================
# TEST DEFINITIONS
# ============================================================================

MODULES = [
    "config",

    # Core
    "core",
    "core.models",
    "core.audio_io",
    "core.analyzer",
    "core.music_dna",
    "core.renewal",
    "core.instrument_mapper",

    # Generation
    "core.generation_request",
    "core.provider_payload",
    "core.generation_result",
    "core.generation_validator",
    "core.generation_pipeline",
    "core.generation_mixer",
    "core.final_audio_pipeline",

    # Providers
    "core.stability_provider",
    "core.stability_provider_adapter",
    "core.real_provider_router",

    # Production
    "core.stem_manager",
    "core.mix_engine",
    "core.master_engine",
    "core.exporter",
    "core.quality_gate",
    "core.plugin_engine",
    "core.mix_report",
    "core.production_state",

    # AI
    "ai",
    "ai.assistant",
    "ai.brain",
    "ai.planner",
    "ai.memory",
    "ai.plugin_bridge",
    "ai.orchestrator",
    "ai.engine",

    # Application
    "app",
    "main",
]


# ============================================================================
# RESULT HELPERS
# ============================================================================

passed = []
failed = []
warnings = []


def ok(name: str):
    passed.append(name)
    print(f"[ OK ] {name}")


def fail(name: str, error: Exception):
    failed.append((name, error))

    print(
        f"[FAIL] {name}\n"
        f"       {type(error).__name__}: {error}"
    )


def warning(name: str, message: str):
    warnings.append((name, message))
    print(
        f"[WARN] {name}\n"
        f"       {message}"
    )


# ============================================================================
# IMPORT CHECK
# ============================================================================

def check_imports():

    print()
    print("=" * 72)
    print("MAVI AI STUDIO • MODULE IMPORT CHECK")
    print("=" * 72)
    print()

    for module_name in MODULES:

        try:
            importlib.import_module(
                module_name
            )

            ok(module_name)

        except Exception as exc:

            fail(
                module_name,
                exc,
            )


# ============================================================================
# CORE OBJECT CHECK
# ============================================================================

def check_core_objects():

    print()
    print("=" * 72)
    print("MAVI AI STUDIO • CORE OBJECT CHECK")
    print("=" * 72)
    print()

    checks = [
        (
            "core.analyzer.ANALYZER",
            "core.analyzer",
            "ANALYZER",
        ),
        (
            "core.music_dna.MUSIC_DNA_BUILDER",
            "core.music_dna",
            "MUSIC_DNA_BUILDER",
        ),
        (
            "core.renewal.RENEWAL_ENGINE",
            "core.renewal",
            "RENEWAL_ENGINE",
        ),
        (
            "core.generation_pipeline.GENERATION_PIPELINE",
            "core.generation_pipeline",
            "GENERATION_PIPELINE",
        ),
        (
            "core.generation_validator.GENERATION_VALIDATOR",
            "core.generation_validator",
            "GENERATION_VALIDATOR",
        ),
        (
            "core.stem_manager.STEM_MANAGER",
            "core.stem_manager",
            "STEM_MANAGER",
        ),
        (
            "core.real_provider_router.REAL_PROVIDER_ROUTER",
            "core.real_provider_router",
            "REAL_PROVIDER_ROUTER",
        ),
        (
            "core.quality_gate.QUALITY_GATE",
            "core.quality_gate",
            "QUALITY_GATE",
        ),
        (
            "core.mix_engine.MIX_ENGINE",
            "core.mix_engine",
            "MIX_ENGINE",
        ),
        (
            "core.master_engine.MASTER_ENGINE",
            "core.master_engine",
            "MASTER_ENGINE",
        ),
        (
            "core.exporter.AUDIO_EXPORTER",
            "core.exporter",
            "AUDIO_EXPORTER",
        ),
        (
            "ai.engine.AI_ENGINE",
            "ai.engine",
            "AI_ENGINE",
        ),
        (
            "ai.orchestrator.MAVI_ORCHESTRATOR",
            "ai.orchestrator",
            "MAVI_ORCHESTRATOR",
        ),
    ]

    for display_name, module_name, attribute_name in checks:

        try:

            module = importlib.import_module(
                module_name
            )

            value = getattr(
                module,
                attribute_name,
            )

            if value is None:
                raise RuntimeError(
                    "Object is None."
                )

            ok(display_name)

        except Exception as exc:

            fail(
                display_name,
                exc,
            )


# ============================================================================
# PROVIDER CHECK
# ============================================================================

def check_provider():

    print()
    print("=" * 72)
    print("MAVI AI STUDIO • REAL PROVIDER CHECK")
    print("=" * 72)
    print()

    try:

        from core.real_provider_router import (
            REAL_PROVIDER_ROUTER,
        )

        status = REAL_PROVIDER_ROUTER.status()

        provider = getattr(
            status,
            "provider",
            "unknown",
        )

        ready = getattr(
            status,
            "ready",
            False,
        )

        configured = getattr(
            status,
            "configured",
            False,
        )

        authenticated = getattr(
            status,
            "authenticated",
            False,
        )

        print(
            f"Provider      : {provider}"
        )

        print(
            f"Configured    : {configured}"
        )

        print(
            f"Authenticated : {authenticated}"
        )

        print(
            f"Ready         : {ready}"
        )

        print()

        if ready:

            ok(
                "REAL_PROVIDER_ROUTER"
            )

        elif configured:

            warning(
                "REAL_PROVIDER_ROUTER",
                "Provider configured but not ready.",
            )

        else:

            warning(
                "REAL_PROVIDER_ROUTER",
                "Real provider API key is not configured yet.",
            )

    except Exception as exc:

        fail(
            "REAL_PROVIDER_ROUTER.status()",
            exc,
        )


# ============================================================================
# AI ENGINE CHECK
# ============================================================================

def check_ai_engine():

    print()
    print("=" * 72)
    print("MAVI AI STUDIO • AI ENGINE CHECK")
    print("=" * 72)
    print()

    try:

        from ai.engine import AI_ENGINE

        snapshot = AI_ENGINE.snapshot()

        print(
            f"Online : {snapshot.get('online')}"
        )

        print(
            f"Busy   : {snapshot.get('busy')}"
        )

        print(
            f"Stage  : {snapshot.get('stage')}"
        )

        print(
            f"Message: {snapshot.get('message')}"
        )

        print()

        ok(
            "AI_ENGINE"
        )

    except Exception as exc:

        fail(
            "AI_ENGINE",
            exc,
        )


# ============================================================================
# ORCHESTRATOR CHECK
# ============================================================================

def check_orchestrator():

    print()
    print("=" * 72)
    print("MAVI AI STUDIO • ORCHESTRATOR CHECK")
    print("=" * 72)
    print()

    try:

        from ai.orchestrator import (
            MAVI_ORCHESTRATOR,
        )

        state = MAVI_ORCHESTRATOR.state()

        print(
            f"Source      : "
            f"{state.get('source_path')}"
        )

        print(
            f"Analysis    : "
            f"{state.get('has_analysis')}"
        )

        print(
            f"Decision    : "
            f"{state.get('has_decision')}"
        )

        print(
            f"Plan        : "
            f"{state.get('has_plan')}"
        )

        print(
            f"Generation  : "
            f"{state.get('has_generation')}"
        )

        print(
            f"Final       : "
            f"{state.get('has_final')}"
        )

        print()

        ok(
            "MAVI_ORCHESTRATOR"
        )

    except Exception as exc:

        fail(
            "MAVI_ORCHESTRATOR",
            exc,
        )


# ============================================================================
# APPLICATION CONSTRUCTION CHECK
# ============================================================================

def check_app_construction():

    print()
    print("=" * 72)
    print("MAVI AI STUDIO • GUI CONSTRUCTION CHECK")
    print("=" * 72)
    print()

    try:

        import tkinter as tk

        # Tcl/Tk availability only.
        root = tk.Tcl()

        root.eval(
            "info patchlevel"
        )

        root.destroy()

        ok(
            "Tkinter / Tcl"
        )

    except Exception as exc:

        fail(
            "Tkinter / Tcl",
            exc,
        )

    try:

        import app

        if not hasattr(
            app,
            "MaviAIStudio",
        ):
            raise RuntimeError(
                "MaviAIStudio class bulunamadı."
            )

        if not callable(
            getattr(
                app,
                "main",
                None,
            )
        ):
            raise RuntimeError(
                "app.main() bulunamadı."
            )

        ok(
            "app.MaviAIStudio"
        )

        ok(
            "app.main"
        )

    except Exception as exc:

        fail(
            "Application module",
            exc,
        )


# ============================================================================
# DIRECTORY CHECK
# ============================================================================

def check_directories():

    print()
    print("=" * 72)
    print("MAVI AI STUDIO • DIRECTORY CHECK")
    print("=" * 72)
    print()

    directories = [
        ROOT / "audio",
        ROOT / "ai",
        ROOT / "core",
        ROOT / "output",
        ROOT / "logs",
    ]

    for directory in directories:

        if directory.exists():

            ok(
                str(
                    directory.relative_to(ROOT)
                )
            )

        else:

            warning(
                str(
                    directory.relative_to(ROOT)
                ),
                "Directory does not exist yet.",
            )


# ============================================================================
# SUMMARY
# ============================================================================

def summary():

    print()
    print("=" * 72)
    print("MAVI AI STUDIO • CHECK SUMMARY")
    print("=" * 72)
    print()

    print(
        f"PASSED   : {len(passed)}"
    )

    print(
        f"FAILED   : {len(failed)}"
    )

    print(
        f"WARNINGS : {len(warnings)}"
    )

    print()

    if failed:

        print(
            "PROJECT STATUS: ATTENTION REQUIRED"
        )

        print()

        print(
            "Failed checks:"
        )

        for name, error in failed:

            print(
                f"  - {name}: "
                f"{type(error).__name__}: {error}"
            )

        print()

        print(
            "Detailed traceback:"
        )

        for name, error in failed:

            print()
            print(
                f"--- {name} ---"
            )

            traceback.print_exception(
                type(error),
                error,
                error.__traceback__,
            )

        return 1

    if warnings:

        print(
            "PROJECT STATUS: STRUCTURE OK / CONFIGURATION WARNINGS"
        )

        print()

        for name, message in warnings:

            print(
                f"  - {name}: {message}"
            )

        print()

        return 0

    print(
        "PROJECT STATUS: ALL CHECKS PASSED"
    )

    print()

    return 0


# ============================================================================
# MAIN
# ============================================================================

def main():

    print()
    print("MAVI AI STUDIO")
    print("Project Integrity Check")
    print(
        f"Root: {ROOT}"
    )
    print()

    check_imports()
    check_core_objects()
    check_provider()
    check_ai_engine()
    check_orchestrator()
    check_app_construction()
    check_directories()

    return summary()


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
