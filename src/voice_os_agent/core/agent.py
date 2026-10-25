from __future__ import annotations

from typing import Any

from ..executors.base import ExecutionResult, ExecutorRegistry
from ..nlu.intents import Intent, IntentType
from ..nlu.parser import IntentParser
from ..security.guard import SecurityGuard

CONFIRM_YES = {"да", "yes", "ага", "подтверждаю", "давай", "точно", "конечно"}
CONFIRM_NO = {"нет", "no", "отмена", "отменить", "не надо", "отбой"}


class VoiceAgent:
    def __init__(
        self,
        parser: IntentParser,
        registry: ExecutorRegistry,
        guard: SecurityGuard,
        speaker: Any | None = None,
    ) -> None:
        self._parser = parser
        self._registry = registry
        self._guard = guard
        self._speaker = speaker
        self._pending: Intent | None = None

    @property
    def awaiting_confirmation(self) -> bool:
        return self._pending is not None

    def handle(self, text: str) -> ExecutionResult:
        cleaned = self._normalize(text)
        if not cleaned:
            return ExecutionResult(success=False, message="Пустая команда.")
        if self._pending is not None:
            return self._resolve_confirmation(cleaned)
        intent = self._parser.parse(cleaned)
        if intent.type is IntentType.UNKNOWN:
            return ExecutionResult(success=False, message="Команда не распознана.")
        verdict = self._guard.check(intent)
        if not verdict.allowed:
            if verdict.needs_confirmation:
                self._pending = intent
                return ExecutionResult(
                    success=False,
                    message=verdict.message,
                    needs_confirmation=True,
                )
            return ExecutionResult(success=False, message=verdict.message)
        return self._registry.execute(intent)

    def speak(self, text: str) -> None:
        if self._speaker is not None:
            self._speaker.speak(text)

    def cancel_pending(self) -> None:
        self._pending = None

    def _resolve_confirmation(self, cleaned: str) -> ExecutionResult:
        intent = self._pending
        self._pending = None
        if intent is None:
            return ExecutionResult(success=False, message="Нет действия для подтверждения.")
        if cleaned in CONFIRM_YES:
            return self._registry.execute(intent)
        if cleaned in CONFIRM_NO:
            return ExecutionResult(success=True, message="Действие отменено.")
        self._pending = intent
        return ExecutionResult(
            success=False,
            message="Скажите да или нет.",
            needs_confirmation=True,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.strip().lower().split())
