# Jira & Wiki MCP Server + ADK Agent (Python)

Python implementation of Jira/Wiki MCP server with ADK agent integration.

**Based on:** Java implementation in `../java-jira-wiki-master`  
**Pattern:** Similar to `../../02_agent_with_mcp_toolset` (Instavibe example)

---

## 📋 What's Included

### MCP Server
- **FastMCP-based** server with `@mcp.tool()` annotations
- **5 Jira tools**: get_ticket, search, my_open_tickets, create_ticket, add_comment
- **3 Wiki tools** (optional): get_page, search, get_page_by_url
- **REST API clients** for Jira and Confluence Wiki

### ADK Agent
- **LlmAgent** with MCPToolset integration
- Connects to local or remote MCP server
- Gemini 2.5 Flash model
- Helpful instructions for Jira/Wiki tasks

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.template` to `.env` and fill in your credentials:

```bash
cp .env.template .env
nano .env
```

Required variables:
```bash
JIRA_BASE_URL=https://your-jira.com/rest/api/2
JIRA_BEARER_TOKEN=your-token
```

### 3. Test Jira API

```bash
python 1_test_jira_api.py
```

### 4. Run MCP Server

```bash
./2_run_mcp_server_locally.sh
```

Server will be available at: `http://localhost:8080/mcp`

### 5. Test with ADK Web

In a new terminal:

```bash
cd agent_local_mcp
cp .env.template .env
# Edit .env and set MCP_SERVER_URL=http://localhost:8080
adk web .
```

Open browser at `http://localhost:8000`

---

## 🛠️ Available Tools

### Jira Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `jira_get_ticket` | Get ticket by ID | `ticket_id` (e.g., "CLM6-11588") |
| `jira_search` | Search with JQL | `jql`, `limit` (default: 10) |
| `jira_my_open_tickets` | Get your open tickets | `limit` (default: 10) |
| `jira_create_ticket` | Create new ticket | `summary`, `description`, `project_key`, `issue_type`, `label` |
| `jira_add_comment` | Add comment | `ticket_id`, `comment` |

### Wiki Tools (Optional)

| Tool | Description | Parameters |
|------|-------------|------------|
| `wiki_get_page` | Get page by ID | `page_id` |
| `wiki_search` | Search with CQL | `cql`, `limit` (default: 10) |
| `wiki_get_page_by_url` | Get page by URL | `url` |

---

## 📂 Project Structure

```
python-jira-wiki-mcp/
├── jira_client.py              # Jira REST API wrapper
├── wiki_client.py              # Wiki REST API wrapper
├── jira_wiki_mcpserver.py      # MCP server with @mcp.tool()
├── requirements.txt            # Python dependencies
├── .env.template               # Environment variables template
│
├── agent_local_mcp/            # ADK agent
│   ├── agent.py                # Agent definition
│   └── .env.template           # Agent env template
│
├── 1_test_jira_api.py          # Test Jira API connectivity
├── 2_run_mcp_server_locally.sh # Run MCP server
├── 3_run_adk_web_local_mcp.md  # ADK web guide
├── 4_run_agent_locally.py      # Run agent programmatically
│
└── README.md                   # This file
```

---

## 🔧 Configuration

### MCP Server (.env)

```bash
# Required — Atlassian Cloud (Basic Auth)
JIRA_BASE_URL=https://your-instance.atlassian.net/rest/api/2
JIRA_AUTH_TYPE=basic
JIRA_USER_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Optional (for ticket creation)
JIRA_DEFAULT_PROJECT_KEY=TRAIN
JIRA_DEFAULT_ISSUE_TYPE=Task
JIRA_DEFAULT_LABEL=mcp-training

# Optional (Wiki integration)
ENABLE_WIKI_INTEGRATION=true
WIKI_BASE_URL=https://your-instance.atlassian.net/wiki/rest/api
WIKI_AUTH_TYPE=basic
WIKI_USER_EMAIL=your-email@example.com
WIKI_API_TOKEN=your-api-token
```

> 💡 Pełna instrukcja konfiguracji Atlassian Cloud: [SETUP_ATLASSIAN.md](SETUP_ATLASSIAN.md)

### Agent (agent_local_mcp/.env)

```bash
MCP_SERVER_URL=http://localhost:8080
```

---

## 💡 Usage Examples

### Example 1: Get Your Open Tickets
```
Show me my open tickets
```

### Example 2: Search with JQL
```
Find all high priority tickets created in the last 7 days
```

### Example 3: Get Specific Ticket
```
Get details for ticket CLM6-11588
```

### Example 4: Create Ticket
```
Create a Story ticket with summary "Implement login" and description "Add user authentication"
```

---

## 🧪 Testing Flow

```
1. Test API      → python 1_test_jira_api.py
2. Run MCP       → ./2_run_mcp_server_locally.sh
3. Test with ADK → adk web agent_local_mcp
4. Run agent     → python 4_run_agent_locally.py
```

---

## 📚 Technical Details

### MCP Server
- **Framework**: FastMCP
- **Transport**: SSE (Server-Sent Events)
- **Port**: 8080
- **Endpoint**: `/mcp`

### ADK Agent
- **Model**: Gemini 2.5 Flash
- **Connection**: StreamableHTTPConnectionParams
- **Toolset**: MCPToolset

### APIs Used
- [Jira REST API v2](https://developer.atlassian.com/cloud/jira/platform/rest/v2/intro)
- [Confluence REST API](https://developer.atlassian.com/cloud/confluence/rest/v1/intro)

---

## 🆚 Comparison: Python vs Java

| Feature | Python (this) | Java (original) |
|---------|---------------|-----------------|
| Lines of code | ~500 | ~2000+ |
| Dependencies | 3 (fastmcp, requests, dotenv) | Many (Spring, etc.) |
| Startup time | <1s | ~5s |
| Memory usage | ~50MB | ~200MB |
| Development speed | Fast | Slower |
| Deployment | Simple (pip install) | Complex (Java 21 required) |

---

## 🚀 Next Steps

1. ✅ Test locally with `adk web`
2. 🔄 Deploy MCP server to Cloud Run
3. 🔄 Deploy agent to Agent Engine
4. 🔄 Add GitLab integration (optional)

---

## 🤝 Contributing

This is a training example. Feel free to extend with:
- GitLab tools
- More Jira operations
- Wiki page creation
- Attachment handling

