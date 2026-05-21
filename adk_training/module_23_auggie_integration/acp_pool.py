"""
Singleton ACP client — opt-in dla scenariuszy z wieloma krótkimi callami.

Subprocess Auggie startuje ~2-3s. ACP klient utrzymuje persistent session,
gdzie kolejne `send_message` zajmują <500ms.

Włącz przez: AUGGIE_USE_ACP=true
Wtedy wszystkie wywołania `auggie_call(...)` używają wspólnego klienta.

Lifecycle:
- Pierwsze wywołanie: lazy start
- Auto-restart przy crashu
- Cleanup przez `shutdown_acp()` (np. atexit / health endpoint)
"""

from __future__ import annotations

import atexit
import logging
import os
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)

USE_ACP = os.getenv("AUGGIE_USE_ACP", "false").lower() in ("1", "true", "yes")

_lock = Lock()
_client: Any = None


def get_client(*, model: str, workspace_root: str, cli_path: str | None,
               api_key: str | None = None, api_url: str | None = None) -> Any:
    """Zwraca singleton AuggieACPClient. Lazy init + auto-restart."""
    global _client
    if not USE_ACP:
        raise RuntimeError("ACP not enabled (set AUGGIE_USE_ACP=true)")

    from auggie_sdk.acp import AuggieACPClient

    with _lock:
        if _client is not None:
            try:
                if _client.is_running():
                    return _client
            except Exception:  # noqa: BLE001
                pass
            logger.warning("ACP client not running — restarting")
            try:
                _client.stop()
            except Exception:  # noqa: BLE001
                pass
            _client = None

        kw: dict = {"model": model, "workspace_root": workspace_root}
        if cli_path:
            kw["cli_path"] = cli_path
        if not os.getenv("AUGMENT_SESSION_AUTH"):
            if api_key:
                kw["api_key"] = api_key
            if api_url:
                kw["api_url"] = api_url

        client = AuggieACPClient(**kw)
        client.start()
        _client = client
        logger.info("ACP client started (singleton)")
        return _client


def shutdown_acp() -> None:
    global _client
    with _lock:
        if _client is not None:
            try:
                _client.stop()
                logger.info("ACP client stopped")
            except Exception as e:  # noqa: BLE001
                logger.warning("ACP shutdown error: %s", e)
            _client = None


def acp_status() -> dict:
    with _lock:
        if _client is None:
            return {"enabled": USE_ACP, "running": False}
        try:
            return {
                "enabled": True,
                "running": _client.is_running(),
                "session_id": getattr(_client, "session_id", None),
            }
        except Exception as e:  # noqa: BLE001
            return {"enabled": True, "running": False, "error": str(e)}


atexit.register(shutdown_acp)
