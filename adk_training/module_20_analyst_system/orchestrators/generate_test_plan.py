"""
Generate Test Plan orchestrator — creates test plan from requirement/design.

Pipeline: source_collector → test_planner → quality_reviewer → writer
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool

from tools.file_tools import read_file, write_document, list_files
from tools.template_tools import load_template, list_templates
from tools.skill_tools import read_skill
from tools.mcp_setup import create_comarch_mcp
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
    name="test_source_collector",
    model=MODEL,
    instruction=COLLECTOR_INSTRUCTION,
    tools=[tool_read_file, tool_list_files, comarch_mcp],
    output_key="collected_sources",
)

# --- Step 2: Test Planner ---
test_planner = LlmAgent(
    name="test_planner",
    model=MODEL,
    instruction="""You are a Test Planner. You create comprehensive test plans.

## Input

`{collected_sources}` — gathered material about the feature to test.

## Your Task

1. Load the test plan template: `load_template("test_plan_template")`
2. Optionally load `requirement-analysis` skill for analysis depth:
   `read_skill("requirement-analysis")`
3. Analyze the feature and identify:
   - Test scenarios grouped by category (positive, negative, edge, integration)
   - Test data requirements
   - Dependencies and prerequisites
   - Performance test considerations
   - Risk areas

## Test Scenario Quality

- Each scenario: ID, description, preconditions, steps, expected result
- Cover both happy paths and edge cases
- Include boundary values
- Consider integration points
- Identify what CAN'T be automated

Fill the template with concrete, realistic test scenarios.
""",
    tools=[tool_load_template, tool_read_skill],
    output_key="test_plan_draft",
)

# --- Step 3: Quality Reviewer ---
quality_reviewer = LlmAgent(
    name="test_quality_reviewer",
    model=MODEL,
    instruction="""You review test plans for completeness and quality.

## Input

`{test_plan_draft}` — the generated test plan.

## Check

- [ ] All TODO placeholders filled
- [ ] Coverage: positive, negative, edge cases present
- [ ] Scenarios have clear preconditions and expected results
- [ ] Test data section is realistic
- [ ] Risk areas identified
- [ ] Exit criteria defined and measurable

Provide corrected version if issues found.
""",
    output_key="test_plan_reviewed",
)

# --- Step 4: Writer ---
writer = LlmAgent(
    name="test_plan_writer",
    model=MODEL,
    instruction="""Write the test plan to disk.

## Input

`{test_plan_reviewed}` — quality-reviewed test plan.

## Task

1. Write using `write_document(file_name, content, subdirectory="test-plans")`
2. Confirm with file path and scenario count summary
""",
    tools=[tool_write_doc],
    output_key="test_plan_result",
)

# --- Orchestrator ---
generate_test_plan_orchestrator = SequentialAgent(
    name="generate_test_plan",
    description="Generate a comprehensive test plan for a feature or requirement. "
    "Creates test scenarios grouped by category with realistic test data.",
    sub_agents=[source_collector, test_planner, quality_reviewer, writer],
)
