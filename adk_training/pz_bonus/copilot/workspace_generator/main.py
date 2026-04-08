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
import yaml
from pathlib import Path
from typing import Dict, Any, List
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
        
        # Load training plan (tematy modułów)
        with open(self.training_plan_path, 'r', encoding='utf-8') as f:
            self.training_plan = f.read()

        # Load funkcje plan (funkcje Copilota)
        funkcje_plan_path = Path(__file__).parent / "funkcje_copilot_plan.md"
        if funkcje_plan_path.exists():
            with open(funkcje_plan_path, 'r', encoding='utf-8') as f:
                self.funkcje_plan = f.read()
            logger.info(f"📋 Loaded funkcje plan from: {funkcje_plan_path.name}")
        else:
            self.funkcje_plan = ""
            logger.warning(f"⚠️  funkcje_copilot_plan.md not found")

        # Load YAML config
        config_path = Path(__file__).parent / "config" / "agents_config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"⚙️  Loaded config from: {config_path.name}")
        else:
            self.config = {}
            logger.warning(f"⚠️  agents_config.yaml not found, using defaults")

        logger.info(f"📋 Loaded training plan from: {self.training_plan_path}")
        logger.info(f"📁 Output directory: {self.output_dir}")

        # Initialize shared state
        self.state = {
            "training_plan": self.training_plan,
            "funkcje_plan": self.funkcje_plan,  # ← DODANO
            "research_results": {},
            "execution_plan": {},
            "generated_files": [],
            "validation_results": {},
            "final_report": {}
        }
        
        # Initialize tools
        self.tools = self._initialize_tools()

        # USUNIĘTO: self.orchestrator = self._build_orchestrator()
        # Nowa architektura (v1.6.0) nie używa monolitycznego orchestratora!
        # Każda faza buduje swoich agentów bezpośrednio.
    
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
    
    # =========================================================================
    # METODY - Izolacja Sesji (v1.6.0)
    # =========================================================================
    # USUNIĘTO: def _build_orchestrator() - martwy kod z v1.5.1
    # Nowa architektura buduje agentów bezpośrednio w każdej fazie.

    async def _run_planning_phase(self) -> Dict[str, Any]:
        """
        Faza 1: Planning - jedna sesja.
        Zwraca execution_plan jako Dict.
        """
        from google.adk.sessions import InMemorySessionService
        from google.adk.runners import Runner
        from google.adk.agents import SequentialAgent
        from agents.planning.documentation_research_agent import create_documentation_research_agent
        from agents.planning.module_structure_planner import create_module_structure_planner
        from agents.planning.planning_aggregator import create_planning_aggregator
        # get_planner_if_enabled() jest w zasięgu globalnym (linia 43), nie trzeba importować!

        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name="copilot_workspace_generator_planning",
            user_id="system",
            state={
                "training_plan": self.training_plan,
                "funkcje_plan": self.funkcje_plan
            }
        )

        # KRYTYCZNE: Buduj PlanningPhase bezpośrednio, NIE przez _build_orchestrator()!
        # (unikamy budowania całego monolitu z 8 modułami)
        planner = get_planner_if_enabled()

        planning_agents = SequentialAgent(
            sub_agents=[
                create_documentation_research_agent(
                    model="gemini-2.5-pro",
                    tools=None,
                    planner=planner
                ),
                create_module_structure_planner(
                    model="gemini-2.5-pro",
                    tools=None,
                    planner=planner
                ),
                create_planning_aggregator(
                    model="gemini-2.5-flash",
                    tools=None
                )
            ],
            name="PlanningPhase"
        )

        runner = Runner(
            agent=planning_agents,
            app_name="copilot_workspace_generator_planning",
            session_service=session_service
        )

        initial_message = f"""
Generate execution plan for GitHub Copilot Masterclass based on this training plan:

{self.training_plan}

Funkcje Copilota do nauczenia:
{self.funkcje_plan}

Generate structured plan for all 8 modules.
"""

        content = types.Content(
            role='user',
            parts=[types.Part(text=initial_message)]
        )

        logger.info("🔍 Running planning agents...")

        raw_plan = None
        plan_text_buffer = ""

        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content
        ):
            # Przechwytujemy eventy bezpośrednio ze strumienia!
            author = getattr(event, 'author', '')

            # Nasłuchujemy na agenta agregującego
            if author == "PlanningAggregator":
                # ADK zwraca obiekty Pydantic w 'event.data' (jeśli output_schema zadziałał)
                if hasattr(event, 'data') and event.data is not None:
                    raw_plan = event.data
                    logger.info(f"✅ Przechwycono execution_plan z event.data (Pydantic)")

                # Jako potężny fallback, zbieramy surowy tekst z odpowiedzi
                if hasattr(event, 'text') and event.text:
                    plan_text_buffer += event.text

                # Sprawdź też event.content
                if hasattr(event, 'content') and event.content:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            plan_text_buffer += part.text

        # =====================================================================
        # KRYTYCZNA POPRAWKA: Przetwarzanie przechwyconych zdarzeń
        # =====================================================================

        # Jeśli ADK nie włożyło Pydantic Modelu do event.data, ratujemy się tekstem
        if not raw_plan and plan_text_buffer:
            logger.info(f"⚠️ Brak event.data, próbuję wydobyć JSON z tekstu...")
            import re
            # Czyścimy z formatowania markdown (usuwamy ewentualne ```json i ```)
            clean_json = re.sub(r'```(?:json)?\s*', '', plan_text_buffer)
            clean_json = re.sub(r'```\s*$', '', clean_json).strip()

            try:
                raw_plan = json.loads(clean_json)
                logger.info(f"✅ Wydobyto execution_plan z tekstu (JSON parsing)")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Nie udało się sparsować JSON z tekstu: {e}")
                logger.error(f"   Tekst: {plan_text_buffer[:500]}...")
                raw_plan = {}

        # Bezpieczne zrzutowanie obiektu do standardowego słownika (Dict)
        if hasattr(raw_plan, 'model_dump'):
            execution_plan = raw_plan.model_dump()
        elif hasattr(raw_plan, 'dict'):
            execution_plan = raw_plan.dict()
        elif isinstance(raw_plan, dict):
            execution_plan = raw_plan
        else:
            logger.error(f"❌ Nieznany typ raw_plan: {type(raw_plan)}")
            execution_plan = {}

        logger.info(f"✅ Planning completed. Generated plan for {len(execution_plan.get('modules', []))} modules")

        return execution_plan

    async def _run_execution_phase_isolated(self, execution_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Faza 2: Execution - osobna sesja dla KAŻDEGO modułu + shared context.
        Zwraca listę podsumowań wygenerowanych modułów.
        """
        from google.adk.sessions import InMemorySessionService
        from google.adk.runners import Runner
        from agents.execution.module_generator import create_module_generator
        import asyncio

        session_service = InMemorySessionService()
        generated_modules_summary = []

        # Project guidelines (spójność między modułami)
        project_guidelines = {
            "java_version": "17",
            "spring_boot_version": "3.2.0",
            "code_style": "Google Java Style",
            "todo_format": "// TODO: [Copilot Feature] - Description",
            "python_version": "3.11+",
            "react_version": "18+",
            "typescript": True
        }

        modules = execution_plan.get("modules", [])

        for module_id in range(1, min(9, len(modules) + 1)):  # 8 modułów lub ile jest w planie
            logger.info(f"\n{'='*80}")
            logger.info(f"🔨 MODULE {module_id}/{len(modules)}")
            logger.info(f"{'='*80}")

            # Pobierz info o obecnym module z planu
            current_module = modules[module_id - 1] if module_id <= len(modules) else {}

            # NOWA SESJA dla każdego modułu
            module_session = await session_service.create_session(
                app_name=f"copilot_workspace_generator_module_{module_id}",
                user_id="system",
                state={
                    # Identyfikacja
                    "module_id": module_id,

                    # Pełny plan (żeby widzieć całość)
                    "execution_plan": execution_plan,

                    # Kontekst szkolenia
                    "training_plan": self.training_plan,
                    "funkcje_plan": self.funkcje_plan,

                    # KLUCZOWE: Podsumowanie poprzednich modułów
                    "previous_modules_summary": generated_modules_summary,

                    # Wytyczne projektu (spójność)
                    "project_guidelines": project_guidelines,

                    # Info o obecnym module
                    "current_module": current_module,

                    # KRYTYCZNE: Wyciągnięte pola dla state injection (unikanie current_module.domain)
                    "current_module_domain": current_module.get("domain", "Unknown"),
                    "current_module_name": current_module.get("name", f"Module {module_id}"),

                    # Output directory (dla LoopController)
                    "output_dir": str(self.output_dir),

                    # -------------------------------------------------------------
                    # ZABEZPIECZENIE PRZED KEYERROR (Google ADK Template injection)
                    # -------------------------------------------------------------
                    "generated_code": "Model zapisał pliki używając narzędzi.",
                    "training_critique": "Brak uwag. To pierwsza iteracja."
                }
            )

            # Narzędzia dla modułu (MUSI BYĆ LISTA, nie Dict!)
            exec_tools_dict = self._initialize_tools()
            exec_tools = list(exec_tools_dict.values())  # ← KRYTYCZNE: ADK wymaga listy!

            # NOWY RUNNER dla każdego modułu
            module_agent = create_module_generator(
                module_id=module_id,
                model="gemini-2.5-flash",
                tools=exec_tools,
                config=self.config
            )

            module_runner = Runner(
                agent=module_agent,
                app_name=f"copilot_workspace_generator_module_{module_id}",
                session_service=session_service
            )

            # Uruchom TYLKO ten moduł
            initial_message = f"Generate module {module_id}: {current_module.get('name', 'Unknown')}"
            content = types.Content(
                role='user',
                parts=[types.Part(text=initial_message)]
            )

            logger.info(f"🤖 Running module {module_id} agent...")

            async for event in module_runner.run_async(
                user_id=module_session.user_id,
                session_id=module_session.id,
                new_message=content
            ):
                # Logowanie eventów (opcjonalne)
                if hasattr(event, 'author'):
                    current_agent = event.author
                    if "PolyglotCodeAgent" in current_agent or "TrainingValueCritic" in current_agent:
                        print(f"\n\033[94m=== 🤖 {current_agent} ===\033[0m")

            # Bezpieczne pobranie liczby plików (niezależnie czy model zwróci int czy listę)
            files_data = current_module.get("files", 0)
            f_count = files_data if isinstance(files_data, int) else len(files_data)

            # ZAPISZ PODSUMOWANIE (dla następnych modułów)
            summary = {
                "module_id": module_id,
                "name": current_module.get("name", f"Module {module_id}"),
                "domain": current_module.get("domain", "Unknown"),
                "copilot_features_used": current_module.get("copilot_features", []),
                "files_count": f_count
            }
            generated_modules_summary.append(summary)

            logger.info(f"✅ Module {module_id} completed!")
            logger.info(f"   Domain: {summary['domain']}")
            logger.info(f"   Features: {', '.join(summary['copilot_features_used'])}")
            logger.info(f"   Files: {summary['files_count']}")

            # Throttling między modułami (unikanie 429)
            if module_id < len(modules):
                logger.info(f"⏳ Throttling 3s before next module...")
                await asyncio.sleep(3)

        return generated_modules_summary

    async def _run_validation_phase(self, generated_modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Faza 3: Validation - jedna sesja.
        Zwraca wyniki walidacji.
        """
        logger.info("🔍 Running validation phase...")

        # TODO: Implementacja walidacji (opcjonalna dla v1.6.0)
        # Na razie zwracamy placeholder

        return {
            "status": "skipped",
            "message": "Validation phase not implemented in v1.6.0"
        }

    async def generate(self) -> Dict[str, Any]:
        """
        Uruchamia cały proces generowania workspace'a.

        ARCHITEKTURA v1.6.0 - Izolacja Sesji + Shared Context:
        - Faza 1: Planning (jedna sesja) → execution_plan.json
        - Faza 2: Execution (osobna sesja dla KAŻDEGO modułu + shared context)
        - Faza 3: Validation (jedna sesja)

        Returns:
            Dict z wynikami: execution_plan, generated_modules, validation_results
        """
        logger.info("=" * 80)
        logger.info("🚀 STARTING WORKSPACE GENERATION v1.6.0")
        logger.info("   Architecture: Isolated Sessions + Shared Context")
        logger.info("=" * 80)

        try:
            # ============================================================
            # FAZA 1: PLANNING (jedna sesja)
            # ============================================================
            logger.info("\n" + "=" * 80)
            logger.info("📋 PHASE 1: PLANNING")
            logger.info("=" * 80)

            execution_plan = await self._run_planning_phase()

            # Zapisz plan do pliku (dla debugowania)
            plan_file = self.output_dir / "execution_plan.json"
            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(execution_plan, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Saved execution plan to: {plan_file}")

            # ============================================================
            # FAZA 2: EXECUTION (osobne sesje + shared context)
            # ============================================================
            logger.info("\n" + "=" * 80)
            logger.info("🔨 PHASE 2: EXECUTION (Isolated Sessions + Shared Context)")
            logger.info("=" * 80)

            generated_modules = await self._run_execution_phase_isolated(execution_plan)

            # ============================================================
            # FAZA 3: VALIDATION (jedna sesja)
            # ============================================================
            logger.info("\n" + "=" * 80)
            logger.info("✅ PHASE 3: VALIDATION")
            logger.info("=" * 80)

            validation_results = await self._run_validation_phase(generated_modules)

            logger.info("\n" + "=" * 80)
            logger.info("✅ GENERATION COMPLETED!")
            logger.info("=" * 80)

            # Zwracamy wyniki
            return {
                "status": "success",
                "output_dir": str(self.output_dir),
                "execution_plan": execution_plan,
                "generated_modules": generated_modules,
                "validation_results": validation_results
            }

        except Exception as e:
            logger.error(f"❌ Error during generation: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "output_dir": str(self.output_dir)
            }
    
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

