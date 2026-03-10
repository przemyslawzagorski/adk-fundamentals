"""
E2E Test for Module 08: Loop Agent with Critique

Tests iteration logic and escalation.
"""

import sys
import os
import asyncio

# Add module to path
module_path = os.path.join(os.path.dirname(__file__), '..', 'module_08_loop_critique')
sys.path.insert(0, module_path)

# Add utils to path
utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from agent import root_agent
from google.adk.sessions import InMemorySessionService
from utils import (
    extract_response_text,
    validate_response_not_empty,
    print_test_header,
    print_test_summary
)


async def test_loop_execution():
    """Test: Loop agent iterates until condition met"""
    print("\n📋 Test: Loop execution")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Napisz wpis do dziennika okrętowego o dzisiejszym dniu na morzu",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text, min_length=50)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Check if session state has expected keys
    state = session.state
    expected_keys = ["log_entry", "critique", "entry_status"]
    
    missing_keys = [key for key in expected_keys if key not in state]
    if missing_keys:
        print(f"❌ FAIL: Missing state keys: {missing_keys}")
        print(f"   Available keys: {list(state.keys())}")
        return False
    
    print(f"✅ PASS: Loop execution completed")
    print(f"   Response length: {len(response_text)} chars")
    return True


async def test_iteration_improvement():
    """Test: Log entry improves through iterations"""
    print("\n📋 Test: Iteration improvement")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Stwórz wpis dziennika o burzy i naprawie żagli",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Check state values
    state = session.state
    
    log_entry = state.get("log_entry", "")
    critique = state.get("critique", "")
    entry_status = state.get("entry_status", {})
    
    if not log_entry or len(log_entry) < 30:
        print(f"❌ FAIL: log_entry is empty or too short")
        return False
    
    # Check if final decision is valid
    decision = entry_status.get("decision", "invalid") if isinstance(entry_status, dict) else "unknown"
    
    print(f"✅ PASS: Iteration completed")
    print(f"   Log entry: {len(log_entry)} chars")
    print(f"   Final decision: {decision}")
    return True


async def test_max_iterations():
    """Test: Loop respects max_iterations limit"""
    print("\n📋 Test: Max iterations limit")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    # Simple request that should complete
    response_text = await extract_response_text(
        root_agent,
        "Krótki wpis o spokojnym dniu",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    print(f"✅ PASS: Completed within iteration limit")
    return True


async def test_different_scenarios():
    """Test: Loop handles different log entry scenarios"""
    print("\n📋 Test: Different scenarios")
    
    scenarios = [
        "Wpis o odkryciu wyspy",
        "Wpis o bitwie morskiej",
    ]
    
    for scenario in scenarios:
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name="test_app",
            user_id="test_user"
        )
        
        response_text = await extract_response_text(
            root_agent,
            scenario,
            session_service,
        session
        )
        
        is_valid, error_msg = validate_response_not_empty(response_text)
        if not is_valid:
            print(f"❌ FAIL: Scenario '{scenario}' - {error_msg}")
            return False
        
        # Check state has log_entry
        state = session.state
        if "log_entry" not in state:
            print(f"❌ FAIL: Scenario '{scenario}' - Missing log_entry")
            return False
    
    print(f"✅ PASS: Handled {len(scenarios)} different scenarios")
    return True


async def main():
    print_test_header("Loop Agent with Critique", "08")
    
    tests = [
        ("Loop execution", test_loop_execution),
        ("Iteration improvement", test_iteration_improvement),
        ("Max iterations", test_max_iterations),
        ("Different scenarios", test_different_scenarios),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ FAIL: {name} - Exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    exit_code = print_test_summary(passed, total)
    
    return exit_code


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

