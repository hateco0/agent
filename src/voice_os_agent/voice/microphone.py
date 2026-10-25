from __future__ import annotations

from typing import Any

try:
    from speech_recognition import AudioSource
except ImportError:  # SpeechRecognition не установлена — модуль всё равно должен импортироваться

    class AudioSource:  # type: ignore[no-redef]
        """Заглушка на случай отсутствия SpeechRecognition."""


class SoundDeviceStream:
    """Поток микрофона с интерфейсом, который ожидает SpeechRecognition."""

    def __init__(
        self,
        sounddevice: Any,
        device: int | None,
        sample_rate: int,
        chunk_size: int,
    ) -> None:
        self._stream = sounddevice.InputStream(
            device=device,
            samplerate=sample_rate,
            blocksize=chunk_size,
            channels=1,
            dtype="int16",
        )
        self._stream.start()

    def read(self, size: int) -> bytes:
        data, _overflowed = self._stream.read(size)
        return data.tobytes()

    def close(self) -> None:
        self._stream.stop()
        self._stream.close()


class SoundDeviceMicrophone(AudioSource):
    """Источник звука для SpeechRecognition без PyAudio (через sounddevice)."""

    def __init__(
        self,
        device: int | None = None,
        sample_rate: int | None = None,
        chunk_size: int = 1024,
    ) -> None:
        self.device = device
        self.SAMPLE_RATE = sample_rate
        self.CHUNK = chunk_size
        self.SAMPLE_WIDTH = 2
        self.stream: SoundDeviceStream | None = None

    def __enter__(self) -> SoundDeviceMicrophone:
        import sounddevice

        sample_rate = self.SAMPLE_RATE
        if sample_rate is None:
            info = sounddevice.query_devices(self.device, kind="input")
            sample_rate = int(info["default_samplerate"]) or 44100
        self.SAMPLE_RATE = sample_rate
        self.stream = SoundDeviceStream(sounddevice, self.device, sample_rate, self.CHUNK)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self.stream is not None:
            self.stream.close()
            self.stream = None
