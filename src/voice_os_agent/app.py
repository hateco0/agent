from __future__ import annotations

import argparse
from pathlib import Path

try:
    from core.logging_setup import log  # noqa: F401
    log.info("app build_agent")
except Exception:
    pass

from .core.agent import VoiceAgent
from .core.settings import Settings
from .executors.apps import AppsExecutor
from .executors.base import ExecutorRegistry
from .executors.files import FilesExecutor
from .executors.shell import ShellExecutor
from .executors.system import SystemExecutor
from .executors.window import WindowExecutor
from .nlu.parser import IntentParser
from .security.guard import SecurityGuard


def build_agent(settings: Settings, speaker=None) -> VoiceAgent:
    registry = ExecutorRegistry()
    registry.register(AppsExecutor())
    registry.register(SystemExecutor())
    registry.register(ShellExecutor())
    registry.register(WindowExecutor())
    registry.register(FilesExecutor())
    return VoiceAgent(
        parser=IntentParser(settings=settings),
        registry=registry,
        guard=SecurityGuard(settings.security),
        speaker=speaker,
    )


def run_text_mode(settings: Settings) -> int:
    from .cli.console import TextConsole

    agent = build_agent(settings)
    TextConsole(agent).run()
    return 0


def run_voice_mode(settings: Settings) -> int:
    from .voice.asr import SpeechListener
    from .voice.tts import Speaker
    from .voice.wake_word import WakeWordDetector

    speaker = Speaker(enabled=settings.voice.enabled, rate=settings.voice.tts_rate)
    agent = build_agent(settings, speaker=speaker)
    listener = SpeechListener(language=settings.voice.asr_language)
    wake = WakeWordDetector(settings.voice.wake_word, listener)

    print(f"Ассистент запущен. Скажите '{settings.voice.wake_word}' для активации.")
    speaker.speak("Ассистент запущен.")
    reported_error = ""

    def report_error() -> None:
        nonlocal reported_error
        if listener.error and listener.error != reported_error:
            reported_error = listener.error
            print(f"Ошибка: {listener.error}")

    try:
        while True:
            if wake.wait_for_wake_word() is None:
                report_error()
                continue
            speaker.speak("Слушаю.")
            command = listener.listen_once(timeout=8.0, phrase_limit=10.0)
            if not command:
                report_error()
                speaker.speak("Не расслышал команду.")
                continue
            result = agent.handle(command)
            speaker.speak(result.message)
            while result.needs_confirmation:
                answer = listener.listen_once(timeout=8.0, phrase_limit=4.0)
                if not answer:
                    report_error()
                    agent.cancel_pending()
                    speaker.speak("Подтверждение не получено. Действие отменено.")
                    break
                result = agent.handle(answer)
                speaker.speak(result.message)
    except KeyboardInterrupt:
        speaker.speak("Ассистент остановлен.")
        return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="voice-agent", description="Голосовой агент управления ОС")
    parser.add_argument("--text", action="store_true", help="Режим текстовых команд")
    parser.add_argument("--config", type=Path, default=None, help="Путь к config.json")
    parser.add_argument("--no-tts", action="store_true", help="Отключить синтез речи")
    args = parser.parse_args(argv)

    settings = Settings.load(args.config)
    settings.text_mode = args.text
    if args.no_tts:
        settings.voice.enabled = False

    if settings.text_mode:
        return run_text_mode(settings)
    return run_voice_mode(settings)


if __name__ == "__main__":
    raise SystemExit(main())
