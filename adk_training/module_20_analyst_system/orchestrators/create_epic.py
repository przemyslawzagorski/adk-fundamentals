"""
Create Epic orchestrator — generates Jira Epic with user stories from requirements.

Pipeline: source_collector → epic_writer → quality_reviewer → template_writer
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool

from tools.file_tools import read_file, write_document, list_files
from tools.template_tools import load_template, list_templates
from tools.mcp_setup import create_comarch_mcp
from tools.skill_tools import read_skill
from agents.source_collector import INSTRUCTION as COLLECTOR_INSTRUCTION

_module_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_module_dir, "..", ".env"))

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

tool_read_file = FunctionTool(func=read_file)
tool_list_files = FunctionTool(func=list_files)
tool_write_doc = FunctionTool(func=write_document)
tool_load_template = FunctionTool(func=load_template)
tool_list_templates = FunctionTool(func=list_templates)
tool_read_skill = FunctionTool(func=read_skill)
comarch_mcp = create_comarch_mcp()

# --- Step 1: Source Collector ---
source_collector = LlmAgent(
    name="epic_source_collector",
    model=MODEL,
    instruction=COLLECTOR_INSTRUCTION,
    tools=[tool_read_file, tool_list_files, comarch_mcp],
    output_key="collected_sources",
)

# --- Step 2: Epic Writer ---
epic_writer = LlmAgent(
    name="epic_writer",
    model=MODEL,
    instruction="""You are an Epic Writer. You decompose requirements into structured
Jira Epics with User Stories.

## Input

`{collected_sources}` — gathered material about the requirement.

## Your Task

1. Load the epic template: call `load_template("epic_template")`
2. Optionally load the `requirement-analysis` skill for analysis guidance:
   call `read_skill("requirement-analysis")`
3. Analyze the requirement and decompose into:
   - Epic title and description
   - User stories (3-8 stories per epic, with Given/When/Then acceptance criteria)
   - Dependencies between stories
   - Risks
4. Fill in the template with concrete content

## Story Quality Rules

- Each story must be independently implementable
- Acceptance criteria in Given/When/Then format
- Include technical notes for non-obvious implementation details
- Stories ordered by dependency (blocking stories first)

Write the complete epic document to state.
""",
    tools=[tool_load_template, tool_read_skill],
    output_key="epic_draft",
)

# --- Step 3: Quality Reviewer ---
quality_reviewer = LlmAgent(
    name="epic_quality_reviewer",
    model=MODEL,
    instruction="""You are an Epic Quality Reviewer. Review the epic for completeness
and quality.

## Input

`{epic_draft}` — the generated epic document.

## Check

- [ ] All stories have clear acceptance criteria (Given/When/Then)
- [ ] Stories are independently implementable
- [ ] Dependencies are correctly identified
- [ ] No TODO placeholders remain
- [ ] Scope is clearly defined (in/out)
- [ ] Risks identified with mitigations

If issues found, provide the corrected version. Otherwise, pass through unchanged.
""",
    output_key="epic_reviewed",
)

# --- Step 4: Writer (save to disk) ---
template_writer = LlmAgent(
    name="epic_template_writer",
    model=MODEL,
    instruction="""You write the final epic document to disk.

## Input

`{epic_reviewed}` — quality-reviewed epic content.

## Task

1. Write the document using `write_document(file_name, content, subdirectory="epics")`
   - file_name: kebab-case based on epic title, e.g. "pre-rating-feature.md"
2. Confirm to the user with file path and summary of stories created
""",
    tools=[tool_write_doc],
    output_key="epic_result",
)

# --- Orchestrator ---
create_epic_orchestrator = SequentialAgent(
    name="create_epic",
    description="Create a Jira Epic with user stories from a requirement or feature description. "
    "Analyzes the requirement, decomposes into stories with acceptance criteria, "
    "reviews quality, and saves to disk.",
    sub_agents=[source_collector, epic_writer, quality_reviewer, template_writer],
)
