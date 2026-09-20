# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
BACKUP MANIFEST
v0.1
============================================================

Prod. By Ufuk Akdoğan

Yeni MAVI AI Studio mimarisinin mevcut dosya yapısını ve
durumunu yedekleme amacıyla JSON manifest olarak kaydeder.

BU DOSYA:
- audio üretmez
- generation başlatmaz
- dosyaları değiştirmez
- yalnızca mevcut yapıyı kaydeder
"""

from __future__ import annotations

import hashlib
import json
import sys

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


ROOT = (
    Path(__file__)
    .resolve()
    .parent
)

OUTPUT_DIR = (
    ROOT / "output"
)

LOG_DIR = (
    ROOT / "logs"
)

MANIFEST = (
    LOG_DIR
    / "mavi_backup_manifest.json"
)


# ============================================================
# FILES
# ============================================================

IMPORTANT_FILES = [
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
    "pipeline_controller.py",
    "mavi_paths.py",
    "mavi_pipeline_status.py",
    "worker_status.py",
    "integration_test.py",
    "inspect_pipeline.py",
    "create_worker_request.py",
    "full_system_check.py",
]


# ============================================================
# HASH
# ============================================================

def sha256_file(
    path: Path,
) -> str:

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:

        while True:

            chunk = handle.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


# ============================================================
# FILE INFO
# ============================================================

def file_info(
    relative: str,
) -> Dict[str, Any]:

    path = (
        ROOT / relative
    )

    if not path.exists():

        return {
            "path": relative,
            "exists": False,
        }

    info = {
        "path": relative,
        "exists": True,
        "is_file": path.is_file(),
        "size_bytes": (
            path.stat().st_size
            if path.is_file()
            else 0
        ),
    }

    if path.is_file():

        try:

            info[
                "sha256"
            ] = sha256_file(
                path
            )

        except OSError:

            info[
                "sha256"
            ] = ""

    return info


# ============================================================
# DIRECTORY INFO
# ============================================================

def directory_info(
    path: Path,
) -> Dict[str, Any]:

    if not path.exists():

        return {
            "path": str(path),
            "exists": False,
        }

    files = 0
    directories = 0

    try:

        for item in path.rglob("*"):

            if item.is_file():

                files += 1

            elif item.is_dir():

                directories += 1

    except OSError:

        pass

    return {
        "path": str(path),
        "exists": True,
        "files": files,
        "directories": directories,
    }


# ============================================================
# ENVIRONMENT
# ============================================================

def environment_info() -> Dict[str, Any]:

    names = [
        "MAVI_STABLE_AUDIO_3_DIR",
        "MAVI_STABLE_AUDIO_CLI",
        "MAVI_WORKER_PYTHON",
        "MAVI_WORKER_SCRIPT",
        "MAVI_STABLE_AUDIO_DEVICE",
        "MAVI_GENERATION_REAL_ONLY",
        "MAVI_ALLOW_FAKE_AUDIO",
        "MAVI_ALLOW_PROCEDURAL_AUDIO",
        "MAVI_ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO",
    ]

    result: Dict[str, Any] = {}

    for name in names:

        value = __import__(
            "os"
        ).environ.get(
            name
        )

        result[name] = value or ""

    return result


# ============================================================
# BUILD
# ============================================================

def build_manifest() -> Dict[str, Any]:

    config_file = (
        ROOT / "config.py"
    )

    app_file = (
        ROOT / "app.py"
    )

    directories = [
        ROOT / "core",
        ROOT / "ai",
        ROOT / "audio",
        ROOT / "audio" / "source",
        ROOT / "audio" / "stems",
        ROOT / "audio" / "mix",
        ROOT / "audio" / "master",
        ROOT / "output",
        ROOT / "output" / "final",
        ROOT / "logs",
        ROOT / "build",
        ROOT / "dist",
    ]

    return {
        "manifest_version": "0.1",

        "created_at": (
            datetime.now().isoformat(
                timespec="seconds"
            )
        ),

        "project_root": str(
            ROOT
        ),

        "python": {
            "executable": sys.executable,
            "version": sys.version,
        },

        "important_files": [
            file_info(
                relative
            )
            for relative in IMPORTANT_FILES
        ],

        "directories": [
            directory_info(
                path
            )
            for path in directories
        ],

        "environment": (
            environment_info()
        ),

        "policy": {
            "real_generation_required": True,
            "fake_audio_allowed": False,
            "procedural_audio_allowed": False,
            "placeholder_audio_allowed": False,
        },

        "backup_note": (
            "Bu manifest dosyaların kendisini yedeklemez; "
            "mevcut proje yapısının ve SHA-256 değerlerinin "
            "kaydını tutar."
        ),

        "config_present": (
            config_file.exists()
        ),

        "app_present": (
            app_file.exists()
        ),
    }


# ============================================================
# SAVE
# ============================================================

def save_manifest(
    payload: Dict[str, Any],
) -> Path:

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    MANIFEST.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return MANIFEST


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    payload = build_manifest()

    path = save_manifest(
        payload
    )

    existing = sum(
        1
        for item
        in payload["important_files"]
        if item["exists"]
    )

    total = len(
        payload["important_files"]
    )

    print()
    print(
        "============================================================"
    )
    print(
        "MAVI AI STUDIO"
    )
    print(
        "BACKUP MANIFEST"
    )
    print(
        "============================================================"
    )
    print()
    print(
        f"FILES : {existing}/{total}"
    )
    print(
        f"MANIFEST : {path}"
    )
    print()
    print(
        "Bu manifest proje dosyalarının kendisini değil, "
        "mevcut yapısını ve hash kayıtlarını yedekler."
    )
    print(
        "============================================================"
    )
    print()

    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )