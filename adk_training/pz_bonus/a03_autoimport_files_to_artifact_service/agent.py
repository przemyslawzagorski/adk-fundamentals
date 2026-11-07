"""
Bonus A03: Auto-import uploaded files to the Artifact Service (Plugins + App)
=============================================================================

``SaveFilesAsArtifactsPlugin`` intercepts every user message. Each attached
file (inline_data) is saved as a session-scoped artifact and replaced in the
prompt by a short placeholder ``[Uploaded Artifact: "<name>"]``. The model
sees the file only when it calls ``load_artifacts`` - this keeps big files out
of the conversation history and the token bill.

Plugins are registered on an ``App``, not on an ``Agent``.

Run (from ``adk_training/pz_bonus``):
    adk web .
Exercise solutions: ``agent_solution.py``.
"""

import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.apps import App
from google.adk.plugins.save_files_as_artifacts_plugin import (
    SaveFilesAsArtifactsPlugin,
)
from google.adk.tools import load_artifacts

load_dotenv()

MODEL = os.getenv("MODEL", "gemini-3.5-flash")

root_agent = Agent(
    name="file_assistant",
    model=MODEL,
    description="Answers questions about files uploaded by the user.",
    instruction="""You help the user work with files they upload (images, PDFs, text).

Uploaded files appear in the message as [Uploaded Artifact: "<name>"].
To read a file's content, call `load_artifacts` with its name. Load only the
files you need for the current question.
Never guess the content of a file you have not loaded.
Reply in the user's language.""",
    tools=[load_artifacts],
)

# Keep the App name equal to the folder name - `adk web` derives the app name
# from the folder and warns about a mismatch.
app = App(
    name="a03_autoimport_files_to_artifact_service",
    root_agent=root_agent,
    plugins=[SaveFilesAsArtifactsPlugin()],
)
