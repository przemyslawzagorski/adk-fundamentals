#!/bin/bash

# Run Jira/Wiki MCP Server Locally
# This script starts the MCP server using FastMCP with SSE transport

echo "=========================================="
echo "Starting Jira/Wiki MCP Server"
echo "=========================================="
echo ""
echo "Server will be available at:"
echo "  http://localhost:8080/mcp"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run MCP server with SSE transport
python jira_wiki_mcpserver.py sse --port 8080 --host 0.0.0.0

