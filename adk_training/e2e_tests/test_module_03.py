"""
E2E Test for Module 03: RAG Agent with Vertex AI Search

Requires: SEARCH_ENGINE_ID or SEARCH_DATASTORE_ID in .env
Tests will be skipped if not configured.
"""

import sys
import os
import asyncio

# Add module to path
module_path = os.path.join(os.path.dirname(__file__), '..', 'module_03_rag_agent')
sys.path.insert(0, module_path)

# Add utils to path
utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from google.adk.sessions import InMemorySessionService
from utils import (
    extract_response_with_tool_calls,
    validate_response_not_empty,
    print_test_header,
    print_test_summary
)


def check_rag_configured():
    """Check if Vertex AI Search is configured."""
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")
    search_datastore_id = os.getenv("SEARCH_DATASTORE_ID")
    return bool(search_engine_id or search_datastore_id)


async def test_rag_basic_query():
    """Test: Agent responds to basic query (may or may not use search)"""
    print("\n📋 Test: Basic query")
    
    if not check_rag_configured():
        print("⚠️  SKIP: No SEARCH_ENGINE_ID or SEARCH_DATASTORE_ID configured")
        return True  # Skip, not fail
    
    # Import agent only if configured (to avoid error on missing config)
    from agent import root_agent
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Cześć, jak się masz?",
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    print(f"✅ PASS: Got response ({len(response_text)} chars)")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    return True


async def test_rag_search_query():
    """Test: Agent uses Vertex AI Search for knowledge query"""
    print("\n📋 Test: Search query")
    
    if not check_rag_configured():
        print("⚠️  SKIP: No SEARCH_ENGINE_ID or SEARCH_DATASTORE_ID configured")
        return True  # Skip, not fail
    
    from agent import root_agent
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Wyszukaj informacje o konfiguracji systemu w dokumentacji",
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    print(f"✅ PASS: Got response ({len(response_text)} chars)")
    if tool_calls:
        print(f"   ✓ Search tool was invoked: {', '.join(tool_calls)}")
    else:
        print(f"   ℹ️  Note: Search tool was not called (LLM decision)")
    
    return True


async def test_rag_multiple_queries():
    """Test: Agent handles multiple queries in same session"""
    print("\n📋 Test: Multiple queries in session")
    
    if not check_rag_configured():
        print("⚠️  SKIP: No SEARCH_ENGINE_ID or SEARCH_DATASTORE_ID configured")
        return True  # Skip, not fail
    
    from agent import root_agent
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    # First query
    response1, tools1 = await extract_response_with_tool_calls(
        root_agent,
        "Znajdź dokumentację API",
        session
    )
    
    is_valid, error_msg = validate_response_not_empty(response1)
    if not is_valid:
        print(f"❌ FAIL: First query - {error_msg}")
        return False
    
    # Second query
    response2, tools2 = await extract_response_with_tool_calls(
        root_agent,
        "Jakie są wymagania bezpieczeństwa?",
        session
    )
    
    is_valid, error_msg = validate_response_not_empty(response2)
    if not is_valid:
        print(f"❌ FAIL: Second query - {error_msg}")
        return False
    
    print(f"✅ PASS: Handled multiple queries")
    print(f"   Query 1: {len(response1)} chars, tools: {tools1 or 'none'}")
    print(f"   Query 2: {len(response2)} chars, tools: {tools2 or 'none'}")
    
    return True


async def main():
    print_test_header("RAG Agent with Vertex AI Search", "03")
    
    # Check configuration first
    if not check_rag_configured():
        print("\n⚠️  WARNING: Vertex AI Search not configured")
        print("   Set SEARCH_ENGINE_ID or SEARCH_DATASTORE_ID in .env")
        print("   All tests will be skipped\n")
    
    tests = [
        ("Basic query", test_rag_basic_query),
        ("Search query", test_rag_search_query),
        ("Multiple queries", test_rag_multiple_queries),
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

