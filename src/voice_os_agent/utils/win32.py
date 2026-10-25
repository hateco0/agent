from __future__ import annotations

import ctypes
import os
import subprocess
from ctypes import wintypes
from datetime import datetime
from pathlib import Path

VK_LWIN = 0x5B
VK_D = 0x44
VK_M = 0x4D
KEYEVENTF_KEYUP = 0x0002

SCREENSHOT_DIR = Path.home() / "Pictures" / "voice_agent_screenshots"

KNOWN_FOLDER_IDS = {
    "desktop": "{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}",
    "documents": "{FDD39AD0-238F-46AF-ADB4-6C85480369C7}",
    "downloads": "{374DE290-123F-4565-9164-39C4925E467B}",
}

KNOWN_FOLDER_FALLBACKS = {
    "desktop": "Desktop",
    "documents": "Documents",
    "downloads": "Downloads",
}

POWERSHELL_SCREENSHOT = (
    "$ErrorActionPreference='SilentlyContinue'; "
    "Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue; "
    "Add-Type -AssemblyName System.Drawing -ErrorAction SilentlyContinue; "
    "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; "
    "[System.Reflection.Assembly]::LoadWithPartialName('System.Drawing') | Out-Null; "
    "$bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen; "
    "if ($bounds.Width -eq 0) { $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds }; "
    "$bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height; "
    "$graphics = [System.Drawing.Graphics]::FromImage($bitmap); "
    "$graphics.CopyFromScreen($bounds.Left, $bounds.Top, 0, 0, $bounds.Size); "
    "$bitmap.Save($env:VOICE_AGENT_SCREENSHOT, [System.Drawing.Imaging.ImageFormat]::Png); "
    "$graphics.Dispose(); $bitmap.Dispose()"
)


def press_hotkey(*keys: int) -> None:
    user32 = ctypes.windll.user32
    for key in keys:
        user32.keybd_event(key, 0, 0, 0)
    for key in reversed(keys):
        user32.keybd_event(key, 0, KEYEVENTF_KEYUP, 0)


def _known_folder_api(guid: str) -> Path | None:
    try:
        shell32 = ctypes.windll.shell32
        shell32.SHGetKnownFolderPath.argtypes = [
            ctypes.c_wchar_p,
            wintypes.DWORD,
            wintypes.HANDLE,
            ctypes.POINTER(ctypes.c_wchar_p),
        ]
        shell32.SHGetKnownFolderPath.restype = ctypes.c_long
        address = ctypes.c_wchar_p()
        if shell32.SHGetKnownFolderPath(guid, 0, None, ctypes.byref(address)) != 0:
            return None
        try:
            return Path(address.value)
        finally:
            ole32 = ctypes.windll.ole32
            ole32.CoTaskMemFree.argtypes = [ctypes.c_void_p]
            ole32.CoTaskMemFree.restype = None
            ole32.CoTaskMemFree(ctypes.cast(address, ctypes.c_void_p))
    except Exception:
        return None


def known_folder(name: str) -> Path | None:
    guid = KNOWN_FOLDER_IDS.get(name)
    if guid is None:
        return None
    resolved = _known_folder_api(guid)
    if resolved is not None:
        return resolved
    fallback = Path.home() / KNOWN_FOLDER_FALLBACKS[name]
    return fallback if fallback.exists() else None


def console_encoding() -> str:
    """Кодировка вывода утилит Windows при перенаправлении в канал (ANSI codepage)."""
    if os.name != "nt":
        return "utf-8"
    return "mbcs"


def minimize_all_windows() -> None:
    press_hotkey(VK_LWIN, VK_M)


def show_desktop() -> None:
    press_hotkey(VK_LWIN, VK_D)


def take_screenshot() -> Path | None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    target = SCREENSHOT_DIR / f"screenshot_{datetime.now():%Y%m%d_%H%M%S}.png"
    env = dict(os.environ, VOICE_AGENT_SCREENSHOT=str(target))
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", POWERSHELL_SCREENSHOT],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            encoding=console_encoding(),
            errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode == 0 and target.exists() and target.stat().st_size > 0:
        return target
    return None
