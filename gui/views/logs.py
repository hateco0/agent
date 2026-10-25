from __future__ import annotations

import customtkinter as ctk
from tkinter import ttk

from core import db


class LogsView(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Логи", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        columns = ("time", "level", "message")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree.heading("time", text="Время")
        self.tree.heading("level", text="Уровень")
        self.tree.heading("message", text="Сообщение")
        self.tree.column("time", width=80)
        self.tree.column("level", width=80)
        self.tree.column("message", width=700)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        ctk.CTkButton(self, text="Обновить", command=self.refresh).grid(row=2, column=0, sticky="e", padx=20, pady=10)
        self.refresh()

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in db.db.get_logs():
            self.tree.insert("", "end", values=(row["ts"], row["level"], row["message"]))
