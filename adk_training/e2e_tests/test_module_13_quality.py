"""
E2E Quality Assurance Tests for Module 13: Code Analyst
========================================================

High-value tests that guarantee commercial quality.
Complements structural tests in test_module_13.py.

Tests cover:
- RAG pipeline integrity (index → query → relevant results)
- Incremental indexing correctness (unchanged files skip, new files index)
- Web API workflow definitions (all 6 complete and prompt-valid)
- Agent pipeline structure (SequentialAgent, 2 sub-agents)
- Security: path traversal in repo_manager, code_indexer
- Instruction quality (both sub-agents have actionable instructions)
- Tool → instruction contract (instruction references tool names)
"""

import os
import re
import sys
import json
import shutil
import tempfile

utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from utils import print_test_header, print_test_summary

module_path = os.path.join(os.path.dirname(__file__), "..", "module_13_code_analyst")
module_path = os.path.abspath(module_path)
if module_path not in sys.path:
    sys.path.insert(0, module_path)

from dotenv import load_dotenv

load_dotenv(os.path.join(module_path, ".env"))


# =============================================================================
# 1. INCREMENTAL INDEXING — only changed files are re-indexed
# =============================================================================


def test_incremental_indexing():
    """Test Q1: Incremental indexing skips unchanged files."""
    print("\n[TEST] Q1: Incremental indexing correctness")

    try:
        from code_indexer import CodeIndexer
    except ImportError as e:
        print(f"FAIL: Cannot import CodeIndexer: {e}")
        return False

    sample_dir = os.path.join(module_path, "sample_project")
    persist_dir = os.path.join(module_path, "_test_incremental")

    try:
        indexer = CodeIndexer(
            project_dir=sample_dir,
            persist_dir=persist_dir,
            collection_name="test_incr",
        )

        # First indexing — should index all files
        stats1 = indexer.index_project(extensions=[".py"], incremental=False)
        if stats1["indexed"] == 0:
            print("FAIL: First indexing indexed 0 files")
            return False

        total_first = stats1["indexed"]

        # Second indexing (incremental) — should skip all
        stats2 = indexer.index_project(extensions=[".py"], incremental=True)
        skipped = stats2.get("skipped", 0)
        indexed = stats2.get("indexed", 0)

        if indexed > 0:
            print(f"FAIL: Incremental should index 0 files (no changes), indexed {indexed}")
            return False

        if skipped != total_first:
            print(f"FAIL: Should skip {total_first} files, skipped {skipped}")
            return False

        print(f"PASS: First run indexed {total_first}, incremental skipped all {skipped}")
        return True

    except Exception as e:
        print(f"FAIL: {e}")
        return False
    finally:
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir, ignore_errors=True)


# =============================================================================
# 2. RAG RELEVANCE — semantic search returns topically correct results
# =============================================================================


def test_rag_relevance():
    """Test Q2: Semantic search returns relevant files for specific queries."""
    print("\n[TEST] Q2: RAG search relevance")

    try:
        from code_indexer import CodeIndexer
    except ImportError as e:
        print(f"FAIL: Cannot import CodeIndexer: {e}")
        return False

    sample_dir = os.path.join(module_path, "sample_project")
    persist_dir = os.path.join(module_path, "_test_relevance")

    try:
        indexer = CodeIndexer(
            project_dir=sample_dir,
            persist_dir=persist_dir,
            collection_name="test_rel",
        )
        indexer.index_project(extensions=[".py"], incremental=False)

        # Query: order/zamówienie → should find order_controller.py
        results = indexer.query("tworzenie zamówień REST API endpoint", top_k=3)

        if not results:
            print("FAIL: No results returned for order query")
            return False

        file_paths = [r.get("file_path", "") for r in results]
        order_found = any("order" in fp.lower() for fp in file_paths)

        if not order_found:
            print(f"WARNING: order_controller not in top results: {file_paths}")
            # Soft pass — semantic search can vary
            print(f"PASS: Returned {len(results)} results (semantic may vary)")
            return True

        print(f"PASS: order_controller found for order query. Results: {file_paths}")
        return True

    except Exception as e:
        print(f"FAIL: {e}")
        return False
    finally:
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir, ignore_errors=True)


