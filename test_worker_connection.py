# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
WORKER CONNECTION TEST
v0.1
============================================================

Prod. By Ufuk Akdoğan

Bu test:
- Ana Python 3.14 ortamını
- Worker Python 3.13 ortamını
- stable_audio_runner.py dosyasını
- Stable Audio 3 CLI yolunu
- worker_bridge.py importunu
- worker.py importunu

kontrol eder.

GERÇEK SES ÜRETİMİ YAPMAZ.

Bu nedenle:
- model indirme başlatmaz
- generation başlatmaz
- test WAV oluşturmaz
- fake/procedural audio üretmez
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys

from pathlib import Path
from typing import Any, Dict, List


# ============================================================
# PATHS
# ============================================================

ROOT = Path(
    __file__
).resolve().parent

MAIN_PYTHON = (
    ROOT
    / ".venv"
    / "Scripts"
    / "python.exe"
)

WORKER_PYTHON = (
    ROOT
    / ".worker_venv"
    / "Scripts"
    / "python.exe"
)

RUNNER = (
    ROOT
    / "stable_audio_runner.py"
)

WORKER = (
    ROOT
    / "worker.py"
)

BRIDGE = (
    ROOT
    / "worker_bridge.py"
)

APP = (
    ROOT
    / "app.py"
)

PREFLIGHT = (
    ROOT
    / "preflight.py"
)


# ============================================================
# RESULT
# ============================================================

class TestReport:

    def __init__(self) -> None:

        self.results: List[
            Dict[str, Any]
        ] = []

    def add(
        self,
        name: str,
        success: bool,
        detail: str = "",
    ) -> None:

        self.results.append(
            {
                "name": name,
                "success": success,
                "detail": detail,
            }
        )

    @property
    def passed(
        self,
    ) -> int:

        return sum(
            1
            for item in self.results
            if item["success"]
        )

    @property
    def failed(
        self,
    ) -> int:

        return sum(
            1
            for item in self.results
            if not item["success"]
        )

    @property
    def success(
        self,
    ) -> bool:

        return self.failed == 0

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "success": self.success,
            "passed": self.passed,
            "failed": self.failed,
            "results": self.results,
        }


# ============================================================
# HELPERS
# ============================================================

def check_file(
    report: TestReport,
    name: str,
    path: Path,
) -> None:

    if path.exists() and path.is_file():

        report.add(
            name,
            True,
            str(path),
        )

    else:

        report.add(
            name,
            False,
            f"Bulunamadı: {path}",
        )


def check_python(
    report: TestReport,
    name: str,
    path: Path,
) -> None:

    if not path.exists():

        report.add(
            name,
            False,
            f"Python bulunamadı: {path}",
        )

        return

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

        report.add(
            name,
            False,
            str(exc),
        )

        return

    success = (
        process.returncode == 0
    )

    detail = (
        process.stdout.strip()
        or process.stderr.strip()
    )

    report.add(
        name,
        success,
        detail,
    )


def import_check(
    report: TestReport,
    module_name: str,
) -> None:

    try:

        module = importlib.import_module(
            module_name
        )

        report.add(
            f"Import: {module_name}",
            True,
            str(
                getattr(
                    module,
                    "__file__",
                    "",
                )
            ),
        )

    except Exception as exc:

        report.add(
            f"Import: {module_name}",
            False,
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )


def read_cli_environment() -> Dict[str, str]:

    return {
        "MAVI_STABLE_AUDIO_3_DIR": (
            os.getenv(
                "MAVI_STABLE_AUDIO_3_DIR",
                "",
            ).strip()
        ),
        "MAVI_STABLE_AUDIO_CLI": (
            os.getenv(
                "MAVI_STABLE_AUDIO_CLI",
                "",
            ).strip()
        ),
        "MAVI_WORKER_PYTHON": (
            os.getenv(
                "MAVI_WORKER_PYTHON",
                "",
            ).strip()
        ),
        "MAVI_WORKER_SCRIPT": (
            os.getenv(
                "MAVI_WORKER_SCRIPT",
                "",
            ).strip()
        ),
    }


