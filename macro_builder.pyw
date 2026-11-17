#!/usr/bin/env python3
"""
Macro Builder
=====================
Repeatedly presses-and-holds the F key.

Features
--------
* Profiles with a custom NAME, a HOLD duration (ms), and a GAP between
  presses (ms). Create / edit / delete / select them from the main menu.
* An always-on-top, draggable overlay pinned to the top-left that shows the
  active profile name and START / STOP buttons. Its background is RED at 50%
  opacity when idle and GREEN at 50% opacity while it is actively holding F.
* An emergency stop: a big button on the main window, a STOP button on the
  overlay, and a global hotkey (default F9) that works even when another app
  (e.g. a game) has focus.

Requires: Python 3.8+ and pynput  ->  pip install pynput
"""

import json
import base64
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import traceback

PYNPUT_OK = True
try:
    from pynput.keyboard import Controller, Listener, Key, KeyCode
    from pynput.mouse import Button, Controller as MouseController
except ImportError:
    PYNPUT_OK = False

# Embedded app icon (PNG, base64) — replaces the default Tk icon.
ICON_B64 = "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"


def _build_ico_from_png(png):
    """Wrap PNG bytes in a minimal .ico container (Vista+ supports PNG icons)."""
    w = int.from_bytes(png[16:20], "big")    # width / height from the IHDR chunk
    h = int.from_bytes(png[20:24], "big")
    bw = 0 if w >= 256 else w                 # 0 means 256 in the ICO format
    bh = 0 if h >= 256 else h
    header = struct.pack("<HHH", 0, 1, 1)     # reserved, type=icon, count=1
    entry = struct.pack("<BBBBHHII", bw & 0xFF, bh & 0xFF, 0, 0, 1, 32, len(png), 22)
    return header + entry + png


def _external_icon():
    """Return the path of a user-supplied icon next to the app, if any."""
    for name in ("icon.png", "icon.ico", "icon.gif"):
        p = os.path.join(BASE_DIR, name)
        if os.path.exists(p):
            return p
    return None


def set_app_icon(root, path=None):
    """Set the window + taskbar icon. Uses `path` if given and valid, else a
    user 'icon.*' file beside the app, else the built-in icon."""
    src = path if (path and os.path.exists(path)) else _external_icon()
    low = src.lower() if src else ""

    # title-bar / Alt-Tab / most platforms (iconphoto reads PNG/GIF)
    try:
        if low.endswith((".png", ".gif")):
            img = tk.PhotoImage(file=src)
        else:
            img = tk.PhotoImage(data=ICON_B64)
        root.iconphoto(True, img)
        root._app_icon = img
    except Exception:
        try:
            img = tk.PhotoImage(data=ICON_B64)
            root.iconphoto(True, img)
            root._app_icon = img
        except Exception:
            pass

    # Windows taskbar + title bar via an .ico
    if sys.platform.startswith("win"):
        try:
            if low.endswith(".ico"):
                root.iconbitmap(default=src)
            else:
                if low.endswith(".png"):
                    png = open(src, "rb").read()
                else:
                    png = base64.b64decode(ICON_B64)
                ico_path = os.path.join(tempfile.gettempdir(), "macro_builder.ico")
                with open(ico_path, "wb") as fh:
                    fh.write(_build_ico_from_png(png))
                root.iconbitmap(default=ico_path)
        except Exception:
            pass

# ---------------------------------------------------------------------------

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()
PROFILE_FILE = os.path.join(BASE_DIR, "macro_profiles.json")
_OLD_PROFILE_FILE = os.path.join(BASE_DIR, "fhold_profiles.json")

# carry settings over from the app's previous name, if they're still around
if not os.path.exists(PROFILE_FILE) and os.path.exists(_OLD_PROFILE_FILE):
    try:
        shutil.copyfile(_OLD_PROFILE_FILE, PROFILE_FILE)
    except OSError:
        PROFILE_FILE = _OLD_PROFILE_FILE     # fall back to the old file

IDLE_COLOR = "#cc1111"     # red
RUN_COLOR = "#11aa11"      # green

# main-window dark theme palette
BG = "#1b1d24"
PANEL = "#2a2d3a"
FG = "#e8e8ea"
MUTED = "#9aa0ad"
ACCENT = "#4f8cff"
CHIP_BG = "#1f2330"
CARD_HOVER = "#343848"
CARD_SEL = "#26324d"

if PYNPUT_OK:
    # Special (named) keys, built defensively so a key missing on some
    # platform is simply skipped instead of crashing at import.
    _HOTKEY_SPECIALS = [
        ("F1", "f1"), ("F2", "f2"), ("F3", "f3"), ("F4", "f4"),
        ("F5", "f5"), ("F6", "f6"), ("F7", "f7"), ("F8", "f8"),
        ("F9", "f9"), ("F10", "f10"), ("F11", "f11"), ("F12", "f12"),
        ("Esc", "esc"), ("Tab", "tab"), ("Space", "space"),
        ("Enter", "enter"), ("Bksp", "backspace"),
        ("Insert", "insert"), ("Delete", "delete"),
        ("Home", "home"), ("End", "end"),
        ("PageUp", "page_up"), ("PageDn", "page_down"),
        ("Up", "up"), ("Down", "down"), ("Left", "left"), ("Right", "right"),
        ("Pause", "pause"), ("PrntScr", "print_screen"),
        ("ScrlLk", "scroll_lock"), ("NumLk", "num_lock"), ("CapsLk", "caps_lock"),
        ("Menu", "menu"),
    ]
    EMERGENCY_KEYS = {}
    for _label, _attr in _HOTKEY_SPECIALS:
        _k = getattr(Key, _attr, None)
        if _k is not None:
            EMERGENCY_KEYS[_label] = _k
    # every letter, digit and common symbol (character keys)
    for _ch in "abcdefghijklmnopqrstuvwxyz":
        EMERGENCY_KEYS[_ch.upper()] = KeyCode.from_char(_ch)
    for _ch in "0123456789":
        EMERGENCY_KEYS[_ch] = KeyCode.from_char(_ch)
    for _ch in "-=[]\\;',./`":
        EMERGENCY_KEYS[_ch] = KeyCode.from_char(_ch)
    # named keys that can be used inside a macro step
    SPECIAL_KEYS = {
        "space": Key.space, "enter": Key.enter, "tab": Key.tab, "esc": Key.esc,
        "backspace": Key.backspace, "delete": Key.delete,
        "shift": Key.shift, "ctrl": Key.ctrl, "alt": Key.alt,
        "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
        "home": Key.home, "end": Key.end,
        "insert": Key.insert, "pageup": Key.page_up, "pagedown": Key.page_down,
        "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4, "f5": Key.f5,
        "f6": Key.f6, "f7": Key.f7, "f8": Key.f8, "f9": Key.f9,
        "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
    }
    STEP_KEY_FROM_KEY = {v: k for k, v in SPECIAL_KEYS.items()}
else:
    EMERGENCY_KEYS = {}
    SPECIAL_KEYS = {}
    STEP_KEY_FROM_KEY = {}


def key_to_step_string(k):
    """Convert a pressed pynput key into a macro-step key string, or None."""
    ch = getattr(k, "char", None)
    if ch:
        if len(ch) == 1 and ch.isprintable():
            return ch.lower() if ch.isalpha() else ch
        return None
    name = STEP_KEY_FROM_KEY.get(k)
    if name:
        return name
    kn = getattr(k, "name", "") or ""        # left/right modifier variants
    if kn.startswith("shift"):
        return "shift"
    if kn.startswith("ctrl"):
        return "ctrl"
    if kn.startswith("alt"):
        return "alt"
    return None

