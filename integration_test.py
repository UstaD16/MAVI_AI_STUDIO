# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
INTEGRATION TEST
v0.1
============================================================

Prod. By Ufuk Akdoğan

Bu test MAVI'nin sıfırdan kurulan mimarisinin ana parçalarının
birbirine bağlanabildiğini kontrol eder.

BU DOSYA GENERATION YAPMAZ.

Kontrol:
- config
- core modelleri
- audio I/O
- analyzer
- regional
- music DNA
- renewal
- generation
- continuity
- quality
- mix
- master
- export
- AI brain
- AI engine
- runtime
- worker
- worker bridge
- Stable Audio runner

Ayrıca:
- gerçek generation policy
- fake audio policy
- procedural audio policy
- kritik singleton'lar
- pipeline stage'leri
- test kaynağı
kontrol edilir.
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import traceback

from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# PATHS
# ============================================================

ROOT = (
    Path(__file__)
    .resolve()
    .parent
)

LOG_DIR = (
    ROOT / "logs"
)

REPORT_PATH = (
    LOG_DIR
    / "integration_test.json"
)

SOURCE_DIR = Path(
    r"C:\Users\ORGOC\Desktop\MAVI'NİN MÜZİKLERİ\Kaynak"
)


# ============================================================
# REPORT
# ============================================================

class IntegrationReport:

    def __init__(self) -> None:

        self.results: List[
            Dict[str, Any]
        ] = []

    def add(
        self,
        name: str,
        success: bool,
        detail: str = "",
        critical: bool = True,
    ) -> None:

        self.results.append(
            {
                "name": name,
                "success": bool(success),
                "detail": str(detail),
                "critical": bool(critical),
            }
        )

    @property
    def passed(self) -> int:

        return sum(
            1
            for item in self.results
            if item["success"]
        )

    @property
    def failed(self) -> int:

        return sum(
            1
            for item in self.results
            if not item["success"]
        )

    @property
    def critical_failures(self) -> int:

        return sum(
            1
            for item in self.results
            if (
                not item["success"]
                and item["critical"]
            )
        )

    @property
    def success(self) -> bool:

        return (
            self.critical_failures == 0
        )

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "success": self.success,
            "passed": self.passed,
            "failed": self.failed,
            "critical_failures": (
                self.critical_failures
            ),
            "results": self.results,
        }


# ============================================================
# HELPERS
# ============================================================

def add_import_test(
    report: IntegrationReport,
    module_name: str,
) -> Optional[Any]:

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
            critical=True,
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


def check_attribute(
    report: IntegrationReport,
    obj: Any,
    name: str,
    label: str,
    critical: bool = True,
) -> bool:

    exists = hasattr(
        obj,
        name,
    )

    report.add(
        label,
        exists,
        (
            "OK"
            if exists
            else "EKSIK"
        ),
        critical=critical,
    )

    return exists


def check_callable(
    report: IntegrationReport,
    obj: Any,
    name: str,
    label: str,
    critical: bool = True,
) -> bool:

    value = getattr(
        obj,
        name,
        None,
    )

    valid = callable(
        value
    )

    report.add(
        label,
        valid,
        (
            "callable"
            if valid
            else "callable degil"
        ),
        critical=critical,
    )

    return valid


def check_file(
    report: IntegrationReport,
    path: Path,
    label: str,
    critical: bool = True,
) -> bool:

    valid = (
        path.exists()
        and path.is_file()
    )

    report.add(
        label,
        valid,
        str(path),
        critical=critical,
    )

    return valid


def check_directory(
    report: IntegrationReport,
    path: Path,
    label: str,
    critical: bool = True,
) -> bool:

    valid = (
        path.exists()
        and path.is_dir()
    )

    report.add(
        label,
        valid,
        str(path),
        critical=critical,
    )

    return valid


# ============================================================
# FILE STRUCTURE
# ============================================================

def inspect_file_structure(
    report: IntegrationReport,
) -> None:

    required_files = [
        "config.py",
        "app.py",
        "preflight.py",
        "build_mavi_studio.py",

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

        "requirements.txt",
        "requirements-worker.txt",

        "setup_mavi.bat",
        "setup_worker.bat",
        "run_worker.bat",
        "configure_worker.bat",
        "start_mavi.bat",
        "stable_audio_env.bat",
        "stable_audio_worker.bat",
        "set_stable_audio_path.bat",
        "check_stable_audio.bat",
        "connect_worker.bat",
        "mavi_run.bat",
        "test_worker_connection.py",
        "test_worker_connection.bat",
        "run_real_generation.bat",
        "run_source_renewal.bat",
        "inspect_pipeline.py",
        "inspect_pipeline.bat",
        "create_worker_request.py",
        "create_worker_request.bat",
        "run_renewal_request.bat",
        "validate_renewal.py",
        "validate_renewal.bat",
    ]

    for relative in required_files:

        check_file(
            report,
            ROOT / relative,
            f"FILE {relative}",
        )


