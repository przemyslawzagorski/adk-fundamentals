"""
Dynamic instruction builder — constructs agent instructions enriched with
project contract data and dynamically loaded skills.
"""

import json
from pathlib import Path

from contract.project_knowledge import ProjectKnowledgeContract
from tools.skill_tools import list_skills, read_skill


def load_contract(contract_path: str) -> ProjectKnowledgeContract:
    """Load project knowledge contract from JSON file."""
    raw = Path(contract_path).read_text(encoding="utf-8")
    return ProjectKnowledgeContract.model_validate_json(raw)


def _format_contract_context(contract: ProjectKnowledgeContract) -> str:
    """Format contract into a concise context block for agent instructions."""
    lines = [
        f"Project: {contract.project_name}",
        f"Domain: {contract.domain.domain}",
        f"Key entities: {', '.join(contract.domain.key_entities[:10])}",
    ]
    if contract.domain.glossary:
        terms = [f"  - {k}: {v}" for k, v in list(contract.domain.glossary.items())[:10]]
        lines.append("Glossary:\n" + "\n".join(terms))
    if contract.documentation.style_notes:
        lines.append("Style notes:\n" + "\n".join(
            f"  - {n}" for n in contract.documentation.style_notes
        ))
    lines.append(f"Doc language: {contract.documentation.primary_language.value}")
    lines.append(f"Doc framework: {contract.documentation.framework.value}")
    if contract.tech_stack:
        lines.append(f"Tech stack: {', '.join(contract.tech_stack[:8])}")
    return "\n".join(lines)


def build_base_instruction(contract: ProjectKnowledgeContract, agent_role: str) -> str:
    """Build base instruction with project context for any agent.

    Args:
        contract: Project knowledge contract.
        agent_role: Description of the agent's role for the system prompt preamble.
    """
    context = _format_contract_context(contract)
    return f"""{agent_role}

## Project Context

{context}
"""


def build_instruction_with_skills(
    contract: ProjectKnowledgeContract,
    agent_role: str,
    skill_names: list[str] | None = None,
    skills_dir: str = "",
) -> str:
    """Build instruction enriched with specific skills.

    Args:
        contract: Project knowledge contract.
        agent_role: Description of the agent's role.
        skill_names: Explicit list of skill names to load. If None, no skills loaded.
        skills_dir: Override path to skills directory.
    """
    instruction = build_base_instruction(contract, agent_role)

    if not skill_names:
        return instruction

    for name in skill_names:
        result = read_skill(name)
        if result["status"] == "ok":
            instruction += f"\n\n---\n## Skill: {name}\n\n{result['content']}"

    return instruction


def discover_relevant_skills(topic: str, skills_dir: str = "") -> list[str]:
    """Find skills relevant to a given topic by matching description keywords.

    Simple keyword matching — scans skill descriptions for topic terms.

    Args:
        topic: Topic string, e.g. "billing HLD" or "SIM lifecycle".

    Returns:
        List of matching skill names.
    """
    result = list_skills(skills_dir)
    if result["status"] != "ok":
        return []

    topic_lower = topic.lower()
    topic_words = set(topic_lower.split())

    matched = []
    for skill in result["skills"]:
        desc_lower = skill.get("description", "").lower()
        name_lower = skill.get("name", "").lower()
        combined = f"{name_lower} {desc_lower}"
        if any(word in combined for word in topic_words if len(word) > 2):
            matched.append(skill["name"])

    return matched
