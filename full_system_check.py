# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
FULL SYSTEM CHECK
v0.1
============================================================

Prod. By Ufuk Akdoğan

Yeni MAVI AI Studio'nun bütün temel katmanlarını tek komutta
kontrol eder.

BU DOSYA:
- audio üretmez
- generation başlatmaz
- mix/master çalıştırmaz
- fake audio üretmez
- procedural audio üretmez
- placeholder audio üretmez

Kontrol katmanları:

1. Python ortamları
2. Dosya yapısı
3. Config
4. Core
5. AI
6. Worker
7. Stable Audio CLI
8. Environment
9. Source audio
10. Integration report
11. Pipeline inspection
12. Generation/renewal raporları
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# ROOT
# ============================================================

ROOT = (
    Path(__file__)
    .resolve()
    .parent
)

LOG_DIR = (
    ROOT
    / "logs"
)

OUTPUT_DIR = (
    ROOT
    / "output"
)


# ============================================================
# DATA
# ============================================================

@dataclass
class CheckItem:

    name: str

    success: bool

    detail: str = ""

    critical: bool = True

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


class SystemReport:

    def __init__(
        self,
    ) -> None:

        self.items: List[
            CheckItem
        ] = []

    def add(
        self,
        name: str,
        success: bool,
        detail: str = "",
        critical: bool = True,
    ) -> None:

        self.items.append(
            CheckItem(
                name=name,
                success=bool(success),
                detail=str(detail),
                critical=critical,
            )
        )

    @property
    def passed(
        self,
    ) -> int:

        return sum(
            1
            for item in self.items
            if item.success
        )

    @property
    def failed(
        self,
    ) -> int:

        return sum(
            1
            for item in self.items
            if not item.success
        )

    @property
    def critical_failures(
        self,
    ) -> int:

        return sum(
            1
            for item in self.items
            if (
                not item.success
                and item.critical
            )
        )

    @property
    def success(
        self,
    ) -> bool:

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
            "items": [
                item.as_dict()
                for item in self.items
            ],
        }


# ============================================================
# PATH CHECK
# ============================================================

def check_file(
    report: SystemReport,
    relative: str,
    critical: bool = True,
) -> None:

    path = (
        ROOT
        / relative
    )

    report.add(
        f"FILE {relative}",
        path.exists()
        and path.is_file(),
        str(path),
        critical=critical,
    )


def check_directory(
    report: SystemReport,
    path: Path,
    label: str,
    critical: bool = True,
) -> None:

    report.add(
        label,
        path.exists()
        and path.is_dir(),
        str(path),
        critical=critical,
    )


# ============================================================
# REQUIRED FILES
# ============================================================

def inspect_file_structure(
    report: SystemReport,
) -> None:

    required = [
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

        "prepare_generation.py",
        "execute_generation.py",
        "validate_generation.py",
        "validate_renewal.py",
        "finalize_renewal.py",
        "production_report.py",

        "integration_test.py",
        "inspect_pipeline.py",
        "worker_status.py",
        "create_worker_request.py",

        "requirements.txt",
        "requirements-worker.txt",
    ]

    for relative in required:

        check_file(
            report,
            relative,
        )


# ============================================================
# PYTHON ENVIRONMENT
# ============================================================

