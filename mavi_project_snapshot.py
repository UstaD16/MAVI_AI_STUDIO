# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
PROJECT SNAPSHOT
v0.1
============================================================

Prod. By Ufuk Akdoğan

Yeni MAVI AI Studio projesinin gerçek dosya yedeğini ZIP
olarak oluşturur.

Dahil edilir:
- Python kaynak dosyaları
- BAT dosyaları
- requirements dosyaları
- config.py
- core/
- ai/
- assets/
- output içindeki JSON/TXT raporları
- logs içindeki raporlar

Hariç tutulur:
- .venv/
- .worker_venv/
- __pycache__/
- .git/
- büyük binary/model dosyaları
- geçici cache
- audio çıktıları ve kaynak audio dosyaları

Amaç:
Kod mimarisinin hızlı ve taşınabilir bir snapshot'ını almak.

BU DOSYA AUDIO ÜRETMEZ.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import zipfile

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


# ============================================================
# ROOT
# ============================================================

ROOT = (
    Path(__file__)
    .resolve()
    .parent
)

BACKUP_DIR = (
    ROOT
    / "backup"
)

DEFAULT_TIMESTAMP = (
    datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
)

DEFAULT_ZIP = (
    BACKUP_DIR
    / (
        "MAVI_AI_STUDIO_snapshot_"
        + DEFAULT_TIMESTAMP
        + ".zip"
    )
)

DEFAULT_MANIFEST = (
    BACKUP_DIR
    / (
        "MAVI_AI_STUDIO_snapshot_"
        + DEFAULT_TIMESTAMP
        + ".json"
    )
)


# ============================================================
# CONSTANTS
# ============================================================

VERSION = "0.1"

INCLUDE_EXTENSIONS = {
    ".py",
    ".bat",
    ".cmd",
    ".txt",
    ".md",
    ".json",
    ".ini",
    ".toml",
    ".yaml",
    ".yml",
}

INCLUDE_ROOT_FILES = {
    "requirements.txt",
    "requirements-worker.txt",
    "config.py",
    "app.py",
}

EXCLUDED_DIRECTORY_NAMES = {
    ".venv",
    ".worker_venv",
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "cache",
    "caches",
    "models",
    "model",
}

EXCLUDED_FILE_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".flac",
    ".ogg",
    ".m4a",
    ".aac",
    ".wma",
    ".pt",
    ".pth",
    ".ckpt",
    ".safetensors",
    ".tflite",
    ".onnx",
    ".bin",
}

EXCLUDED_OUTPUT_BINARY_NAMES = {
    "real_generation.wav",
    "prepared_generation.wav",
    "shote_mori_renewal.wav",
}


# ============================================================
# ERRORS
# ============================================================

class SnapshotError(Exception):
    """Snapshot temel hatası."""


# ============================================================
# COLLECTOR
# ============================================================

class SnapshotCollector:

    def __init__(
        self,
        root: Path,
    ) -> None:

        self.root = root.resolve()

    # --------------------------------------------------------
    # DIRECTORY EXCLUDED
    # --------------------------------------------------------

    @staticmethod
    def excluded_directory(
        path: Path,
    ) -> bool:

        return any(
            part in EXCLUDED_DIRECTORY_NAMES
            for part in path.parts
        )

    # --------------------------------------------------------
    # FILE INCLUDED
    # --------------------------------------------------------

    def include_file(
        self,
        path: Path,
    ) -> bool:

        if not path.exists():
            return False

        if not path.is_file():
            return False

        if self.excluded_directory(
            path.parent
        ):

            return False

        if path.suffix.lower() in (
            EXCLUDED_FILE_EXTENSIONS
        ):

            return False

        if (
            path.parent.name == "output"
            and path.name
            in EXCLUDED_OUTPUT_BINARY_NAMES
        ):

            return False

        if path.suffix.lower() in (
            INCLUDE_EXTENSIONS
        ):

            return True

        if (
            path.name
            in INCLUDE_ROOT_FILES
        ):

            return True

        return False

    # --------------------------------------------------------
    # COLLECT
    # --------------------------------------------------------

    def collect(
        self,
    ) -> List[Path]:

        collected: List[Path] = []

        for path in self.root.rglob("*"):

            if not self.include_file(
                path
            ):

                continue

            collected.append(
                path
            )

        collected.sort(
            key=lambda item: str(
                item.relative_to(
                    self.root
                )
            ).lower()
        )

        return collected


# ============================================================
# SNAPSHOT
# ============================================================

