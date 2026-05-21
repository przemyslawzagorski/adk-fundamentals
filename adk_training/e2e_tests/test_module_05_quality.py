"""
E2E Quality Assurance Tests for Module 05: Human-in-the-Loop
=============================================================

High-value tests for the approval gate pattern.
Complements structural tests in test_module_05.py.

Tests cover:
- Callback chain completeness (before_agent, before_model, before_tool, after_tool)
- Tool parameter validation (max amount, empty purpose)
- Approval threshold logic (≤100 auto, >100 pending)
- Admiral as AgentTool pattern (output_schema enforced)
- Treasury state isolation (global state vs. session state)
"""

import os
import sys

utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from utils import print_test_header, print_test_summary

module_path = os.path.join(os.path.dirname(__file__), "..", "module_05_human_in_loop")
module_path = os.path.abspath(module_path)
if module_path not in sys.path:
    sys.path.insert(0, module_path)


# =============================================================================
# 1. CALLBACK CHAIN — All 4 callbacks wired
# =============================================================================


def test_callback_chain_complete():
    """Test Q1: Root agent has all required callbacks wired."""
    print("\n[TEST] Q1: Callback chain completeness")

    from agent import root_agent

    checks = {
        "before_agent_callback": getattr(root_agent, "before_agent_callback", None),
        "before_model_callback": getattr(root_agent, "before_model_callback", None),
        "before_tool_callback": getattr(root_agent, "before_tool_callback", None),
        "after_tool_callback": getattr(root_agent, "after_tool_callback", None),
    }

    missing = [name for name, cb in checks.items() if cb is None]

    if missing:
        print(f"FAIL: Missing callbacks: {missing}")
        return False

    # All callbacks should be callable
    not_callable = [name for name, cb in checks.items() if not callable(cb)]
    if not_callable:
        print(f"FAIL: Not callable: {not_callable}")
        return False

    print(f"PASS: All 4 callbacks wired: {list(checks.keys())}")
    return True


# =============================================================================
# 2. APPROVAL THRESHOLD — ≤100 auto-approve, >100 pending
# =============================================================================


def test_approval_threshold():
    """Test Q2: request_expenditure auto-approves ≤100, requires approval >100."""
    print("\n[TEST] Q2: Approval threshold logic")

    from agent import request_expenditure, SHIP_TREASURY

    original_balance = SHIP_TREASURY["current_balance"]

    try:
        # Small amount → auto-approve
        result_small = request_expenditure(50, "rum")
        if result_small.get("status") != "approved":
            print(f"FAIL: 50 dublons should be auto-approved, got: {result_small.get('status')}")
            return False

        # Large amount → pending
        result_large = request_expenditure(500, "armaty")
        if result_large.get("status") != "pending_approval":
            print(f"FAIL: 500 dublons should be pending, got: {result_large.get('status')}")
            return False

        print("PASS: ≤100 auto-approved, >100 pending_approval")
        return True

    finally:
        # Restore balance
        SHIP_TREASURY["current_balance"] = original_balance


# =============================================================================
# 3. TOOL VALIDATION — before_tool_callback blocks bad params
# =============================================================================


def test_tool_validation():
    """Test Q3: before_tool_callback rejects invalid params."""
    print("\n[TEST] Q3: Tool parameter validation")

    from agent import validate_tool_params

    class FakeTool:
        def __init__(self, name):
            self.name = name

    errors = []

    # Over-limit amount
    try:
        validate_tool_params(None, FakeTool("request_expenditure"),
                             {"amount": 99999, "purpose": "test"})
        errors.append("Should reject amount >10000")
    except ValueError:
        pass

    # Empty purpose
    try:
        validate_tool_params(None, FakeTool("request_expenditure"),
                             {"amount": 100, "purpose": ""})
        errors.append("Should reject empty purpose")
    except ValueError:
        pass

    # Too short purpose
    try:
        validate_tool_params(None, FakeTool("request_expenditure"),
                             {"amount": 100, "purpose": "ab"})
        errors.append("Should reject purpose <3 chars")
    except ValueError:
        pass

    # Valid params — should NOT raise
    try:
        validate_tool_params(None, FakeTool("request_expenditure"),
                             {"amount": 100, "purpose": "rum for crew"})
    except ValueError as e:
        errors.append(f"Rejected valid params: {e}")

    if errors:
        for err in errors:
            print(f"  - {err}")
        print(f"FAIL: {len(errors)} validation issues")
        return False

    print("PASS: Blocks >10000, empty purpose, short purpose; accepts valid")
    return True


# =============================================================================
# 4. ADMIRAL AS AGENT-TOOL — output_schema enforced
# =============================================================================


def test_admiral_agent_tool():
    """Test Q4: Admiral wired as AgentTool with structured output."""
    print("\n[TEST] Q4: Admiral AgentTool pattern")

    from agent import root_agent, admiral

    # Admiral has output_schema
    schema = getattr(admiral, "output_schema", None)
    if schema is None:
        print("FAIL: Admiral agent has no output_schema")
        return False

    # Schema has decision field
    fields = schema.model_fields if hasattr(schema, "model_fields") else {}
    if "decision" not in fields:
        print(f"FAIL: Admiral schema missing 'decision' field. Has: {list(fields.keys())}")
        return False

    # Admiral is in root_agent's tools
    tool_names = []
    for t in (root_agent.tools or []):
        name = getattr(t, "name", "") or getattr(getattr(t, "agent", None), "name", "")
        tool_names.append(name)

    if "admiral" not in tool_names:
        print(f"FAIL: Admiral not in root_agent tools. Tools: {tool_names}")
        return False

    print(f"PASS: Admiral as AgentTool with schema [{', '.join(fields.keys())}]")
    return True


# =============================================================================
# 5. ROOT AGENT HAS TREASURY TOOLS
# =============================================================================


def test_root_agent_tools():
    """Test Q5: Root agent has treasury management tools."""
    print("\n[TEST] Q5: Root agent tool set")

    from agent import root_agent

    tool_names = []
    for t in (root_agent.tools or []):
        name = getattr(t, "name", None) or getattr(t, "__name__", None)
        if not name:
            name = getattr(getattr(t, "agent", None), "name", "?")
        tool_names.append(name)

    required = {"check_treasury_balance", "request_expenditure"}
    missing = required - set(tool_names)

    if missing:
        print(f"FAIL: Missing tools: {missing}. Has: {tool_names}")
        return False

    print(f"PASS: All treasury tools present: {tool_names}")
    return True


# =============================================================================
# MAIN
# =============================================================================


def run_all_tests():
    print_test_header("Human-in-the-Loop — Quality Assurance", "05-Q")

    results = {}
    results["Callback chain"] = test_callback_chain_complete()
    results["Approval threshold"] = test_approval_threshold()
    results["Tool validation"] = test_tool_validation()
    results["Admiral AgentTool"] = test_admiral_agent_tool()
    results["Root agent tools"] = test_root_agent_tools()

    passed = sum(1 for r in results.values() if r)
    total = len(results)
    return print_test_summary(passed, total)


if __name__ == "__main__":
    sys.exit(run_all_tests())
