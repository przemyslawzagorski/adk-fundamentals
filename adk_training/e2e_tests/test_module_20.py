"""
E2E Tests for Module 20: Analyst System

Tests cover:
- Module loading and agent structure
- Contract/Pydantic validation
- Tool functions (file, template, skill, MCP)
- Orchestrator wiring (agent count, output_keys, tool assignment)
- Skill files (frontmatter, spec compliance)
- Template files (placeholders, structure)
- Root agent routing (AgentTool wrapping)
"""

import sys
import os
import json
import tempfile
import shutil

utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from utils import (
    print_test_header,
    print_test_summary,
)

module_path = os.path.join(os.path.dirname(__file__), "..", "module_20_analyst_system")
if module_path not in sys.path:
    sys.path.insert(0, module_path)

from dotenv import load_dotenv

load_dotenv(os.path.join(module_path, ".env"), override=False)

# Ensure SKILLS_DIR is set so skill tools find the correct directory
if "SKILLS_DIR" not in os.environ:
    os.environ["SKILLS_DIR"] = os.path.join(module_path, "skills")


# =============================================================================
# 1. MODULE LOADING
# =============================================================================


def test_root_agent_loads():
    """Test 1: Root agent loads and is an LlmAgent with 6 AgentTools."""
    print("\n[TEST] Test 1: Root agent loads correctly")
    try:
        from google.adk.agents import LlmAgent
        from google.adk.tools import AgentTool

        spec = _import_agent()
        root = spec.root_agent

        if not isinstance(root, LlmAgent):
            print(f"FAIL: root_agent is {type(root).__name__}, expected LlmAgent")
            return False

        if root.name != "analyst_captain":
            print(f"FAIL: Expected name 'analyst_captain', got '{root.name}'")
            return False

        agent_tools = [t for t in root.tools if isinstance(t, AgentTool)]
        if len(agent_tools) != 6:
            print(f"FAIL: Expected 6 AgentTools, got {len(agent_tools)}")
            return False

        names = sorted([t.agent.name for t in agent_tools])
        expected = sorted([
            "analyze_requirement",
            "create_epic",
            "generate_document",
            "generate_skill",
            "generate_test_plan",
            "review_document",
        ])
        if names != expected:
            print(f"FAIL: Orchestrator names mismatch: {names} != {expected}")
            return False

        print(f"PASS: root_agent '{root.name}' loaded with 6 orchestrators: {names}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 2. CONTRACT / PYDANTIC
# =============================================================================


def test_contract_model_validates():
    """Test 2: ProjectKnowledgeContract validates sample_contract.json."""
    print("\n[TEST] Test 2: Contract model validates sample data")
    try:
        from contract.project_knowledge import ProjectKnowledgeContract

        sample_path = os.path.join(module_path, "contract", "sample_contract.json")
        with open(sample_path, encoding="utf-8") as f:
            data = json.load(f)

        contract = ProjectKnowledgeContract(**data)
        if contract.project_name != "IoT Connect":
            print(f"FAIL: project_name mismatch: {contract.project_name}")
            return False
        if not contract.domain.bounded_contexts:
            print("FAIL: No bounded_contexts in sample contract")
            return False

        print(f"PASS: Contract validated — project='{contract.project_name}', "
              f"contexts={len(contract.domain.bounded_contexts)}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_contract_rejects_invalid():
    """Test 3: Contract model rejects invalid data."""
    print("\n[TEST] Test 3: Contract rejects invalid data")
    try:
        from contract.project_knowledge import ProjectKnowledgeContract

        try:
            ProjectKnowledgeContract(**{})
            print("FAIL: Should have rejected empty dict")
            return False
        except Exception:
            pass

        try:
            ProjectKnowledgeContract(project_name="X")
            print("FAIL: Should have rejected missing domain")
            return False
        except Exception:
            pass

        print("PASS: Contract correctly rejects invalid data")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 3. TOOL FUNCTIONS
# =============================================================================


def test_file_tools():
    """Test 4: file_tools read/write/list work correctly."""
    print("\n[TEST] Test 4: File tools work")
    try:
        from tools.file_tools import read_file, write_document, list_files

        # read_file — existing file
        result = read_file(os.path.join(module_path, "README.md"))
        if result["status"] != "ok":
            print(f"FAIL: read_file failed: {result.get('error_message')}")
            return False
        if "Analyst" not in result["content"]:
            print("FAIL: README.md content doesn't contain 'Analyst'")
            return False

        # read_file — non-existent
        result = read_file("/nonexistent/file.txt")
        if result["status"] != "error":
            print("FAIL: read_file should fail for non-existent file")
            return False

        # write_document + list_files
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["OUTPUT_DIR"] = tmpdir
            result = write_document("test-doc.md", "# Test", "sub")
            if result["status"] != "ok":
                print(f"FAIL: write_document failed: {result.get('error_message')}")
                return False

            result = list_files(os.path.join(tmpdir, "sub"), "*.md")
            if result["status"] != "ok" or len(result["files"]) != 1:
                print(f"FAIL: list_files returned {result}")
                return False

        print("PASS: file_tools (read, write, list) all work correctly")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_template_tools():
    """Test 5: template_tools list/load templates."""
    print("\n[TEST] Test 5: Template tools work")
    try:
        from tools.template_tools import list_templates, load_template

        result = list_templates()
        if result["status"] != "ok":
            print(f"FAIL: list_templates failed: {result.get('error_message')}")
            return False

        templates = result["templates"]
        expected_names = {"hld_template", "lld_template", "epic_template", "test_plan_template"}
        found = {t["name"] for t in templates}
        if not expected_names.issubset(found):
            print(f"FAIL: Missing templates. Expected {expected_names}, got {found}")
            return False

        # Load one
        result = load_template("hld_template")
        if result["status"] != "ok":
            print(f"FAIL: load_template failed: {result.get('error_message')}")
            return False
        if "[TODO:" not in result["content"]:
            print("FAIL: HLD template missing [TODO:] placeholders")
            return False

        print(f"PASS: Found {len(templates)} templates, loaded hld_template with TODOs")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_skill_tools():
    """Test 6: skill_tools CRUD operations."""
    print("\n[TEST] Test 6: Skill tools work")
    try:
        from tools.skill_tools import (
            validate_skill_name,
            list_skills,
            get_skill_metadata,
            read_skill,
            write_skill_draft,
        )

        # validate_skill_name
        ok = validate_skill_name("diataxis-writing")
        if not ok["valid"]:
            print(f"FAIL: 'diataxis-writing' should be valid: {ok['issues']}")
            return False

        bad = validate_skill_name("INVALID NAME!")
        if bad.get("valid", True):
            print("FAIL: 'INVALID NAME!' should be invalid")
            return False

        # list_skills — need to set SKILLS_DIR because CWD != module dir
        default_skills_dir = os.path.join(module_path, "skills")
        result = list_skills(default_skills_dir)
        if result["status"] != "ok":
            print(f"FAIL: list_skills failed: {result.get('error_message')}")
            return False
        names = [s["name"] for s in result["skills"]]
        if "diataxis-writing" not in names:
            print(f"FAIL: 'diataxis-writing' not found. Got: {names}")
            return False

        # get_skill_metadata
        result = get_skill_metadata("style-guide")
        if result["status"] != "ok":
            print(f"FAIL: get_skill_metadata failed: {result.get('error_message')}")
            return False
        if "name" not in result["metadata"]:
            print("FAIL: metadata missing 'name'")
            return False

        # read_skill
        result = read_skill("requirement-analysis")
        if result["status"] != "ok":
            print(f"FAIL: read_skill failed: {result.get('error_message')}")
            return False
        if not result["content"]:
            print("FAIL: skill content is empty")
            return False

        # write_skill_draft (in temp dir)
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["SKILLS_DIR"] = tmpdir
            content = "---\nname: test-skill\ndescription: A test\n---\n# Test"
            result = write_skill_draft("test-skill", content)
            if result["status"] != "ok":
                print(f"FAIL: write_skill_draft failed: {result.get('error_message')}")
                return False
            skill_path = os.path.join(tmpdir, "test-skill", "SKILL.md")
            if not os.path.exists(skill_path):
                print("FAIL: SKILL.md not created")
                return False

        print(f"PASS: All skill_tools operations work. Found {len(names)} skills: {names}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 4. ORCHESTRATOR STRUCTURE
# =============================================================================


def test_analyze_requirement_structure():
    """Test 7: analyze_requirement has correct agent pipeline."""
    print("\n[TEST] Test 7: analyze_requirement orchestrator structure")
    try:
        from orchestrators.analyze_requirement import analyze_requirement_orchestrator
        from google.adk.agents import SequentialAgent, ParallelAgent

        orch = analyze_requirement_orchestrator
        if not isinstance(orch, SequentialAgent):
            print(f"FAIL: Expected SequentialAgent, got {type(orch).__name__}")
            return False

        subs = orch.sub_agents
        if len(subs) != 3:
            print(f"FAIL: Expected 3 sub_agents, got {len(subs)}")
            return False

        # Step 2 should be ParallelAgent with 4 analysts
        if not isinstance(subs[1], ParallelAgent):
            print(f"FAIL: Step 2 should be ParallelAgent, got {type(subs[1]).__name__}")
            return False

        parallel_count = len(subs[1].sub_agents)
        if parallel_count != 4:
            print(f"FAIL: ParallelAgent should have 4 sub_agents, got {parallel_count}")
            return False

        parallel_names = sorted([a.name for a in subs[1].sub_agents])
        expected = sorted(["clarity_analyst", "scope_analyst", "cross_ref_analyst", "docs_gap_analyst"])
        if parallel_names != expected:
            print(f"FAIL: Parallel agent names mismatch: {parallel_names}")
            return False

        print(f"PASS: Sequential[collector → Parallel{parallel_names} → synthesis]")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_generate_skill_structure():
    """Test 8: generate_skill has 6-step pipeline."""
    print("\n[TEST] Test 8: generate_skill orchestrator structure")
    try:
        from orchestrators.generate_skill import generate_skill_orchestrator
        from google.adk.agents import SequentialAgent

        orch = generate_skill_orchestrator
        if not isinstance(orch, SequentialAgent):
            print(f"FAIL: Expected SequentialAgent, got {type(orch).__name__}")
            return False

        subs = orch.sub_agents
        if len(subs) != 6:
            print(f"FAIL: Expected 6 sub_agents, got {len(subs)}")
            return False

        expected_keys = [
            "collected_knowledge",
            "extracted_knowledge",
            "dedup_decision",
            "skill_draft",
            "skill_reviewed",
            "skill_result",
        ]
        actual_keys = [getattr(a, "output_key", None) for a in subs]
        if actual_keys != expected_keys:
            print(f"FAIL: output_keys mismatch:\n  expected: {expected_keys}\n  actual:   {actual_keys}")
            return False

        print(f"PASS: 6-step pipeline with output_keys: {expected_keys}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_generate_document_structure():
    """Test 9: generate_document has 5-step pipeline with dynamic skills."""
    print("\n[TEST] Test 9: generate_document orchestrator structure")
    try:
        from orchestrators.generate_document import generate_document_orchestrator
        from google.adk.agents import SequentialAgent

        orch = generate_document_orchestrator
        if not isinstance(orch, SequentialAgent):
            print(f"FAIL: Expected SequentialAgent, got {type(orch).__name__}")
            return False

        subs = orch.sub_agents
        if len(subs) != 5:
            print(f"FAIL: Expected 5 sub_agents, got {len(subs)}")
            return False

        names = [a.name for a in subs]
        if "doc_content_writer" not in names:
            print(f"FAIL: Missing doc_content_writer agent")
            return False

        # Content writer should have skill tools
        writer = subs[2]  # 3rd agent (0-indexed)
        tool_names = [getattr(t, "func", None) and t.func.__name__ for t in (writer.tools or [])]
        if "read_skill" not in tool_names or "list_skills" not in tool_names:
            print(f"FAIL: Content writer missing skill tools. Has: {tool_names}")
            return False

        print(f"PASS: 5-step pipeline with dynamic skill loading: {names}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_all_orchestrators_have_descriptions():
    """Test 10: All orchestrators have description for AgentTool."""
    print("\n[TEST] Test 10: Orchestrator descriptions")
    try:
        from orchestrators.analyze_requirement import analyze_requirement_orchestrator
        from orchestrators.create_epic import create_epic_orchestrator
        from orchestrators.generate_document import generate_document_orchestrator
        from orchestrators.generate_test_plan import generate_test_plan_orchestrator
        from orchestrators.review_document import review_document_orchestrator
        from orchestrators.generate_skill import generate_skill_orchestrator

        orchestrators = [
            analyze_requirement_orchestrator,
            create_epic_orchestrator,
            generate_document_orchestrator,
            generate_test_plan_orchestrator,
            review_document_orchestrator,
            generate_skill_orchestrator,
        ]

        for orch in orchestrators:
            if not getattr(orch, "description", None):
                print(f"FAIL: {orch.name} has no description")
                return False

        names = [o.name for o in orchestrators]
        print(f"PASS: All 6 orchestrators have descriptions: {names}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 5. SKILLS & TEMPLATES VALIDATION
# =============================================================================


def test_skill_frontmatter_compliance():
    """Test 11: All SKILL.md files have valid frontmatter per agentskills.io spec."""
    print("\n[TEST] Test 11: Skill frontmatter compliance")
    try:
        import yaml

        skills_dir = os.path.join(module_path, "skills")
        skill_dirs = [
            d for d in os.listdir(skills_dir)
            if os.path.isdir(os.path.join(skills_dir, d)) and not d.startswith("_")
        ]

        errors = []
        for skill_name in skill_dirs:
            skill_file = os.path.join(skills_dir, skill_name, "SKILL.md")
            if not os.path.exists(skill_file):
                errors.append(f"{skill_name}: SKILL.md not found")
                continue

            with open(skill_file, encoding="utf-8") as f:
                content = f.read()

            # Parse frontmatter
            if not content.startswith("---"):
                errors.append(f"{skill_name}: Missing frontmatter delimiter")
                continue

            parts = content.split("---", 2)
            if len(parts) < 3:
                errors.append(f"{skill_name}: Invalid frontmatter format")
                continue

            try:
                fm = yaml.safe_load(parts[1])
            except yaml.YAMLError as e:
                errors.append(f"{skill_name}: YAML parse error: {e}")
                continue

            # Required fields per agentskills.io
            if "name" not in fm:
                errors.append(f"{skill_name}: Missing 'name'")
            elif fm["name"] != skill_name:
                errors.append(f"{skill_name}: name mismatch: '{fm['name']}' != '{skill_name}'")

            if "description" not in fm:
                errors.append(f"{skill_name}: Missing 'description'")
            elif len(fm["description"]) > 1024:
                errors.append(f"{skill_name}: description > 1024 chars")

            # Body length check
            body = parts[2].strip()
            body_lines = body.split("\n")
            if len(body_lines) > 500:
                errors.append(f"{skill_name}: Body exceeds 500 lines ({len(body_lines)})")

        if errors:
            for err in errors:
                print(f"  - {err}")
            print(f"FAIL: {len(errors)} frontmatter issues found")
            return False

        print(f"PASS: All {len(skill_dirs)} skills have valid frontmatter: {skill_dirs}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_templates_have_todos():
    """Test 12: All templates have [TODO:] placeholders."""
    print("\n[TEST] Test 12: Templates have TODO placeholders")
    try:
        assets_dir = os.path.join(module_path, "skills", "document-templates", "assets")
        templates = [f for f in os.listdir(assets_dir) if f.endswith(".md")]

        if len(templates) != 4:
            print(f"FAIL: Expected 4 templates, found {len(templates)}")
            return False

        for name in templates:
            path = os.path.join(assets_dir, name)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            todo_count = content.count("[TODO:")
            if todo_count == 0:
                print(f"FAIL: {name} has no [TODO:] placeholders")
                return False

        print(f"PASS: All 4 templates have [TODO:] placeholders: {templates}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 6. AGENT INSTRUCTION QUALITY
# =============================================================================


def test_agent_instructions_exist():
    """Test 13: All agent instruction modules export INSTRUCTION constant."""
    print("\n[TEST] Test 13: Agent instruction modules")
    try:
        agent_modules = [
            "agents.source_collector",
            "agents.clarity_analyst",
            "agents.scope_analyst",
            "agents.cross_ref_analyst",
            "agents.docs_gap_analyst",
            "agents.synthesis_agent",
            "agents.template_writer",
            "agents.quality_reviewer",
            "agents.skill_knowledge_extractor",
            "agents.skill_dedup_checker",
            "agents.skill_architect",
            "agents.skill_quality_reviewer",
        ]

        for mod_name in agent_modules:
            try:
                parts = mod_name.split(".")
                mod = __import__(mod_name, fromlist=[parts[-1]])
            except ImportError as e:
                print(f"FAIL: Cannot import {mod_name}: {e}")
                return False

            if not hasattr(mod, "INSTRUCTION"):
                print(f"FAIL: {mod_name} missing INSTRUCTION constant")
                return False

            instr = mod.INSTRUCTION
            if not isinstance(instr, str) or len(instr) < 100:
                print(f"FAIL: {mod_name} INSTRUCTION too short ({len(instr)} chars)")
                return False

        print(f"PASS: All {len(agent_modules)} agent modules export valid INSTRUCTION")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_instruction_state_references():
    """Test 14: Agent instructions reference correct state variables."""
    print("\n[TEST] Test 14: Instruction state variable references")
    try:
        import re

        # Map of agent → expected state variable references
        expected_refs = {
            "agents.clarity_analyst": ["{collected_sources}"],
            "agents.scope_analyst": ["{collected_sources}"],
            "agents.cross_ref_analyst": ["{collected_sources}"],
            "agents.docs_gap_analyst": ["{collected_sources}"],
            "agents.skill_knowledge_extractor": ["{collected_knowledge}"],
        }

        errors = []
        for mod_name, refs in expected_refs.items():
            parts = mod_name.split(".")
            mod = __import__(mod_name, fromlist=[parts[-1]])
            instr = mod.INSTRUCTION

            for ref in refs:
                if ref not in instr:
                    errors.append(f"{mod_name}: missing reference '{ref}'")

        if errors:
            for err in errors:
                print(f"  - {err}")
            print(f"FAIL: {len(errors)} missing state references")
            return False

        print(f"PASS: All checked agents reference correct state variables")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 7. PROMPT BUILDER
# =============================================================================


def test_prompt_builder():
    """Test 15: Prompt builder enriches instructions with contract context."""
    print("\n[TEST] Test 15: Prompt builder")
    try:
        from prompts.agent_instructions import (
            load_contract,
            build_base_instruction,
            discover_relevant_skills,
        )

        sample_path = os.path.join(module_path, "contract", "sample_contract.json")
        contract = load_contract(sample_path)

        if contract.project_name != "IoT Connect":
            print(f"FAIL: Contract load returned wrong name: {contract.project_name}")
            return False

        instruction = build_base_instruction(contract, "Test Agent")
        if "IoT Connect" not in instruction:
            print("FAIL: Base instruction missing project name")
            return False

        skills_dir = os.path.join(module_path, "skills")
        skills = discover_relevant_skills("documentation writing style", skills_dir)
        # discover_relevant_skills returns list[str] of skill names
        # Should find style-guide at minimum
        if not any("style" in n for n in skills):
            print(f"FAIL: discover_relevant_skills didn't find style-guide. Got: {skills}")
            return False

        print(f"PASS: Contract loaded, instruction enriched, discovered skills: {skills}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


# =============================================================================
# 8. OUTPUT_KEY CONSISTENCY
# =============================================================================


def test_output_key_chain_consistency():
    """Test 16: output_key values form valid chains across all orchestrators."""
    print("\n[TEST] Test 16: output_key chain consistency")

    try:
        from orchestrators.generate_skill import generate_skill_orchestrator
        from orchestrators.analyze_requirement import analyze_requirement_orchestrator
        from orchestrators.create_epic import create_epic_orchestrator
        from orchestrators.generate_document import generate_document_orchestrator
        from orchestrators.generate_test_plan import generate_test_plan_orchestrator
        from orchestrators.review_document import review_document_orchestrator

        def check_chain(orch):
            """Verify all sub_agents have output_key and they're unique."""
            keys = []
            agents = _flatten_agents(orch)
            for a in agents:
                key = getattr(a, "output_key", None)
                if key:
                    keys.append(key)
            # All output_keys should be unique within an orchestrator
            if len(keys) != len(set(keys)):
                return False, f"Duplicate output_keys: {keys}"
            if not keys:
                return False, "No output_keys found"
            return True, keys

        orchestrators = {
            "generate_skill": generate_skill_orchestrator,
            "analyze_requirement": analyze_requirement_orchestrator,
            "create_epic": create_epic_orchestrator,
            "generate_document": generate_document_orchestrator,
            "generate_test_plan": generate_test_plan_orchestrator,
            "review_document": review_document_orchestrator,
        }

        errors = []
        for name, orch in orchestrators.items():
            ok, info = check_chain(orch)
            if not ok:
                errors.append(f"{name}: {info}")

        if errors:
            for err in errors:
                print(f"  - {err}")
            print(f"FAIL: {len(errors)} output_key issues")
            return False

        print(f"PASS: All 6 orchestrators have unique, valid output_key chains")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def _flatten_agents(agent):
    """Recursively collect all LlmAgent instances from an orchestrator."""
    from google.adk.agents import LlmAgent

    result = []
    if isinstance(agent, LlmAgent):
        result.append(agent)
    sub = getattr(agent, "sub_agents", []) or []
    for s in sub:
        result.extend(_flatten_agents(s))
    return result


# =============================================================================
# UTILITY
# =============================================================================

_cached_module = None


def _import_agent():
    global _cached_module
    if _cached_module is None:
        import importlib.util

        agent_file = os.path.join(module_path, "agent.py")
        spec = importlib.util.spec_from_file_location("agent_m20", agent_file)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["agent_m20"] = mod
        spec.loader.exec_module(mod)
        _cached_module = mod
    return _cached_module


# =============================================================================
# MAIN
# =============================================================================


def run_all_tests():
    """Execute all tests for Module 20."""
    print_test_header("Analyst System", "20")

    results = {}

    # Module loading
    results["Root agent loads"] = test_root_agent_loads()

    # Contract
    results["Contract validates"] = test_contract_model_validates()
    results["Contract rejects invalid"] = test_contract_rejects_invalid()

    # Tools
    results["File tools"] = test_file_tools()
    results["Template tools"] = test_template_tools()
    results["Skill tools"] = test_skill_tools()

    # Orchestrator structure
    results["analyze_requirement structure"] = test_analyze_requirement_structure()
    results["generate_skill structure"] = test_generate_skill_structure()
    results["generate_document structure"] = test_generate_document_structure()
    results["Orchestrator descriptions"] = test_all_orchestrators_have_descriptions()

    # Skills & templates
    results["Skill frontmatter"] = test_skill_frontmatter_compliance()
    results["Template TODOs"] = test_templates_have_todos()

    # Agent instructions
    results["Agent instructions"] = test_agent_instructions_exist()
    results["State variable refs"] = test_instruction_state_references()

    # Prompt builder
    results["Prompt builder"] = test_prompt_builder()

    # Output keys
    results["output_key consistency"] = test_output_key_chain_consistency()

    passed = sum(1 for r in results.values() if r)
    total = len(results)
    exit_code = print_test_summary(passed, total)
    return exit_code


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
