from __future__ import annotations

import threading
import time
from typing import Callable

try:
    import numpy as np
    import sounddevice as sd
except Exception:
    np = None  # type: ignore
    sd = None  # type: ignore

try:
    from core import logging_setup
    log = logging_setup.log
except Exception:
    def log(*args, **kwargs):  # type: ignore
        pass


class MicTester:
    def __init__(self, device: int | None = None, device_name: str | None = None, callback: Callable[[float], None] | None = None, on_level: Callable[[float], None] | None = None, enable_monitor: bool = False):
        self.device = device
        self.device_name = device_name
        self.callback = callback
        self.on_level = on_level or callback
        self.enable_monitor = bool(enable_monitor)
        self.stream_in = None
        self.stream_out = None
        self.running = False
        self._lock = threading.Lock()

    def start(self):
        if self.running:
            return True
        if sd is None or np is None:
            log.warning("MicTester: sounddevice/numpy missing")
            return False
        try:
            dev_in = self.device
            dev_out = None
            try:
                from core import audio_devices
                if dev_in is None and self.device_name:
                    for d in audio_devices.list_input_devices():
                        if d.get("name") == self.device_name and d.get("index") is not None:
                            dev_in = int(d["index"])
                            break
                if dev_in is None:
                    dev_in = audio_devices.get_default_input()
                dev_out = audio_devices.get_default_output()
            except Exception as e:
                log.debug(f"MicTester dev resolve err: {e}")
            sr = 44100
            try:
                if dev_in is not None:
                    di = sd.query_devices(dev_in)
                    if di.get("default_samplerate"):
                        sr = int(di["default_samplerate"])
            except Exception:
                pass

            def _cb(indata, outdata, frames, time_info, status):
                if not self.running:
                    return
                try:
                    rms = float(np.sqrt(np.mean(indata ** 2)))
                    lvl = min(1.0, rms * 12.0)
                    if self.on_level:
                        try:
                            self.on_level(lvl)
                        except Exception:
                            pass
                    if self.enable_monitor and outdata is not None:
                        try:
                            outdata[:] = indata
                        except Exception:
                            pass
                except Exception:
                    pass

            if self.enable_monitor and dev_out is not None:
                self.stream_in = sd.InputStream(device=dev_in, channels=1, samplerate=sr, blocksize=1024, callback=_cb)
                self.stream_out = sd.OutputStream(device=dev_out, channels=1, samplerate=sr, blocksize=1024)
                self.stream_in.start()
                self.stream_out.start()
            else:
                def _cb_in(indata, frames, time_info, status):
                    _cb(indata, None, frames, time_info, status)
                self.stream_in = sd.InputStream(device=dev_in, channels=1, samplerate=sr, blocksize=1024, callback=_cb_in)
                self.stream_in.start()
            self.running = True
            log.info(f"MicTester started in={dev_in} out={dev_out} mon={self.enable_monitor}")
            return True
        except Exception as e:
            log.exception(f"MicTester start err: {e}")
            raise

    def stop(self):
        self.running = False
        try:
            if self.stream_in is not None:
                try:
                    self.stream_in.stop()
                    self.stream_in.close()
                except Exception:
                    pass
                self.stream_in = None
        except Exception:
            pass
        try:
            if self.stream_out is not None:
                try:
                    self.stream_out.stop()
                    self.stream_out.close()
                except Exception:
                    pass
                self.stream_out = None
        except Exception:
            pass
        log.debug("MicTester stopped")
