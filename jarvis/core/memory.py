"""Small local conversation store using SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class ConversationMemory:
    def __init__(self, path: Path) -> None:
        self._connection = sqlite3.connect(path, check_same_thread=False)
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self._connection.commit()

    def add(self, role: str, content: str) -> None:
        self._connection.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)",
            (role, content),
        )
        self._connection.commit()

    def recent(self, limit: int = 12) -> list[tuple[str, str]]:
        rows = self._connection.execute(
            """
            SELECT role, content FROM messages
            ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return list(reversed(rows))

    def clear(self) -> None:
        self._connection.execute("DELETE FROM messages")
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()