class ProjectSnapshot:

    def __init__(
        self,
        root: Path,
    ) -> None:

        self.root = (
            root.resolve()
        )

        self.collector = (
            SnapshotCollector(
                self.root
            )
        )

    # --------------------------------------------------------
    # MANIFEST
    # --------------------------------------------------------

    def build_manifest(
        self,
        files: Iterable[Path],
        zip_path: Path,
    ) -> Dict[str, Any]:

        items: List[
            Dict[str, Any]
        ] = []

        total_bytes = 0

        for path in files:

            try:

                relative = path.relative_to(
                    self.root
                )

                size = (
                    path.stat().st_size
                )

            except OSError:

                continue

            except ValueError:

                continue

            total_bytes += size

            items.append(
                {
                    "path": str(
                        relative
                    ),
                    "size_bytes": size,
                }
            )

        return {
            "snapshot_version": VERSION,

            "created_at": (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            ),

            "project_root": str(
                self.root
            ),

            "snapshot_zip": str(
                zip_path
            ),

            "python": {
                "executable": (
                    sys.executable
                ),
                "version": sys.version,
            },

            "environment": {
                "stable_audio_root": os.getenv(
                    "MAVI_STABLE_AUDIO_3_DIR",
                    "",
                ),
                "stable_audio_cli": os.getenv(
                    "MAVI_STABLE_AUDIO_CLI",
                    "",
                ),
                "worker_python": os.getenv(
                    "MAVI_WORKER_PYTHON",
                    "",
                ),
                "worker_script": os.getenv(
                    "MAVI_WORKER_SCRIPT",
                    "",
                ),
            },

            "policy": {
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
                "placeholder_audio": False,
            },

            "files": {
                "count": len(
                    items
                ),
                "total_bytes": total_bytes,
                "items": items,
            },

            "excluded": {
                "virtual_environments": True,
                "models": True,
                "audio_binaries": True,
                "git": True,
                "cache": True,
                "pycache": True,
            },
        }

    # --------------------------------------------------------
    # WRITE ZIP
    # --------------------------------------------------------

    def create_zip(
        self,
        files: Iterable[Path],
        zip_path: Path,
    ) -> int:

        zip_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        count = 0

        with zipfile.ZipFile(
            zip_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=6,
        ) as archive:

            for path in files:

                try:

                    relative = (
                        path.relative_to(
                            self.root
                        )
                    )

                except ValueError:

                    continue

                archive.write(
                    path,
                    arcname=str(
                        relative
                    ),
                )

                count += 1

        return count

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    def create(
        self,
        zip_path: Path,
        manifest_path: Path,
    ) -> Dict[str, Any]:

        files = (
            self.collector.collect()
        )

        if not files:

            raise SnapshotError(
                "Yedeklenecek dosya bulunamadı."
            )

        count = self.create_zip(
            files,
            zip_path,
        )

        manifest = (
            self.build_manifest(
                files,
                zip_path,
            )
        )

        manifest_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        manifest_path.write_text(
            json.dumps(
                manifest,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        manifest[
            "snapshot_manifest"
        ] = str(
            manifest_path
        )

        return manifest


# ============================================================
# CLI
# ============================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Create MAVI AI Studio code snapshot"
        )
    )

    parser.add_argument(
        "--zip",
        default=str(
            DEFAULT_ZIP
        ),
        help="Snapshot ZIP yolu.",
    )

    parser.add_argument(
        "--manifest",
        default=str(
            DEFAULT_MANIFEST
        ),
        help="Snapshot manifest yolu.",
    )

    return parser


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    parser = build_parser()

    args = parser.parse_args()

    zip_path = (
        Path(
            args.zip
        )
        .expanduser()
        .resolve()
    )

    manifest_path = (
        Path(
            args.manifest
        )
        .expanduser()
        .resolve()
    )

    try:

        snapshot = (
            ProjectSnapshot(
                ROOT
            )
        )

        manifest = snapshot.create(
            zip_path=zip_path,
            manifest_path=manifest_path,
        )

    except Exception as exc:

        print()
        print(
            "MAVI PROJECT SNAPSHOT FAILED"
        )
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()

        return 1

    print()
    print(
        "============================================================"
    )
    print(
        "MAVI AI STUDIO"
    )
    print(
        "PROJECT SNAPSHOT"
    )
    print(
        "============================================================"
    )
    print()

    print(
        "STATUS : SUCCESS"
    )

    print(
        f"FILES  : "
        f"{manifest['files']['count']}"
    )

    print(
        f"SIZE   : "
        f"{manifest['files']['total_bytes']} bytes"
    )

    print()

    print(
        "ZIP:"
    )

    print(
        zip_path
    )

    print()

    print(
        "MANIFEST:"
    )

    print(
        manifest_path
    )

    print()
    print(
        "Audio ve model dosyaları özellikle snapshot dışında bırakıldı."
    )

    print(
        "============================================================"
    )
    print()

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )