"""
E2E Quality Assurance Tests for Module 20: Analyst System
=========================================================

High-value tests focused on catching real bugs that break commercial quality.
Complements structural tests in test_module_20.py.

Tests cover:
- Routing table ↔ tool name consistency (mismatches = wrong routing)
- output_key → instruction chain integrity (broken = pipeline crash)
- Agent name uniqueness (duplicates = state pollution)
- Path traversal security (blocked patterns)
- write_document output containment (escape = security hole)
- Missing orchestrator structure tests (create_epic, test_plan, review)
- Contract enrichment completeness (missing fields = lost context)
- Skill discovery precision (bad matches = wrong skills loaded)
"""

import os
import re
import sys
import tempfile
from pathlib import Path

utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from utils import print_test_header, print_test_summary

module_path = os.path.join(os.path.dirname(__file__), "..", "module_20_analyst_system")
module_path = os.path.abspath(module_path)
if module_path not in sys.path:
    sys.path.insert(0, module_path)

# Ensure SKILLS_DIR is absolute for skill discovery
os.environ["SKILLS_DIR"] = os.path.join(module_path, "skills")


# =============================================================================
# 1. ROUTING TABLE → TOOL NAME CONSISTENCY
# =============================================================================


def test_routing_table_matches_tools():
    """Test Q1: Captain routing table tool names match actual AgentTool names."""
    print("\n[TEST] Q1: Routing table ↔ tool name consistency")
    try:
        from agent import root_agent

        instruction = root_agent.instruction
        # Find tool names in routing table: | `tool_name` | description |
        table_tools = re.findall(r'\|\s*`(\w+)`\s*\|', instruction)

        if not table_tools:
            print("FAIL: No tool names found in routing table")
            return False

        # Actual AgentTool names = wrapped orchestrator names
        actual_names = set()
        for tool in root_agent.tools:
            agent = getattr(tool, 'agent', None)
            if agent:
                actual_names.add(agent.name)

        errors = []
        for name in table_tools:
            if name not in actual_names:
                errors.append(
                    f"Routing table mentions '{name}' but no AgentTool has that name. "
                    f"Available: {sorted(actual_names)}"
                )

        if errors:
            for err in errors:
                print(f"  - {err}")
            print(f"FAIL: {len(errors)} routing table mismatches")
            return False

        print(f"PASS: All {len(table_tools)} routing entries match tools: {sorted(actual_names)}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 2. OUTPUT_KEY ↔ INSTRUCTION STATE REFERENCE CHAIN
# =============================================================================


def test_output_key_chain_references():
    """Test Q2: Every {state_var} in an instruction has a matching output_key from a prior agent."""
    print("\n[TEST] Q2: output_key → instruction reference chain integrity")
    try:
        from orchestrators.analyze_requirement import analyze_requirement_orchestrator
        from orchestrators.create_epic import create_epic_orchestrator
        from orchestrators.generate_document import generate_document_orchestrator
        from orchestrators.generate_test_plan import generate_test_plan_orchestrator
        from orchestrators.review_document import review_document_orchestrator
        from orchestrators.generate_skill import generate_skill_orchestrator
        from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent

        def flatten_ordered(orch):
            """Get agents in pipeline order for output_key chain analysis."""
            result = []
            for sub in (orch.sub_agents or []):
                if isinstance(sub, LlmAgent):
                    result.append(sub)
                elif isinstance(sub, ParallelAgent):
                    for inner in (sub.sub_agents or []):
                        if isinstance(inner, LlmAgent):
                            result.append(inner)
                elif isinstance(sub, SequentialAgent):
                    result.extend(flatten_ordered(sub))
            return result

        orchestrators = {
            "analyze_requirement": analyze_requirement_orchestrator,
            "create_epic": create_epic_orchestrator,
            "generate_document": generate_document_orchestrator,
            "generate_test_plan": generate_test_plan_orchestrator,
            "review_document": review_document_orchestrator,
            "generate_skill": generate_skill_orchestrator,
        }

        # Words that look like {state_var} but are actually parameter names or formatting
        false_positives = {
            'name', 'file_name', 'content', 'subdirectory', 'file_path',
            'pattern', 'directory', 'skill_name', 'topic', 'path',
            'count', 'skills_dir', 'default_skills_dir',
        }

        errors = []
        for name, orch in orchestrators.items():
            agents = flatten_ordered(orch)
            available_keys = set()

            for agent in agents:
                instruction = getattr(agent, 'instruction', '') or ''
                # Find {state_var} references — single-word identifiers
                refs = re.findall(r'`?\{(\w+)\}`?', instruction)
                refs = [r for r in refs if r not in false_positives]

                for ref in refs:
                    if ref not in available_keys:
                        errors.append(
                            f"{name}/{agent.name}: references '{{{ref}}}' but "
                            f"no prior agent has output_key='{ref}'. "
                            f"Available: {available_keys or '{none}'}"
                        )

                key = getattr(agent, 'output_key', None)
                if key:
                    available_keys.add(key)

        if errors:
            for err in errors:
                print(f"  - {err}")
            print(f"FAIL: {len(errors)} broken state references")
            return False

        print(f"PASS: All state references have matching output_keys across 6 orchestrators")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 3. AGENT NAME UNIQUENESS ACROSS SYSTEM
# =============================================================================


def test_agent_names_unique():
    """Test Q3: All agent names across all orchestrators are globally unique."""
    print("\n[TEST] Q3: Agent name uniqueness")
    try:
        from orchestrators.analyze_requirement import analyze_requirement_orchestrator
        from orchestrators.create_epic import create_epic_orchestrator
        from orchestrators.generate_document import generate_document_orchestrator
        from orchestrators.generate_test_plan import generate_test_plan_orchestrator
        from orchestrators.review_document import review_document_orchestrator
        from orchestrators.generate_skill import generate_skill_orchestrator

        def collect_names(agent, orch_name=""):
            """Recursively collect (agent_name, orchestrator_name) pairs."""
            names = []
            name = getattr(agent, 'name', None)
            if name:
                names.append((name, orch_name))
            for sub in (getattr(agent, 'sub_agents', []) or []):
                names.extend(collect_names(sub, orch_name))
            return names

        all_names = []
        orchestrators = {
            "analyze_requirement": analyze_requirement_orchestrator,
            "create_epic": create_epic_orchestrator,
            "generate_document": generate_document_orchestrator,
            "generate_test_plan": generate_test_plan_orchestrator,
            "review_document": review_document_orchestrator,
            "generate_skill": generate_skill_orchestrator,
        }

        for orch_name, orch in orchestrators.items():
            all_names.extend(collect_names(orch, orch_name))

        # Count occurrences
        name_locations = {}
        for name, orch in all_names:
            name_locations.setdefault(name, []).append(orch)

        duplicates = {n: locs for n, locs in name_locations.items() if len(locs) > 1}

        if duplicates:
            for name, locs in duplicates.items():
                print(f"  - DUPLICATE '{name}' in: {locs}")
            print(f"FAIL: {len(duplicates)} duplicate agent names")
            return False

        print(f"PASS: All {len(all_names)} agent names are unique across 6 orchestrators")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 4. SECURITY: PATH TRAVERSAL
# =============================================================================


def test_security_path_traversal():
    """Test Q4: read_file blocks known dangerous paths."""
    print("\n[TEST] Q4: Path traversal security")
    try:
        from tools.file_tools import read_file

        dangerous_paths = [
            "/etc/shadow",
            "/etc/passwd",
            "../../etc/shadow",
            "../../../etc/passwd",
            "C:\\Windows\\System32\\config\\SAM",
            "..\\..\\windows\\system32\\config\\SAM",
        ]

        leaked = []
        for path in dangerous_paths:
            result = read_file(path)
            if result.get("status") == "ok" and result.get("content"):
                leaked.append(path)

        if leaked:
            print(f"FAIL: Dangerous paths returned content: {leaked}")
            return False

        print(f"PASS: All {len(dangerous_paths)} dangerous paths blocked/not found")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 5. SECURITY: WRITE DOCUMENT OUTPUT CONTAINMENT
# =============================================================================


def test_write_document_path_containment():
    """Test Q5: write_document cannot escape OUTPUT_DIR via path traversal."""
    print("\n[TEST] Q5: write_document output directory containment")
    try:
        from tools.file_tools import write_document

        canary = "SECURITY_TEST_CANARY_DELETE_ME"

        with tempfile.TemporaryDirectory() as tmpdir:
            old_output = os.environ.get("OUTPUT_DIR")
            os.environ["OUTPUT_DIR"] = tmpdir

            # Attempt escape via file_name
            result1 = write_document("../../escape_canary_1.txt", canary)
            # Attempt escape via subdirectory
            result2 = write_document("escape_canary_2.txt", canary, subdirectory="../../outside")

            # Restore env
            if old_output:
                os.environ["OUTPUT_DIR"] = old_output
            else:
                os.environ.pop("OUTPUT_DIR", None)

            output_root = Path(tmpdir).resolve()
            escaped = []

            for i, result in enumerate([result1, result2], 1):
                if result.get("status") == "ok" and result.get("path"):
                    written = Path(result["path"]).resolve()
                    # Clean up regardless
                    if written.exists():
                        written.unlink()
                    if not str(written).startswith(str(output_root)):
                        escaped.append(f"canary_{i} escaped to {written}")

            if escaped:
                for e in escaped:
                    print(f"  - {e}")
                print(f"FAIL: write_document allows path traversal escape")
                return False

            print(f"PASS: write_document stays within OUTPUT_DIR")
            return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 6-8. MISSING ORCHESTRATOR STRUCTURE TESTS
# =============================================================================


def test_create_epic_pipeline():
    """Test Q6: create_epic has 4-step pipeline with correct output_keys."""
    print("\n[TEST] Q6: create_epic pipeline structure")
    try:
        from orchestrators.create_epic import create_epic_orchestrator
        from google.adk.agents import SequentialAgent

        orch = create_epic_orchestrator
        if not isinstance(orch, SequentialAgent):
            print(f"FAIL: Expected SequentialAgent, got {type(orch).__name__}")
            return False

        subs = orch.sub_agents
        if len(subs) != 4:
            print(f"FAIL: Expected 4 sub_agents, got {len(subs)}")
            return False

        expected_keys = ["collected_sources", "epic_draft", "epic_reviewed", "epic_result"]
        actual_keys = [getattr(a, 'output_key', None) for a in subs]
        if actual_keys != expected_keys:
            print(f"FAIL: output_keys mismatch:\n  expected: {expected_keys}\n  actual:   {actual_keys}")
            return False

        print(f"PASS: 4-step create_epic with correct keys: {expected_keys}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_generate_test_plan_pipeline():
    """Test Q7: generate_test_plan has 4-step pipeline with correct output_keys."""
    print("\n[TEST] Q7: generate_test_plan pipeline structure")
    try:
        from orchestrators.generate_test_plan import generate_test_plan_orchestrator
        from google.adk.agents import SequentialAgent

        orch = generate_test_plan_orchestrator
        if not isinstance(orch, SequentialAgent):
            print(f"FAIL: Expected SequentialAgent, got {type(orch).__name__}")
            return False

        subs = orch.sub_agents
        if len(subs) != 4:
            print(f"FAIL: Expected 4 sub_agents, got {len(subs)}")
            return False

        expected_keys = [
            "collected_sources", "test_plan_draft",
            "test_plan_reviewed", "test_plan_result",
        ]
        actual_keys = [getattr(a, 'output_key', None) for a in subs]
        if actual_keys != expected_keys:
            print(f"FAIL: output_keys mismatch:\n  expected: {expected_keys}\n  actual:   {actual_keys}")
            return False

        print(f"PASS: 4-step generate_test_plan with correct keys: {expected_keys}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_review_document_pipeline():
    """Test Q8: review_document has 3-step pipeline with correct output_keys."""
    print("\n[TEST] Q8: review_document pipeline structure")
    try:
        from orchestrators.review_document import review_document_orchestrator
        from google.adk.agents import SequentialAgent

        orch = review_document_orchestrator
        if not isinstance(orch, SequentialAgent):
            print(f"FAIL: Expected SequentialAgent, got {type(orch).__name__}")
            return False

        subs = orch.sub_agents
        if len(subs) != 3:
            print(f"FAIL: Expected 3 sub_agents, got {len(subs)}")
            return False

        expected_keys = ["doc_content", "doc_review", "review_result"]
        actual_keys = [getattr(a, 'output_key', None) for a in subs]
        if actual_keys != expected_keys:
            print(f"FAIL: output_keys mismatch:\n  expected: {expected_keys}\n  actual:   {actual_keys}")
            return False

        print(f"PASS: 3-step review_document with correct keys: {expected_keys}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 9. CONTRACT ENRICHMENT COMPLETENESS
# =============================================================================


def test_contract_enrichment_completeness():
    """Test Q9: Enriched instruction includes all critical contract fields."""
    print("\n[TEST] Q9: Contract enrichment covers critical fields")
    try:
        from prompts.agent_instructions import load_contract, build_base_instruction

        contract_path = os.path.join(module_path, "contract", "sample_contract.json")
        contract = load_contract(contract_path)

        instruction = build_base_instruction(contract, "Test Agent")

        checks = {
            "project_name": contract.project_name in instruction,
            "domain": contract.domain.domain in instruction,
            "key_entities": any(
                e in instruction for e in contract.domain.key_entities[:3]
            ),
            "glossary_terms": (
                any(k in instruction for k in list(contract.domain.glossary.keys())[:3])
                if contract.domain.glossary
                else True
            ),
            "tech_stack": (
                any(t in instruction for t in contract.tech_stack[:3])
                if contract.tech_stack
                else True
            ),
            "primary_language": (
                contract.documentation.primary_language.value.lower()
                in instruction.lower()
            ),
        }

        failures = [field for field, ok in checks.items() if not ok]

        if failures:
            for f in failures:
                print(f"  - Missing in enriched instruction: {f}")
            print(f"FAIL: {len(failures)} contract fields not in enriched instruction")
            return False

        print(f"PASS: All {len(checks)} contract fields present in enriched instruction")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 10. SKILL DISCOVERY PRECISION
# =============================================================================


def test_skill_discovery_precision():
    """Test Q10: discover_relevant_skills returns meaningful matches."""
    print("\n[TEST] Q10: Skill discovery precision")
    try:
        from prompts.agent_instructions import discover_relevant_skills

        skills_dir = os.path.join(module_path, "skills")

        # Positive: specific queries should find expected skills
        test_cases = [
            ("documentation writing style", "style-guide"),
            ("requirement analysis", "requirement-analysis"),
            ("document templates", "document-templates"),
            ("diataxis writing framework", "diataxis-writing"),
        ]

        errors = []
        for query, expected_skill in test_cases:
            results = discover_relevant_skills(query, skills_dir)
            if expected_skill not in results:
                errors.append(f"Query '{query}' should find '{expected_skill}', got: {results}")

        # Negative: gibberish should match few/no skills
        gibberish_results = discover_relevant_skills("xyzzy quantum blockchain", skills_dir)
        if len(gibberish_results) > 2:
            errors.append(
                f"Gibberish matched too many skills "
                f"({len(gibberish_results)}): {gibberish_results}"
            )

        if errors:
            for err in errors:
                print(f"  - {err}")
            print(f"FAIL: {len(errors)} discovery precision issues")
            return False

        print(f"PASS: Skill discovery precise for all {len(test_cases)} positive queries")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# MAIN
# =============================================================================


def run_all_tests():
    """Execute all quality assurance tests for Module 20."""
    print_test_header("Analyst System — Quality Assurance", "20-Q")

    results = {}

    # Integrity
    results["Routing table matches tools"] = test_routing_table_matches_tools()
    results["output_key chain integrity"] = test_output_key_chain_references()
    results["Agent names unique"] = test_agent_names_unique()

    # Security
    results["Path traversal security"] = test_security_path_traversal()
    results["Write path containment"] = test_write_document_path_containment()

    # Missing orchestrator tests
    results["create_epic pipeline"] = test_create_epic_pipeline()
    results["generate_test_plan pipeline"] = test_generate_test_plan_pipeline()
    results["review_document pipeline"] = test_review_document_pipeline()

    # Contract & skills
    results["Contract enrichment"] = test_contract_enrichment_completeness()
    results["Skill discovery precision"] = test_skill_discovery_precision()

    passed = sum(1 for r in results.values() if r)
    total = len(results)
    exit_code = print_test_summary(passed, total)
    return exit_code


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
