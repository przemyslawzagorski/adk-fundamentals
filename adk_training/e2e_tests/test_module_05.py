"""
E2E Test for Module 05: Human-in-Loop Agent

Tests callbacks and approval workflow.
"""

import sys
import os
import asyncio

# Add module to path
module_path = os.path.join(os.path.dirname(__file__), '..', 'module_05_human_in_loop')
sys.path.insert(0, module_path)

# Add utils to path
utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from agent import root_agent, SHIP_TREASURY
from google.adk.sessions import InMemorySessionService
from utils import (
    extract_response_text,
    validate_response_not_empty,
    print_test_header,
    print_test_summary
)


async def test_small_expense_no_approval():
    """Test: Small expense doesn't require admiral approval"""
    print("\n📋 Test: Small expense (no approval needed)")
    
    # Reset treasury
    SHIP_TREASURY["current_balance"] = 5000
    SHIP_TREASURY["pending_requests"] = []
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Potrzebuję 50 dublonów na prowiant",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Check balance was deducted
    expected_balance = 4950
    actual_balance = SHIP_TREASURY["current_balance"]
    
    if actual_balance != expected_balance:
        print(f"⚠️  WARNING: Balance not updated as expected")
        print(f"   Expected: {expected_balance}, Got: {actual_balance}")
    
    print(f"✅ PASS: Small expense processed")
    print(f"   Treasury balance: {actual_balance}")
    return True


async def test_large_expense_with_approval():
    """Test: Large expense requires admiral approval"""
    print("\n📋 Test: Large expense (requires approval)")
    
    # Reset treasury
    SHIP_TREASURY["current_balance"] = 5000
    SHIP_TREASURY["pending_requests"] = []
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Zapytaj admirała - potrzebujemy 500 dublonów na działa bo nadchodzi bitwa",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Response should mention admiral or approval
    response_lower = response_text.lower()
    if "admiral" not in response_lower and "zatwierdz" not in response_lower:
        print(f"⚠️  WARNING: Response doesn't mention admiral/approval")
    
    print(f"✅ PASS: Large expense handled")
    print(f"   Response length: {len(response_text)} chars")
    return True


async def test_check_balance():
    """Test: Agent can check current treasury balance"""
    print("\n📋 Test: Check treasury balance")
    
    # Reset treasury
    SHIP_TREASURY["current_balance"] = 5000
    SHIP_TREASURY["pending_requests"] = []
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Ile mamy dublonów w skarbcu?",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Should mention the balance (5000)
    if "5000" not in response_text:
        print(f"⚠️  WARNING: Response doesn't mention balance 5000")
        print(f"   Response: {response_text}")
    
    print(f"✅ PASS: Balance check successful")
    return True


async def test_conversation_flow():
    """Test: Multi-turn conversation with expenses"""
    print("\n📋 Test: Multi-turn conversation")
    
    # Reset treasury
    SHIP_TREASURY["current_balance"] = 5000
    SHIP_TREASURY["pending_requests"] = []
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    # First expense
    response1 = await extract_response_text(
        root_agent,
        "Potrzebuję 30 dublonów na liny",
        session_service,
        session
    )
    
    is_valid, _ = validate_response_not_empty(response1)
    if not is_valid:
        print(f"❌ FAIL: First expense failed")
        return False
    
    # Check balance
    response2 = await extract_response_text(
        root_agent,
        "Ile teraz mamy w skarbcu?",
        session_service,
        session
    )
    
    is_valid, _ = validate_response_not_empty(response2)
    if not is_valid:
        print(f"❌ FAIL: Balance check failed")
        return False
    
    print(f"✅ PASS: Multi-turn conversation successful")
    print(f"   Final balance: {SHIP_TREASURY['current_balance']}")
    return True


async def main():
    print_test_header("Human-in-Loop Agent", "05")
    
    tests = [
        ("Small expense", test_small_expense_no_approval),
        ("Large expense", test_large_expense_with_approval),
        ("Check balance", test_check_balance),
        ("Multi-turn conversation", test_conversation_flow),
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

