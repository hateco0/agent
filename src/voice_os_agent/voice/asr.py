from __future__ import annotations

from .microphone import SoundDeviceMicrophone


class SpeechListener:
    def __init__(self, language: str = "ru-RU", device_index: int | None = None, device_name: str | None = None) -> None:
        self.language = language
        self.device_index = device_index
        self.device_name = device_name
        self._recognizer = None
        self._error = ""

    @property
    def error(self) -> str:
        return self._error

    def _ensure_recognizer(self):
        if self._recognizer is not None:
            return self._recognizer
        import speech_recognition as sr

        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True
        try:
            recognizer.energy_threshold = 300
        except Exception:
            pass
        self._recognizer = recognizer
        return recognizer

    def _open_pyaudio_microphone(self):
        try:
            import speech_recognition as sr

            try:
                if self.device_index is not None and self.device_index >= 0:
                    return sr.Microphone(device_index=self.device_index)
                if self.device_name:
                    try:
                        from core import audio_devices

                        for d in audio_devices.list_input_devices():
                            if d.get("name") == self.device_name and d.get("index") is not None:
                                return sr.Microphone(device_index=int(d["index"]))
                    except Exception:
                        pass
            except Exception:
                pass
            return sr.Microphone()
        except Exception:
            return None

    def _open_sounddevice_microphone(self):
        try:
            if self.device_index is not None and self.device_index >= 0:
                return SoundDeviceMicrophone(device=self.device_index)
            if self.device_name:
                try:
                    from core import audio_devices

                    for d in audio_devices.list_input_devices():
                        if d.get("name") == self.device_name and d.get("index") is not None:
                            return SoundDeviceMicrophone(device=int(d["index"]))
                except Exception:
                    pass
            return SoundDeviceMicrophone()
        except Exception:
            return None

    def listen_once(self, timeout: float | None = 6.0, phrase_limit: float = 10.0) -> str | None:
        self._error = ""
        try:
            import speech_recognition as sr
        except Exception as e:
            self._error = f"Нет speech_recognition: {e}"
            return None
        recognizer = self._ensure_recognizer()
        for opener in (self._open_pyaudio_microphone, self._open_sounddevice_microphone):
            try:
                source = opener()
            except Exception as e:
                self._error = str(e)
                continue
            if source is None:
                continue
            try:
                with source as microphone:
                    try:
                        recognizer.adjust_for_ambient_noise(microphone, duration=1.0)
                    except Exception:
                        pass
                    try:
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
                self._error = f"Не удалось распознать: {exc}"
                return None
            self._error = ""
            return text
        if not self._error:
            self._error = "Микрофон недоступен"
        return None


SpeechRecognizer = SpeechListener


SpeechRecognizer = SpeechListener


SpeechRecognizer = SpeechListener
