from __future__ import annotations

import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

LOG_FILE = os.path.join("data", "agent_debug.log")


class LogsView(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Логи", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        btns = ctk.CTkFrame(self)
        btns.grid(row=0, column=0, sticky="e", padx=20, pady=(20, 10))
        ctk.CTkButton(btns, text="Обновить", width=90, command=self.refresh).grid(row=0, column=0, padx=2)
        ctk.CTkButton(btns, text="Открыть файл", width=110, command=self.open_log).grid(row=0, column=1, padx=2)
        ctk.CTkButton(btns, text="Копировать последние 100", width=190, command=self.copy_last).grid(row=0, column=2, padx=2)

        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        self.text = tk.Text(frame, wrap="word", bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scrollbar.set)
        self.refresh()
        self.after(2000, self.auto_refresh)

    def read_log(self):
        try:
            if not os.path.exists(LOG_FILE):
                return "Лог-файл не найден: data/agent_debug.log"
            with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            return "".join(lines[-200:])
        except Exception as e:
            return f"Ошибка чтения лога: {e}"

    def refresh(self):
        try:
            self.text.delete("1.0", "end")
            self.text.insert("1.0", self.read_log())
            self.text.see("end")
        except Exception:
            pass

    def auto_refresh(self):
        try:
            self.refresh()
        except Exception:
            pass
        self.after(2000, self.auto_refresh)

    def open_log(self):
        try:
            os.startfile(os.path.abspath(LOG_FILE))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def copy_last(self):
        try:
            if not os.path.exists(LOG_FILE):
                return
            with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            txt = "".join(lines[-100:])
            self.clipboard_clear()
            self.clipboard_append(txt)
            messagebox.showinfo("Логи", "Скопировано последние 100 строк")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

