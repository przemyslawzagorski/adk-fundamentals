"""Comarch MCP connector — HTTP MCPToolset wokol `@comarch/mcp-integration-tool`.

Uzywamy trybu streamable-http (jeden, dlugo-zyjacy serwer w osobnym terminalu).
Startowanie: adk_training/module_22_spec_generator/start_mcp.ps1
(serwer slucha na http://127.0.0.1:3001/mcp)

Dlaczego HTTP a nie STDIO:
  - jeden proces npx, nie startujemy przy kazdym requescie,
  - latwo zalogowac requesty serwera w osobnym terminalu,
  - identyczny pattern co w pz_bonus/copilot/analyst_assistant.

Filtrujemy zestaw narzedzi do read-only minimum (Gemini lepiej wybiera nazwy,
szybsza inicjalizacja toollist).

Resilience:
  Comarch MCP w trybie stateful akceptuje TYLKO JEDNO `initialize` na zycie
  procesu node. MCPToolset jest LAZY — nie laczy sie w konstruktorze, wiec
  nie mozna zlapac bledu 400 w try/except wokol new MCPToolset().
  Dlatego: przy kazdym starcie backendu (_CACHED_TOOLSET=None) PROAKTYWNIE
  restartujemy MCP node, gwarantujac czysta sesje:
    1. Kill node na porcie 3001
    2. Restart MCP z start_mcp.ps1 (subprocess)
    3. Czeka az /mcp bedzie odpowiadac
    4. Tworzy MCPToolset()

ENV (czytane z adk_training/.env):
  MCP_SERVER_URL  (default: http://127.0.0.1:3001)
"""

from __future__ import annotations

import logging
import os
import subprocess
import time
from typing import Any, Optional

logger = logging.getLogger("spec_generator.comarch_mcp")

_CACHED_TOOLSET: Optional[Any] = None

# Read-only subset wystarczajacy dla ticket_fetcher / context (jira + wiki + gitlab).
_TOOL_FILTER = [
    # Jira
    "jira_get_issue",
    "jira_search",
    "jira_get_comments",
    "jira_get_issue_links",
    # Wiki / Confluence
    "wiki_get_page",
    "wiki_search",
    "wiki_get_page_children",
    # GitLab
    "gitlab_get_projects",
    "gitlab_get_repository_file_raw",
    "gitlab_search",
]


def _kill_mcp_on_port(port: int = 3001) -> None:
    """Kill node process listening on given port (Windows)."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue "
             f"| ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}"],
            capture_output=True, timeout=10,
        )
        logger.info("Kill MCP on port %d: exit=%d", port, result.returncode)
    except Exception as e:
        logger.warning("Failed to kill MCP on port %d: %s", port, e)


def _start_mcp_subprocess() -> subprocess.Popen | None:
    """Start MCP server via start_mcp.ps1 as background subprocess.

    IMPORTANT: stdout/stderr go to DEVNULL. Using PIPE without reading
    causes the child to block on write once the OS pipe buffer fills (~4KB
    on Windows) — the MCP node process would hang before reaching 'listening'.
    """
    mcp_script = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "start_mcp.ps1")
    )
    if not os.path.isfile(mcp_script):
        logger.error("MCP start script not found: %s", mcp_script)
        return None
    logger.info("Starting MCP subprocess: %s", mcp_script)
    return subprocess.Popen(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", mcp_script],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )


def _wait_for_mcp(url: str, timeout_s: int = 45) -> bool:
    """Wait until MCP server responds on /mcp endpoint.

    Any HTTP response (even 4xx) means the server is up and listening.
    We only retry on connection refused / timeout.
    """
    import httpx
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            r = httpx.post(url, json={"jsonrpc": "2.0", "method": "ping", "id": 0}, timeout=3)
            # Any response = server is listening. 406 is common (missing Accept header).
            logger.info("MCP server ready at %s (status=%d)", url, r.status_code)
            return True
        except Exception:
            pass
        time.sleep(1)
    logger.error("MCP server not ready after %ds", timeout_s)
    return False


def _restart_mcp(port: int = 3001) -> bool:
    """Kill existing MCP, start fresh, wait for ready."""
    logger.warning("=== MCP AUTO-RESTART: killing node on port %d, relaunching ===", port)
    _kill_mcp_on_port(port)
    time.sleep(2)  # give OS time to release port
    proc = _start_mcp_subprocess()
    if proc is None:
        return False
    url = f"http://127.0.0.1:{port}/mcp"
    ready = _wait_for_mcp(url, timeout_s=45)
    if not ready and proc.poll() is None:
        logger.error("MCP not ready — killing subprocess")
        proc.terminate()
    return ready


def _create_mcp_toolset(server_url: str) -> Any:
    """Create MCPToolset + apply stateful monkey-patch."""
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import (
        StreamableHTTPConnectionParams,
    )

    url = f"{server_url}/mcp"
    logger.info("Comarch MCP (HTTP): connecting to %s, filter=%s tools", url, len(_TOOL_FILTER))

    toolset = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(url=url),
        tool_filter=_TOOL_FILTER,
    )

    # Monkey-patch: prevent ADK from treating GET-stream flaps as "disconnected"
    # (which would trigger cleanup + re-initialize → 400 from stateful MCP).
    try:
        sm = toolset._mcp_session_manager  # noqa: SLF001
        sm._is_session_disconnected = lambda _session: False  # type: ignore[method-assign]
        logger.info("MCP: auto-cleanup disabled (stateful mode).")
    except Exception as e:
        logger.warning("Failed to patch MCP session manager: %s", e)

    return toolset


def build_comarch_mcp_toolset() -> Optional[Any]:
    """Singleton HTTP MCPToolset dla Comarch MCP. None gdy brak URL serwera.

    Strategia: MCPToolset jest LAZY — konstruktor nie laczy sie z MCP.
    Polaczenie nastepuje dopiero w get_tools() (wewnatrz ADK runtime).
    Dlatego NIE MOZNA zlapac bledu sesji w try/except wokol konstruktora.

    Zamiast tego: poniewaz _CACHED_TOOLSET=None oznacza swiezy restart backendu,
    a MCP stateful akceptuje TYLKO JEDNO initialize na proces node,
    ZAWSZE restartujemy MCP przy pierwszym budowaniu toolseta.
    To gwarantuje czysta sesje.
    """
    global _CACHED_TOOLSET
    if _CACHED_TOOLSET is not None:
        return _CACHED_TOOLSET

    server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:3001").rstrip("/")
    port = int(server_url.rsplit(":", 1)[-1]) if ":" in server_url.rsplit("/", 1)[-1] else 3001

    try:
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset  # noqa: F401
    except ImportError as e:
        logger.error("Brak zaleznosci ADK MCP: %s", e)
        return None

    # ALWAYS restart MCP on first toolset build (= backend just started).
    # Stateful MCP rejects second initialize, so we need a fresh node process.
    logger.info("First toolset build — proactively restarting MCP for clean session.")
    _restart_mcp(port=port)

    toolset = _create_mcp_toolset(server_url)
    _CACHED_TOOLSET = toolset
    return toolset


def get_jira_tools() -> list[Any] | None:
    ts = build_comarch_mcp_toolset()
    return [ts] if ts is not None else None


def get_wiki_tools() -> list[Any] | None:
    # Ten sam toolset wystawia tools wiki — unikamy duplikatow w toollist.
    return None


def get_gitlab_tools() -> list[Any] | None:
    # jw. — gitlab_* jest w tym samym toolset.
    return None
