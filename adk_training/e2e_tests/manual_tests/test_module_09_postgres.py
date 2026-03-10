"""
Manual E2E Test for Module 09: MCP Database Agent (PostgreSQL)

This test requires manual setup:
1. Set up PostgreSQL database (Neon.tech, Supabase, or local)
2. Run setup_db.sql to create schema and sample data
3. Configure DATABASE_URL in .env
4. Start Toolbox server: ./toolbox --tools-file toolbox.yaml
5. Run this test

Tests MCP toolset integration with PostgreSQL backend.
"""

import sys
import os
import asyncio

# Add module to path
module_path = os.path.join(os.path.dirname(__file__), '..', '..', 'module_09_database_postgres')
sys.path.insert(0, module_path)

# Add utils to path
utils_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, utils_path)

from agent import root_agent, TOOLBOX_URL
from google.adk.sessions import InMemorySessionService
from utils import (
    extract_response_with_tool_calls,
    validate_response_not_empty,
    print_test_header,
    print_test_summary
)


async def test_mcp_connection():
    """Test: MCP Toolbox connection is available"""
    print("\n📋 Test: MCP Toolbox connection")
    
    try:
        import requests
        response = requests.get(f"{TOOLBOX_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ PASS: Toolbox server is running at {TOOLBOX_URL}")
            return True
        else:
            print(f"❌ FAIL: Toolbox server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Cannot connect to Toolbox server: {e}")
        print(f"   Make sure Toolbox is running: ./toolbox --tools-file toolbox.yaml")
        return False


async def test_search_hotels():
    """Test: Search hotels via MCP tools"""
    print("\n📋 Test: Search hotels")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Pokaż hotele w Warszawie",
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    print(f"✅ PASS: Search hotels successful")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    return True


async def test_price_range_search():
    """Test: Search by price range via MCP"""
    print("\n📋 Test: Price range search")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Znajdź hotele w cenie 300-500 zł",
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    print(f"✅ PASS: Price range search successful")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    return True


async def test_top_rated_hotels():
    """Test: Get top-rated hotels"""
    print("\n📋 Test: Top-rated hotels")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Pokaż najlepiej oceniane hotele",
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    print(f"✅ PASS: Top-rated hotels query successful")
    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")
    return True


async def main():
    print_test_header("MCP Database Agent (PostgreSQL)", "09-Postgres")
    
    print("\n⚙️  SETUP REQUIREMENTS:")
    print("   1. PostgreSQL database configured (DATABASE_URL in .env)")
    print("   2. Database schema created (run setup_db.sql)")
    print("   3. Toolbox server running: ./toolbox --tools-file toolbox.yaml")
    print(f"   4. Toolbox URL: {TOOLBOX_URL}")
    
    tests = [
        ("MCP connection", test_mcp_connection),
        ("Search hotels", test_search_hotels),
        ("Price range search", test_price_range_search),
        ("Top-rated hotels", test_top_rated_hotels),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append(result)
            
            # If MCP connection fails, skip remaining tests
            if name == "MCP connection" and not result:
                print("\n⚠️  Skipping remaining tests (MCP server not available)")
                break
                
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