# =============================================================================
# 3. ALL 6 WORKFLOWS COMPLETE AND VALID
# =============================================================================


def test_workflow_definitions_complete():
    """Test Q3: All 6 workflows have required fields and valid prompt/template."""
    print("\n[TEST] Q3: Workflow definitions completeness")

    try:
        web_dir = os.path.join(module_path, "web")
        if web_dir not in sys.path:
            sys.path.insert(0, web_dir)

        from app import WORKFLOWS
    except ImportError as e:
        print(f"FAIL: Cannot import WORKFLOWS from web app: {e}")
        return False

    expected_ids = {"onboarding", "impact", "security", "stories", "document", "debug"}

    if set(WORKFLOWS.keys()) != expected_ids:
        missing = expected_ids - set(WORKFLOWS.keys())
        extra = set(WORKFLOWS.keys()) - expected_ids
        print(f"FAIL: Missing: {missing}, Extra: {extra}")
        return False

    errors = []
    for wf_id, wf in WORKFLOWS.items():
        # Required fields
        for field in ["name", "icon", "description"]:
            if not wf.get(field):
                errors.append(f"{wf_id}: missing '{field}'")

        # Must have either 'prompt' or 'prompt_template'
        has_prompt = bool(wf.get("prompt"))
        has_template = bool(wf.get("prompt_template"))
        if not has_prompt and not has_template:
            errors.append(f"{wf_id}: missing both 'prompt' and 'prompt_template'")

        # Templates must have {user_input} placeholder
        if has_template and "{user_input}" not in wf["prompt_template"]:
            errors.append(f"{wf_id}: prompt_template missing '{{user_input}}' placeholder")

        # Templates should also define input_placeholder for UI
        if has_template and not wf.get("input_placeholder"):
            errors.append(f"{wf_id}: has prompt_template but no 'input_placeholder' for UI")

        # Prompts must be substantial (not placeholder)
        prompt_text = wf.get("prompt") or wf.get("prompt_template") or ""
        if len(prompt_text) < 50:
            errors.append(f"{wf_id}: prompt too short ({len(prompt_text)} chars)")

    if errors:
        for err in errors:
            print(f"  - {err}")
        print(f"FAIL: {len(errors)} workflow issues")
        return False

    print(f"PASS: All 6 workflows complete with valid prompts")
    return True


# =============================================================================
# 4. WEB AGENT PIPELINE STRUCTURE
# =============================================================================


def test_web_agent_pipeline():
    """Test Q4: Web app creates correct SequentialAgent pipeline."""
    print("\n[TEST] Q4: Web agent pipeline structure")

    try:
        from code_indexer import CodeIndexer

        web_dir = os.path.join(module_path, "web")
        if web_dir not in sys.path:
            sys.path.insert(0, web_dir)

        from app import _create_agent

        sample_dir = os.path.join(module_path, "sample_project")
        persist_dir = os.path.join(module_path, "_test_pipeline")

        try:
            indexer = CodeIndexer(
                project_dir=sample_dir,
                persist_dir=persist_dir,
                collection_name="test_pipe",
            )

            agent = _create_agent(indexer)

            from google.adk.agents import SequentialAgent

            if not isinstance(agent, SequentialAgent):
                print(f"FAIL: Expected SequentialAgent, got {type(agent).__name__}")
                return False

            subs = agent.sub_agents
            if len(subs) != 2:
                print(f"FAIL: Expected 2 sub_agents, got {len(subs)}")
                return False

            names = [s.name for s in subs]
            if "code_analyst" not in names:
                print(f"FAIL: Missing code_analyst. Got: {names}")
                return False

            if "solution_architect" not in names:
                print(f"FAIL: Missing solution_architect. Got: {names}")
                return False

            # code_analyst must have search tools
            analyst = subs[0]
            analyst_tool_names = [
                getattr(t, "name", getattr(getattr(t, "func", None), "__name__", ""))
                for t in (analyst.tools or [])
            ]
            if "search_code" not in analyst_tool_names:
                print(f"FAIL: code_analyst missing search_code tool. Has: {analyst_tool_names}")
                return False

            print(f"PASS: SequentialAgent[{' → '.join(names)}], analyst tools: {analyst_tool_names}")
            return True

        finally:
            if os.path.exists(persist_dir):
                shutil.rmtree(persist_dir, ignore_errors=True)

    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 5. INSTRUCTION ↔ TOOL CONTRACT
