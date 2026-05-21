"""NotebookLM jako narzedzie agenta — wrapper na NotebookLMAgentSystem.

Pod spodem uzywa `adk_training.notebooklm_agent.NotebookLMAgentSystem`, ktory steruje
prawdziwa przegladarka (Playwright + Computer Use Gemini) na notebooklm.google.com.

Auth: cookies w `~/.notebooklm-agent/cookies.json` (USE_COOKIE_AUTH=true) lub
persistent Chrome profile (CHROME_PROFILE_DIR).

Flagi env:
  NOTEBOOKLM_ENABLED=1          — wlacza tool (inaczej build_notebooklm_tool() → None)
  NOTEBOOK_URL=https://...      — URL notebooka (np. ec182696-...)
  HEADLESS=true|false           — tryb przegladarki
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Optional

logger = logging.getLogger("spec_generator.notebooklm_tool")

_SYSTEM_LOCK = threading.Lock()
_SYSTEM_INSTANCE: Optional[Any] = None  # NotebookLMAgentSystem singleton
_NOTEBOOK_URL_OVERRIDE: Optional[str] = None  # dynamic override from web request


def set_notebook_url(url: str | None) -> None:
    """Ustaw notebook URL dla nastepnego/biezacego zapytania.

    Jesli singleton juz istnieje — nadpisz jego _notebook_url.
    Jesli jeszcze nie — zapamietaj do tworzenia singletona.
    """
    global _NOTEBOOK_URL_OVERRIDE, _SYSTEM_INSTANCE
    _NOTEBOOK_URL_OVERRIDE = url
    if _SYSTEM_INSTANCE is not None and url:
        _SYSTEM_INSTANCE._notebook_url = url
        logger.info("NotebookLM notebook_url overridden to: %s", url)


def _get_or_create_system() -> Any:
    """Lazy singleton — pierwsze wywolanie inicjalizuje Playwright.

    Uwaga: importujemy `NotebookLMAgentSystem` przez import_module aby uniknac
    wykonania module-level kodu w `notebooklm_agent.agent` (tworzy on globalny
    `root_agent` z PlaywrightComputer, ktorego sygnatura __init__ moze sie zmieniac).
    """
    global _SYSTEM_INSTANCE
    if _SYSTEM_INSTANCE is not None:
        return _SYSTEM_INSTANCE
    with _SYSTEM_LOCK:
        if _SYSTEM_INSTANCE is not None:
            return _SYSTEM_INSTANCE

        # Resolve notebook URL: override > SpecGenSettings > notebooklm_agent CONFIG
        notebook_url = _NOTEBOOK_URL_OVERRIDE
        if not notebook_url:
            from config import get_settings
            notebook_url = get_settings().notebooklm_notebook_url

        try:
            from notebooklm_agent.agent import NotebookLMAgentSystem  # type: ignore
        except TypeError as e:
            logger.warning(
                "notebooklm_agent.agent module-level init failed (%s) — retry via importlib", e
            )
            import importlib
            mod = importlib.import_module("notebooklm_agent.agent")
            NotebookLMAgentSystem = getattr(mod, "NotebookLMAgentSystem")

        kwargs = {}
        if notebook_url:
            kwargs["notebook_url"] = notebook_url
            logger.info("NotebookLMAgentSystem will use notebook: %s", notebook_url)
        _SYSTEM_INSTANCE = NotebookLMAgentSystem(**kwargs)
        logger.info("NotebookLMAgentSystem singleton created (lazy).")
    return _SYSTEM_INSTANCE


def build_notebooklm_tool() -> Any | None:
    """Zwroc FunctionTool wywolujacy NotebookLM przez Computer Use, lub None."""
    from config import get_settings
    s = get_settings()
    if not s.notebooklm_enabled:
        return None

    from google.adk.tools import FunctionTool

    async def notebooklm_query(question: str) -> dict:
        """Zapytaj NotebookLM o wiedze domenowa (SWOK / Comarch product docs).

        Args:
            question: Pytanie po polsku.

        Returns:
            dict: {"ok": bool, "answer": str, "sources": list}.
        """
        try:
            system = _get_or_create_system()
            logger.info("[NotebookLM] QUESTION: %s", question[:200])
            answer = await system.ask(
                question=question,
                session_id="spec_generator",
                user_id="spec_generator",
            )
            logger.info(
                "[NotebookLM] RAW ANSWER (len=%d): %s",
                len(answer or ""),
                (answer or "")[:1000],
            )
            return {
                "ok": True,
                "answer": answer or "(NotebookLM zwrocil pusta odpowiedz)",
                "sources": [],
            }
        except Exception as e:  # pragma: no cover
            logger.exception("NotebookLM query failed")
            return {
                "ok": False,
                "answer": f"Blad NotebookLM: {e}",
                "sources": [],
            }

    return FunctionTool(func=notebooklm_query)