# ============================================================
# CONFIG
# ============================================================

def inspect_config(
    report: IntegrationReport,
    config: Any,
) -> None:

    required = [
        "APP_NAME",
        "APP_VERSION",
        "BASE_DIR",
        "CORE_DIR",
        "AI_DIR",
        "AUDIO_DIR",
        "OUTPUT_DIR",
        "LOG_DIR",
        "BUILD_DIR",
        "DIST_DIR",
        "SOURCE_DIR",
        "STEMS_DIR",
        "MIX_DIR",
        "MASTER_DIR",
        "SUPPORTED_INSTRUMENTS",
        "PIPELINE_STAGES",
    ]

    for name in required:

        check_attribute(
            report,
            config,
            name,
            f"CONFIG {name}",
        )

    real_only = getattr(
        config,
        "REQUIRE_REAL_GENERATION",
        None,
    )

    fake_audio = getattr(
        config,
        "ALLOW_FAKE_AUDIO",
        None,
    )

    procedural = getattr(
        config,
        "ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO",
        None,
    )

    report.add(
        "REAL GENERATION REQUIRED",
        real_only is True,
        repr(real_only),
    )

    report.add(
        "FAKE AUDIO DISABLED",
        fake_audio is False,
        repr(fake_audio),
    )

    report.add(
        "PROCEDURAL PLACEHOLDER DISABLED",
        procedural is False,
        repr(procedural),
    )

    stages = list(
        getattr(
            config,
            "PIPELINE_STAGES",
            (),
        )
    )

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

    report.add(
        "PIPELINE STAGE ORDER",
        stages == expected,
        json.dumps(
            stages,
            ensure_ascii=False,
        ),
    )


# ============================================================
# DIRECTORIES
# ============================================================

def inspect_directories(
    report: IntegrationReport,
    config: Any,
) -> None:

    for name in [
        "AUDIO_DIR",
        "OUTPUT_DIR",
        "LOG_DIR",
        "SOURCE_DIR",
        "STEMS_DIR",
        "MIX_DIR",
        "MASTER_DIR",
    ]:

        path = Path(
            getattr(
                config,
                name,
            )
        )

        check_directory(
            report,
            path,
            f"DIRECTORY {name}",
        )


# ============================================================
# MODEL API
# ============================================================

