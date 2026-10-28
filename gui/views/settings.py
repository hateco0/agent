from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from core import audio_devices, tts_utils


class SettingsView(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Настройки", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        tabs = ctk.CTkTabview(self)
        tabs.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        tabs.add("Аудио")
        tabs.add("Голос")
        tabs.add("LLM")
        tabs.add("Безопасность")
        tabs.add("Общие")

        # Аудио
        audio = tabs.tab("Аудио")
        audio.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(audio, text="Устройства ввода/вывода", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        ctk.CTkLabel(audio, text="Микрофон:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ins = audio_devices.list_input_devices()
        self.in_combo = ctk.CTkComboBox(audio, values=[d["name"] for d in ins])
        try:
            def_in = audio_devices.get_default_input_name()
            names_in = [d["name"] for d in ins]
            if def_in and def_in in names_in:
                self.in_combo.set(def_in)
            elif ins:
                self.in_combo.set(ins[0]["name"])
        except Exception:
            if ins:
                self.in_combo.set(ins[0]["name"])
        self.in_combo.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(audio, text="Устройство вывода:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        outs = audio_devices.list_output_devices()
        self.out_combo = ctk.CTkComboBox(audio, values=[d["name"] for d in outs])
        try:
            def_out = audio_devices.get_default_output_name()
            names_out = [d["name"] for d in outs]
            if def_out and def_out in names_out:
                self.out_combo.set(def_out)
            elif outs:
                self.out_combo.set(outs[0]["name"])
        except Exception:
            if outs:
                self.out_combo.set(outs[0]["name"])
        self.out_combo.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

        # Голос
        voice = tabs.tab("Голос")
        voice.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(voice, text="Озвучка TTS", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        ctk.CTkLabel(voice, text="Голос:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        vs = tts_utils.list_voices()
        self.voices = vs
        self.voice_combo = ctk.CTkComboBox(voice, values=[v["name"] for v in vs] if vs else ["По умолчанию"])
        if vs:
            self.voice_combo.set(vs[0]["name"])
        self.voice_combo.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(voice, text="Скорость:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.rate = ctk.CTkSlider(voice, from_=120, to=220, number_of_steps=100)
        self.rate.set(getattr(self.app.settings.voice, "tts_rate", 170))
        self.rate.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(voice, text="Громкость:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.vol = ctk.CTkSlider(voice, from_=0.0, to=1.0, number_of_steps=10)
        self.vol.set(getattr(self.app.settings.voice, "tts_volume", 1.0))
        self.vol.grid(row=3, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkButton(voice, text="Протестировать озвучку", command=self.test_voice).grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=10)

        # LLM
        llm = tabs.tab("LLM")
        llm.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(llm, text="Ollama", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        ctk.CTkLabel(llm, text="База URL:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.llm_url = ctk.CTkEntry(llm)
        self.llm_url.insert(0, getattr(self.app.settings.llm, "base_url", "http://127.0.0.1:11434"))
        self.llm_url.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(llm, text="Модель:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.llm_model = ctk.CTkEntry(llm)
        self.llm_model.insert(0, getattr(self.app.settings.llm, "model", "qwen2.5:3b-instruct"))
        self.llm_model.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        self.llm_status = ctk.CTkLabel(llm, text="Статус: проверка...")
        self.llm_status.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        ctk.CTkButton(llm, text="Проверить подключение", command=self.check_llm).grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        self.check_llm()

        # Безопасность
        sec = tabs.tab("Безопасность")
        sec.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(sec, text="Безопасность", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        self.confirm = ctk.CTkSwitch(sec, text="Подтверждать опасные действия")
        self.confirm.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        try:
            if getattr(getattr(self.app.settings, "security", None), "confirm_dangerous", True):
                self.confirm.select()
        except Exception:
            self.confirm.select()

        # Общие
        gen = tabs.tab("Общие")
        gen.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(gen, text="Тема", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        self.theme = ctk.CTkSegmentedButton(gen, values=["Светлая", "Тёмная", "Системная"], command=self.change_theme)
        self.theme.set("Системная")
        self.theme.grid(row=1, column=0, columnspan=2, sticky="w", padx=10)

    def test_voice(self):
        try:
            name = self.voice_combo.get()
            vid = None
            for v in self.voices:
                if v["name"] == name:
                    vid = v["id"]
                    break
            tts_utils.speak_test("Тест озвучки. Проверка голоса агента.", voice_id=vid, rate=int(self.rate.get()), volume=float(self.vol.get()))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def check_llm(self):
        try:
            import requests
            url = self.llm_url.get().rstrip("/") + "/api/tags"
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                data = r.json()
                models = [m.get("name") for m in data.get("models", [])]
                m = self.llm_model.get()
                if any(m in x for x in models):
                    self.llm_status.configure(text=f"Статус: Подключён | Модель найдена: {m}")
                elif models:
                    self.llm_status.configure(text=f"Статус: Подключён | Доступны: {', '.join(models)} | Нужна {m}")
                else:
                    self.llm_status.configure(text="Статус: Подключён | Моделей нет. Нужно скачать: ollama pull " + m)
            else:
                self.llm_status.configure(text=f"Статус: Ошибка {r.status_code}")
        except Exception as e:
            self.llm_status.configure(text=f"Статус: Не подключён ({e})")

    def change_theme(self, value: str):
        mapping = {"Светлая": "light", "Тёмная": "dark", "Системная": "system"}
        self.app.set_theme(mapping.get(value, "system"))

