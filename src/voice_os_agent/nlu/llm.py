from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any

from ..nlu.intents import Intent, IntentType

SYSTEM_PROMPT = """Ты - парсер команд для голосового агента управления Windows.
Твоя задача - преобразовать команду пользователя в JSON-формат без объяснений.

Доступные типы команд:
- OPEN_APP: открыть приложение. entities: {"app": "название приложения"}
- CLOSE_APP: закрыть приложение. entities: {"app": "название приложения"}
- OPEN_PATH: открыть папку/путь. entities: {"path": "рабочий стол|мои документы|загрузки|корзина|или_путь"}
- SET_VOLUME: установить громкость. entities: {"level": "число 0-100"}
- CHANGE_VOLUME: изменить громкость. entities: {"direction": "увеличь|уменьши", "step": "число"}
- TOGGLE_MUTE: вкл/выкл звук. entities: {"mute": "выключи|включи"}
- SHUTDOWN: выключить компьютер
- RESTART: перезагрузить компьютер
- SLEEP: спящий режим
- LOCK: заблокировать компьютер
- CANCEL_POWER: отменить запланированное выключение/перезагрузку
- SCREENSHOT: сделать скриншот
- MINIMIZE_ALL: свернуть все окна
- SHOW_DESKTOP: показать рабочий стол
- SHELL_COMMAND: выполнить команду из белого списка. entities: {"command": "команда"}
- UNKNOWN: не распознано

Известные приложения: блокнот, калькулятор, браузер/chrome/хром/msedge/edge/firefox, проводник/explorer, дискорд/discord, телеграм/telegram, steam, spotify, vs code/code, терминал/wt/cmd/powershell, диспетчер задач/taskmgr

Белый список shell: ipconfig, systeminfo, tasklist, hostname, whoami, date, time, ver, driverquery, route, arp, netstat, getmac

Правила:
- Отвечай ТОЛЬКО валидным JSON без markdown, комментариев, текста
- Если не уверен - верни {"type": "UNKNOWN"}
- Для shell команды бери ТОЛЬКО команду из белого списка
- Учитывай естественные формулировки на русском языке

Примеры:
"мне надо открыть блокнот" -> {"type": "OPEN_APP", "entities": {"app": "блокнот"}}
"закрой дискорд" -> {"type": "CLOSE_APP", "entities": {"app": "дискорд"}}
"открой загрузки" -> {"type": "OPEN_PATH", "entities": {"path": "загрузки"}}
"поставь громкость потише на 10" -> {"type": "CHANGE_VOLUME", "entities": {"direction": "уменьши", "step": "10"}}
"выруби звук" -> {"type": "TOGGLE_MUTE", "entities": {"mute": "выключи"}}
"выключи комп" -> {"type": "SHUTDOWN"}
"сделай скриншот" -> {"type": "SCREENSHOT"}
"покажи рабочий стол" -> {"type": "SHOW_DESKTOP"}
"""


class LLMParser:
    def __init__(self, settings) -> None:
        self._settings = settings
        self._available = True

    def is_available(self) -> bool:
        return self._available and getattr(self._settings, "enabled", True)

    def parse(self, text: str) -> Intent | None:
        if not self.is_available() or not text:
            return None
        try:
            payload = self._build_payload(text)
            response = self._request(payload)
            if not response:
                return None
            data = self._extract_json(response)
            if not data or not isinstance(data, dict):
                return None
            intent_type = self._map_type(data.get("type"))
            if intent_type is None or intent_type == IntentType.UNKNOWN:
                # Проверяем явный UNKNOWN
                if data.get("type") == "UNKNOWN":
                    return Intent(type=IntentType.UNKNOWN, raw_text=text)
                return None
            entities = data.get("entities") or {}
            if not isinstance(entities, dict):
                entities = {}
            # Валидация сущностей
            if intent_type == IntentType.SHELL_COMMAND:
                cmd = str(entities.get("command", "")).strip().split()[0].lower().removesuffix(".exe")
                whitelist = {item.lower().removesuffix(".exe") for item in getattr(getattr(self._settings, "security", None), "shell_whitelist", [])}
                if cmd not in whitelist:
                    return None
            return Intent(type=intent_type, raw_text=text, entities=entities)
        except Exception:
            self._available = False
            return None

    def _build_payload(self, text: str) -> dict[str, Any]:
        settings = self._settings
        if settings.provider == "ollama":
            return {
                "model": settings.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                "stream": False,
                "options": {"temperature": settings.temperature},
            }
        # OpenRouter/Groq совместимый формат
        headers = {}
        if settings.api_key:
            headers["Authorization"] = f"Bearer {settings.api_key}"
        return {
            "model": settings.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            "temperature": settings.temperature,
            "max_tokens": 256,
        }

    def _request(self, payload: dict[str, Any]) -> str | None:
        settings = self._settings
        if settings.provider == "ollama":
            url = f"{settings.base_url.rstrip('/')}/api/chat"
        elif settings.provider == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
        elif settings.provider == "openrouter":
            url = "https://openrouter.ai/api/v1/chat/completions"
        else:
            url = f"{settings.base_url.rstrip('/')}/v1/chat/completions"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        if settings.api_key and settings.provider != "ollama":
            req.add_header("Authorization", f"Bearer {settings.api_key}")
        try:
            with urllib.request.urlopen(req, timeout=settings.timeout) as resp:
                body = resp.read().decode("utf-8")
        except Exception:
            return None
        return body

    def _extract_json(self, response: str) -> dict[str, Any] | None:
        try:
            data = json.loads(response)
        except Exception:
            m = re.search(r"\{.*\}", response, re.DOTALL)
            if not m:
                return None
            try:
                data = json.loads(m.group(0))
            except Exception:
                return None
        if isinstance(data, dict) and "message" in data:
            content = data["message"].get("content", "")
            if isinstance(content, str):
                m = re.search(r"\{.*\}", content, re.DOTALL)
                if m:
                    try:
                        return json.loads(m.group(0))
                    except Exception:
                        return None
        if isinstance(data, dict) and "choices" in data:
            try:
                content = data["choices"][0]["message"]["content"]
                if isinstance(content, str):
                    m = re.search(r"\{.*\}", content, re.DOTALL)
                    if m:
                        return json.loads(m.group(0))
            except Exception:
                return None
        if isinstance(data, dict) and "type" in data:
            return data
        return None

    def _map_type(self, type_str: Any) -> IntentType | None:
        if not isinstance(type_str, str):
            return None
        mapping = {
            "OPEN_APP": IntentType.OPEN_APP,
            "CLOSE_APP": IntentType.CLOSE_APP,
            "OPEN_PATH": IntentType.OPEN_PATH,
            "SET_VOLUME": IntentType.SET_VOLUME,
            "CHANGE_VOLUME": IntentType.CHANGE_VOLUME,
            "TOGGLE_MUTE": IntentType.TOGGLE_MUTE,
            "SHUTDOWN": IntentType.SHUTDOWN,
            "RESTART": IntentType.RESTART,
            "SLEEP": IntentType.SLEEP,
            "LOCK": IntentType.LOCK,
            "CANCEL_POWER": IntentType.CANCEL_POWER,
            "SCREENSHOT": IntentType.SCREENSHOT,
            "MINIMIZE_ALL": IntentType.MINIMIZE_ALL,
            "SHOW_DESKTOP": IntentType.SHOW_DESKTOP,
            "SHELL_COMMAND": IntentType.SHELL_COMMAND,
            "UNKNOWN": IntentType.UNKNOWN,
        }
        return mapping.get(type_str.upper())
