from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

CONFIG_PATH = Path("config") / "config.json"


@dataclass
class AudioSettings:
    input_device: int | None = None
    output_device: int | None = None
    muted: bool = False


@dataclass
class LLMSettings:
    enabled: bool = True
    base_url: str = "http://127.0.0.1:11434"
    model: str = "qwen2.5:3b-instruct"
    timeout: int = 60
    temperature: float = 0.2


@dataclass
class VoiceSettings:
    engine: str = "pyttsx3"
    tts_rate: int = 170
    tts_volume: float = 1.0
    tts_voice: str | None = None
    wake_word: str = "дейл"
    listen_timeout: int = 5
    phrase_time_limit: int = 8


@dataclass
class SecuritySettings:
    confirm_dangerous: bool = True
    allow_shell: bool = False


@dataclass
class BehaviorSettings:
    aliases: dict[str, str] = field(default_factory=dict)
    repeat_last: bool = True


@dataclass
class Settings:
    audio: AudioSettings = field(default_factory=AudioSettings)
    llm: LLMSettings = field(default_factory=LLMSettings)
    voice: VoiceSettings = field(default_factory=VoiceSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    behavior: BehaviorSettings = field(default_factory=BehaviorSettings)
    locale: str = "ru"
    theme: str = "system"

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> "Settings":
        if not path.exists():
            s = cls()
            try:
                s.save(path)
            except Exception:
                pass
            return s
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            if not isinstance(data, dict):
                return cls()
            s = cls()
            if isinstance(data.get("audio"), dict):
                s.audio = AudioSettings(**{k: v for k, v in data["audio"].items() if k in AudioSettings.__dataclass_fields__})
            if isinstance(data.get("llm"), dict):
                s.llm = LLMSettings(**{k: v for k, v in data["llm"].items() if k in LLMSettings.__dataclass_fields__})
            if isinstance(data.get("voice"), dict):
                s.voice = VoiceSettings(**{k: v for k, v in data["voice"].items() if k in VoiceSettings.__dataclass_fields__})
            if isinstance(data.get("security"), dict):
                s.security = SecuritySettings(**{k: v for k, v in data["security"].items() if k in SecuritySettings.__dataclass_fields__})
            if isinstance(data.get("behavior"), dict):
                s.behavior = BehaviorSettings(**{k: v for k, v in data["behavior"].items() if k in BehaviorSettings.__dataclass_fields__})
            s.locale = data.get("locale", s.locale)
            s.theme = data.get("theme", s.theme)
            return s
        except Exception:
            return cls()

    def save(self, path: Path = CONFIG_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "audio": asdict(self.audio),
            "llm": asdict(self.llm),
            "voice": asdict(self.voice),
            "security": asdict(self.security),
            "behavior": asdict(self.behavior),
            "locale": self.locale,
            "theme": self.theme,
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
