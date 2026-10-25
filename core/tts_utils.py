from __future__ import annotations

import pyttsx3


def list_voices():
    try:
        engine = pyttsx3.init()
        voices = []
        for v in engine.getProperty("voices"):
            voices.append({"id": v.id, "name": v.name})
        engine.stop()
        return voices
    except Exception:
        return []


def speak_test(text: str = "Тест озвучки. Проверка голоса агента.", voice_id: str | None = None, rate: int = 170, volume: float = 1.0):
    try:
        engine = pyttsx3.init()
        if voice_id:
            engine.setProperty("voice", voice_id)
        engine.setProperty("rate", rate)
        engine.setProperty("volume", volume)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        return True
    except Exception:
        return False