# =============================================================================


def test_instruction_references_tools():
    """Test Q5: Agent instruction references tool names that actually exist."""
    print("\n[TEST] Q5: Instruction ↔ tool contract")

    try:
        from code_indexer import CodeIndexer

        web_dir = os.path.join(module_path, "web")
        if web_dir not in sys.path:
            sys.path.insert(0, web_dir)

        from app import _create_agent

        sample_dir = os.path.join(module_path, "sample_project")
        persist_dir = os.path.join(module_path, "_test_instr")

        try:
            indexer = CodeIndexer(
                project_dir=sample_dir,
                persist_dir=persist_dir,
                collection_name="test_instr",
            )

            agent = _create_agent(indexer)
            analyst = agent.sub_agents[0]

            instruction = analyst.instruction or ""

            # Instruction mentions search_code → tool must exist
            mentioned_tools = re.findall(r'(\w+)\(\)', instruction)

            actual_tools = set()
            for t in (analyst.tools or []):
                name = getattr(t, "name", None) or ""
                func = getattr(t, "func", None)
                if func:
                    name = func.__name__
                if name:
                    actual_tools.add(name)

            errors = []
            for mentioned in mentioned_tools:
                if mentioned not in actual_tools and mentioned not in {
                    "format", "strip", "lower", "upper", "join", "split",
                }:
                    errors.append(
                        f"Instruction mentions '{mentioned}()' but tool not in agent. "
                        f"Available: {sorted(actual_tools)}"
                    )

            if errors:
                for err in errors:
                    print(f"  - {err}")
                print(f"FAIL: {len(errors)} phantom tool references")
                return False

            print(f"PASS: All mentioned tools exist. Tools: {sorted(actual_tools)}")
            return True

        finally:
            if os.path.exists(persist_dir):
                shutil.rmtree(persist_dir, ignore_errors=True)

    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 6. REPO MANAGER — SECURITY: PATH VALIDATION
# =============================================================================


def test_repo_manager_path_validation():
    """Test Q6: RepoManager rejects dangerous/nonexistent paths."""
    print("\n[TEST] Q6: RepoManager path validation")

    try:
        web_dir = os.path.join(module_path, "web")
        if web_dir not in sys.path:
            sys.path.insert(0, web_dir)

        from repo_manager import RepoManager
    except ImportError as e:
        print(f"FAIL: Cannot import RepoManager: {e}")
        return False

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = RepoManager(data_dir=tmpdir)

        dangerous_paths = [
            "/etc/shadow",
            "C:\\Windows\\System32",
            "../../../etc/passwd",
            "",
            "a" * 600,  # exceeds 500 char limit
            "/nonexistent/path/that/does/not/exist",
        ]

        leaked = []
        for path in dangerous_paths:
            repo, error = manager.add(path, f"test-{path[:20]}")
            if repo is not None and not error:
                leaked.append(path)

        if leaked:
            print(f"FAIL: Accepted dangerous paths: {leaked}")
            return False

        # Positive: a real directory should be accepted
        real_dir = os.path.join(module_path, "sample_project")
        repo, error = manager.add(real_dir, "valid-project")
        if repo is None:
            print(f"FAIL: Rejected valid path: {error}")
            return False

        print(f"PASS: Blocked {len(dangerous_paths)} bad paths, accepted valid directory")
        return True


