from __future__ import annotations

import subprocess

from ..nlu.intents import Intent, IntentType
from ..utils import win32
from .base import BaseExecutor, ExecutionResult

DOWN_WORDS = ("уменьш", "снизи", "убав", "down", "decrease", "lower")

PYCAW_HINT = "Управление звуком недоступно: установите pycaw и comtypes."


class SystemExecutor(BaseExecutor):
    handled = frozenset(
        {
            IntentType.SET_VOLUME,
            IntentType.CHANGE_VOLUME,
            IntentType.TOGGLE_MUTE,
            IntentType.SHUTDOWN,
            IntentType.RESTART,
            IntentType.SLEEP,
            IntentType.LOCK,
            IntentType.CANCEL_POWER,
        }
    )

    def execute(self, intent: Intent) -> ExecutionResult:
        handlers = {
            IntentType.SET_VOLUME: self._set_volume,
            IntentType.CHANGE_VOLUME: self._change_volume,
            IntentType.TOGGLE_MUTE: self._toggle_mute,
            IntentType.SHUTDOWN: lambda item: self._power("shutdown", item),
            IntentType.RESTART: lambda item: self._power("restart", item),
            IntentType.SLEEP: self._sleep,
            IntentType.LOCK: self._lock,
            IntentType.CANCEL_POWER: self._cancel_power,
        }
        return handlers[intent.type](intent)

    @staticmethod
    def _volume_interface():
        try:
            from pycaw.pycaw import AudioUtilities
        except ImportError:
            return None, PYCAW_HINT
        try:
            device = AudioUtilities.GetSpeakers()
            if device is None:
                return None, "Управление звуком недоступно: не найдено устройство вывода."
            endpoint = getattr(device, "EndpointVolume", None)
            if endpoint is not None:
                return endpoint, ""
            from ctypes import POINTER, cast

            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import IAudioEndpointVolume

            interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            return cast(interface, POINTER(IAudioEndpointVolume)), ""
        except Exception as exc:
            return None, f"Управление звуком недоступно: {exc}"

    def _set_volume(self, intent: Intent) -> ExecutionResult:
        try:
            level = max(0, min(100, int(intent.entities.get("level", 50))))
        except (TypeError, ValueError):
            return ExecutionResult(success=False, message="Не удалось распознать уровень громкости.")
        volume, error = self._volume_interface()
        if volume is None:
            return ExecutionResult(success=False, message=error)
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return ExecutionResult(success=True, message=f"Громкость {level} процентов.")

    def _change_volume(self, intent: Intent) -> ExecutionResult:
        raw_direction = str(intent.entities.get("direction", "увеличь")).lower()
        direction = "down" if any(word in raw_direction for word in DOWN_WORDS) else "up"
        try:
            step = int(intent.entities.get("step", 10))
        except (TypeError, ValueError):
            step = 10
        volume, error = self._volume_interface()
        if volume is None:
            return ExecutionResult(success=False, message=error)
        current = volume.GetMasterVolumeLevelScalar()
        delta = step / 100.0 if direction == "up" else -step / 100.0
        new_level = max(0.0, min(1.0, current + delta))
        volume.SetMasterVolumeLevelScalar(new_level, None)
        return ExecutionResult(success=True, message=f"Громкость {round(new_level * 100)} процентов.")

    def _toggle_mute(self, intent: Intent) -> ExecutionResult:
        raw = str(intent.entities.get("mute", "выключи")).lower()
        mute = not any(word in raw for word in ("включи", "верни", "восстанови", "unmute", "turn on"))
        volume, error = self._volume_interface()
        if volume is None:
            return ExecutionResult(success=False, message=error)
        volume.SetMute(1 if mute else 0, None)
        return ExecutionResult(success=True, message="Звук выключен." if mute else "Звук включен.")

    @staticmethod
    def _power(action: str, intent: Intent) -> ExecutionResult:
        if action == "shutdown":
            args = ["shutdown", "/s", "/t", "60"]
            message = "Компьютер выключится через 60 секунд. Скажите 'отмена' для отмены."
        else:
            args = ["shutdown", "/r", "/t", "60"]
            message = "Перезагрузка через 60 секунд. Скажите 'отмена' для отмены."
        try:
            completed = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=15,
                encoding=win32.console_encoding(),
                errors="replace",
            )
            if completed.returncode != 0:
                output = (completed.stdout or completed.stderr or "").strip()
                return ExecutionResult(success=False, message=output or "Не удалось запланировать выключение/перезагрузку.")
        except Exception as exc:
            return ExecutionResult(success=False, message=f"Не удалось запланировать выключение/перезагрузку: {exc}")
        return ExecutionResult(success=True, message=message)

    @staticmethod
    def _sleep(intent: Intent) -> ExecutionResult:
        try:
            completed = subprocess.run(
                ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
                capture_output=True,
                timeout=15,
            )
        except Exception as exc:
            return ExecutionResult(success=False, message=f"Не удалось перевести компьютер в спящий режим: {exc}")
        if completed.returncode != 0:
            return ExecutionResult(success=False, message="Не удалось перевести компьютер в спящий режим.")
        return ExecutionResult(success=True, message="Спящий режим включен.")

    @staticmethod
    def _lock(intent: Intent) -> ExecutionResult:
        try:
            subprocess.run(
                ["rundll32.exe", "user32.dll,LockWorkStation"],
                capture_output=True,
                timeout=15,
            )
        except Exception as exc:
            return ExecutionResult(success=False, message=f"Не удалось заблокировать компьютер: {exc}")
        return ExecutionResult(success=True, message="Рабочая станция заблокирована.")

    @staticmethod
    def _cancel_power(intent: Intent) -> ExecutionResult:
        completed = subprocess.run(
            ["shutdown", "/a"],
            capture_output=True,
            text=True,
            timeout=15,
            encoding=win32.console_encoding(),
            errors="replace",
        )
        if completed.returncode == 0:
            return ExecutionResult(success=True, message="Запланированное действие отменено.")
        return ExecutionResult(success=False, message="Нечего отменять.")
