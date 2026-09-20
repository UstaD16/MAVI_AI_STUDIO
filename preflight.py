# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
PRE-FLIGHT CHECK
v0.1
============================================================

Prod. By Ufuk Akdoğan

Yeni MAVI AI Studio mimarisinin bütün ana katmanlarını
uygulamayı çalıştırmadan önce kontrol eder.

Amaç:
- import hatalarını önceden görmek
- model constructor'larını kontrol etmek
- core bağlantılarını doğrulamak
- AI runtime bağlantısını doğrulamak
- gerçek generation backend durumunu göstermek
- output klasörlerini doğrulamak

Bu dosya AUDIO ÜRETMEZ.
"""

from __future__ import annotations

import importlib
import sys
import traceback

from pathlib import Path
from typing import Any, Dict, List, Tuple

import config


# ============================================================
# CHECK RESULT
# ============================================================

class CheckResult:

    def __init__(
        self,
        name: str,
        success: bool,
        message: str = "",
    ) -> None:

        self.name = name
        self.success = success
        self.message = message

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "name": self.name,
            "success": self.success,
            "message": self.message,
        }


# ============================================================
# PRE-FLIGHT
# ============================================================

class MaviPreflight:

    CORE_MODULES = [
        "core.models",
        "core.audio_io",
        "core.analyzer",
        "core.music_dna",
        "core.regional",
        "core.renewal",
        "core.generation",
        "core.continuity",
        "core.quality",
        "core.mix",
        "core.master",
        "core.export",
    ]

    AI_MODULES = [
        "ai.brain",
        "ai.engine",
        "ai.runtime",
    ]

    def __init__(self) -> None:

        self.results: List[
            CheckResult
        ] = []

    # ========================================================
    # ADD
    # ========================================================

    def add(
        self,
        name: str,
        success: bool,
        message: str = "",
    ) -> None:

        self.results.append(
            CheckResult(
                name=name,
                success=success,
                message=message,
            )
        )

    # ========================================================
    # IMPORT
    # ========================================================

    def check_import(
        self,
        module_name: str,
    ) -> Any:

        try:

            module = importlib.import_module(
                module_name
            )

            self.add(
                module_name,
                True,
                "import OK",
            )

            return module

        except Exception as exc:

            self.add(
                module_name,
                False,
                (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

            return None

    # ========================================================
    # CONFIG
    # ========================================================

    def check_config(
        self,
    ) -> None:

        required = [
            "APP_NAME",
            "APP_VERSION",
            "BASE_DIR",
            "CORE_DIR",
            "AI_DIR",
            "AUDIO_DIR",
            "OUTPUT_DIR",
            "SOURCE_DIR",
            "STEMS_DIR",
            "MIX_DIR",
            "MASTER_DIR",
            "SUPPORTED_AUDIO_EXTENSIONS",
            "DEFAULT_SAMPLE_RATE",
            "REQUIRE_REAL_GENERATION",
            "ALLOW_FAKE_AUDIO",
            "ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO",
        ]

        missing = [
            name
            for name in required
            if not hasattr(
                config,
                name,
            )
        ]

        if missing:

            self.add(
                "config",
                False,
                (
                    "Eksik alanlar: "
                    + ", ".join(
                        missing
                    )
                ),
            )

            return

        try:

            config.ensure_directories()

        except Exception as exc:

            self.add(
                "config",
                False,
                (
                    "Dizinler oluşturulamadı: "
                    f"{exc}"
                ),
            )

            return

        directories = [
            config.AUDIO_DIR,
            config.OUTPUT_DIR,
            config.LOG_DIR,
            config.SOURCE_DIR,
            config.STEMS_DIR,
            config.MIX_DIR,
            config.MASTER_DIR,
        ]

        missing_directories = [
            str(path)
            for path in directories
            if not Path(path).exists()
        ]

        if missing_directories:

            self.add(
                "config",
                False,
                (
                    "Eksik dizinler: "
                    + ", ".join(
                        missing_directories
                    )
                ),
            )

            return

        self.add(
            "config",
            True,
            (
                f"{config.APP_NAME} "
                f"v{config.APP_VERSION}"
            ),
        )

    # ========================================================
    # CORE IMPORTS
    # ========================================================

    def check_core(
        self,
    ) -> Dict[str, Any]:

        imported: Dict[str, Any] = {}

        for module_name in self.CORE_MODULES:

            module = self.check_import(
                module_name
            )

            if module is not None:
                imported[module_name] = module

        return imported

    # ========================================================
    # AI IMPORTS
    # ========================================================

    def check_ai(
        self,
    ) -> Dict[str, Any]:

        imported: Dict[str, Any] = {}

        for module_name in self.AI_MODULES:

            module = self.check_import(
                module_name
            )

            if module is not None:
                imported[module_name] = module

        return imported

    # ========================================================
    # MODEL CONSTRUCTORS
    # ========================================================

    def check_models(
        self,
        models_module: Any,
    ) -> None:

        if models_module is None:

            self.add(
                "core.models objects",
                False,
                "models import edilemedi.",
            )

            return

        required_classes = [
            "SourceAudio",
            "AudioFeatures",
            "RegionalIdentity",
            "Instrument",
            "InstrumentPlan",
            "MusicDNA",
            "RenewalRequest",
            "ProductionSection",
            "Stem",
            "QualityResult",
            "MixResult",
            "MasterResult",
            "ProductionResult",
            "ChatMessage",
            "MaviState",
        ]

        missing = [
            name
            for name in required_classes
            if not hasattr(
                models_module,
                name,
            )
        ]

        if missing:

            self.add(
                "core.models objects",
                False,
                (
                    "Eksik class: "
                    + ", ".join(
                        missing
                    )
                ),
            )

            return

        self.add(
            "core.models objects",
            True,
            "Tüm temel model class'ları mevcut.",
        )

    # ========================================================
    # RENEWAL
    # ========================================================

    def check_renewal(
        self,
        renewal_module: Any,
    ) -> None:

        if renewal_module is None:
            self.add(
                "renewal API",
                False,
                "renewal import yok.",
            )
            return

        required = [
            "RenewalPlan",
            "RenewalEngine",
            "create_renewal_plan",
            "build_renewal_request",
            "build_generation_payload",
        ]

        missing = [
            item
            for item in required
            if not hasattr(
                renewal_module,
                item,
            )
        ]

        self.add(
            "renewal API",
            not missing,
            (
                "OK"
                if not missing
                else "Eksik: "
                + ", ".join(
                    missing
                )
            ),
        )

    # ========================================================
    # GENERATION
    # ========================================================

    def check_generation(
        self,
        generation_module: Any,
    ) -> None:

        if generation_module is None:

            self.add(
                "generation API",
                False,
                "generation import yok.",
            )

            return

        required = [
            "GenerationRequest",
            "GenerationResult",
            "GenerationEngine",
            "LocalStableAudioBackend",
            "build_generation_request",
            "generation_backend_status",
        ]

        missing = [
            item
            for item in required
            if not hasattr(
                generation_module,
                item,
            )
        ]

        if missing:

            self.add(
                "generation API",
                False,
                (
                    "Eksik: "
                    + ", ".join(
                        missing
                    )
                ),
            )

            return

        try:

            status = (
                generation_module
                .generation_backend_status()
            )

            configured = bool(
                status.get(
                    "configured",
                    False,
                )
            )

            self.add(
                "generation API",
                True,
                (
                    "API OK • "
                    f"backend="
                    f"{status.get('backend', 'unknown')} • "
                    f"configured="
                    f"{configured}"
                ),
            )

        except Exception as exc:

            self.add(
                "generation API",
                False,
                (
                    f"status hatası: "
                    f"{exc}"
                ),
            )

    # ========================================================
    # CONTINUITY
    # ========================================================

    def check_continuity(
        self,
        module: Any,
    ) -> None:

        if module is None:

            self.add(
                "continuity API",
                False,
                "continuity import yok.",
            )

            return

        required = [
            "ContinuityPlanner",
            "ContinuityGenerator",
            "ContinuityStitcher",
            "create_continuity_plan",
            "generate_long_audio",
        ]

        missing = [
            item
            for item in required
            if not hasattr(
                module,
                item,
            )
        ]

        self.add(
            "continuity API",
            not missing,
            (
                "OK"
                if not missing
                else "Eksik: "
                + ", ".join(
                    missing
                )
            ),
        )

    # ========================================================
    # QUALITY
    # ========================================================

    def check_quality(
        self,
        module: Any,
    ) -> None:

        if module is None:

            self.add(
                "quality API",
                False,
                "quality import yok.",
            )

            return

        required = [
            "QualityGate",
            "QualityResult",
            "check_audio_quality",
            "require_quality_pass",
            "quality_report",
        ]

        missing = [
            item
            for item in required
            if not hasattr(
                module,
                item,
            )
        ]

        self.add(
            "quality API",
            not missing,
            (
                "OK"
                if not missing
                else "Eksik: "
                + ", ".join(
                    missing
                )
            ),
        )

    # ========================================================
    # MIX
    # ========================================================

    def check_mix(
        self,
        module: Any,
    ) -> None:

        if module is None:

            self.add(
                "mix API",
                False,
                "mix import yok.",
            )

            return

        required = [
            "MixInput",
            "MixPlan",
            "MixEngine",
            "build_mix_plan",
            "mix_audio",
            "validate_mix_output",
        ]

        missing = [
            item
            for item in required
            if not hasattr(
                module,
                item,
            )
        ]

        self.add(
            "mix API",
            not missing,
            (
                "OK"
                if not missing
                else "Eksik: "
                + ", ".join(
                    missing
                )
            ),
        )

    # ========================================================
    # MASTER
    # ========================================================

    def check_master(
        self,
        module: Any,
    ) -> None:

        if module is None:

            self.add(
                "master API",
                False,
                "master import yok.",
            )

            return

        required = [
            "MasterPlan",
            "MasterResult",
            "MasterEngine",
            "master_audio",
            "validate_master_output",
        ]

        missing = [
            item
            for item in required
            if not hasattr(
                module,
                item,
            )
        ]

        self.add(
            "master API",
            not missing,
            (
                "OK"
                if not missing
                else "Eksik: "
                + ", ".join(
                    missing
                )
            ),
        )

    # ========================================================
    # EXPORT
    # ========================================================

    def check_export(
        self,
        module: Any,
    ) -> None:

        if module is None:

            self.add(
                "export API",
                False,
                "export import yok.",
            )

            return

        required = [
            "ExportRequest",
            "ExportResult",
            "ExportEngine",
            "export_audio",
            "export_master",
            "export_engine_status",
        ]

        missing = [
            item
            for item in required
            if not hasattr(
                module,
                item,
            )
        ]

        self.add(
            "export API",
            not missing,
            (
                "OK"
                if not missing
                else "Eksik: "
                + ", ".join(
                    missing
                )
            ),
        )

    # ========================================================
    # BRAIN
    # ========================================================

    def check_brain(
        self,
        module: Any,
    ) -> None:

        if module is None:

            self.add(
                "brain API",
                False,
                "brain import yok.",
            )

            return

        required = [
            "ProducerIntent",
            "ProducerBrain",
            "brain",
            "parse_producer_command",
            "producer_brain_status",
        ]

        missing = [
            item
            for item in required
            if not hasattr(
                module,
                item,
            )
        ]

        self.add(
            "brain API",
            not missing,
            (
                "OK"
                if not missing
                else "Eksik: "
                + ", ".join(
                    missing
                )
            ),
        )

    # ========================================================
    # ENGINE
    # ========================================================

    def check_engine(
        self,
        module: Any,
    ) -> None:

        if module is None:

            self.add(
                "ai.engine API",
                False,
                "ai.engine import yok.",
            )

            return

        required = [
            "PipelineResult",
            "EngineState",
            "ProductionPathBuilder",
            "AIProductionEngine",
            "engine",
            "execute_command",
            "run_production",
            "engine_status",
        ]

        missing = [
            item
            for item in required
            if not hasattr(
                module,
                item,
            )
        ]

        self.add(
            "ai.engine API",
            not missing,
            (
                "OK"
                if not missing
                else "Eksik: "
                + ", ".join(
                    missing
                )
            ),
        )

    # ========================================================
    # RUNTIME
    # ========================================================

    def check_runtime(
        self,
        module: Any,
    ) -> None:

        if module is None:

            self.add(
                "ai.runtime API",
                False,
                "ai.runtime import yok.",
            )

            return

        required = [
            "RuntimeEvent",
            "RuntimeSnapshot",
            "RuntimeEventBus",
            "RuntimeWorker",
            "MaviRuntime",
            "runtime",
            "chat_with_mavi",
            "produce_music",
            "produce_music_async",
            "runtime_status",
        ]

        missing = [
            item
            for item in required
            if not hasattr(
                module,
                item,
            )
        ]

        self.add(
            "ai.runtime API",
            not missing,
            (
                "OK"
                if not missing
                else "Eksik: "
                + ", ".join(
                    missing
                )
            ),
        )

    # ========================================================
    # REAL GENERATION POLICY
    # ========================================================

    def check_generation_policy(
        self,
    ) -> None:

        real_required = bool(
            getattr(
                config,
                "REQUIRE_REAL_GENERATION",
                True,
            )
        )

        fake = bool(
            getattr(
                config,
                "ALLOW_FAKE_AUDIO",
                False,
            )
        )

        procedural = bool(
            getattr(
                config,
                "ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO",
                False,
            )
        )

        success = (
            real_required
            and not fake
            and not procedural
        )

        message = (
            "REAL AUDIO POLICY ACTIVE"
            if success
            else (
                "Policy dikkat: "
                f"real_required={real_required}, "
                f"fake={fake}, "
                f"procedural={procedural}"
            )
        )

        self.add(
            "generation policy",
            success,
            message,
        )

    # ========================================================
    # SOURCE DIRECTORY
    # ========================================================

    def check_source_directory(
        self,
    ) -> None:

        path = Path(
            config.SOURCE_DIR
        )

        if not path.exists():

            self.add(
                "source directory",
                False,
                str(path),
            )

            return

        audio_files = [
            item
            for item in path.iterdir()
            if item.is_file()
            and item.suffix.lower()
            in getattr(
                config,
                "SUPPORTED_AUDIO_EXTENSIONS",
                (),
            )
        ]

        self.add(
            "source directory",
            True,
            (
                f"{len(audio_files)} audio file"
                + (
                    "s"
                    if len(audio_files) != 1
                    else ""
                )
            ),
        )

    # ========================================================
    # APP IMPORT
    # ========================================================

    def check_app(
        self,
    ) -> Any:

        return self.check_import(
            "app"
        )

    # ========================================================
    # APP OBJECT
    # ========================================================

    def check_app_class(
        self,
        app_module: Any,
    ) -> None:

        if app_module is None:

            self.add(
                "app.MaviApp",
                False,
                "app import yok.",
            )

            return

        if not hasattr(
            app_module,
            "MaviApp",
        ):

            self.add(
                "app.MaviApp",
                False,
                "MaviApp bulunamadı.",
            )

            return

        if not hasattr(
            app_module,
            "main",
        ):

            self.add(
                "app.main",
                False,
                "main() bulunamadı.",
            )

            return

        self.add(
            "app GUI",
            True,
            "MaviApp + main() OK",
        )

    # ========================================================
    # FULL RUN
    # ========================================================

    def run(
        self,
    ) -> List[CheckResult]:

        self.results.clear()

        # ----------------------------------------------------
        # CONFIG
        # ----------------------------------------------------

        self.check_config()

        self.check_source_directory()

        self.check_generation_policy()

        # ----------------------------------------------------
        # CORE
        # ----------------------------------------------------

        core = self.check_core()

        # ----------------------------------------------------
        # AI
        # ----------------------------------------------------

        ai = self.check_ai()

        # ----------------------------------------------------
        # MODEL
        # ----------------------------------------------------

        self.check_models(
            core.get(
                "core.models"
            )
        )

        self.check_renewal(
            core.get(
                "core.renewal"
            )
        )

        self.check_generation(
            core.get(
                "core.generation"
            )
        )

        self.check_continuity(
            core.get(
                "core.continuity"
            )
        )

        self.check_quality(
            core.get(
                "core.quality"
            )
        )

        self.check_mix(
            core.get(
                "core.mix"
            )
        )

        self.check_master(
            core.get(
                "core.master"
            )
        )

        self.check_export(
            core.get(
                "core.export"
            )
        )

        self.check_brain(
            ai.get(
                "ai.brain"
            )
        )

        self.check_engine(
            ai.get(
                "ai.engine"
            )
        )

        self.check_runtime(
            ai.get(
                "ai.runtime"
            )
        )

        # ----------------------------------------------------
        # APP
        # ----------------------------------------------------

        app_module = self.check_app()

        self.check_app_class(
            app_module
        )

        return list(
            self.results
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    def summary(
        self,
    ) -> Dict[str, Any]:

        passed = sum(
            1
            for result in self.results
            if result.success
        )

        failed = sum(
            1
            for result in self.results
            if not result.success
        )

        return {
            "total": len(
                self.results
            ),
            "passed": passed,
            "failed": failed,
            "success": failed == 0,
            "results": [
                result.as_dict()
                for result in self.results
            ],
        }

    # ========================================================
    # PRINT
    # ========================================================

    def print_report(
        self,
    ) -> None:

        summary = self.summary()

        print(
            ""
        )

        print(
            "============================================================"
        )

        print(
            "MAVI AI STUDIO • PRE-FLIGHT CHECK"
        )

        print(
            "============================================================"
        )

        for result in self.results:

            marker = (
                "[ OK ]"
                if result.success
                else "[FAIL]"
            )

            if result.message:

                print(
                    f"{marker} "
                    f"{result.name} : "
                    f"{result.message}"
                )

            else:

                print(
                    f"{marker} "
                    f"{result.name}"
                )

        print(
            ""
        )

        print(
            f"PASSED : {summary['passed']}"
        )

        print(
            f"FAILED : {summary['failed']}"
        )

        print(
            "============================================================"
        )

        if summary["success"]:

            print(
                "PRE-FLIGHT PASSED."
            )

            print(
                "MAVI AI STUDIO mimarisi hazır."
            )

        else:

            print(
                "PRE-FLIGHT FAILED."
            )

            print(
                "Önce FAILED satırları düzeltilmeli."
            )

        print(
            "============================================================"
        )

        print(
            ""
        )


# ============================================================
# PUBLIC API
# ============================================================

def run_preflight() -> Dict[str, Any]:

    checker = MaviPreflight()

    checker.run()

    return checker.summary()


def main() -> int:

    checker = MaviPreflight()

    try:

        checker.run()

    except Exception as exc:

        print(
            ""
        )

        print(
            "PRE-FLIGHT INTERNAL ERROR"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        traceback.print_exc()

        return 1

    checker.print_report()

    return (
        0
        if checker.summary()["success"]
        else 1
    )


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":
    raise SystemExit(
        main()
    )