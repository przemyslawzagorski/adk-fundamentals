"""
Manual E2E Test for Module 09: Simple Database Agent (SQLite)

This test requires manual setup:
1. Run: python adk_training/module_09_database_simple/init_database.py
2. Verify hotels.db exists
3. Run this test

Tests database tools with SQLite backend.
"""

import sys
import os
import asyncio

# Add module to path
module_path = os.path.join(os.path.dirname(__file__), '..', '..', 'module_09_database_simple')
sys.path.insert(0, module_path)

# Add utils to path
utils_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, utils_path)

from agent import root_agent
from google.adk.sessions import InMemorySessionService
from utils import (
    extract_response_with_tool_calls,
    validate_response_not_empty,
    print_test_header,
    print_test_summary
)


async def test_search_by_name():
    """Test: Search hotels by name"""
    print("\n📋 Test: Search by name")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Znajdź hotel Grand",
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Should mention hotel name
    if "grand" not in response_text.lower():
        print(f"⚠️  WARNING: Response doesn't mention 'Grand'")
    
    print(f"✅ PASS: Search by name successful")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    return True


async def test_search_by_location():
    """Test: Search hotels by city"""
    print("\n📋 Test: Search by location")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Jakie hotele są w Warszawie?",
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Should mention Warsaw or hotels
    response_lower = response_text.lower()
    if "warszaw" not in response_lower and "warsaw" not in response_lower:
        print(f"⚠️  WARNING: Response doesn't mention Warsaw")
    
    print(f"✅ PASS: Search by location successful")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    return True


async def test_search_by_price():
    """Test: Search hotels by price range"""
    print("\n📋 Test: Search by price range")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Pokaż hotele w cenie 200-400 zł",
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    print(f"✅ PASS: Search by price successful")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    return True


async def test_get_hotel_details():
    """Test: Get specific hotel details"""
    print("\n📋 Test: Get hotel details")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Pokaż szczegóły hotelu o ID 1",
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    print(f"✅ PASS: Get hotel details successful")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    return True


async def main():
    print_test_header("Simple Database Agent (SQLite)", "09-Simple")
    
    # Check if database exists
    db_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', 
        'module_09_database_simple', 
        'hotels.db'
    )
    
    if not os.path.exists(db_path):
        print("\n❌ SETUP REQUIRED:")
        print("   Database not found. Please run:")
        print("   python adk_training/module_09_database_simple/init_database.py")
        return 1
    
    print(f"\n✅ Database found: {db_path}")
    
    tests = [
        ("Search by name", test_search_by_name),
        ("Search by location", test_search_by_location),
        ("Search by price", test_search_by_price),
        ("Get hotel details", test_get_hotel_details),
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

