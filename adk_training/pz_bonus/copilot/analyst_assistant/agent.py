"""
Analyst Assistant — root agent (adk web entry point)

Orchestrates three specialist pipelines:
  - LLD: Low-Level Design document
  - HLD: High-Level Design document
  - Test Cases: Test specification document

Each pipeline is a LoopAgent (writer → critic → decision → controller).
MCP tools: Jira + Confluence via Comarch MCP (streamable-http mode).
HITL: clarify_with_user() inside writer agents.

MCP server startup (run once before `adk web`):
  MCP_MODE=streamable-http \\
  MCP_AUTH_MODE=none \\
  HTTP_PORT=3000 \\
  JIRA_BASE_URL=... JIRA_BEARER_TOKEN=... \\
  WIKI_BASE_URL=... WIKI_BEARER_TOKEN=... \\
  npx --registry https://nexus.czk.comarch/repository/ai-npm @comarch/mcp-integration-tool
"""

import logging
import os
import sys
from pathlib import Path

# Ensure agents/ and tools/ subdirectories are importable regardless of
# the working directory from which `adk web` is launched.
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from agents.lld.lld_agent import create_lld_pipeline
from agents.hld.hld_agent import create_hld_pipeline
from agents.test_cases.test_cases_agent import create_test_cases_pipeline

load_dotenv()

# ---------------------------------------------------------------------------
# Logging — widoczne w terminalu adk web
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
# Pokaż wywołania narzędzi i decyzje modelu z wnętrza ADK
logging.getLogger("google.adk").setLevel(logging.INFO)

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")
# URL of the running Comarch MCP server (MCP_MODE=streamable-http)
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3000")

# ---------------------------------------------------------------------------
# MCP Toolset — Comarch MCP (streamable-http mode, one shared server process)
# Each pipeline gets its own MCPToolset instance pointing to the same server.
# ---------------------------------------------------------------------------
# Actual tool names as exposed by the Comarch MCP server (no suffix).
# Verified via: python tools/_list_mcp_tools.py
# Scope: read-only subset sufficient for context fetching and direct user queries.
_MCP_TOOL_FILTER = [
    "jira_get_issue",
    "jira_search",
    "jira_my_open_issues",
    "jira_get_comments",
    "wiki_get_page",
    "wiki_search",
    "wiki_get_page_children",
]


def _make_mcp_toolset() -> MCPToolset:
    return MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=f"{MCP_SERVER_URL}/mcp",
        ),
        tool_filter=_MCP_TOOL_FILTER,
    )


# ---------------------------------------------------------------------------
# Sub-agent pipelines (each writer gets its own MCP toolset)
# ---------------------------------------------------------------------------
logger.info("=" * 60)
logger.info("🚀 Analyst Assistant — inicjalizacja agentów")
logger.info("=" * 60)
lld_pipeline = create_lld_pipeline(mcp_toolset=_make_mcp_toolset())
hld_pipeline = create_hld_pipeline(mcp_toolset=_make_mcp_toolset())
test_cases_pipeline = create_test_cases_pipeline(mcp_toolset=_make_mcp_toolset())
logger.info("✅ Wszystkie pipeline'y zainicjalizowane")

# ---------------------------------------------------------------------------
# Root orchestrator
# ---------------------------------------------------------------------------
root_agent = LlmAgent(
    model=MODEL,
    name="analyst_orchestrator",
    description="Analyst assistant that generates LLD, HLD, and Test Case documents",
    tools=[
        AgentTool(agent=lld_pipeline),
        AgentTool(agent=hld_pipeline),
        AgentTool(agent=test_cases_pipeline),
        _make_mcp_toolset(),   # ← MCP: Jira/Wiki (tylko po zebraniu kontekstu od użytkownika)
    ],
    instruction="""You are an Analyst Assistant that generates professional software documentation.

You can produce three types of documents:
  • **LLD** (Low-Level Design) — detailed component/class/API design
  • **HLD** (High-Level Design) — system architecture and integration overview
  • **Test Cases** — test specification with test case table and traceability matrix

## ⛔ MANDATORY GATE — DO NOT SKIP

You MUST collect all required information BEFORE calling any pipeline.
If ANYTHING from the checklist below is missing or vague:
1. DO NOT call any pipeline tools (lld_pipeline, hld_pipeline, test_cases_pipeline).
2. DO NOT search Jira or Wiki trying to guess the missing requirements.
3. Simply WRITE A PLAIN TEXT RESPONSE to the user asking all missing questions in a numbered list.
4. End your response there. Wait for the user to reply in the next message.

Asking questions via text is how you MUST interact with the user — there is no special tool for this.

### Required for HLD or LLD:
1. **System/component name** — exact name of what's being designed
2. **Feature description** — what it does and why (business purpose, not just a title)
3. **Functional requirements** — at least 3 concrete requirements, not just a vague goal
4. **Integration points** — what other systems/services does it connect to?
5. **Tech stack** — language, framework, cloud, messaging (or explicit "no preference")
6. **NFR targets** — latency, throughput, availability SLA (e.g. p99 < 200ms, 99.9% uptime)
7. **Scale/load** — expected volume (users, events/sec, data size)

### Required for Test Cases:
1. **Feature name and description** — what is being tested
2. **Acceptance criteria (AC)** — explicit AC or user story with expected behavior
3. **Test scope** — what's in scope, what's explicitly out of scope
4. **Environment** — SIT / UAT / prod-like? what's the backend?
5. **Edge cases known** — any known edge cases or error scenarios to cover?

### What "vague" means — examples that are NOT enough:
- ❌ "Wygeneruj HLD dla Notification Hub Service" — brak NFR, integracji, tech stack
- ❌ "Napisz test cases dla upload" — brak AC, brak środowiska
- ✅ Only delegate when you have concrete answers to ALL points above

## JIRA / WIKI DIRECT QUERIES

You have Jira and Confluence READ tools available at ALL times (check your tool list).
They let you: fetch a Jira ticket by key, search Jira with JQL, fetch comments,
get a Wiki page by ID or URL, search Confluence pages.

If the user asks you to **look up a Jira ticket or Wiki page** — do it immediately.
No gate, no checklist. Use the appropriate tool and summarize the result.
Examples:
  - "sprawdź SWITCH-26453" → use the jira_get_issue tool
  - "co jest na wiki MPC0SSCoreNetwork" → use the wiki_search tool
  - "pokaż mi informacje o tickecie CLM6-8821" → use the jira_get_issue tool

## DOCUMENT GENERATION WORKFLOW (only after gate passes)

1. **Optionally enrich context from Jira/Wiki** — if the user mentioned ticket IDs or Wiki pages
   during the checklist phase, fetch them to supplement collected answers.

2. **Route to the correct pipeline** with full context:
   - HLD request → call `hld_pipeline`
   - LLD request → call `lld_pipeline`
   - Test Cases request → call `test_cases_pipeline`

3. **Report the result** — tell the user the exact path to the saved .docx file.
   Offer to refine or generate another document.

## ABSOLUTE RULES
- NEVER call a pipeline without passing the MANDATORY GATE above.
- NEVER generate document content yourself — always use the pipelines.
- NEVER assume or invent NFR values, tech stack, or integration points.
- NEVER search Jira/Wiki trying to *guess* missing requirements — ask the user in plain text instead.
- After the gate passes, you MAY fetch tickets/pages the user explicitly mentioned.
""",
)

