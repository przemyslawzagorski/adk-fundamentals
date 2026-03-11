#!/usr/bin/env python3
"""
🤖 GitHub Copilot Masterclass - Agentic Workspace Generator
Main Orchestrator - koordynuje wszystkie fazy generowania workspace'a
"""

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Google ADK imports
from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types, errors

# Throttling zamiast retry (unikamy restartowania całego procesu)

# Local imports - agenty są teraz tworzone bezpośrednio w orchestratorze
from agents.planning.documentation_research_agent import create_documentation_research_agent
from agents.planning.module_structure_planner import create_module_structure_planner
from agents.planning.planning_aggregator import create_planning_aggregator

from agents.execution.module_generator import create_module_generator

from agents.validation.coherence_validator import create_coherence_validator
from agents.validation.pedagogical_reviewer import create_pedagogical_reviewer
from agents.validation.final_reporter import create_final_reporter

# web_search usunięty - używamy natywnego google_search z ADK w research_agent
from tools.file_operations import create_file, read_file, list_files, create_directory
from tools.code_validator import validate_java_code, count_todo_comments, check_code_quality

load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model configuration (zgodnie z ADK 1.18.0)
MODEL_PRO = os.getenv("ADK_MODEL_PRO", "gemini-2.5-pro")
MODEL_FLASH = os.getenv("ADK_MODEL_FLASH", "gemini-2.5-flash")

# Feature flags
USE_BUILTIN_PLANNER = os.getenv("USE_BUILTIN_PLANNER", "true").lower() == "true"  # Thinking mode
USE_RETRY_LOGIC = os.getenv("USE_RETRY_LOGIC", "true").lower() == "true"  # Exponential backoff

# Request counter będzie w callbackach agentów, nie tutaj
# (eventy to chunki odpowiedzi, nie requesty!)


def get_planner_if_enabled():
    """Zwraca BuiltInPlanner jeśli włączony, None w przeciwnym razie"""
    if USE_BUILTIN_PLANNER:
        logger.info("🧠 BuiltInPlanner ENABLED (thinking mode)")
        return BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1,  # Unlimited thinking
                include_thoughts=True
            )
        )
    else:
        logger.info("⚡ BuiltInPlanner DISABLED (faster, less requests)")
        return None


