"""
Module 20: Analyst System — Root Agent (starter version)
========================================================
Captain agent that routes user requests to specialized orchestrators
using the AgentTool pattern.

Orchestrators:
- analyze_requirement: Multi-dimensional requirement analysis
- create_epic: Generate Jira Epic with user stories
- generate_document: Create HLD, LLD, tutorials, how-to guides
- generate_test_plan: Create test plan with scenarios
- review_document: Review existing document for quality
- generate_skill: Create Agent Skills from knowledge sources
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool

load_dotenv()

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

# --- Import orchestrators ---
from orchestrators.analyze_requirement import analyze_requirement_orchestrator
from orchestrators.create_epic import create_epic_orchestrator
from orchestrators.generate_document import generate_document_orchestrator
from orchestrators.generate_test_plan import generate_test_plan_orchestrator
from orchestrators.review_document import review_document_orchestrator
from orchestrators.generate_skill import generate_skill_orchestrator

# --- Wrap as tools ---
analyze_tool = AgentTool(agent=analyze_requirement_orchestrator)
epic_tool = AgentTool(agent=create_epic_orchestrator)
document_tool = AgentTool(agent=generate_document_orchestrator)
test_plan_tool = AgentTool(agent=generate_test_plan_orchestrator)
review_tool = AgentTool(agent=review_document_orchestrator)
skill_tool = AgentTool(agent=generate_skill_orchestrator)

# --- Root agent ---
root_agent = LlmAgent(
    model=MODEL,
    name="analyst_captain",
    description="Analyst assistant that helps with requirements, documentation, "
    "epics, test plans, reviews, and skill generation.",
    instruction="""You are an Analyst Assistant — a captain that coordinates specialized teams.

Your job is to route user requests to the right tool and present results clearly.

## Available Tools

| Tool | Use When |
|------|----------|
| `analyze_requirement` | User wants to analyze a requirement, feature, or Jira ticket |
| `create_epic` | User wants to create a Jira Epic with user stories |
| `generate_document` | User wants to create documentation (HLD, LLD, tutorial, how-to, reference, explanation) |
| `generate_test_plan` | User wants test scenarios or a test plan |
| `review_document` | User wants to review/check an existing document |
| `generate_skill` | User wants to create an Agent Skill from knowledge sources |

## Routing Rules

1. Understand the user's intent
2. Select the MOST appropriate tool
3. Pass all relevant context to the tool
4. Present the tool's result to the user
5. Ask follow-up questions if needed

## Multi-step Workflows

Some requests may need multiple tools:
- "Analyze this requirement and create an epic" → analyze_requirement, then create_epic
- "Generate HLD and test plan" → generate_document, then generate_test_plan

Execute sequentially, passing results forward.

## Language

Respond in the same language the user uses.
Default to Polish for documentation-related tasks.
""",
    tools=[analyze_tool, epic_tool, document_tool, test_plan_tool, review_tool, skill_tool],
)
