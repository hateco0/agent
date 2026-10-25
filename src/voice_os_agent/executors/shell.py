from __future__ import annotations

import subprocess

from ..nlu.intents import Intent, IntentType
from ..utils import win32
from .base import BaseExecutor, ExecutionResult

MAX_OUTPUT = 500


class ShellExecutor(BaseExecutor):
    handled = frozenset({IntentType.SHELL_COMMAND})

    def execute(self, intent: Intent) -> ExecutionResult:
        command = str(intent.entities.get("command", "")).strip()
        if not command:
            return ExecutionResult(success=False, message="Пустая команда.")
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
                shell=True,
                encoding=win32.console_encoding(),
                errors="replace",
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(success=False, message="Команда превысила лимит времени.")
        except OSError as exc:
            return ExecutionResult(success=False, message=f"Не удалось выполнить команду: {exc}")
        output = (completed.stdout or completed.stderr or "").strip()
        if len(output) > MAX_OUTPUT:
            output = output[:MAX_OUTPUT] + "..."
        if completed.returncode == 0:
            return ExecutionResult(success=True, message=output or "Команда выполнена.")
        return ExecutionResult(success=False, message=output or f"Код ошибки {completed.returncode}.")
