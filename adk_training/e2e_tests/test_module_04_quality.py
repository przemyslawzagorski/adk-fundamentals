"""
E2E Quality Assurance Tests for Module 04: Sequential Agent Pipeline
=====================================================================

High-value tests that guarantee commercial quality of the RAID pipeline.
Complements structural tests in test_module_04.py.

Tests cover:
- output_key chain integrity (broken = pipeline crash)
- Instruction references previous output_keys (broken = agent blind)
- Sub-agent ordering matches data dependencies
- Agent name uniqueness (duplicates = state pollution)
- Instruction quality: actionable, role-aware, formatted output
"""

import os
import re
import sys

utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from utils import print_test_header, print_test_summary

module_path = os.path.join(os.path.dirname(__file__), "..", "module_04_sequential_agent")
module_path = os.path.abspath(module_path)
if module_path not in sys.path:
    sys.path.insert(0, module_path)


# =============================================================================
# 1. OUTPUT_KEY CHAIN — Every sub-agent stores its result
# =============================================================================


def test_output_key_chain():
    """Test Q1: Every sub-agent in the pipeline has a unique output_key."""
    print("\n[TEST] Q1: output_key chain integrity")

    from agent import root_agent

    subs = root_agent.sub_agents or []
    if len(subs) < 2:
        print(f"FAIL: Sequential pipeline needs >=2 sub-agents, has {len(subs)}")
        return False

    keys = []
    for agent in subs:
        key = getattr(agent, "output_key", None)
        if not key:
            print(f"FAIL: Agent '{agent.name}' has no output_key — result lost between stages")
            return False
        keys.append(key)

    if len(keys) != len(set(keys)):
        print(f"FAIL: Duplicate output_keys → state overwrite. Keys: {keys}")
        return False

    print(f"PASS: Chain [{' → '.join(keys)}] — all unique, no data loss")
    return True


# =============================================================================
# 2. INSTRUCTION REFERENCES — Later agents read earlier output_keys
# =============================================================================


def test_instruction_references_prior_keys():
    """Test Q2: Strategist/Captain instructions reference earlier output_keys."""
    print("\n[TEST] Q2: Instruction ↔ output_key references")

    from agent import root_agent

    subs = root_agent.sub_agents or []
    errors = []

    for i, agent in enumerate(subs):
        if i == 0:
            continue  # First agent has no prior keys to reference

        instruction = getattr(agent, "instruction", "") or ""

        # Collect all prior output_keys
        prior_keys = [
            getattr(subs[j], "output_key", "") for j in range(i)
        ]

        referenced_any = False
        for key in prior_keys:
            if key and f"{{{key}}}" in instruction:
                referenced_any = True

        if not referenced_any:
            errors.append(
                f"Agent '{agent.name}' (stage {i+1}) doesn't reference any prior "
                f"output_keys {prior_keys} — it's blind to earlier stages"
            )

    if errors:
        for err in errors:
            print(f"  - {err}")
        print(f"FAIL: {len(errors)} broken references")
        return False

    print(f"PASS: All downstream agents reference prior output_keys")
    return True


# =============================================================================
# 3. AGENT NAME UNIQUENESS — No duplicates
# =============================================================================


def test_agent_name_uniqueness():
    """Test Q3: All agents in pipeline have unique names."""
    print("\n[TEST] Q3: Agent name uniqueness")

    from agent import root_agent

    names = [root_agent.name]
    for sub in (root_agent.sub_agents or []):
        names.append(sub.name)

    if len(names) != len(set(names)):
        dupes = [n for n in names if names.count(n) > 1]
        print(f"FAIL: Duplicate names → state pollution: {dupes}")
        return False

    print(f"PASS: All names unique: {names}")
    return True


# =============================================================================
# 4. PIPELINE IS SEQUENTIAL TYPE
# =============================================================================


def test_pipeline_is_sequential():
    """Test Q4: Root agent is SequentialAgent (not LlmAgent or parallel)."""
    print("\n[TEST] Q4: Pipeline type check")

    from agent import root_agent
    from google.adk.agents import SequentialAgent

    if not isinstance(root_agent, SequentialAgent):
        print(f"FAIL: Root should be SequentialAgent, is {type(root_agent).__name__}")
        return False

    count = len(root_agent.sub_agents or [])
    if count < 3:
        print(f"FAIL: RAID pipeline needs 3 stages (scout→strategist→captain), has {count}")
        return False

    print(f"PASS: SequentialAgent with {count} stages")
    return True


# =============================================================================
# 5. INSTRUCTION QUALITY — Substantial, role-specific, formatted
# =============================================================================


def test_instruction_quality():
    """Test Q5: Each sub-agent has substantial, role-specific instructions."""
    print("\n[TEST] Q5: Instruction quality")

    from agent import root_agent

    errors = []
    for agent in (root_agent.sub_agents or []):
        instruction = getattr(agent, "instruction", "") or ""

        if len(instruction) < 100:
            errors.append(f"'{agent.name}': instruction too short ({len(instruction)} chars)")

        # Must define role clearly (handle Polish encoding variants)
        role_words = ["jeste", "you are", "your", "twoj"]
        has_role = any(w in instruction.lower() for w in role_words)
        if not has_role:
            errors.append(f"'{agent.name}': no role definition in instruction")

    if errors:
        for err in errors:
            print(f"  - {err}")
        print(f"FAIL: {len(errors)} instruction quality issues")
        return False

    names = [a.name for a in root_agent.sub_agents]
    print(f"PASS: All {len(names)} agents have substantial role-specific instructions")
    return True


# =============================================================================
# MAIN
# =============================================================================


def run_all_tests():
    print_test_header("Sequential Pipeline — Quality Assurance", "04-Q")

    results = {}
    results["output_key chain"] = test_output_key_chain()
    results["Instruction refs prior keys"] = test_instruction_references_prior_keys()
    results["Agent name uniqueness"] = test_agent_name_uniqueness()
    results["Pipeline is SequentialAgent"] = test_pipeline_is_sequential()
    results["Instruction quality"] = test_instruction_quality()

    passed = sum(1 for r in results.values() if r)
    total = len(results)
    return print_test_summary(passed, total)


if __name__ == "__main__":
    sys.exit(run_all_tests())
