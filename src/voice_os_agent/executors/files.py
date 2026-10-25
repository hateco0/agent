from __future__ import annotations

import os
from pathlib import Path

from ..nlu.intents import Intent, IntentType
from ..utils import win32
from .base import BaseExecutor, ExecutionResult

KNOWN_FOLDERS: dict[str, str] = {
    "рабочий стол": "desktop",
    "рабочего стола": "desktop",
    "мои документы": "documents",
    "документы": "documents",
    "загрузки": "downloads",
    "desktop": "desktop",
    "documents": "documents",
    "downloads": "downloads",
}

RECYCLE_BIN_NAMES = {"корзину", "корзина", "recycle bin"}
RECYCLE_BIN = "shell:RecycleBinFolder"


class FilesExecutor(BaseExecutor):
    handled = frozenset({IntentType.OPEN_PATH})

    def execute(self, intent: Intent) -> ExecutionResult:
        raw = str(intent.entities.get("path", "")).strip()
        if not raw:
            return ExecutionResult(success=False, message="Путь не указан.")
        key = raw.lower().strip()
        if key in RECYCLE_BIN_NAMES:
            target: Path | str = RECYCLE_BIN
        elif key in KNOWN_FOLDERS:
            folder = win32.known_folder(KNOWN_FOLDERS[key])
            if folder is None:
                folder = Path.home() / {"desktop": "Desktop", "documents": "Documents", "downloads": "Downloads"}[KNOWN_FOLDERS[key]]
            target = folder
        else:
            path = Path(raw)
            if not path.exists():
                return ExecutionResult(success=False, message=f"Путь не найден: {path}")
            target = path
        if isinstance(target, Path) and not target.exists():
            return ExecutionResult(success=False, message=f"Путь не найден: {target}")
        try:
            os.startfile(str(target))
        except OSError as exc:
            return ExecutionResult(success=False, message=f"Не удалось открыть: {exc}")
        return ExecutionResult(success=True, message=f"Открываю {raw}.")
