from __future__ import annotations


class Speaker:
    def __init__(self, enabled: bool = True, rate: int = 180, voice_hint: str = "ru") -> None:
        self.enabled = enabled
        self._engine = None
        if enabled:
            self._init_engine(rate, voice_hint)

    def _init_engine(self, rate: int, voice_hint: str) -> None:
        try:
            import pyttsx3
        except ImportError:
            self.enabled = False
            return
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", rate)
            self._select_voice(engine, voice_hint)
            self._engine = engine
        except Exception:
            self.enabled = False

    @staticmethod
    def _select_voice(engine, voice_hint: str) -> None:
        hint = voice_hint.lower()
        for voice in engine.getProperty("voices") or []:
            haystack = f"{getattr(voice, 'id', '')} {getattr(voice, 'name', '')}".lower()
            if hint and hint in haystack:
                engine.setProperty("voice", voice.id)
                return

    def speak(self, text: str) -> None:
        if not self.enabled or not text or self._engine is None:
            return
        try:
            self._engine.say(text)
            self._engine.runAndWait()
        except Exception:
            self.enabled = False