def run_python_version(
    path: Path,
) -> tuple[
    bool,
    str,
]:

    if not path.exists():

        return (
            False,
            "Python bulunamadı.",
        )

    try:

        process = subprocess.run(
            [
                str(path),
                "--version",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    except OSError as exc:

        return (
            False,
            str(exc),
        )

    detail = (
        process.stdout.strip()
        or process.stderr.strip()
    )

    return (
        process.returncode == 0,
        detail,
    )


def inspect_python(
    report: SystemReport,
) -> None:

    main_python = (
        ROOT
        / ".venv"
        / "Scripts"
        / "python.exe"
    )

    worker_python = (
        ROOT
        / ".worker_venv"
        / "Scripts"
        / "python.exe"
    )

    success, detail = (
        run_python_version(
            main_python
        )
    )

    report.add(
        "MAIN PYTHON",
        success,
        detail,
    )

    success, detail = (
        run_python_version(
            worker_python
        )
    )

    report.add(
        "WORKER PYTHON",
        success,
        detail,
    )


# ============================================================
# CONFIG
# ============================================================

def inspect_config(
    report: SystemReport,
) -> Optional[Any]:

    try:

        config = importlib.import_module(
            "config"
        )

    except Exception as exc:

        report.add(
            "CONFIG IMPORT",
            False,
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )

        return None

    report.add(
        "CONFIG IMPORT",
        True,
        str(
            getattr(
                config,
                "__file__",
                "",
            )
        ),
    )

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
        "REQUIRE_REAL_GENERATION",
        "ALLOW_FAKE_AUDIO",
        "ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO",
    ]

    for name in required:

        exists = hasattr(
            config,
            name,
        )

        report.add(
            f"CONFIG {name}",
            exists,
            (
                repr(
                    getattr(
                        config,
                        name,
                    )
                )
                if exists
                else "Eksik"
            ),
        )

    report.add(
        "CONFIG REAL ONLY",
        getattr(
            config,
            "REQUIRE_REAL_GENERATION",
            False,
        ) is True,
        repr(
            getattr(
                config,
                "REQUIRE_REAL_GENERATION",
                None,
            )
        ),
    )

    report.add(
        "CONFIG FAKE AUDIO OFF",
        getattr(
            config,
            "ALLOW_FAKE_AUDIO",
            True,
        ) is False,
        repr(
            getattr(
                config,
                "ALLOW_FAKE_AUDIO",
                None,
            )
        ),
    )

    report.add(
        "CONFIG PROCEDURAL OFF",
        getattr(
            config,
            "ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO",
            True,
        ) is False,
        repr(
            getattr(
                config,
                "ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO",
                None,
            )
        ),
    )

    return config


# ============================================================
# DIRECTORIES
# ============================================================

def inspect_directories(
    report: SystemReport,
    config: Any,
) -> None:

    names = [
        "CORE_DIR",
        "AI_DIR",
        "ASSETS_DIR",
        "AUDIO_DIR",
        "OUTPUT_DIR",
        "LOG_DIR",
        "BUILD_DIR",
        "DIST_DIR",
        "SOURCE_DIR",
        "STEMS_DIR",
        "MIX_DIR",
        "MASTER_DIR",
    ]

    for name in names:

        path = getattr(
            config,
            name,
            None,
        )

        if path is None:

            report.add(
                f"DIRECTORY {name}",
                False,
                "Config değeri yok.",
            )

            continue

        check_directory(
            report,
            Path(path),
            f"DIRECTORY {name}",
        )


# ============================================================
# PIPELINE
# ============================================================

def inspect_pipeline(
    report: SystemReport,
    config: Any,
) -> None:

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

    actual = list(
        getattr(
            config,
            "PIPELINE_STAGES",
            (),
        )
    )

    report.add(
        "PIPELINE STAGES",
        actual == expected,
        (
            f"actual={actual}"
        ),
    )


# ============================================================
# MODULE IMPORTS
# ============================================================

def inspect_imports(
    report: SystemReport,
) -> Dict[str, Any]:

    modules: Dict[
        str,
        Any
    ] = {}

    names = [
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
        "stable_audio_worker",
        "stable_audio_runner",
    ]

    for name in names:

        try:

            module = importlib.import_module(
                name
            )

        except Exception as exc:

            report.add(
                f"IMPORT {name}",
                False,
                (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

            modules[name] = None

            continue

        report.add(
            f"IMPORT {name}",
            True,
            str(
                getattr(
                    module,
                    "__file__",
                    "",
                )
            ),
        )

        modules[name] = module

    return modules


# ============================================================
# API CHECKS
# ============================================================

def inspect_api(
    report: SystemReport,
    modules: Dict[str, Any],
) -> None:

    checks = {
        "core.models": [
            "SourceAudio",
            "AudioFeatures",
            "RegionalIdentity",
            "MusicDNA",
            "RenewalRequest",
            "ProductionResult",
            "MixResult",
            "MasterResult",
        ],

        "core.audio_io": [
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
        ],

        "core.renewal": [
            "RenewalEngine",
            "create_renewal_plan",
            "build_renewal_request",
        ],

        "core.generation": [
            "GenerationEngine",
            "GenerationRequest",
            "generate_audio",
        ],

        "core.continuity": [
            "ContinuityGenerator",
            "ContinuityPlanner",
            "ContinuityStitcher",
        ],

        "core.quality": [
            "QualityGate",
            "check_audio_quality",
        ],

        "core.mix": [
            "MixEngine",
            "MixPlanner",
            "mix_audio",
        ],

        "core.master": [
            "MasterEngine",
            "master_audio",
        ],

        "core.export": [
            "ExportEngine",
            "export_audio",
            "export_master",
        ],

        "ai.brain": [
            "ProducerBrain",
            "ProducerIntent",
            "brain",
        ],

        "ai.engine": [
            "AIProductionEngine",
            "engine",
            "run_production",
            "execute_command",
        ],

        "ai.runtime": [
            "MaviRuntime",
            "runtime",
            "set_source",
            "chat_with_mavi",
            "produce_music",
        ],

        "worker": [
            "GenerationRequest",
            "RealAudioWorker",
        ],

        "worker_bridge": [
            "WorkerRequest",
            "WorkerBridge",
        ],

        "stable_audio_runner": [
            "StableAudioRunRequest",
            "StableAudioRunner",
        ],

        "stable_audio_worker": [
            "StableAudioRequest",
            "StableAudioWorker",
        ],
    }

    for module_name, names in checks.items():

        module = modules.get(
            module_name
        )

        if module is None:
            continue

        for name in names:

            value = getattr(
                module,
                name,
                None,
            )

            report.add(
                (
                    f"API "
                    f"{module_name}.{name}"
                ),
                value is not None,
                (
                    "OK"
                    if value is not None
                    else "Eksik"
                ),
            )


# ============================================================
# ENVIRONMENT
# ============================================================

def inspect_environment(
    report: SystemReport,
) -> None:

    real_only = os.getenv(
        "MAVI_GENERATION_REAL_ONLY",
        "",
    ).strip().lower()

    fake = os.getenv(
        "MAVI_ALLOW_FAKE_AUDIO",
        "",
    ).strip().lower()

    procedural = os.getenv(
        "MAVI_ALLOW_PROCEDURAL_AUDIO",
        "",
    ).strip().lower()

    placeholder = os.getenv(
        "MAVI_ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO",
        "",
    ).strip().lower()

    report.add(
        "ENV REAL GENERATION",
        real_only in {
            "1",
            "true",
            "yes",
        },
        real_only or "NOT SET",
    )

    report.add(
        "ENV FAKE AUDIO OFF",
        fake not in {
            "1",
            "true",
            "yes",
        },
        fake or "NOT SET",
    )

    report.add(
        "ENV PROCEDURAL OFF",
        procedural not in {
            "1",
            "true",
            "yes",
        },
        procedural or "NOT SET",
    )

    report.add(
        "ENV PLACEHOLDER OFF",
        placeholder not in {
            "1",
            "true",
            "yes",
        },
        placeholder or "NOT SET",
    )

    cli = os.getenv(
        "MAVI_STABLE_AUDIO_CLI",
        "",
    ).strip()

    if cli:

        path = (
            Path(
                cli
            )
            .expanduser()
            .resolve()
        )

        report.add(
            "ENV STABLE AUDIO CLI",
            path.exists()
            and path.is_file(),
            str(path),
            critical=False,
        )

    else:

        report.add(
            "ENV STABLE AUDIO CLI",
            False,
            "NOT SET",
            critical=False,
        )


# ============================================================
# SOURCE
# ============================================================

def inspect_source(
    report: SystemReport,
    config: Any,
) -> Optional[Path]:

    source_dir = Path(
        getattr(
            config,
            "SOURCE_DIR",
            ROOT / "audio" / "source",
        )
    )

    if not source_dir.exists():

        report.add(
            "SOURCE DIRECTORY",
            False,
            str(source_dir),
            critical=False,
        )

        return None

    extensions = {
        ".wav",
        ".mp3",
        ".flac",
        ".ogg",
        ".m4a",
        ".aac",
        ".wma",
    }

    files = sorted(
        [
            path
            for path in source_dir.iterdir()
            if (
                path.is_file()
                and path.suffix.lower()
                in extensions
            )
        ],
        key=lambda path: path.name.lower(),
    )

    report.add(
        "SOURCE DIRECTORY",
        True,
        str(source_dir),
        critical=False,
    )

    report.add(
        "SOURCE AUDIO AVAILABLE",
        bool(files),
        (
            str(files[0])
            if files
            else "Audio bulunamadı."
        ),
        critical=False,
    )

    return (
        files[0]
        if files
        else None
    )


# ============================================================
# WORKER STATUS
# ============================================================

def inspect_worker_status(
    report: SystemReport,
) -> None:

    worker_python = (
        ROOT
        / ".worker_venv"
        / "Scripts"
        / "python.exe"
    )

    runner = (
        ROOT
        / "stable_audio_runner.py"
    )

    if not worker_python.exists():

        report.add(
            "WORKER STATUS COMMAND",
            False,
            "Worker Python bulunamadı.",
            critical=False,
        )

        return

    if not runner.exists():

        report.add(
            "WORKER STATUS COMMAND",
            False,
            "Runner bulunamadı.",
            critical=False,
        )

        return

    try:

        process = subprocess.run(
            [
                str(worker_python),
                str(runner),
                "--status",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    except OSError as exc:

        report.add(
            "WORKER STATUS COMMAND",
            False,
            str(exc),
            critical=False,
        )

        return

    report.add(
        "WORKER STATUS COMMAND",
        process.returncode == 0,
        (
            process.stdout[-1000:]
            or process.stderr[-1000:]
        ),
        critical=False,
    )


# ============================================================
# HISTORICAL REPORTS
# ============================================================

def inspect_saved_reports(
    report: SystemReport,
) -> None:

    files = [
        LOG_DIR / "integration_test.json",
        LOG_DIR / "pipeline_inspection.json",
        LOG_DIR / "worker_status.json",

        OUTPUT_DIR / "generation_result.json",
        OUTPUT_DIR / "generation_validation.json",
        OUTPUT_DIR / "shote_mori_validation.json",
        OUTPUT_DIR / "finalize_renewal_result.json",
        OUTPUT_DIR / "MAVI_production_report.json",
    ]

    for path in files:

        exists = (
            path.exists()
            and path.is_file()
        )

        report.add(
            f"REPORT {path.name}",
            exists,
            str(path),
            critical=False,
        )


# ============================================================
# RUN PRECHECK
# ============================================================

def run_existing_preflight(
    report: SystemReport,
) -> None:

    preflight = (
        ROOT
        / "preflight.py"
    )

    python = (
        ROOT
        / ".venv"
        / "Scripts"
        / "python.exe"
    )

    if not python.exists():

        return

    if not preflight.exists():

        return

    try:

        process = subprocess.run(
            [
                str(python),
                str(preflight),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    except OSError as exc:

        report.add(
            "PREFLIGHT EXECUTION",
            False,
            str(exc),
        )

        return

    report.add(
        "PREFLIGHT EXECUTION",
        process.returncode == 0,
        (
            process.stdout[-1500:]
            or process.stderr[-1500:]
        ),
    )


# ============================================================
# SAVE
# ============================================================

def save_report(
    report: SystemReport,
) -> Path:

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        LOG_DIR
        / "full_system_check.json"
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
# PRINT
# ============================================================

def print_report(
    report: SystemReport,
) -> None:

    print()
    print(
        "============================================================"
    )
    print(
        "MAVI AI STUDIO"
    )
    print(
        "FULL SYSTEM CHECK"
    )
    print(
        "============================================================"
    )
    print()

    for item in report.items:

        prefix = (
            "[ OK ]"
            if item.success
            else "[FAIL]"
        )

        print(
            f"{prefix} {item.name}"
        )

        if item.detail:

            detail = (
                item.detail
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
            "SYSTEM READY"
            if report.success
            else "SYSTEM NEEDS FIX"
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

    report = SystemReport()

    inspect_file_structure(
        report
    )

    inspect_python(
        report
    )

    config = inspect_config(
        report
    )

    if config is not None:

        inspect_directories(
            report,
            config,
        )

        inspect_pipeline(
            report,
            config,
        )

    modules = inspect_imports(
        report
    )

    inspect_api(
        report,
        modules,
    )

    inspect_environment(
        report
    )

    if config is not None:

        inspect_source(
            report,
            config,
        )

    inspect_worker_status(
        report
    )

    inspect_saved_reports(
        report
    )

    # Preflight ayrıca çalıştırılır; generation başlamaz.
    run_existing_preflight(
        report
    )

    try:

        report_path = save_report(
            report
        )

    except Exception:

        report_path = (
            LOG_DIR
            / "full_system_check.json"
        )

    print_report(
        report
    )

    print(
        f"REPORT: {report_path}"
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