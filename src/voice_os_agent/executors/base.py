from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..nlu.intents import Intent, IntentType


@dataclass
class ExecutionResult:
    success: bool
    message: str
    needs_confirmation: bool = False


class BaseExecutor(ABC):
    handled: frozenset[IntentType] = frozenset()

    @abstractmethod
    def execute(self, intent: Intent) -> ExecutionResult:
        raise NotImplementedError


class ExecutorRegistry:
    def __init__(self) -> None:
        self._executors: dict[IntentType, BaseExecutor] = {}

    def register(self, executor: BaseExecutor) -> None:
        for intent_type in executor.handled:
            self._executors[intent_type] = executor

    def execute(self, intent: Intent) -> ExecutionResult:
        executor = self._executors.get(intent.type)
        if executor is None:
            return ExecutionResult(
                success=False,
                message=f"Для команды '{intent.type.name}' нет обработчика.",
            )
        try:
            return executor.execute(intent)
        except Exception as exc:
            return ExecutionResult(success=False, message=f"Ошибка выполнения: {exc}")
