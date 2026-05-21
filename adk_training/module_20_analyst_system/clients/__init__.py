"""REST clients for external systems (Jira DC, Confluence DC).

Cienka warstwa transportu — bez logiki biznesowej, bez MCP, bez ADK.
FunctionTools wokół tych klientów żyją w `module_20/tools/`.
"""

from .jira_dc_client import JiraDCClient, JiraIssue, JiraError, get_jira_client
from .confluence_dc_client import (
    ConfluenceDCClient,
    ConfluencePage,
    ConfluenceError,
    get_confluence_client,
)

__all__ = [
    "JiraDCClient",
    "JiraIssue",
    "JiraError",
    "get_jira_client",
    "ConfluenceDCClient",
    "ConfluencePage",
    "ConfluenceError",
    "get_confluence_client",
]
