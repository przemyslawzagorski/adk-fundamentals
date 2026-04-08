"""
Generate Skill orchestrator — 6-step pipeline that transforms raw knowledge
sources into validated Agent Skills (SKILL.md).

Pipeline: source_collector → knowledge_extractor → dedup_checker →
          skill_architect → quality_reviewer → present_to_user
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool

from tools.skill_tools import (
    list_skills,
    read_skill,
    get_skill_metadata,
    write_skill_draft,
    validate_skill_name,
)
from tools.file_tools import read_file, list_files
from tools.mcp_setup import create_comarch_mcp
from agents.skill_knowledge_extractor import INSTRUCTION as EXTRACTOR_INSTRUCTION
from agents.skill_dedup_checker import INSTRUCTION as DEDUP_INSTRUCTION
from agents.skill_architect import INSTRUCTION as ARCHITECT_INSTRUCTION
from agents.skill_quality_reviewer import INSTRUCTION as REVIEWER_INSTRUCTION

_module_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_module_dir, "..", ".env"))

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")
MODEL_STRONG = os.getenv("ADK_MODEL_STRONG", "gemini-2.5-pro")

# --- Tools ---
tool_list_skills = FunctionTool(func=list_skills)
tool_read_skill = FunctionTool(func=read_skill)
tool_get_metadata = FunctionTool(func=get_skill_metadata)
tool_write_skill = FunctionTool(func=write_skill_draft)
tool_validate_name = FunctionTool(func=validate_skill_name)
tool_read_file = FunctionTool(func=read_file)
tool_list_files = FunctionTool(func=list_files)

comarch_mcp = create_comarch_mcp()

# --- Step 1: Source Collector ---
source_collector = LlmAgent(
    name="skill_source_collector",
    model=MODEL,
    instruction="""You are a Knowledge Source Collector. Your job is to gather raw material
on a given topic from multiple sources.

## Input

The user provides a topic and source directions, e.g.:
- "Search Wiki for HLD guidelines"
- "Read docs/internal/ for initiative writing patterns"
- "Search Jira for acceptance criteria conventions"

## Your Task

1. Use available tools to fetch content from the specified sources:
   - MCP tools (search_wiki, get_wiki_page, search_jira, get_jira_ticket) for external sources
   - read_file / list_files for local files
2. Collect all relevant material
3. Organize it clearly with source attribution

## Output

Write collected material to state with clear source labels:
- Source: [WIKI: page title / JIRA: ticket key / FILE: path]
- Content: [relevant excerpt]

Collect BROADLY — the extraction step will filter what's relevant.
Do NOT summarize or interpret — provide raw material.
""",
    tools=[tool_read_file, tool_list_files, comarch_mcp],
    output_key="collected_knowledge",
)

# --- Step 2: Knowledge Extractor ---
knowledge_extractor = LlmAgent(
    name="skill_knowledge_extractor",
    model=MODEL_STRONG,
    instruction=EXTRACTOR_INSTRUCTION,
    output_key="extracted_knowledge",
)

# --- Step 3: Dedup Checker ---
dedup_checker = LlmAgent(
    name="skill_dedup_checker",
    model=MODEL,
    instruction=DEDUP_INSTRUCTION,
    tools=[tool_list_skills, tool_read_skill],
    output_key="dedup_decision",
)

# --- Step 4: Skill Architect ---
skill_architect = LlmAgent(
    name="skill_architect",
    model=MODEL_STRONG,
    instruction=ARCHITECT_INSTRUCTION,
    tools=[tool_validate_name],
    output_key="skill_draft",
)

# --- Step 5: Quality Reviewer ---
quality_reviewer = LlmAgent(
    name="skill_quality_reviewer",
    model=MODEL_STRONG,
    instruction=REVIEWER_INSTRUCTION,
    tools=[tool_list_skills, tool_read_skill],
    output_key="skill_reviewed",
)

# --- Step 6: Present to User ---
present_to_user = LlmAgent(
    name="skill_presenter",
    model=MODEL,
    instruction="""You are the final step of the Skill Generator pipeline. Present the
generated skill to the user for review and approval.

## Input

- `{skill_reviewed}` — quality-reviewed skill content
- `{dedup_decision}` — CREATE/UPDATE/MERGE/SKIP decision

## Your Task

Present a clear summary:

1. **Action**: CREATE new skill / UPDATE existing / MERGE skills / SKIP (already exists)
2. **Skill name**: proposed name
3. **Quality score**: from review (1-10)
4. **Warnings**: any remaining issues from quality review
5. **Full SKILL.md content**: formatted for reading
6. **Reference files**: if any
7. **Source references**: where the knowledge came from

If the action is SKIP, explain which existing skill covers this and why.

Ask the user to APPROVE or REQUEST CHANGES.

If approved, call `write_skill_draft` to save the skill to disk.
If the user requests changes, describe what would need to change.
""",
    tools=[tool_write_skill],
    output_key="skill_result",
)

# --- Orchestrator ---
generate_skill_orchestrator = SequentialAgent(
    name="generate_skill",
    description="Generate an Agent Skill (SKILL.md) from knowledge sources. "
    "Collects raw material, extracts patterns, checks for duplicates, "
    "designs the skill structure, validates quality, and presents for review.",
    sub_agents=[
        source_collector,
        knowledge_extractor,
        dedup_checker,
        skill_architect,
        quality_reviewer,
        present_to_user,
    ],
)
