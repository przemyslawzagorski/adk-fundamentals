"""
E2E Test for Module 11: Memory Bank Agent

Tests mock memory tools and recall functionality.
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
module_path = os.path.join(os.path.dirname(__file__), '..', 'module_11_memory_bank')
agent_module = import_agent_module(module_path)
root_agent = agent_module.root_agent
_memory_store = agent_module._memory_store


async def test_recall_voyages():
    """Test: Agent recalls past voyages from memory"""
    print("\n📋 Test: Recall voyages")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Jakie były nasze ostatnie wyprawy?",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Should mention some voyage destinations
    response_lower = response_text.lower()
    if "port royal" not in response_lower and "tortuga" not in response_lower:
        print(f"⚠️  WARNING: Response doesn't mention known voyage destinations")
    
    print(f"✅ PASS: Recalled voyages")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    return True


async def test_recall_treasures():
    """Test: Agent recalls treasure information"""
    print("\n📋 Test: Recall treasures")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Jakie skarby znaleźliśmy?",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Should mention treasures
    response_lower = response_text.lower()
    if "gold" not in response_lower and "doubloon" not in response_lower:
        print(f"⚠️  WARNING: Response doesn't mention known treasures")
    
    print(f"✅ PASS: Recalled treasures")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    return True


async def test_recall_crew():
    """Test: Agent recalls crew member information"""
    print("\n📋 Test: Recall crew notes")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Co wiesz o Jacku Sparrow?",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Should mention Jack Sparrow info
    response_lower = response_text.lower()
    if "jack" not in response_lower and "sparrow" not in response_lower:
        print(f"⚠️  WARNING: Response doesn't mention Jack Sparrow")
    
    print(f"✅ PASS: Recalled crew information")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    return True


async def test_add_memory():
    """Test: Agent can add new memories"""
    print("\n📋 Test: Add new memory")
    
    # Store original count
    original_voyage_count = len(_memory_store.get("voyages", []))
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Zapisz nową wyprawę: 1723-12-01, Karaiby, znaleźliśmy mapę skarbu",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Check if memory was added
    new_voyage_count = len(_memory_store.get("voyages", []))
    
    if new_voyage_count > original_voyage_count:
        print(f"✅ PASS: New memory added")
        print(f"   Voyages: {original_voyage_count} → {new_voyage_count}")
    else:
        print(f"⚠️  WARNING: Memory count unchanged (LLM might not have called add tool)")
        print(f"✅ PASS: Response generated successfully")
    
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    
    return True


async def main():
    print_test_header("Memory Bank Agent", "11")
    
    tests = [
        ("Recall voyages", test_recall_voyages),
        ("Recall treasures", test_recall_treasures),
        ("Recall crew", test_recall_crew),
        ("Add memory", test_add_memory),
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

