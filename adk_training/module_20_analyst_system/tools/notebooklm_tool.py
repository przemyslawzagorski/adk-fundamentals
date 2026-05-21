"""NotebookLM jako narzędzie agenta — wrapper na NotebookLMAgentSystem.

Port z `zagi-analyst-assistant`. Steruje przeglądarką (Playwright + Computer Use Gemini)
na notebooklm.google.com. Lazy singleton — nie tworzy sesji przy imporcie.

Auth: cookies w `~/.notebooklm-agent/cookies.json` lub persistent Chrome profile.

ENV:
    NOTEBOOKLM_ENABLED=1               — włącza tool (inaczej build_*() -> None)
    NOTEBOOKLM_NOTEBOOK_URL=https://...
    NOTEBOOKLM_COOKIES_PATH=~/.notebooklm-agent/cookies.json
    NOTEBOOKLM_HEADLESS=true|false
"""

from __future__ import annotations

import logging
import os
import threading
from typing import Any, Optional

logger = logging.getLogger(__name__)

_SYSTEM_LOCK = threading.Lock()
_SYSTEM_INSTANCE: Optional[Any] = None
_NOTEBOOK_URL_OVERRIDE: Optional[str] = None


def is_enabled() -> bool:
    return os.getenv("NOTEBOOKLM_ENABLED", "0").strip().lower() in ("1", "true", "yes", "on")


def set_notebook_url(url: str | None) -> None:
    """Override notebook URL dla bieżącego/najbliższego zapytania."""
    global _NOTEBOOK_URL_OVERRIDE, _SYSTEM_INSTANCE
    _NOTEBOOK_URL_OVERRIDE = url
    if _SYSTEM_INSTANCE is not None and url:
        try:
            _SYSTEM_INSTANCE._notebook_url = url
            logger.info("NotebookLM notebook_url overridden to: %s", url)
        except Exception as e:  # pragma: no cover
            logger.warning("Failed to override notebook URL: %s", e)


def _get_or_create_system() -> Any:
    """Lazy singleton — pierwsze wywołanie inicjalizuje Playwright."""
    global _SYSTEM_INSTANCE
    if _SYSTEM_INSTANCE is not None:
        return _SYSTEM_INSTANCE
    with _SYSTEM_LOCK:
        if _SYSTEM_INSTANCE is not None:
            return _SYSTEM_INSTANCE

        notebook_url = _NOTEBOOK_URL_OVERRIDE or os.getenv("NOTEBOOKLM_NOTEBOOK_URL")

        try:
            # adk_training/notebooklm_agent — istnieje w naszym repo
            from adk_training.notebooklm_agent.agent import NotebookLMAgentSystem  # type: ignore
        except (TypeError, ImportError) as e:
            logger.warning("notebooklm_agent.agent import failed (%s) — retry via importlib", e)
            import importlib
            mod = importlib.import_module("adk_training.notebooklm_agent.agent")
            NotebookLMAgentSystem = getattr(mod, "NotebookLMAgentSystem")

        kwargs: dict[str, Any] = {}
        if notebook_url:
            kwargs["notebook_url"] = notebook_url
            logger.info("NotebookLMAgentSystem will use notebook: %s", notebook_url)
        _SYSTEM_INSTANCE = NotebookLMAgentSystem(**kwargs)
        logger.info("NotebookLMAgentSystem singleton created (lazy).")
    return _SYSTEM_INSTANCE


def build_notebooklm_tool() -> Any | None:
    """Zwróć FunctionTool wywołujący NotebookLM. None gdy NOTEBOOKLM_ENABLED!=1."""
    if not is_enabled():
        return None

    from google.adk.tools import FunctionTool

    async def notebooklm_query(question: str) -> dict:
        """Zadaj pytanie do bazy wiedzy NotebookLM (jeden notebook).

        Args:
            question: Pytanie po polsku, konkretne (nazwy procesów, modułów).

        Returns:
            {ok, answer, sources, error?}
        """
        try:
            system = _get_or_create_system()
            logger.info("[NotebookLM] Q: %s", question[:200])
            answer = await system.ask(
                question=question,
                session_id="ticket_to_hld",
                user_id="analyst_system",
            )
            logger.info("[NotebookLM] A (len=%d): %s", len(answer or ""), (answer or "")[:400])
            return {"ok": True, "answer": answer or "(NotebookLM zwrócił pustą odpowiedź)", "sources": []}
        except Exception as e:  # pragma: no cover
            logger.exception("NotebookLM query failed")
            return {"ok": False, "answer": "", "error": str(e), "sources": []}

    return FunctionTool(func=notebooklm_query)
