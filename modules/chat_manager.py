from __future__ import annotations

import sqlite3
import uuid
import json
from datetime import datetime, timezone
from pathlib import Path

import config


class ChatManager:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or (config.DATABASE_DIR / "chat.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sources TEXT,
                    created_at TEXT NOT NULL
                )
            """)

    def new_conversation(self, title: str = "New conversation") -> str:
        conversation_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (conversation_id, title, now, now),
            )
        return conversation_id

    def list_conversations(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM conversations ORDER BY updated_at DESC"
            ).fetchall()
            return [dict(row) for row in rows]

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as connection:
            return connection.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]

    def add_message(self, conversation_id: str, role: str, content: str, sources: list[dict] | None = None) -> None:
        now = datetime.now(timezone.utc).isoformat()
        sources_json = json.dumps(sources or [])
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "INSERT INTO messages (conversation_id, role, content, sources, created_at) VALUES (?, ?, ?, ?, ?)",
                (conversation_id, role, content, sources_json, now),
            )
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now, conversation_id),
            )

    def get_messages(self, conversation_id: str) -> list[dict]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT role, content, sources, created_at FROM messages WHERE conversation_id = ? ORDER BY id",
                (conversation_id,),
            ).fetchall()
            messages = []
            for row in rows:
                item = dict(row)
                item["sources"] = json.loads(item["sources"]) if item["sources"] else []
                messages.append(item)
            return messages

    def delete_conversation(self, conversation_id: str) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            connection.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))

    def rename_conversation(self, conversation_id: str, title: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                (title.strip() or "New conversation", now, conversation_id),
            )
