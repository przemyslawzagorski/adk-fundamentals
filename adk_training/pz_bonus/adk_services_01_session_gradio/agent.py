"""
Bonus Services 01: Session state in your own UI (agent part)
=============================================================

State scopes used here (prefix decides where ADK stores the value):

* ``user:profile``      - per user, shared by all of that user's sessions,
* ``user:preferences``  - per user, written by the ``remember_preference`` tool,
* ``now``               - per session, refreshed before every turn.

``{user:profile}`` / ``{now}`` / ``{user:preferences?}`` in the instruction are
filled from session state on every turn (``?`` = optional).

The custom Gradio UI lives in ``ui.py``; the agent also works in ``adk web``
(a guest profile is seeded when the UI did not provide one).
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext

load_dotenv()

MODEL = os.getenv("ADK_MODEL", "gemini-3.5-flash-lite")

GUEST_PROFILE = {"name": "Guest", "role": "unknown", "language": "en"}


def refresh_context(callback_context: CallbackContext) -> None:
    """Runs before every agent turn: keeps `now` fresh and seeds a profile."""
    state = callback_context.state
    state["now"] = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M (%A, UTC%z)")
    if "user:profile" not in state:
        state["user:profile"] = GUEST_PROFILE


def remember_preference(key: str, value: str, tool_context: ToolContext) -> dict:
    """Stores a user preference that persists across all of the user's sessions.

    Args:
        key: Short snake_case name, e.g. "favourite_drink" or "answer_style".
        value: The preference value.

    Returns:
        dict: All stored preferences after the update.
    """
    preferences = dict(tool_context.state.get("user:preferences", {}))
    preferences[key] = value
    tool_context.state["user:preferences"] = preferences
    return {"status": "saved", "preferences": preferences}


root_agent = Agent(
    model=MODEL,
    name="personal_assistant",
    description="Assistant that personalises answers using session and user state.",
    instruction="""You are a helpful personal assistant.

Current user profile: {user:profile}
User preferences: {user:preferences?}
Current time: {now}

- Use the profile and preferences to personalise answers.
- When the user states a lasting preference ("I prefer...", "always...",
  "remember that..."), call `remember_preference`.
- Reply in the language from the profile unless the user writes in another one.""",
    tools=[remember_preference],
    before_agent_callback=refresh_context,
)
