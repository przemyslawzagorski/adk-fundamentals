"""
Bonus 02c: Planner topology - PlanReActPlanner + experts as tools
=================================================================

``PlanReActPlanner`` makes the model write an explicit plan in text
(``/*PLANNING*/``, ``/*ACTION*/``, ``/*REASONING*/``, ``/*REPLANNING*/``,
``/*FINAL_ANSWER*/``). ADK marks everything except the final answer as
"thought", so in ``adk web`` the plan is visible in the event trace.

It works with any model, including models without built-in thinking.
Compare with ``d1_11b_builtin_planner``.

Run (from ``adk_training/pz_bonus``):
    adk web .
"""

import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.planners import PlanReActPlanner
from google.adk.tools import AgentTool

load_dotenv()

MODEL = os.getenv("ADK_MODEL", "gemini-3.5-flash-lite")

marketing_expert = Agent(
    model=MODEL,
    name="marketing_expert",
    description="Answers questions about marketing strategy, positioning and campaigns.",
    instruction="You are a B2B marketing specialist. Answer concisely (max 150 words).",
)

cloud_expert = Agent(
    model=MODEL,
    name="google_cloud_expert",
    description="Answers questions about Google Cloud products and architecture.",
    instruction="You are a Google Cloud architect. Answer concisely (max 150 words).",
)

legal_expert = Agent(
    model=MODEL,
    name="legal_expert",
    description="Answers questions about law, compliance and GDPR.",
    instruction="You are an EU legal and compliance specialist. Answer concisely (max 150 words).",
)

root_agent = Agent(
    model=MODEL,
    name="employee_assistant_react",
    description="Plans which experts to consult, consults them and combines the answers.",
    instruction="""You help employees by consulting experts (your tools).
Ask each relevant expert a focused question, then merge their answers into one
short, structured response. Reply in the user's language.""",
    tools=[
        AgentTool(agent=marketing_expert),
        AgentTool(agent=cloud_expert),
        AgentTool(agent=legal_expert),
    ],
    planner=PlanReActPlanner(),
)
