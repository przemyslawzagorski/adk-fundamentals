"""
E2E Test for Module 04: Sequential Agent

Tests multi-agent pipeline flow with output_keys.
"""

import sys
import os
import asyncio

# Add utils to path
utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from utils import (
    import_agent_module,
    extract_response_text,
    validate_response_not_empty,
    print_test_header,
    print_test_summary
)
from google.adk.sessions import InMemorySessionService

# Import agent module dynamically
module_path = os.path.join(os.path.dirname(__file__), '..', 'module_04_sequential_agent')
agent_module = import_agent_module(module_path)
root_agent = agent_module.root_agent


async def test_sequential_pipeline():
    """Test: Sequential agents execute in order"""
    print("\n📋 Test: Sequential pipeline execution")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Zaplanuj rajd na Port Royal",
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
    expected_keys = ["raport_wywiadu", "plan_bitwy", "decyzja_kapitana"]
    
    missing_keys = [key for key in expected_keys if key not in state]
    if missing_keys:
        print(f"❌ FAIL: Missing state keys: {missing_keys}")
        print(f"   Available keys: {list(state.keys())}")
        return False
    
    print(f"✅ PASS: Sequential pipeline executed")
    print(f"   Response length: {len(response_text)} chars")
    print(f"   State keys present: {expected_keys}")
    return True


async def test_state_propagation():
    """Test: Data flows through pipeline via state"""
    print("\n📋 Test: State propagation between agents")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Zaplanuj operację na wyspie skarbów",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Check state values are not empty
    state = session.state
    
    raport = state.get("raport_wywiadu", "")
    plan = state.get("plan_bitwy", "")
    decyzja = state.get("decyzja_kapitana", "")
    
    if not raport or len(raport) < 20:
        print(f"❌ FAIL: raport_wywiadu is empty or too short")
        return False
    
    if not plan or len(plan) < 20:
        print(f"❌ FAIL: plan_bitwy is empty or too short")
        return False
    
    if not decyzja or len(decyzja) < 20:
        print(f"❌ FAIL: decyzja_kapitana is empty or too short")
        return False
    
    print(f"✅ PASS: State propagated correctly")
    print(f"   raport_wywiadu: {len(raport)} chars")
    print(f"   plan_bitwy: {len(plan)} chars")
    print(f"   decyzja_kapitana: {len(decyzja)} chars")
    return True


async def test_different_targets():
    """Test: Pipeline handles different raid targets"""
    print("\n📋 Test: Different raid targets")
    
    targets = [
        "statek handlowy",
        "fort nadbrzeżny",
    ]
    
    for target in targets:
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name="test_app",
            user_id="test_user"
        )
        
        response_text = await extract_response_text(
            root_agent,
            f"Zaplanuj rajd na {target}",
            session_service,
        session
        )
        
        is_valid, error_msg = validate_response_not_empty(response_text)
        if not is_valid:
            print(f"❌ FAIL: Target '{target}' - {error_msg}")
            return False
        
        # Check state has all keys
        state = session.state
        if "raport_wywiadu" not in state or "plan_bitwy" not in state:
            print(f"❌ FAIL: Target '{target}' - Missing state keys")
            return False
    
    print(f"✅ PASS: Handled {len(targets)} different targets")
    return True


async def main():
    print_test_header("Sequential Agent Pipeline", "04")
    
    tests = [
        ("Sequential pipeline", test_sequential_pipeline),
        ("State propagation", test_state_propagation),
        ("Different targets", test_different_targets),
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

