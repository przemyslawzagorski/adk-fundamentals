"""
E2E Test for Module 01: Hello World Agent

Tests basic agent functionality without external dependencies.
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
    print_test_result,
    print_test_summary
)
from google.adk.sessions import InMemorySessionService

# Import agent module dynamically
module_path = os.path.join(os.path.dirname(__file__), '..', 'module_01_hello_world')
agent_module = import_agent_module(module_path)
root_agent = agent_module.root_agent


async def test_basic_greeting():
    """Test: Agent responds to basic greeting in Polish"""
    print("\n📋 Test: Basic greeting")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    # Execute agent
    response_text = await extract_response_text(
        root_agent,
        "Cześć! Kim jesteś?",
        session_service,
        session
    )
    
    # Validate
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    print(f"✅ PASS: Got response ({len(response_text)} chars)")
    print(f"   Preview: {response_text[:100]}...")
    return True


async def test_technical_question():
    """Test: Agent responds to technical question"""
    print("\n📋 Test: Technical question about Python")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Opowiedz mi krótko o języku Python",
        session_service,
        session
    )
    
    # Validate - should mention Python
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    if "python" not in response_text.lower():
        print(f"❌ FAIL: Response doesn't mention Python")
        return False
    
    print(f"✅ PASS: Response mentions Python ({len(response_text)} chars)")
    return True


async def test_conversation_context():
    """Test: Agent maintains conversation context"""
    print("\n📋 Test: Conversation context")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    # First message
    response1 = await extract_response_text(
        root_agent,
        "Mam na imię Jan",
        session_service,
        session
    )

    is_valid, error_msg = validate_response_not_empty(response1)
    if not is_valid:
        print(f"❌ FAIL: First response - {error_msg}")
        return False

    # Second message - should remember name
    response2 = await extract_response_text(
        root_agent,
        "Jak mam na imię?",
        session_service,
        session
    )
    
    is_valid, error_msg = validate_response_not_empty(response2)
    if not is_valid:
        print(f"❌ FAIL: Second response - {error_msg}")
        return False
    
    if "jan" not in response2.lower():
        print(f"❌ FAIL: Agent didn't remember the name")
        print(f"   Response: {response2}")
        return False
    
    print(f"✅ PASS: Agent remembered context")
    return True


async def main():
    print_test_header("Hello World Agent", "01")
    
    tests = [
        ("Basic greeting", test_basic_greeting),
        ("Technical question", test_technical_question),
        ("Conversation context", test_conversation_context),
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

