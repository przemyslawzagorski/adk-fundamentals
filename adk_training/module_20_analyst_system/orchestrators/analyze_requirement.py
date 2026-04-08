"""
Analyze Requirement orchestrator — multi-dimensional requirement analysis.

Pipeline: source_collector → ParallelAgent[clarity, scope, cross_ref, docs_gap] → synthesis
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import FunctionTool

from tools.file_tools import read_file, list_files
from tools.mcp_setup import create_comarch_mcp
from agents.source_collector import INSTRUCTION as COLLECTOR_INSTRUCTION
from agents.clarity_analyst import INSTRUCTION as CLARITY_INSTRUCTION
from agents.scope_analyst import INSTRUCTION as SCOPE_INSTRUCTION
from agents.cross_ref_analyst import INSTRUCTION as CROSS_REF_INSTRUCTION
from agents.docs_gap_analyst import INSTRUCTION as DOCS_GAP_INSTRUCTION
from agents.synthesis_agent import INSTRUCTION as SYNTHESIS_INSTRUCTION

_module_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_module_dir, "..", ".env"))

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

tool_read_file = FunctionTool(func=read_file)
tool_list_files = FunctionTool(func=list_files)
comarch_mcp = create_comarch_mcp()

# --- Step 1: Source Collector ---
source_collector = LlmAgent(
    name="req_source_collector",
    model=MODEL,
    instruction=COLLECTOR_INSTRUCTION,
    tools=[tool_read_file, tool_list_files, comarch_mcp],
    output_key="collected_sources",
)

# --- Step 2: Parallel Analysis ---
clarity_analyst = LlmAgent(
    name="clarity_analyst",
    model=MODEL,
    instruction=CLARITY_INSTRUCTION,
    output_key="clarity_analysis",
)

scope_analyst = LlmAgent(
    name="scope_analyst",
    model=MODEL,
    instruction=SCOPE_INSTRUCTION,
    output_key="scope_analysis",
)

cross_ref_analyst = LlmAgent(
    name="cross_ref_analyst",
    model=MODEL,
    instruction=CROSS_REF_INSTRUCTION,
    tools=[tool_read_file, tool_list_files, comarch_mcp],
    output_key="cross_ref_analysis",
)

docs_gap_analyst = LlmAgent(
    name="docs_gap_analyst",
    model=MODEL,
    instruction=DOCS_GAP_INSTRUCTION,
    tools=[tool_read_file, tool_list_files, comarch_mcp],
    output_key="docs_gap_analysis",
)

parallel_analysts = ParallelAgent(
    name="parallel_requirement_analysts",
    sub_agents=[clarity_analyst, scope_analyst, cross_ref_analyst, docs_gap_analyst],
)

# --- Step 3: Synthesis ---
synthesis = LlmAgent(
    name="req_synthesis",
    model=MODEL,
    instruction=SYNTHESIS_INSTRUCTION + """

## Specific Inputs

You receive outputs from four parallel analysts:
- `{clarity_analysis}` — clarity and ambiguity assessment
- `{scope_analysis}` — scope layers and risks
- `{cross_ref_analysis}` — related docs and tickets
- `{docs_gap_analysis}` — documentation gaps

Synthesize into a unified requirement analysis report.
End with a clear RECOMMENDATION: Ready for implementation / Needs refinement / Needs spike.
""",
    output_key="requirement_analysis",
)

# --- Orchestrator ---
analyze_requirement_orchestrator = SequentialAgent(
    name="analyze_requirement",
    description="Analyze a requirement for clarity, scope, risks, dependencies, "
    "and documentation gaps. Produces a comprehensive analysis report.",
    sub_agents=[source_collector, parallel_analysts, synthesis],
)
