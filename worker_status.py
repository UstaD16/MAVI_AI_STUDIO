# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
WORKER STATUS
v0.1
============================================================

Prod. By Ufuk Akdoğan

Real Audio Worker durumunu tek noktadan kontrol eder.

BU DOSYA:
- generation başlatmaz
- audio üretmez
- model çalıştırmaz
- fake/procedural audio üretmez
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict


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

LOG_DIR = (
    ROOT
    / "logs"
)

STATUS_FILE = (
    LOG_DIR
    / "worker_status.json"
)


# ============================================================
# ENVIRONMENT HELPERS
# ============================================================

def env_value(
    name: str,
) -> str:

    return (
        os.getenv(
            name,
            "",
        )
        .strip()
    )


def path_status(
    value: str,
) -> Dict[str, Any]:

    if not value:

        return {
            "configured": False,
            "exists": False,
            "path": "",
        }

    path = (
        Path(
            value
        )
        .expanduser()
        .resolve()
    )

    return {
        "configured": True,
        "exists": path.exists(),
        "file": path.is_file(),
        "directory": path.is_dir(),
        "path": str(path),
    }


# ============================================================
# PYTHON CHECK
# ============================================================

def python_status(
    path: Path,
) -> Dict[str, Any]:

    result: Dict[str, Any] = {
        "exists": path.exists(),
        "path": str(path),
        "version": "",
        "success": False,
        "error": "",
    }

    if not path.exists():

        result["error"] = (
            "Python bulunamadı."
        )

        return result

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

        result["error"] = str(
            exc
        )

        return result

    version = (
        process.stdout.strip()
        or process.stderr.strip()
    )

    result["version"] = version

    result["success"] = (
        process.returncode == 0
    )

    if not result["success"]:

        result["error"] = (
            process.stderr.strip()
            or "Python çalıştırılamadı."
        )

    return result


# ============================================================
# RUNNER STATUS
# ============================================================

