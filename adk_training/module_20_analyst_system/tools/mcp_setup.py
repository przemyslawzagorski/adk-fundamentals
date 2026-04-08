"""
MCP setup — factory for Comarch MCP toolset (Jira + Wiki + GitLab).

Reuses the pattern from module_13 (code_analyst).
"""

import os

from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StdioConnectionParams,
    StdioServerParameters,
)


def create_comarch_mcp() -> McpToolset:
    """Create Comarch MCP toolset for Jira, Wiki, and GitLab integration.

    Environment variables required (see .env.template):
        COMARCH_MCP_REGISTRY, NODE_EXTRA_CA_CERTS,
        JIRA_BASE_URL, JIRA_BEARER_TOKEN,
        WIKI_BASE_URL, WIKI_BEARER_TOKEN,
        GITLAB_BASE_URL, GITLAB_TOKEN
    """
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

    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@comarch/mcp-integration-tool@latest"],
                env=env,
            ),
            timeout=30.0,
        ),
    )