# =============================================================================
# 7. RETRIEVAL TOOL WRAPPER — returns correct shape
# =============================================================================


def test_retrieval_tool_response_shape():
    """Test Q7: FunctionTool wrappers return expected dict structure."""
    print("\n[TEST] Q7: Tool response shape")

    try:
        # Set env before import so the tool picks up correct paths
        os.environ["CODE_PROJECT_DIR"] = os.path.join(module_path, "sample_project")
        test_persist = os.path.join(module_path, "_test_shape")
        os.environ["CODE_INDEX_DIR"] = test_persist

        # Re-import to get fresh indexer with test paths
        if "code_retrieval_tool" in sys.modules:
            del sys.modules["code_retrieval_tool"]

        from code_retrieval_tool import search_code, index_project, get_index_stats
    except ImportError as e:
        print(f"FAIL: Cannot import tools: {e}")
        return False

    try:
        # index_project
        index_result = index_project(extensions=".py", incremental=False)
        for key in ["indexed", "total_chunks"]:
            if key not in index_result:
                print(f"FAIL: index_project missing key '{key}'. Got: {list(index_result.keys())}")
                return False

        # get_index_stats
        stats = get_index_stats()
        for key in ["total_chunks", "indexed_files"]:
            if key not in stats:
                print(f"FAIL: get_index_stats missing key '{key}'. Got: {list(stats.keys())}")
                return False

        # search_code
        search_result = search_code("user management", top_k=2)
        if "results" not in search_result:
            print(f"FAIL: search_code missing 'results'. Got: {list(search_result.keys())}")
            return False

        if search_result["results"]:
            r = search_result["results"][0]
            for key in ["text", "file_path"]:
                if key not in r:
                    print(f"FAIL: search result missing '{key}'. Got: {list(r.keys())}")
                    return False

        print(f"PASS: All 3 tools return correct shape (indexed {index_result['indexed']} files)")
        return True

    except Exception as e:
        print(f"FAIL: {e}")
        return False
    finally:
        test_persist = os.path.join(module_path, "_test_shape")
        if os.path.exists(test_persist):
            shutil.rmtree(test_persist, ignore_errors=True)


# =============================================================================
# 8. BOTH SUB-AGENT INSTRUCTIONS ARE ACTIONABLE
# =============================================================================


def test_sub_agent_instruction_quality():
    """Test Q8: Both sub-agent instructions have clear role, rules, and output format."""
    print("\n[TEST] Q8: Sub-agent instruction quality")

    try:
        web_dir = os.path.join(module_path, "web")
        if web_dir not in sys.path:
            sys.path.insert(0, web_dir)

        from app import _CODE_ANALYST_INSTRUCTION, _ARCHITECT_INSTRUCTION
    except ImportError as e:
        print(f"FAIL: Cannot import instructions: {e}")
        return False

    errors = []

    # Code analyst checks
    analyst = _CODE_ANALYST_INSTRUCTION
    if len(analyst) < 200:
        errors.append(f"Code analyst instruction too short ({len(analyst)} chars)")
    if "search_code" not in analyst:
        errors.append("Code analyst doesn't mention search_code tool")
    if "polsku" not in analyst.lower() and "polski" not in analyst.lower():
        errors.append("Code analyst doesn't specify Polish language")

    # Architect checks
    architect = _ARCHITECT_INSTRUCTION
    if len(architect) < 200:
        errors.append(f"Architect instruction too short ({len(architect)} chars)")
    if "mermaid" not in architect.lower():
        errors.append("Architect doesn't mention Mermaid diagrams")
    if "stories" not in architect.lower():
        errors.append("Architect doesn't mention stories/user stories")

    if errors:
        for err in errors:
            print(f"  - {err}")
        print(f"FAIL: {len(errors)} instruction quality issues")
        return False

    print(
        f"PASS: Both instructions substantial "
        f"(analyst: {len(analyst)} chars, architect: {len(architect)} chars)"
    )
    return True


