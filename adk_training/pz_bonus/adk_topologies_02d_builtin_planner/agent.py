"""
Bonus 02d: Planner topology - BuiltInPlanner (native model thinking)
====================================================================

``BuiltInPlanner`` adds no prompt text. It only sets the model's
``thinking_config``, so the model plans in its own (native) reasoning.
``include_thoughts=True`` returns thought summaries, visible in ``adk web``.

Gemini 3.x uses ``thinking_level`` (MINIMAL/LOW/MEDIUM/HIGH);
``thinking_budget`` (tokens) is the older Gemini 2.5 knob.

Equivalent without a planner:
    Agent(..., generate_content_config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(...)))
If both are set, the planner wins.

Run (from ``adk_training/pz_bonus``):
    adk web .
"""

import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.planners import BuiltInPlanner
from google.adk.tools import AgentTool
from google.genai import types

load_dotenv()

MODEL = os.getenv("MODEL", "gemini-3.5-flash")

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
    name="employee_assistant_thinking",
    description="Thinks about which experts to consult, consults them and combines the answers.",
    instruction="""You help employees by consulting experts (your tools).
Ask each relevant expert a focused question, then merge their answers into one
short, structured response. Reply in the user's language.""",
    tools=[
        AgentTool(agent=marketing_expert),
        AgentTool(agent=cloud_expert),
        AgentTool(agent=legal_expert),
    ],
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            thinking_level=types.ThinkingLevel.HIGH,
            include_thoughts=True,
        )
    ),
)
