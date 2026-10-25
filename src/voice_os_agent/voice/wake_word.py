from __future__ import annotations

from .asr import SpeechListener


class WakeWordDetector:
    def __init__(self, keyword: str, listener: SpeechListener) -> None:
        self.keyword = keyword.strip().lower()
        self._listener = listener

    def wait_for_wake_word(self) -> str | None:
        heard = self._listener.listen_once(timeout=None, phrase_limit=3.0)
        if not heard:
            return None
        if self.keyword in heard.lower():
            return heard
        return None
