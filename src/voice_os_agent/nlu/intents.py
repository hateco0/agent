from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class IntentType(Enum):
    UNKNOWN = auto()
    OPEN_APP = auto()
    CLOSE_APP = auto()
    OPEN_PATH = auto()
    SET_VOLUME = auto()
    CHANGE_VOLUME = auto()
    TOGGLE_MUTE = auto()
    SHUTDOWN = auto()
    RESTART = auto()
    SLEEP = auto()
    LOCK = auto()
    CANCEL_POWER = auto()
    SCREENSHOT = auto()
    MINIMIZE_ALL = auto()
    SHOW_DESKTOP = auto()
    SHELL_COMMAND = auto()


@dataclass
class Intent:
    type: IntentType
    raw_text: str = ""
    confidence: float = 1.0
    entities: dict[str, Any] = field(default_factory=dict)
