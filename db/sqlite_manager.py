"""
SQLite Manager - 封装 SQLite CRUD，包含 FTS5 配置与写入互斥锁
"""
import sqlite3
import threading
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from config.path_manager import path_manager


@dataclass
class MemoryRecord:
    id: str
    created_at: str
    image_path: str
    ai_summary: str
    app_name: str
    text_content: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: tuple) -> "MemoryRecord":
        return cls(
            id=row[0],
            created_at=row[1],
            image_path=row[2],
            ai_summary=row[3],
            app_name=row[4],
            text_content=row[5] if len(row) > 5 else None,
        )


class SQLiteManager:
    """SQLite 管理器 - 单例模式"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._conn: Optional[sqlite3.Connection] = None
        self._write_lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        db_path = path_manager.sqlite_path
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

        cursor = self._conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                image_path TEXT NOT NULL,
                ai_summary TEXT,
                app_name TEXT,
                text_content TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_created_at
            ON memories(created_at DESC)
        """)

        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
            USING fts5(ai_summary, text_content, content='memories', content_rowid='rowid')
        """)

        self._conn.commit()

    def insert_memory(self, record: MemoryRecord) -> bool:
        with self._write_lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO memories (id, created_at, image_path, ai_summary, app_name, text_content)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.id,
                        record.created_at,
                        record.image_path,
                        record.ai_summary,
                        record.app_name,
                        record.text_content,
                    ),
                )
                self._conn.commit()
                return True
            except Exception as e:
                print(f"Insert memory error: {e}")
                return False

    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryRecord]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        if row:
            return MemoryRecord.from_row(row)
        return None

    def get_all_memories(self, limit: int = 100, offset: int = 0) -> List[MemoryRecord]:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM memories ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = cursor.fetchall()
        return [MemoryRecord.from_row(row) for row in rows]

    def search_memories(self, query: str, limit: int = 20) -> List[MemoryRecord]:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT m.* FROM memories m
            WHERE m.ai_summary LIKE ? OR m.text_content LIKE ?
            ORDER BY m.created_at DESC
            LIMIT ?
            """,
            (f"%{query}%", f"%{query}%", limit),
        )
        rows = cursor.fetchall()
        return [MemoryRecord.from_row(row) for row in rows]

    def update_memory_summary(self, memory_id: str, summary: str) -> bool:
        with self._write_lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute(
                    "UPDATE memories SET ai_summary = ? WHERE id = ?",
                    (summary, memory_id),
                )
                self._conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Update memory error: {e}")
                return False

    def delete_memory(self, memory_id: str) -> bool:
        with self._write_lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                self._conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Delete memory error: {e}")
                return False

    def get_memories_count(self) -> int:
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        return cursor.fetchone()[0]

    def close(self):
        if self._conn:
            self._conn.close()


sqlite_manager = SQLiteManager()
