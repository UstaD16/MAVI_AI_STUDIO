# -*- coding: utf-8 -*-
"""
MAVI AI STUDIO
ULTIMATE WORKSTATION APP
v7.0

Ana uygulama katmanı.
Mevcut core / ai / audio mimarisini tek bir gerçek çalışma alanında birleştirir.
Sahte üretim yapmaz: generation backend yoksa RENEW reddedilir.
"""
from __future__ import annotations

import json
import os
import sys
import time
import threading
import traceback
import ctypes
import wave
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
try:
    import config
    APP_NAME = config.APP_NAME
    APP_VERSION = config.APP_VERSION
    WINDOW_WIDTH = config.WINDOW_WIDTH
    WINDOW_HEIGHT = config.WINDOW_HEIGHT
    WINDOW_MIN_WIDTH = config.WINDOW_MIN_WIDTH
    WINDOW_MIN_HEIGHT = config.WINDOW_MIN_HEIGHT
    OUTPUT_PATH = Path(config.OUTPUT_DIR)
    DEFAULT_RENEWAL_STYLE = "Kaynak karakteri"
    DEFAULT_RENEWAL_REGION = ""
    DEFAULT_RENEWAL_INSTRUMENTS = ["davul", "zurna", "bass guitar", "sol klarnet"]
    RENEWAL_QUALITY_THRESHOLD = float(getattr(config, "MIN_GENERATION_QUALITY", 0.25))
    RENEWAL_MAX_ATTEMPTS = 1
except Exception:
    APP_NAME = "MAVI AI STUDIO"
    APP_VERSION = "0.1"
    WINDOW_WIDTH, WINDOW_HEIGHT = 1150, 650
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT = 1000, 550
    OUTPUT_PATH = BASE_DIR / "output"
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    DEFAULT_RENEWAL_STYLE = "Kaynak karakteri"
    DEFAULT_RENEWAL_REGION = ""
    DEFAULT_RENEWAL_INSTRUMENTS = ["davul", "zurna", "bass guitar", "sol klarnet"]
    RENEWAL_QUALITY_THRESHOLD = 0.25
    RENEWAL_MAX_ATTEMPTS = 1

# -----------------------------------------------------------------------------
# OPTIONAL DEPENDENCIES
# -----------------------------------------------------------------------------
try:
    import numpy as np
except Exception:
    np = None

try:
    import psutil
except Exception:
    psutil = None

try:
    import pygame
    try:
        pygame.mixer.init()
        PYGAME_AVAILABLE = True
    except Exception:
        PYGAME_AVAILABLE = False
except Exception:
    pygame = None
    PYGAME_AVAILABLE = False

# -----------------------------------------------------------------------------
# OPTIONAL PROJECT MODULES
# -----------------------------------------------------------------------------

def optional_imports() -> dict[str, Any]:
    modules: dict[str, Any] = {}
    try:
        from audio.analyzer import analyze_audio
        modules["analyze_audio"] = analyze_audio
    except Exception:
        modules["analyze_audio"] = None
    try:
        from audio.converter import convert_to_wav
        modules["convert_to_wav"] = convert_to_wav
    except Exception:
        modules["convert_to_wav"] = None
    try:
        from ai.renewal_command import parse_renewal_command, renewal_command_from_dict
        modules["parse_renewal_command"] = parse_renewal_command
        modules["renewal_command_from_dict"] = renewal_command_from_dict
    except Exception:
        modules["parse_renewal_command"] = None
        modules["renewal_command_from_dict"] = None
    try:
        from core.production_service import get_production_service
        modules["get_production_service"] = get_production_service
    except Exception:
        modules["get_production_service"] = None
    try:
        from core.production_factory import get_production_factory
        modules["get_production_factory"] = get_production_factory
    except Exception:
        modules["get_production_factory"] = None
    try:
        from ai.renewal_engine import RenewalEngine
        modules["RenewalEngine"] = RenewalEngine
    except Exception:
        modules["RenewalEngine"] = None
    try:
        from ai.assistant import assistant
        modules["assistant"] = assistant
    except Exception:
        modules["assistant"] = None
    try:
        import ai.brain as brain
        modules["brain"] = brain
    except Exception:
        modules["brain"] = None
    try:
        from ai.music_dna import build_music_dna
        modules["build_music_dna"] = build_music_dna
    except Exception:
        modules["build_music_dna"] = None
    return modules

BACKENDS = optional_imports()

# -----------------------------------------------------------------------------
# REAL MAVI PIPELINE
# -----------------------------------------------------------------------------
from pipeline_controller import (
    PipelineControllerEvent,
    pipeline_controller,
    stop_pipeline,
)
from ai.brain import (
    brain,
    parse_producer_command,
    producer_intent_to_dict,
)
from ai.runtime import RuntimeEventType


# -----------------------------------------------------------------------------
# THEME
# -----------------------------------------------------------------------------
BG_MAIN = "#080D12"
BG_PANEL = "#0B1116"
BG_CARD = "#111A21"
BG_INNER = "#0D151C"
BG_ACTIVE = "#14232C"
BORDER = "#263B47"
BORDER_ACTIVE = "#245365"
CYAN = "#00D9FF"
CYAN_SOFT = "#7EE8FF"
GREEN = "#35E6C5"
YELLOW = "#FFC857"
RED = "#FF5577"
WHITE = "#F2F5F7"
TEXT_DIM = "#93A4B7"
TEXT_MUTED = "#657684"
FONT = "Segoe UI"
MONO = "Consolas"

# -----------------------------------------------------------------------------
# STATE
# -----------------------------------------------------------------------------
loaded_file_path: Optional[str] = None
loaded_track_name = ""
loaded_audio = None
loaded_sample_rate = 44100
loaded_analysis: dict[str, Any] = {}

current_music_dna = None
current_renewal_command = None
current_renewal_plan = None
current_renewal_result = None
current_output_wav: Optional[str] = None

playlist: list[str] = []
playlist_index = -1
player_backend: Optional[str] = None
playing_state = False
is_paused = False
playback_started_at = 0.0

renewal_running = False
application_closing = False

# -----------------------------------------------------------------------------
# ROOT
# -----------------------------------------------------------------------------
root = tk.Tk()
root.title(f"{APP_NAME}  •  {APP_VERSION}")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
root.configure(bg=BG_MAIN)

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
def ui(fn, *args, **kwargs):
    if application_closing:
        return
    try:
        root.after(0, lambda: fn(*args, **kwargs))
    except Exception:
        pass


def stamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def text(value: Any, fallback: str = "—") -> str:
    if value is None or value == "":
        return fallback
    return str(value)


def fmt_time(value: Any) -> str:
    try:
        seconds = max(0, int(float(value)))
    except Exception:
        seconds = 0
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def log(message: str, level: str = "INFO") -> None:
    line = f"[{stamp()}] {level:<5} {message}"
    print(line)
    try:
        log_box.configure(state="normal")
        log_box.insert("end", line + "\n")
        log_box.see("end")
        log_box.configure(state="disabled")
    except Exception:
        pass


