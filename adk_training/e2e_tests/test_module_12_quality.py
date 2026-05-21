"""
E2E Quality Assurance Tests for Module 12: Router Agent
========================================================

High-value tests for the intelligent dispatch pattern.
Complements structural tests in test_module_12.py.

Tests cover:
- Specialist count and name uniqueness
- Description quality (routing depends on description precision)
- Instruction mentions routing to sub_agents
- Domain coverage — no domain gaps
- Specialist instruction quality (role + format)
"""

import os
import sys

utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from utils import print_test_header, print_test_summary

module_path = os.path.join(os.path.dirname(__file__), "..", "module_12_router_agent")
module_path = os.path.abspath(module_path)
if module_path not in sys.path:
    sys.path.insert(0, module_path)


# =============================================================================
# 1. SPECIALIST COUNT + UNIQUENESS
# =============================================================================


def test_specialist_count_and_uniqueness():
    """Test Q1: Router has multiple specialists with unique names."""
    print("\n[TEST] Q1: Specialist count + uniqueness")

    from agent import root_agent

    subs = root_agent.sub_agents or []
    if len(subs) < 2:
        print(f"FAIL: Router needs >=2 specialists, has {len(subs)}")
        return False

    names = [s.name for s in subs]
    if len(names) != len(set(names)):
        dupes = [n for n in names if names.count(n) > 1]
        print(f"FAIL: Duplicate specialist names: {dupes}")
        return False

    print(f"PASS: {len(subs)} unique specialists: {names}")
    return True


# =============================================================================
# 2. DESCRIPTION QUALITY — Routing depends on this
# =============================================================================


def test_specialist_descriptions():
    """Test Q2: Every specialist has a substantial description for routing."""
    print("\n[TEST] Q2: Specialist description quality")

    from agent import root_agent

    errors = []
    for sub in (root_agent.sub_agents or []):
        desc = getattr(sub, "description", "") or ""
        if len(desc) < 20:
            errors.append(f"'{sub.name}': description too short ({len(desc)} chars)")
        elif "," not in desc and " i " not in desc and " and " not in desc:
            errors.append(f"'{sub.name}': description lacks domain keywords (no commas/conjunctions)")

    if errors:
        for err in errors:
            print(f"  - {err}")
        print(f"FAIL: {len(errors)} description issues — routing will fail")
        return False

    print(f"PASS: All specialists have routing-quality descriptions")
    return True


# =============================================================================
# 3. ROUTER INSTRUCTION MENTIONS SUB-AGENTS
# =============================================================================


def test_router_instruction_references_subs():
    """Test Q3: Captain router instruction mentions specialist names/domains."""
    print("\n[TEST] Q3: Router instruction references specialists")

    from agent import root_agent

    instruction = getattr(root_agent, "instruction", "") or ""

    if len(instruction) < 50:
        print(f"FAIL: Router instruction too short ({len(instruction)} chars)")
        return False

    sub_names = [s.name for s in (root_agent.sub_agents or [])]

    # Instruction should reference at least some specialist names or domains
    found = 0
    for name in sub_names:
        if name in instruction.lower():
            found += 1

    if found == 0:
        print(f"FAIL: Router instruction doesn't mention any specialist: {sub_names}")
        return False

    print(f"PASS: Router instruction references {found}/{len(sub_names)} specialists")
    return True


# =============================================================================
# 4. NO DOMAIN GAPS — Router instruction covers all specialists
# =============================================================================


def test_no_domain_gaps():
    """Test Q4: Router instruction maps clear domains to all specialists."""
    print("\n[TEST] Q4: Domain coverage (no gaps)")

    from agent import root_agent

    instruction = (getattr(root_agent, "instruction", "") or "").lower()
    subs = root_agent.sub_agents or []

    # Each specialist's description keywords should appear somewhere in router instruction
    unmapped = []
    for sub in subs:
        desc = (getattr(sub, "description", "") or "").lower()
        # Extract first 3 significant words (>4 chars)
        keywords = [w for w in desc.split() if len(w) > 4][:3]
        found = any(kw in instruction for kw in keywords)
        if not found:
            unmapped.append(f"'{sub.name}' (keywords: {keywords})")

    if unmapped:
        for u in unmapped:
            print(f"  - gap: {u}")
        print(f"FAIL: {len(unmapped)} specialists not mapped in router instruction")
        return False

    print(f"PASS: All {len(subs)} specialist domains mapped in router instruction")
    return True


# =============================================================================
# 5. SPECIALIST INSTRUCTION QUALITY
# =============================================================================


def test_specialist_instruction_quality():
    """Test Q5: Each specialist has role-specific instruction."""
    print("\n[TEST] Q5: Specialist instruction quality")

    from agent import root_agent

    errors = []
    for sub in (root_agent.sub_agents or []):
        instr = (getattr(sub, "instruction", "") or "").strip()
        if len(instr) < 30:
            errors.append(f"'{sub.name}': instruction too short ({len(instr)} chars)")
            continue

        role_words = ["jeste", "you are", "your role", "twoj"]
        has_role = any(w in instr.lower() for w in role_words)
        if not has_role:
            errors.append(f"'{sub.name}': no role definition")

    if errors:
        for err in errors:
            print(f"  - {err}")
        print(f"FAIL: {len(errors)} instruction quality issues")
        return False

    names = [s.name for s in root_agent.sub_agents]
    print(f"PASS: All {len(names)} specialists have role-specific instructions")
    return True


# =============================================================================
# MAIN
# =============================================================================


def run_all_tests():
    print_test_header("Router Agent — Quality Assurance", "12-Q")

    results = {}
    results["Specialist count + unique"] = test_specialist_count_and_uniqueness()
    results["Description quality"] = test_specialist_descriptions()
    results["Router refs specialists"] = test_router_instruction_references_subs()
    results["No domain gaps"] = test_no_domain_gaps()
    results["Specialist instruction QA"] = test_specialist_instruction_quality()

    passed = sum(1 for r in results.values() if r)
    total = len(results)
    return print_test_summary(passed, total)


if __name__ == "__main__":
    sys.exit(run_all_tests())
