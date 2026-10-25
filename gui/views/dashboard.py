from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from core import audio_devices
from core.mic_tester import MicTester


class Dashboard(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.mic_tester = None
        self.muted = False

        ctk.CTkLabel(self, text="Дашборд", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        status_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.status_lbl = ctk.CTkLabel(status_frame, text="Статус агента: Остановлен")
        self.status_lbl.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.mic_status = ctk.CTkLabel(status_frame, text="Микрофон: включен")
        self.mic_status.grid(row=0, column=1, padx=10, pady=10)
        self.ollama_status = ctk.CTkLabel(status_frame, text="Ollama: проверка...")
        self.ollama_status.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        mic_frame = ctk.CTkFrame(self)
        mic_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        mic_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(mic_frame, text="Микрофон", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=5)
        ctk.CTkLabel(mic_frame, text="Устройство:").grid(row=1, column=0, padx=10)
        self.mic_combo = ctk.CTkComboBox(mic_frame, values=[d["name"] for d in audio_devices.list_input_devices()])
        self.mic_combo.grid(row=1, column=1, sticky="ew", padx=10)
        self.test_mic_btn = ctk.CTkButton(mic_frame, text="Проверить микрофон", width=160, command=self.toggle_mic_test)
        self.test_mic_btn.grid(row=1, column=2, padx=10)
        ctk.CTkLabel(mic_frame, text="Уровень:").grid(row=2, column=0, padx=10, pady=5)
        self.level_bar = ctk.CTkProgressBar(mic_frame)
        self.level_bar.set(0)
        self.level_bar.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        self.mute_btn = ctk.CTkButton(mic_frame, text="Вкл/Выкл микрофон", width=160, command=self.toggle_mute)
        self.mute_btn.grid(row=2, column=2, padx=10, pady=5)

        ctrl_frame = ctk.CTkFrame(self)
        ctrl_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        self.start_btn = ctk.CTkButton(ctrl_frame, text="Запустить агента", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=10, pady=10)
        self.stop_btn = ctk.CTkButton(ctrl_frame, text="Остановить агента", command=self.stop, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=10, pady=10)

        test_frame = ctk.CTkFrame(self)
        test_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(10, 20))
        test_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(test_frame, text="Быстрый тест команды:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=5)
        self.cmd_entry = ctk.CTkEntry(test_frame)
        self.cmd_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)
        ctk.CTkButton(test_frame, text="Выполнить", command=self.run_cmd).grid(row=1, column=2, padx=10)
        self.result_lbl = ctk.CTkLabel(test_frame, text="")
        self.result_lbl.grid(row=2, column=0, columnspan=3, sticky="w", padx=10, pady=5)

        self.check_ollama()

    def toggle_mic_test(self):
        if self.mic_tester and self.mic_tester.running:
            try:
                self.mic_tester.stop()
            except Exception:
                pass
            self.mic_tester = None
            self.test_mic_btn.configure(text="Проверить микрофон")
            self.level_bar.set(0)
            return
        try:
            devs = audio_devices.list_input_devices()
            name = self.mic_combo.get()
            dev_idx = None
            for d in devs:
                if d["name"] == name:
                    dev_idx = d["index"]
                    break
            self.mic_tester = MicTester(device=dev_idx, callback=self._on_level)
            self.mic_tester.start()
            self.test_mic_btn.configure(text="Остановить тест микрофона")
        except Exception as e:
            self.result_lbl.configure(text=f"Ошибка теста микрофона: {e}")

    def _on_level(self, rms: float):
        try:
            val = min(1.0, rms * 8.0)
            self.after(0, lambda v=val: self.level_bar.set(v))
        except Exception:
            pass

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            self.mic_status.configure(text="Микрофон: выключен (MUTE)")
        else:
            self.mic_status.configure(text="Микрофон: включен")

    def start(self):
        self.status_lbl.configure(text="Статус агента: Запущен")
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

    def stop(self):
        self.status_lbl.configure(text="Статус агента: Остановлен")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def run_cmd(self):
        try:
            from voice_os_agent.nlu.parser import IntentParser
            from voice_os_agent.core.settings import Settings
            p = IntentParser(settings=Settings.load())
            text = self.cmd_entry.get()
            intent = p.parse(text)
            self.result_lbl.configure(text=f"{intent.type.name} | {intent.entities}")
        except Exception as e:
            self.result_lbl.configure(text=f"Ошибка: {e}")

    def check_ollama(self):
        try:
            import requests
            r = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
            if r.status_code == 200:
                data = r.json()
                models = [m.get("name") for m in data.get("models", [])]
                if any("qwen2.5:3b-instruct" in m for m in models):
                    self.ollama_status.configure(text="Ollama: подключён | qwen2.5:3b-instruct")
                elif models:
                    self.ollama_status.configure(text=f"Ollama: подключён | {', '.join(models[:2])}")
                else:
                    self.ollama_status.configure(text="Ollama: подключён | моделей нет")
            else:
                self.ollama_status.configure(text="Ollama: ошибка")
        except Exception:
            self.ollama_status.configure(text="Ollama: не подключён")

