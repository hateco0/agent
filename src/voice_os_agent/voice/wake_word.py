from __future__ import annotations

from .asr import SpeechListener

try:
    from core import logging_setup
    log = logging_setup.log
except Exception:
    def log(*args, **kwargs):  # type: ignore
        pass


class WakeWordDetector:
    def __init__(self, keyword: str = "ассистент", listener: SpeechListener | None = None) -> None:
        self.keyword = (keyword or "ассистент").strip().lower()
        self._listener = listener

    def contains_wake(self, text: str) -> bool:
        try:
            if not text:
                return False
            t = text.lower()
            return self.keyword in t
        except Exception:
            return False

    def strip_wake(self, text: str) -> str:
        try:
            if not text:
                return ""
            t = text
            tl = t.lower()
            if self.keyword in tl:
                idx = tl.find(self.keyword)
                cmd = t[idx + len(self.keyword) :].strip()
                cmd = cmd.strip(' ,.:;!?')
                return cmd
            return t.strip()
        except Exception:
            return (text or "").strip()

    def wait_for_wake_word(self, timeout: float | None = None, phrase_limit: float = 4.0) -> str | None:
        try:
            if self._listener is None:
                return None
            heard = self._listener.listen_once(timeout=timeout, phrase_limit=phrase_limit)
            if not heard:
                return None
            if self.contains_wake(heard):
                log.debug(f"WAKE_DETECTED: {heard}")
                return heard
            return None
        except Exception as e:
            log.debug(f"wake err: {e}")
            return None

    def listen_command_after_wake(self, timeout: float = 6.0, phrase_limit: float = 10.0) -> str | None:
        try:
            if self._listener is None:
                return None
            cmd = self._listener.listen_once(timeout=timeout, phrase_limit=phrase_limit)
            if not cmd:
                return None
            log.debug(f"WAKE_CMD: {cmd}")
            return cmd.strip()
        except Exception as e:
            log.debug(f"wake cmd err: {e}")
            return None
