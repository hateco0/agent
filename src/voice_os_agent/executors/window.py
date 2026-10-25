from __future__ import annotations

from ..nlu.intents import Intent, IntentType
from ..utils import win32
from .base import BaseExecutor, ExecutionResult


class WindowExecutor(BaseExecutor):
    handled = frozenset(
        {
            IntentType.SCREENSHOT,
            IntentType.MINIMIZE_ALL,
            IntentType.SHOW_DESKTOP,
        }
    )

    def execute(self, intent: Intent) -> ExecutionResult:
        if intent.type is IntentType.SCREENSHOT:
            path = win32.take_screenshot()
            if path is None:
                return ExecutionResult(success=False, message="Не удалось сделать скриншот.")
            return ExecutionResult(success=True, message=f"Скриншот сохранен: {path}")
        if intent.type is IntentType.MINIMIZE_ALL:
            try:
                win32.minimize_all_windows()
            except Exception as exc:
                return ExecutionResult(success=False, message=f"Не удалось свернуть окна: {exc}")
            return ExecutionResult(success=True, message="Все окна свернуты.")
        try:
            win32.show_desktop()
        except Exception as exc:
            return ExecutionResult(success=False, message=f"Не удалось показать рабочий стол: {exc}")
        return ExecutionResult(success=True, message="Рабочий стол открыт.")
