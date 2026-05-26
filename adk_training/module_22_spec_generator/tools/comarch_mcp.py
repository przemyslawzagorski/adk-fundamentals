"""Comarch MCP connector — STDIO MCPToolset wokol `@comarch/mcp-integration-tool`.

Uzywamy trybu STDIO (MCP_MODE=stdio), identycznego jak konfiguracja Augment.
ADK startuje `npx @comarch/mcp-integration-tool` jako subprocess przy pierwszym
wywolaniu get_tools() i utrzymuje go przez caly czas zycia backendu.

Zalety STDIO vs HTTP:
  - dziala z Comarch MCP (HTTP/StreamableHTTP zwraca 400 — inna wersja spec),
  - brak problemu "session poisoning" (kazde wywolanie to izolowany subprocess),
  - zgodny z konfiguracja Augment MCP (ten sam npx command + env vars).

ENV (czytane z adk_training/.env):
  JIRA_BASE_URL, JIRA_BEARER_TOKEN
  WIKI_BASE_URL, WIKI_BEARER_TOKEN
  GITLAB_BASE_URL, GITLAB_TOKEN
  NODE_EXTRA_CA_CERTS           (sciezka do cert CA)
  MCP_NPX_REGISTRY              (default: https://nexus.czk.comarch/repository/ai-npm)
"""

from __future__ import annotations

import logging
import os
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


def _build_stdio_env() -> dict[str, str]:
    """Zbiera env vars potrzebne do uruchomienia npx MCP w trybie stdio."""
    env: dict[str, str] = {
        "MCP_MODE": "stdio",
        "NODE_TLS_REJECT_UNAUTHORIZED": "0",
        "HTTP_REJECT_UNAUTHORIZED": "false",
    }

    # Certyfikat CA (opcjonalny)
    ca_certs = os.getenv("NODE_EXTRA_CA_CERTS", "")
    if ca_certs:
        env["NODE_EXTRA_CA_CERTS"] = ca_certs

    # Jira
    jira_url = os.getenv("JIRA_BASE_URL", "")
    jira_token = os.getenv("JIRA_BEARER_TOKEN", "")
    if jira_url:
        env["JIRA_BASE_URL"] = jira_url
    if jira_token:
        env["JIRA_BEARER_TOKEN"] = jira_token

    # Wiki / Confluence
    wiki_url = os.getenv("WIKI_BASE_URL", "")
    wiki_token = os.getenv("WIKI_BEARER_TOKEN", "")
    if wiki_url:
        env["WIKI_BASE_URL"] = wiki_url
    if wiki_token:
        env["WIKI_BEARER_TOKEN"] = wiki_token

    # GitLab
    gitlab_url = os.getenv("GITLAB_BASE_URL", "")
    gitlab_token = os.getenv("GITLAB_TOKEN", "")
    if gitlab_url:
        env["GITLAB_BASE_URL"] = gitlab_url
    if gitlab_token:
        env["GITLAB_TOKEN"] = gitlab_token

    return env


def build_comarch_mcp_toolset() -> Optional[Any]:
    """Singleton STDIO MCPToolset dla Comarch MCP. None gdy brak tokenow.

    ADK startuje npx jako subprocess przy pierwszym get_tools().
    Proces zyje przez caly czas zycia backendu (singleton).
    """
    global _CACHED_TOOLSET
    if _CACHED_TOOLSET is not None:
        return _CACHED_TOOLSET

    # Warunek minimalny: token Jiry musi byc ustawiony
    if not os.getenv("JIRA_BEARER_TOKEN"):
        logger.warning("JIRA_BEARER_TOKEN nie ustawiony — pomijam MCP toolset.")
        return None

    try:
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters
    except ImportError as e:
        logger.error("Brak zaleznosci ADK MCP: %s", e)
        return None

    registry = os.getenv(
        "MCP_NPX_REGISTRY",
        "https://nexus.czk.comarch/repository/ai-npm",
    )
    env_vars = _build_stdio_env()

    logger.info(
        "Comarch MCP (STDIO): registry=%s, filter=%d tools", registry, len(_TOOL_FILTER)
    )

    toolset = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["--registry", registry, "@comarch/mcp-integration-tool"],
                env=env_vars,
            )
        ),
        tool_filter=_TOOL_FILTER,
    )

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
