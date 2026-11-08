"""
Bonus Services 01: Session state in your own UI (Gradio front-end)
==================================================================

Shows what ``adk web`` normally hides:

* ``Runner`` + ``SessionService`` wired by hand,
* one ADK session per browser tab (``gr.State``), not one global session,
* ``user:`` state shared between sessions of the same user,
* live preview of the session state after every turn.

Run (from ``adk_training/d1_05_runner_session_gradio``):
    python ui.py
Then open http://127.0.0.1:7860
"""

import gradio as gr
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

try:
    from .agent import root_agent
except ImportError:
    from agent import root_agent

APP_NAME = "d1_05_runner_session_gradio"

# Fictional demo users - never put real personal data into training code.
USERS = {
    "anna": {"name": "Anna Nowak", "role": "Data Engineer", "city": "Kraków", "language": "pl"},
    "john": {"name": "John Smith", "role": "Sales Manager", "city": "London", "language": "en"},
}

# InMemory = state is lost on restart. Swap for
# DatabaseSessionService(db_url="sqlite+aiosqlite:///./sessions.db") to persist.
session_service = InMemorySessionService()
runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)


async def _new_session(user_id: str):
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        state={"user:profile": USERS[user_id]},
    )
    return session


async def _state_of(user_id: str, session_id: str) -> dict:
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    return dict(session.state) if session else {}


async def start_session(user_id: str):
    """New conversation for the selected user (user: state is kept)."""
    session = await _new_session(user_id)
    return [], session.id, await _state_of(user_id, session.id)


async def chat(message: str, history: list, user_id: str, session_id: str | None):
    if not message.strip():
        return "", history, session_id, await _state_of(user_id, session_id or "")
    if not session_id:
        session_id = (await _new_session(user_id)).id

    reply = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(role="user", parts=[types.Part(text=message)]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            reply += [p.text for p in event.content.parts if p.text and not p.thought]

    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": "\n".join(reply) or "(no answer)"},
    ]
    return "", history, session_id, await _state_of(user_id, session_id)


with gr.Blocks(title="ADK - session state demo") as demo:
    gr.Markdown(
        "## ADK session state demo\n"
        "Try: *What do you know about me?* -> *Remember I prefer short answers* -> "
        "**New session** -> *How should you answer me?*"
    )
    session_id = gr.State(None)
    with gr.Row():
        with gr.Column(scale=3):
            user = gr.Dropdown(choices=list(USERS), value="anna", label="User (user_id)")
            chatbot = gr.Chatbot(height=420)
            message = gr.Textbox(placeholder="Ask something...", show_label=False)
            new_session = gr.Button("New session")
        with gr.Column(scale=2):
            gr.Markdown("### Session state (`session.state`)")
            state_view = gr.JSON()

    message.submit(
        chat,
        inputs=[message, chatbot, user, session_id],
        outputs=[message, chatbot, session_id, state_view],
    )
    new_session.click(start_session, inputs=[user], outputs=[chatbot, session_id, state_view])
    user.change(start_session, inputs=[user], outputs=[chatbot, session_id, state_view])
    demo.load(start_session, inputs=[user], outputs=[chatbot, session_id, state_view])


if __name__ == "__main__":
    demo.launch()
