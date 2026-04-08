"""
HLD Pipeline Agent
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

_TEMPLATE_PATH = Path(__file__).parent.parent.parent / "prompts" / "hld_template.md"
HLD_TEMPLATE = _TEMPLATE_PATH.read_text(encoding="utf-8")


class Decision(BaseModel):
    decision: str = Field(description="Either 'valid' or 'invalid'")
    reason: str = Field(description="Brief explanation of the decision")


async def _init_hld_state(callback_context: CallbackContext):
    callback_context.state.setdefault("user_context", "")
    callback_context.state.setdefault("hld_draft", "")
    callback_context.state.setdefault("hld_critique", "")
    callback_context.state.setdefault("hld_status", {"decision": "invalid", "reason": ""})


async def _throttle(callback_context: CallbackContext):
    """Pauza przed wywołaniem LLM — zapobiega 429 RESOURCE_EXHAUSTED."""
    logger.info(f"[HLD] ⏳ Throttling {THROTTLE_SECONDS}s before LLM call (429 prevention)...")
    await asyncio.sleep(THROTTLE_SECONDS)
    return None


_HLD_WRITER_INSTRUCTION = f"""You are a solution architect writing a High-Level Design document.

DOCUMENT TEMPLATE TO FOLLOW:
{HLD_TEMPLATE}

CONTEXT AVAILABLE IN SESSION STATE:
- {{user_context}}: user-provided specs or feature descriptions
- {{hld_draft}}: previous draft (empty on first iteration)
- {{hld_critique}}: critic feedback to address (empty on first iteration)

INSTRUCTIONS:
1. Review all user-provided context (specs, attachments, descriptions).
2. Use Jira/Wiki tools to fetch additional context if ticket IDs or Wiki pages are mentioned.
3. Write a complete HLD following every section of the template above.
   Make reasonable assumptions for unclear points — document them as assumptions.
4. On subsequent iterations, address ALL points raised in {{hld_critique}}.
5. Output only the document content in markdown format — no preamble, no meta-commentary.

DIAGRAM REQUIREMENTS — MANDATORY:
For every section that describes a diagram, embed a Mermaid code block immediately after the description.
Use ```mermaid ... ``` fences. The document renderer will convert these to images automatically.

Section 5.1 Context Diagram → flowchart showing: internal consumers → Notification Hub → external providers.
IMPORTANT: use simple node labels, avoid subgraph labels with square brackets.
Example pattern:
```mermaid
flowchart LR
    CLM[CLM Core] --> API[Notification API]
    BM[Billing Module] --> API
    RM[Reporting Module] --> API
    API --> SG[SendGrid]
    API --> TW[Twilio / SNS]
    API --> FCM[Firebase FCM]
    SG --> EU((End User))
    TW --> EU
    FCM --> EU
```

Section 5.2 Container Diagram → flowchart showing internal containers and their connections.
Section 8 Data Flow → sequence diagram for the happy-path and error-path flows.
Example sequence pattern:
```mermaid
sequenceDiagram
    participant BS as Billing Service
    participant KF as Kafka
    participant API as Notification API
    participant SG as SendGrid
    BS->>KF: publish PaymentSuccessful
    KF->>API: consume event
    API->>API: create PENDING record
    API->>SG: POST /v3/mail/send
    SG-->>API: 202 Accepted
    API->>API: update status SENT
```

Always generate valid Mermaid syntax. Use short node labels (no special chars except spaces).
"""

_hld_critic = LlmAgent(
    model=MODEL_FLASH,
    name="hld_critic",
    description="Reviews HLD draft for completeness and quality",
    output_key="hld_critique",
    before_agent_callback=_throttle,
    instruction="""You are a senior architect reviewing an HLD document.

Review the draft in {hld_draft} against these criteria:
1. All template sections present and substantive
2. Context and container diagrams are described (text-based is fine)
3. Integration points have protocol/contract details
4. NFR table has concrete targets (not just categories)
5. Risk register has at least 3 entries with mitigations
6. Technology choices are justified
7. No vague placeholder text remains

Provide specific, actionable critique for each gap found.
If fully satisfactory, write exactly: "No improvements needed."
""",
)

_hld_decision = LlmAgent(
    model=MODEL_FLASH,
    name="hld_decision",
    description="Decides if HLD is ready for finalization",
    output_key="hld_status",
    output_schema=Decision,
    before_agent_callback=_throttle,
    instruction="""You are the approving architect for HLD documents.

Draft: {hld_draft}
Critique: {hld_critique}

Decision rules:
- If critique says "No improvements needed" → decision: "valid"
- If there are unresolved issues → decision: "invalid"

Output your decision in the required schema.
""",
)


class _HldLoopController(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("hld_status", {})
        decision = status.get("decision", "invalid") if isinstance(status, dict) else "invalid"
        reason = status.get("reason", "") if isinstance(status, dict) else ""
        should_stop = decision == "valid"

        logger.info(f"[HLD Loop] decision={decision} | reason={reason} | stop={should_stop}")

        if should_stop:
            draft = ctx.session.state.get("hld_draft", "")
            if draft:
                logger.info(f"[HLD Loop] 📄 Generating docx — draft length={len(draft)} chars")
                result = generate_docx(
                    document_type="HLD",
                    title="High-Level Design Document",
                    content=draft,
                )
                logger.info(f"[HLD Loop] 📄 {result}")
            else:
                logger.warning("[HLD Loop] ⚠️ decision=valid but hld_draft is empty — skipping docx")
        else:
            logger.info("[HLD Loop] ⏳ Throttling 5s before next iteration (429 prevention)...")
            await asyncio.sleep(5)

        yield Event(author=self.name, actions=EventActions(escalate=should_stop))


def create_hld_pipeline(mcp_toolset=None) -> LoopAgent:
    """Returns the HLD LoopAgent pipeline."""
    writer_tools = []
    if mcp_toolset:
        writer_tools.append(mcp_toolset)
    logger.info(f"[HLD] Creating pipeline — MCP={'yes' if mcp_toolset else 'no'}")

    hld_writer = LlmAgent(
        model=MODEL_PRO,
        name="hld_writer",
        description="Generates and refines HLD document drafts",
        output_key="hld_draft",
        before_agent_callback=_init_hld_state,
        instruction=_HLD_WRITER_INSTRUCTION,
        tools=writer_tools,
    )

    pipeline = LoopAgent(
        name="hld_pipeline",
        description="Generates a High-Level Design document with iterative critique and refinement",
        max_iterations=3,
        sub_agents=[
            hld_writer,
            _hld_critic,
            _hld_decision,
            _HldLoopController(name="hld_loop_controller"),
        ],
    )
    logger.info("[HLD] Pipeline created: hld_writer → hld_critic → hld_decision → hld_loop_controller")
    return pipeline

