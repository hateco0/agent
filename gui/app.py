from __future__ import annotations

import json
import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core import db
from voice_os_agent.app import build_agent
from voice_os_agent.core.settings import Settings
from voice_os_agent.nlu.intents import IntentType
from voice_os_agent.nlu.parser import IntentParser


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("dail_agent")
        self.geometry("1100x700")
        self.minsize(950, 650)
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.settings = Settings.load()
        self.agent = None
        self.parser = IntentParser(settings=self.settings)
        self.running = False
        self.thread = None
        self.tray_icon = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        ctk.CTkLabel(self.sidebar, text="dail_agent", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkLabel(self.sidebar, text="v0.1.0", font=ctk.CTkFont(size=9)).grid(row=1, column=0, padx=20, pady=(0, 10))
        self.buttons = []
        for i, (name, cmd) in enumerate([("Запуск", self.show_dashboard), ("Команды", self.show_commands), ("Исполнители", self.show_executors), ("Настройки", self.show_settings), ("Логи", self.show_logs)]):
            btn = ctk.CTkButton(self.sidebar, text=name, command=cmd)
            btn.grid(row=i + 1, column=0, padx=20, pady=5)
            self.buttons.append(btn)

        ctk.CTkButton(self.sidebar, text="Свернуть в трей", command=self.minimize_to_tray).grid(row=11, column=0, padx=20, pady=(10, 20))

        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        from gui.views.dashboard import Dashboard
        from gui.views.commands import CommandsView
        from gui.views.executors import ExecutorsView
        from gui.views.settings import SettingsView
        from gui.views.logs import LogsView

        for F in (Dashboard, CommandsView, ExecutorsView, SettingsView, LogsView):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_dashboard()
        db.db.scan_built_in()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_frame(self, name: str) -> None:
        self.frames[name].tkraise()

    def show_dashboard(self) -> None:
        self.show_frame("Dashboard")

    def show_commands(self) -> None:
        self.frames["CommandsView"].refresh()
        self.show_frame("CommandsView")

    def show_executors(self) -> None:
        self.frames["ExecutorsView"].refresh()
        self.show_frame("ExecutorsView")

    def show_settings(self) -> None:
        self.show_frame("SettingsView")

    def show_logs(self) -> None:
        self.frames["LogsView"].refresh()
        self.show_frame("LogsView")

    def set_theme(self, mode: str) -> None:
        ctk.set_appearance_mode(mode)

    def minimize_to_tray(self) -> None:
        self.withdraw()
        if self.tray_icon is None:
            image = Image.new("RGB", (64, 64), color=(40, 40, 40))
            draw = ImageDraw.Draw(image)
            draw.ellipse((16, 16, 48, 48), fill=(100, 150, 255))
            menu = pystray.Menu(
                pystray.MenuItem("Показать", lambda: self.after(0, self.show_from_tray)),
                pystray.MenuItem("Выход", lambda: self.after(0, self.quit_app)),
            )
            self.tray_icon = pystray.Icon("dail_agent", image, "dail_agent", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        else:
            try:
                self.tray_icon.visible = True
            except Exception:
                pass

    def show_from_tray(self) -> None:
        try:
            self.tray_icon.visible = False
        except Exception:
            pass
        self.after(0, self.deiconify)

    def quit_app(self) -> None:
        try:
            if self.tray_icon:
                self.tray_icon.stop()
        except Exception:
            pass
        self.destroy()

    def on_close(self) -> None:
        self.minimize_to_tray()
