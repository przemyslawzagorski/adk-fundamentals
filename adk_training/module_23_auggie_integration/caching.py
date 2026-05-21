"""
LRU cache dla wywołań Auggie — eliminuje powtarzalne zapytania.

Klucz cache = SHA256(prompt + model + return_type + sorted(extra_cli)).
Hit = natychmiastowa odpowiedź (bez subprocess Auggie).

Cache jest świadomy semantyki:
- Pomija zapytania z `success_criteria` (każda runda weryfikacji powinna być świeża).
- Pomija zapytania z `functions=[...]` (custom funkcje mogą zwracać różne wyniki).
- Honoruje TTL (domyślnie 1h, konfigurowalne).
- Limit pamięciowy (max_entries) — LRU eviction.

Stats: hits / misses / saved_seconds.
"""

from __future__ import annotations

import hashlib
import os
import time
from collections import OrderedDict
from dataclasses import dataclass
from threading import Lock
from typing import Any


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    skipped: int = 0  # zapytania nie-cacheable
    saved_seconds: float = 0.0
    evictions: int = 0

    def to_dict(self) -> dict:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "skipped_uncacheable": self.skipped,
            "hit_rate": round(self.hits / total, 3) if total else 0.0,
            "saved_seconds": round(self.saved_seconds, 2),
            "evictions": self.evictions,
        }


class AuggieCache:
    """Thread-safe LRU + TTL cache. In-memory; w produkcji łatwo podmienić na Redis."""

    def __init__(self, *, max_entries: int = 256, ttl_seconds: int = 3600):
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self._store: OrderedDict[str, tuple[float, Any, float]] = OrderedDict()
        self._lock = Lock()
        self.stats = CacheStats()

    @staticmethod
    def make_key(prompt: str, model: str, return_type: str, extra_cli: list[str] | None) -> str:
        h = hashlib.sha256()
        h.update(prompt.encode("utf-8"))
        h.update(b"\x00")
        h.update(model.encode("utf-8"))
        h.update(b"\x00")
        h.update(return_type.encode("utf-8"))
        h.update(b"\x00")
        for arg in sorted(extra_cli or []):
            h.update(arg.encode("utf-8"))
            h.update(b"\x00")
        return h.hexdigest()

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self.stats.misses += 1
                return None
            ts, value, last_duration = entry
            if time.time() - ts > self.ttl_seconds:
                del self._store[key]
                self.stats.misses += 1
                return None
            # LRU bump
            self._store.move_to_end(key)
            self.stats.hits += 1
            self.stats.saved_seconds += last_duration
            return value

    def put(self, key: str, value: Any, original_duration_s: float) -> None:
        with self._lock:
            self._store[key] = (time.time(), value, original_duration_s)
            self._store.move_to_end(key)
            while len(self._store) > self.max_entries:
                self._store.popitem(last=False)
                self.stats.evictions += 1

    def mark_skipped(self) -> None:
        with self._lock:
            self.stats.skipped += 1

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


# Globalna instancja — singletony są OK dla in-process cache
CACHE = AuggieCache(
    max_entries=int(os.getenv("AUGGIE_CACHE_MAX", "256")),
    ttl_seconds=int(os.getenv("AUGGIE_CACHE_TTL", "3600")),
)
CACHE_ENABLED = os.getenv("AUGGIE_CACHE", "true").lower() in ("1", "true", "yes")


def is_cacheable(*, success_criteria: list | None, functions: list | None) -> bool:
    """Zapytania z weryfikacją lub custom funkcjami nie powinny być cache'owane."""
    if success_criteria:
        return False
    if functions:
        return False
    return True
