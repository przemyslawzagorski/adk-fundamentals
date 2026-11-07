"""
Bonus A01: Image studio - tools, ToolContext and versioned artifacts
====================================================================

The agent generates and edits images with a Gemini image model
("Nano Banana", ``gemini-2.5-flash-image``) and stores every result in the
Artifact Service:

* ``generate_image`` -> creates a new artifact (or a new version of it),
* ``edit_image``     -> loads an artifact (any version), edits it and saves the
                        result as the next version of the same file,
* ``list_images``    -> reads artifact metadata without downloading bytes,
* ``load_artifacts`` -> built-in tool that lets the LLM *see* an artifact.

Run (from ``adk_training/pz_bonus``):
    adk web .
"""

import logging
import os
from datetime import datetime
from typing import Literal, Optional

from dotenv import load_dotenv
from google import genai
from google.adk import Agent
from google.adk.tools import ToolContext, load_artifacts
from google.genai import types

load_dotenv()

logger = logging.getLogger(__name__)

MODEL = os.getenv("MODEL", "gemini-3.5-flash")
# Imagen 3/4 are not available on the `global` endpoint used in this training;
# Gemini image models are, and they can also edit an existing image.
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-2.5-flash-image")

AspectRatio = Literal["1:1", "3:4", "4:3", "9:16", "16:9"]

_client: Optional[genai.Client] = None


def _genai_client() -> genai.Client:
    global _client
    if _client is None:
        # Image models have low per-minute quotas; retry 429/5xx with backoff.
        _client = genai.Client(
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=5, initial_delay=4.0)
            )
        )
    return _client


def _artifact_name(filename: str) -> str:
    """`user:` scope keeps images across sessions of the same user."""
    name = filename.strip().removeprefix("user:")
    if not name.lower().endswith(".png"):
        name += ".png"
    return f"user:{name}"


async def _render(contents: list, aspect_ratio: Optional[str] = None) -> types.Part:
    response = await _genai_client().aio.models.generate_content(
        model=IMAGE_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=(
                types.ImageConfig(aspect_ratio=aspect_ratio) if aspect_ratio else None
            ),
        ),
    )
    for candidate in response.candidates or []:
        for part in (candidate.content.parts if candidate.content else None) or []:
            if part.inline_data and part.inline_data.data:
                return types.Part.from_bytes(
                    data=part.inline_data.data,
                    mime_type=part.inline_data.mime_type or "image/png",
                )
    reason = response.candidates[0].finish_reason if response.candidates else None
    raise RuntimeError(f"Model returned no image (finish_reason={reason}).")


async def generate_image(
    prompt: str,
    tool_context: ToolContext,
    filename: str = "image.png",
    aspect_ratio: AspectRatio = "1:1",
) -> dict:
    """Generates a new image from a text prompt and saves it as an artifact.

    Saving to an existing filename creates a new version of that artifact.

    Args:
        prompt: Detailed, English description of the image to create.
        filename: Artifact file name, e.g. "cat_f1.png".
        aspect_ratio: One of "1:1", "3:4", "4:3", "9:16", "16:9".

    Returns:
        dict: status, artifact name and the saved version number.
    """
    name = _artifact_name(filename)
    try:
        image = await _render([prompt], aspect_ratio)
    except Exception as e:
        logger.warning("Image generation failed: %s", e)
        return {"status": "error", "error": f"{type(e).__name__}: {e}"}
    version = await tool_context.save_artifact(name, image)
    return {"status": "success", "artifact": name, "version": version}


async def edit_image(
    instruction: str,
    tool_context: ToolContext,
    filename: str = "image.png",
    source_version: Optional[int] = None,
) -> dict:
    """Edits an existing image artifact and saves the result as its next version.

    Args:
        instruction: What to change, e.g. "put a racing helmet on the cat".
        filename: Name of the artifact to edit.
        source_version: Version to start from; omit to use the latest one.

    Returns:
        dict: status, artifact name, source version and the new version number.
    """
    name = _artifact_name(filename)
    source = await tool_context.load_artifact(name, version=source_version)
    if source is None:
        return {
            "status": "error",
            "error": f"Artifact {name} (version {source_version}) not found.",
        }
    try:
        image = await _render([source, instruction])
    except Exception as e:
        logger.warning("Image edit failed: %s", e)
        return {"status": "error", "error": f"{type(e).__name__}: {e}"}
    version = await tool_context.save_artifact(name, image)
    return {
        "status": "success",
        "artifact": name,
        "source_version": source_version if source_version is not None else "latest",
        "version": version,
    }


async def list_images(tool_context: ToolContext) -> dict:
    """Lists saved artifacts with their latest version, MIME type and creation time."""
    files = []
    for name in await tool_context.list_artifacts():
        info = await tool_context.get_artifact_version(name)
        files.append(
            {
                "artifact": name,
                "latest_version": info.version if info else None,
                "mime_type": info.mime_type if info else None,
                "created": (
                    datetime.fromtimestamp(info.create_time).isoformat(timespec="seconds")
                    if info and info.create_time
                    else None
                ),
            }
        )
    return {"count": len(files), "files": files}


root_agent = Agent(
    name="image_studio",
    model=MODEL,
    description="Generates and edits images and keeps them as versioned artifacts.",
    instruction="""You are a friendly image studio assistant.

Tools:
- `generate_image` - create a NEW picture. Turn the user's idea into a rich,
  English prompt (subject, setting, lighting, style, camera). Pick a short
  snake_case filename that describes the picture.
- `edit_image` - change an EXISTING picture ("make it night", "add a helmet").
  Reuse the same filename so the result becomes the next version. Use
  `source_version` only when the user wants to go back to an older version.
- `list_images` - show what is stored (name, latest version, type).
- `load_artifacts` - look at a stored image when the user asks about its
  content; never call it right after generating.

After a successful call, tell the user the artifact name and version.
If a tool returns status "error", explain the error; do not pretend it worked.
Reply in the user's language.""",
    tools=[generate_image, edit_image, list_images, load_artifacts],
)
