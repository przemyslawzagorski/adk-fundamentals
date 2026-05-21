"""
E2E Quality Assurance Tests for Module 08: Loop Critique
=========================================================

High-value tests for the iterative refinement pattern.
Complements structural tests in test_module_08.py.

Tests cover:
- LoopAgent type with max_iterations safety bound
- Loop body has write → review → decide → control stages
- Custom BaseAgent for loop exit (CheckStatusAndEscalate)
- EntryDecision schema with valid/invalid values
- output_key flow within loop body
"""

import os
import sys

utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from utils import print_test_header, print_test_summary

module_path = os.path.join(os.path.dirname(__file__), "..", "module_08_loop_critique")
module_path = os.path.abspath(module_path)
if module_path not in sys.path:
    sys.path.insert(0, module_path)


# =============================================================================
# 1. LOOP TYPE + SAFETY BOUND
# =============================================================================


def test_loop_type_and_bound():
    """Test Q1: Root is LoopAgent with max_iterations safety limit."""
    print("\n[TEST] Q1: LoopAgent type + safety bound")

    from agent import root_agent
    from google.adk.agents import LoopAgent

    if not isinstance(root_agent, LoopAgent):
        print(f"FAIL: Root should be LoopAgent, is {type(root_agent).__name__}")
        return False

    max_iter = getattr(root_agent, "max_iterations", None)
    if max_iter is None or max_iter < 1:
        print(f"FAIL: No max_iterations safety bound (got {max_iter})")
        return False

    if max_iter > 20:
        print(f"FAIL: max_iterations={max_iter} too high — risk of infinite loop")
        return False

    print(f"PASS: LoopAgent with max_iterations={max_iter}")
    return True


# =============================================================================
# 2. LOOP BODY STAGES — Write → Review → Decide → Control
# =============================================================================


def test_loop_body_stages():
    """Test Q2: Loop has >=3 stages (writer, critic, decider)."""
    print("\n[TEST] Q2: Loop body stages")

    from agent import root_agent

    subs = root_agent.sub_agents or []
    if len(subs) < 3:
        print(f"FAIL: Loop needs >=3 stages (write/review/decide), has {len(subs)}")
        return False

    names = [s.name for s in subs]

    # Name uniqueness
    if len(names) != len(set(names)):
        dupes = [n for n in names if names.count(n) > 1]
        print(f"FAIL: Duplicate names in loop: {dupes}")
        return False

    print(f"PASS: Loop body has {len(subs)} stages: {names}")
    return True


# =============================================================================
# 3. CUSTOM BASE AGENT — Escalation controller exists
# =============================================================================


def test_escalation_controller():
    """Test Q3: Loop has a custom BaseAgent for escalation control."""
    print("\n[TEST] Q3: Escalation controller (custom BaseAgent)")

    from agent import root_agent
    from google.adk.agents import BaseAgent, LlmAgent

    subs = root_agent.sub_agents or []

    custom_agents = [
        s for s in subs
        if isinstance(s, BaseAgent) and not isinstance(s, LlmAgent)
    ]

    if not custom_agents:
        print("FAIL: No custom BaseAgent for loop exit control")
        return False

    ctrl = custom_agents[0]

    # Must have _run_async_impl
    has_impl = hasattr(ctrl, "_run_async_impl")
    if not has_impl:
        print(f"FAIL: '{ctrl.name}' missing _run_async_impl override")
        return False

    print(f"PASS: Custom loop controller '{ctrl.name}' with _run_async_impl")
    return True


# =============================================================================
# 4. DECISION SCHEMA — EntryDecision with valid/invalid
# =============================================================================


def test_decision_schema():
    """Test Q4: Captain uses output_schema with decision field."""
    print("\n[TEST] Q4: Decision schema structure")

    from agent import EntryDecision

    # Validate schema fields
    fields = EntryDecision.model_fields
    if "decision" not in fields:
        print(f"FAIL: EntryDecision missing 'decision' field. Has: {list(fields.keys())}")
        return False

    # Test valid instances
    valid = EntryDecision(decision="valid", reason="Good entry")
    invalid = EntryDecision(decision="invalid", reason="Needs work")

    if valid.decision != "valid" or invalid.decision != "invalid":
        print("FAIL: Schema doesn't preserve decision values")
        return False

    # Find captain agent with output_schema
    from agent import root_agent
    schema_agents = [
        s for s in root_agent.sub_agents
        if getattr(s, "output_schema", None) is not None
    ]
    if not schema_agents:
        print("FAIL: No agent in loop uses output_schema")
        return False

    print(f"PASS: EntryDecision schema with fields: {list(fields.keys())}")
    return True


# =============================================================================
# 5. OUTPUT_KEY FLOW — Keys chain within loop body
# =============================================================================


def test_output_key_flow():
    """Test Q5: Loop body agents have output_keys that feed into each other."""
    print("\n[TEST] Q5: output_key flow within loop")

    from agent import root_agent
    from google.adk.agents import LlmAgent

    subs = root_agent.sub_agents or []
    llm_agents = [s for s in subs if isinstance(s, LlmAgent)]

    keys = []
    for agent in llm_agents:
        key = getattr(agent, "output_key", None)
        if key:
            keys.append((agent.name, key))

    if len(keys) < 2:
        print(f"FAIL: Need >=2 output_keys for data flow, found {len(keys)}")
        return False

    # Check downstream agents reference upstream keys
    referenced = 0
    for agent in llm_agents:
        instruction = getattr(agent, "instruction", "") or ""
        for name, key in keys:
            if name != agent.name and f"{{{key}}}" in instruction:
                referenced += 1

    if referenced == 0:
        print("FAIL: No agent references prior output_keys in instruction")
        return False

    key_chain = " → ".join(f"{n}:{k}" for n, k in keys)
    print(f"PASS: output_key flow: [{key_chain}], {referenced} cross-refs")
    return True


# =============================================================================
# MAIN
# =============================================================================


def run_all_tests():
    print_test_header("Loop Critique — Quality Assurance", "08-Q")

    results = {}
    results["Loop type + safety"] = test_loop_type_and_bound()
    results["Loop body stages"] = test_loop_body_stages()
    results["Escalation controller"] = test_escalation_controller()
    results["Decision schema"] = test_decision_schema()
    results["output_key flow"] = test_output_key_flow()

    passed = sum(1 for r in results.values() if r)
    total = len(results)
    return print_test_summary(passed, total)


if __name__ == "__main__":
    sys.exit(run_all_tests())
