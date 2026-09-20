# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
CENTRAL PATHS
v0.1
============================================================

Prod. By Ufuk Akdoğan

MAVI AI Studio içindeki tüm önemli dosya ve klasör yollarını
tek merkezden yönetir.

Amaç:
- path tekrarlarını azaltmak
- Windows yollarını güvenli yönetmek
- source / stems / mix / master / output ayrımını net tutmak
- pipeline'ın aynı klasörleri kullanmasını sağlamak

Bu dosya audio üretmez.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional

import config


# ============================================================
# ROOT
# ============================================================

BASE_DIR = Path(
    config.BASE_DIR
).resolve()

AUDIO_DIR = Path(
    config.AUDIO_DIR
).resolve()

SOURCE_DIR = Path(
    config.SOURCE_DIR
).resolve()

STEMS_DIR = Path(
    config.STEMS_DIR
).resolve()

MIX_DIR = Path(
    config.MIX_DIR
).resolve()

MASTER_DIR = Path(
    config.MASTER_DIR
).resolve()

OUTPUT_DIR = Path(
    config.OUTPUT_DIR
).resolve()

FINAL_OUTPUT_DIR = (
    OUTPUT_DIR
    / "final"
)

TEMP_OUTPUT_DIR = (
    OUTPUT_DIR
    / "temp"
)

ANALYSIS_DIR = (
    OUTPUT_DIR
    / "analysis"
)

RENEWAL_DIR = (
    OUTPUT_DIR
    / "renewal"
)

REQUEST_DIR = (
    OUTPUT_DIR
    / "requests"
)

RESULT_DIR = (
    OUTPUT_DIR
    / "results"
)

LOG_DIR = Path(
    config.LOG_DIR
).resolve()

BUILD_DIR = Path(
    config.BUILD_DIR
).resolve()

DIST_DIR = Path(
    config.DIST_DIR
).resolve()


# ============================================================
# SUPPORTED EXTENSIONS
# ============================================================

SUPPORTED_AUDIO_EXTENSIONS = tuple(
    getattr(
        config,
        "SUPPORTED_AUDIO_EXTENSIONS",
        (
            ".wav",
            ".mp3",
            ".flac",
            ".ogg",
            ".m4a",
            ".aac",
            ".wma",
        ),
    )
)


# ============================================================
# ERRORS
# ============================================================

class MaviPathsError(Exception):
    """MAVI path yönetimi temel hatası."""


class MaviPathValidationError(
    MaviPathsError
):
    """Geçersiz path."""


# ============================================================
# PATH MANAGER
# ============================================================

