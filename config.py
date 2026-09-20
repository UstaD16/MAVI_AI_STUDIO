# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
CONFIGURATION
v0.1
============================================================

Prod. By Ufuk Akdoğan

Merkezi uygulama ayarları.
GUI, analyzer, generation, pipeline ve build sistemi
tarafından ortak kullanılabilir.
"""

from __future__ import annotations

import os
from pathlib import Path


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "MAVI AI STUDIO"
APP_VERSION = "0.1"
APP_AUTHOR = "Ufuk Akdoğan"

APP_TITLE = (
    f"{APP_NAME}  •  REAL MUSIC AI"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent

CORE_DIR = BASE_DIR / "core"
AI_DIR = BASE_DIR / "ai"
ASSETS_DIR = BASE_DIR / "assets"

AUDIO_DIR = BASE_DIR / "audio"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

BUILD_DIR = BASE_DIR / "build"
DIST_DIR = BASE_DIR / "dist"


# ============================================================
# AUDIO DIRECTORIES
# ============================================================

SOURCE_DIR = AUDIO_DIR / "source"
STEMS_DIR = AUDIO_DIR / "stems"
MIX_DIR = AUDIO_DIR / "mix"
MASTER_DIR = AUDIO_DIR / "master"


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

REQUIRED_DIRECTORIES = [
    AUDIO_DIR,
    OUTPUT_DIR,
    LOG_DIR,
    SOURCE_DIR,
    STEMS_DIR,
    MIX_DIR,
    MASTER_DIR,
]


def ensure_directories() -> None:
    """
    Gerekli çalışma klasörlerini oluşturur.
    """

    for directory in REQUIRED_DIRECTORIES:

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )


# ============================================================
# SUPPORTED AUDIO
# ============================================================

SUPPORTED_AUDIO_EXTENSIONS = (
    ".wav",
    ".mp3",
    ".flac",
    ".ogg",
    ".m4a",
    ".aac",
    ".wma",
)


# ============================================================
# AUDIO DEFAULTS
# ============================================================

DEFAULT_SAMPLE_RATE = 48000

DEFAULT_CHANNELS = 2

DEFAULT_BIT_DEPTH = 24

DEFAULT_AUDIO_FORMAT = "wav"


# ============================================================
# ANALYSIS
# ============================================================

ANALYSIS_SAMPLE_LIMIT = 2_000_000

DEFAULT_ANALYSIS_SEGMENT_SECONDS = 15.0

MIN_BPM = 50.0

MAX_BPM = 220.0


# ============================================================
# RENEWAL
# ============================================================

DEFAULT_RENEWAL_STRENGTH = 0.65

DEFAULT_SOURCE_PRESERVATION = 0.98

DEFAULT_GENERATION_TEMPERATURE = 0.35


# ============================================================
# INSTRUMENTS
# ============================================================

SUPPORTED_INSTRUMENTS = [
    "bass",
    "bass guitar",
    "davul",
    "drum",
    "trumpet",
    "trompet",
    "clarinet",
    "klarnet",
    "b flat clarinet",
    "si bemol klarnet",
    "g clarinet",
    "sol klarnet",
    "zurna",
    "strings",
    "yaylı",
    "yaylılar",
    "folk percussion",
    "ritim",
]


# ============================================================
# MIX
# ============================================================

DEFAULT_SOURCE_GAIN_DB = 0.0

DEFAULT_STEM_GAIN_DB = -3.0

DEFAULT_MASTER_TARGET_LUFS = -14.0

DEFAULT_MASTER_TRUE_PEAK = -1.0

DEFAULT_MASTER_LRA = 7.0


# ============================================================
# FILE NAMES
# ============================================================

MIX_SUFFIX = "_mavi_mix.wav"

MASTER_SUFFIX = "_MAVI_MASTER.wav"

ANALYSIS_SUFFIX = "_analysis.json"

RENEWAL_SUFFIX = "_renewal.json"

REPORT_SUFFIX = "_mix_report.txt"


# ============================================================
# PROVIDER
# ============================================================

PROVIDER_NAME = os.getenv(
    "MAVI_PROVIDER",
    "unavailable",
)

PROVIDER_API_KEY = os.getenv(
    "MAVI_API_KEY",
    "",
)

PROVIDER_ENDPOINT = os.getenv(
    "MAVI_PROVIDER_ENDPOINT",
    "",
)


def provider_configured() -> bool:
    """
    Gerçek bir provider yapılandırılmış mı?
    """

    return bool(
        PROVIDER_API_KEY
        and PROVIDER_ENDPOINT
        and PROVIDER_NAME
        and PROVIDER_NAME.lower()
        != "unavailable"
    )


# ============================================================
# FFMPEG
# ============================================================

FFMPEG_ENV = os.getenv(
    "MAVI_FFMPEG",
    "",
)

FFPROBE_ENV = os.getenv(
    "MAVI_FFPROBE",
    "",
)


def get_ffmpeg_override() -> str:
    return FFMPEG_ENV.strip()


def get_ffprobe_override() -> str:
    return FFPROBE_ENV.strip()


# ============================================================
# GUI
# ============================================================

WINDOW_WIDTH = 1150

WINDOW_HEIGHT = 650

WINDOW_MIN_WIDTH = 1000

WINDOW_MIN_HEIGHT = 550


# ============================================================
# UI COLORS
# ============================================================

UI_BG = "#080D12"

UI_PANEL = "#0B1116"

UI_CARD = "#111A21"

UI_CARD_ALT = "#0D151C"

UI_CARD_INNER = "#16232B"

UI_CYAN = "#00D9FF"

UI_GREEN = "#35E6C5"

UI_YELLOW = "#FFC857"

UI_RED = "#FF5C6C"

UI_TEXT = "#EAF7FF"

UI_TEXT_MUTED = "#7F9AA8"

UI_BORDER = "#263B47"

UI_BORDER_ACTIVE = "#245365"


# ============================================================
# FONT
# ============================================================

UI_FONT = "Segoe UI"

UI_MONO_FONT = "Consolas"


# ============================================================
# CHAT
# ============================================================

CHAT_PLACEHOLDER = (
    "Mavi'ye bir şey söyle..."
)

CHAT_READY_TEXT = (
    "● ONLINE • READY"
)


# ============================================================
# SYSTEM
# ============================================================

SYSTEM_REFRESH_MS = 1000

PROGRESS_REFRESH_MS = 100


# ============================================================
# LOGGING
# ============================================================

LOG_FILE = LOG_DIR / "mavi_ai_studio.log"

MAX_LOG_LINES = 500


# ============================================================
# QUALITY GATE
# ============================================================

MIN_ANALYSIS_QUALITY = 0.25

MIN_GENERATION_QUALITY = 0.25

REQUIRE_REAL_GENERATION = True

ALLOW_FAKE_AUDIO = False

ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO = False


# ============================================================
# PIPELINE
# ============================================================

PIPELINE_STAGES = (
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
)


# ============================================================
# APPLICATION STATE
# ============================================================

DEFAULT_STATUS = "READY"

DEFAULT_ENGINE_STATUS = (
    "REAL AUDIO ENGINE"
)

DEFAULT_MEMORY_COUNT = 0


# ============================================================
# INITIALIZATION
# ============================================================

ensure_directories()
