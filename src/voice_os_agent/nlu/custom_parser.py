from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..nlu.intents import Intent, IntentType

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from core import db
except Exception:
    db = None


@dataclass
class CustomMatch:
    intent: Intent
    matched_by: str


class CustomCommandParser:
    def __init__(self) -> None:
        self._custom = []
        self.reload()

    def reload(self) -> None:
        self._custom = []
        if db is None:
            return
        for cmd in db.db.get_custom_commands():
            trigger = cmd["trigger_text"]
            try:
                regex = re.compile("^" + re.escape(trigger).replace(r"\*", ".*") + "$", re.IGNORECASE)
            except Exception:
                regex = re.compile(re.escape(trigger), re.IGNORECASE)
            self._custom.append((regex, cmd))

    def match(self, cleaned_text: str) -> Intent | None:
        for regex, cmd in self._custom:
            if regex.match(cleaned_text) or regex.search(cleaned_text):
                intent_type = getattr(IntentType, cmd["intent_type"], IntentType.UNKNOWN)
                entities = cmd.get("entities") or {}
                return Intent(type=intent_type, raw_text=cleaned_text, entities=entities)
        return None
