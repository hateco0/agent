from __future__ import annotations

import os
import subprocess

from ..nlu.intents import Intent, IntentType
from ..utils import win32
from .base import BaseExecutor, ExecutionResult

KNOWN_APPS: dict[str, str] = {
    "браузер": "chrome",
    "интернет": "chrome",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "chrome": "chrome",
    "google chrome": "chrome",
    "хром": "chrome",
    "firefox": "firefox",
    "фаерфокс": "firefox",
    "opera": "opera",
    "проводник": "explorer",
    "explorer": "explorer",
    "блокнот": "notepad",
    "notepad": "notepad",
    "калькулятор": "calc",
    "calc": "calc",
    "paint": "mspaint",
    "пейнт": "mspaint",
    "диспетчер задач": "taskmgr",
    "диспетчер процессов": "taskmgr",
    "параметры": "ms-settings:",
    "настройки": "ms-settings:",
    "терминал": "wt",
    "windows terminal": "wt",
    "wt": "wt",
    "powershell": "powershell",
    "ворд": "winword",
    "word": "winword",
    "эксель": "excel",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "outlook": "outlook",
    "steam": "steam",
    "стим": "steam",
    "spotify": "spotify",
    "discord": "discord",
    "дискорд": "discord",
    "дискордк": "discord",
    "telegram": "telegram",
    "телеграм": "telegram",
    "телега": "telegram",
    "visual studio code": "code",
    "vs code": "code",
    "vscode": "code",
    "код": "code",
    "ножницы": "snippingtool",
    "snipping tool": "snippingtool",
    "snippingtool": "snippingtool",
    "командная строка": "cmd",
    "cmd": "cmd",
    "консоль": "cmd",
}

PROCESS_NAMES: dict[str, str] = {
    "браузер": "chrome.exe",
    "интернет": "chrome.exe",
    "edge": "msedge.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "хром": "chrome.exe",
    "firefox": "firefox.exe",
    "фаерфокс": "firefox.exe",
    "opera": "opera.exe",
    "проводник": "explorer.exe",
    "explorer": "explorer.exe",
    "блокнот": "notepad.exe",
    "notepad": "notepad.exe",
    "paint": "mspaint.exe",
    "пейнт": "mspaint.exe",
    "диспетчер задач": "taskmgr.exe",
    "диспетчер процессов": "taskmgr.exe",
    "терминал": "WindowsTerminal.exe",
    "windows terminal": "WindowsTerminal.exe",
    "powershell": "powershell.exe",
    "ворд": "winword.exe",
    "word": "winword.exe",
    "эксель": "excel.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "outlook": "outlook.exe",
    "steam": "steam.exe",
    "стим": "steam.exe",
    "spotify": "spotify.exe",
    "discord": "Discord.exe",
    "дискорд": "Discord.exe",
    "дискордк": "Discord.exe",
    "telegram": "Telegram.exe",
    "телеграм": "Telegram.exe",
    "телега": "Telegram.exe",
    "visual studio code": "Code.exe",
    "vs code": "Code.exe",
    "code": "Code.exe",
    "vscode": "Code.exe",
    "cmd": "cmd.exe",
    "командная строка": "cmd.exe",
}


class AppsExecutor(BaseExecutor):
    handled = frozenset({IntentType.OPEN_APP, IntentType.CLOSE_APP})

    def execute(self, intent: Intent) -> ExecutionResult:
        app = str(intent.entities.get("app", "")).strip()
        if not app:
            return ExecutionResult(success=False, message="Не указано приложение.")
        key = app.lower()
        if intent.type is IntentType.OPEN_APP:
            return self._open(app, KNOWN_APPS.get(key, app))
        return self._close(app, key, KNOWN_APPS.get(key, app))

    @staticmethod
    def _open(app: str, target: str) -> ExecutionResult:
        try:
            os.startfile(target)
            return ExecutionResult(success=True, message=f"Открываю {app}.")
        except OSError:
            pass
        try:
            subprocess.Popen(["cmd", "/c", "start", "", target])
            return ExecutionResult(success=True, message=f"Открываю {app}.")
        except OSError:
            pass
        try:
            subprocess.Popen(target, shell=True)
            return ExecutionResult(success=True, message=f"Открываю {app}.")
        except Exception:
            pass
        # Попробовать найти в меню "Пуск" / ярлыках
        try:
            import winreg
            # Поиск по App Paths
            for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                try:
                    key = winreg.OpenKey(root, rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{target}.exe")
                    val, _ = winreg.QueryValue(key, None)
                    winreg.CloseKey(key)
                    os.startfile(val)
                    return ExecutionResult(success=True, message=f"Открываю {app}.")
                except Exception:
                    continue
        except Exception:
            pass
        try:
            subprocess.Popen(["cmd", "/c", "start", "", f"{target}.exe"])
            return ExecutionResult(success=True, message=f"Открываю {app}.")
        except OSError as exc:
            return ExecutionResult(success=False, message=f"Не удалось открыть {app}: {exc}")
        except Exception as exc:
            return ExecutionResult(success=False, message=f"Не удалось открыть {app}: {exc}")

    @staticmethod
    def _close(app: str, key: str, target: str) -> ExecutionResult:
        process = PROCESS_NAMES.get(key)
        if process is None:
            process = target if target.lower().endswith(".exe") else f"{target}.exe"
        completed = subprocess.run(
            ["taskkill", "/IM", process, "/F"],
            capture_output=True,
            text=True,
            timeout=15,
            encoding=win32.console_encoding(),
            errors="replace",
        )
        if completed.returncode == 0:
            return ExecutionResult(success=True, message=f"{app} закрыт.")
        output = (completed.stdout or completed.stderr or "").lower()
        if "not found" in output or "не найден" in output or "no process" in output or "процесс" in output and "не найден" in output:
            return ExecutionResult(success=True, message=f"{app} закрыт.")
        return ExecutionResult(success=False, message=f"Не удалось закрыть {app}.")