def chat(sender: str, message: str) -> None:
    try:
        mavi_chat_box.configure(state="normal")
        tag = "mavi" if sender == "MAVI" else "user"
        mavi_chat_box.insert("end", f"{sender}\n", tag)
        mavi_chat_box.insert("end", f"{message}\n\n")
        mavi_chat_box.see("end")
        mavi_chat_box.configure(state="disabled")
    except Exception:
        pass


def report(message: str) -> None:
    try:
        ai_report_box.configure(state="normal")
        ai_report_box.delete("1.0", "end")
        ai_report_box.insert("end", message)
        ai_report_box.configure(state="disabled")
    except Exception:
        pass

# -----------------------------------------------------------------------------
# UI FACTORY
# -----------------------------------------------------------------------------
def card(parent: tk.Widget, title: str, height: Optional[int] = None):
    frame = tk.Frame(parent, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER)
    if height:
        frame.configure(height=height)
        frame.pack_propagate(False)
    header = tk.Frame(frame, bg=BG_CARD, height=33)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text=title, bg=BG_CARD, fg=CYAN_SOFT,
             font=(FONT, 9, "bold")).pack(side="left", padx=11, pady=8)
    tk.Frame(frame, bg=BORDER_ACTIVE, height=1).pack(fill="x")
    body = tk.Frame(frame, bg=BG_CARD)
    body.pack(fill="both", expand=True)
    return frame, body

# -----------------------------------------------------------------------------
# TOP BAR
# -----------------------------------------------------------------------------
top = tk.Frame(root, bg=BG_PANEL, height=62, highlightthickness=1, highlightbackground=BORDER)
top.pack(fill="x")
top.pack_propagate(False)

logo = tk.Frame(top, bg=BG_PANEL)
logo.pack(side="left", padx=17)
tk.Label(logo, text="MAVI", bg=BG_PANEL, fg=CYAN,
         font=(FONT, 20, "bold")).pack(side="left")
tk.Label(logo, text=" AI STUDIO", bg=BG_PANEL, fg=WHITE,
         font=(FONT, 15, "bold")).pack(side="left")
tk.Label(logo, text="  /  PERSONAL AI MUSIC WORKSTATION", bg=BG_PANEL,
         fg=TEXT_MUTED, font=(MONO, 7)).pack(side="left", padx=8)

hud = tk.Frame(top, bg=BG_PANEL)
hud.pack(side="right", padx=16)
hud_online = tk.Label(hud, text="● ONLINE", bg=BG_PANEL, fg=GREEN,
                      font=(MONO, 8, "bold"))
hud_online.pack(side="left", padx=9)
hud_engine = tk.Label(hud, text="ENGINE: BOOT", bg=BG_PANEL, fg=TEXT_DIM,
                      font=(MONO, 7, "bold"))
hud_engine.pack(side="left", padx=9)
hud_system = tk.Label(hud, text="SYSTEM", bg=BG_PANEL, fg=TEXT_DIM,
                      font=(MONO, 7, "bold"))
hud_system.pack(side="left", padx=9)

# -----------------------------------------------------------------------------
# WORKSPACE
# -----------------------------------------------------------------------------
workspace = tk.Frame(root, bg=BG_MAIN)
workspace.pack(fill="both", expand=True, padx=8, pady=(8, 0))
workspace.grid_columnconfigure(0, minsize=300, weight=0)
workspace.grid_columnconfigure(1, minsize=550, weight=1)
workspace.grid_columnconfigure(2, minsize=315, weight=0)
workspace.grid_rowconfigure(0, weight=1)

left = tk.Frame(workspace, bg=BG_MAIN)
left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
center = tk.Frame(workspace, bg=BG_MAIN)
center.grid(row=0, column=1, sticky="nsew", padx=5)
right = tk.Frame(workspace, bg=BG_MAIN)
right.grid(row=0, column=2, sticky="nsew", padx=(5, 0))

# -----------------------------------------------------------------------------
# LEFT: PLAYLIST
# -----------------------------------------------------------------------------
playlist_card, playlist_body = card(left, "♫  PROJECT / PLAYLIST", 225)
playlist_card.pack(fill="x", pady=(0, 6))

playlist_tools = tk.Frame(playlist_body, bg=BG_CARD)
playlist_tools.pack(fill="x", padx=8, pady=7)

playlist_list = tk.Listbox(
    playlist_body, bg=BG_INNER, fg=WHITE, selectbackground="#16485A",
    selectforeground=WHITE, activestyle="none", relief="flat", bd=0,
    font=(FONT, 8)
)
playlist_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))


def refresh_playlist():
    playlist_list.delete(0, "end")
    for i, path in enumerate(playlist):
        marker = "▶ " if i == playlist_index else "   "
        playlist_list.insert("end", marker + Path(path).stem[:34])


def add_audio_files():
    paths = filedialog.askopenfilenames(
        title="Müzik Dosyaları",
        filetypes=[("Audio", "*.wav *.mp3 *.flac *.ogg *.m4a *.aac"), ("All", "*.*")]
    )
    for path in paths:
        if path not in playlist:
            playlist.append(path)
    refresh_playlist()
    if paths:
        load_track(paths[0])


def clear_playlist():
    playlist.clear()
    refresh_playlist()


def select_playlist(index: int):
    global playlist_index
    if not playlist:
        playlist_index = -1
        return
    playlist_index = max(0, min(index, len(playlist) - 1))
    refresh_playlist()
    playlist_list.selection_clear(0, "end")
    playlist_list.selection_set(playlist_index)
    playlist_list.see(playlist_index)


def on_playlist_double_click(event=None):
    sel = playlist_list.curselection()
    if sel:
        select_playlist(sel[0])
        load_track(playlist[playlist_index])


tk.Button(playlist_tools, text="+ ADD", command=add_audio_files,
          bg=BG_INNER, fg=CYAN_SOFT, activebackground=BG_ACTIVE,
          relief="flat", bd=0, font=(MONO, 7, "bold"), padx=10).pack(side="left")
tk.Button(playlist_tools, text="CLEAR", command=clear_playlist,
          bg=BG_INNER, fg=TEXT_DIM, activebackground=BG_ACTIVE,
          relief="flat", bd=0, font=(MONO, 7, "bold"), padx=10).pack(side="right")
playlist_list.bind("<Double-Button-1>", on_playlist_double_click)

# -----------------------------------------------------------------------------
# LEFT: CHAT
# -----------------------------------------------------------------------------
chat_card, chat_body = card(left, "🧠  MAVI / AI PRODUCER", 290)
chat_card.pack(fill="both", expand=True, pady=(0, 6))

mavi_chat_box = scrolledtext.ScrolledText(
    chat_body, bg=BG_INNER, fg=WHITE, insertbackground=WHITE,
    relief="flat", bd=0, wrap="word", font=(FONT, 8)
)
mavi_chat_box.pack(fill="both", expand=True, padx=8, pady=8)
mavi_chat_box.tag_config("mavi", foreground=CYAN_SOFT, font=(FONT, 8, "bold"))
mavi_chat_box.tag_config("user", foreground=GREEN, font=(FONT, 8, "bold"))
mavi_chat_box.configure(state="disabled")

