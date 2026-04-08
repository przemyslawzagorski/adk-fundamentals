"""
E2E Test for Module 15: Gmail Integration

Tests:
- Agent loads correctly with tool_filter
- tool_filter reduces tools from ~80 to expected subset
- Agent responds to basic queries (no OAuth required for structural tests)
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
    print_test_summary,
)
from google.adk.sessions import InMemorySessionService

# Import agent module dynamically
module_path = os.path.join(os.path.dirname(__file__), '..', 'module_15_gmail_integration')
agent_module = import_agent_module(module_path)
root_agent = agent_module.root_agent


# =========================================================================
# Structural tests (no OAuth needed)
# =========================================================================

async def test_agent_loads():
    """Test: Agent module loads without errors"""
    print("\n📋 Test: Agent loads correctly")

    if root_agent is None:
        print("❌ FAIL: root_agent is None")
        return False

    if root_agent.name != "gmail_assistant":
        print(f"❌ FAIL: Expected name 'gmail_assistant', got '{root_agent.name}'")
        return False

    print(f"✅ PASS: Agent '{root_agent.name}' loaded")
    return True


async def test_tool_filter_limits_tools():
    """Test: tool_filter limits Gmail tools to expected subset"""
    print("\n📋 Test: tool_filter limits number of tools")

    expected_tools = set(agent_module.GMAIL_TOOLS)
    gmail_toolset = agent_module.gmail_toolset

    tools = await gmail_toolset.get_tools()
    tool_names = {t.name for t in tools}

    print(f"   Expected tools: {expected_tools}")
    print(f"   Got tools:      {tool_names}")
    print(f"   Tool count:     {len(tool_names)}")

    if tool_names != expected_tools:
        missing = expected_tools - tool_names
        extra = tool_names - expected_tools
        if missing:
            print(f"❌ FAIL: Missing tools: {missing}")
        if extra:
            print(f"❌ FAIL: Unexpected extra tools: {extra}")
        return False

    if len(tool_names) > 10:
        print(f"❌ FAIL: Too many tools ({len(tool_names)}), filter not working")
        return False

    print(f"✅ PASS: Exactly {len(tool_names)} tools (was ~80 without filter)")
    return True


async def test_instruction_no_pirate():
    """Test: Instruction doesn't contain pirate-speak"""
    print("\n📋 Test: Instruction is professional (no pirate theme)")

    instruction = agent_module.INSTRUCTION.lower()

    pirate_keywords = ["ahoy", "ye be", "ship's messenger", "treasure", "pirate", "bottle"]
    found = [kw for kw in pirate_keywords if kw in instruction]

    if found:
        print(f"❌ FAIL: Pirate keywords found in instruction: {found}")
        return False

    # Should contain Polish professional content
    polish_keywords = ["gmail", "email", "zasady"]
    has_polish = any(kw in instruction for kw in polish_keywords)
    if not has_polish:
        print(f"⚠️  WARNING: Instruction might not be in Polish")

    print("✅ PASS: Instruction is professional, no pirate theme")
    return True


async def test_credentials_configured():
    """Test: OAuth credentials are loaded from .env"""
    print("\n📋 Test: OAuth credentials configured")

    client_id = agent_module.GOOGLE_CLIENT_ID
    client_secret = agent_module.GOOGLE_CLIENT_SECRET

    if not client_id:
        print("❌ FAIL: GOOGLE_CLIENT_ID not set")
        return False

    if not client_secret:
        print("❌ FAIL: GOOGLE_CLIENT_SECRET not set")
        return False

    if not client_id.endswith(".apps.googleusercontent.com"):
        print(f"⚠️  WARNING: Client ID doesn't look like Google OAuth ID: {client_id[:20]}...")

    print(f"✅ PASS: Credentials configured (ID: {client_id[:15]}...)")
    return True


async def test_agent_basic_response():
    """Test: Agent responds to a general question (no Gmail API call needed)"""
    print("\n📋 Test: Agent responds to basic question")

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )

    try:
        response_text = await asyncio.wait_for(
            extract_response_text(
                root_agent,
                "Jakie operacje na emailach potrafisz wykonać? Odpowiedz krótko.",
                session_service,
                session,
            ),
            timeout=30,
        )
    except asyncio.TimeoutError:
        print("❌ FAIL: Agent response timed out (30s)")
        return False

    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False

    print(f"✅ PASS: Got response ({len(response_text)} chars)")
    print(f"   Preview: {response_text[:150]}...")
    return True


# =========================================================================
# Main
# =========================================================================

async def main():
    print_test_header("Gmail Integration", "15")

    tests = [
        ("Agent loads", test_agent_loads),
        ("Tool filter limits tools", test_tool_filter_limits_tools),
        ("No pirate instruction", test_instruction_no_pirate),
        ("Credentials configured", test_credentials_configured),
        ("Basic agent response", test_agent_basic_response),
    ]

    passed = 0
    total = len(tests)

    for name, test_fn in tests:
        try:
            result = await test_fn()
            if result:
                passed += 1
        except Exception as e:
            print(f"\n❌ EXCEPTION in '{name}': {e}")

    exit_code = print_test_summary(passed, total)
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