def run_runner_status(
    report: TestReport,
) -> None:

    if not WORKER_PYTHON.exists():

        report.add(
            "Stable Audio runner status",
            False,
            "Worker Python bulunamadı.",
        )

        return

    if not RUNNER.exists():

        report.add(
            "Stable Audio runner status",
            False,
            "stable_audio_runner.py bulunamadı.",
        )

        return

    try:

        process = subprocess.run(
            [
                str(WORKER_PYTHON),
                str(RUNNER),
                "--status",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    except OSError as exc:

        report.add(
            "Stable Audio runner status",
            False,
            str(exc),
        )

        return

    if process.returncode != 0:

        report.add(
            "Stable Audio runner status",
            False,
            (
                process.stdout
                or process.stderr
            )[-3000:],
        )

        return

    report.add(
        "Stable Audio runner status",
        True,
        process.stdout[-3000:],
    )


# ============================================================
# ENVIRONMENT CHECKS
# ============================================================

def check_environment(
    report: TestReport,
) -> None:

    environment = (
        read_cli_environment()
    )

    stable_cli = (
        environment[
            "MAVI_STABLE_AUDIO_CLI"
        ]
    )

    if stable_cli:

        cli_path = Path(
            stable_cli
        ).expanduser()

        report.add(
            "Stable Audio CLI path",
            cli_path.exists()
            and cli_path.is_file(),
            str(cli_path),
        )

    else:

        report.add(
            "Stable Audio CLI path",
            False,
            (
                "MAVI_STABLE_AUDIO_CLI "
                "tanımlı değil."
            ),
        )

    worker_python = (
        environment[
            "MAVI_WORKER_PYTHON"
        ]
    )

    if worker_python:

        report.add(
            "Worker environment variable",
            Path(
                worker_python
            ).exists(),
            worker_python,
        )

    else:

        report.add(
            "Worker environment variable",
            False,
            (
                "MAVI_WORKER_PYTHON "
                "tanımlı değil."
            ),
        )

    worker_script = (
        environment[
            "MAVI_WORKER_SCRIPT"
        ]
    )

    if worker_script:

        report.add(
            "Worker script environment variable",
            Path(
                worker_script
            ).exists(),
            worker_script,
        )

    else:

        report.add(
            "Worker script environment variable",
            False,
            (
                "MAVI_WORKER_SCRIPT "
                "tanımlı değil."
            ),
        )

    generation_only = (
        os.getenv(
            "MAVI_GENERATION_REAL_ONLY",
            "",
        ).strip()
    )

    fake_audio = (
        os.getenv(
            "MAVI_ALLOW_FAKE_AUDIO",
            "",
        ).strip()
    )

    procedural = (
        os.getenv(
            "MAVI_ALLOW_PROCEDURAL_AUDIO",
            "",
        ).strip()
    )

    report.add(
        "Real generation policy",
        generation_only
        in {
            "1",
            "true",
            "TRUE",
            "yes",
            "YES",
        },
        (
            f"MAVI_GENERATION_REAL_ONLY="
            f"{generation_only or 'NOT SET'}"
        ),
    )

    report.add(
        "Fake audio disabled",
        fake_audio
        not in {
            "1",
            "true",
            "TRUE",
            "yes",
            "YES",
        },
        (
            f"MAVI_ALLOW_FAKE_AUDIO="
            f"{fake_audio or 'NOT SET'}"
        ),
    )

    report.add(
        "Procedural audio disabled",
        procedural
        not in {
            "1",
            "true",
            "TRUE",
            "yes",
            "YES",
        },
        (
            f"MAVI_ALLOW_PROCEDURAL_AUDIO="
            f"{procedural or 'NOT SET'}"
        ),
    )


# ============================================================
# PYTHON IMPORT ENVIRONMENT
# ============================================================

def check_worker_imports(
    report: TestReport,
) -> None:

    # Worker modules are imported by the current interpreter
    # only to detect syntax/module-level failures.
    # No generation is started.

    modules = [
        "worker_bridge",
        "worker",
        "stable_audio_runner",
    ]

    for module_name in modules:

        import_check(
            report,
            module_name,
        )


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    report = TestReport()

    print()
    print(
        "============================================================"
    )
    print(
        "MAVI AI STUDIO"
    )
    print(
        "WORKER CONNECTION TEST"
    )
    print(
        "============================================================"
    )
    print()

    # --------------------------------------------------------
    # FILES
    # --------------------------------------------------------

    print(
        "[1] DOSYALAR"
    )

    check_file(
        report,
        "config.py",
        ROOT / "config.py",
    )

    check_file(
        report,
        "app.py",
        APP,
    )

    check_file(
        report,
        "worker.py",
        WORKER,
    )

    check_file(
        report,
        "worker_bridge.py",
        BRIDGE,
    )

    check_file(
        report,
        "stable_audio_runner.py",
        RUNNER,
    )

    check_file(
        report,
        "preflight.py",
        PREFLIGHT,
    )

    print()

    # --------------------------------------------------------
    # PYTHON
    # --------------------------------------------------------

    print(
        "[2] PYTHON"
    )

    check_python(
        report,
        "Ana Python 3.14",
        MAIN_PYTHON,
    )

    check_python(
        report,
        "Worker Python 3.13",
        WORKER_PYTHON,
    )

    print()

    # --------------------------------------------------------
    # ENV
    # --------------------------------------------------------

    print(
        "[3] ENVIRONMENT"
    )

    check_environment(
        report
    )

    print()

    # --------------------------------------------------------
    # IMPORTS
    # --------------------------------------------------------

    print(
        "[4] MODULE IMPORTLARI"
    )

    check_worker_imports(
        report
    )

    print()

    # --------------------------------------------------------
    # RUNNER STATUS
    # --------------------------------------------------------

    print(
        "[5] STABLE AUDIO RUNNER"
    )

    run_runner_status(
        report
    )

    print()

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    for item in report.results:

        prefix = (
            "[ OK ]"
            if item["success"]
            else "[FAIL]"
        )

        print(
            f"{prefix} "
            f"{item['name']}"
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

            if len(detail) > 220:
                detail = (
                    detail[-220:]
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
            "READY"
            if report.success
            else "NOT READY"
        )
    )

    print(
        "============================================================"
    )
    print()

    # --------------------------------------------------------
    # JSON OUTPUT
    # --------------------------------------------------------

    result_file = (
        ROOT
        / "logs"
        / "worker_connection_test.json"
    )

    try:

        result_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        result_file.write_text(
            json.dumps(
                report.as_dict(),
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    except OSError:
        pass

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