class CopilotMasterclassWorkspaceGenerator:
    """
    Główny orchestrator systemu agentowego.
    Koordynuje Planning → Execution → Validation phases.
    """
    
    def __init__(self, training_plan_path: str, output_dir: str = "./output"):
        self.training_plan_path = Path(training_plan_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load training plan
        with open(self.training_plan_path, 'r', encoding='utf-8') as f:
            self.training_plan = f.read()
        
        logger.info(f"📋 Loaded training plan from: {self.training_plan_path}")
        logger.info(f"📁 Output directory: {self.output_dir}")
        
        # Initialize shared state
        self.state = {
            "training_plan": self.training_plan,
            "research_results": {},
            "execution_plan": {},
            "generated_files": [],
            "validation_results": {},
            "final_report": {}
        }
        
        # Initialize tools
        self.tools = self._initialize_tools()
        
        # Initialize agents
        self.orchestrator = self._build_orchestrator()
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """Inicjalizuje narzędzia dla agentów"""
        logger.info("🔧 Initializing tools...")

        # Tools są teraz funkcjami Python, nie klasami
        # web_search usunięty - używamy natywnego google_search z ADK
        return {
            "create_file": create_file,
            "read_file": read_file,
            "list_files": list_files,
            "create_directory": create_directory,
            "validate_java_code": validate_java_code,
            "count_todo_comments": count_todo_comments,
            "check_code_quality": check_code_quality,
        }
    
    def _build_orchestrator(self) -> SequentialAgent:
        """
        Buduje głównego orchestratora zgodnie z architekturą:
        
        ORCHESTRATOR (Sequential)
        ├─▶ PLANNING PHASE
        ├─▶ EXECUTION PHASE
        └─▶ VALIDATION PHASE
        """
        logger.info("🏗️  Building orchestrator...")
        
        # ============================================================
        # PLANNING PHASE (Research + Structure -> Aggregator)
        # ============================================================

        # Tworzymy agentów używając factory functions
        # Planning używa BuiltInPlanner dla lepszej jakości
        planner = get_planner_if_enabled()

        # Research agent używa natywnego google_search z ADK (nie przekazujemy tools)
        research_agent = create_documentation_research_agent(
            model=MODEL_PRO,
            tools=None,  # google_search jest już wbudowany w agenta
            planner=planner
        )

        structure_planner = create_module_structure_planner(
            model=MODEL_PRO,
            tools=None,
            planner=planner
        )

        planning_aggregator = create_planning_aggregator(
            model=MODEL_FLASH,
            tools=None
        )

        # Planning: SEKWENCYJNIE (unikamy 429 przy niskich limitach Quota)
        # Research → Structure → Aggregator (jeden po drugim)
        planning_phase = SequentialAgent(
            sub_agents=[
                research_agent,      # Najpierw research
                structure_planner,   # Potem planowanie struktury
                planning_aggregator  # Na końcu agregacja
            ],
            name="PlanningPhase"
        )
        
        # ============================================================
        # EXECUTION PHASE (Sequential - po 1 module dla stabilności API)
        # ============================================================

        # Tools dla execution: create_file, validate_java_code
        exec_tools = [create_file, validate_java_code, count_todo_comments]

        # Generujemy moduły SEKWENCYJNIE z THROTTLING (unikamy 429 RESOURCE_EXHAUSTED)
        # Każdy moduł to LoopAgent (Writer->Critic->Controller), więc dużo requestów
        # THROTTLING: Dodajemy opóźnienie między modułami

        module_agents = []
        THROTTLE_DELAY = int(os.getenv("THROTTLE_DELAY_SECONDS", "3"))  # 3s między modułami

        for module_id in range(1, 9):  # 8 modułów
            module_agents.append(
                create_module_generator(module_id=module_id, model=MODEL_FLASH, tools=exec_tools)
            )

        execution_phase = SequentialAgent(
            sub_agents=module_agents,
            name="ExecutionPhase"
        )
        
        # ============================================================
        # VALIDATION PHASE (Sequential: Validators → Reporter)
        # ============================================================

        coherence_validator = create_coherence_validator(
            model=MODEL_PRO,
            tools=None
        )

        pedagogical_reviewer = create_pedagogical_reviewer(
            model=MODEL_PRO,
            tools=None
        )

        final_reporter = create_final_reporter(
            model=MODEL_FLASH,
            tools=[create_file, list_files]  # Tylko potrzebne funkcje
        )

        validation_phase = SequentialAgent(
            sub_agents=[
                ParallelAgent(
                    sub_agents=[coherence_validator, pedagogical_reviewer],
                    name="ValidationAgents"
                ),
                final_reporter
            ],
            name="ValidationPhase"
        )
        
        # ============================================================
        # MASTER ORCHESTRATOR (Sequential: Planning → Execution → Validation)
        # ============================================================

        orchestrator = SequentialAgent(
            sub_agents=[planning_phase, execution_phase, validation_phase],
            name="MasterOrchestrator"
        )

        logger.info("✅ Orchestrator built successfully!")
        return orchestrator
    
    async def generate(self) -> Dict[str, Any]:
        """
        Uruchamia cały proces generowania workspace'a.

        Returns:
            Dict z wynikami: generated_files, validation_results, final_report
        """
        logger.info("=" * 80)
        logger.info("🚀 STARTING WORKSPACE GENERATION")
        logger.info("=" * 80)

        try:
            # Tworzymy session service i runner (zgodnie z ADK patterns)
            session_service = InMemorySessionService()
            session = await session_service.create_session(
                app_name="copilot_workspace_generator",
                user_id="system"
            )

            runner = Runner(
                agent=self.orchestrator,
                app_name="copilot_workspace_generator",
                session_service=session_service
            )

            # Przygotowujemy wiadomość z planem szkolenia
            initial_message = f"""
Generate GitHub Copilot Masterclass workspace based on this training plan:

{self.training_plan}

Output directory: {self.output_dir}
"""

            content = types.Content(
                role='user',
                parts=[types.Part(text=initial_message)]
            )

            # Uruchamiamy agenta (BEZ retry na Runnerze - to by restartowało cały proces!)
            logger.info("🤖 Running orchestrator...")
            logger.info(f"📊 Quota limits: ~10-15 RPM for Gemini Pro, ~60 RPM for Flash (Vertex AI)")
            logger.info("⚠️  429 errors będą obsługiwane przez throttling między modułami")

            response_text = ""
            current_agent = None

            # Przechwytywanie eventów ze strumieniowaniem do konsoli (ANSI colors!)
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=content
            ):
                # 1. Wykrywanie zmiany agenta (żeby wiedzieć, kto teraz "mówi")
                if hasattr(event, 'author') and event.author != current_agent:
                    current_agent = event.author
                    # '\033[94m' = niebieski, '\033[0m' = reset koloru
                    print(f"\n\n\033[94m=== 🤖 Zmiana kontekstu: {current_agent} rozpoczyna pracę ===\033[0m\n")

                # 2. Przechwytywanie i wyświetlanie tekstu w locie
                if hasattr(event, 'content') and event.content:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            # Dodajemy tekst do pełnej odpowiedzi (aby zapisać do pliku na końcu)
                            response_text += part.text

                            # Drukujemy na bieżąco w konsoli bez wchodzenia do nowej linii!
                            print(part.text, end="", flush=True)

                        # Opcjonalnie: logowanie użycia narzędzia (Function Calling)
                        if hasattr(part, 'function_call') and part.function_call:
                            fn_name = part.function_call.name
                            # '\033[93m' = żółty
                            print(f"\n\033[93m[🛠️  Agent używa narzędzia: {fn_name}...]\033[0m\n", flush=True)

            logger.info("=" * 80)
            logger.info("✅ WORKSPACE GENERATION COMPLETED!")
            logger.info("=" * 80)

            result = {
                "status": "success",
                "response": response_text,
                "output_dir": str(self.output_dir)
            }

            # Save final state
            self._save_state(result)

            return result

        except Exception as e:
            logger.error(f"❌ Error during generation: {e}", exc_info=True)
            raise
    
    def _save_state(self, result: Dict[str, Any]):
        """Zapisuje finalny stan do pliku JSON"""
        state_file = self.output_dir / "generation_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 State saved to: {state_file}")


async def main_async():
    """Main entry point (async)"""
    parser = argparse.ArgumentParser(
        description="GitHub Copilot Masterclass Workspace Generator"
    )
    parser.add_argument(
        "--training-plan",
        required=True,
        help="Path to training plan file"
    )
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="Output directory for generated workspace"
    )

    args = parser.parse_args()

    # Create generator
    generator = CopilotMasterclassWorkspaceGenerator(
        training_plan_path=args.training_plan,
        output_dir=args.output_dir
    )

    # Generate workspace
    result = await generator.generate()

    # Print summary
    print("\n" + "=" * 80)
    print("📊 GENERATION SUMMARY")
    print("=" * 80)
    print(f"Status: {result.get('status', 'N/A')}")
    print(f"Output directory: {result.get('output_dir', 'N/A')}")
    print("=" * 80)


def main():
    """Synchronous wrapper for async main"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

