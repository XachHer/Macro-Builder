# Macro Builder

A desktop automation tool written in Python (Tkinter) for building, saving, and running custom keyboard and mouse macros.

## Features

- **Step-by-step macro editor**: chain key presses, mouse clicks, holds, and delays, then reorder or edit steps
- **Profiles**: create, edit, delete, and reorder macro profiles, each with its own start/stop hotkeys
- **Global hotkeys**: start, stop, and close the app even when another window has focus
- **Emergency stop**: instantly halts everything and releases any held keys or mouse buttons
- **Always-on-top overlay**: draggable status panel that turns green while a macro is running and red when idle, with adjustable opacity
- **Auto clicker**: separate clicker with its own interval and toggle hotkey
- **AutoHotkey launcher**: pick a `.ahk` script and start or stop it from inside the app
- **Custom app icon** and dark theme

## How it works

- Macros run on a background thread so the UI stays responsive
- A `pynput` keyboard listener runs in its own thread for global hotkeys and press-to-bind key capture
- Profiles and settings are saved to a local JSON file (`macro_profiles.json`)
- `try/finally` cleanup makes sure no key is ever left stuck down

## Setup

Requires Python 3.8+.

```
pip install -r requirements.txt
python macro_builder.pyw
```

On Windows you can also just double-click `macro_builder.pyw`.

## Built with

- Python 3
- Tkinter / ttk
- pynput
- threading, subprocess, json
