from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

from core import db
from voice_os_agent.nlu.intents import IntentType
from voice_os_agent.nlu.parser import IntentParser


class CommandsView(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self.parser = IntentParser(settings=app.settings)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        ctk.CTkLabel(header, text="Команды", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        ctk.CTkButton(header, text="Добавить команду", command=self.add_command).pack(side="right", padx=10)
        ctk.CTkButton(header, text="Обновить", command=self.refresh).pack(side="right", padx=5)

        test_frame = ctk.CTkFrame(self)
        test_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        test_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(test_frame, text="Тест команды:").grid(row=0, column=0, padx=10)
        self.test_entry = ctk.CTkEntry(test_frame)
        self.test_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ctk.CTkButton(test_frame, text="Протестировать", command=self.test_command).grid(row=0, column=2, padx=10)
        self.test_result = ctk.CTkLabel(test_frame, text="")
        self.test_result.grid(row=1, column=0, columnspan=3, sticky="w", padx=10)

        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

        columns = ("id", "type", "trigger", "intent", "entities", "desc")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=20)
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Тип")
        self.tree.heading("trigger", text="Триггер")
        self.tree.heading("intent", text="Intent")
        self.tree.heading("entities", text="Сущности")
        self.tree.heading("desc", text="Описание")
        self.tree.column("id", width=40)
        self.tree.column("type", width=80)
        self.tree.column("trigger", width=200)
        self.tree.column("intent", width=120)
        self.tree.column("entities", width=200)
        self.tree.column("desc", width=250)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<Double-1>", lambda e: self.edit_command())

        actions = ctk.CTkFrame(self)
        actions.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        ctk.CTkButton(actions, text="Удалить", command=self.delete_command).pack(side="right", padx=10)

        self.refresh()

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in db.db.get_built_in():
            self.tree.insert("", "end", values=(row["id"], "Встроенная", row["pattern"][:60], row["intent_type"], "", ""))
        cur = db.db._conn.cursor()
        cur.execute("SELECT * FROM custom_commands ORDER BY priority ASC")
        for row in cur.fetchall():
            r = dict(row)
            self.tree.insert("", "end", values=(r["id"], "Пользовательская", r["trigger_text"], r["intent_type"], r["entities_json"], r["description"]))

    def test_command(self) -> None:
        text = self.test_entry.get().strip()
        if not text:
            return
        intent = self.parser.parse(text)
        self.test_result.configure(text=f"Intent: {intent.type.name} | Сущности: {intent.entities} | raw: {intent.raw_text}")

    def add_command(self) -> None:
        self.form_window(mode="add")

    def edit_command(self) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        if values[1] == "Встроенная":
            return
        self.form_window(mode="edit", cmd_id=int(values[0]), values=values)

    def form_window(self, mode: str, cmd_id: int | None = None, values: tuple | None = None) -> None:
        win = ctk.CTkToplevel(self)
        win.title("Добавить/Редактировать команду" if mode == "add" else "Редактировать команду")
        win.geometry("520x420")
        win.grab_set()

        ctk.CTkLabel(win, text="Триггер (фраза):").pack(anchor="w", padx=20, pady=(20, 0))
        trigger = ctk.CTkEntry(win)
        trigger.pack(fill="x", padx=20)

        ctk.CTkLabel(win, text="IntentType:").pack(anchor="w", padx=20, pady=(10, 0))
        intent_var = ctk.StringVar(value="OPEN_APP")
        intents = [t.name for t in IntentType if t.name != "UNKNOWN"]
        intent_menu = ctk.CTkOptionMenu(win, values=intents, variable=intent_var)
        intent_menu.pack(fill="x", padx=20)

        ctk.CTkLabel(win, text="Сущности JSON (например {'app':'discord'}):").pack(anchor="w", padx=20, pady=(10, 0))
        entities = ctk.CTkEntry(win)
        entities.pack(fill="x", padx=20)
        entities.insert(0, "{}")

        ctk.CTkLabel(win, text="Описание:").pack(anchor="w", padx=20, pady=(10, 0))
        desc = ctk.CTkEntry(win)
        desc.pack(fill="x", padx=20)

        ctk.CTkLabel(win, text="Приоритет (меньше = выше приоритет):").pack(anchor="w", padx=20, pady=(10, 0))
        priority = ctk.CTkEntry(win)
        priority.pack(fill="x", padx=20)
        priority.insert(0, "10")

        if mode == "edit" and values:
            trigger.insert(0, values[2])
            intent_var.set(values[3])
            entities.delete(0, "end")
            entities.insert(0, values[4] if values[4] else "{}")
            desc.insert(0, values[5])
            cur = db.db._conn.cursor()
            cur.execute("SELECT priority FROM custom_commands WHERE id=?", (cmd_id,))
            row = cur.fetchone()
            if row:
                priority.delete(0, "end")
                priority.insert(0, str(row[0]))

        def save() -> None:
            import json
            try:
                ent = json.loads(entities.get() or "{}")
            except Exception:
                messagebox.showerror("Ошибка", "Неверный JSON сущностей")
                return
            if mode == "add":
                db.db.add_custom_command(trigger.get(), intent_var.get(), ent, desc.get(), int(priority.get() or 100))
            else:
                cur = db.db._conn.cursor()
                cur.execute("UPDATE custom_commands SET trigger_text=?,intent_type=?,entities_json=?,description=?,priority=? WHERE id=?", (trigger.get().lower(), intent_var.get(), json.dumps(ent, ensure_ascii=False), desc.get(), int(priority.get() or 100), cmd_id))
                db.db._conn.commit()
            win.destroy()
            self.app.parser = IntentParser(settings=self.app.settings)
            self.refresh()

        ctk.CTkButton(win, text="Сохранить", command=save).pack(pady=20)

    def delete_command(self) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        if values[1] == "Встроенная":
            messagebox.showinfo("Инфо", "Встроенные команды нельзя удалить")
            return
        if messagebox.askyesno("Подтверждение", "Удалить команду?"):
            db.db.delete_custom_command(int(values[0]))
            self.refresh()
