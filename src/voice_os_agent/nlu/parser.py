from __future__ import annotations

import re

from ..core.settings import Settings
from .custom_parser import CustomCommandParser
from .intents import Intent, IntentType
from .llm import LLMParser
from .patterns import PATTERN_SPECS


class IntentParser:
    def __init__(self, specs: tuple[tuple[str, IntentType], ...] = PATTERN_SPECS, settings: Settings | None = None) -> None:
        self._compiled = [(re.compile(pattern, re.IGNORECASE), intent_type) for pattern, intent_type in specs]
        self._llm = LLMParser(settings.llm if settings else None)
        self._settings = settings
        self._custom = CustomCommandParser()

    def parse(self, text: str) -> Intent:
        cleaned = self._normalize(text)
        if not cleaned:
            return Intent(type=IntentType.UNKNOWN, raw_text="")
        # Кастомные команды имеют приоритет
        self._custom.reload()
        custom = self._custom.match(cleaned)
        if custom is not None:
            return custom
        for regex, intent_type in self._compiled:
            match = regex.match(cleaned)
            if match:
                entities = {key: value for key, value in match.groupdict().items() if value is not None}
                return Intent(type=intent_type, raw_text=cleaned, entities=entities)
        intent = self._heuristic(cleaned)
        if intent is not None:
            return intent
        if self._llm.is_available():
            llm_intent = self._llm.parse(cleaned)
            if llm_intent is not None:
                return llm_intent
        return Intent(type=IntentType.UNKNOWN, raw_text=cleaned)

    def _heuristic(self, cleaned: str) -> Intent | None:
        # Пытаемся догадаться по ключевым словам
        if re.search(r"\b(откр\w*|запус\w*|включ\w*)\b.*\b(папк\w*|проводник)\b", cleaned):
            for name in ("рабочий стол", "мои документы", "документы", "загрузки", "корзину", "desktop", "documents", "downloads"):
                if name in cleaned:
                    return Intent(type=IntentType.OPEN_PATH, raw_text=cleaned, entities={"path": name})
            m = re.search(r"(папк\w*|каталог\w*|директор\w*)\s+(.+)$", cleaned)
            if m:
                path = m.group(2).strip()
                if path and path not in ("папку", "каталог", "директорию"):
                    return Intent(type=IntentType.OPEN_PATH, raw_text=cleaned, entities={"path": path})
        # открытие приложения/файла
        if re.search(r"\b(откр\w*|запус\w*|включ\w*)\b", cleaned) and not re.search(r"\b(папк\w*|каталог\w*|директор\w*|проводник)\b", cleaned):
            m = re.search(r"(?:откр\w*|запус\w*|включ\w*)\s+(?:мне\s+|бы\s+)?(.+)$", cleaned)
            if m:
                app = m.group(1).strip()
                if app and app not in ("папку", "каталог", "директорию", "проводник", "команду"):
                    # если это известный путь
                    for name in ("рабочий стол", "мои документы", "документы", "загрузки", "корзину"):
                        if name == app:
                            return Intent(type=IntentType.OPEN_PATH, raw_text=cleaned, entities={"path": name})
                    return Intent(type=IntentType.OPEN_APP, raw_text=cleaned, entities={"app": app})
        if re.search(r"\b(закр\w*|заверш\w*)\b.*\b(прогр\w*|прилож\w*)\b", cleaned) or re.search(r"\b(убей|прибей)\b", cleaned):
            m = re.search(r"(?:приложение|программу|программы|програма|прогу)\s+(.+)$", cleaned)
            if m:
                return Intent(type=IntentType.CLOSE_APP, raw_text=cleaned, entities={"app": m.group(1).strip()})
        if re.search(r"\b(громк\w*)\b", cleaned):
            m = re.search(r"(\d{1,3})", cleaned)
            if m:
                if re.search(r"(уменьш\w*|сниз\w*|убав\w*|потих\w*|тише|down|lower|decrease)", cleaned):
                    return Intent(type=IntentType.CHANGE_VOLUME, raw_text=cleaned, entities={"direction": "уменьши", "step": m.group(1)})
                if re.search(r"(увелич\w*|повысь\w*|прибав\w*|добав\w*|громче|погромч\w*|up|raise|increase)", cleaned):
                    return Intent(type=IntentType.CHANGE_VOLUME, raw_text=cleaned, entities={"direction": "увеличь", "step": m.group(1)})
                return Intent(type=IntentType.SET_VOLUME, raw_text=cleaned, entities={"level": m.group(1)})
        if re.search(r"\b(уменьш\w*\s+громк\w*|сниз\w*\s+громк\w*)\b", cleaned):
            m = re.search(r"(\d{1,3})", cleaned)
            return Intent(type=IntentType.CHANGE_VOLUME, raw_text=cleaned, entities={"direction": "уменьши", "step": m.group(1) if m else "10"})
        if re.search(r"\b(увелич\w*\s+громк\w*|повысь\w*\s+громк\w*)\b", cleaned):
            m = re.search(r"(\d{1,3})", cleaned)
            return Intent(type=IntentType.CHANGE_VOLUME, raw_text=cleaned, entities={"direction": "увеличь", "step": m.group(1) if m else "10"})
        if re.search(r"\b(выключ\w*\s+звук|без\s+звука|заглуш\w*|выруби\s+звук)\b", cleaned):
            return Intent(type=IntentType.TOGGLE_MUTE, raw_text=cleaned, entities={"mute": "выключи"})
        if re.search(r"\b(включ\w*\s+звук|верн\w*\s+звук)\b", cleaned):
            return Intent(type=IntentType.TOGGLE_MUTE, raw_text=cleaned, entities={"mute": "включи"})
        if re.search(r"\b(выключ\w*\s+(комп\w*|пк|машин\w*|систем\w*))\b", cleaned) or cleaned in ("заверши работу", "выключи работу"):
            return Intent(type=IntentType.SHUTDOWN, raw_text=cleaned)
        if re.search(r"\b(перезагр\w*)\b", cleaned):
            return Intent(type=IntentType.RESTART, raw_text=cleaned)
        if re.search(r"\b(спящ\w*|сон|усн\w*)\b", cleaned):
            return Intent(type=IntentType.SLEEP, raw_text=cleaned)
        if re.search(r"\b(заблок\w*)\b", cleaned):
            return Intent(type=IntentType.LOCK, raw_text=cleaned)
        if re.search(r"\b(отмен\w*)\b", cleaned):
            return Intent(type=IntentType.CANCEL_POWER, raw_text=cleaned)
        if re.search(r"\b(скриншот|сним\w*\s+экран\w*)\b", cleaned):
            return Intent(type=IntentType.SCREENSHOT, raw_text=cleaned)
        if re.search(r"\b(сверн\w*\s+все|минимиз\w*)\b", cleaned):
            return Intent(type=IntentType.MINIMIZE_ALL, raw_text=cleaned)
        if re.search(r"\b(покаж\w*\s+рабоч\w*\s+стол|рабоч\w*\s+стол.*покаж\w*|покаж\w*.*рабоч\w*\s+стол)\b", cleaned):
            # при наличии явного "открой" приоритет папке
            if re.search(r"\b(откр\w*)\b", cleaned):
                return Intent(type=IntentType.OPEN_PATH, raw_text=cleaned, entities={"path": "рабочий стол"})
            return Intent(type=IntentType.SHOW_DESKTOP, raw_text=cleaned)
        if re.search(r"\b(откр\w*\s+рабоч\w*\s+стол)\b", cleaned):
            return Intent(type=IntentType.OPEN_PATH, raw_text=cleaned, entities={"path": "рабочий стол"})
        if re.search(r"\b(выполни|выполнить|запусти\s+команду|введи)\b", cleaned):
            m = re.search(r"(?:выполни|выполнить|запусти\s+команду|введи)\s+(.+)$", cleaned)
            if m and m.group(1).strip():
                return Intent(type=IntentType.SHELL_COMMAND, raw_text=cleaned, entities={"command": m.group(1).strip()})
        return None

    @staticmethod
    def _normalize(text: str) -> str:
        cleaned = text.replace("\ufeff", "").strip().lower()
        cleaned = cleaned.rstrip("?!.,;:")
        cleaned = re.sub(r"[^\w\s\\/:.-]", " ", cleaned)
        return " ".join(cleaned.split())
