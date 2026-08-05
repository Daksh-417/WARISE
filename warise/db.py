import json
import sqlite3
from datetime import datetime

from .config import DB_PATH, HISTORY_LIMIT


def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                query TEXT,
                mode TEXT,
                confidence INTEGER,
                answer TEXT,
                sources TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_session(query, mode, answer, confidence, sources):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            INSERT INTO sessions (created_at, query, mode, confidence, answer, sources)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                query,
                mode,
                confidence,
                answer,
                json.dumps(sources, ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def load_history(limit=None):
    init_db()
    limit = limit or HISTORY_LIMIT
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, created_at, query, mode, confidence, answer, sources
            FROM sessions
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        
        out = []
        for row in rows:
            item = dict(row)
            try:
                item["sources"] = json.loads(item.get("sources") or "[]")
            except json.JSONDecodeError:
                item["sources"] = []
            out.append(item)
        return out
    finally:
        conn.close()