if PYNPUT_OK:
    BUTTONS = {"left": Button.left, "right": Button.right, "middle": Button.middle}
else:
    BUTTONS = {}

# suggestions offered in the step editor's key box (still free-typeable)
KEY_CHOICES = ["f", "e", "q", "r", "w", "a", "s", "d", "1", "2", "3",
               "space", "enter", "shift", "ctrl", "alt", "tab",
               "up", "down", "left", "right"]


def resolve_key(name):
    """Turn a key name from a step into a pynput key object."""
    name = (name or "").strip()
    low = name.lower()
    if low in SPECIAL_KEYS:
        return SPECIAL_KEYS[low]
    if name:
        return KeyCode.from_char(name[0])
    return KeyCode.from_char("f")


def normalize_profile(p):
    """Ensure a profile uses the step format; migrate the old hold/gap format."""
    if isinstance(p.get("steps"), list):
        p.setdefault("loop", True)
        p.setdefault("name", "Profile")
        p.setdefault("start_key", "F8")
        p.setdefault("stop_key", "F9")
        return p
    hold = int(p.get("hold_ms", 50))
    gap = int(p.get("gap_ms", 50))
    return {
        "name": p.get("name", "Profile"),
        "loop": True,
        "start_key": p.get("start_key", "F8"),
        "stop_key": p.get("stop_key", "F9"),
        "steps": [
            {"type": "key", "key": "f", "hold_ms": hold},
            {"type": "delay", "ms": gap},
        ],
    }


def fmt_step_key(s):
    """Friendly label for a step key value (keyboard or mouse:*)."""
    if s and s.startswith("mouse:"):
        return s.split(":", 1)[1].capitalize() + " mouse"
    return s or "?"


