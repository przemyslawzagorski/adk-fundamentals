"""
LLD Pipeline Agent
LoopAgent: writer → critic → decision → controller
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import AsyncGenerator

from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent, LoopAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.events import Event, EventActions

from tools.document_generator import generate_docx

logger = logging.getLogger(__name__)

MODEL_PRO = os.getenv("ADK_MODEL_PRO", "gemini-2.5-pro")
MODEL_FLASH = os.getenv("ADK_MODEL_FLASH", "gemini-2.5-flash")
THROTTLE_SECONDS = int(os.getenv("THROTTLE_SECONDS", "8"))
THROTTLE_SECONDS = int(os.getenv("THROTTLE_SECONDS", "8"))

_TEMPLATE_PATH = Path(__file__).parent.parent.parent / "prompts" / "lld_template.md"
LLD_TEMPLATE = _TEMPLATE_PATH.read_text(encoding="utf-8")


class Decision(BaseModel):
    decision: str = Field(description="Either 'valid' or 'invalid'")
    reason: str = Field(description="Brief explanation of the decision")


async def _init_lld_state(callback_context: CallbackContext):
    callback_context.state.setdefault("user_context", "")
    callback_context.state.setdefault("lld_draft", "")
    callback_context.state.setdefault("lld_critique", "")
    callback_context.state.setdefault("lld_status", {"decision": "invalid", "reason": ""})


async def _throttle(callback_context: CallbackContext):
    """Pauza przed wywołaniem LLM — zapobiega 429 RESOURCE_EXHAUSTED."""
    logger.info(f"[LLD] ⏳ Throttling {THROTTLE_SECONDS}s before LLM call (429 prevention)...")
    await asyncio.sleep(THROTTLE_SECONDS)
    return None


_LLD_WRITER_INSTRUCTION = f"""You are a senior software architect writing a Low-Level Design document.

DOCUMENT TEMPLATE TO FOLLOW:
{LLD_TEMPLATE}

CONTEXT AVAILABLE IN SESSION STATE:
- {{user_context}}: user-provided specs or descriptions
- {{lld_draft}}: previous draft (empty on first iteration)
- {{lld_critique}}: critic feedback to address (empty on first iteration)

INSTRUCTIONS:
1. Review the user context and any Jira/Wiki data already gathered.
2. Use Jira/Wiki tools to fetch additional context if relevant Jira ticket IDs or Wiki pages are mentioned.
3. Write a complete LLD following every section of the template above.
   Make reasonable assumptions for unclear points — document them as assumptions.
4. On subsequent iterations, address ALL points raised in {{lld_critique}}.
5. Output only the document content in markdown format — no preamble, no meta-commentary.

DIAGRAM REQUIREMENTS — MANDATORY:
Embed Mermaid code blocks using ```mermaid ... ``` fences. The renderer converts them to images.

Component/class diagram for the main module structure:
```mermaid
classDiagram
    class NotificationService {{
        +send(request NotificationRequest) NotificationId
        +getStatus(id NotificationId) NotificationStatus
    }}
    class ChannelAdapter {{
        <<interface>>
        +dispatch(notification Notification) Result
    }}
    NotificationService --> ChannelAdapter
```

Sequence diagram for the primary API flow (REST or async):
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant DB
    Client->>API: POST /v1/resource
    API->>Service: process(request)
    Service->>DB: save(entity)
    DB-->>Service: saved
    Service-->>API: result
    API-->>Client: 202 Accepted
```

ER diagram for the data model section:
```mermaid
erDiagram
    NOTIFICATION {{
        uuid id PK
        string status
        string channel
        timestamp created_at
    }}
    TEMPLATE {{
        uuid id PK
        string name
        string body
    }}
    NOTIFICATION }}o--|| TEMPLATE : uses
```

Use the patterns above as templates — adapt node names and fields to the actual component being designed.
"""

_lld_critic = LlmAgent(
    model=MODEL_FLASH,
    name="lld_critic",
    description="Reviews LLD draft for completeness and quality",
    output_key="lld_critique",
    before_agent_callback=_throttle,
    instruction="""You are a thorough technical reviewer checking an LLD document.

Review the draft in {lld_draft} against these criteria:
1. All template sections are present and non-empty
2. Data model is specific (field names, types, constraints)
3. API contracts include signatures, parameters, return types
4. Error handling and edge cases are addressed
5. Security and NFR sections have concrete content
6. No vague placeholder text remains

Provide specific, actionable critique for each deficiency found.
If the document meets all criteria, write exactly: "No improvements needed."
""",
)

_lld_decision = LlmAgent(
    model=MODEL_FLASH,
    name="lld_decision",
    description="Decides if LLD is ready for finalization",
    output_key="lld_status",
    output_schema=Decision,
    before_agent_callback=_throttle,
    instruction="""You are the approving architect for LLD documents.

Draft: {lld_draft}
Critique: {lld_critique}

Decision rules:
- If critique says "No improvements needed" → decision: "valid"
- If there are unresolved issues → decision: "invalid"

Be decisive. Output your decision in the required schema.
""",
)


class _LldLoopController(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("lld_status", {})
        decision = status.get("decision", "invalid") if isinstance(status, dict) else "invalid"
        reason = status.get("reason", "") if isinstance(status, dict) else ""
        should_stop = decision == "valid"

        logger.info(f"[LLD Loop] decision={decision} | reason={reason} | stop={should_stop}")

        if should_stop:
            draft = ctx.session.state.get("lld_draft", "")
            if draft:
                logger.info(f"[LLD Loop] 📄 Generating docx — draft length={len(draft)} chars")
                result = generate_docx(
                    document_type="LLD",
                    title="Low-Level Design Document",
                    content=draft,
                )
                logger.info(f"[LLD Loop] 📄 {result}")
            else:
                logger.warning("[LLD Loop] ⚠️ decision=valid but lld_draft is empty — skipping docx")
        else:
            logger.info("[LLD Loop] ⏳ Throttling 5s before next iteration (429 prevention)...")
            await asyncio.sleep(5)

        yield Event(author=self.name, actions=EventActions(escalate=should_stop))


def create_lld_pipeline(mcp_toolset=None) -> LoopAgent:
    """Returns the LLD LoopAgent pipeline."""
    writer_tools = []
    if mcp_toolset:
        writer_tools.append(mcp_toolset)
    logger.info(f"[LLD] Creating pipeline — MCP={'yes' if mcp_toolset else 'no'}")

    lld_writer = LlmAgent(
        model=MODEL_PRO,
        name="lld_writer",
        description="Generates and refines LLD document drafts",
        output_key="lld_draft",
        before_agent_callback=_init_lld_state,
        instruction=_LLD_WRITER_INSTRUCTION,
        tools=writer_tools,
    )

    pipeline = LoopAgent(
        name="lld_pipeline",
        description="Generates a Low-Level Design document with iterative critique and refinement",
        max_iterations=3,
        sub_agents=[
            lld_writer,
            _lld_critic,
            _lld_decision,
            _LldLoopController(name="lld_loop_controller"),
        ],
    )
    logger.info("[LLD] Pipeline created: lld_writer → lld_critic → lld_decision → lld_loop_controller")
    return pipeline