class MaviPaths:

    def __init__(
        self,
        base_dir: Optional[
            Path
        ] = None,
    ) -> None:

        self.base_dir = (
            Path(
                base_dir
                or BASE_DIR
            )
            .expanduser()
            .resolve()
        )

    # --------------------------------------------------------
    # DIRECTORY MAP
    # --------------------------------------------------------

    def directories(
        self,
    ) -> Dict[str, Path]:

        return {
            "base": self.base_dir,
            "audio": self.base_dir / "audio",
            "source": self.base_dir
            / "audio"
            / "source",
            "stems": self.base_dir
            / "audio"
            / "stems",
            "mix": self.base_dir
            / "audio"
            / "mix",
            "master": self.base_dir
            / "audio"
            / "master",
            "output": self.base_dir
            / "output",
            "final": self.base_dir
            / "output"
            / "final",
            "temp": self.base_dir
            / "output"
            / "temp",
            "analysis": self.base_dir
            / "output"
            / "analysis",
            "renewal": self.base_dir
            / "output"
            / "renewal",
            "requests": self.base_dir
            / "output"
            / "requests",
            "results": self.base_dir
            / "output"
            / "results",
            "logs": self.base_dir
            / "logs",
            "build": self.base_dir
            / "build",
            "dist": self.base_dir
            / "dist",
            "assets": self.base_dir
            / "assets",
        }

    # --------------------------------------------------------
    # ENSURE
    # --------------------------------------------------------

    def ensure_directories(
        self,
    ) -> Dict[str, Path]:

        directories = (
            self.directories()
        )

        for path in directories.values():

            path.mkdir(
                parents=True,
                exist_ok=True,
            )

        return directories

    # --------------------------------------------------------
    # SOURCE
    # --------------------------------------------------------

    def source_path(
        self,
        filename: str,
    ) -> Path:

        return self._build_file(
            SOURCE_DIR,
            filename,
        )

    # --------------------------------------------------------
    # STEM
    # --------------------------------------------------------

    def stem_path(
        self,
        filename: str,
    ) -> Path:

        return self._build_file(
            STEMS_DIR,
            filename,
        )

    # --------------------------------------------------------
    # MIX
    # --------------------------------------------------------

    def mix_path(
        self,
        filename: str,
    ) -> Path:

        return self._build_file(
            MIX_DIR,
            filename,
        )

    # --------------------------------------------------------
    # MASTER
    # --------------------------------------------------------

    def master_path(
        self,
        filename: str,
    ) -> Path:

        return self._build_file(
            MASTER_DIR,
            filename,
        )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    def final_path(
        self,
        filename: str,
    ) -> Path:

        return self._build_file(
            FINAL_OUTPUT_DIR,
            filename,
        )

    # --------------------------------------------------------
    # ANALYSIS
    # --------------------------------------------------------

    def analysis_path(
        self,
        filename: str,
    ) -> Path:

        return self._build_file(
            ANALYSIS_DIR,
            filename,
        )

    # --------------------------------------------------------
    # RENEWAL
    # --------------------------------------------------------

    def renewal_path(
        self,
        filename: str,
    ) -> Path:

        return self._build_file(
            RENEWAL_DIR,
            filename,
        )

    # --------------------------------------------------------
    # REQUEST
    # --------------------------------------------------------

    def request_path(
        self,
        filename: str,
    ) -> Path:

        return self._build_file(
            REQUEST_DIR,
            filename,
        )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    def result_path(
        self,
        filename: str,
    ) -> Path:

        return self._build_file(
            RESULT_DIR,
            filename,
        )

    # --------------------------------------------------------
    # LOG
    # --------------------------------------------------------

    def log_path(
        self,
        filename: str,
    ) -> Path:

        return self._build_file(
            LOG_DIR,
            filename,
        )

    # --------------------------------------------------------
    # BUILD FILE
    # --------------------------------------------------------

    @staticmethod
    def _build_file(
        directory: Path,
        filename: str,
    ) -> Path:

        name = str(
            filename
            or ""
        ).strip()

        if not name:

            raise MaviPathValidationError(
                "Dosya adı boş olamaz."
            )

        # Kullanıcının yanlışlıkla mutlak path geçmesi
        # merkez path sistemini bozmamalı.
        candidate = Path(
            name
        )

        if candidate.is_absolute():

            raise MaviPathValidationError(
                (
                    "Mutlak path yerine yalnızca "
                    f"dosya adı bekleniyor: {name}"
                )
            )

        if (
            candidate.name
            != name
            or ".." in candidate.parts
        ):

            raise MaviPathValidationError(
                (
                    "Güvensiz dosya adı: "
                    f"{name}"
                )
            )

        return (
            directory
            / candidate
        ).resolve()


# ============================================================
# FILE DISCOVERY
# ============================================================

def list_audio_files(
    directory: str | Path,
    recursive: bool = False,
) -> List[Path]:

    root = (
        Path(
            directory
        )
        .expanduser()
        .resolve()
    )

    if not root.exists():
        return []

    if not root.is_dir():
        return []

    pattern = (
        "**/*"
        if recursive
        else "*"
    )

    files: List[Path] = []

    for path in root.glob(
        pattern
    ):

        if not path.is_file():
            continue

        if (
            path.suffix.lower()
            not in SUPPORTED_AUDIO_EXTENSIONS
        ):
            continue

        files.append(
            path.resolve()
        )

    files.sort(
        key=lambda item: item.name.lower()
    )

    return files


def find_audio_file(
    filename: str,
    directories: Optional[
        Iterable[
            str | Path
        ]
    ] = None,
) -> Optional[Path]:

    target_name = str(
        filename
        or ""
    ).strip().lower()

    if not target_name:
        return None

    search_dirs = list(
        directories
        if directories is not None
        else [
            SOURCE_DIR,
            OUTPUT_DIR,
            FINAL_OUTPUT_DIR,
            MIX_DIR,
            MASTER_DIR,
            STEMS_DIR,
        ]
    )

    for directory in search_dirs:

        root = (
            Path(
                directory
            )
            .expanduser()
            .resolve()
        )

        if not root.exists():
            continue

        if not root.is_dir():
            continue

        direct = (
            root
            / filename
        )

        if (
            direct.exists()
            and direct.is_file()
        ):

            return direct.resolve()

        try:

            matches = list(
                root.rglob(
                    filename
                )
            )

        except OSError:

            matches = []

        for match in matches:

            if (
                match.is_file()
                and match.name.lower()
                == target_name
            ):

                return match.resolve()

    return None


