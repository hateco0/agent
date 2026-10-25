from __future__ import annotations

from .microphone import SoundDeviceMicrophone


class SpeechListener:
    def __init__(self, language: str = "ru-RU") -> None:
        self.language = language
        self._recognizer = None
        self._error = ""

    @property
    def error(self) -> str:
        """Последняя ошибка захвата звука или распознавания (пусто, если всё в порядке)."""
        return self._error

    def _ensure_recognizer(self):
        if self._recognizer is not None:
            return self._recognizer
        import speech_recognition as sr

        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True
        self._recognizer = recognizer
        return recognizer

    @staticmethod
    def _open_pyaudio_microphone():
        try:
            import speech_recognition as sr

            return sr.Microphone()
        except Exception:
            return None

    @staticmethod
    def _open_sounddevice_microphone():
        try:
            return SoundDeviceMicrophone()
        except Exception:
            return None

    def listen_once(self, timeout: float | None = 5.0, phrase_limit: float = 8.0) -> str | None:
        self._error = ""
        try:
            import speech_recognition as sr
        except ImportError:
            self._error = "Не установлена библиотека SpeechRecognition."
            return None
        recognizer = self._ensure_recognizer()
        for opener in (self._open_pyaudio_microphone, self._open_sounddevice_microphone):
            source = opener()
            if source is None:
                continue
            try:
                with source as microphone:
                    recognizer.adjust_for_ambient_noise(microphone, duration=0.3)
                    audio = recognizer.listen(
                        microphone,
                        timeout=timeout,
                        phrase_time_limit=phrase_limit,
                    )
            except sr.WaitTimeoutError:
                self._error = ""
                return None
            except Exception as exc:
                self._error = f"Микрофон недоступен: {exc}"
                continue
            try:
                text = recognizer.recognize_google(audio, language=self.language)
            except sr.UnknownValueError:
                self._error = "Речь не распознана."
                return None
            except sr.RequestError as exc:
                self._error = f"Сервис распознавания недоступен: {exc}"
                return None
            except Exception as exc:
                self._error = f"Не удалось распознать речь: {exc}"
                return None
            self._error = ""
            return text
        if not self._error:
            self._error = "Микрофон недоступен: не установлен PyAudio или sounddevice."
        return None