def find_ahk_exe():
    """Best-effort location of an installed AutoHotkey executable."""
    candidates = [
        r"C:\Program Files\AutoHotkey\v2\AutoHotkey.exe",
        r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
        r"C:\Program Files\AutoHotkey\AutoHotkeyU64.exe",
        r"C:\Program Files\AutoHotkey\AutoHotkeyU32.exe",
        r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\AutoHotkeyU64.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return shutil.which("AutoHotkey") or shutil.which("AutoHotkeyU64") or ""


def describe_step(step):
    if step.get("type") == "key":
        key = step.get("key", "f")
        hold = int(step.get("hold_ms", 0))
        if isinstance(key, str) and key.startswith("mouse:"):
            btn = key.split(":", 1)[1]
            if hold <= 0:
                return f"Click  {btn} mouse"
            return f"Hold  {btn} mouse  for {hold} ms"
        if hold <= 0:
            return f"Tap  {key}"
        return f"Hold  {key}  for {hold} ms"
    return f"Wait  {int(step.get('ms', 0))} ms"


DEFAULT_PROFILES = [
    {"name": "Hold F", "loop": True, "start_key": "F8", "stop_key": "F9",
     "steps": [{"type": "key", "key": "f", "hold_ms": 50},
               {"type": "delay", "ms": 50}]},
    {"name": "Spam Space", "loop": True, "start_key": "F8", "stop_key": "F9",
     "steps": [{"type": "key", "key": "space", "hold_ms": 0},
               {"type": "delay", "ms": 300}]},
    {"name": "W → Space combo", "loop": True, "start_key": "F8", "stop_key": "F9",
     "steps": [{"type": "key", "key": "w", "hold_ms": 400},
               {"type": "key", "key": "space", "hold_ms": 0},
               {"type": "delay", "ms": 600}]},
]


class FHoldApp:
    def __init__(self, root):
        self.root = root
        self.kb = Controller()
        self.mouse = MouseController()

        self.profiles = []
        self.active_index = None
        self.running = False
        self.stop_event = threading.Event()
        self.worker = None

        self.start_key_var = tk.StringVar(value="F8")
        self.emergency_var = tk.StringVar(value="F9")  # stop key
        self.close_key_var = tk.StringVar(value="F10")  # close-app key
        self.opacity_var = tk.IntVar(value=90)  # overlay opacity, percent
        self._overlay_geo = "+0+0"
        self._quit_flag = False

        # ----- AutoHotkey runner -----
        self.ahk_exe = find_ahk_exe()
        self.ahk_script = ""
        self.ahk_proc = None
        self.ahk_running = False

        # custom app icon path ("" = built-in)
        self.icon_path = ""

        # ----- standalone auto clicker -----
        self.autoclick_running = False
        self.autoclick_stop = threading.Event()
        self.autoclick_worker = None
        self.autoclick_ms_var = tk.StringVar(value="100")  # ms between clicks
        self.autoclick_key_var = tk.StringVar(value="F7")  # toggle hotkey
        self._autoclick_ms = 100  # plain int kept in sync for the hotkey thread

        # press-to-bind capture state
        self._capturing = None     # which hotkey is being rebound, or None
        self._captured = None      # (which, label) handed back to the main thread
        self._step_key_var = None  # step-editor key var while capturing
        self._step_key_btn = None  # step-editor key button while capturing

        self.load_profiles()
        self.build_main_window()
        self.build_overlay()
        self.refresh_profile_list()
        self._apply_icon()            # apply any saved custom icon
        self.start_emergency_listener()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.tick()  # start the UI refresh loop

    # ----- persistence -----------------------------------------------------
    def load_profiles(self):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.profiles = data.get("profiles", [])
            self._overlay_geo = data.get("overlay_geo", "+0+0")
            self.close_key_var.set(data.get("close_key", "F10"))
            self.opacity_var.set(int(data.get("overlay_opacity", 90)))
            self.autoclick_ms_var.set(str(data.get("autoclick_ms", 100)))
            self.autoclick_key_var.set(data.get("autoclick_key", "F7"))
            self.ahk_script = data.get("ahk_script", "")
            self.icon_path = data.get("icon_path", "")
            saved_exe = data.get("ahk_exe", "")
            if saved_exe and os.path.exists(saved_exe):
                self.ahk_exe = saved_exe
            # migrate any old global start/stop onto profiles that lack their own
            old_start = data.get("start_key")
            old_stop = data.get("emergency_key")
            for rp in self.profiles:
                if isinstance(rp, dict):
                    if old_start and "start_key" not in rp:
                        rp["start_key"] = old_start
                    if old_stop and "stop_key" not in rp:
                        rp["stop_key"] = old_stop
            if not self.profiles:
                self.profiles = list(DEFAULT_PROFILES)
            self.profiles = [normalize_profile(p) for p in self.profiles]
            if self.profiles:
                self.active_index = 0
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            self.profiles = [normalize_profile(p) for p in DEFAULT_PROFILES]
            self.active_index = 0 if self.profiles else None
        self._sync_profile_hotkeys()
        self._sync_profile_hotkeys()

    def _sync_profile_hotkeys(self):
        """Load the active profile's start/stop hotkeys into the display vars."""
        if self.active_index is not None and 0 <= self.active_index < len(self.profiles):
            p = self.profiles[self.active_index]
            self.start_key_var.set(p.get("start_key", "F8"))
            self.emergency_var.set(p.get("stop_key", "F9"))

    def save_profiles(self):
        try:
            geo = self.overlay.geometry().split("+", 1)
            overlay_geo = "+" + geo[1] if len(geo) > 1 else self._overlay_geo
        except Exception:
            overlay_geo = self._overlay_geo
        data = {
            "profiles": self.profiles,
            "overlay_geo": overlay_geo,
            "close_key": self.close_key_var.get(),
            "overlay_opacity": self.opacity_var.get(),
            "autoclick_ms": self.autoclick_ms_var.get(),
            "autoclick_key": self.autoclick_key_var.get(),
            "ahk_script": self.ahk_script,
            "ahk_exe": self.ahk_exe,
            "icon_path": self.icon_path,
        }
        try:
            with open(PROFILE_FILE, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
        except OSError:
            pass

    # ----- main window ------------------------------------------------------
    def apply_theme(self):
        self.root.configure(bg=BG)
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        ui = "Segoe UI"
        style.configure(".", background=BG, foreground=FG, font=(ui, 10))
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("Header.TLabel", foreground=ACCENT, font=(ui, 15, "bold"))
        style.configure("Section.TLabel", foreground=MUTED, font=(ui, 9, "bold"))
        style.configure("Status.TLabel", foreground=MUTED, font=("Consolas", 9))
        style.configure("TButton", background=PANEL, foreground=FG,
                        borderwidth=0, focusthickness=0, padding=6, font=(ui, 9, "bold"))
        style.map("TButton",
                  background=[("active", ACCENT), ("pressed", ACCENT)],
                  foreground=[("active", "#ffffff")])
        style.configure("TCombobox", fieldbackground=PANEL, background=PANEL,
                        foreground=FG, arrowcolor=FG, bordercolor=PANEL,
                        selectbackground=PANEL, selectforeground=FG, padding=2)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL)],
                  foreground=[("readonly", FG)])
        style.configure("TEntry", fieldbackground=PANEL, foreground=FG,
                        insertcolor=FG, bordercolor="#3a3e4d",
                        lightcolor="#3a3e4d", darkcolor="#3a3e4d",
                        selectbackground=ACCENT, selectforeground="#ffffff",
                        padding=5)
        style.map("TEntry",
                  fieldbackground=[("focus", PANEL)],
                  foreground=[("focus", FG)],
                  bordercolor=[("focus", ACCENT)])
        style.configure("Horizontal.TScale", background=BG, troughcolor=PANEL,
                        bordercolor=BG)
        style.configure("TCheckbutton", background=BG, foreground=FG)
        style.map("TCheckbutton", background=[("active", BG)],
                  foreground=[("active", FG)],
                  indicatorcolor=[("selected", ACCENT), ("!selected", PANEL)])
        # combobox drop-down list colors
        self.root.option_add("*TCombobox*Listbox.background", PANEL)
        self.root.option_add("*TCombobox*Listbox.foreground", FG)
        self.root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        self.root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 9))

    def build_main_window(self):
        self.root.title("Macro Builder")
        self.root.geometry("470x740")
        self.root.minsize(430, 660)
        self.apply_theme()

        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="⌨  Macro Builder", style="Header.TLabel").pack(anchor="w")
        ttk.Label(outer, text="build & run key macros", style="Section.TLabel").pack(
            anchor="w", pady=(0, 6))
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill="x", pady=(0, 12))

        self.profiles_header = ttk.Label(outer, text="PROFILES", style="Section.TLabel")
        self.profiles_header.pack(anchor="w")

        # scrollable list of profile cards
        list_panel = tk.Frame(outer, bg=PANEL, bd=0, highlightthickness=1,
                              highlightbackground="#3a3e4d")
        list_panel.pack(fill="both", expand=True, pady=(4, 8))
        self.cards_canvas = tk.Canvas(list_panel, bg=PANEL, bd=0, highlightthickness=0,
                                      height=170)
        vsb = ttk.Scrollbar(list_panel, orient="vertical", command=self.cards_canvas.yview)
        self.cards_frame = tk.Frame(self.cards_canvas, bg=PANEL)
        self._cards_window = self.cards_canvas.create_window(
            (0, 0), window=self.cards_frame, anchor="nw")
        self.cards_canvas.configure(yscrollcommand=vsb.set)
        self.cards_canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.cards_frame.bind(
            "<Configure>",
            lambda e: self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all")))
        self.cards_canvas.bind(
            "<Configure>",
            lambda e: self.cards_canvas.itemconfig(self._cards_window, width=e.width))
        self.cards_canvas.bind("<MouseWheel>", self._on_wheel)
        self.profile_cards = []

        edit_row = ttk.Frame(outer)
        edit_row.pack(fill="x", pady=(0, 12))
        ttk.Button(edit_row, text="+ New",  command=self.add_profile).pack(side="left")
        ttk.Button(edit_row, text="Edit",   command=self.edit_profile).pack(side="left", padx=6)
        ttk.Button(edit_row, text="Delete", command=self.delete_profile).pack(side="left")
        ttk.Button(edit_row, text="↓", width=3,
                   command=lambda: self.move_profile(1)).pack(side="right")
        ttk.Button(edit_row, text="↑", width=3,
                   command=lambda: self.move_profile(-1)).pack(side="right", padx=(0, 6))

        ttk.Label(outer, text="HOTKEYS", style="Section.TLabel").pack(anchor="w")
        ttk.Label(outer, text="Start/Stop save to the selected profile · Close is global",
                  style="Status.TLabel").pack(anchor="w")
        hk_row = ttk.Frame(outer)
        hk_row.pack(fill="x", pady=(4, 12))

        def bind_btn(parent, which):
            b = tk.Button(parent, width=9, bg=PANEL, fg=FG, relief="flat", bd=0,
                          activebackground=ACCENT, activeforeground="#ffffff",
                          font=("Segoe UI", 9, "bold"), cursor="hand2",
                          command=lambda: self.set_capture(which))
            return b

        ttk.Label(hk_row, text="Start").grid(row=0, column=0, sticky="w", pady=3, padx=(0, 4))
        self.hk_start_btn = bind_btn(hk_row, "start")
        self.hk_start_btn.grid(row=0, column=1, padx=(0, 18), pady=3)
        ttk.Label(hk_row, text="Stop").grid(row=0, column=2, sticky="w", pady=3, padx=(0, 4))
        self.hk_stop_btn = bind_btn(hk_row, "stop")
        self.hk_stop_btn.grid(row=0, column=3, pady=3)
        ttk.Label(hk_row, text="Close").grid(row=1, column=0, sticky="w", pady=3, padx=(0, 4))
        self.hk_close_btn = bind_btn(hk_row, "close")
        self.hk_close_btn.grid(row=1, column=1, padx=(0, 18), pady=3)

        # ----- auto clicker section -----
        ttk.Label(outer, text="AUTO CLICKER", style="Section.TLabel").pack(anchor="w")
        ac_row = ttk.Frame(outer)
        ac_row.pack(fill="x", pady=(4, 4))
        ttk.Label(ac_row, text="ms between clicks").grid(row=0, column=0, sticky="w", padx=(0, 6))
        ttk.Entry(ac_row, textvariable=self.autoclick_ms_var, width=8).grid(
            row=0, column=1, padx=(0, 18))
        ttk.Label(ac_row, text="Hotkey").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.hk_autoclick_btn = tk.Button(
            ac_row, width=9, bg=PANEL, fg=FG, relief="flat", bd=0,
            activebackground=ACCENT, activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"), cursor="hand2",
            command=lambda: self.set_capture("autoclick"))
        self.hk_autoclick_btn.grid(row=0, column=3)
        self.autoclick_btn = tk.Button(outer, text="Start clicking", bg=PANEL, fg=FG,
                                       activebackground=ACCENT, activeforeground="#ffffff",
                                       relief="flat", bd=0, font=("Segoe UI", 10, "bold"),
                                       cursor="hand2", command=self.toggle_autoclick)
        self.autoclick_btn.pack(fill="x", pady=(2, 12), ipady=5)

        # ----- AutoHotkey section -----
        ttk.Label(outer, text="AUTOHOTKEY", style="Section.TLabel").pack(anchor="w")
        ahk_row = ttk.Frame(outer)
        ahk_row.pack(fill="x", pady=(4, 4))
        ttk.Button(ahk_row, text="Choose .ahk…", command=self.choose_ahk).pack(side="left")
        self.ahk_name_label = ttk.Label(ahk_row, text="(no script)", style="Status.TLabel")
        self.ahk_name_label.pack(side="left", padx=8)
        self.ahk_btn = tk.Button(outer, text="Run script", bg=PANEL, fg=FG,
                                 activebackground=ACCENT, activeforeground="#ffffff",
                                 relief="flat", bd=0, font=("Segoe UI", 10, "bold"),
                                 cursor="hand2", command=self.run_ahk)
        self.ahk_btn.pack(fill="x", pady=(2, 12), ipady=5)

        ttk.Label(outer, text="OVERLAY OPACITY", style="Section.TLabel").pack(anchor="w")
        op_row = ttk.Frame(outer)
        op_row.pack(fill="x", pady=(4, 12))
        self.op_value_label = ttk.Label(op_row, text=f"{self.opacity_var.get()}%",
                                        width=5, style="Status.TLabel")
        self.op_value_label.pack(side="right")
        ttk.Scale(op_row, from_=20, to=100, variable=self.opacity_var,
                  command=self.on_opacity_change).pack(
                      side="left", fill="x", expand=True, padx=(0, 8))

        # ----- app icon -----
        ttk.Label(outer, text="APP ICON", style="Section.TLabel").pack(anchor="w")
        icon_row = ttk.Frame(outer)
        icon_row.pack(fill="x", pady=(4, 12))
        ttk.Button(icon_row, text="Choose…", command=self.choose_icon).pack(side="left")
        ttk.Button(icon_row, text="Reset", command=self.reset_icon).pack(side="left", padx=6)
        self.icon_name_label = ttk.Label(icon_row, text="default", style="Status.TLabel")
        self.icon_name_label.pack(side="left", padx=8)

        self.status_label = ttk.Label(outer, text="OFF", style="Status.TLabel")
        self.status_label.pack(anchor="w", pady=(2, 8))

        ctrl = ttk.Frame(outer)
        ctrl.pack(fill="x")
        self.start_btn = tk.Button(ctrl, text="START", bg=RUN_COLOR, fg="white",
                                   activebackground="#0d8f0d", activeforeground="white",
                                   relief="flat", bd=0, font=("Segoe UI", 12, "bold"),
                                   cursor="hand2", command=self.start_holding)
        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0, 4), ipady=8)
        self.stop_btn = tk.Button(ctrl, text="EMERGENCY STOP", bg=IDLE_COLOR, fg="white",
                                  activebackground="#a30d0d", activeforeground="white",
                                  relief="flat", bd=0, font=("Segoe UI", 12, "bold"),
                                  cursor="hand2", command=self.stop_holding)
        self.stop_btn.pack(side="left", expand=True, fill="x", padx=(4, 0), ipady=8)

    # ----- overlay ----------------------------------------------------------
    def build_overlay(self):
        self.overlay = tk.Toplevel(self.root)
        self.overlay.title("Macro Builder")
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.apply_opacity()
        self.overlay.geometry(self._overlay_geo)

        # dark header bar
        self.ov_frame = tk.Frame(self.overlay, bg="black", bd=1, relief="solid")
        self.ov_frame.pack(fill="both", expand=True)

        self.ov_header = tk.Label(self.ov_frame, text="DESTINY", bg="black",
                                  fg="white", font=("Consolas", 9, "bold"),
                                  padx=6, pady=2)
        self.ov_header.pack(fill="x")

        # info rows on the colored status background
        self.ov_body = tk.Frame(self.ov_frame, bg=IDLE_COLOR, padx=6, pady=4)
        self.ov_body.pack(fill="both", expand=True)

        rowfont = ("Consolas", 9, "bold")

        def make_row(label):
            r = tk.Frame(self.ov_body, bg=IDLE_COLOR)
            r.pack(fill="x", anchor="w")
            tk.Label(r, text=label, bg=IDLE_COLOR, fg="white",
                     font=rowfont, width=8, anchor="w").pack(side="left")
            val = tk.Label(r, text="", bg=IDLE_COLOR, fg="white",
                           font=rowfont, anchor="w")
            val.pack(side="left")
            return r, val

        self.row_profile, self.ov_profile_val = make_row("Profile:")
        self.row_start, self.ov_start_val = make_row("Start:")
        self.row_stop, self.ov_stop_val = make_row("Stop:")

        # On/Off toggle button
        self.ov_toggle = tk.Button(self.ov_body, text="OFF", font=("Consolas", 9, "bold"),
                                   fg="white", bg=IDLE_COLOR, activebackground=IDLE_COLOR,
                                   activeforeground="white", relief="ridge", bd=2,
                                   command=self.toggle_holding)
        self.ov_toggle.pack(fill="x", pady=(4, 0))

        # make the overlay draggable by the header / body (not the toggle button)
        drag_targets = [self.ov_frame, self.ov_header, self.ov_body,
                        self.row_profile, self.row_start, self.row_stop,
                        self.ov_profile_val, self.ov_start_val, self.ov_stop_val]
        for w in drag_targets:
            w.bind("<Button-1>", self._start_move)
            w.bind("<B1-Motion>", self._on_move)

    def apply_opacity(self):
        try:
            self.overlay.attributes("-alpha", max(0.2, self.opacity_var.get() / 100.0))
        except tk.TclError:
            pass

    def on_opacity_change(self, _value=None):
        # Scale gives a float string; round to a whole percent
        pct = int(round(float(self.opacity_var.get())))
        self.opacity_var.set(pct)
        if hasattr(self, "op_value_label"):
            self.op_value_label.configure(text=f"{pct}%")
        self.apply_opacity()

    def toggle_holding(self):
        if self.running:
            self.stop_holding()
        else:
            self.start_holding()

    def _start_move(self, e):
        self._drag_x, self._drag_y = e.x, e.y

    def _on_move(self, e):
        x = self.overlay.winfo_x() + e.x - self._drag_x
        y = self.overlay.winfo_y() + e.y - self._drag_y
        self.overlay.geometry(f"+{x}+{y}")

    # ----- profile management ----------------------------------------------
    def _on_wheel(self, e):
        try:
            self.cards_canvas.yview_scroll(int(-e.delta / 120), "units")
        except Exception:
            pass

    def refresh_profile_list(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        self.profile_cards = []

        if hasattr(self, "profiles_header"):
            self.profiles_header.configure(text=f"PROFILES  ({len(self.profiles)})")

        if not self.profiles:
            tk.Label(self.cards_frame, text="No profiles yet — click  + New",
                     bg=PANEL, fg=MUTED, font=("Segoe UI", 9, "italic"),
                     pady=20).pack(fill="x")
            return

        for i, p in enumerate(self.profiles):
            self._make_card(i, p)
        self._paint_cards()

    def _make_card(self, i, p):
        card = tk.Frame(self.cards_frame, bg=PANEL, cursor="hand2")
        card.pack(fill="x", padx=6, pady=3)

        bar = tk.Frame(card, bg=PANEL, width=4)
        bar.pack(side="left", fill="y")

        body = tk.Frame(card, bg=PANEL)
        body.pack(side="left", fill="both", expand=True, padx=(8, 8), pady=7)

        name = tk.Label(body, text=p["name"], bg=PANEL, fg=FG,
                        font=("Segoe UI", 11, "bold"), anchor="w")
        name.pack(fill="x")

        n = len(p.get("steps", []))
        loop_txt = "⟳ loop" if p.get("loop", True) else "▶ once"
        chips = tk.Frame(body, bg=PANEL)
        chips.pack(fill="x", pady=(4, 0))
        c1 = tk.Label(chips, text=f"▸ {n} step{'s' if n != 1 else ''}",
                      bg=CHIP_BG, fg="#c7ccd6", font=("Consolas", 8), padx=7, pady=2)
        c1.pack(side="left")
        c2 = tk.Label(chips, text=loop_txt, bg=CHIP_BG, fg="#c7ccd6",
                      font=("Consolas", 8), padx=7, pady=2)
        c2.pack(side="left", padx=(6, 0))

        entry = {"index": i, "card": card, "bar": bar,
                 "paint": [card, body, name, chips]}
        self.profile_cards.append(entry)

        for w in (card, body, name, chips, c1, c2):
            w.bind("<Button-1>", lambda e, idx=i: self._select_card(idx))
            w.bind("<Double-Button-1>", lambda e, idx=i: self._edit_card(idx))
            w.bind("<Enter>", lambda e, idx=i: self._hover_card(idx, True))
            w.bind("<Leave>", lambda e, idx=i: self._hover_card(idx, False))
            w.bind("<MouseWheel>", self._on_wheel)

    def _paint_cards(self):
        for c in self.profile_cards:
            sel = (c["index"] == self.active_index)
            bg = CARD_SEL if sel else PANEL
            for w in c["paint"]:
                w.configure(bg=bg)
            c["bar"].configure(bg=ACCENT if sel else bg)

    def _hover_card(self, idx, entering):
        if idx == self.active_index:
            return
        c = self.profile_cards[idx]
        if not entering:
            # ignore the leave if the pointer is still over this card's children
            x, y = c["card"].winfo_pointerxy()
            under = c["card"].winfo_containing(x, y)
            if under is not None and str(under).startswith(str(c["card"])):
                return
        bg = CARD_HOVER if entering else PANEL
        for w in c["paint"]:
            w.configure(bg=bg)
        c["bar"].configure(bg=bg)

    def _select_card(self, idx):
        self.active_index = idx
        self._paint_cards()
        self._sync_profile_hotkeys()

    def _edit_card(self, idx):
        self.active_index = idx
        self._paint_cards()
        self._sync_profile_hotkeys()
        self.edit_profile()

    def add_profile(self):
        data = self.profile_dialog("New profile")
        if data:
            self.profiles.append(normalize_profile(data))
            self.active_index = len(self.profiles) - 1
            self.refresh_profile_list()
            self._sync_profile_hotkeys()
            self.save_profiles()

    def edit_profile(self):
        if self.active_index is None or not self.profiles:
            return
        old = self.profiles[self.active_index]
        data = self.profile_dialog("Edit profile", old)
        if data:
            # keep the profile's existing start/stop hotkeys
            data["start_key"] = old.get("start_key", "F8")
            data["stop_key"] = old.get("stop_key", "F9")
            self.profiles[self.active_index] = data
            self.refresh_profile_list()
            self._sync_profile_hotkeys()
            self.save_profiles()

    def delete_profile(self):
        if self.active_index is None or not self.profiles:
            return
        name = self.profiles[self.active_index]["name"]
        if messagebox.askyesno("Delete", f"Delete profile '{name}'?"):
            del self.profiles[self.active_index]
            if not self.profiles:
                self.active_index = None
            else:
                self.active_index = min(self.active_index, len(self.profiles) - 1)
            self.refresh_profile_list()
            self._sync_profile_hotkeys()
            self.save_profiles()

    def move_profile(self, delta):
        if self.active_index is None or not self.profiles:
            return
        i = self.active_index
        j = i + delta
        if 0 <= j < len(self.profiles):
            self.profiles[i], self.profiles[j] = self.profiles[j], self.profiles[i]
            self.active_index = j
            self.refresh_profile_list()
            self.save_profiles()

    def _center_dialog(self, dlg, parent=None):
        """Position a dialog centered over its parent window."""
        parent = parent or self.root
        dlg.update_idletasks()
        w = dlg.winfo_width() or dlg.winfo_reqwidth()
        h = dlg.winfo_height() or dlg.winfo_reqheight()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        sw, sh = dlg.winfo_screenwidth(), dlg.winfo_screenheight()
        x = max(0, min(x, sw - w))
        y = max(0, min(y, sh - h))
        dlg.geometry(f"+{x}+{y}")

    def profile_dialog(self, title, initial=None):
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.configure(bg=BG)
        dlg.grab_set()

        name_var = tk.StringVar(value=(initial["name"] if initial else ""))
        loop_var = tk.BooleanVar(value=(initial.get("loop", True) if initial else True))
        # working copy of the steps so Cancel discards changes
        steps = [dict(s) for s in initial["steps"]] if initial else []

        frm = ttk.Frame(dlg, padding=18)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Name").pack(anchor="w")
        name_entry = ttk.Entry(frm, textvariable=name_var, width=34)
        name_entry.pack(fill="x", pady=(2, 10))

        ttk.Checkbutton(frm, text="Repeat until stopped (loop)",
                        variable=loop_var).pack(anchor="w", pady=(0, 10))

        ttk.Label(frm, text="Steps  (run top to bottom)",
                  style="Section.TLabel").pack(anchor="w")
        steps_list = tk.Listbox(frm, height=7, bd=0, relief="flat", bg=PANEL, fg=FG,
                                font=("Consolas", 10), highlightthickness=1,
                                highlightbackground="#3a3e4d", activestyle="none",
                                selectbackground=ACCENT, selectforeground="#ffffff")
        steps_list.pack(fill="x", pady=(4, 6))

        def render_steps(select=None):
            steps_list.delete(0, tk.END)
            for idx, s in enumerate(steps):
                steps_list.insert(tk.END, f" {idx + 1}.  {describe_step(s)}")
            if select is not None and 0 <= select < len(steps):
                steps_list.selection_clear(0, tk.END)
                steps_list.selection_set(select)
                steps_list.see(select)

        def selected_index():
            sel = steps_list.curselection()
            return sel[0] if sel else None

        def add_key():
            s = self.step_dialog(dlg, "key")
            if s:
                steps.append(s)
                render_steps(len(steps) - 1)

        def add_delay():
            s = self.step_dialog(dlg, "delay")
            if s:
                steps.append(s)
                render_steps(len(steps) - 1)

        def edit_step():
            i = selected_index()
            if i is None:
                return
            s = self.step_dialog(dlg, steps[i].get("type", "key"), steps[i])
            if s:
                steps[i] = s
                render_steps(i)

        def remove_step():
            i = selected_index()
            if i is None:
                return
            del steps[i]
            render_steps(min(i, len(steps) - 1) if steps else None)

        def move(delta):
            i = selected_index()
            if i is None:
                return
            j = i + delta
            if 0 <= j < len(steps):
                steps[i], steps[j] = steps[j], steps[i]
                render_steps(j)

        steps_list.bind("<Double-Button-1>", lambda e: edit_step())

        row1 = ttk.Frame(frm)
        row1.pack(fill="x", pady=(0, 4))
        ttk.Button(row1, text="+ Key", command=add_key).pack(side="left")
        ttk.Button(row1, text="+ Delay", command=add_delay).pack(side="left", padx=6)
        ttk.Button(row1, text="Edit", command=edit_step).pack(side="left")
        ttk.Button(row1, text="Remove", command=remove_step).pack(side="left", padx=6)

        row2 = ttk.Frame(frm)
        row2.pack(fill="x", pady=(0, 12))
        ttk.Button(row2, text="↑ Move up", command=lambda: move(-1)).pack(side="left")
        ttk.Button(row2, text="↓ Move down", command=lambda: move(1)).pack(side="left", padx=6)

        result = {}

        def on_ok():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Invalid", "Please enter a name.", parent=dlg)
                return
            if not steps:
                messagebox.showwarning("Invalid", "Add at least one step.", parent=dlg)
                return
            result.update(name=name, loop=bool(loop_var.get()), steps=steps)
            dlg.destroy()

        btns = ttk.Frame(frm)
        btns.pack(fill="x")
        ttk.Button(btns, text="Save", command=on_ok).pack(side="right")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side="right", padx=(0, 6))

        render_steps()
        name_entry.focus_set()
        self._center_dialog(dlg)
        dlg.wait_window()
        return result or None

    def step_dialog(self, parent, kind, initial=None):
        """Add/edit a single macro step. kind is 'key' or 'delay'."""
        dlg = tk.Toplevel(parent)
        dlg.title("Key step" if kind == "key" else "Delay step")
        dlg.transient(parent)
        dlg.resizable(False, False)
        dlg.configure(bg=BG)
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=16)
        frm.pack(fill="both", expand=True)
        result = {}

        if kind == "key":
            key_var = tk.StringVar(value=(initial.get("key", "f") if initial else "f"))
            hold_var = tk.StringVar(
                value=str(initial.get("hold_ms", 50) if initial else 50))
            ttk.Label(frm, text="Key  —  click, then press the key").pack(anchor="w")
            key_btn = tk.Button(frm, text=fmt_step_key(key_var.get()), bg=PANEL, fg=FG,
                                relief="flat", bd=0, activebackground=ACCENT,
                                activeforeground="#ffffff", font=("Segoe UI", 10, "bold"),
                                cursor="hand2")
            key_btn.configure(command=lambda: self.capture_step_key(key_var, key_btn))
            key_btn.pack(fill="x", pady=(2, 6), ipady=4)
            key_var.trace_add(
                "write", lambda *a: key_btn.configure(text=fmt_step_key(key_var.get())))

            def set_mouse(which):
                if self._capturing == "step":
                    self._capturing = None
                key_var.set("mouse:" + which)

            ttk.Label(frm, text="…or a mouse button", style="Status.TLabel").pack(anchor="w")
            mrow = ttk.Frame(frm)
            mrow.pack(fill="x", pady=(2, 10))
            ttk.Button(mrow, text="Left", command=lambda: set_mouse("left")).pack(side="left")
            ttk.Button(mrow, text="Right", command=lambda: set_mouse("right")).pack(
                side="left", padx=6)
            ttk.Button(mrow, text="Middle", command=lambda: set_mouse("middle")).pack(side="left")

            ttk.Label(frm, text="Hold for (milliseconds)  ·  0 = quick tap/click").pack(anchor="w")
            ttk.Entry(frm, textvariable=hold_var, width=26).pack(fill="x", pady=(2, 12))

            def ok():
                key = key_var.get().strip()
                if not key:
                    messagebox.showwarning("Invalid", "Pick a key or mouse button.", parent=dlg)
                    return
                try:
                    hold = int(float(hold_var.get()))
                    if hold < 0:
                        raise ValueError
                except ValueError:
                    messagebox.showwarning("Invalid", "Hold must be a number (ms).", parent=dlg)
                    return
                result.update(type="key", key=key, hold_ms=hold)
                dlg.destroy()
        else:
            ms_var = tk.StringVar(value=str(initial.get("ms", 100) if initial else 100))
            ttk.Label(frm, text="Wait for (milliseconds)").pack(anchor="w")
            ent = ttk.Entry(frm, textvariable=ms_var, width=26)
            ent.pack(fill="x", pady=(2, 12))
            ent.focus_set()

            def ok():
                try:
                    ms = int(float(ms_var.get()))
                    if ms < 0:
                        raise ValueError
                except ValueError:
                    messagebox.showwarning("Invalid", "Enter a number (ms).", parent=dlg)
                    return
                result.update(type="delay", ms=ms)
                dlg.destroy()

        btns = ttk.Frame(frm)
        btns.pack(fill="x")
        ttk.Button(btns, text="OK", command=ok).pack(side="right")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side="right", padx=(0, 6))
        dlg.bind("<Return>", lambda e: ok())
        self._center_dialog(dlg, parent)
        dlg.wait_window()
        if self._capturing == "step":      # dialog closed mid-capture
            self._capturing = None
        self._step_key_var = None
        self._step_key_btn = None
        return result or None

    # ----- the actual macro -------------------------------------------------
    def start_holding(self):
        if self.running:
            return
        if self.active_index is None or not self.profiles:
            messagebox.showwarning("No profile", "Create or select a profile first.")
            return
        p = self.profiles[self.active_index]
        steps = p.get("steps", [])
        if not steps:
            messagebox.showwarning("Empty macro",
                                   "This profile has no steps. Edit it to add some.")
            return
        loop = bool(p.get("loop", True))
        self.stop_event.clear()
        self.running = True
        self.worker = threading.Thread(
            target=self.macro_loop, args=(steps, loop), daemon=True)
        self.worker.start()

    def stop_holding(self):
        """Emergency stop: halt the macro, auto clicker and AHK script."""
        self.stop_event.set()
        self.running = False
        self.stop_autoclick()
        self.stop_ahk()

    # ----- standalone auto clicker -----------------------------------------
    def toggle_autoclick(self):
        if self.autoclick_running:
            self.stop_autoclick()
        else:
            self.start_autoclick()

    def start_autoclick(self):
        if self.autoclick_running:
            return
        interval_s = max(0.001, self._autoclick_ms / 1000.0)
        self.autoclick_stop.clear()
        self.autoclick_running = True
        self.autoclick_worker = threading.Thread(
            target=self.autoclick_loop, args=(interval_s,), daemon=True)
        self.autoclick_worker.start()

    def stop_autoclick(self):
        self.autoclick_stop.set()
        self.autoclick_running = False

    def autoclick_loop(self, interval_s):
        try:
            while not self.autoclick_stop.is_set():
                self.mouse.click(Button.left, 1)
                if self.autoclick_stop.wait(interval_s):
                    break
        finally:
            self.autoclick_running = False

    # ----- AutoHotkey runner -----------------------------------------------
    def choose_ahk(self):
        path = filedialog.askopenfilename(
            parent=self.root, title="Choose an AutoHotkey script",
            filetypes=[("AutoHotkey scripts", "*.ahk"), ("All files", "*.*")])
        if path:
            self.ahk_script = path
            self.save_profiles()

    def run_ahk(self):
        if not self.ahk_script or not os.path.exists(self.ahk_script):
            messagebox.showwarning("No script", "Choose a .ahk script first.")
            return
        self.stop_ahk()   # replace any instance we previously launched
        exe = self.ahk_exe if (self.ahk_exe and os.path.exists(self.ahk_exe)) else find_ahk_exe()
        if not exe:
            exe = filedialog.askopenfilename(
                parent=self.root, title="Locate AutoHotkey.exe",
                filetypes=[("AutoHotkey", "AutoHotkey*.exe"), ("All files", "*.*")])
        try:
            if exe and os.path.exists(exe):
                self.ahk_exe = exe
                self.ahk_proc = subprocess.Popen([exe, self.ahk_script])
            else:
                starter = getattr(os, "startfile", None)   # Windows file association
                if starter is None:
                    messagebox.showwarning(
                        "AutoHotkey not found",
                        "Couldn't find AutoHotkey. Install it from autohotkey.com, "
                        "then try again.")
                    return
                starter(self.ahk_script)
                self.ahk_proc = None
            self.ahk_running = True
            self.save_profiles()
        except Exception as e:
            self.ahk_running = False
            messagebox.showwarning("Couldn't run script", str(e))

    def stop_ahk(self):
        p = self.ahk_proc
        if p is not None:
            try:
                if p.poll() is None:
                    p.terminate()
            except Exception:
                pass
        self.ahk_proc = None
        self.ahk_running = False

    # ----- app icon --------------------------------------------------------
    def _icon_png_bytes(self):
        """PNG bytes for the current icon source (chosen / beside app / built-in)."""
        src = self.icon_path if (self.icon_path and os.path.exists(self.icon_path)) \
            else _external_icon()
        low = src.lower() if src else ""
        try:
            if low.endswith(".png"):
                return open(src, "rb").read()
            if low.endswith(".ico"):
                data = open(src, "rb").read()
                i = data.find(b"\x89PNG\r\n\x1a\n")     # PNG entry inside the .ico
                if i != -1:
                    return data[i:]
        except Exception:
            pass
        return base64.b64decode(ICON_B64)

    def _win_set_icon(self):
        """Force the title-bar + taskbar icon on Windows. Builds icon handles
        directly from the image bytes, which works for both PNG and ICO."""
        if not sys.platform.startswith("win"):
            return
        try:
            import ctypes
            from ctypes import wintypes
            u = ctypes.windll.user32
            u.GetAncestor.restype = wintypes.HWND
            u.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
            u.LoadImageW.restype = wintypes.HANDLE
            u.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
                                     ctypes.c_int, ctypes.c_int, wintypes.UINT]
            u.CreateIconFromResourceEx.restype = wintypes.HANDLE
            u.CreateIconFromResourceEx.argtypes = [ctypes.c_char_p, wintypes.DWORD,
                                                   wintypes.BOOL, wintypes.DWORD,
                                                   ctypes.c_int, ctypes.c_int, wintypes.UINT]
            u.SendMessageW.restype = ctypes.c_ssize_t
            u.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT,
                                       ctypes.c_size_t, ctypes.c_ssize_t]
            set_class = getattr(u, "SetClassLongPtrW", None) or u.SetClassLongW
            set_class.restype = ctypes.c_ssize_t
            set_class.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]

            GA_ROOT, WM_SETICON = 2, 0x0080
            ICON_SMALL, ICON_BIG = 0, 1
            IMAGE_ICON, LR = 1, 0x00000010          # LR_LOADFROMFILE
            GCLP_HICON, GCLP_HICONSM = -14, -34
            VER = 0x00030000

            hwnd = u.GetAncestor(self.root.winfo_id(), GA_ROOT) or self.root.winfo_id()

            src = self.icon_path if (self.icon_path and os.path.exists(self.icon_path)) \
                else _external_icon()
            big = small = 0
            # a real .ico: let Windows pick the right embedded sizes
            if src and src.lower().endswith(".ico"):
                big = u.LoadImageW(None, src, IMAGE_ICON, 32, 32, LR) or 0
                small = u.LoadImageW(None, src, IMAGE_ICON, 16, 16, LR) or 0
            # PNG (or .ico that LoadImage couldn't read): build handles from bytes
            if not big or not small:
                png = self._icon_png_bytes()
                buf = ctypes.create_string_buffer(png, len(png))
                if not big:
                    big = u.CreateIconFromResourceEx(buf, len(png), True, VER, 32, 32, 0) or 0
                if not small:
                    small = u.CreateIconFromResourceEx(buf, len(png), True, VER, 16, 16, 0) or 0

            if big:
                u.SendMessageW(hwnd, WM_SETICON, ICON_BIG, big)
                set_class(hwnd, GCLP_HICON, big)
            if small:
                u.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, small)
                set_class(hwnd, GCLP_HICONSM, small)
        except Exception:
            pass

    def _apply_icon(self):
        set_app_icon(self.root, self.icon_path or None)
        if sys.platform.startswith("win"):
            # the taskbar button may not exist immediately; try a few times
            for delay in (60, 800, 2000):
                self.root.after(delay, self._win_set_icon)
        if hasattr(self, "icon_name_label"):
            self.icon_name_label.configure(
                text=os.path.basename(self.icon_path) if self.icon_path else "default")

    def choose_icon(self):
        path = filedialog.askopenfilename(
            parent=self.root, title="Choose an icon image",
            filetypes=[("Images", "*.png *.ico *.gif"),
                       ("PNG", "*.png"), ("Icon", "*.ico"),
                       ("GIF", "*.gif"), ("All files", "*.*")])
        if not path:
            return
        if not path.lower().endswith((".png", ".ico", ".gif")):
            messagebox.showwarning(
                "Unsupported image",
                "Please choose a .png, .ico or .gif file.\n"
                "(JPGs aren't supported — convert it to PNG first.)")
            return
        self.icon_path = path
        self._apply_icon()
        self.save_profiles()

    def reset_icon(self):
        self.icon_path = ""
        self._apply_icon()
        self.save_profiles()

    def macro_loop(self, steps, loop):
        held = []
        held_mouse = []
        try:
            while not self.stop_event.is_set():
                for step in steps:
                    if self.stop_event.is_set():
                        break
                    if step.get("type") == "key":
                        keyname = step.get("key", "f")
                        hold_s = max(0.0, int(step.get("hold_ms", 0)) / 1000.0)
                        if isinstance(keyname, str) and keyname.startswith("mouse:"):
                            btn = BUTTONS.get(keyname.split(":", 1)[1], Button.left)
                            self.mouse.press(btn)
                            held_mouse.append(btn)
                            interrupted = self.stop_event.wait(hold_s)
                            self.mouse.release(btn)
                            if btn in held_mouse:
                                held_mouse.remove(btn)
                            if interrupted:
                                break
                        else:
                            key = resolve_key(keyname)
                            self.kb.press(key)
                            held.append(key)
                            interrupted = self.stop_event.wait(hold_s)
                            self.kb.release(key)
                            if key in held:
                                held.remove(key)
                            if interrupted:
                                break
                    else:  # delay
                        delay_s = max(0.0, int(step.get("ms", 0)) / 1000.0)
                        if self.stop_event.wait(delay_s):
                            break
                if not loop:
                    break
        finally:
            for k in held:                 # never leave a key stuck down
                try:
                    self.kb.release(k)
                except Exception:
                    pass
            for b in held_mouse:           # nor a mouse button
                try:
                    self.mouse.release(b)
                except Exception:
                    pass
            self.running = False

    # ----- global emergency hotkey -----------------------------------------
    def start_emergency_listener(self):
        self.listener = None
        try:
            self.listener = Listener(on_press=self.on_global_key)
            self.listener.daemon = True
            self.listener.start()
        except Exception:
            # The global hotkey couldn't be registered (e.g. the OS denied
            # input monitoring). The on-screen STOP buttons still work.
            self.listener = None

    @staticmethod
    def _key_matches(pressed, target):
        """True if a pressed key equals a configured hotkey, handling both
        named keys (Key.*) and character keys (letters/digits/symbols)."""
        if target is None:
            return False
        if isinstance(target, Key):
            return pressed == target
        # character key: compare by character, case-insensitively
        tchar = getattr(target, "char", None)
        pchar = getattr(pressed, "char", None)
        if tchar is not None and pchar is not None:
            return tchar.lower() == pchar.lower()
        return pressed == target

    def _label_for_pressed(self, pressed):
        """Find the dropdown label for a pressed key, or None if unsupported."""
        for label, target in EMERGENCY_KEYS.items():
            if self._key_matches(pressed, target):
                return label
        return None

    def _hotkey_var(self, which):
        return {"start": self.start_key_var, "stop": self.emergency_var,
                "close": self.close_key_var, "autoclick": self.autoclick_key_var}[which]

    def set_capture(self, which):
        # clicking the same button again cancels; clicking another switches
        self._capturing = None if self._capturing == which else which

    def capture_step_key(self, key_var, btn):
        if self._capturing == "step":          # toggle off
            self._capturing = None
            btn.configure(text=key_var.get() or "?")
            return
        self._capturing = "step"
        self._step_key_var = key_var
        self._step_key_btn = btn
        btn.configure(text="Press…")
        btn.focus_set()

    def on_global_key(self, key):
        if self._capturing == "step":
            s = key_to_step_string(key)
            if s is not None:
                self._captured = ("step", s)
                self._capturing = None
            return
        if self._capturing:
            label = self._label_for_pressed(key)
            if label is not None:
                self._captured = (self._capturing, label)
                self._capturing = None
            return  # swallow the key while rebinding; don't trigger actions

        close_key = EMERGENCY_KEYS.get(self.close_key_var.get())
        stop_key = EMERGENCY_KEYS.get(self.emergency_var.get())
        start_key = EMERGENCY_KEYS.get(self.start_key_var.get())
        autoclick_key = EMERGENCY_KEYS.get(self.autoclick_key_var.get())
        if self._key_matches(key, autoclick_key):   # auto clicker has its own toggle
            self.toggle_autoclick()
        if self._key_matches(key, close_key):
            self.stop_holding()      # release F right away
            self._quit_flag = True   # main thread closes the app on next tick
        elif self._key_matches(key, stop_key):   # stop wins over start on a shared key
            self.stop_holding()
        elif self._key_matches(key, start_key):
            self.start_holding()

    # ----- UI refresh loop --------------------------------------------------
    def tick(self):
        if self._quit_flag:
            self.on_close()
            return

        # apply a hotkey captured by the listener thread
        if self._captured is not None:
            which, val = self._captured
            self._captured = None
            if which == "step":
                if self._step_key_var is not None:
                    self._step_key_var.set(val)
            else:
                self._hotkey_var(which).set(val)
                # start/stop are saved on the active profile
                if which in ("start", "stop") and self.active_index is not None \
                        and 0 <= self.active_index < len(self.profiles):
                    p = self.profiles[self.active_index]
                    p["start_key" if which == "start" else "stop_key"] = val
                self.save_profiles()

        if self.active_index is not None and 0 <= self.active_index < len(self.profiles):
            name = self.profiles[self.active_index]["name"]
        else:
            name = "No profile"
        color = RUN_COLOR if self.running else IDLE_COLOR
        on_off = "ON" if self.running else "OFF"
        start_k = self.start_key_var.get()
        stop_k = self.emergency_var.get()

        # header reflects current profile + state
        self.ov_header.configure(text=f"{name.upper()}  {on_off}")

        # repaint the colored status body
        for w in (self.ov_body, self.row_profile, self.row_start, self.row_stop):
            w.configure(bg=color)
        for child in (self.row_profile.winfo_children()
                      + self.row_start.winfo_children()
                      + self.row_stop.winfo_children()):
            child.configure(bg=color)

        self.ov_profile_val.configure(text=name)
        self.ov_start_val.configure(text=start_k)
        self.ov_stop_val.configure(text=stop_k)
        self.ov_toggle.configure(text=on_off, bg=color, activebackground=color)

        self.status_label.configure(
            text=f"{on_off}  ·  Start: {start_k}  ·  Stop: {stop_k}  ·  "
                 f"Close: {self.close_key_var.get()}")

        # keep the plain ms value in sync for the hotkey thread
        try:
            v = int(float(self.autoclick_ms_var.get()))
            self._autoclick_ms = max(1, v)
        except (ValueError, tk.TclError):
            pass
        ac_key = self.autoclick_key_var.get()
        if self.autoclick_running:
            self.autoclick_btn.configure(text=f"Stop clicking  ({ac_key})",
                                         bg=RUN_COLOR, fg="white")
        else:
            self.autoclick_btn.configure(text=f"Start clicking  ({ac_key})",
                                         bg=PANEL, fg=FG)

        # press-to-bind buttons: show "Press…" while listening, else the key
        for which, btn, var in (
                ("start", self.hk_start_btn, self.start_key_var),
                ("stop", self.hk_stop_btn, self.emergency_var),
                ("close", self.hk_close_btn, self.close_key_var),
                ("autoclick", self.hk_autoclick_btn, self.autoclick_key_var)):
            if self._capturing == which:
                btn.configure(text="Press…", bg=ACCENT, fg="#ffffff")
            else:
                btn.configure(text=var.get(), bg=PANEL, fg=FG)

        # AutoHotkey runner state
        if self.ahk_proc is not None and self.ahk_proc.poll() is not None:
            self.ahk_proc = None
            self.ahk_running = False
        name = os.path.basename(self.ahk_script) if self.ahk_script else "(no script)"
        if self.ahk_running:
            name += "   · running"
        self.ahk_name_label.configure(text=name)
        self.ahk_btn.configure(text="Run script", bg=PANEL, fg=FG)

        self.root.after(100, self.tick)

    # ----- shutdown ---------------------------------------------------------
    def on_close(self):
        # stop the macro + auto clicker, but leave any AHK script running
        self.stop_event.set()
        self.running = False
        self.stop_autoclick()
        try:
            self.listener.stop()
        except Exception:
            pass
        self.save_profiles()
        self.root.destroy()


def main():
    if not PYNPUT_OK:
        r = tk.Tk()
        r.withdraw()
        messagebox.showerror(
            "Missing dependency",
            "Macro Builder needs the 'pynput' package, which isn't installed for "
            "the Python you're running this with.\n\n"
            "Install it from a terminal / command prompt:\n\n"
            "    python -m pip install pynput\n\n"
            "then start the program again.")
        r.destroy()
        return

    if sys.platform.startswith("win"):
        try:   # distinct taskbar identity (must be set before the window exists)
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "MacroBuilder.App")
        except Exception:
            pass

    root = tk.Tk()
    set_app_icon(root)

    def show_callback_error(*_args):
        messagebox.showerror("Macro Builder - error", traceback.format_exc())
    root.report_callback_exception = show_callback_error

    try:
        FHoldApp(root)
        root.mainloop()
    except Exception:
        try:
            root.withdraw()
        except Exception:
            pass
        messagebox.showerror("Macro Builder - startup error",
                             traceback.format_exc())
        try:
            root.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    main()
