from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "voice_agent.db"


class Database:
    def __init__(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self.init()

    def init(self) -> None:
        cur = self._conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS built_in_commands(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT,
                intent_type TEXT,
                description TEXT,
                executor TEXT,
                entities_hint TEXT
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS custom_commands(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger_text TEXT UNIQUE,
                intent_type TEXT,
                entities_json TEXT,
                action_type TEXT,
                action_target TEXT,
                description TEXT,
                enabled INTEGER DEFAULT 1,
                priority INTEGER DEFAULT 100,
                created_at TEXT
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS aliases_apps(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                target TEXT
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS aliases_paths(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                target TEXT
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS settings(
                key TEXT PRIMARY KEY,
                value TEXT
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS logs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT,
                level TEXT,
                message TEXT
            )"""
        )
        self._conn.commit()

    def get_custom_commands(self) -> list[dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM custom_commands WHERE enabled=1 ORDER BY priority ASC, id ASC")
        rows = cur.fetchall()
        result = []
        for row in rows:
            item = dict(row)
            try:
                item["entities"] = json.loads(item["entities_json"]) if item["entities_json"] else {}
            except Exception:
                item["entities"] = {}
            result.append(item)
        return result

    def add_custom_command(
        self,
        trigger_text: str,
        intent_type: str,
        entities: dict[str, Any] | None = None,
        description: str = "",
        priority: int = 100,
    ) -> int:
        cur = self._conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO custom_commands(trigger_text,intent_type,entities_json,description,enabled,priority,created_at) VALUES(?,?,?,?,1,?,?)",
            (
                trigger_text.strip().lower(),
                intent_type,
                json.dumps(entities or {}, ensure_ascii=False),
                description,
                priority,
                datetime.now().isoformat(),
            ),
        )
        self._conn.commit()
        return cur.lastrowid

    def delete_custom_command(self, cmd_id: int) -> None:
        cur = self._conn.cursor()
        cur.execute("DELETE FROM custom_commands WHERE id=?", (cmd_id,))
        self._conn.commit()

    def log(self, level: str, message: str) -> None:
        cur = self._conn.cursor()
        cur.execute("INSERT INTO logs(ts,level,message) VALUES(?,?,?)", (datetime.now().strftime("%H:%M:%S"), level, message))
        self._conn.commit()

    def get_logs(self, limit: int = 100) -> list[dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        return [dict(row) for row in reversed(rows)]

    def scan_built_in(self) -> int:
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) as c FROM built_in_commands")
        if cur.fetchone()["c"] > 0:
            return 0
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
        from voice_os_agent.nlu import patterns
        from voice_os_agent.nlu.intents import IntentType

        count = 0
        for pattern, intent_type in patterns.PATTERN_SPECS:
            cur.execute(
                "INSERT INTO built_in_commands(pattern,intent_type,description,executor,entities_hint) VALUES(?,?,?,?,?)",
                (pattern, intent_type.name, "", "", ""),
            )
            count += 1
        self._conn.commit()
        return count

    def get_built_in(self) -> list[dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM built_in_commands ORDER BY id ASC")
        return [dict(row) for row in cur.fetchall()]


db = Database()
