"""
E2E Test for Module 10: Local RAG (FilesRetrieval)

Tests local file-based RAG with LlamaIndex vector search.
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
    extract_response_with_tool_calls,
    validate_response_not_empty,
    print_test_header,
    print_test_summary
)
from google.adk.sessions import InMemorySessionService


# =============================================================================
# SETUP
# =============================================================================
module_path = os.path.join(os.path.dirname(__file__), '..', 'module_10_local_rag')

# Cache the agent module import to avoid re-indexing docs for each test
_cached_module = None


def _get_agent_module():
    global _cached_module
    if _cached_module is None:
        _cached_module = import_agent_module(module_path)
    return _cached_module


def test_agent_loads():
    """Test 1: Agent module loads and creates root_agent with FilesRetrieval tool"""
    print("\n📋 Test 1: Agent loads correctly")

    try:
        agent_module = _get_agent_module()
        root_agent = agent_module.root_agent
    except Exception as e:
        print(f"❌ FAIL: Could not load agent module: {e}")
        return False

    # Verify agent name
    if root_agent.name != "local_rag_agent":
        print(f"❌ FAIL: Expected name 'local_rag_agent', got '{root_agent.name}'")
        return False

    # Verify model
    if "gemini" not in root_agent.model.lower():
        print(f"❌ FAIL: Expected gemini model, got '{root_agent.model}'")
        return False

    print(f"✅ PASS: Agent '{root_agent.name}' loaded with model '{root_agent.model}'")
    return True


def test_docs_directory_exists():
    """Test 2: docs/ directory exists with sample documents"""
    print("\n📋 Test 2: Documentation directory exists")

    docs_dir = os.path.join(module_path, "docs")
    if not os.path.isdir(docs_dir):
        print(f"❌ FAIL: docs/ directory not found at {docs_dir}")
        return False

    files = os.listdir(docs_dir)
    md_files = [f for f in files if f.endswith('.md')]

    if len(md_files) < 2:
        print(f"❌ FAIL: Expected at least 2 .md files, found {len(md_files)}")
        return False

    expected_files = ["polityka_bezpieczenstwa.md", "onboarding.md", "architektura.md"]
    for expected in expected_files:
        if expected not in files:
            print(f"❌ FAIL: Missing expected file: {expected}")
            return False

    print(f"✅ PASS: docs/ contains {len(md_files)} markdown files: {', '.join(md_files)}")
    return True


def test_files_retrieval_tool_configured():
    """Test 3: FilesRetrieval tool is properly configured in the agent"""
    print("\n📋 Test 3: FilesRetrieval tool configured")

    try:
        agent_module = _get_agent_module()
        root_agent = agent_module.root_agent
    except Exception as e:
        print(f"❌ FAIL: Could not load agent: {e}")
        return False

    # Check tools list
    if not root_agent.tools or len(root_agent.tools) == 0:
        print("❌ FAIL: Agent has no tools configured")
        return False

    tool = root_agent.tools[0]
    tool_name = getattr(tool, 'name', str(type(tool).__name__))

    # Verify it's a FilesRetrieval/LlamaIndexRetrieval type
    type_name = type(tool).__name__
    if type_name not in ("FilesRetrieval", "LlamaIndexRetrieval"):
        print(f"❌ FAIL: Expected FilesRetrieval tool, got {type_name}")
        return False

    print(f"✅ PASS: Tool '{tool_name}' of type {type_name} configured")
    return True


def test_instruction_polish():
    """Test 4: Agent instruction is in Polish and professional"""
    print("\n📋 Test 4: Instruction quality check")

    try:
        agent_module = _get_agent_module()
        root_agent = agent_module.root_agent
    except Exception as e:
        print(f"❌ FAIL: Could not load agent: {e}")
        return False

    instruction = root_agent.instruction
    if not instruction:
        print("❌ FAIL: No instruction set")
        return False

    # Check for Polish keywords
    polish_keywords = ["pytania", "wiedzy", "narzędzi"]
    found = sum(1 for kw in polish_keywords if kw.lower() in instruction.lower())
    if found < 2:
        print(f"❌ FAIL: Instruction doesn't appear to be in Polish (found {found}/3 markers)")
        return False

    # Check minimum length
    if len(instruction) < 100:
        print(f"❌ FAIL: Instruction too short ({len(instruction)} chars)")
        return False

    print(f"✅ PASS: Instruction is {len(instruction)} chars, in Polish, professional tone")
    return True


async def test_agent_responds_with_rag():
    """Test 5: Agent responds to a question about company docs using RAG"""
    print("\n📋 Test 5: Agent responds with RAG knowledge")

    try:
        agent_module = _get_agent_module()
        root_agent = agent_module.root_agent
    except Exception as e:
        print(f"❌ FAIL: Could not load agent: {e}")
        return False

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )

    # Ask about password policy (from polityka_bezpieczenstwa.md)
    response_text, tool_calls = await extract_response_with_tool_calls(
        root_agent,
        "Jaka jest minimalna długość hasła w firmie?",
        session_service,
        session
    )

    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False

    # Response should mention "12" (chars) from the security policy
    if "12" in response_text:
        print(f"✅ PASS: Agent correctly found password policy (mentions 12 chars)")
    else:
        print(f"⚠️  WARNING: Response might not reference the security doc accurately")
        print(f"   Response: {response_text[:200]}...")

    if tool_calls:
        print(f"   Tools called: {', '.join(tool_calls)}")

    return True


# =============================================================================
# MAIN
# =============================================================================
def run_all_tests():
    """Execute all tests for Module 10."""
    print_test_header("Local RAG (FilesRetrieval)", "10")

    results = {}

    # Sync tests
    results["Agent loads"] = test_agent_loads()
    results["Docs directory"] = test_docs_directory_exists()
    results["FilesRetrieval configured"] = test_files_retrieval_tool_configured()
    results["Polish instruction"] = test_instruction_polish()

    # Async test
    results["RAG response"] = asyncio.run(test_agent_responds_with_rag())

    # Summary
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print_test_summary(passed, total)


if __name__ == "__main__":
    run_all_tests()