chat_input = tk.Frame(chat_body, bg=BG_CARD)
chat_input.pack(fill="x", padx=8, pady=(0, 8))
chat_entry = tk.Entry(chat_input, bg=BG_INNER, fg=WHITE, insertbackground=WHITE,
                      relief="flat", bd=0, font=(FONT, 9))
chat_entry.pack(side="left", fill="x", expand=True, ipady=7, padx=(6, 4))

# -----------------------------------------------------------------------------
# CENTER: NOW PLAYING
# -----------------------------------------------------------------------------
now_card, now_body = card(center, "NOW PLAYING", 78)
now_card.pack(fill="x", pady=(0, 6))
current_track_label = tk.Label(now_body, text="No track loaded", bg=BG_CARD, fg=WHITE,
                               font=(FONT, 14, "bold"), anchor="w")
current_track_label.pack(side="left", padx=13, pady=10)
current_file_label = tk.Label(now_body, text="Select a source track", bg=BG_CARD, fg=TEXT_DIM,
                              font=(MONO, 7), anchor="w")
current_file_label.pack(side="left", padx=4, pady=10)
session_status_label = tk.Label(now_body, text="● ONLINE • READY", bg=BG_CARD, fg=GREEN,
                               font=(MONO, 7, "bold"))
session_status_label.pack(side="right", padx=14)

# -----------------------------------------------------------------------------
# CENTER: WAVEFORM
# -----------------------------------------------------------------------------
wave_card, wave_body = card(center, "〰  AUDIO / MUSIC DNA", 300)
wave_card.pack(fill="x", pady=(0, 6))
wave_canvas = tk.Canvas(wave_body, bg=BG_INNER, highlightthickness=0, bd=0)
wave_canvas.pack(fill="both", expand=True, padx=8, pady=8)
wave_data: list[float] = []


