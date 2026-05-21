"""
MCP setup — factory for Comarch MCP toolset (Jira + Wiki + GitLab).

Reuses the pattern from module_13 (code_analyst).
MCP is optional — if tokens are not configured, returns None (graceful fallback).
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

_mcp_instance: object | None = ...  # sentinel: ... means "not yet initialised"


def _has_mcp_config() -> bool:
    """Check if at least one MCP integration has credentials configured."""
    return bool(
        os.environ.get("JIRA_BEARER_TOKEN")
        or os.environ.get("WIKI_BEARER_TOKEN")
        or os.environ.get("GITLAB_TOKEN")
    )


def get_comarch_mcp():
    """Get the shared Comarch MCP toolset (singleton, lazy-initialised).

    Returns McpToolset if MCP tokens are configured, None otherwise.
    Safe to call multiple times — creates the toolset only once.
    """
    global _mcp_instance
    if _mcp_instance is not ...:
        return _mcp_instance

    if not _has_mcp_config():
        logger.info("MCP: no tokens configured — Jira/Wiki/GitLab tools disabled")
        _mcp_instance = None
        return None

    try:
        from google.adk.tools.mcp_tool.mcp_toolset import (
            McpToolset,
            StdioConnectionParams,
            StdioServerParameters,
        )

        ca_cert = os.environ.get("NODE_EXTRA_CA_CERTS", "")
        registry = os.environ.get(
            "COMARCH_MCP_REGISTRY",
            "https://nexus.czk.comarch/repository/ai-npm",
        )

        env = {
            "NODE_EXTRA_CA_CERTS": ca_cert,
            "npm_config_registry": registry,
            "npm_config_cafile": ca_cert,
            "JIRA_BASE_URL": os.environ.get("JIRA_BASE_URL", ""),
            "JIRA_BEARER_TOKEN": os.environ.get("JIRA_BEARER_TOKEN", ""),
            "WIKI_BASE_URL": os.environ.get("WIKI_BASE_URL", ""),
            "WIKI_BEARER_TOKEN": os.environ.get("WIKI_BEARER_TOKEN", ""),
            "GITLAB_BASE_URL": os.environ.get("GITLAB_BASE_URL", ""),
            "GITLAB_TOKEN": os.environ.get("GITLAB_TOKEN", ""),
        }

        _mcp_instance = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["-y", "@comarch/mcp-integration-tool@latest"],
                    env=env,
                ),
                timeout=30.0,
            ),
        )
        logger.info("MCP: toolset created successfully")
        return _mcp_instance
    except Exception as e:
        logger.warning("MCP: failed to create toolset — %s", e)
        _mcp_instance = None
        return None


# Keep backward-compatible alias
def create_comarch_mcp():
    """Backward-compatible alias for get_comarch_mcp()."""
    return get_comarch_mcp()
