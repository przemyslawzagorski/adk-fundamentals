"""
Skill tools — manage Agent Skills (agentskills.io) in the skills/ directory.

Provides CRUD operations for skills: listing, reading metadata, reading full content,
writing drafts, and validating skill names against the specification.
"""

import os
import re
from pathlib import Path

import yaml


_SKILL_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]{0,62}[a-z0-9]$")
_RESERVED_NAMES = frozenset({"scripts", "references", "assets", "test", "tests"})
_MAX_DESCRIPTION_LENGTH = 1024
_MAX_BODY_LINES = 500


def _skills_dir() -> Path:
    return Path(os.environ.get("SKILLS_DIR", "./skills"))


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from SKILL.md content, return (metadata, body)."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        meta = {}
    body = parts[2].lstrip("\n")
    return meta, body


def validate_skill_name(name: str) -> dict:
    """Validate a skill name against the Agent Skills specification.

    Rules: lowercase letters, digits and hyphens, 2-64 chars, not reserved.

    Args:
        name: Proposed skill name.

    Returns:
        dict with 'valid' (bool) and 'issues' list.
    """
    issues = []
    if not name:
        issues.append("Name cannot be empty")
    elif not _SKILL_NAME_PATTERN.match(name):
        issues.append(
            "Name must be 2-64 chars, lowercase letters/digits/hyphens, "
            "start with letter, end with letter or digit"
        )
    if name in _RESERVED_NAMES:
        issues.append(f"'{name}' is a reserved name")
    if len(name) > 64:
        issues.append(f"Name too long: {len(name)} chars (max 64)")
    return {"valid": len(issues) == 0, "issues": issues}


def list_skills(skills_dir: str = "") -> dict:
    """List all skills with their metadata (name, description, file count).

    Args:
        skills_dir: Override path to skills directory (uses SKILLS_DIR env var if empty).

    Returns:
        dict with 'status' and 'skills' list containing name, description, file_count.
    """
    try:
        base = Path(skills_dir) if skills_dir else _skills_dir()
        if not base.is_dir():
            return {"status": "ok", "skills": []}
        skills = []
        for entry in sorted(base.iterdir()):
            skill_md = entry / "SKILL.md"
            if entry.is_dir() and skill_md.is_file():
                content = skill_md.read_text(encoding="utf-8")
                meta, _ = _parse_frontmatter(content)
                file_count = sum(1 for _ in entry.rglob("*") if _.is_file())
                skills.append({
                    "name": meta.get("name", entry.name),
                    "description": meta.get("description", ""),
                    "metadata": meta.get("metadata", {}),
                    "file_count": file_count,
                })
        return {"status": "ok", "skills": skills, "count": len(skills)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_skill_metadata(skill_name: str) -> dict:
    """Read only YAML frontmatter metadata for a skill (fast, for bulk comparison).

    Args:
        skill_name: Name of the skill folder.

    Returns:
        dict with 'status' and 'metadata' or 'error_message'.
    """
    try:
        skill_md = _skills_dir() / skill_name / "SKILL.md"
        if not skill_md.is_file():
            return {"status": "error", "error_message": f"Skill '{skill_name}' not found"}
        content = skill_md.read_text(encoding="utf-8")
        meta, _ = _parse_frontmatter(content)
        return {"status": "ok", "metadata": meta, "skill_name": skill_name}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def read_skill(skill_name: str) -> dict:
    """Read full SKILL.md content + list reference/asset files for a skill.

    Args:
        skill_name: Name of the skill folder.

    Returns:
        dict with 'status', 'content', 'references', 'assets', or 'error_message'.
    """
    try:
        skill_dir = _skills_dir() / skill_name
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            return {"status": "error", "error_message": f"Skill '{skill_name}' not found"}
        content = skill_md.read_text(encoding="utf-8")

        references = {}
        refs_dir = skill_dir / "references"
        if refs_dir.is_dir():
            for f in sorted(refs_dir.glob("*")):
                if f.is_file():
                    references[f.name] = f.read_text(encoding="utf-8")

        assets = []
        assets_dir = skill_dir / "assets"
        if assets_dir.is_dir():
            assets = sorted(f.name for f in assets_dir.glob("*") if f.is_file())

        return {
            "status": "ok",
            "content": content,
            "references": references,
            "assets": assets,
            "skill_name": skill_name,
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def write_skill_draft(
    skill_name: str,
    skill_md_content: str,
    references: dict[str, str] | None = None,
    assets: dict[str, str] | None = None,
) -> dict:
    """Write a skill to skills/{skill_name}/SKILL.md + optional reference/asset files.

    Creates the directory if needed. This is used after human approval.

    Args:
        skill_name: Name matching the folder name (validated against spec).
        skill_md_content: Full SKILL.md content including YAML frontmatter.
        references: Optional dict of {filename: content} for references/ dir.
        assets: Optional dict of {filename: content} for assets/ dir.

    Returns:
        dict with 'status', 'created_files' list, or 'error_message'.
    """
    validation = validate_skill_name(skill_name)
    if not validation["valid"]:
        return {"status": "error", "error_message": f"Invalid name: {validation['issues']}"}

    try:
        skill_dir = _skills_dir() / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        created_files = []

        skill_md_path = skill_dir / "SKILL.md"
        skill_md_path.write_text(skill_md_content, encoding="utf-8")
        created_files.append(str(skill_md_path))

        if references:
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(exist_ok=True)
            for fname, fcontent in references.items():
                fpath = refs_dir / fname
                fpath.write_text(fcontent, encoding="utf-8")
                created_files.append(str(fpath))

        if assets:
            assets_dir = skill_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            for fname, fcontent in assets.items():
                fpath = assets_dir / fname
                fpath.write_text(fcontent, encoding="utf-8")
                created_files.append(str(fpath))

        return {"status": "ok", "created_files": created_files}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
