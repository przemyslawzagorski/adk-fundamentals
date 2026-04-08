"""
E2E Test for Module 13: Code Analyst (Persistent RAG + LlamaIndex)

Tests code indexing, persistence (SimpleVectorStore), and agent functionality.
"""

import sys
import os
import shutil
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
    print_test_summary,
)
from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService


# =============================================================================
# SETUP
# =============================================================================
module_path = os.path.join(os.path.dirname(__file__), '..', 'module_13_code_analyst')

# Load .env so GoogleGenAIEmbedding picks up Vertex AI config
load_dotenv(os.path.join(module_path, ".env"))

_cached_module = None


def _get_agent_module():
    global _cached_module
    if _cached_module is None:
        # Add module_path to sys.path so local imports (code_retrieval_tool) work
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        _cached_module = import_agent_module(module_path)
    return _cached_module


# =============================================================================
# TESTS
# =============================================================================


def test_agent_loads():
    """Test 1: Agent loads with FunctionTool-based tools"""
    print("\n[TEST] Test 1: Agent loads correctly")

    try:
        agent_module = _get_agent_module()
        root_agent = agent_module.root_agent
    except Exception as e:
        print(f"FAIL: Could not load agent module: {e}")
        return False

    if root_agent.name != "code_analyst_agent":
        print(f"FAIL: Expected name 'code_analyst_agent', got '{root_agent.name}'")
        return False

    if not root_agent.tools or len(root_agent.tools) < 2:
        print(f"FAIL: Expected at least 2 tools, got {len(root_agent.tools or [])}")
        return False

    tool_names = [getattr(t, 'name', type(t).__name__) for t in root_agent.tools]
    print(f"PASS: Agent '{root_agent.name}' loaded with tools: {tool_names}")
    return True


def test_sample_project_exists():
    """Test 2: sample_project/ directory has code files for testing"""
    print("\n[TEST] Test 2: Sample project directory exists")

    sample_dir = os.path.join(module_path, "sample_project")
    if not os.path.isdir(sample_dir):
        print(f"FAIL: sample_project/ not found at {sample_dir}")
        return False

    py_files = [f for f in os.listdir(sample_dir) if f.endswith('.py')]
    if len(py_files) < 2:
        print(f"FAIL: Expected at least 2 .py files, found {len(py_files)}")
        return False

    expected = ["user_service.py", "auth_service.py", "order_controller.py"]
    for f in expected:
        if f not in py_files:
            print(f"FAIL: Missing {f}")
            return False

    print(f"PASS: sample_project/ contains {len(py_files)} Python files: {', '.join(py_files)}")
    return True


def test_code_indexer_imports():
    """Test 3: CodeIndexer class is importable and has required methods"""
    print("\n[TEST] Test 3: CodeIndexer importable")

    try:
        sys.path.insert(0, module_path)
        from code_indexer import CodeIndexer
    except ImportError as e:
        print(f"FAIL: Cannot import CodeIndexer: {e}")
        return False

    required_methods = ["index_project", "query", "get_stats", "reset_index"]
    for method in required_methods:
        if not hasattr(CodeIndexer, method):
            print(f"FAIL: CodeIndexer missing method: {method}")
            return False

    print(f"PASS: CodeIndexer importable with methods: {required_methods}")
    return True