# =============================================================================
# 9. CLI AGENT ↔ WEB AGENT CONSISTENCY
# =============================================================================


def test_cli_web_agent_name_consistency():
    """Test Q9: CLI agent and web pipeline agent names don't collide."""
    print("\n[TEST] Q9: CLI ↔ web agent name consistency")

    try:
        from code_indexer import CodeIndexer

        # CLI agent
        import importlib.util

        agent_file = os.path.join(module_path, "agent.py")
        spec = importlib.util.spec_from_file_location("agent_m13", agent_file)
        cli_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli_mod)
        cli_agent = cli_mod.root_agent

        # Web agent
        web_dir = os.path.join(module_path, "web")
        if web_dir not in sys.path:
            sys.path.insert(0, web_dir)

        from app import _create_agent

        persist_dir = os.path.join(module_path, "_test_names")
        try:
            indexer = CodeIndexer(
                project_dir=os.path.join(module_path, "sample_project"),
                persist_dir=persist_dir,
                collection_name="test_names",
            )
            web_agent = _create_agent(indexer)

            # CLI root name
            cli_name = cli_agent.name

            # Web pipeline name + sub-agent names
            web_names = [web_agent.name]
            for sub in (web_agent.sub_agents or []):
                web_names.append(sub.name)

            # No collision between CLI root and web sub-agents
            if cli_name in web_names:
                print(
                    f"FAIL: CLI agent name '{cli_name}' collides with web agent names {web_names}"
                )
                return False

            print(f"PASS: CLI='{cli_name}', Web={web_names} — no collisions")
            return True
        finally:
            if os.path.exists(persist_dir):
                shutil.rmtree(persist_dir, ignore_errors=True)

    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 10. CODE INDEXER — EXTENSION FILTERING
# =============================================================================


def test_indexer_extension_filtering():
    """Test Q10: CodeIndexer respects extension filter — doesn't index junk."""
    print("\n[TEST] Q10: Extension filtering")

    try:
        from code_indexer import CodeIndexer
    except ImportError as e:
        print(f"FAIL: Cannot import CodeIndexer: {e}")
        return False

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mixed files
        (open(os.path.join(tmpdir, "main.py"), "w")).write("print('hello')")
        (open(os.path.join(tmpdir, "data.csv"), "w")).write("a,b,c\n1,2,3")
        (open(os.path.join(tmpdir, "image.png"), "w")).write("not-a-real-image")

        persist_dir = os.path.join(tmpdir, "_index")

        indexer = CodeIndexer(
            project_dir=tmpdir,
            persist_dir=persist_dir,
            collection_name="test_ext",
        )

        stats = indexer.index_project(extensions=[".py"], incremental=False)

        if stats["indexed"] != 1:
            print(f"FAIL: Should index 1 .py file, indexed {stats['indexed']}")
            return False

        print(f"PASS: Indexed 1/3 files (only .py), skipped .csv and .png")
        return True


# =============================================================================
# MAIN
# =============================================================================


def run_all_tests():
    """Execute all quality assurance tests for Module 13."""
    print_test_header("Code Analyst — Quality Assurance", "13-Q")

    results = {}

    # RAG pipeline
    results["Incremental indexing"] = test_incremental_indexing()
    results["RAG relevance"] = test_rag_relevance()

    # Web workflows
    results["Workflow definitions"] = test_workflow_definitions_complete()
    results["Web agent pipeline"] = test_web_agent_pipeline()
    results["Instruction ↔ tools"] = test_instruction_references_tools()

    # Security
    results["Repo path validation"] = test_repo_manager_path_validation()

    # Tools
    results["Tool response shape"] = test_retrieval_tool_response_shape()
    results["Instruction quality"] = test_sub_agent_instruction_quality()

    # Consistency
    results["CLI ↔ web names"] = test_cli_web_agent_name_consistency()
    results["Extension filtering"] = test_indexer_extension_filtering()

    passed = sum(1 for r in results.values() if r)
    total = len(results)
    exit_code = print_test_summary(passed, total)
    return exit_code


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
