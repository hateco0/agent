from __future__ import annotations

from ..core.agent import VoiceAgent

EXIT_WORDS = {"выход", "exit", "quit", "стоп", "выключись"}


class TextConsole:
    def __init__(self, agent: VoiceAgent) -> None:
        self._agent = agent

    def run(self) -> None:
        print("Текстовый режим. Введите команду. Для выхода: выход")
        while True:
            try:
                line = input("> ")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            cleaned = line.strip()
            if not cleaned:
                continue
            if cleaned.lower() in EXIT_WORDS:
                print("До встречи.")
                break
            result = self._agent.handle(cleaned)
            prefix = "OK" if result.success else "ERROR"
            print(f"{prefix}: {result.message}")
