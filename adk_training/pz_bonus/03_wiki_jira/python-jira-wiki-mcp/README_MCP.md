# Jira & Wiki MCP Server (Standalone)

FastMCP-based server providing Jira and Confluence Wiki integration via Model Context Protocol (MCP).

## What It Does

Exposes Jira and Wiki operations as MCP tools that can be used by any MCP-compatible client (Claude Desktop, Cursor, etc.):
- **Jira**: Get tickets, search with JQL, create tickets, add comments, view open tickets
- **Wiki**: Get pages, search with CQL, retrieve pages by URL (optional)

## Files Required

**Core MCP Server:**
- `jira_wiki_mcpserver.py` - Main MCP server with tool definitions
- `jira_client.py` - Jira REST API client
- `wiki_client.py` - Confluence Wiki REST API client
- `requirements.txt` - Python dependencies (minimal version below)
- `.env` - Environment configuration

**Testing & Utilities:**
- `1_test_jira_api.py` - Test Jira API connectivity
- `2_run_mcp_server_locally.sh` - Run server with SSE transport (for ADK)
- `run_mcp_server.ps1` - Run server with stdio transport (for MCP clients)

**NOT Required (ADK Agent files - exclude these):**
- `agent_local_mcp/` - ADK agent implementation
- `4_run_agent_locally.py` - ADK agent runner
- `3_run_adk_web_local_mcp.md` - ADK web instructions
- `mcp_client_config.json` - ADK-specific config

## Installation

### 1. Dependencies

Create minimal `requirements.txt`:
```
fastmcp
requests
python-dotenv
```

Install:
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file:

```bash
# Jira Configuration
JIRA_BASE_URL=https://your-instance.atlassian.net/rest/api/2
JIRA_AUTH_TYPE=basic
JIRA_USER_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
JIRA_DEFAULT_PROJECT_KEY=PROJ
JIRA_DEFAULT_ISSUE_TYPE=Task
JIRA_DEFAULT_LABEL=mcp-created

# Wiki Configuration (optional)
ENABLE_WIKI_INTEGRATION=true
WIKI_BASE_URL=https://your-instance.atlassian.net/wiki/rest/api
WIKI_AUTH_TYPE=basic
WIKI_USER_EMAIL=your-email@example.com
WIKI_API_TOKEN=your-api-token
```

**Get API Token:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy token to `.env` file

**For On-Premise Jira/Wiki (Bearer Auth):**
```bash
JIRA_AUTH_TYPE=bearer
JIRA_BEARER_TOKEN=your-pat-token
WIKI_AUTH_TYPE=bearer
WIKI_BEARER_TOKEN=your-pat-token
```

## Running the Server

### Test Jira Connection First
```bash
python 1_test_jira_api.py
```

### For MCP Clients (Claude Desktop, Cursor, etc.)
```bash
python jira_wiki_mcpserver.py
# or
./run_mcp_server.ps1  # Windows
```

### For ADK/SSE Transport
```bash
python jira_wiki_mcpserver.py sse --port 8080 --host 0.0.0.0
# or
./2_run_mcp_server_locally.sh
```

## MCP Client Configuration

Add to your MCP client config (e.g., Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "jira-wiki": {
      "command": "python",
      "args": ["jira_wiki_mcpserver.py"],
      "cwd": "/absolute/path/to/python-jira-wiki-mcp",
      "env": {
        "JIRA_BASE_URL": "https://your-instance.atlassian.net/rest/api/2",
        "JIRA_AUTH_TYPE": "basic",
        "JIRA_USER_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-api-token",
        "JIRA_DEFAULT_PROJECT_KEY": "PROJ",
        "JIRA_DEFAULT_ISSUE_TYPE": "Task",
        "ENABLE_WIKI_INTEGRATION": "true",
        "WIKI_BASE_URL": "https://your-instance.atlassian.net/wiki/rest/api",
        "WIKI_AUTH_TYPE": "basic",
        "WIKI_USER_EMAIL": "your-email@example.com",
        "WIKI_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Available Tools

### Jira Tools

**`jira_get_ticket(ticket_id: str)`**
- Get ticket details by ID
- Example: `ticket_id="PROJ-123"`

**`jira_search(jql: str, limit: int = 10)`**
- Search tickets with JQL
- Example: `jql="project = PROJ AND status = Open"`

**`jira_my_open_tickets(limit: int = 10)`**
- Get current user's unresolved tickets

**`jira_create_ticket(summary: str, description: str, project_key: str = None, issue_type: str = None, label: str = None)`**
- Create new ticket (rate limited: 5/hour)
- Uses defaults from env vars if not specified

**`jira_add_comment(ticket_id: str, comment: str)`**
- Add comment to ticket

### Wiki Tools (if enabled)

**`wiki_get_page(page_id: str)`**
- Get page by ID

**`wiki_search(cql: str, limit: int = 10)`**
- Search with CQL
- Example: `cql="type=page AND space=DEV"`

**`wiki_get_page_by_url(url: str)`**
- Get page by full URL

## Testing

1. **Test API connectivity:**
   ```bash
   python 1_test_jira_api.py
   ```

2. **Test MCP server with MCP Inspector:**
   ```bash
   npx @modelcontextprotocol/inspector python jira_wiki_mcpserver.py
   ```

3. **Test in Claude Desktop:**
   - Add config above
   - Restart Claude Desktop
   - Ask: "Show me my open Jira tickets"

## Troubleshooting

**401 Unauthorized:**
- Verify API token is correct
- Check email matches Atlassian account
- Ensure token hasn't expired

**Connection errors:**
- Verify base URLs are correct
- Check network/firewall settings
- For on-premise: ensure VPN is connected

**Wiki tools not available:**
- Set `ENABLE_WIKI_INTEGRATION=true`
- Verify `WIKI_BASE_URL` is correct
- Check Wiki API token permissions