# ============================================================
# SOURCE SELECTION
# ============================================================

def first_source_audio() -> Optional[Path]:

    files = list_audio_files(
        SOURCE_DIR,
        recursive=False,
    )

    if not files:
        return None

    return files[0]


# ============================================================
# NAME HELPERS
# ============================================================

def safe_stem(
    filename: str | Path,
) -> str:

    path = Path(
        filename
    )

    return path.stem.strip()


def build_analysis_filename(
    source: str | Path,
) -> str:

    return (
        safe_stem(
            source
        )
        + getattr(
            config,
            "ANALYSIS_SUFFIX",
            "_analysis.json",
        )
    )


def build_renewal_filename(
    source: str | Path,
) -> str:

    return (
        safe_stem(
            source
        )
        + getattr(
            config,
            "RENEWAL_SUFFIX",
            "_renewal.json",
        )
    )


def build_mix_filename(
    source: str | Path,
) -> str:

    return (
        safe_stem(
            source
        )
        + getattr(
            config,
            "MIX_SUFFIX",
            "_mavi_mix.wav",
        )
    )


def build_master_filename(
    source: str | Path,
) -> str:

    return (
        safe_stem(
            source
        )
        + getattr(
            config,
            "MASTER_SUFFIX",
            "_MAVI_MASTER.wav",
        )
    )


def build_report_filename(
    source: str | Path,
) -> str:

    return (
        safe_stem(
            source
        )
        + getattr(
            config,
            "REPORT_SUFFIX",
            "_mix_report.txt",
        )
    )


# ============================================================
# PIPELINE PATHS
# ============================================================

def pipeline_paths(
    source: str | Path,
) -> Dict[str, Path]:

    source_path = (
        Path(
            source
        )
        .expanduser()
        .resolve()
    )

    analysis = (
        ANALYSIS_DIR
        / build_analysis_filename(
            source_path
        )
    )

    renewal = (
        RENEWAL_DIR
        / build_renewal_filename(
            source_path
        )
    )

    mix = (
        MIX_DIR
        / build_mix_filename(
            source_path
        )
    )

    master = (
        MASTER_DIR
        / build_master_filename(
            source_path
        )
    )

    report = (
        RESULT_DIR
        / build_report_filename(
            source_path
        )
    )

    final = (
        FINAL_OUTPUT_DIR
        / build_master_filename(
            source_path
        )
    )

    return {
        "source": source_path,
        "analysis": analysis,
        "renewal": renewal,
        "mix": mix,
        "master": master,
        "report": report,
        "final": final,
    }


# ============================================================
# DIRECTORY STATUS
# ============================================================

def paths_status() -> Dict[str, Any]:

    manager = MaviPaths()

    directories = (
        manager.ensure_directories()
    )

    payload: Dict[str, Any] = {}

    for name, path in directories.items():

        payload[name] = {
            "path": str(path),
            "exists": path.exists(),
            "is_directory": path.is_dir(),
        }

    payload[
        "source_audio_count"
    ] = len(
        list_audio_files(
            SOURCE_DIR
        )
    )

    payload[
        "final_audio_count"
    ] = len(
        list_audio_files(
            FINAL_OUTPUT_DIR
        )
    )

    return payload


# ============================================================
# PUBLIC HELPERS
# ============================================================

def ensure_mavi_paths() -> Dict[str, Path]:

    return MaviPaths().ensure_directories()


def get_source_path(
    filename: str,
) -> Path:

    return MaviPaths().source_path(
        filename
    )


def get_final_path(
    filename: str,
) -> Path:

    return MaviPaths().final_path(
        filename
    )


# ============================================================
# CLI
# ============================================================

def main() -> int:

    payload = paths_status()

    print()
    print(
        "============================================================"
    )
    print(
        "MAVI AI STUDIO"
    )
    print(
        "CENTRAL PATH STATUS"
    )
    print(
        "============================================================"
    )
    print()

    for name, info in payload.items():

        if name in {
            "source_audio_count",
            "final_audio_count",
        }:

            continue

        state = (
            "[ OK ]"
            if (
                info["exists"]
                and info["is_directory"]
            )
            else "[FAIL]"
        )

        print(
            f"{state} {name.upper():10} "
            f"{info['path']}"
        )

    print()
    print(
        f"SOURCE AUDIO COUNT : "
        f"{payload['source_audio_count']}"
    )

    print(
        f"FINAL AUDIO COUNT  : "
        f"{payload['final_audio_count']}"
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