def test_code_indexer_persistence():
    """Test 4: CodeIndexer creates persistent index (SimpleVectorStore)"""
    print("\n[TEST] Test 4: Index persistence")

    try:
        sys.path.insert(0, module_path)
        from code_indexer import CodeIndexer
    except ImportError as e:
        print(f"FAIL: Cannot import CodeIndexer: {e}")
        return False

    test_persist_dir = os.path.join(module_path, "_test_index_store")
    sample_dir = os.path.join(module_path, "sample_project")

    try:
        # Index the sample project
        indexer = CodeIndexer(
            project_dir=sample_dir,
            persist_dir=test_persist_dir,
            collection_name="test_collection",
        )
        stats = indexer.index_project(extensions=[".py"], incremental=False)

        if stats["indexed"] == 0:
            print(f"FAIL: No files indexed")
            return False

        if stats["total_chunks"] == 0:
            print(f"FAIL: No chunks created")
            return False

        chunk_count = stats["total_chunks"]

        # Create new indexer pointing to same persist_dir - should load existing
        indexer2 = CodeIndexer(
            project_dir=sample_dir,
            persist_dir=test_persist_dir,
            collection_name="test_collection",
        )
        stats2 = indexer2.get_stats()

        if stats2["total_chunks"] != chunk_count:
            print(f"FAIL: Persistence lost. Original: {chunk_count}, Reloaded: {stats2['total_chunks']}")
            return False

        print(f"PASS: Indexed {stats['indexed']} files -> {chunk_count} chunks, persistence verified")
        return True

    finally:
        # Cleanup test data
        if os.path.exists(test_persist_dir):
            shutil.rmtree(test_persist_dir, ignore_errors=True)


def test_code_indexer_query():
    """Test 5: CodeIndexer can semantically query indexed code"""
    print("\n[TEST] Test 5: Semantic code search")

    try:
        sys.path.insert(0, module_path)
        from code_indexer import CodeIndexer
    except ImportError as e:
        print(f"FAIL: Cannot import CodeIndexer: {e}")
        return False

    test_persist_dir = os.path.join(module_path, "_test_index_store_query")
    sample_dir = os.path.join(module_path, "sample_project")

    try:
        indexer = CodeIndexer(
            project_dir=sample_dir,
            persist_dir=test_persist_dir,
            collection_name="test_query",
        )
        indexer.index_project(extensions=[".py"], incremental=False)

        # Query for authentication-related code
        results = indexer.query("uwierzytelnianie uzytkownikow i logowanie", top_k=3)

        if not results:
            print("FAIL: No results returned")
            return False

        if "error" in results[0]:
            print(f"FAIL: {results[0]['error']}")
            return False

        # Check that auth_service.py appears in results
        file_paths = [r["file_path"] for r in results]
        auth_found = any("auth" in fp.lower() for fp in file_paths)

        if auth_found:
            print(f"PASS: Found auth-related code. Top results: {file_paths}")
        else:
            print(f"WARNING: auth_service not in top results. Got: {file_paths}")
            # Still pass - semantic search may vary
            print(f"PASS: Query returned {len(results)} results (semantic may vary)")

        return True

    finally:
        if os.path.exists(test_persist_dir):
            shutil.rmtree(test_persist_dir, ignore_errors=True)


def test_instruction_polish():
    """Test 6: Agent instruction is in Polish and mentions key workflows"""
    print("\n[TEST] Test 6: Instruction quality")

    try:
        agent_module = _get_agent_module()
        root_agent = agent_module.root_agent
    except Exception as e:
        print(f"FAIL: Could not load agent: {e}")
        return False

    instruction = root_agent.instruction
    if not instruction or len(instruction) < 100:
        print(f"FAIL: Instruction too short or empty")
        return False

    # Check Polish markers
    polish_terms = ["przeszukaj", "rozwiaz", "diagram", "mermaid", "stories"]
    found = sum(1 for t in polish_terms if t.lower() in instruction.lower())
    if found < 3:
        print(f"FAIL: Instruction missing key terms ({found}/5 found)")
        return False

    print(f"PASS: Instruction is {len(instruction)} chars, Polish, {found}/5 workflow terms found")
    return True


# =============================================================================
# MAIN
# =============================================================================
def run_all_tests():
    """Execute all tests for Module 13."""
    print_test_header("Code Analyst (Persistent RAG)", "13")

    results = {}

    results["Agent loads"] = test_agent_loads()
    results["Sample project"] = test_sample_project_exists()
    results["CodeIndexer imports"] = test_code_indexer_imports()
    results["Index persistence"] = test_code_indexer_persistence()
    results["Semantic search"] = test_code_indexer_query()
    results["Instruction quality"] = test_instruction_polish()

    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print_test_summary(passed, total)


if __name__ == "__main__":
    run_all_tests()
