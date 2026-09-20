# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
PIPELINE INSPECTOR
v0.1
============================================================

Prod. By Ufuk Akdoğan

Üretim pipeline'ını gerçek generation başlatmadan inceler.

Kontrol edilen yapı:

SOURCE
ANALYZE
MUSIC DNA
REGIONAL
RENEWAL PLAN
GENERATION
CONTINUITY
QUALITY
MIX
MASTER
EXPORT
RUNTIME

Amaç:
- modül import hatalarını yakalamak
- sınıf/fonksiyon varlığını kontrol etmek
- kritik API yüzeylerini görmek
- config ile engine arasındaki temel uyumu kontrol etmek
- gerçek generation başlamadan önce eksikleri göstermek

BU DOSYA SES ÜRETMEZ.
"""

from __future__ import annotations

import importlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(
    __file__
).resolve().parent


# ============================================================
# REPORT
# ============================================================

class PipelineInspection:

    def __init__(self) -> None:

        self.items: List[
            Dict[str, Any]
        ] = []

    def add(
        self,
        name: str,
        success: bool,
        detail: str = "",
        severity: str = "ERROR",
    ) -> None:

        self.items.append(
            {
                "name": name,
                "success": bool(success),
                "detail": str(detail),
                "severity": severity,
            }
        )

    @property
    def passed(self) -> int:

        return sum(
            1
            for item in self.items
            if item["success"]
        )

    @property
    def failed(self) -> int:

        return sum(
            1
            for item in self.items
            if not item["success"]
        )

    @property
    def success(self) -> bool:

        return self.failed == 0

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "success": self.success,
            "passed": self.passed,
            "failed": self.failed,
            "items": self.items,
        }


# ============================================================
# IMPORT TEST
# ============================================================

def import_module(
    report: PipelineInspection,
    module_name: str,
) -> Any:

    try:

        module = importlib.import_module(
            module_name
        )

    except Exception as exc:

        report.add(
            f"IMPORT {module_name}",
            False,
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )

        return None

    report.add(
        f"IMPORT {module_name}",
        True,
        str(
            getattr(
                module,
                "__file__",
                "",
            )
        ),
    )

    return module


# ============================================================
# ATTRIBUTE TEST
# ============================================================

def check_attributes(
    report: PipelineInspection,
    module: Any,
    module_name: str,
    attributes: List[str],
) -> None:

    if module is None:
        return

    for attribute in attributes:

        exists = hasattr(
            module,
            attribute,
        )

        report.add(
            (
                f"{module_name}.{attribute}"
            ),
            exists,
            (
                "OK"
                if exists
                else "Eksik"
            ),
        )


# ============================================================
# CALLABLE TEST
# ============================================================

def check_callable(
    report: PipelineInspection,
    module: Any,
    module_name: str,
    callable_name: str,
) -> None:

    if module is None:
        return

    value = getattr(
        module,
        callable_name,
        None,
    )

    success = callable(
        value
    )

    report.add(
        (
            f"CALLABLE "
            f"{module_name}.{callable_name}"
        ),
        success,
        (
            "callable"
            if success
            else "callable değil"
        ),
    )


# ============================================================
# SIGNATURE TEST
# ============================================================

def inspect_signature(
    report: PipelineInspection,
    module: Any,
    module_name: str,
    function_name: str,
) -> None:

    if module is None:
        return

    function = getattr(
        module,
        function_name,
        None,
    )

    if not callable(function):

        report.add(
            (
                f"SIGNATURE "
                f"{module_name}.{function_name}"
            ),
            False,
            "Fonksiyon bulunamadı.",
        )

        return

    try:

        signature = inspect.signature(
            function
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        report.add(
            (
                f"SIGNATURE "
                f"{module_name}.{function_name}"
            ),
            False,
            str(exc),
        )

        return

    report.add(
        (
            f"SIGNATURE "
            f"{module_name}.{function_name}"
        ),
        True,
        str(signature),
        severity="INFO",
    )


# ============================================================
# FILE STRUCTURE
# ============================================================

def inspect_files(
    report: PipelineInspection,
) -> None:

    required = [
        "config.py",
        "app.py",

        "core/__init__.py",
        "core/models.py",
        "core/audio_io.py",
        "core/analyzer.py",
        "core/music_dna.py",
        "core/regional.py",
        "core/renewal.py",
        "core/generation.py",
        "core/continuity.py",
        "core/quality.py",
        "core/mix.py",
        "core/master.py",
        "core/export.py",

        "ai/__init__.py",
        "ai/brain.py",
        "ai/engine.py",
        "ai/runtime.py",

        "worker.py",
        "worker_bridge.py",
        "stable_audio_worker.py",
        "stable_audio_runner.py",
        "preflight.py",
        "build_mavi_studio.py",
    ]

    for relative in required:

        path = (
            ROOT
            / relative
        )

        report.add(
            f"FILE {relative}",
            path.exists()
            and path.is_file(),
            (
                str(path)
                if path.exists()
                else "Eksik"
            ),
        )


# ============================================================
# CONFIG INSPECTION
# ============================================================

def inspect_config(
    report: PipelineInspection,
    module: Any,
) -> None:

    if module is None:
        return

    required_values = [
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
        "SUPPORTED_INSTRUMENTS",
        "PIPELINE_STAGES",
        "REQUIRE_REAL_GENERATION",
        "ALLOW_FAKE_AUDIO",
        "ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO",
    ]

    for name in required_values:

        exists = hasattr(
            module,
            name,
        )

        report.add(
            f"CONFIG {name}",
            exists,
            (
                repr(
                    getattr(
                        module,
                        name,
                    )
                )
                if exists
                else "Eksik"
            ),
        )

    real_only = getattr(
        module,
        "REQUIRE_REAL_GENERATION",
        None,
    )

    fake_allowed = getattr(
        module,
        "ALLOW_FAKE_AUDIO",
        None,
    )

    procedural_allowed = getattr(
        module,
        "ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO",
        None,
    )

    report.add(
        "CONFIG real generation policy",
        real_only is True,
        repr(real_only),
    )

    report.add(
        "CONFIG fake audio policy",
        fake_allowed is False,
        repr(fake_allowed),
    )

    report.add(
        "CONFIG procedural audio policy",
        procedural_allowed is False,
        repr(procedural_allowed),
    )


# ============================================================
# MODELS INSPECTION
# ============================================================

def inspect_models(
    report: PipelineInspection,
    module: Any,
) -> None:

    if module is None:
        return

    required = [
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

    check_attributes(
        report,
        module,
        "core.models",
        required,
    )


# ============================================================
# CORE PIPELINE INSPECTION
# ============================================================

def inspect_core(
    report: PipelineInspection,
    modules: Dict[str, Any],
) -> None:

    checks = {
        "core.audio_io": [
            "validate_audio_path",
            "probe_audio",
            "ensure_wav",
            "read_wav_frames",
            "write_wav_frames",
            "extract_segment",
            "concatenate_wav",
        ],

        "core.analyzer": [
            "AudioAnalyzer",
            "analyze_audio",
        ],

        "core.music_dna": [
            "MusicDNABuilder",
            "build_music_dna",
        ],

        "core.regional": [
            "RegionalDetector",
            "detect_regional_identity",
            "build_regional_context",
        ],

        "core.renewal": [
            "RenewalEngine",
            "create_renewal_plan",
            "build_renewal_request",
            "renew_from_command",
            "build_generation_payload",
        ],

        "core.generation": [
            "GenerationEngine",
            "GenerationRequest",
            "GenerationResult",
            "generate_audio",
            "build_generation_request",
        ],

        "core.continuity": [
            "ContinuityGenerator",
            "ContinuityPlanner",
            "ContinuityStitcher",
            "generate_continuous_audio",
        ],

        "core.quality": [
            "QualityGate",
            "QualityScorer",
            "check_audio_quality",
            "require_quality_pass",
        ],

        "core.mix": [
            "MixEngine",
            "MixPlanner",
            "build_mix_plan",
            "mix_audio",
        ],

        "core.master": [
            "MasterEngine",
            "MasterProcessor",
            "master_audio",
        ],

        "core.export": [
            "ExportEngine",
            "export_audio",
            "export_master",
            "validate_export",
        ],
    }

    for module_name, names in checks.items():

        module = modules.get(
            module_name
        )

        check_attributes(
            report,
            module,
            module_name,
            names,
        )


# ============================================================
# AI INSPECTION
# ============================================================

def inspect_ai(
    report: PipelineInspection,
    modules: Dict[str, Any],
) -> None:

    brain = modules.get(
        "ai.brain"
    )

    engine = modules.get(
        "ai.engine"
    )

    runtime = modules.get(
        "ai.runtime"
    )

    check_attributes(
        report,
        brain,
        "ai.brain",
        [
            "ProducerBrain",
            "ProducerIntent",
            "brain",
        ],
    )

    check_attributes(
        report,
        engine,
        "ai.engine",
        [
            "AIProductionEngine",
            "EngineState",
            "ProductionPathBuilder",
            "engine",
            "execute_command",
            "run_production",
        ],
    )

    check_attributes(
        report,
        runtime,
        "ai.runtime",
        [
            "MaviRuntime",
            "RuntimeWorker",
            "runtime",
            "set_source",
            "chat_with_mavi",
            "produce_music",
            "produce_music_async",
        ],
    )

    inspect_signature(
        report,
        engine,
        "ai.engine",
        "run_production",
    )

    inspect_signature(
        report,
        engine,
        "ai.engine",
        "execute_command",
    )

    inspect_signature(
        report,
        runtime,
        "ai.runtime",
        "produce_music",
    )

    inspect_signature(
        report,
        runtime,
        "ai.runtime",
        "chat_with_mavi",
    )


# ============================================================
# WORKER INSPECTION
# ============================================================

def inspect_worker(
    report: PipelineInspection,
    modules: Dict[str, Any],
) -> None:

    worker = modules.get(
        "worker"
    )

    bridge = modules.get(
        "worker_bridge"
    )

    runner = modules.get(
        "stable_audio_runner"
    )

    stable_worker = modules.get(
        "stable_audio_worker"
    )

    check_attributes(
        report,
        worker,
        "worker",
        [
            "GenerationRequest",
            "GenerationResult",
            "RealAudioWorker",
        ],
    )

    check_attributes(
        report,
        bridge,
        "worker_bridge",
        [
            "WorkerRequest",
            "WorkerResult",
            "WorkerBridge",
        ],
    )

    check_attributes(
        report,
        runner,
        "stable_audio_runner",
        [
            "StableAudioRunRequest",
            "StableAudioRunResult",
            "StableAudioRunner",
        ],
    )

    check_attributes(
        report,
        stable_worker,
        "stable_audio_worker",
        [
            "StableAudioRequest",
            "StableAudioResult",
            "StableAudioWorker",
        ],
    )


# ============================================================
# IMPORT ISOLATION
# ============================================================

def inspect_runtime_imports(
    report: PipelineInspection,
) -> Dict[str, Any]:

    modules: Dict[str, Any] = {}

    names = [
        "config",

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

        "ai.brain",
        "ai.engine",
        "ai.runtime",

        "worker",
        "worker_bridge",
        "stable_audio_runner",
        "stable_audio_worker",
    ]

    for name in names:

        module = import_module(
            report,
            name,
        )

        modules[name] = module

    return modules


# ============================================================
# ENGINE OBJECT
# ============================================================

def inspect_engine_object(
    report: PipelineInspection,
    engine_module: Any,
) -> None:

    if engine_module is None:
        return

    engine = getattr(
        engine_module,
        "engine",
        None,
    )

    report.add(
        "AI engine singleton",
        engine is not None,
        (
            type(engine).__name__
            if engine is not None
            else "engine yok"
        ),
    )

    if engine is None:
        return

    expected_methods = [
        "run_production",
        "analyze_source",
        "build_pipeline",
    ]

    for method_name in expected_methods:

        if hasattr(
            engine,
            method_name,
        ):

            inspect_signature(
                report,
                engine,
                "engine",
                method_name,
            )

        else:

            report.add(
                f"ENGINE METHOD {method_name}",
                False,
                "Eksik",
                severity="WARNING",
            )


# ============================================================
# RUNTIME OBJECT
# ============================================================

def inspect_runtime_object(
    report: PipelineInspection,
    runtime_module: Any,
) -> None:

    if runtime_module is None:
        return

    runtime = getattr(
        runtime_module,
        "runtime",
        None,
    )

    report.add(
        "Runtime singleton",
        runtime is not None,
        (
            type(runtime).__name__
            if runtime is not None
            else "runtime yok"
        ),
    )

    if runtime is None:
        return

    methods = [
        "set_source",
        "chat",
        "produce",
        "produce_async",
        "stop",
    ]

    for method in methods:

        exists = hasattr(
            runtime,
            method,
        )

        report.add(
            f"RUNTIME METHOD {method}",
            exists,
            (
                "OK"
                if exists
                else "Eksik"
            ),
            severity=(
                "INFO"
                if exists
                else "WARNING"
            ),
        )


# ============================================================
# APP INSPECTION
# ============================================================

def inspect_app(
    report: PipelineInspection,
) -> None:

    module = import_module(
        report,
        "app",
    )

    if module is None:
        return

    names = [
        "MaviApp",
        "main",
    ]

    check_attributes(
        report,
        module,
        "app",
        names,
    )

    main = getattr(
        module,
        "main",
        None,
    )

    if callable(main):

        try:

            signature = inspect.signature(
                main
            )

            report.add(
                "app.main signature",
                True,
                str(signature),
                severity="INFO",
            )

        except Exception as exc:

            report.add(
                "app.main signature",
                False,
                str(exc),
                severity="WARNING",
            )


# ============================================================
# PIPELINE STAGE CHECK
# ============================================================

def inspect_pipeline_stages(
    report: PipelineInspection,
    config_module: Any,
) -> None:

    if config_module is None:
        return

    expected = [
        "SOURCE",
        "ANALYZE",
        "MUSIC DNA",
        "RENEWAL PLAN",
        "REAL GENERATION",
        "STEMS",
        "QUALITY GATE",
        "MIX",
        "MASTER",
        "WAV",
    ]

    stages = getattr(
        config_module,
        "PIPELINE_STAGES",
        (),
    )

    try:

        actual = list(
            stages
        )

    except Exception:

        actual = []

    report.add(
        "Pipeline stage count",
        len(actual) == len(expected),
        (
            f"actual={len(actual)} "
            f"expected={len(expected)}"
        ),
    )

    for index, expected_stage in enumerate(
        expected
    ):

        actual_stage = (
            actual[index]
            if index < len(actual)
            else None
        )

        report.add(
            f"Pipeline stage {index + 1}",
            actual_stage
            == expected_stage,
            (
                f"actual={actual_stage!r} "
                f"expected={expected_stage!r}"
            ),
        )


# ============================================================
# SOURCE DIRECTORY
# ============================================================

def inspect_audio_directories(
    report: PipelineInspection,
    config_module: Any,
) -> None:

    if config_module is None:
        return

    names = [
        "SOURCE_DIR",
        "STEMS_DIR",
        "MIX_DIR",
        "MASTER_DIR",
        "OUTPUT_DIR",
    ]

    for name in names:

        path = getattr(
            config_module,
            name,
            None,
        )

        valid = (
            path is not None
            and Path(
                path
            ).exists()
        )

        report.add(
            f"DIRECTORY {name}",
            valid,
            str(path),
        )


# ============================================================
# JSON
# ============================================================

def save_report(
    report: PipelineInspection,
) -> Path:

    log_dir = (
        ROOT
        / "logs"
    )

    log_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        log_dir
        / "pipeline_inspection.json"
    )

    path.write_text(
        json.dumps(
            report.as_dict(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return path


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    report = PipelineInspection()

    print()
    print(
        "============================================================"
    )
    print(
        "MAVI AI STUDIO"
    )
    print(
        "PIPELINE INSPECTOR"
    )
    print(
        "============================================================"
    )
    print()

    # --------------------------------------------------------
    # FILES
    # --------------------------------------------------------

    print(
        "[1] FILE STRUCTURE"
    )

    inspect_files(
        report
    )

    print()

    # --------------------------------------------------------
    # IMPORTS
    # --------------------------------------------------------

    print(
        "[2] MODULE IMPORTS"
    )

    modules = inspect_runtime_imports(
        report
    )

    print()

    # --------------------------------------------------------
    # CONFIG
    # --------------------------------------------------------

    print(
        "[3] CONFIG"
    )

    config_module = modules.get(
        "config"
    )

    inspect_config(
        report,
        config_module,
    )

    inspect_pipeline_stages(
        report,
        config_module,
    )

    inspect_audio_directories(
        report,
        config_module,
    )

    print()

    # --------------------------------------------------------
    # MODELS
    # --------------------------------------------------------

    print(
        "[4] DATA MODELS"
    )

    inspect_models(
        report,
        modules.get(
            "core.models"
        ),
    )

    print()

    # --------------------------------------------------------
    # CORE
    # --------------------------------------------------------

    print(
        "[5] CORE PIPELINE"
    )

    inspect_core(
        report,
        modules,
    )

    print()

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    print(
        "[6] AI LAYER"
    )

    inspect_ai(
        report,
        modules,
    )

    inspect_engine_object(
        report,
        modules.get(
            "ai.engine"
        ),
    )

    inspect_runtime_object(
        report,
        modules.get(
            "ai.runtime"
        ),
    )

    print()

    # --------------------------------------------------------
    # WORKER
    # --------------------------------------------------------

    print(
        "[7] REAL AUDIO WORKER"
    )

    inspect_worker(
        report,
        modules,
    )

    print()

    # --------------------------------------------------------
    # APP
    # --------------------------------------------------------

    print(
        "[8] APP"
    )

    inspect_app(
        report
    )

    print()

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print(
        "============================================================"
    )

    for item in report.items:

        prefix = (
            "[ OK ]"
            if item["success"]
            else "[FAIL]"
        )

        print(
            f"{prefix} {item['name']}"
        )

        if item["detail"]:

            detail = (
                item["detail"]
                .replace(
                    "\n",
                    " ",
                )
            )

            if len(detail) > 180:

                detail = (
                    detail[:177]
                    + "..."
                )

            print(
                f"       {detail}"
            )

    print()
    print(
        "============================================================"
    )

    print(
        f"PASSED : {report.passed}"
    )

    print(
        f"FAILED : {report.failed}"
    )

    print(
        "STATUS : "
        + (
            "PIPELINE READY"
            if report.success
            else "PIPELINE NEEDS FIX"
        )
    )

    print(
        "============================================================"
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    try:

        report_path = save_report(
            report
        )

        print()
        print(
            "REPORT:"
        )

        print(
            report_path
        )

    except OSError as exc:

        print()
        print(
            f"Report yazılamadı: {exc}"
        )

    print()

    return (
        0
        if report.success
        else 1
    )


if __name__ == "__main__":

    raise SystemExit(
        main()
    )