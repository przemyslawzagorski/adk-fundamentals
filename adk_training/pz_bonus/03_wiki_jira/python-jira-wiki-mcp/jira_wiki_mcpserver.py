"""
Jira & Wiki MCP Server

MCP server providing tools for Jira and Confluence Wiki integration.
Uses FastMCP with @mcp.tool() annotations.
"""

import os
import sys
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from jira_client import JiraClient
from wiki_client import WikiClient

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Jira & Wiki MCP")

# Initialize Jira client (always required)
jira = JiraClient(
    base_url=os.getenv("JIRA_BASE_URL")
)

# Initialize Wiki client (optional)
wiki = None
if os.getenv("ENABLE_WIKI_INTEGRATION", "false").lower() == "true":
    try:
        wiki = WikiClient(
            base_url=os.getenv("WIKI_BASE_URL")
        )
        print("[OK] Wiki integration enabled")
    except ValueError as e:
        print(f"[WARNING] Wiki integration disabled: {e}")


# ============================================================================
# JIRA TOOLS
# ============================================================================

@mcp.tool()
def jira_get_ticket(ticket_id: str) -> dict:
    """
    Get info about a Jira ticket by ID.

    Args:
        ticket_id: Ticket ID (e.g., "CLM6-11588")

    Returns:
        dict: Ticket information including key, summary, status, assignee, description
    """
    return jira.get_ticket(ticket_id)


@mcp.tool()
def jira_search(jql: str, limit: int = 10) -> list:
    """
    Search Jira tickets using JQL (Jira Query Language).

    Args:
        jql: JQL query string. Examples:
             - "project = CLM6 AND status = Open"
             - "assignee = currentUser()"
             - "created >= -7d"
        limit: Maximum number of results (default: 10)

    Returns:
        list: List of matching tickets
    """
    return jira.search(jql, limit)


@mcp.tool()
def jira_my_open_tickets(limit: int = 10) -> list:
    """
    Get unresolved tickets assigned to current user, sorted by update date.

    Args:
        limit: Maximum number of results (default: 10)

    Returns:
        list: List of open tickets
    """
    return jira.my_open_tickets(limit)


@mcp.tool()
def jira_create_ticket(
    summary: str,
    description: str,
    project_key: str = None,
    issue_type: str = None,
    label: str = None
) -> dict:
    """
    Create a new Jira ticket.
    WARNING: Rate limited: 5 tickets per hour

    Args:
        summary: Ticket summary/title
        description: Ticket description
        project_key: Project key (e.g., "CLM6"). Uses JIRA_DEFAULT_PROJECT_KEY if not provided
        issue_type: Issue type (e.g., "Story", "Task", "Bug"). Uses JIRA_DEFAULT_ISSUE_TYPE if not provided
        label: Label to add. Uses JIRA_DEFAULT_LABEL if not provided

    Returns:
        dict: Created ticket information with key and ID
    """
    return jira.create_ticket(summary, description, project_key, issue_type, label)


@mcp.tool()
def jira_add_comment(ticket_id: str, comment: str) -> dict:
    """
    Add a comment to a Jira ticket.
    WARNING: Rate limited: 5 comments per hour

    Args:
        ticket_id: Ticket ID (e.g., "CLM6-11588")
        comment: Comment text

    Returns:
        dict: Comment information
    """
    return jira.add_comment(ticket_id, comment)


# ============================================================================
# WIKI TOOLS (Optional)
# ============================================================================

if wiki:
    @mcp.tool()
    def wiki_get_page(page_id: str) -> dict:
        """
        Get info about a Confluence Wiki page by ID.

        Args:
            page_id: Page ID

        Returns:
            dict: Page information including title, body, version, space
        """
        return wiki.get_page(page_id)


    @mcp.tool()
    def wiki_search(cql: str, limit: int = 10) -> list:
        """
        Search Wiki content using CQL (Confluence Query Language).

        Args:
            cql: CQL query string. Examples:
                 - "type=page AND space=DEV"
                 - "title ~ 'documentation'"
            limit: Maximum number of results (default: 10)

        Returns:
            list: List of matching pages
        """
        return wiki.search(cql, limit)


    @mcp.tool()
    def wiki_get_page_by_url(url: str) -> dict:
        """
        Get Wiki page info by URL.

        Args:
            url: Full Wiki page URL (e.g., "https://wiki.example.com/pages/viewpage.action?pageId=123456")

        Returns:
            dict: Page information
        """
        return wiki.get_page_by_url(url)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    # Default: stdio (compatible with MCP clients like Claude Desktop, Cursor, etc.)
    # For SSE: python jira_wiki_mcpserver.py sse
    transport = "stdio"
    if len(sys.argv) > 1 and sys.argv[1] in ("sse", "stdio"):
        transport = sys.argv[1]
    mcp.run(transport=transport)

