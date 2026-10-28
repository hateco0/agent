from __future__ import annotations

import re
import shlex
from dataclasses import dataclass

from ..core.settings import SecuritySettings
from ..nlu.intents import Intent, IntentType

DANGEROUS_INTENTS = frozenset(
    {
        IntentType.SHUTDOWN,
        IntentType.RESTART,
        IntentType.SLEEP,
    }
)

SHELL_SEPARATORS = re.compile(r"[&|;><`\n\r]|\$\(")


@dataclass
class GuardVerdict:
    allowed: bool
    needs_confirmation: bool = False
    message: str = ""


class SecurityGuard:
    def __init__(self, settings):
        self.settings = settings
        self._whitelist = set()
        try:
            sec = getattr(settings, "security", None)
            if sec is None and hasattr(settings, "shell_whitelist"):
                wl = getattr(settings, "shell_whitelist")
            elif sec is not None:
                wl = getattr(sec, "shell_whitelist", None)
            else:
                wl = None
            if wl:
                self._whitelist = {str(item).lower().removesuffix(".exe") for item in wl}
        except Exception:
            self._whitelist = set()

    def check(self, intent: Intent) -> GuardVerdict:
        if intent.type is IntentType.SHELL_COMMAND:
            return self._check_shell(intent)
        if intent.type in DANGEROUS_INTENTS and self._settings.confirm_dangerous:
            return GuardVerdict(
                allowed=False,
                needs_confirmation=True,
                message=f"Подтвердите действие: {intent.raw_text}. Скажите да или нет.",
            )
        return GuardVerdict(allowed=True)

    def _check_shell(self, intent: Intent) -> GuardVerdict:
        command = str(intent.entities.get("command", "")).strip()
        if not command:
            return GuardVerdict(allowed=False, message="Пустая команда.")
        parts: list[str] = []
        try:
            # shlex.split корректно разбирает кавычки, но backtick/subshell лучше проверять отдельно
            raw_parts = [part.strip() for part in SHELL_SEPARATORS.split(command)]
            raw_parts = [part for part in raw_parts if part]
            for part in raw_parts:
                try:
                    parts.extend(shlex.split(part, posix=False))
                except ValueError:
                    parts.append(part)
            # Если после кавычек/сплита ничего не осталось — проверяем исходный текст
            if not parts:
                parts = raw_parts
        except Exception:
            parts = [part.strip() for part in SHELL_SEPARATORS.split(command)]
            parts = [part for part in parts if part]
        if not parts:
            return GuardVerdict(allowed=False, message="Пустая команда.")
        for part in parts:
            token = part.strip().strip('"').strip("'")
            if not token:
                continue
            if token in {"&", "|", ";", "&&", "||"}:
                continue
            head = token.split()[0].lower().removesuffix(".exe")
            if head not in self._whitelist:
                return GuardVerdict(
                    allowed=False,
                    message=f"Команда '{head}' запрещена политикой безопасности.",
                )
        return GuardVerdict(allowed=True)