def runner_status() -> Dict[str, Any]:

    result: Dict[str, Any] = {
        "success": False,
        "stdout": "",
        "stderr": "",
        "payload": {},
    }

    if not WORKER_PYTHON.exists():

        result["stderr"] = (
            "Worker Python bulunamadı."
        )

        return result

    if not RUNNER.exists():

        result["stderr"] = (
            "stable_audio_runner.py bulunamadı."
        )

        return result

    try:

        process = subprocess.run(
            [
                str(WORKER_PYTHON),
                str(RUNNER),
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

        result["stderr"] = str(
            exc
        )

        return result

    result["stdout"] = (
        process.stdout or ""
    )

    result["stderr"] = (
        process.stderr or ""
    )

    if process.returncode != 0:

        return result

    try:

        payload = json.loads(
            result["stdout"]
        )

    except json.JSONDecodeError:

        return result

    result["payload"] = payload

    result["success"] = True

    return result


# ============================================================
# WORKER STATUS
# ============================================================

def build_status() -> Dict[str, Any]:

    generation_real_only = env_value(
        "MAVI_GENERATION_REAL_ONLY"
    )

    fake_audio = env_value(
        "MAVI_ALLOW_FAKE_AUDIO"
    )

    procedural_audio = env_value(
        "MAVI_ALLOW_PROCEDURAL_AUDIO"
    )

    placeholder_audio = env_value(
        "MAVI_ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO"
    )

    stable_cli = env_value(
        "MAVI_STABLE_AUDIO_CLI"
    )

    stable_root = env_value(
        "MAVI_STABLE_AUDIO_3_DIR"
    )

    worker_python_env = env_value(
        "MAVI_WORKER_PYTHON"
    )

    worker_script_env = env_value(
        "MAVI_WORKER_SCRIPT"
    )

    runner = runner_status()

    return {
        "status_version": "0.1",

        "root": str(
            ROOT
        ),

        "current_python": {
            "path": sys.executable,
            "version": sys.version,
        },

        "main_python": python_status(
            MAIN_PYTHON
        ),

        "worker_python": python_status(
            WORKER_PYTHON
        ),

        "files": {
            "worker": {
                "exists": WORKER.exists(),
                "path": str(WORKER),
            },
            "bridge": {
                "exists": BRIDGE.exists(),
                "path": str(BRIDGE),
            },
            "runner": {
                "exists": RUNNER.exists(),
                "path": str(RUNNER),
            },
        },

        "environment": {
            "stable_audio_root": path_status(
                stable_root
            ),
            "stable_audio_cli": path_status(
                stable_cli
            ),
            "worker_python": path_status(
                worker_python_env
            ),
            "worker_script": path_status(
                worker_script_env
            ),
        },

        "policy": {
            "real_generation_only": (
                generation_real_only.lower()
                in {
                    "1",
                    "true",
                    "yes",
                }
            ),
            "fake_audio_allowed": (
                fake_audio.lower()
                in {
                    "1",
                    "true",
                    "yes",
                }
            ),
            "procedural_audio_allowed": (
                procedural_audio.lower()
                in {
                    "1",
                    "true",
                    "yes",
                }
            ),
            "placeholder_audio_allowed": (
                placeholder_audio.lower()
                in {
                    "1",
                    "true",
                    "yes",
                }
            ),
        },

        "runner": runner,

        "real_worker_ready": False,
        "ready_reasons": [],
        "blocking_reasons": [],
    }


# ============================================================
# READINESS
# ============================================================

def evaluate_readiness(
    status: Dict[str, Any],
) -> Dict[str, Any]:

    blocking: list[str] = []
    ready: list[str] = []

    main_python = status[
        "main_python"
    ]

    worker_python = status[
        "worker_python"
    ]

    files = status[
        "files"
    ]

    environment = status[
        "environment"
    ]

    policy = status[
        "policy"
    ]

    runner = status[
        "runner"
    ]

    if main_python.get(
        "success"
    ):

        ready.append(
            "Ana Python hazır."
        )

    else:

        blocking.append(
            "Ana Python hazır değil."
        )

    if worker_python.get(
        "success"
    ):

        ready.append(
            "Worker Python hazır."
        )

    else:

        blocking.append(
            "Worker Python hazır değil."
        )

    if files[
        "worker"
    ][
        "exists"
    ]:

        ready.append(
            "worker.py mevcut."
        )

    else:

        blocking.append(
            "worker.py eksik."
        )

    if files[
        "bridge"
    ][
        "exists"
    ]:

        ready.append(
            "worker_bridge.py mevcut."
        )

    else:

        blocking.append(
            "worker_bridge.py eksik."
        )

    if files[
        "runner"
    ][
        "exists"
    ]:

        ready.append(
            "stable_audio_runner.py mevcut."
        )

    else:

        blocking.append(
            "stable_audio_runner.py eksik."
        )

    if environment[
        "stable_audio_cli"
    ].get(
        "exists"
    ):

        ready.append(
            "Stable Audio CLI mevcut."
        )

    else:

        blocking.append(
            "Stable Audio CLI bulunamadı."
        )

    if runner.get(
        "success"
    ):

        ready.append(
            "Stable Audio runner cevap veriyor."
        )

    else:

        blocking.append(
            "Stable Audio runner status başarısız."
        )

    if policy[
        "real_generation_only"
    ]:

        ready.append(
            "Real generation politikası aktif."
        )

    else:

        blocking.append(
            "Real generation-only politikası aktif değil."
        )

    if not policy[
        "fake_audio_allowed"
    ]:

        ready.append(
            "Fake audio kapalı."
        )

    else:

        blocking.append(
            "Fake audio açık."
        )

    if not policy[
        "procedural_audio_allowed"
    ]:

        ready.append(
            "Procedural audio kapalı."
        )

    else:

        blocking.append(
            "Procedural audio açık."
        )

    if not policy[
        "placeholder_audio_allowed"
    ]:

        ready.append(
            "Placeholder audio kapalı."
        )

    else:

        blocking.append(
            "Placeholder audio açık."
        )

    return {
        "real_worker_ready": (
            len(blocking) == 0
        ),
        "ready_reasons": ready,
        "blocking_reasons": blocking,
    }


# ============================================================
# SAVE
# ============================================================

def save_status(
    status: Dict[str, Any],
) -> Path:

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    STATUS_FILE.write_text(
        json.dumps(
            status,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return STATUS_FILE


# ============================================================
# PRINT
# ============================================================

def print_status(
    status: Dict[str, Any],
) -> None:

    print()
    print(
        "============================================================"
    )
    print(
        "MAVI AI STUDIO"
    )
    print(
        "REAL WORKER STATUS"
    )
    print(
        "============================================================"
    )
    print()

    print(
        "MAIN PYTHON"
    )

    print(
        f"  {status['main_python']['version']}"
    )

    print()

    print(
        "WORKER PYTHON"
    )

    print(
        f"  {status['worker_python']['version']}"
    )

    print()

    print(
        "STABLE AUDIO CLI"
    )

    cli = status[
        "environment"
    ][
        "stable_audio_cli"
    ]

    print(
        f"  {cli['path'] or 'NOT SET'}"
    )

    print(
        f"  EXISTS: {cli['exists']}"
    )

    print()

    runner = status[
        "runner"
    ]

    print(
        "RUNNER"
    )

    print(
        f"  SUCCESS: {runner['success']}"
    )

    if runner.get(
        "payload"
    ):

        payload = (
            runner["payload"]
        )

        print(
            f"  CLI FOUND: "
            f"{payload.get('cli_found', False)}"
        )

        print(
            f"  REAL GENERATION: "
            f"{payload.get('real_generation', True)}"
        )

    print()

    policy = status[
        "policy"
    ]

    print(
        "POLICY"
    )

    print(
        f"  REAL ONLY       : "
        f"{policy['real_generation_only']}"
    )

    print(
        f"  FAKE AUDIO      : "
        f"{policy['fake_audio_allowed']}"
    )

    print(
        f"  PROCEDURAL      : "
        f"{policy['procedural_audio_allowed']}"
    )

    print(
        f"  PLACEHOLDER     : "
        f"{policy['placeholder_audio_allowed']}"
    )

    print()

    print(
        "============================================================"
    )

    if status[
        "real_worker_ready"
    ]:

        print(
            "STATUS : REAL WORKER READY"
        )

    else:

        print(
            "STATUS : REAL WORKER NOT READY"
        )

        print()

        for reason in status[
            "blocking_reasons"
        ]:

            print(
                f"[BLOCK] {reason}"
            )

    print(
        "============================================================"
    )
    print()


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    status = build_status()

    readiness = evaluate_readiness(
        status
    )

    status.update(
        readiness
    )

    try:

        path = save_status(
            status
        )

        status["status_file"] = str(
            path
        )

    except OSError:

        status["status_file"] = ""

    print_status(
        status
    )

    return (
        0
        if status["real_worker_ready"]
        else 1
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )