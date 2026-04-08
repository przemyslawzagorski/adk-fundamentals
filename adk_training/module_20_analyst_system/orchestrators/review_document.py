"""
Review Document orchestrator — reviews an existing document for quality.

Pipeline: read_doc → quality_review → report
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool

from tools.file_tools import read_file, list_files
from tools.skill_tools import list_skills, read_skill

_module_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_module_dir, "..", ".env"))

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

tool_read_file = FunctionTool(func=read_file)
tool_list_files = FunctionTool(func=list_files)
tool_list_skills = FunctionTool(func=list_skills)
tool_read_skill = FunctionTool(func=read_skill)

# --- Step 1: Read the document ---
doc_reader = LlmAgent(
    name="doc_reader",
    model=MODEL,
    instruction="""Read the document file specified by the user.

Use `read_file(file_path)` to load the document content.
Also identify:
- Document type (HLD, LLD, tutorial, how-to, reference, explanation, epic, test plan)
- Document language (Polish / English)
- Any metadata or frontmatter

Pass all content and metadata to the next step.
""",
    tools=[tool_read_file, tool_list_files],
    output_key="doc_content",
)

# --- Step 2: Quality Review (with skills) ---
quality_reviewer = LlmAgent(
    name="review_quality_analyst",
    model=MODEL,
    instruction="""You are a Document Quality Reviewer with access to skills.

## Input

`{doc_content}` — the document content and metadata.

## Your Task

1. **Load style skills** for review criteria:
   - Call `list_skills()` to find relevant skills
   - Always load `style-guide` for style conventions
   - Load `diataxis-writing` if the doc is a Diátaxis type
   - Load any domain-specific skills

2. **Review against loaded skills**:
   - Style compliance
   - Completeness
   - Accuracy
   - Language conventions
   - Heading hierarchy
   - Formatting

3. **Produce review report** with:
   - Quality score (1-10)
   - Critical issues (must fix)
   - Suggestions (nice to have)
   - Specific locations and corrections
""",
    tools=[tool_list_skills, tool_read_skill],
    output_key="doc_review",
)

# --- Step 3: Report ---
report = LlmAgent(
    name="review_report",
    model=MODEL,
    instruction="""Present the document review results to the user.

## Input

`{doc_review}` — quality review analysis.

## Output

Present a clear, actionable review report:

1. **Quality score**: X/10
2. **Summary**: one-paragraph assessment
3. **Critical issues**: numbered list with file locations and corrections
4. **Suggestions**: numbered list of improvements
5. **What's good**: positive observations (motivational)

Be specific — cite exact quotes and line references when possible.
""",
    output_key="review_result",
)

# --- Orchestrator ---
review_document_orchestrator = SequentialAgent(
    name="review_document",
    description="Review an existing document for quality, style compliance, "
    "and completeness against project conventions and style guides.",
    sub_agents=[doc_reader, quality_reviewer, report],
)
