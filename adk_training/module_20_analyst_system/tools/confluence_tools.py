"""ADK FunctionTools wrapping ConfluenceDCClient (read-only — publish odbywa się
poza LLM pipelinem przez bezpośrednie wywołanie ConfluenceDCClient.create_page()).
"""

from __future__ import annotations

import logging
from typing import Any

from google.adk.tools import FunctionTool

from ..clients.confluence_dc_client import ConfluenceError, get_confluence_client

logger = logging.getLogger(__name__)


def confluence_search(cql: str, limit: int = 10) -> dict[str, Any]:
    """Wyszukaj strony Confluence przez CQL.

    Args:
        cql: Zapytanie CQL, np. 'type=page AND space=SWOK AND text~"rozliczenia"'.
        limit: 1..50.

    Returns:
        {ok, count, results: [{id, title, space, type, url}], error?}
    """
    client = get_confluence_client()
    if client is None:
        return {"ok": False, "error": "Confluence client not configured."}
    try:
        results = client.search(cql=cql, limit=limit)
    except (ConfluenceError, ValueError) as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "count": len(results), "results": results}


def confluence_get_page(page_id: str) -> dict[str, Any]:
    """Pobierz stronę Confluence po ID (XHTML body + view HTML).

    Args:
        page_id: Identyfikator strony.

    Returns:
        {ok, id, title, space_key, url, version, body_view, body_storage, error?}
    """
    client = get_confluence_client()
    if client is None:
        return {"ok": False, "error": "Confluence client not configured."}
    try:
        page = client.get_page(page_id)
    except (ConfluenceError, ValueError) as e:
        return {"ok": False, "error": str(e)}
    return {
        "ok": True,
        "id": page.id,
        "title": page.title,
        "space_key": page.space_key,
        "url": page.url,
        "version": page.version,
        "labels": page.labels,
        "body_view": page.body_view,
        "body_storage": page.body_storage,
    }


def build_confluence_tools() -> list[FunctionTool]:
    """Read-only Confluence tools. [] gdy klient nieskonfigurowany."""
    if get_confluence_client() is None:
        return []
    return [
        FunctionTool(func=confluence_search),
        FunctionTool(func=confluence_get_page),
    ]
