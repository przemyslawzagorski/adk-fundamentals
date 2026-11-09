"""
Bonus A03 - exercise solutions
==============================

1. ``list_files``         - list artifacts with metadata (no bytes in the prompt)
2. ``list_files`` filter  - filter by kind: image / pdf / text / all
3. ``analyze_file``       - automatic analysis after upload; the summary is
                            saved as a separate Markdown artifact

Run the solution in ``adk web`` by changing ``__init__.py`` to:
    from .agent_solution import app
"""

import os
from typing import Literal, Optional

from dotenv import load_dotenv
from google import genai
from google.adk import Agent
from google.adk.apps import App
from google.adk.plugins.save_files_as_artifacts_plugin import (
    SaveFilesAsArtifactsPlugin,
)
from google.adk.tools import ToolContext, load_artifacts
from google.genai import types

load_dotenv()

MODEL = os.getenv("ADK_MODEL", "gemini-3.5-flash-lite")

FileKind = Literal["image", "pdf", "text", "all"]
_KIND_PREFIX = {"image": "image/", "pdf": "application/pdf", "text": "text/", "all": ""}
SUMMARY_SUFFIX = ".summary.md"

_client: Optional[genai.Client] = None


def _genai_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


# =============================================================================
# EXERCISES 1 + 2: metadata listing with an optional type filter
# =============================================================================


async def list_files(tool_context: ToolContext, kind: FileKind = "all") -> dict:
    """Lists uploaded files with metadata, optionally filtered by kind.

    Uses `get_artifact_version`, which returns metadata only - file bytes never
    enter the LLM context.

    Args:
        kind: "image", "pdf", "text" or "all".

    Returns:
        dict: number of matching files and their metadata.
    """
    prefix = _KIND_PREFIX[kind]
    files = []
    for name in await tool_context.list_artifacts():
        info = await tool_context.get_artifact_version(name)
        mime_type = (info.mime_type if info else None) or "unknown"
        if prefix and not mime_type.startswith(prefix):
            continue
        files.append(
            {
                "name": name,
                "mime_type": mime_type,
                "latest_version": info.version if info else None,
                "scope": "user" if name.startswith("user:") else "session",
            }
        )
    return {"kind": kind, "count": len(files), "files": files}


# =============================================================================
# EXERCISE 3: automatic analysis saved as a new artifact
# =============================================================================


async def analyze_file(filename: str, tool_context: ToolContext) -> dict:
    """Analyzes an uploaded file and stores the summary as `<filename>.summary.md`.

    Args:
        filename: Artifact name exactly as shown in [Uploaded Artifact: "..."].

    Returns:
        dict: status, the summary text and the name of the summary artifact.
    """
    artifact = await tool_context.load_artifact(filename)
    if artifact is None:
        return {"status": "error", "error": f"Artifact '{filename}' not found."}
    if artifact.inline_data is None:
        return {"status": "error", "error": f"Artifact '{filename}' has no binary content."}

    response = await _genai_client().aio.models.generate_content(
        model=MODEL,
        contents=[
            artifact,
            "Analyze this file. Return Markdown with sections: "
            "**Type**, **Summary** (2-3 sentences), **Key details** (bullets), "
            "**Suggested next steps** (bullets).",
        ],
    )
    summary = response.text or ""
    summary_name = f"{filename}{SUMMARY_SUFFIX}"
    version = await tool_context.save_artifact(
        summary_name,
        types.Part.from_bytes(data=summary.encode("utf-8"), mime_type="text/markdown"),
        custom_metadata={"source": filename},
    )
    return {
        "status": "success",
        "source": filename,
        "mime_type": artifact.inline_data.mime_type,
        "summary_artifact": summary_name,
        "summary_version": version,
        "summary": summary,
    }


root_agent = Agent(
    name="file_manager",
    model=MODEL,
    description="Manages uploaded files: lists, filters and analyzes them.",
    instruction=f"""You are a file management assistant.

Uploaded files appear in the message as [Uploaded Artifact: "<name>"].

Rules:
1. For EVERY new [Uploaded Artifact: "<name>"] call `analyze_file` with that
   exact name, then present the summary and suggest next steps.
2. Questions like "what files do I have" / "show only images" -> `list_files`
   with the right `kind`. Hide artifacts ending with "{SUMMARY_SUFFIX}" unless asked.
3. Detailed questions about a file's content -> `load_artifacts` for that file.
4. Never guess the content of a file you have not analyzed or loaded.

Reply in the user's language.""",
    tools=[list_files, analyze_file, load_artifacts],
)

app = App(
    name="d2_01x_ext_autoimport_artifacts",
    root_agent=root_agent,
    plugins=[SaveFilesAsArtifactsPlugin()],
)
