from __future__ import annotations

import time
from typing import Callable

import numpy as np
import sounddevice as sd


class MicTester:
    def __init__(self, device: int | None = None, callback: Callable[[float], None] | None = None):
        self.device = device
        self.callback = callback
        self.stream = None
        self.running = False

    def start(self):
        if self.running:
            return
        try:
            def _cb(indata, frames, time_info, status):
                if status:
                    pass
                try:
                    rms = float(np.sqrt(np.mean(indata**2)))
                    if self.callback:
                        self.callback(rms)
                except Exception:
                    pass

            self.stream = sd.InputStream(device=self.device, channels=1, samplerate=16000, callback=_cb)
            self.stream.start()
            self.running = True
        except Exception as e:
            raise e

    def stop(self):
        try:
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()
                self.stream = None
        except Exception:
            pass
        self.running = False
