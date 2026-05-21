"""
MCP server wrapper — wystawia narzędzia jako MCP tools dla Claude Desktop / Cursor / dowolnego MCP clienta.

Uruchom (stdio):
    python mcp_server.py

W konfiguracji klienta (Claude Desktop ~/.config/Claude/claude_desktop_config.json):
{
  "mcpServers": {
    "ai-code-concierge": {
      "command": "C:/path/to/.venv312/Scripts/python.exe",
      "args": ["C:/path/to/module_23_auggie_integration/mcp_server.py"]
    }
  }
}

Wymaga: pip install "mcp>=1.0"
"""

from __future__ import annotations

import asyncio
import logging
import pathlib
import sys

from dotenv import load_dotenv

_HERE = pathlib.Path(__file__).parent
load_dotenv(_HERE / ".env")
load_dotenv(_HERE.parent / ".env", override=False)

# Import naszych narzędzi
sys.path.insert(0, str(_HERE))
from tools import (  # noqa: E402
    analyze_codebase, ask_specialist, auggie_cost_report, auggie_health,
    auggie_telemetry, code_review_pr, generate_implementation,
    refactor_workflow, security_audit,
)

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool
except ImportError:
    print("Brak pakietu 'mcp'. Zainstaluj: pip install mcp", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("mcp_server")

server = Server("ai-code-concierge")

TOOL_REGISTRY = {
    "code_review_pr": (code_review_pr, {
        "type": "object",
        "properties": {
            "diff": {"type": "string", "description": "unified diff"},
            "repo_context": {"type": "string", "default": ""},
            "max_retries": {"type": "integer", "default": 3},
        },
        "required": ["diff"],
    }),
    "analyze_codebase": (analyze_codebase, {
        "type": "object",
        "properties": {
            "focus_paths": {"type": "string", "default": ""},
            "max_files": {"type": "integer", "default": 20},
        },
    }),
    "generate_implementation": (generate_implementation, {
        "type": "object",
        "properties": {
            "spec": {"type": "string"},
            "language": {"type": "string", "default": "python"},
            "must_have_csv": {"type": "string", "default": ""},
        },
        "required": ["spec"],
    }),
    "refactor_workflow": (refactor_workflow, {
        "type": "object",
        "properties": {
            "target_file": {"type": "string"},
            "refactor_goal": {"type": "string"},
        },
        "required": ["target_file", "refactor_goal"],
    }),
    "security_audit": (security_audit, {
        "type": "object",
        "properties": {"target": {"type": "string", "default": "."}},
    }),
    "ask_specialist": (ask_specialist, {
        "type": "object",
        "properties": {"question": {"type": "string"}},
        "required": ["question"],
    }),
    "auggie_telemetry": (auggie_telemetry, {"type": "object", "properties": {}}),
    "auggie_cost_report": (auggie_cost_report, {"type": "object", "properties": {}}),
    "auggie_health": (auggie_health, {"type": "object", "properties": {}}),
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name=name,
            description=(fn.__doc__ or name).strip().split("\n")[0],
            inputSchema=schema,
        )
        for name, (fn, schema) in TOOL_REGISTRY.items()
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name not in TOOL_REGISTRY:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    fn, _ = TOOL_REGISTRY[name]
    try:
        # Async-safe: tool może być sync, więc odpalamy w threadpool
        result = await asyncio.to_thread(fn, **(arguments or {}))
        return [TextContent(type="text", text=str(result))]
    except Exception as e:  # noqa: BLE001
        logger.exception("tool %s failed", name)
        return [TextContent(type="text", text=f"ERROR: {type(e).__name__}: {e}")]


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
