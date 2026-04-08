"""
Generate Document orchestrator — creates HLD, LLD, how-to, tutorials, etc.

Pipeline: classify_type → source_collector → content_writer → quality_reviewer
Enhanced with dynamic skill loading based on document topic.
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool

from tools.file_tools import read_file, write_document, list_files
from tools.template_tools import load_template, list_templates
from tools.skill_tools import list_skills, read_skill
from tools.mcp_setup import create_comarch_mcp
from agents.source_collector import INSTRUCTION as COLLECTOR_INSTRUCTION

_module_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_module_dir, "..", ".env"))

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")
MODEL_STRONG = os.getenv("ADK_MODEL_STRONG", "gemini-2.5-pro")

tool_read_file = FunctionTool(func=read_file)
tool_list_files = FunctionTool(func=list_files)
tool_write_doc = FunctionTool(func=write_document)
tool_load_template = FunctionTool(func=load_template)
tool_list_templates = FunctionTool(func=list_templates)
tool_list_skills = FunctionTool(func=list_skills)
tool_read_skill = FunctionTool(func=read_skill)
comarch_mcp = create_comarch_mcp()

# --- Step 1: Classify Document Type ---
classify_type = LlmAgent(
    name="doc_type_classifier",
    model=MODEL,
    instruction="""You classify the user's request into a document type and identify
the topic for skill matching.

## Document Types

| Type | Template | When |
|------|----------|------|
| HLD | hld_template | Architecture, high-level design |
| LLD | lld_template | Detailed design, implementation spec |
| Tutorial | (Diátaxis) | Learning-oriented, step-by-step |
| How-to | (Diátaxis) | Problem-solving, practical |
| Reference | (Diátaxis) | Information, tables, completeness |
| Explanation | (Diátaxis) | Understanding, concepts, context |
| Epic | epic_template | Jira epic (redirect to create_epic) |
| Test Plan | test_plan_template | Test scenarios |

## Output

State your classification:
- `document_type`: one of the types above
- `template_name`: corresponding template name (or "none" for Diátaxis without template)
- `topic`: key topic for skill matching (e.g., "billing", "SIM lifecycle", "HLD")
- `title`: suggested document title
""",
    output_key="doc_classification",
)

# --- Step 2: Source Collector ---
source_collector = LlmAgent(
    name="doc_source_collector",
    model=MODEL,
    instruction=COLLECTOR_INSTRUCTION,
    tools=[tool_read_file, tool_list_files, comarch_mcp],
    output_key="collected_sources",
)

# --- Step 3: Content Writer (with dynamic skill loading) ---
content_writer = LlmAgent(
    name="doc_content_writer",
    model=MODEL_STRONG,
    instruction="""You are a Document Writer with access to domain skills.

## Input

- `{doc_classification}` — document type, template, topic
- `{collected_sources}` — gathered source material

## Your Task

1. **Load relevant skills** for domain expertise:
   - Call `list_skills()` to see available skills
   - Call `read_skill(name)` for skills matching the topic
   - Always load `style-guide` skill for writing conventions
   - Load `diataxis-writing` skill if writing Tutorial/How-to/Reference/Explanation
   - Load any domain-specific skills matching the topic

2. **Load template** if applicable:
   - Call `load_template(template_name)` from classification

3. **Write the document**:
   - Follow loaded skill conventions
   - Fill template TODOs with content from sources
   - Apply style guide rules
   - Use domain terminology from loaded skills
   - Be concrete and specific

## Quality Principles

- Every section must have substance — no filler
- Use tables for structured data
- Examples must be realistic
- Follow the project's documentation language
""",
    tools=[tool_list_skills, tool_read_skill, tool_load_template],
    output_key="doc_draft",
)

# --- Step 4: Quality Reviewer ---
quality_reviewer = LlmAgent(
    name="doc_quality_reviewer",
    model=MODEL,
    instruction="""You are a Document Quality Reviewer.

## Input

`{doc_draft}` — the generated document.
`{doc_classification}` — document type info.

## Review Checklist

- [ ] All TODO placeholders filled
- [ ] Heading hierarchy correct (no skipped levels)
- [ ] Style guide followed (active voice, no emoji, proper formatting)
- [ ] Diátaxis type rules followed (if applicable)
- [ ] Terminology consistent
- [ ] Polish language conventions (if Polish doc)
- [ ] Tables used for structured data
- [ ] Examples are concrete

If critical issues found, provide corrected version.
Otherwise pass the document through with quality score.
""",
    tools=[tool_read_skill],
    output_key="doc_reviewed",
)

# --- Step 5: Save to disk ---
doc_writer = LlmAgent(
    name="doc_file_writer",
    model=MODEL,
    instruction="""Write the reviewed document to disk.

## Input

`{doc_reviewed}` — quality-reviewed document content.
`{doc_classification}` — document type and title.

## Task

1. Determine file name from title (kebab-case + .md)
2. Determine subdirectory from type (hld/ lld/ tutorials/ how-to/ reference/ explanation/)
3. Write using `write_document(file_name, content, subdirectory)`
4. Confirm with file path and brief summary
""",
    tools=[tool_write_doc],
    output_key="doc_result",
)

# --- Orchestrator ---
generate_document_orchestrator = SequentialAgent(
    name="generate_document",
    description="Generate a document (HLD, LLD, tutorial, how-to, reference, explanation) "
    "from a topic or requirement. Dynamically loads relevant skills for domain expertise, "
    "applies templates, reviews quality, and saves to disk.",
    sub_agents=[classify_type, source_collector, content_writer, quality_reviewer, doc_writer],
)
