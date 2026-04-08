"""
Test Cases Pipeline Agent
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

_TEMPLATE_PATH = Path(__file__).parent.parent.parent / "prompts" / "test_cases_template.md"
TC_TEMPLATE = _TEMPLATE_PATH.read_text(encoding="utf-8")


class Decision(BaseModel):
    decision: str = Field(description="Either 'valid' or 'invalid'")
    reason: str = Field(description="Brief explanation of the decision")


async def _init_tc_state(callback_context: CallbackContext):
    callback_context.state.setdefault("user_context", "")
    callback_context.state.setdefault("tc_draft", "")
    callback_context.state.setdefault("tc_critique", "")
    callback_context.state.setdefault("tc_status", {"decision": "invalid", "reason": ""})


async def _throttle(callback_context: CallbackContext):
    """Pauza przed wywołaniem LLM — zapobiega 429 RESOURCE_EXHAUSTED."""
    logger.info(f"[TC] ⏳ Throttling {THROTTLE_SECONDS}s before LLM call (429 prevention)...")
    await asyncio.sleep(THROTTLE_SECONDS)
    return None


_TC_WRITER_INSTRUCTION = f"""You are a QA lead writing a Test Case specification document.

DOCUMENT TEMPLATE TO FOLLOW:
{TC_TEMPLATE}

CONTEXT AVAILABLE IN SESSION STATE:
- {{user_context}}: user-provided feature specs or acceptance criteria
- {{tc_draft}}: previous draft (empty on first iteration)
- {{tc_critique}}: critic feedback to address (empty on first iteration)

INSTRUCTIONS:
1. Review user context and any Jira/Wiki data available.
2. Use Jira/Wiki tools to fetch acceptance criteria or existing test docs if ticket IDs are mentioned.
3. Write a complete test specification following every section of the template.
   Make reasonable assumptions for unclear points — document them as assumptions.
4. Create at least 5 positive test cases, 3 negative/edge cases, and 1 NFR test.
5. Each TC must have a unique TC-ID, clear steps, and concrete expected results.
6. On subsequent iterations, address ALL points raised in {{tc_critique}}.
7. Output only the document content in markdown format — no preamble, no meta-commentary.
"""

_tc_critic = LlmAgent(
    model=MODEL_FLASH,
    name="tc_critic",
    description="Reviews Test Cases draft for completeness and quality",
    output_key="tc_critique",
    before_agent_callback=_throttle,
    instruction="""You are a QA manager reviewing a Test Case specification.

Review the draft in {tc_draft} against these criteria:
1. All template sections are present and non-empty
2. Each test case has: unique TC-ID, clear preconditions, numbered steps, specific expected result
3. Minimum coverage: 5 positive, 3 negative/edge, 1 NFR test case
4. Traceability matrix maps requirements to test cases
5. Exit criteria are specific and measurable
6. No vague expected results (e.g. "works correctly" is NOT acceptable)

Provide specific critique for each gap.
If fully satisfactory, write exactly: "No improvements needed."
""",
)

_tc_decision = LlmAgent(
    model=MODEL_FLASH,
    name="tc_decision",
    description="Decides if Test Cases doc is ready for finalization",
    output_key="tc_status",
    output_schema=Decision,
    before_agent_callback=_throttle,
    instruction="""You are the QA lead approving a test specification.

Draft: {tc_draft}
Critique: {tc_critique}

Decision rules:
- If critique says "No improvements needed" → decision: "valid"
- If there are unresolved issues → decision: "invalid"

Output your decision in the required schema.
""",
)


class _TcLoopController(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("tc_status", {})
        decision = status.get("decision", "invalid") if isinstance(status, dict) else "invalid"
        reason = status.get("reason", "") if isinstance(status, dict) else ""
        should_stop = decision == "valid"

        logger.info(f"[TC Loop] decision={decision} | reason={reason} | stop={should_stop}")

        if should_stop:
            draft = ctx.session.state.get("tc_draft", "")
            if draft:
                logger.info(f"[TC Loop] 📄 Generating docx — draft length={len(draft)} chars")
                result = generate_docx(
                    document_type="TEST_CASES",
                    title="Test Case Specification",
                    content=draft,
                )
                logger.info(f"[TC Loop] 📄 {result}")
            else:
                logger.warning("[TC Loop] ⚠️ decision=valid but tc_draft is empty — skipping docx")
        else:
            logger.info("[TC Loop] ⏳ Throttling 5s before next iteration (429 prevention)...")
            await asyncio.sleep(5)

        yield Event(author=self.name, actions=EventActions(escalate=should_stop))


def create_test_cases_pipeline(mcp_toolset=None) -> LoopAgent:
    """Returns the Test Cases LoopAgent pipeline."""
    writer_tools = []
    if mcp_toolset:
        writer_tools.append(mcp_toolset)
    logger.info(f"[TC] Creating pipeline — MCP={'yes' if mcp_toolset else 'no'}")

    tc_writer = LlmAgent(
        model=MODEL_PRO,
        name="tc_writer",
        description="Generates and refines Test Case specification drafts",
        output_key="tc_draft",
        before_agent_callback=_init_tc_state,
        instruction=_TC_WRITER_INSTRUCTION,
        tools=writer_tools,
    )

    pipeline = LoopAgent(
        name="test_cases_pipeline",
        description="Generates a Test Case specification with iterative critique and refinement",
        max_iterations=3,
        sub_agents=[
            tc_writer,
            _tc_critic,
            _tc_decision,
            _TcLoopController(name="tc_loop_controller"),
        ],
    )
    logger.info("[TC] Pipeline created: tc_writer → tc_critic → tc_decision → tc_loop_controller")
    return pipeline