def draw_waveform(audio):
    global wave_data
    wave_canvas.delete("all")
    if audio is None:
        wave_canvas.create_text(300, 100, text="SOURCE AUDIO BEKLENİYOR",
                                fill=TEXT_MUTED, font=(MONO, 9))
        return
    try:
        if np is not None:
            arr = np.asarray(audio)
            if arr.ndim > 1:
                arr = np.mean(arr, axis=1)
            arr = arr.astype(float)
            if len(arr) > 4000:
                arr = arr[np.linspace(0, len(arr) - 1, 1600).astype(int)]
            peak = float(np.max(np.abs(arr))) if len(arr) else 1.0
            if peak > 0:
                arr = arr / peak
            wave_data = arr.tolist()
        else:
            wave_data = list(audio)
    except Exception:
        wave_data = []
    if not wave_data:
        return
    width = max(1, wave_canvas.winfo_width())
    height = max(1, wave_canvas.winfo_height())
    mid = height / 2
    step = max(1, len(wave_data) // max(100, width))
    pts = []
    for i in range(0, len(wave_data), step):
        x = (i / max(1, len(wave_data) - 1)) * width
        y = mid - float(wave_data[i]) * height * 0.40
        pts.extend((x, y))
    if len(pts) >= 4:
        wave_canvas.create_line(*pts, fill=CYAN, width=1, smooth=True)
    wave_canvas.create_line(0, mid, width, mid, fill="#18333F", width=1)

wave_canvas.bind("<Configure>", lambda e: draw_waveform(loaded_audio))

# -----------------------------------------------------------------------------
# CENTER: METRICS
# -----------------------------------------------------------------------------
metrics_card, metrics_body = card(center, "MUSIC DNA / ANALYSIS", 106)
metrics_card.pack(fill="x", pady=(0, 6))
metric_vars = {k: tk.StringVar(value="—") for k in
               ["BPM", "KEY", "MAKAM", "GENRE", "REGION", "ENERGY", "TIME", "INSTRUMENTS"]}
metric_frame = tk.Frame(metrics_body, bg=BG_CARD)
metric_frame.pack(fill="both", expand=True, padx=8, pady=7)
for i, key in enumerate(metric_vars):
    cell = tk.Frame(metric_frame, bg=BG_INNER)
    cell.grid(row=0, column=i, sticky="nsew", padx=2)
    tk.Label(cell, text=key, bg=BG_INNER, fg=TEXT_MUTED,
             font=(MONO, 6, "bold")).pack(pady=(5, 0))
    tk.Label(cell, textvariable=metric_vars[key], bg=BG_INNER, fg=WHITE,
             font=(MONO, 7, "bold"), wraplength=70).pack(pady=(2, 5))
    metric_frame.grid_columnconfigure(i, weight=1)

# -----------------------------------------------------------------------------
# CENTER: PRODUCTION
# -----------------------------------------------------------------------------
production_card, production_body = card(center, "♻  RENEW / PRODUCTION", 116)
production_card.pack(fill="x")
prod = tk.Frame(production_body, bg=BG_CARD)
prod.pack(fill="both", expand=True, padx=10, pady=8)
style_var = tk.StringVar(value=DEFAULT_RENEWAL_STYLE)
region_var = tk.StringVar(value=DEFAULT_RENEWAL_REGION)
strength_var = tk.IntVar(value=100)

for col in range(6):
    prod.grid_columnconfigure(col, weight=1 if col == 5 else 0)
tk.Label(prod, text="STYLE", bg=BG_CARD, fg=TEXT_MUTED, font=(MONO, 7, "bold")).grid(row=0, column=0, padx=3)
tk.Entry(prod, textvariable=style_var, bg=BG_INNER, fg=WHITE,
         insertbackground=WHITE, relief="flat", width=12).grid(row=0, column=1, padx=3)
tk.Label(prod, text="REGION", bg=BG_CARD, fg=TEXT_MUTED, font=(MONO, 7, "bold")).grid(row=0, column=2, padx=3)
tk.Entry(prod, textvariable=region_var, bg=BG_INNER, fg=WHITE,
         insertbackground=WHITE, relief="flat", width=12).grid(row=0, column=3, padx=3)
tk.Label(prod, text="STRENGTH", bg=BG_CARD, fg=TEXT_MUTED, font=(MONO, 7, "bold")).grid(row=0, column=4, padx=3)
tk.Scale(prod, from_=0, to=100, variable=strength_var, orient="horizontal",
         bg=BG_CARD, fg=WHITE, troughcolor=BG_INNER, highlightthickness=0,
         showvalue=True, width=10).grid(row=0, column=5, sticky="ew", padx=3)
renew_button = tk.Button(prod, text="♻  RENEW SOURCE",
                         command=lambda: start_renewal(), bg="#123744", fg=GREEN,
                         activebackground="#16485A", activeforeground=WHITE,
                         relief="flat", bd=0, font=(FONT, 9, "bold"), pady=6)
renew_button.grid(row=1, column=0, columnspan=6, sticky="ew", pady=(10, 0))

# -----------------------------------------------------------------------------
# RIGHT: CONTROL CENTER
# -----------------------------------------------------------------------------
cc_header = tk.Frame(right, bg=BG_CARD, height=42, highlightthickness=1, highlightbackground=BORDER)
cc_header.pack(fill="x", pady=(0, 6))
cc_header.pack_propagate(False)
tk.Label(cc_header, text="MAVI AI CONTROL CENTER", bg=BG_CARD, fg=CYAN,
         font=(FONT, 9, "bold")).pack(side="left", padx=12, pady=12)

master_card, master_body = card(right, "🧠 MASTER AI STATUS", 90)
master_card.pack(fill="x", pady=(0, 6))
master_status = tk.Label(master_body, text="● ONLINE / STANDBY", bg=BG_CARD, fg=GREEN,
                        font=(MONO, 9, "bold"), anchor="w")
master_status.pack(fill="x", padx=12, pady=(9, 1))
master_detail = tk.Label(master_body, text="DECISION • RENEW • MIX • MASTER",
                         bg=BG_CARD, fg=TEXT_DIM, font=(MONO, 6), anchor="w")
master_detail.pack(fill="x", padx=12)

engine_card, engine_body = card(right, "⚙  AI ENGINE", 108)
engine_card.pack(fill="x", pady=(0, 6))
engine_status = tk.Label(engine_body, text="Booting...", bg=BG_CARD, fg=TEXT_DIM,
                        font=(MONO, 7), justify="left", anchor="w")
engine_status.pack(fill="both", expand=True, padx=12, pady=8)

system_card, system_body = card(right, "▣  SYSTEM", 82)
system_card.pack(fill="x", pady=(0, 6))
system_status = tk.Label(system_body, text="CPU —   RAM —", bg=BG_CARD, fg=TEXT_DIM,
                         font=(MONO, 7), justify="left", anchor="w")
system_status.pack(fill="both", expand=True, padx=12, pady=8)

report_card, report_body = card(right, "📋  AI MIX REPORT", 145)
report_card.pack(fill="x", pady=(0, 6))
ai_report_box = scrolledtext.ScrolledText(report_body, bg=BG_INNER, fg=WHITE,
                                         relief="flat", bd=0, wrap="word", font=(MONO, 7))
ai_report_box.pack(fill="both", expand=True, padx=8, pady=8)
ai_report_box.configure(state="disabled")

memory_card, memory_body = card(right, "🧠 MEMORY", 92)
memory_card.pack(fill="x", pady=(0, 6))
memory_label = tk.Label(memory_body,
                        text="Memory: Active\nExperience: Active\nDecision history: Ready",
                        bg=BG_CARD, fg=TEXT_DIM, font=(MONO, 7), justify="left", anchor="w")
memory_label.pack(fill="both", expand=True, padx=12, pady=8)

log_card, log_body = card(right, "▤ LOG", 145)
log_card.pack(fill="both", expand=True)
log_box = scrolledtext.ScrolledText(log_body, bg=BG_INNER, fg=GREEN,
                                    relief="flat", bd=0, wrap="word", font=(MONO, 6))
log_box.pack(fill="both", expand=True, padx=8, pady=8)
log_box.configure(state="disabled")

# -----------------------------------------------------------------------------
# BOTTOM TRANSPORT
# -----------------------------------------------------------------------------
transport = tk.Frame(root, bg=BG_PANEL, height=74,
                     highlightthickness=1, highlightbackground=BORDER)
transport.pack(fill="x", padx=8, pady=(8, 0))
transport.pack_propagate(False)
transport_left = tk.Frame(transport, bg=BG_PANEL)
transport_left.pack(side="left", fill="y", padx=9)

progress_var = tk.DoubleVar(value=0)
transport_state = tk.Label(transport, text="READY", bg=BG_PANEL, fg=TEXT_DIM,
                          font=(MONO, 6, "bold"))

def transport_btn(label, command, primary=False):
    return tk.Button(transport_left, text=label, command=command,
                     bg="#123744" if primary else BG_INNER,
                     fg=CYAN if primary else WHITE,
                     activebackground="#16485A", activeforeground=WHITE,
                     relief="flat", bd=0, font=(FONT, 9, "bold"),
                     width=8 if primary else 6, pady=7)

# Commands are defined later; buttons bind through lambdas.
transport_btn("▶ PLAY", lambda: toggle_playback(), True).pack(side="left", padx=3, pady=14)
transport_btn("⏸ PAUSE", lambda: pause_audio()).pack(side="left", padx=3, pady=14)
transport_btn("■ STOP", lambda: stop_audio()).pack(side="left", padx=3, pady=14)
transport_btn("◀ PREV", lambda: previous_track()).pack(side="left", padx=3, pady=14)
transport_btn("NEXT ▶", lambda: next_track()).pack(side="left", padx=3, pady=14)

transport_center = tk.Frame(transport, bg=BG_PANEL)
transport_center.pack(side="left", fill="both", expand=True)
progress = ttk.Progressbar(transport_center, variable=progress_var, maximum=100)
progress.pack(fill="x", padx=20, pady=(25, 2))
transport_state.pack(in_=transport_center)

transport_right = tk.Frame(transport, bg=BG_PANEL)
transport_right.pack(side="right", padx=15)
volume_var = tk.DoubleVar(value=80)
tk.Label(transport_right, text="VOL", bg=BG_PANEL, fg=TEXT_MUTED,
         font=(MONO, 6, "bold")).pack(side="left", padx=4)
tk.Scale(transport_right, from_=0, to=100, variable=volume_var, orient="horizontal",
         bg=BG_PANEL, fg=WHITE, troughcolor=BG_INNER, highlightthickness=0,
         showvalue=False, width=8, length=100, command=lambda v: set_volume(float(v))).pack(side="left")

signature = tk.Label(root,
                     text="PROD. BY UFUK AKDOĞAN  /  HALK OYUNLARI EĞİTMENİ ÖZEL SÜRÜMÜ",
                     bg=BG_MAIN, fg="#4D6675", font=(MONO, 6, "italic"))
signature.place(relx=0.995, rely=0.995, anchor="se")

# -----------------------------------------------------------------------------
# MCI PLAYER
# -----------------------------------------------------------------------------
MCI_ALIAS = "MAVI_PLAYER"

def mci(command: str):
    try:
        buf = ctypes.create_unicode_buffer(512)
        code = ctypes.windll.winmm.mciSendStringW(command, buf, 512, 0)
        return code, buf.value
    except Exception:
        return -1, ""


def mci_close():
    mci(f"close {MCI_ALIAS}")


def mci_open(path: str) -> bool:
    mci_close()
    return mci(f'open "{os.path.abspath(path)}" alias {MCI_ALIAS}')[0] == 0


def mci_play(): return mci(f"play {MCI_ALIAS}")[0] == 0

def mci_pause(): return mci(f"pause {MCI_ALIAS}")[0] == 0

def mci_resume(): return mci(f"resume {MCI_ALIAS}")[0] == 0

def mci_stop(): return mci(f"stop {MCI_ALIAS}")[0] == 0

def mci_position():
    code, value = mci(f"status {MCI_ALIAS} position")
    try:
        return float(value) / 1000 if code == 0 else 0.0
    except Exception:
        return 0.0


def mci_length():
    code, value = mci(f"status {MCI_ALIAS} length")
    try:
        return float(value) / 1000 if code == 0 else 0.0
    except Exception:
        return 0.0


def set_volume(value: float):
    value = max(0, min(100, float(value)))
    if PYGAME_AVAILABLE:
        try:
            pygame.mixer.music.set_volume(value / 100.0)
        except Exception:
            pass


def open_player(path: str) -> Optional[str]:
    if PYGAME_AVAILABLE:
        try:
            pygame.mixer.music.load(path)
            set_volume(volume_var.get())
            return "pygame"
        except Exception as exc:
            log(f"Pygame yükleme başarısız: {exc}", "WARN")
    if os.name == "nt" and mci_open(path):
        return "mci"
    return None

# -----------------------------------------------------------------------------
# AUDIO CONTROL
# -----------------------------------------------------------------------------
def play_loaded():
    global playing_state, is_paused, playback_started_at
    if not loaded_file_path or not player_backend:
        return False
    ok = False
    if player_backend == "pygame":
        try:
            pygame.mixer.music.play()
            ok = True
        except Exception:
            ok = False
    elif player_backend == "mci":
        ok = mci_play()
    if ok:
        playing_state = True
        is_paused = False
        playback_started_at = time.time()
        transport_state.config(text="PLAYING", fg=GREEN)
    return ok


def pause_audio():
    global is_paused
    if not playing_state:
        return
    ok = False
    if player_backend == "pygame":
        try:
            pygame.mixer.music.pause(); ok = True
        except Exception: pass
    elif player_backend == "mci":
        ok = mci_pause()
    if ok:
        is_paused = True
        transport_state.config(text="PAUSED", fg=YELLOW)


def stop_audio():
    global playing_state, is_paused
    if player_backend == "pygame":
        try: pygame.mixer.music.stop()
        except Exception: pass
    elif player_backend == "mci":
        mci_stop()
    playing_state = False
    is_paused = False
    progress_var.set(0)
    transport_state.config(text="STOPPED", fg=TEXT_DIM)


def toggle_playback():
    global is_paused
    if not loaded_file_path:
        if playlist:
            load_track(playlist[0])
        else:
            add_audio_files()
        if not loaded_file_path:
            return
    if is_paused:
        if player_backend == "pygame":
            try: pygame.mixer.music.unpause()
            except Exception: pass
        elif player_backend == "mci":
            mci_resume()
        is_paused = False
        transport_state.config(text="PLAYING", fg=GREEN)
        return
    if playing_state:
        pause_audio()
        return
    play_loaded()

# -----------------------------------------------------------------------------
# ANALYSIS
# -----------------------------------------------------------------------------
def normalize_analysis(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return dict(result)
    if isinstance(result, tuple):
        keys = ["audio", "sample_rate", "bpm", "key", "genre", "instruments",
                "duration", "channels", "peak", "rms", "dynamic_range",
                "spectral_centroid", "zero_crossing", "energy"]
        return {k: result[i] for i, k in enumerate(keys) if i < len(result)}
    return {}


def wav_fallback(path: str):
    if not np or not path.lower().endswith(".wav"):
        return None
    try:
        with wave.open(path, "rb") as wf:
            channels = wf.getnchannels(); sr = wf.getframerate()
            width = wf.getsampwidth(); raw = wf.readframes(wf.getnframes())
        if width == 2:
            arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        elif width == 4:
            arr = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
        else:
            arr = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128) / 128.0
        if channels > 1:
            arr = arr.reshape(-1, channels)
        return {"audio": arr, "sample_rate": sr, "channels": channels,
                "duration": len(arr) / sr if sr else 0}
    except Exception as exc:
        log(f"WAV fallback hata: {exc}", "WARN")
        return None


def analyze_source(path: str):
    fn = BACKENDS.get("analyze_audio")
    if fn:
        try:
            result = fn(path)
            data = normalize_analysis(result)
            if data:
                return data
        except Exception as exc:
            log(f"Analyzer hata: {exc}", "WARN")
    return wav_fallback(path)


def update_metrics(data: dict[str, Any]):
    metric_vars["BPM"].set(text(data.get("bpm")))
    metric_vars["KEY"].set(text(data.get("key")))
    metric_vars["MAKAM"].set(text(data.get("makam", data.get("karar"))))
    metric_vars["GENRE"].set(text(data.get("genre")))
    metric_vars["REGION"].set(text(data.get("region")))
    metric_vars["ENERGY"].set(text(data.get("energy")))
    metric_vars["TIME"].set(fmt_time(data.get("duration", 0)))
    inst = data.get("instruments", [])
    if isinstance(inst, (list, tuple)):
        value = ", ".join(map(str, inst[:3])) + ("..." if len(inst) > 3 else "")
    else:
        value = text(inst)
    metric_vars["INSTRUMENTS"].set(value)


def analyze_loaded_source():
    if not loaded_file_path:
        chat("MAVI", "Önce bir kaynak müzik yükle.")
        return
    def worker():
        global loaded_audio, loaded_sample_rate, loaded_analysis, current_music_dna
        ui(set_session, "● ANALYZING", YELLOW)
        transport_state.config(text="ANALYZING", fg=YELLOW)
        data = analyze_source(loaded_file_path)
        if not data:
            ui(report, "ANALYSIS FAILED\n\nAnalyzer bağlantısı yok veya dosya okunamadı.")
            ui(chat, "MAVI", "Kaynağı analiz edemedim.")
            ui(set_session, "● ONLINE • ERROR", RED)
            return
        loaded_analysis = data
        loaded_audio = data.get("audio")
        loaded_sample_rate = int(data.get("sample_rate") or data.get("sr") or 44100)
        try:
            builder = BACKENDS.get("build_music_dna")
            current_music_dna = builder(data) if builder else data
        except Exception as exc:
            log(f"Music DNA hata: {exc}", "WARN")
            current_music_dna = data
        ui(draw_waveform, loaded_audio)
        ui(update_metrics, data)
        ui(report, "MAVI AI SOURCE ANALYSIS\n────────────────────────\n" +
            "\n".join([
                f"BPM        : {text(data.get('bpm'))}",
                f"KEY        : {text(data.get('key'))}",
                f"MAKAM      : {text(data.get('makam', data.get('karar')))}",
                f"GENRE      : {text(data.get('genre'))}",
                f"REGION     : {text(data.get('region'))}",
                f"DURATION   : {fmt_time(data.get('duration', 0))}",
                f"ENERGY     : {text(data.get('energy'))}",
                f"INSTRUMENTS: {text(data.get('instruments'))}",
            ]))
        ui(set_session, "● ONLINE • SOURCE READY", GREEN)
        ui(transport_state.config, text="SOURCE READY", fg=GREEN)
        log("Source analysis tamamlandı.")
        ui(chat, "MAVI", f"Kaynağı analiz ettim. BPM {text(data.get('bpm'))}, ton {text(data.get('key'))}. RENEW hazır.")
    threading.Thread(target=worker, daemon=True).start()

# -----------------------------------------------------------------------------
# TRACKS
# -----------------------------------------------------------------------------
def load_track(path: str):
    global loaded_file_path, loaded_track_name, current_output_wav, player_backend
    if not path or not os.path.exists(path):
        log(f"Dosya bulunamadı: {path}", "ERROR")
        return
    stop_audio()
    loaded_file_path = os.path.abspath(path)
    loaded_track_name = Path(path).name
    current_output_wav = None
    current_track_label.config(text=Path(path).stem[:42])
    current_file_label.config(text=loaded_file_path)
    player_backend = open_player(loaded_file_path)
    if path in playlist:
        select_playlist(playlist.index(path))
    log(f"Track loaded: {loaded_track_name}")
    analyze_loaded_source()


def previous_track():
    if not playlist: return
    idx = playlist_index - 1 if playlist_index > 0 else len(playlist) - 1
    load_track(playlist[idx])


def next_track():
    if not playlist: return
    idx = playlist_index + 1
    if idx >= len(playlist): idx = 0
    load_track(playlist[idx])

# -----------------------------------------------------------------------------
# COMMAND / REAL PRODUCTION
# -----------------------------------------------------------------------------
def parse_command(raw: str):
    return parse_producer_command(raw)


def production_status():
    try:
        return pipeline_controller.status()
    except Exception as exc:
        log(f"Pipeline status hata: {exc}", "WARN")
        return {}


def build_ui_renew_command():
    style = style_var.get().strip()
    region = region_var.get().strip()
    strength = max(0, min(100, int(strength_var.get())))
    instruments = list(DEFAULT_RENEWAL_INSTRUMENTS)
    pieces = ["kaynak müziği koru"]
    if style and style.lower() not in {"kaynak karakteri", "kaynak karakteri"}:
        pieces.append(f"{style} karakterinde yenile")
    if region:
        pieces.append(f"{region} karakterini koru")
    pieces.append("toparla")
    pieces.append("doğal yap")
    pieces.append("".join([" ", "ve ".join(instruments), " ekle"]))
    pieces.append(f"yenileme gücü {strength}")
    return ", ".join(piece.strip() for piece in pieces if piece.strip())


def _controller_callback(event: PipelineControllerEvent):
    global current_renewal_result, current_output_wav, current_renewal_plan
    try:
        event_type = str(event.event_type or "")
        progress = max(0.0, min(1.0, float(event.progress or 0.0)))
        stage = str(event.stage or "PIPELINE")
        state = str(event.state or "")
        message = str(event.message or "")

        if event_type == RuntimeEventType.STARTED:
            ui(set_session, "● RENEWING", YELLOW)
            ui(master_status.config, text="● RENEW / PROCESSING", fg=YELLOW)
            ui(transport_state.config, text=stage, fg=YELLOW)
            ui(report, f"MAVI AI PRODUCTION\n────────────────────────\nSTAGE      : {stage}\nSTATUS     : RUNNING\nPROGRESS   : {progress * 100:.0f}%\n\n{message}")
            return

        ui(set_session, f"● {stage} • {progress * 100:.0f}%", YELLOW)
        ui(transport_state.config, text=stage, fg=YELLOW)
        if message:
            ui(master_detail.config, text=message[:80])

        if event_type == RuntimeEventType.PROGRESS:
            return

        if event_type == RuntimeEventType.RESULT:
            result = event.result
            current_renewal_result = result
            if result is not None:
                current_renewal_plan = getattr(result, "renewal_plan", None)
                output = getattr(result, "final_path", "") or getattr(result, "generated_path", "")
                if output and os.path.exists(output):
                    current_output_wav = output
                    ui(load_track, output)
                ui(report, _format_pipeline_report(result))
            ui(set_session, "● ONLINE • RENEW ACCEPTED", GREEN)
            ui(master_status.config, text="● ONLINE / READY", fg=GREEN)
            ui(transport_state.config, text="READY", fg=GREEN)
            ui(chat, "MAVI", "RENEW tamamlandı. Gerçek generation, kalite ve final pipeline başarıyla geçti.")
            return

        if event_type == RuntimeEventType.ERROR:
            current_renewal_result = None
            ui(set_session, "● ONLINE • RENEW FAILED", RED)
            ui(master_status.config, text="● ONLINE / RENEW FAILED", fg=RED)
            ui(transport_state.config, text="FAILED", fg=RED)
            ui(report, f"MAVI AI PRODUCTION REJECTED\n────────────────────────\n{message}\n\nFake/procedural/placeholder audio oluşturulmadı.")
            ui(chat, "MAVI", f"Production reddedildi: {message}")
            return

        if event_type == RuntimeEventType.STOPPED:
            ui(set_session, "● ONLINE • STOPPED", TEXT_DIM)
            ui(master_status.config, text="● ONLINE / STOPPED", fg=YELLOW)
            ui(transport_state.config, text="STOPPED", fg=YELLOW)
            ui(chat, "MAVI", "Production durduruldu.")
            return

        if event_type == RuntimeEventType.FINISHED and state in {"COMPLETE", "IDLE"}:
            ui(transport_state.config, text="READY", fg=TEXT_DIM)

    except Exception as exc:
        log(f"Controller callback hata: {exc}", "WARN")


def _format_pipeline_report(result: Any) -> str:
    data = result.as_dict() if hasattr(result, "as_dict") else {}
    intent = data.get("intent") or {}
    metadata = data.get("metadata") or {}
    instruments = intent.get("instruments") or metadata.get("instruments") or []
    actions = intent.get("instrument_actions") or metadata.get("instrument_actions") or {}
    final_path = data.get("final_path") or ""
    return (
        "MAVI AI PRODUCTION REPORT\n"
        "────────────────────────\n"
        f"STATUS      : ACCEPTED\n"
        f"SOURCE      : {Path(data.get('source_path', '')).name}\n"
        f"OUTPUT      : {Path(final_path).name if final_path else '—'}\n"
        f"GENERATION  : REAL BACKEND\n"
        f"INSTRUMENTS : {', '.join(map(str, instruments)) if instruments else '—'}\n"
        f"ACTIONS     : {actions or '—'}\n"
        f"REGION      : {intent.get('regional_request') or metadata.get('regional_request') or '—'}\n"
        f"DANCE       : {intent.get('dance_family') or metadata.get('dance_family') or '—'}\n"
        f"ELAPSED     : {data.get('elapsed_seconds', 0)} sec\n"
        "\nKaynak melodisi, ritim ve tonal kimlik korunacak şekilde işlendi."
    )


def _wait_for_pipeline_result(job):
    global renewal_running
    global current_renewal_result
    global current_output_wav
    global current_renewal_plan

    try:
        job_result = pipeline_controller.wait(timeout=1800)

        if job_result is None:
            raise RuntimeError(
                "Pipeline sonucu alınamadı."
            )

        # ------------------------------------------------------------
        # PipelineController -> PipelineJob
        # Gerçek AI sonucu -> job.result
        # ------------------------------------------------------------
        current_renewal_result = (
            getattr(job_result, "result", None)
            or getattr(job, "result", None)
        )

        # ------------------------------------------------------------
        # JOB başarısızsa gerçek hatayı göster
        # ------------------------------------------------------------
        job_status = str(
            getattr(job_result, "status", "")
            or ""
        ).upper()

        if job_status in {"FAILED", "STOPPED"}:
            error = (
                getattr(job_result, "error", "")
                or getattr(job_result, "message", "")
                or "Pipeline başarısız."
            )

            log(
                f"Pipeline sonucu: {job_status} - {error}",
                "ERROR",
            )

            chat(
                "MAVI",
                f"Üretim tamamlanamadı: {error}",
            )

            return

        # ------------------------------------------------------------
        # GERÇEK PipelineResult
        # ------------------------------------------------------------
        result = current_renewal_result

        if result is None:
            raise RuntimeError(
                "PipelineJob tamamlandı fakat PipelineResult bulunamadı."
            )

        success = bool(
            getattr(result, "success", False)
        )

        if not success:
            error = (
                getattr(result, "error", "")
                or getattr(job_result, "error", "")
                or getattr(result, "message", "")
                or "Üretim başarısız."
            )

            log(
                f"Pipeline production failed: {error}",
                "ERROR",
            )

            chat(
                "MAVI",
                f"Üretim başarısız: {error}",
            )

            return

        # ------------------------------------------------------------
        # RENEWAL PLAN
        # ------------------------------------------------------------
        current_renewal_plan = getattr(
            result,
            "renewal_plan",
            None,
        )

        # ------------------------------------------------------------
        # ÇIKTI DOSYASI
        # ------------------------------------------------------------
        output = (
            getattr(result, "final_path", None)
            or getattr(result, "master_path", None)
            or getattr(result, "mixed_path", None)
            or getattr(result, "generated_path", None)
            or getattr(result, "output_path", None)
        )

        if output:
            output = str(output)

        if output and os.path.exists(output):
            current_output_wav = output

            log(
                f"RENEW COMPLETE: {output}",
                "INFO",
            )

            ui(
                load_track,
                output,
            )

            chat(
                "MAVI",
                (
                    "Üretim tamamlandı. "
                    "Kaynak müziğin kimliği korunarak "
                    "yeni düzenleme hazırlandı."
                ),
            )

            return

        # ------------------------------------------------------------
        # Başarılı PipelineResult ama dosya bulunamadı
        # ------------------------------------------------------------
        log(
            "Pipeline başarılı fakat çıktı dosyası bulunamadı.",
            "ERROR",
        )

        chat(
            "MAVI",
            "Üretim tamamlandı ancak çıktı dosyası bulunamadı.",
        )

    except Exception as exc:
        log(
            f"Pipeline wait hata: {exc}",
            "ERROR",
        )

        chat(
            "MAVI",
            f"Üretim sonucu alınırken hata oluştu: {exc}",
        )

    finally:
        renewal_running = False

        try:
            ui(
                renew_button.configure,
                state="normal",
            )
        except Exception:
            pass

def start_renewal(command_text: str = ""):
    global renewal_running, current_renewal_command

    if renewal_running or pipeline_controller.busy:
        chat("MAVI", "RENEW zaten çalışıyor.")
        return

    if not loaded_file_path:
        chat("MAVI", "RENEW için önce kaynak müzik yükle.")
        return

    command = command_text.strip() or build_ui_renew_command()
    current_renewal_command = parse_command(command)

    try:
        status = pipeline_controller.status()
        backend = ((status.get("runtime") or {}).get("generation_backend") or
                   status.get("generation_backend") or {})
        if backend and backend.get("ready") is False:
            chat("MAVI", "Gerçek generation backend hazır değil. Üretim başlatılmadı.")
            return

        renewal_running = True
        renew_button.configure(state="disabled")
        master_status.config(text="● RENEW / PROCESSING", fg=YELLOW)
        set_session("● RENEWING", YELLOW)
        transport_state.config(text="BRAIN", fg=YELLOW)

        log(f"MAVI COMMAND: {command}")
        log(f"INTENT: {current_renewal_command.as_dict() if hasattr(current_renewal_command, 'as_dict') else current_renewal_command}")

        job = pipeline_controller.start(
            source_path=loaded_file_path,
            command=command,
            seconds=30.0,
            seed=314159,
            steps=8,
            threads=4,
            cfg=1.0,
            init_noise_level=0.20,
        )

        report(
            "MAVI AI PRODUCTION\n"
            "────────────────────────\n"
            f"JOB        : {job.job_id}\n"
            f"COMMAND    : {command}\n"
            f"INTENT     : {job.intent.get('intent_type') if job.intent else '—'}\n"
            f"INSTRUMENT : {', '.join(job.metadata.get('instruments', [])) or '—'}\n"
            "STATUS     : RUNNING\n"
            "GENERATION : REAL BACKEND"
        )

        threading.Thread(
            target=_wait_for_pipeline_result,
            args=(job,),
            daemon=True,
            name="MAVI-Pipeline-Wait",
        ).start()

    except Exception as exc:
        renewal_running = False
        renew_button.configure(state="normal")
        log(f"RENEW START ERROR: {exc}", "ERROR")
        set_session("● ONLINE • RENEW REJECTED", RED)
        master_status.config(text="● ONLINE / RENEW REJECTED", fg=RED)
        transport_state.config(text="FAILED", fg=RED)
        chat("MAVI", f"RENEW başlatılamadı: {exc}")

# -----------------------------------------------------------------------------
# CHAT
# -----------------------------------------------------------------------------
def assistant_answer(command: str):
    fn = BACKENDS.get("assistant")
    ctx = {"source_file": loaded_file_path, "music_dna": current_music_dna,
           "analysis": loaded_analysis, "renewal_result": current_renewal_result}
    if fn:
        try:
            if callable(fn):
                try: result = fn(command, context=ctx)
                except TypeError: result = fn(command)
            elif hasattr(fn, "respond"):
                result = fn.respond(command, context=ctx)
            elif hasattr(fn, "ask"):
                result = fn.ask(command, context=ctx)
            else:
                result = None
            if result:
                return str(result)
        except Exception as exc:
            log(f"Assistant hata: {exc}", "WARN")
    return "Komutu aldım. İlgili gerçek üretim/işleme motoruna aktarılabilecek durumda."


def process_command(command: str):
    global current_renewal_command
    raw = command.strip()
    if not raw:
        return

    chat("SEN", raw)

    try:
        intent = parse_producer_command(raw)
        current_renewal_command = intent
        intent_type = intent.intent_type
        log(f"CHAT INTENT: {intent_type}")

        if intent_type in {"play"}:
            toggle_playback()
            return
        if intent_type in {"pause"}:
            pause_audio()
            return
        if intent_type in {"stop"}:
            if pipeline_controller.busy:
                stop_pipeline()
            else:
                stop_audio()
            return
        if intent_type == "analyze":
            analyze_loaded_source()
            return
        if intent_type in {"renew", "generate", "mix", "master"}:
            start_renewal(raw)
            return
        if intent_type == "export":
            export_current()
            return
        if intent_type == "help":
            chat("MAVI", intent.response_hint)
            return

        chat("MAVI", intent.response_hint or "Komutu aldım.")

    except Exception as exc:
        log(f"Command parse hata: {exc}", "ERROR")
        chat("MAVI", f"Komutu işleyemedim: {exc}")


def send_chat(event=None):
    raw = chat_entry.get().strip()
    if raw:
        chat_entry.delete(0, "end")
        process_command(raw)
    return "break"

chat_send = tk.Button(chat_input, text="➤", command=send_chat,
                      bg="#123744", fg=CYAN, activebackground="#16485A",
                      activeforeground=WHITE, relief="flat", bd=0,
                      font=(FONT, 11, "bold"), width=3)
chat_send.pack(side="right", padx=2)
chat_entry.bind("<Return>", send_chat)

# -----------------------------------------------------------------------------
# QUICK ACTIONS
# -----------------------------------------------------------------------------
quick_card, quick_body = card(left, "⚡ QUICK ACTIONS", 105)
quick_card.pack(fill="x")
quick = tk.Frame(quick_body, bg=BG_CARD)
quick.pack(fill="both", expand=True, padx=8, pady=8)

def quick_cmd(value: str):
    chat_entry.delete(0, "end"); chat_entry.insert(0, value); send_chat()

tk.Button(quick, text="🔍 ANALYZE", command=analyze_loaded_source,
          bg=BG_INNER, fg=CYAN_SOFT, relief="flat", bd=0,
          font=(MONO, 7, "bold")).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
tk.Button(quick, text="♻ RENEW", command=lambda: quick_cmd("renew"),
          bg=BG_INNER, fg=GREEN, relief="flat", bd=0,
          font=(MONO, 7, "bold")).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
tk.Button(quick, text="💾 EXPORT", command=lambda: export_current(),
          bg=BG_INNER, fg=YELLOW, relief="flat", bd=0,
          font=(MONO, 7, "bold")).grid(row=1, column=0, sticky="ew", padx=2, pady=2)
tk.Button(quick, text="▶ PLAY", command=toggle_playback,
          bg="#123744", fg=CYAN, relief="flat", bd=0,
          font=(MONO, 7, "bold")).grid(row=1, column=1, sticky="ew", padx=2, pady=2)
quick.grid_columnconfigure(0, weight=1); quick.grid_columnconfigure(1, weight=1)

# -----------------------------------------------------------------------------
# EXPORT
# -----------------------------------------------------------------------------
def export_current():
    source = current_output_wav or loaded_file_path
    if not source or not os.path.exists(source):
        messagebox.showwarning(APP_NAME, "Export edilecek gerçek audio yok.")
        return
    target = filedialog.asksaveasfilename(
        title="Export", initialdir=str(OUTPUT_PATH),
        initialfile=Path(source).stem + "_MAVI.wav",
        defaultextension=".wav", filetypes=[("WAV", "*.wav")])
    if not target: return
    try:
        with open(source, "rb") as src, open(target, "wb") as dst:
            dst.write(src.read())
        log(f"Export: {target}")
        chat("MAVI", f"Export tamamlandı: {Path(target).name}")
    except Exception as exc:
        log(f"Export hata: {exc}", "ERROR")
        messagebox.showerror("Export", str(exc))

# -----------------------------------------------------------------------------
# STATUS
# -----------------------------------------------------------------------------
def set_session(value: str, color: str = GREEN):
    session_status_label.config(text=value, fg=color)


def refresh_engine():
    try:
        status = production_status()
        runtime = status.get("runtime") or {}
        backend = status.get("generation_backend") or runtime.get("generation_backend") or {}
        busy = bool(status.get("busy") or runtime.get("running"))
        ready = backend.get("ready")
        lines = [
            f"Pipeline   : {'RUNNING' if busy else 'READY'}",
            f"Generation : {'READY' if ready is not False else 'UNAVAILABLE'}",
            f"Brain      : CONNECTED • MEMORY {len(getattr(brain, 'memory', []))}",
            f"Backend    : {'STABLE AUDIO 3' if ready else 'CHECKING'}",
        ]
        engine_status.config(text="\n".join(lines))
        hud_engine.config(
            text="ENGINE: REAL" if ready is not False else "ENGINE: WAITING",
            fg=GREEN if ready is not False else YELLOW,
        )
    except Exception as exc:
        engine_status.config(text=f"Pipeline : ERROR\n{exc}")
        hud_engine.config(text="ENGINE: ERROR", fg=RED)


def refresh_system():
    if psutil:
        try:
            cpu = psutil.cpu_percent(interval=None); ram = psutil.virtual_memory().percent
            system_status.config(text=f"CPU {cpu:>3.0f}%    RAM {ram:>3.0f}%\nPYTHON {sys.version_info.major}.{sys.version_info.minor}")
            hud_system.config(text=f"CPU {cpu:.0f}% RAM {ram:.0f}%")
            return
        except Exception: pass
    system_status.config(text=f"CPU —    RAM —\nPYTHON {sys.version_info.major}.{sys.version_info.minor}")


def refresh_memory():
    try:
        f = BASE_DIR / "memory.json"
        if f.exists():
            data = json.loads(f.read_text(encoding="utf-8"))
            count = data.get("songs") or data.get("learned_songs") or data.get("count") or "—"
            memory_label.config(text=f"Memory: Active\nLearned songs: {count}\nExperience: Active")
            return
    except Exception: pass
    memory_label.config(text="Memory: Active\nExperience: Active\nDecision history: Ready")


def refresh_playback():
    if not loaded_file_path: return
    duration = 0.0; position = 0.0
    if player_backend == "mci":
        position = mci_position(); duration = mci_length()
    elif player_backend == "pygame":
        if loaded_audio is not None and loaded_sample_rate:
            try: duration = len(loaded_audio) / loaded_sample_rate
            except Exception: duration = 0.0
        if playing_state and not is_paused:
            position = min(duration, max(0.0, time.time() - playback_started_at))
    if duration <= 0 and loaded_audio is not None and loaded_sample_rate:
        try: duration = len(loaded_audio) / loaded_sample_rate
        except Exception: pass
    if duration > 0:
        progress_var.set(min(100, position / duration * 100))
        transport_time = f"{fmt_time(position)} / {fmt_time(duration)}"
        current_file_label.config(text=f"{loaded_file_path}    {transport_time}")
        if playing_state and position >= duration - 0.2:
            stop_audio()


def status_loop():
    if application_closing: return
    refresh_system(); refresh_playback()
    root.after(1000, status_loop)

# -----------------------------------------------------------------------------
# CLOSE / BOOT
# -----------------------------------------------------------------------------
def close_app():
    global application_closing
    application_closing = True
    try: stop_audio()
    except Exception: pass
    try: mci_close()
    except Exception: pass
    try: root.destroy()
    except Exception: pass


pipeline_controller.set_callback(_controller_callback)

def boot():
    chat("MAVI", "Hazırım. Kaynak müziği yükle. Önce dinleyip analiz edeceğim; RENEW yalnızca gerçek generation backend hazırsa çalışacak.")
    report("MAVI AI MIX REPORT READY\n\nKaynak yüklenmesini bekliyor.")
    refresh_engine(); refresh_system(); refresh_memory()
    hud_online.config(text="● ONLINE", fg=GREEN)
    master_status.config(text="● ONLINE / STANDBY", fg=GREEN)
    log("MAVI AI STUDIO initialized.")
    log("Real generation required for RENEW.")

root.protocol("WM_DELETE_WINDOW", close_app)
root.update_idletasks()
root.after(300, boot)
root.after(1000, status_loop)

screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
x = max(0, (screen_w - WINDOW_WIDTH) // 2)
y = max(0, (screen_h - WINDOW_HEIGHT) // 2)
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
root.mainloop()
