# Analyst Assistant — Implementation Plan

## Folder Structure
```
analyst_assistant/
├── agent.py                  # root_agent (orchestrator, adk web entry point)
├── __init__.py
├── requirements.txt
├── PLAN.md                   # this file
├── agents/
│   ├── __init__.py
│   ├── lld/
│   │   ├── __init__.py
│   │   └── lld_agent.py      # create_lld_pipeline() → LoopAgent
│   ├── hld/
│   │   ├── __init__.py
│   │   └── hld_agent.py      # create_hld_pipeline() → LoopAgent
│   └── test_cases/
│       ├── __init__.py
│       └── test_cases_agent.py
├── tools/
│   ├── __init__.py
│   ├── document_generator.py # generate_docx() via python-docx
│   └── context_helpers.py    # clarify_with_user() via HumanInputTool
├── prompts/
│   ├── lld_template.md
│   ├── hld_template.md
│   └── test_cases_template.md
└── output/                   # generated .docx files
```

## Architecture
- **Orchestrator**: `LlmAgent` (root_agent) routes via `AgentTool` pattern (module_12 style)
- **3 Pipelines**: `LoopAgent` each with writer → critic → decision → LoopController (module_08 style)
- **HITL**: `HumanInputTool` inside `clarify_with_user()` tool function (module_05 style)
- **MCP**: `MCPToolset(StreamableHTTPConnectionParams)` reusing existing comarch-mcp server
- **Word output**: `generate_docx()` using python-docx

## Per-Pipeline Loop (max_iterations=3)
```
writer   → reads {draft} + {critique} → output_key="<type>_draft"
critic   → reads {draft}              → output_key="<type>_critique"
decision → reads draft+critique       → output_schema=Decision → output_key="<type>_status"
controller (BaseAgent) → escalate if decision=="valid"
```

## Tools per Writer Agent
- `clarify_with_user(question)` — HITL pause
- `generate_docx(type, title, content)` — final Word file output
- Jira MCP toolset (jira_search_issues, jira_get_issue)
- Wiki MCP toolset (wiki_search, wiki_get_page)

## Assumptions
- Language: English for documents and prompts
- Models: gemini-2.5-pro for writers, gemini-2.5-flash for critic/decision
- MCP: reuse comarch-mcp server via StreamableHTTPConnectionParams
- User context: text pasted in chat → stored in session state
- Entry point: adk web (agent.py exports root_agent)

