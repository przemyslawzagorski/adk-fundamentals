"""SQLite-backed disclaimer ack store.

Replaces the in-memory ``Dict[str, DisclaimerAck]`` so:
- acks survive backend restarts,
- TTLs are enforced consistently,
- multiple Concierge replicas share one source of truth.
"""
from __future__ import annotations

import sqlite3
import threading
import time
import uuid
from pathlib import Path
from typing import Optional

from .safety import DisclaimerAck

_SCHEMA = """
CREATE TABLE IF NOT EXISTS acks (
    token       TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL,
    target_url  TEXT NOT NULL,
    statement   TEXT NOT NULL,
    created_at  REAL NOT NULL,
    expires_at  REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_acks_expiry ON acks(expires_at);
"""


class AckStore:
    """Thread-safe SQLite ack vault."""

    def __init__(self, db_path: Path, default_ttl_s: int = 3600) -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._ttl = default_ttl_s
        self._lock = threading.Lock()
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        c = sqlite3.connect(self._path)
        c.row_factory = sqlite3.Row
        return c

    def register(self, ack: DisclaimerAck, ttl_s: Optional[int] = None) -> str:
        token = uuid.uuid4().hex
        ttl = ttl_s or self._ttl
        now = time.time()
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO acks(token, user_id, target_url, statement, created_at, expires_at) "
                "VALUES (?,?,?,?,?,?)",
                (token, ack.user_id, ack.target_url, ack.statement, now, now + ttl),
            )
            conn.commit()
        return token

    def get(self, token: str) -> Optional[DisclaimerAck]:
        if not token:
            return None
        now = time.time()
        with self._lock, self._connect() as conn:
            self._purge(conn, now)
            row = conn.execute(
                "SELECT user_id, target_url, statement, created_at, expires_at "
                "FROM acks WHERE token = ?",
                (token,),
            ).fetchone()
        if row is None:
            return None
        return DisclaimerAck(
            acknowledged=True,
            user_id=row["user_id"],
            target_url=row["target_url"],
            timestamp=row["created_at"],
            statement=row["statement"],
        )

    def revoke(self, token: str) -> bool:
        with self._lock, self._connect() as conn:
            cur = conn.execute("DELETE FROM acks WHERE token = ?", (token,))
            conn.commit()
            return cur.rowcount > 0

    def purge_expired(self) -> int:
        with self._lock, self._connect() as conn:
            n = self._purge(conn, time.time())
            conn.commit()
            return n

    @staticmethod
    def _purge(conn: sqlite3.Connection, now: float) -> int:
        cur = conn.execute("DELETE FROM acks WHERE expires_at < ?", (now,))
        return cur.rowcount or 0
