# Run ADK Web with Local MCP Server

This guide shows how to test the Jira Assistant agent with the local MCP server using `adk web`.

## Prerequisites

1. ✅ MCP server is running (see `2_run_mcp_server_locally.sh`)
2. ✅ Environment variables are set in `agent_local_mcp/.env`

## Steps

### 1. Make sure MCP server is running

In Terminal 1:
```bash
./2_run_mcp_server_locally.sh
```

You should see:
```
Starting Jira/Wiki MCP Server
Server will be available at: http://localhost:8080/mcp
```

### 2. Run ADK web interface

In Terminal 2:
```bash
cd agent_local_mcp
adk web .
```

This will start the ADK web interface at `http://localhost:8000`

### 3. Test the agent

Open your browser at `http://localhost:8000` and try these prompts:

#### Example 1: Get your open tickets
```
Show me my open tickets
```

#### Example 2: Search for tickets
```
Search for tickets in project CLM6 that are open
```

#### Example 3: Get specific ticket
```
Get details for ticket CLM6-11588
```

#### Example 4: Search with JQL
```
Find all high priority tickets created in the last 7 days
```

#### Example 5: Create a ticket (if you have permissions)
```
Create a new Story ticket with summary "Test ticket" and description "This is a test"
```

## Troubleshooting

### MCP server not responding
- Check that the MCP server is running on port 8080
- Verify `MCP_SERVER_URL` in `agent_local_mcp/.env` is set to `http://localhost:8080`

### Authentication errors
- Verify `JIRA_BASE_URL` and `JIRA_BEARER_TOKEN` are set correctly
- Test with `1_test_jira_api.py` first

### No tools available
- Check MCP server logs for errors
- Verify the connection URL format: `http://localhost:8080/mcp`

## Next Steps

Once everything works locally:
1. Deploy MCP server to Cloud Run (see deployment guide)
2. Update `MCP_SERVER_URL` to point to Cloud Run
3. Deploy agent to Agent Engine

