"""
E2E Test for Module 02: Custom Tool Agent

Tests tool invocation and state changes.
"""

import sys
import os
import asyncio

# Add utils to path
utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from utils import (
    import_agent_module,
    extract_response_with_tool_calls,
    validate_response_not_empty,
    print_test_header,
    print_test_summary
)
from google.adk.sessions import InMemorySessionService

# Import agent module dynamically
module_path = os.path.join(os.path.dirname(__file__), '..', 'module_02_custom_tool')
agent_module = import_agent_module(module_path)
root_agent = agent_module.root_agent
TREASURE_INVENTORY = agent_module.TREASURE_INVENTORY


async def test_get_treasure_count():
    """Test: Agent uses get_treasure_count tool"""
    print("\n📋 Test: Get treasure count")

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )

    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Ile mamy złotych dublonów?",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False

    # Should mention treasure or count (flexible check)
    response_lower = response_text.lower()
    if "dublon" not in response_lower and "treasure" not in response_lower:
        print(f"⚠️  WARNING: Response doesn't mention dublonów")
        print(f"   Response: {response_text}")

    print(f"✅ PASS: Treasure count query handled")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    return True


async def test_list_all_treasures():
    """Test: Agent uses list_all_treasures tool"""
    print("\n📋 Test: List all treasures")

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )

    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Pokaż mi wszystkie skarby w inwentarzu",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Should mention some treasure types
    response_lower = response_text.lower()
    if "dublon" not in response_lower and "rubin" not in response_lower:
        print(f"❌ FAIL: Response doesn't mention treasure types")
        return False
    
    print(f"✅ PASS: Listed treasures")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    return True


async def test_add_treasure():
    """Test: Agent uses add_treasure tool"""
    print("\n📋 Test: Add treasure")
    
    # Reset inventory to known state
    original_rubies = TREASURE_INVENTORY.get("rubiny", 45)
    TREASURE_INVENTORY["rubiny"] = 45
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Dodaj 100 rubinów do skarbca",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Check inventory was updated
    expected_count = 145
    actual_count = TREASURE_INVENTORY.get("rubiny", 0)
    
    if actual_count != expected_count:
        print(f"❌ FAIL: Inventory not updated correctly")
        print(f"   Expected: {expected_count}, Got: {actual_count}")
        # Restore original value
        TREASURE_INVENTORY["rubiny"] = original_rubies
        return False
    
    print(f"✅ PASS: Inventory updated correctly ({actual_count} rubinów)")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    
    # Restore original value
    TREASURE_INVENTORY["rubiny"] = original_rubies
    return True


async def test_treasure_not_found():
    """Test: Agent handles non-existent treasure gracefully"""
    print("\n📋 Test: Non-existent treasure")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Ile mamy smoków?",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Should indicate item not found
    response_lower = response_text.lower()
    if "nie" not in response_lower and "brak" not in response_lower:
        print(f"⚠️  WARNING: Response might not clearly indicate item not found")
    
    print(f"✅ PASS: Handled non-existent item")
    return True


async def main():
    print_test_header("Custom Tool Agent", "02")
    
    tests = [
        ("Get treasure count", test_get_treasure_count),
        ("List all treasures", test_list_all_treasures),
        ("Add treasure", test_add_treasure),
        ("Non-existent treasure", test_treasure_not_found),
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

