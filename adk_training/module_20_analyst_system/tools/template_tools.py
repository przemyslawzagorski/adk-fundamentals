"""
Template tools — load and render document templates from skills/document-templates/assets/.
"""

import os
from pathlib import Path


def list_templates() -> dict:
    """List all available document templates.

    Returns:
        dict with 'status' and 'templates' list (name + first-line description).
    """
    try:
        skills_dir = Path(os.environ.get("SKILLS_DIR", "./skills"))
        assets_dir = skills_dir / "document-templates" / "assets"
        if not assets_dir.is_dir():
            return {"status": "ok", "templates": [], "message": "No templates directory found"}
        templates = []
        for f in sorted(assets_dir.glob("*.md")):
            first_line = f.read_text(encoding="utf-8").split("\n", 1)[0].strip("# \n")
            templates.append({"name": f.stem, "file": f.name, "title": first_line})
        return {"status": "ok", "templates": templates}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def load_template(template_name: str) -> dict:
    """Load a document template by name.

    Args:
        template_name: Template name without extension (e.g. 'hld_template').

    Returns:
        dict with 'status' and 'content' or 'error_message'.
    """
    try:
        skills_dir = Path(os.environ.get("SKILLS_DIR", "./skills"))
        template_path = skills_dir / "document-templates" / "assets" / f"{template_name}.md"
        if not template_path.is_file():
            return {
                "status": "error",
                "error_message": f"Template '{template_name}' not found at {template_path}",
            }
        content = template_path.read_text(encoding="utf-8")
        return {"status": "ok", "content": content, "template_name": template_name}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
