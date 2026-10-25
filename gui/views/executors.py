from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from voice_os_agent.executors.base import ExecutorRegistry
from voice_os_agent.executors.apps import AppsExecutor
from voice_os_agent.executors.system import SystemExecutor
from voice_os_agent.executors.shell import ShellExecutor
from voice_os_agent.executors.window import WindowExecutor
from voice_os_agent.executors.files import FilesExecutor


class ExecutorsView(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Исполнители", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        columns = ("executor", "intents")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree.heading("executor", text="Исполнитель")
        self.tree.heading("intents", text="Обрабатываемые IntentType")
        self.tree.column("executor", width=200)
        self.tree.column("intents", width=600)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.refresh()

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for exe in [AppsExecutor(), SystemExecutor(), ShellExecutor(), WindowExecutor(), FilesExecutor()]:
            name = exe.__class__.__name__
            intents = ", ".join(sorted([i.name for i in exe.handled]))
            self.tree.insert("", "end", values=(name, intents))
