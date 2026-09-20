# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
BUILD SYSTEM
v0.1
============================================================

Prod. By Ufuk Akdoğan

Yeni MAVI AI Studio'nun:
- klasör yapısını hazırlayan
- preflight çalıştıran
- PyInstaller build komutunu oluşturan
- build/dist çıktısını yöneten
- son build durumunu raporlayan

merkezi build yardımcı programı.

Bu dosya audio üretmez.
"""

from __future__ import annotations

import shutil
import subprocess
import sys

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import config


# ============================================================
# ERRORS
# ============================================================

class BuildError(Exception):
    """Build sistemi temel hatası."""


class BuildPreflightError(BuildError):
    """Preflight başarısız."""


class BuildToolError(BuildError):
    """Build aracı bulunamadı veya çalışmadı."""


# ============================================================
# DATA
# ============================================================

@dataclass
class BuildResult:

    success: bool

    executable_path: str = ""

    build_directory: str = ""

    dist_directory: str = ""

    command: List[str] = None  # type: ignore[assignment]

    stdout: str = ""

    stderr: str = ""

    elapsed_seconds: float = 0.0

    warnings: List[str] = None  # type: ignore[assignment]

    metadata: Dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:

        if self.command is None:
            self.command = []

        if self.warnings is None:
            self.warnings = []

        if self.metadata is None:
            self.metadata = {}

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(self)


# ============================================================
# BUILD PATHS
# ============================================================

class BuildPaths:

    def __init__(
        self,
    ) -> None:

        self.base = Path(
            config.BASE_DIR
        ).resolve()

        self.build = Path(
            config.BUILD_DIR
        ).resolve()

        self.dist = Path(
            config.DIST_DIR
        ).resolve()

        self.spec = (
            self.base
            / "mavi_ai_studio.spec"
        )

        self.build.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.dist.mkdir(
            parents=True,
            exist_ok=True,
        )

    @property
    def exe_name(
        self,
    ) -> str:

        return (
            str(
                getattr(
                    config,
                    "APP_NAME",
                    "MAVI AI STUDIO",
                )
            )
            .replace(
                " ",
                "_",
            )
        )

    @property
    def executable(
        self,
    ) -> Path:

        suffix = (
            ".exe"
            if sys.platform.startswith(
                "win"
            )
            else ""
        )

        return (
            self.dist
            / (
                self.exe_name
                + suffix
            )
        )


# ============================================================
# FILE CHECKER
# ============================================================

class BuildFileChecker:

    REQUIRED_FILES = [
        "config.py",
        "app.py",

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

        "ai/brain.py",
        "ai/engine.py",
        "ai/runtime.py",

        "preflight.py",
    ]

    def __init__(
        self,
        base_dir: Optional[
            Path
        ] = None,
    ) -> None:

        self.base_dir = (
            base_dir
            or Path(
                config.BASE_DIR
            ).resolve()
        )

    def check(
        self,
    ) -> List[str]:

        missing: List[str] = []

        for relative in self.REQUIRED_FILES:

            target = (
                self.base_dir
                / relative
            )

            if not target.exists():
                missing.append(
                    relative
                )

        return missing


# ============================================================
# PYINSTALLER RESOLVER
# ============================================================

class PyInstallerResolver:

    def resolve(
        self,
    ) -> Optional[str]:

        direct = shutil.which(
            "pyinstaller"
        )

        if direct:
            return direct

        python_executable = (
            sys.executable
        )

        try:

            result = subprocess.run(
                [
                    python_executable,
                    "-m",
                    "PyInstaller",
                    "--version",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

        except OSError:
            return None

        if result.returncode == 0:
            return python_executable

        return None

    def command_prefix(
        self,
    ) -> List[str]:

        direct = shutil.which(
            "pyinstaller"
        )

        if direct:
            return [
                direct
            ]

        if self.resolve() == sys.executable:

            return [
                sys.executable,
                "-m",
                "PyInstaller",
            ]

        raise BuildToolError(
            (
                "PyInstaller bulunamadı. "
                "Build için PyInstaller kurulmalı."
            )
        )


# ============================================================
# DIRECTORY PREPARATION
# ============================================================

class BuildPreparer:

    def prepare(
        self,
    ) -> BuildPaths:

        paths = BuildPaths()

        directories = [
            config.AI_DIR,
            config.CORE_DIR,
            config.ASSETS_DIR,
            config.AUDIO_DIR,
            config.OUTPUT_DIR,
            config.LOG_DIR,
            config.BUILD_DIR,
            config.DIST_DIR,
            config.SOURCE_DIR,
            config.STEMS_DIR,
            config.MIX_DIR,
            config.MASTER_DIR,
        ]

        for directory in directories:

            Path(
                directory
            ).mkdir(
                parents=True,
                exist_ok=True,
            )

        return paths


# ============================================================
# PRE-FLIGHT RUNNER
# ============================================================

class PreflightRunner:

    def run(
        self,
    ) -> Dict[str, Any]:

        command = [
            sys.executable,
            str(
                Path(
                    config.BASE_DIR
                )
                / "preflight.py"
            ),
        ]

        try:

            result = subprocess.run(
                command,
                cwd=str(
                    config.BASE_DIR
                ),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

        except OSError as exc:

            raise BuildPreflightError(
                (
                    f"preflight.py çalıştırılamadı: "
                    f"{exc}"
                )
            ) from exc

        if result.returncode != 0:

            raise BuildPreflightError(
                (
                    "PRE-FLIGHT FAILED.\n\n"
                    + (
                        result.stdout
                        or ""
                    )
                    + "\n"
                    + (
                        result.stderr
                        or ""
                    )
                )
            )

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }


# ============================================================
# SPEC FILE
# ============================================================

class SpecBuilder:

    def __init__(
        self,
        paths: BuildPaths,
    ) -> None:

        self.paths = paths

    def write(
        self,
    ) -> Path:

        app_path = (
            self.paths.base
            / "app.py"
        )

        spec_text = f'''# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_root = Path(
    r"{self.paths.base}"
)


a = Analysis(
    [r"{app_path}"],
    pathex=[
        r"{self.paths.base}"
    ],
    binaries=[],
    datas=[],
    hiddenimports=[
        "config",

        "core",
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

        "ai",
        "ai.brain",
        "ai.engine",
        "ai.runtime",
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)


pyz = PYZ(
    a.pure
)


exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="{self.paths.exe_name}",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)
'''

        self.paths.spec.write_text(
            spec_text,
            encoding="utf-8",
        )

        return self.paths.spec


# ============================================================
# BUILD ENGINE
# ============================================================

class BuildEngine:

    def __init__(
        self,
    ) -> None:

        self.paths = BuildPaths()

        self.preparer = (
            BuildPreparer()
        )

        self.file_checker = (
            BuildFileChecker(
                self.paths.base
            )
        )

        self.pyinstaller = (
            PyInstallerResolver()
        )

        self.preflight = (
            PreflightRunner()
        )

        self.spec_builder = (
            SpecBuilder(
                self.paths
            )
        )

    # --------------------------------------------------------
    # CLEAN
    # --------------------------------------------------------

    def clean(
        self,
    ) -> None:

        self.preparer.prepare()

        if self.paths.build.exists():

            for item in self.paths.build.iterdir():

                # spec dosyasını koru.
                if item == self.paths.spec:
                    continue

                if item.is_dir():

                    shutil.rmtree(
                        item,
                        ignore_errors=True,
                    )

                else:

                    try:
                        item.unlink()
                    except OSError:
                        pass

        if self.paths.dist.exists():

            for item in self.paths.dist.iterdir():

                if item.is_dir():

                    shutil.rmtree(
                        item,
                        ignore_errors=True,
                    )

                else:

                    try:
                        item.unlink()
                    except OSError:
                        pass

    # --------------------------------------------------------
    # FILE CHECK
    # --------------------------------------------------------

    def check_files(
        self,
    ) -> None:

        missing = (
            self.file_checker.check()
        )

        if missing:

            raise BuildError(
                (
                    "Build için eksik dosyalar:\n"
                    + "\n".join(
                        f"- {item}"
                        for item in missing
                    )
                )
            )

    # --------------------------------------------------------
    # PREFLIGHT
    # --------------------------------------------------------

    def run_preflight(
        self,
    ) -> Dict[str, Any]:

        self.check_files()

        return self.preflight.run()

    # --------------------------------------------------------
    # COMMAND
    # --------------------------------------------------------

    def build_command(
        self,
    ) -> List[str]:

        prefix = (
            self.pyinstaller.command_prefix()
        )

        return (
            prefix
            + [
                "--clean",
                "--noconfirm",
                "--onefile",
                "--console",

                "--name",
                self.paths.exe_name,

                "--distpath",
                str(
                    self.paths.dist
                ),

                "--workpath",
                str(
                    self.paths.build
                ),

                "--specpath",
                str(
                    self.paths.base
                ),

                str(
                    self.paths.base
                    / "app.py"
                ),
            ]
        )

    # --------------------------------------------------------
    # BUILD
    # --------------------------------------------------------

    def build(
        self,
        clean_first: bool = False,
        run_preflight: bool = True,
    ) -> BuildResult:

        started = time_now()

        self.preparer.prepare()

        if clean_first:
            self.clean()

        self.check_files()

        preflight_data = None

        if run_preflight:

            preflight_data = (
                self.run_preflight()
            )

        command = (
            self.build_command()
        )

        try:

            process = subprocess.run(
                command,
                cwd=str(
                    self.paths.base
                ),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

        except OSError as exc:

            raise BuildToolError(
                (
                    f"PyInstaller çalıştırılamadı: "
                    f"{exc}"
                )
            ) from exc

        elapsed = (
            time_now()
            - started
        )

        executable = (
            self.paths.executable
        )

        if (
            process.returncode != 0
            or not executable.exists()
        ):

            return BuildResult(
                success=False,
                executable_path=(
                    str(executable)
                    if executable.exists()
                    else ""
                ),
                build_directory=(
                    str(self.paths.build)
                ),
                dist_directory=(
                    str(self.paths.dist)
                ),
                command=command,
                stdout=(
                    process.stdout
                    or ""
                ),
                stderr=(
                    process.stderr
                    or ""
                ),
                elapsed_seconds=round(
                    elapsed,
                    3,
                ),
                warnings=[
                    "PyInstaller build başarısız."
                ],
                metadata={
                    "returncode": (
                        process.returncode
                    ),
                    "preflight": (
                        preflight_data
                    ),
                },
            )

        return BuildResult(
            success=True,
            executable_path=str(
                executable
            ),
            build_directory=str(
                self.paths.build
            ),
            dist_directory=str(
                self.paths.dist
            ),
            command=command,
            stdout=(
                process.stdout
                or ""
            ),
            stderr=(
                process.stderr
                or ""
            ),
            elapsed_seconds=round(
                elapsed,
                3,
            ),
            metadata={
                "returncode": (
                    process.returncode
                ),
                "size_bytes": (
                    executable.stat().st_size
                ),
                "preflight": (
                    preflight_data
                ),
            },
        )


# ============================================================
# TIME HELPER
# ============================================================

def time_now() -> float:

    import time

    return time.perf_counter()


# ============================================================
# PUBLIC API
# ============================================================

def prepare_build() -> BuildPaths:

    return BuildPreparer().prepare()


def run_build_preflight() -> Dict[str, Any]:

    return PreflightRunner().run()


def build_mavi_studio(
    clean_first: bool = False,
    run_preflight: bool = True,
) -> BuildResult:

    return BuildEngine().build(
        clean_first=clean_first,
        run_preflight=run_preflight,
    )


def build_status() -> Dict[str, Any]:

    paths = BuildPaths()

    checker = BuildFileChecker(
        paths.base
    )

    executable = (
        paths.executable
    )

    return {
        "app_name": getattr(
            config,
            "APP_NAME",
            "MAVI AI STUDIO",
        ),
        "app_version": getattr(
            config,
            "APP_VERSION",
            "0.1",
        ),
        "base_dir": str(
            paths.base
        ),
        "build_dir": str(
            paths.build
        ),
        "dist_dir": str(
            paths.dist
        ),
        "source_files_ready": (
            len(
                checker.check()
            )
            == 0
        ),
        "missing_files": (
            checker.check()
        ),
        "pyinstaller": bool(
            PyInstallerResolver().resolve()
        ),
        "executable_exists": (
            executable.exists()
        ),
        "executable_path": (
            str(executable)
            if executable.exists()
            else ""
        ),
        "executable_size": (
            executable.stat().st_size
            if executable.exists()
            else 0
        ),
    }


def print_build_result(
    result: BuildResult,
) -> None:

    print(
        ""
    )

    print(
        "============================================================"
    )

    print(
        "MAVI AI STUDIO • BUILD"
    )

    print(
        "============================================================"
    )

    print(
        "STATUS : "
        + (
            "SUCCESS"
            if result.success
            else "FAILED"
        )
    )

    print(
        f"TIME   : {result.elapsed_seconds:.2f}s"
    )

    if result.executable_path:

        print(
            "EXE    : "
            + result.executable_path
        )

    if result.warnings:

        print(
            ""
        )

        print(
            "WARNINGS:"
        )

        for warning in result.warnings:

            print(
                "- "
                + warning
            )

    if result.stderr.strip():

        print(
            ""
        )

        print(
            "STDERR:"
        )

        print(
            result.stderr[-5000:]
        )

    print(
        "============================================================"
    )

    print(
        ""
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    engine = BuildEngine()

    try:

        result = engine.build(
            clean_first=False,
            run_preflight=True,
        )

    except Exception as exc:

        print(
            ""
        )

        print(
            "MAVI BUILD ERROR"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return 1

    print_build_result(
        result
    )

    return (
        0
        if result.success
        else 1
    )


if __name__ == "__main__":

    raise SystemExit(
        main()
    )