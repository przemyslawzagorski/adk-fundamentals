"""
Code Retrieval Tool - ADK FunctionTool wrapper dla CodeIndexer
==============================================================
Owija CodeIndexer w narzędzie ADK, które agent może wywołać.
"""

import os
from typing import Optional
from code_indexer import CodeIndexer

# Globalny indekser - inicjalizowany raz per sesja
_indexer: Optional[CodeIndexer] = None


def _get_indexer() -> CodeIndexer:
    """Lazy init indeksera z ustawieniami z env."""
    global _indexer
    if _indexer is None:
        project_dir = os.environ.get("CODE_PROJECT_DIR", ".")
        persist_dir = os.environ.get("CODE_INDEX_DIR", "./index_store")
        _indexer = CodeIndexer(
            project_dir=project_dir,
            persist_dir=persist_dir,
        )
    return _indexer


def search_code(query: str, top_k: int = 5) -> dict:
    """
    Przeszukaj zaindeksowany kod źródłowy semantycznie.

    Użyj tego narzędzia gdy potrzebujesz znaleźć fragmenty kodu powiązane
    z danym problemem, funkcjonalnością lub opisem z ticketa Jira.

    Args:
        query: Opis funkcjonalności lub problemu do znalezienia w kodzie.
               Np. "uwierzytelnianie użytkowników" lub "obsługa błędów płatności"
        top_k: Liczba najbardziej relevantnych fragmentów do zwrócenia (domyślnie 5)

    Returns:
        dict z wynikami wyszukiwania lub statystykami indeksu
    """
    indexer = _get_indexer()
    results = indexer.query(query, top_k=top_k)
    stats = indexer.get_stats()

    return {
        "results": results,
        "total_indexed_files": stats["indexed_files"],
        "total_chunks": stats["total_chunks"],
    }


def index_project(
    extensions: str = "",
    incremental: bool = True,
) -> dict:
    """
    Zaindeksuj lub odśwież indeks kodu źródłowego projektu.

    Uruchom to na początku pracy, aby agent miał dostęp do aktualnego kodu.
    W trybie incremental (domyślnym) indeksuje tylko zmienione pliki.

    Args:
        extensions: Opcjonalna lista rozszerzeń oddzielona przecinkami,
                   np. ".py,.java,.ts". Jeśli puste - użyje domyślnych.
        incremental: Jeśli True - indeksuj tylko zmienione pliki.
                    Jeśli False - pełne re-indeksowanie.

    Returns:
        dict ze statystykami indeksowania
    """
    indexer = _get_indexer()
    ext_list = [e.strip() for e in extensions.split(",") if e.strip()] or None
    return indexer.index_project(
        extensions=ext_list,
        incremental=incremental,
    )


def get_index_stats() -> dict:
    """
    Pokaż statystyki aktualnego indeksu kodu.

    Returns:
        dict z informacjami: liczba plików, chunków, ścieżka projektu
    """
    return _get_indexer().get_stats()
