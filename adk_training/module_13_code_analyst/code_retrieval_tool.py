"""
Code Retrieval Tool — fabryka ADK FunctionTool dla konkretnej instancji CodeIndexer.

Glowne API produkcyjne: :func:`make_retrieval_tools(indexer)` — multi-tenant,
uzywane przez web/app.py. Dodatkowo eksportujemy cienkie wrappery:
:func:`search_code`, :func:`index_project`, :func:`get_index_stats`
dla trybu CLI (``agent.py`` / ``adk web``) — dzialaja na globalnym indekserze
skonfigurowanym przez ENV ``CODE_PROJECT_DIR`` / ``CODE_INDEX_DIR``.
"""

from __future__ import annotations

import os
import threading
from typing import Optional

from google.adk.tools import FunctionTool

from code_indexer import CodeIndexer


def make_retrieval_tools(indexer: CodeIndexer) -> list[FunctionTool]:
    """Zwroc liste narzedzi RAG powiazanych z danym indekserem."""

    def search_code(query: str, top_k: int = 5) -> dict:
        """Semantycznie przeszukaj zaindeksowany kod zrodlowy.

        Args:
            query: Opis tego czego szukasz (np. 'autoryzacja JWT').
            top_k: Ile wynikow zwrocic (1-20).
        """
        top_k = max(1, min(int(top_k), 20))
        results = indexer.query(query, top_k=top_k)
        stats = indexer.get_stats()
        return {
            "ok": True,
            "results": results,
            "total_files": stats["indexed_files"],
            "total_chunks": stats["total_chunks"],
            "similarity_cutoff": stats.get("similarity_cutoff"),
        }

    def get_index_stats() -> dict:
        """Pokaz statystyki indeksu kodu (pliki, chunki, cutoff)."""
        return {"ok": True, **indexer.get_stats()}

    return [
        FunctionTool(func=search_code),
        FunctionTool(func=get_index_stats),
    ]


# ---------------------------------------------------------------------------
# CLI convenience: pojedynczy globalny indekser dla `adk web` / `agent.py`.
# Uzywaj TYLKO z CLI — warstwa web uzywa make_retrieval_tools per-repo.
# ---------------------------------------------------------------------------

_singleton_lock = threading.Lock()
_singleton_indexer: Optional[CodeIndexer] = None


def _cli_indexer() -> CodeIndexer:
    global _singleton_indexer
    with _singleton_lock:
        if _singleton_indexer is None:
            project_dir = os.environ.get("CODE_PROJECT_DIR", ".")
            persist_dir = os.environ.get("CODE_INDEX_DIR", "./index_store")
            _singleton_indexer = CodeIndexer(
                project_dir=project_dir, persist_dir=persist_dir
            )
        return _singleton_indexer


def search_code(query: str, top_k: int = 5) -> dict:
    """(CLI) Semantycznie przeszukaj zaindeksowany kod zrodlowy."""
    top_k = max(1, min(int(top_k), 20))
    idx = _cli_indexer()
    results = idx.query(query, top_k=top_k)
    stats = idx.get_stats()
    return {
        "ok": True,
        "results": results,
        "total_files": stats["indexed_files"],
        "total_chunks": stats["total_chunks"],
    }


def index_project(incremental: bool = True) -> dict:
    """(CLI) Zaindeksuj projekt z ENV ``CODE_PROJECT_DIR``."""
    idx = _cli_indexer()
    stats = idx.index_project(incremental=incremental)
    return {"ok": True, **stats}


def get_index_stats() -> dict:
    """(CLI) Statystyki globalnego indeksu."""
    return {"ok": True, **_cli_indexer().get_stats()}

