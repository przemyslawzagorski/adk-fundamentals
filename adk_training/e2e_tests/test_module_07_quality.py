"""
E2E Quality Assurance Tests for Module 07: Parallel Agent
==========================================================

High-value tests for the fork-join pattern.
Complements structural tests in test_module_07.py.

Tests cover:
- Parallel agent has >=2 scouts (fork width)
- Each scout has isolated output_key (no cross-contamination)
- Spymaster references all scout output_keys (complete synthesis)
- Root agent wraps parallel + synthesis in SequentialAgent
- Scout instructions are domain-specific (not copy-paste)
"""

import os
import sys

utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from utils import print_test_header, print_test_summary

module_path = os.path.join(os.path.dirname(__file__), "..", "module_07_parallel_agent")
module_path = os.path.abspath(module_path)
if module_path not in sys.path:
    sys.path.insert(0, module_path)


# =============================================================================
# 1. FORK WIDTH — ParallelAgent has 3 scouts
# =============================================================================


def test_parallel_fork_width():
    """Test Q1: Parallel stage has multiple scouts running concurrently."""
    print("\n[TEST] Q1: Parallel fork width")

    from agent import root_agent
    from google.adk.agents import SequentialAgent, ParallelAgent

    if not isinstance(root_agent, SequentialAgent):
        print(f"FAIL: Root should be SequentialAgent wrapper, is {type(root_agent).__name__}")
        return False

    parallel_stage = None
    for sub in root_agent.sub_agents:
        if isinstance(sub, ParallelAgent):
            parallel_stage = sub
            break

    if not parallel_stage:
        print("FAIL: No ParallelAgent stage found in root pipeline")
        return False

    scout_count = len(parallel_stage.sub_agents or [])
    if scout_count < 2:
        print(f"FAIL: Parallel stage needs >=2 scouts, has {scout_count}")
        return False

    names = [s.name for s in parallel_stage.sub_agents]
    print(f"PASS: {scout_count} parallel scouts: {names}")
    return True


# =============================================================================
# 2. ISOLATED OUTPUT KEYS — Each scout writes to own key
# =============================================================================


def test_scout_output_keys_isolated():
    """Test Q2: Each scout has unique output_key (no cross-contamination)."""
    print("\n[TEST] Q2: Scout output_key isolation")

    from agent import root_agent
    from google.adk.agents import ParallelAgent

    parallel_stage = None
    for sub in root_agent.sub_agents:
        if isinstance(sub, ParallelAgent):
            parallel_stage = sub
            break

    keys = []
    for scout in parallel_stage.sub_agents:
        key = getattr(scout, "output_key", None)
        if not key:
            print(f"FAIL: Scout '{scout.name}' has no output_key — result lost")
            return False
        keys.append(key)

    if len(keys) != len(set(keys)):
        print(f"FAIL: Duplicate output_keys among scouts: {keys}")
        return False

    print(f"PASS: All scouts isolated: {keys}")
    return True


# =============================================================================
# 3. SPYMASTER REFERENCES ALL SCOUT KEYS
# =============================================================================


def test_spymaster_references_all_scouts():
    """Test Q3: Spymaster instruction references ALL scout output_keys."""
    print("\n[TEST] Q3: Spymaster ↔ scout output_key references")

    from agent import root_agent
    from google.adk.agents import ParallelAgent

    parallel_stage = None
    synthesis_agent = None
    for sub in root_agent.sub_agents:
        if isinstance(sub, ParallelAgent):
            parallel_stage = sub
        else:
            synthesis_agent = sub

    if not synthesis_agent:
        print("FAIL: No synthesis agent found after parallel stage")
        return False

    instruction = getattr(synthesis_agent, "instruction", "") or ""
    scout_keys = [
        getattr(s, "output_key", "") for s in parallel_stage.sub_agents
    ]

    missing = []
    for key in scout_keys:
        if key and f"{{{key}}}" not in instruction:
            missing.append(key)

    if missing:
        print(f"FAIL: Spymaster doesn't reference scout keys: {missing}")
        return False

    print(f"PASS: Spymaster references all {len(scout_keys)} scout outputs")
    return True


# =============================================================================
# 4. PIPELINE STRUCTURE — Sequential[Parallel, Synthesis]
# =============================================================================


def test_pipeline_structure():
    """Test Q4: Root is Sequential wrapping Parallel + synthesis."""
    print("\n[TEST] Q4: Pipeline structure integrity")

    from agent import root_agent
    from google.adk.agents import SequentialAgent, ParallelAgent

    subs = root_agent.sub_agents or []
    if len(subs) != 2:
        print(f"FAIL: Expected 2 stages (parallel + synthesis), got {len(subs)}")
        return False

    if not isinstance(subs[0], ParallelAgent):
        print(f"FAIL: First stage should be ParallelAgent, is {type(subs[0]).__name__}")
        return False

    # Second stage should have output_key for briefing
    synth_key = getattr(subs[1], "output_key", None)
    if not synth_key:
        print("FAIL: Synthesis agent has no output_key")
        return False

    print(f"PASS: Sequential[ParallelAgent → {subs[1].name}(output_key='{synth_key}')]")
    return True


# =============================================================================
# 5. SCOUT INSTRUCTIONS ARE DOMAIN-SPECIFIC
# =============================================================================


def test_scout_instructions_diverse():
    """Test Q5: Scout instructions are domain-unique (not copy-pasted)."""
    print("\n[TEST] Q5: Scout instruction diversity")

    from agent import root_agent
    from google.adk.agents import ParallelAgent

    parallel_stage = None
    for sub in root_agent.sub_agents:
        if isinstance(sub, ParallelAgent):
            parallel_stage = sub
            break

    instructions = []
    for scout in parallel_stage.sub_agents:
        instr = (getattr(scout, "instruction", "") or "").strip()
        if len(instr) < 50:
            print(f"FAIL: Scout '{scout.name}' instruction too short ({len(instr)} chars)")
            return False
        instructions.append(instr)

    # Check pairwise similarity — if >80% same tokens, likely copy-paste
    for i in range(len(instructions)):
        for j in range(i + 1, len(instructions)):
            words_i = set(instructions[i].lower().split())
            words_j = set(instructions[j].lower().split())
            overlap = len(words_i & words_j) / max(len(words_i | words_j), 1)
            if overlap > 0.85:
                scouts = parallel_stage.sub_agents
                print(
                    f"FAIL: '{scouts[i].name}' and '{scouts[j].name}' "
                    f"instructions too similar ({overlap:.0%})"
                )
                return False

    print(f"PASS: All {len(instructions)} scout instructions are domain-specific")
    return True


# =============================================================================
# MAIN
# =============================================================================


def run_all_tests():
    print_test_header("Parallel Agent — Quality Assurance", "07-Q")

    results = {}
    results["Parallel fork width"] = test_parallel_fork_width()
    results["Scout output_key isolation"] = test_scout_output_keys_isolated()
    results["Spymaster refs all scouts"] = test_spymaster_references_all_scouts()
    results["Pipeline structure"] = test_pipeline_structure()
    results["Scout instruction diversity"] = test_scout_instructions_diverse()

    passed = sum(1 for r in results.values() if r)
    total = len(results)
    return print_test_summary(passed, total)


if __name__ == "__main__":
    sys.exit(run_all_tests())
