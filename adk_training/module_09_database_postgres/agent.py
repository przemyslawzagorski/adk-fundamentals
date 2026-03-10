"""
MCP Database Agent - PostgreSQL Example (WITH MCP)

This example shows how to use ADK with MCP Toolbox and a real PostgreSQL database.
Uses free cloud PostgreSQL (Neon.tech, Supabase, etc.)

Key concepts:
- MCP (Model Context Protocol) for standardized tool access
- Remote PostgreSQL database
- Toolbox as MCP server
- Production-ready architecture

Compare with adk04-simple-database to see the difference!

Usage:
    # 1. Start Toolbox server:
    ./toolbox --tools-file toolbox.yaml

    # 2. Run with ADK web interface:
    adk web adkagents/00-adk-intro/adk04-mcp-postgres

    # Or programmatically (see README.md for examples)
"""

import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

MODEL = "gemini-2.5-flash"
AGENT_APP_NAME = 'hotel_expert_mcp'

# MCP Toolbox URL
# Local: http://127.0.0.1:5000
# Remote: Your deployed toolbox URL (e.g., Cloud Run)
TOOLBOX_URL = os.getenv("TOOLBOX_URL", "http://127.0.0.1:5000")

instruction_prompt = """
You are a helpful hotel search assistant for Poland.

You can help users:
- Find hotels by name
- Find hotels in specific cities
- Find hotels within a price range
- Get detailed information about specific hotels
- Show top-rated hotels


Always provide clear, friendly responses with relevant details like:
- Hotel name and location
- Rating (out of 5)
- Price per night in PLN
- Brief description

If multiple hotels match, show the top results sorted by rating.
Be conversational and helpful!
"""

# =============================================================================
# MCP TOOLSET SETUP
# =============================================================================

# Connect to MCP Toolbox via SSE (Server-Sent Events)
connection_params = SseConnectionParams(
    url=f"{TOOLBOX_URL}/mcp/sse",
    headers={}
)

mcp_toolset = MCPToolset(connection_params=connection_params)

# =============================================================================
# CREATE AGENT
# =============================================================================

root_agent = Agent(
    model=MODEL,
    name=AGENT_APP_NAME,
    description="Agent to help users find hotels in Poland using MCP and PostgreSQL.",
    instruction=instruction_prompt,
    tools=[mcp_toolset]
)

# =============================================================================
# EXAMPLE USAGE (Optional - for testing)
# =============================================================================
#
# This agent is designed to be used with ADK web interface or deployment tools.
#
# Prerequisites:
#   1. Start Toolbox server:
#      ./toolbox --tools-file toolbox.yaml
#
#   2. Configure .env with TOOLBOX_URL (default: http://127.0.0.1:5000)
#
# For quick testing with ADK web:
#   adk web adkagents/00-adk-intro/adk04-mcp-postgres
#
# Or programmatically:
#
#   from google.adk.runners import InMemoryRunner
#   from google.genai import types
#
#   runner = InMemoryRunner(agent=root_agent)
#
#   async def test():
#       events = await runner.run_debug("Find hotels in Warsaw")
#       for event in events:
#           if event.is_final_response():
#               print(event.content.parts[0].text)
#
#   import asyncio
#   asyncio.run(test())