def inspect_models(
    report: IntegrationReport,
    models: Any,
) -> None:

    names = [
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

    for name in names:

        check_attribute(
            report,
            models,
            name,
            f"MODEL {name}",
        )


# ============================================================
# CORE
# ============================================================

def inspect_core(
    report: IntegrationReport,
    modules: Dict[str, Any],
) -> None:

    checks = {
        "core.audio_io": [
            "validate_audio_path",
            "probe_audio",
            "ensure_wav",
            "read_wav_frames",
            "write_wav_frames",
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

        if module is None:
            continue

        for name in names:

            check_attribute(
                report,
                module,
                name,
                (
                    f"API "
                    f"{module_name}.{name}"
                ),
            )


# ============================================================
# AI
# ============================================================

def inspect_ai(
    report: IntegrationReport,
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

    check_attribute(
        report,
        brain,
        "ProducerBrain",
        "AI Brain ProducerBrain",
    )

    check_attribute(
        report,
        brain,
        "ProducerIntent",
        "AI Brain ProducerIntent",
    )

    check_attribute(
        report,
        brain,
        "brain",
        "AI Brain singleton",
    )

    check_attribute(
        report,
        engine,
        "AIProductionEngine",
        "AI Engine AIProductionEngine",
    )

    check_attribute(
        report,
        engine,
        "engine",
        "AI Engine singleton",
    )

    check_callable(
        report,
        engine,
        "run_production",
        "AI Engine run_production",
    )

    check_callable(
        report,
        engine,
        "execute_command",
        "AI Engine execute_command",
    )

    check_attribute(
        report,
        runtime,
        "MaviRuntime",
        "Runtime MaviRuntime",
    )

    check_attribute(
        report,
        runtime,
        "runtime",
        "Runtime singleton",
    )

    check_callable(
        report,
        runtime,
        "set_source",
        "Runtime set_source",
    )

    check_callable(
        report,
        runtime,
        "chat_with_mavi",
        "Runtime chat_with_mavi",
    )

    check_callable(
        report,
        runtime,
        "produce_music",
        "Runtime produce_music",
    )


# ============================================================
# WORKER
# ============================================================

def inspect_worker(
    report: IntegrationReport,
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

    check_attribute(
        report,
        worker,
        "RealAudioWorker",
        "Worker RealAudioWorker",
    )

    check_attribute(
        report,
        bridge,
        "WorkerBridge",
        "WorkerBridge",
    )

    check_attribute(
        report,
        runner,
        "StableAudioRunner",
        "StableAudioRunner",
    )

    check_attribute(
        report,
        stable_worker,
        "StableAudioWorker",
        "StableAudioWorker",
    )


# ============================================================
# ENVIRONMENT
# ============================================================

def inspect_environment(
    report: IntegrationReport,
) -> None:

    env_checks = {
        "MAVI_GENERATION_REAL_ONLY": (
            os.getenv(
                "MAVI_GENERATION_REAL_ONLY",
                "",
            )
        ),
        "MAVI_ALLOW_FAKE_AUDIO": (
            os.getenv(
                "MAVI_ALLOW_FAKE_AUDIO",
                "",
            )
        ),
        "MAVI_ALLOW_PROCEDURAL_AUDIO": (
            os.getenv(
                "MAVI_ALLOW_PROCEDURAL_AUDIO",
                "",
            )
        ),
        "MAVI_STABLE_AUDIO_3_DIR": (
            os.getenv(
                "MAVI_STABLE_AUDIO_3_DIR",
                "",
            )
        ),
        "MAVI_STABLE_AUDIO_CLI": (
            os.getenv(
                "MAVI_STABLE_AUDIO_CLI",
                "",
            )
        ),
    }

    real_only = (
        env_checks[
            "MAVI_GENERATION_REAL_ONLY"
        ]
    )

    fake = (
        env_checks[
            "MAVI_ALLOW_FAKE_AUDIO"
        ]
    )

    procedural = (
        env_checks[
            "MAVI_ALLOW_PROCEDURAL_AUDIO"
        ]
    )

    report.add(
        "ENV real generation",
        real_only.lower()
        in {
            "1",
            "true",
            "yes",
        },
        real_only or "NOT SET",
    )

    report.add(
        "ENV fake audio disabled",
        fake.lower()
        not in {
            "1",
            "true",
            "yes",
        },
        fake or "NOT SET",
    )

    report.add(
        "ENV procedural audio disabled",
        procedural.lower()
        not in {
            "1",
            "true",
            "yes",
        },
        procedural or "NOT SET",
    )

    stable_cli = (
        env_checks[
            "MAVI_STABLE_AUDIO_CLI"
        ]
    )

    if stable_cli:

        path = Path(
            stable_cli
        ).expanduser()

        report.add(
            "ENV Stable Audio CLI exists",
            path.exists()
            and path.is_file(),
            str(path),
            critical=False,
        )

    else:

        report.add(
            "ENV Stable Audio CLI exists",
            False,
            "NOT SET",
            critical=False,
        )

    stable_dir = (
        env_checks[
            "MAVI_STABLE_AUDIO_3_DIR"
        ]
    )

    if stable_dir:

        path = Path(
            stable_dir
        ).expanduser()

        report.add(
            "ENV Stable Audio root exists",
            path.exists()
            and path.is_dir(),
            str(path),
            critical=False,
        )

    else:

        report.add(
            "ENV Stable Audio root exists",
            False,
            "NOT SET",
            critical=False,
        )


# ============================================================
# SOURCE DISCOVERY
# ============================================================

def discover_source(
    report: IntegrationReport,
) -> Optional[Path]:

    if not SOURCE_DIR.exists():

        report.add(
            "SOURCE test directory",
            False,
            str(SOURCE_DIR),
            critical=False,
        )

        return None

    supported = {
        ".wav",
        ".mp3",
        ".flac",
        ".ogg",
        ".m4a",
        ".aac",
        ".wma",
    }

    matches = [
        item
        for item in SOURCE_DIR.iterdir()
        if (
            item.is_file()
            and item.suffix.lower()
            in supported
        )
    ]

    matches.sort(
        key=lambda item: item.name.lower()
    )

    if not matches:

        report.add(
            "SOURCE test audio",
            False,
            (
                "Kaynak klasöründe audio bulunamadı."
            ),
            critical=False,
        )

        return None

    source = matches[0]

    report.add(
        "SOURCE test audio",
        True,
        str(source),
        critical=False,
    )

    return source


# ============================================================
# AUDIO PATH TEST
# ============================================================

def inspect_audio_probe(
    report: IntegrationReport,
    modules: Dict[str, Any],
    source: Optional[Path],
) -> None:

    audio_io = modules.get(
        "core.audio_io"
    )

    if audio_io is None or source is None:
        return

    probe = getattr(
        audio_io,
        "probe_audio",
        None,
    )

    if not callable(probe):

        report.add(
            "AUDIO probe callable",
            False,
            "probe_audio yok.",
        )

        return

    try:

        result = probe(
            source
        )

        report.add(
            "AUDIO source probe",
            result is not None,
            str(result),
        )

    except Exception as exc:

        report.add(
            "AUDIO source probe",
            False,
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )


# ============================================================
# RENEWAL API TEST
# ============================================================

def inspect_renewal_builder(
    report: IntegrationReport,
    modules: Dict[str, Any],
) -> None:

    renewal = modules.get(
        "core.renewal"
    )

    if renewal is None:
        return

    function = getattr(
        renewal,
        "renew_from_command",
        None,
    )

    if not callable(function):

        return

    report.add(
        "RENEWAL command parser callable",
        True,
        "renew_from_command hazır.",
        critical=True,
    )


# ============================================================
# GENERATION POLICY
# ============================================================

def inspect_generation_policy(
    report: IntegrationReport,
    modules: Dict[str, Any],
) -> None:

    generation = modules.get(
        "core.generation"
    )

    if generation is None:
        return

    engine = getattr(
        generation,
        "GenerationEngine",
        None,
    )

    report.add(
        "GENERATION engine class",
        engine is not None,
        (
            type(engine).__name__
            if engine is not None
            else "yok"
        ),
    )


# ============================================================
# IMPORT ALL
# ============================================================

def load_modules(
    report: IntegrationReport,
) -> Dict[str, Any]:

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

    modules: Dict[
        str,
        Any
    ] = {}

    for name in names:

        modules[name] = (
            add_import_test(
                report,
                name,
            )
        )

    return modules


# ============================================================
# REPORT SAVE
# ============================================================

def save_report(
    report: IntegrationReport,
) -> None:

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            report.as_dict(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


# ============================================================
# PRINT
# ============================================================

def print_report(
    report: IntegrationReport,
) -> None:

    print()
    print(
        "============================================================"
    )
    print(
        "MAVI AI STUDIO"
    )
    print(
        "INTEGRATION TEST"
    )
    print(
        "============================================================"
    )
    print()

    for item in report.results:

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
                str(
                    item["detail"]
                )
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
        f"PASSED            : {report.passed}"
    )
    print(
        f"FAILED            : {report.failed}"
    )
    print(
        f"CRITICAL FAILURES : {report.critical_failures}"
    )
    print(
        "STATUS             : "
        + (
            "INTEGRATION READY"
            if report.success
            else "INTEGRATION NEEDS FIX"
        )
    )
    print(
        "============================================================"
    )
    print()


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    report = IntegrationReport()

    try:

        inspect_file_structure(
            report
        )

        modules = load_modules(
            report
        )

        config = modules.get(
            "config"
        )

        models = modules.get(
            "core.models"
        )

        if config is not None:

            inspect_config(
                report,
                config,
            )

            inspect_directories(
                report,
                config,
            )

        if models is not None:

            inspect_models(
                report,
                models,
            )

        inspect_core(
            report,
            modules,
        )

        inspect_ai(
            report,
            modules,
        )

        inspect_worker(
            report,
            modules,
        )

        inspect_environment(
            report
        )

        source = discover_source(
            report
        )

        inspect_audio_probe(
            report,
            modules,
            source,
        )

        inspect_renewal_builder(
            report,
            modules,
        )

        inspect_generation_policy(
            report,
            modules,
        )

    except Exception as exc:

        report.add(
            "INTEGRATION TEST INTERNAL ERROR",
            False,
            (
                f"{type(exc).__name__}: "
                f"{exc}\n"
                f"{traceback.format_exc()}"
            ),
        )

    try:

        save_report(
            report
        )

    except Exception:
        pass

    print_report(
        report
    )

    return (
        0
        if report.success
        else 1
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )