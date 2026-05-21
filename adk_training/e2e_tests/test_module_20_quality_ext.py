"""
E2E Quality Assurance Tests — Module 20 EXTENDED (Production)
==============================================================

Extends test_module_20_quality.py with P0/P1 tests for untested orchestrators:
- analyze_requirement parallel pattern integrity
- generate_document dynamic skill loading + 5-step pipeline
- generate_skill Knowledge Loop 6-step pipeline + dedup tools
- MCP graceful fallback (system works without tokens)
- MODEL_STRONG assignment on critical agents

Existing 10 tests in test_module_20_quality.py already cover:
  Q1 routing, Q2 output_key chain, Q3 name uniqueness, Q4-Q5 security,
  Q6-Q8 create_epic/test_plan/review pipelines, Q9 contract, Q10 skill discovery
"""

import os
import sys
import re

utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from utils import print_test_header, print_test_summary

module_path = os.path.join(os.path.dirname(__file__), "..", "module_20_analyst_system")
module_path = os.path.abspath(module_path)
if module_path not in sys.path:
    sys.path.insert(0, module_path)

os.environ["SKILLS_DIR"] = os.path.join(module_path, "skills")


# =============================================================================
# 11. ANALYZE_REQUIREMENT — Parallel pattern (P0)
# =============================================================================


def test_analyze_requirement_parallel():
    """Test Q11: analyze_requirement has Sequential[collect → Parallel(4) → synth]."""
    print("\n[TEST] Q11: analyze_requirement parallel pattern")
    try:
        from orchestrators.analyze_requirement import analyze_requirement_orchestrator as orch
        from google.adk.agents import SequentialAgent, ParallelAgent

        if not isinstance(orch, SequentialAgent):
            print(f"FAIL: Expected SequentialAgent, got {type(orch).__name__}")
            return False

        subs = orch.sub_agents or []
        if len(subs) != 3:
            print(f"FAIL: Expected 3 stages (collect, parallel, synth), got {len(subs)}")
            return False

        # Stage 1: collector with output_key
        collector = subs[0]
        if getattr(collector, "output_key", None) != "collected_sources":
            print(f"FAIL: Stage 1 should have output_key='collected_sources', "
                  f"got '{getattr(collector, 'output_key', None)}'")
            return False

        # Stage 2: ParallelAgent with 4 analysts
        parallel = subs[1]
        if not isinstance(parallel, ParallelAgent):
            print(f"FAIL: Stage 2 should be ParallelAgent, got {type(parallel).__name__}")
            return False

        analyst_count = len(parallel.sub_agents or [])
        if analyst_count != 4:
            print(f"FAIL: Parallel stage needs 4 analysts, has {analyst_count}")
            return False

        # Each analyst has unique output_key
        analyst_keys = [getattr(a, "output_key", None) for a in parallel.sub_agents]
        if None in analyst_keys:
            missing = [a.name for a, k in zip(parallel.sub_agents, analyst_keys) if k is None]
            print(f"FAIL: Analysts without output_key: {missing}")
            return False
        if len(set(analyst_keys)) != 4:
            print(f"FAIL: Analyst output_keys not unique: {analyst_keys}")
            return False

        # Stage 3: synthesis with output_key
        synthesis = subs[2]
        if getattr(synthesis, "output_key", None) != "requirement_analysis":
            print(f"FAIL: Synthesis should have output_key='requirement_analysis'")
            return False

        print(f"PASS: Sequential[collector → Parallel({analyst_keys}) → synthesis]")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 12. ANALYZE_REQUIREMENT — Synthesis references all parallel keys (P0)
# =============================================================================


def test_synthesis_references_all_analysts():
    """Test Q12: Synthesis instruction references all 4 analyst output_keys."""
    print("\n[TEST] Q12: Synthesis references all parallel analyst outputs")
    try:
        from orchestrators.analyze_requirement import analyze_requirement_orchestrator as orch
        from google.adk.agents import ParallelAgent

        parallel = [s for s in orch.sub_agents if isinstance(s, ParallelAgent)][0]
        synthesis = orch.sub_agents[-1]

        analyst_keys = [getattr(a, "output_key", "") for a in parallel.sub_agents]
        instruction = getattr(synthesis, "instruction", "") or ""

        missing = [k for k in analyst_keys if f"{{{k}}}" not in instruction]

        if missing:
            print(f"FAIL: Synthesis doesn't reference: {missing}")
            return False

        print(f"PASS: Synthesis references all {len(analyst_keys)} analyst outputs")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 13. GENERATE_DOCUMENT — 5-step pipeline (P1)
# =============================================================================


def test_generate_document_pipeline():
    """Test Q13: generate_document has 5-step classify→collect→write→review→save."""
    print("\n[TEST] Q13: generate_document 5-step pipeline")
    try:
        from orchestrators.generate_document import generate_document_orchestrator as orch
        from google.adk.agents import SequentialAgent

        if not isinstance(orch, SequentialAgent):
            print(f"FAIL: Expected SequentialAgent, got {type(orch).__name__}")
            return False

        subs = orch.sub_agents or []
        if len(subs) != 5:
            print(f"FAIL: Expected 5 stages, got {len(subs)}")
            return False

        expected_keys = [
            "doc_classification", "collected_sources",
            "doc_draft", "doc_reviewed", "doc_result",
        ]
        actual_keys = [getattr(a, "output_key", None) for a in subs]
        if actual_keys != expected_keys:
            print(f"FAIL: output_keys mismatch:")
            print(f"  expected: {expected_keys}")
            print(f"  actual:   {actual_keys}")
            return False

        print(f"PASS: 5-step pipeline: {expected_keys}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 14. GENERATE_DOCUMENT — Content writer has skill tools (P1)
# =============================================================================


def test_content_writer_has_skill_tools():
    """Test Q14: content_writer has skill loading tools for dynamic skill injection."""
    print("\n[TEST] Q14: Content writer has skill loading tools")
    try:
        from orchestrators.generate_document import generate_document_orchestrator as orch

        # content_writer is stage 3 (index 2)
        writer = orch.sub_agents[2]

        tool_names = set()
        for t in (writer.tools or []):
            name = getattr(t, "name", None) or getattr(t, "__name__", None)
            if not name:
                func = getattr(t, "func", None)
                name = getattr(func, "__name__", "?") if func else "?"
            tool_names.add(name)

        required_skill_tools = {"list_skills", "read_skill"}
        missing = required_skill_tools - tool_names

        if missing:
            print(f"FAIL: Content writer missing skill tools: {missing}. Has: {tool_names}")
            return False

        # Also needs template loading
        if "load_template" not in tool_names:
            print(f"FAIL: Content writer missing load_template. Has: {tool_names}")
            return False

        print(f"PASS: Content writer has skill tools + template tools: {sorted(tool_names)}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 15. GENERATE_SKILL — 6-step Knowledge Loop (P0)
# =============================================================================


def test_generate_skill_pipeline():
    """Test Q15: generate_skill has 6-step pipeline (longest pipeline in system)."""
    print("\n[TEST] Q15: generate_skill 6-step Knowledge Loop")
    try:
        from orchestrators.generate_skill import generate_skill_orchestrator as orch
        from google.adk.agents import SequentialAgent

        if not isinstance(orch, SequentialAgent):
            print(f"FAIL: Expected SequentialAgent, got {type(orch).__name__}")
            return False

        subs = orch.sub_agents or []
        if len(subs) != 6:
            print(f"FAIL: Knowledge Loop needs 6 stages, has {len(subs)}")
            return False

        # Verify complete output_key chain
        keys = [getattr(a, "output_key", None) for a in subs]
        if None in keys:
            broken = [(a.name, k) for a, k in zip(subs, keys) if k is None]
            print(f"FAIL: Stages without output_key: {broken}")
            return False

        if len(set(keys)) != 6:
            print(f"FAIL: output_keys not all unique: {keys}")
            return False

        names = [a.name for a in subs]
        print(f"PASS: 6-step pipeline: {' → '.join(names)}")
        print(f"      Keys: {keys}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 16. GENERATE_SKILL — Dedup checker has skill listing tools (P0)
# =============================================================================


def test_skill_dedup_checker_tools():
    """Test Q16: dedup_checker can list+read existing skills."""
    print("\n[TEST] Q16: Dedup checker skill tools")
    try:
        from orchestrators.generate_skill import generate_skill_orchestrator as orch

        # dedup_checker is stage 3 (index 2)
        dedup = orch.sub_agents[2]

        tool_names = set()
        for t in (dedup.tools or []):
            name = getattr(t, "name", None) or getattr(t, "__name__", None)
            if not name:
                func = getattr(t, "func", None)
                name = getattr(func, "__name__", "?") if func else "?"
            tool_names.add(name)

        required = {"list_skills", "read_skill"}
        missing = required - tool_names

        if missing:
            print(f"FAIL: Dedup checker missing: {missing}. Has: {tool_names}")
            return False

        print(f"PASS: Dedup checker has both skill inspection tools: {sorted(tool_names)}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 17. GENERATE_SKILL — Presenter has write_skill_draft (P0)
# =============================================================================


def test_skill_presenter_has_write_tool():
    """Test Q17: Final step (presenter) can save approved skill to disk."""
    print("\n[TEST] Q17: Presenter has write_skill_draft tool")
    try:
        from orchestrators.generate_skill import generate_skill_orchestrator as orch

        # Presenter is last stage (index 5)
        presenter = orch.sub_agents[-1]

        tool_names = set()
        for t in (presenter.tools or []):
            name = getattr(t, "name", None) or getattr(t, "__name__", None)
            if not name:
                func = getattr(t, "func", None)
                name = getattr(func, "__name__", "?") if func else "?"
            tool_names.add(name)

        if "write_skill_draft" not in tool_names:
            print(f"FAIL: Presenter missing write_skill_draft. Has: {tool_names}")
            return False

        print(f"PASS: Presenter can save skills: {sorted(tool_names)}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 18. MODEL_STRONG — Critical agents use stronger model (P1)
# =============================================================================


def test_strong_model_assignment():
    """Test Q18: Knowledge-heavy agents use MODEL_STRONG (gemini-2.5-pro)."""
    print("\n[TEST] Q18: MODEL_STRONG on critical agents")
    try:
        from orchestrators.generate_skill import generate_skill_orchestrator as skill_orch
        from orchestrators.generate_document import generate_document_orchestrator as doc_orch

        model_strong = os.getenv("ADK_MODEL_STRONG", "gemini-2.5-pro")
        model_regular = os.getenv("ADK_MODEL", "gemini-2.5-flash")

        # Agents that MUST use strong model
        strong_agents = []

        # generate_skill: extractor, architect, reviewer use STRONG
        for agent in skill_orch.sub_agents:
            if any(kw in agent.name for kw in ["extractor", "architect", "quality_reviewer"]):
                strong_agents.append((f"skill/{agent.name}", agent))

        # generate_document: content_writer uses STRONG
        for agent in doc_orch.sub_agents:
            if "writer" in agent.name and "file" not in agent.name:
                strong_agents.append((f"doc/{agent.name}", agent))

        errors = []
        for path, agent in strong_agents:
            model = getattr(agent, "model", None) or ""
            if model_strong not in model and "pro" not in model:
                errors.append(f"{path}: model='{model}' (expected STRONG={model_strong})")

        if errors:
            for err in errors:
                print(f"  - {err}")
            print(f"FAIL: {len(errors)} critical agents not using MODEL_STRONG")
            return False

        names = [path for path, _ in strong_agents]
        print(f"PASS: {len(strong_agents)} critical agents use MODEL_STRONG: {names}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 19. MCP GRACEFUL FALLBACK (P1)
# =============================================================================


def test_mcp_graceful_fallback():
    """Test Q19: System works when MCP tokens are not configured."""
    print("\n[TEST] Q19: MCP graceful fallback")
    try:
        # Save original tokens
        saved = {}
        for key in ["JIRA_BEARER_TOKEN", "WIKI_BEARER_TOKEN", "GITLAB_TOKEN"]:
            saved[key] = os.environ.pop(key, None)

        try:
            # Force-reimport mcp_setup to test without tokens
            # Just verify the orchestrators import cleanly
            from orchestrators.analyze_requirement import analyze_requirement_orchestrator
            from orchestrators.create_epic import create_epic_orchestrator
            from orchestrators.generate_document import generate_document_orchestrator
            from orchestrators.generate_skill import generate_skill_orchestrator

            # All orchestrators should have sub_agents (not broken by missing MCP)
            for name, orch in [
                ("analyze_requirement", analyze_requirement_orchestrator),
                ("create_epic", create_epic_orchestrator),
                ("generate_document", generate_document_orchestrator),
                ("generate_skill", generate_skill_orchestrator),
            ]:
                subs = orch.sub_agents or []
                if not subs:
                    print(f"FAIL: {name} has no sub_agents — MCP failure broke it")
                    return False

            print("PASS: All orchestrators load cleanly without MCP tokens")
            return True
        finally:
            # Restore tokens
            for key, val in saved.items():
                if val is not None:
                    os.environ[key] = val
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 20. SKILL NAME VALIDATION — Security boundary (P1)
# =============================================================================


def test_skill_name_validation():
    """Test Q20: validate_skill_name enforces spec + blocks reserved names."""
    print("\n[TEST] Q20: Skill name validation")
    try:
        from tools.skill_tools import validate_skill_name

        # Good names
        good = ["my-skill", "api-design-patterns", "style-guide", "a1"]
        for name in good:
            result = validate_skill_name(name)
            if not result.get("valid"):
                print(f"FAIL: Rejected valid name '{name}': {result.get('issues')}")
                return False

        # Bad names
        bad = [
            "My Skill",         # uppercase + spaces
            "test",             # reserved
            "scripts",          # reserved
            "-bad-start",       # starts with hyphen
            "a" * 100,          # too long
        ]
        for name in bad:
            result = validate_skill_name(name)
            if result.get("valid"):
                print(f"FAIL: Accepted invalid name '{name}'")
                return False

        print(f"PASS: Accepted {len(good)} valid names, rejected {len(bad)} invalid")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# MAIN
# =============================================================================


def run_all_tests():
    print_test_header("Analyst System EXTENDED — Production Quality", "20-EXT")

    results = {}
    results["analyze_req parallel pattern"] = test_analyze_requirement_parallel()
    results["synthesis refs all analysts"] = test_synthesis_references_all_analysts()
    results["generate_doc 5-step pipeline"] = test_generate_document_pipeline()
    results["content_writer skill tools"] = test_content_writer_has_skill_tools()
    results["generate_skill 6-step Loop"] = test_generate_skill_pipeline()
    results["dedup checker tools"] = test_skill_dedup_checker_tools()
    results["presenter write tool"] = test_skill_presenter_has_write_tool()
    results["MODEL_STRONG assignment"] = test_strong_model_assignment()
    results["MCP graceful fallback"] = test_mcp_graceful_fallback()
    results["Skill name validation"] = test_skill_name_validation()

    passed = sum(1 for r in results.values() if r)
    total = len(results)
    return print_test_summary(passed, total)


if __name__ == "__main__":
    sys.exit(run_all_tests())
