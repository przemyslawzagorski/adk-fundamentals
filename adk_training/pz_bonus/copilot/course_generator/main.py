#!/usr/bin/env python3
"""
🎓 GitHub Copilot Course Generator v2.0
System agentowy z wzorcem Orchestrator (zamiast SequentialAgent)
"""

import argparse
import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

# Google ADK imports
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types

# Local imports - agenty
from agents.ingestion.documentation_ingestion_agent import create_documentation_ingestion_agent
from agents.evaluation.documentation_evaluator_agent import create_documentation_evaluator_agent
from agents.planning.priority_aware_syllabus_planner import create_priority_aware_syllabus_planner
from agents.repository.repository_finder_agent import create_repository_finder_agent
from agents.content.priority_aware_content_generator import create_priority_aware_content_generator

# Tools
from tools.file_operations import create_file, create_directory, read_file
from tools.web_fetcher import fetch_and_parse_url, fetch_multiple_urls
from tools.github_search import search_github, find_best_java_repository

load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model configuration
MODEL_PRO = os.getenv("ADK_MODEL_PRO", "gemini-2.5-pro")
MODEL_FLASH = os.getenv("ADK_MODEL_FLASH", "gemini-2.5-flash")

# Feature flags
USE_BUILTIN_PLANNER = os.getenv("USE_BUILTIN_PLANNER", "true").lower() == "true"


def get_planner_if_enabled():
    """Zwraca BuiltInPlanner jeśli włączony"""
    if USE_BUILTIN_PLANNER:
        logger.info("🧠 BuiltInPlanner ENABLED (thinking mode)")
        return BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1,
                include_thoughts=True
            )
        )
    else:
        logger.info("⚡ BuiltInPlanner DISABLED")
        return None


def extract_json_from_text(text: str) -> Dict:
    """Wyciąga JSON z tekstu (usuwa markdown formatting i thinking text)"""
    try:
        # 1. Spróbuj znaleźć blok kodu JSON pomiędzy znacznikami
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            json_str = match.group(1)
            logger.info("✅ Znaleziono JSON w bloku markdown")
            return json.loads(json_str)

        # 2. Fallback: Szukaj pierwszego { i ostatniego }
        start = text.find('{')
        end = text.rfind('}')

        if start != -1 and end != -1 and end > start:
            json_str = text[start:end+1]
            logger.info("✅ Znaleziono JSON bez znaczników markdown")
            return json.loads(json_str)

        # 3. Ostatnia szansa: usuń thinking text i spróbuj parsować
        clean_json = re.sub(r'^.*?(?=\{)', '', text, flags=re.DOTALL)
        clean_json = re.sub(r'\}[^}]*$', '}', clean_json)
        logger.info("⚠️ Próba parsowania po usunięciu thinking text")
        return json.loads(clean_json)

    except json.JSONDecodeError as e:
        logger.error(f"❌ Nie udało się sparsować JSON: {e}")
        logger.error(f"   Tekst (pierwsze 500 znaków): {text[:500]}...")
        logger.error(f"   Tekst (ostatnie 500 znaków): ...{text[-500:]}")
        return {}


class CopilotCourseGenerator:
    """
    Główny orchestrator systemu agentowego.
    Wzorzec: Orchestrator (zamiast SequentialAgent)
    Każda faza wywołuje agenta niezależnie i przekazuje dane jako f-string w initial_message.
    """

    def __init__(self, doc_links_path: str, output_dir: str = "./output/copilot_training"):
        self.doc_links_path = Path(doc_links_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load doc_links
        with open(self.doc_links_path, 'r', encoding='utf-8') as f:
            self.doc_links_content = f.read()

        # Parse URLs
        self.urls = [line.strip() for line in self.doc_links_content.split('\n') if line.strip() and line.startswith('http')]

        logger.info(f"📋 Loaded {len(self.urls)} URLs from: {self.doc_links_path}")
        logger.info(f"📁 Output directory: {self.output_dir}")

        # Session service (reused across phases)
        self.session_service = InMemorySessionService()

    async def _run_single_agent(
        self,
        agent: LlmAgent,
        initial_message: str,
        app_name: str,
        state: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Wywołuje pojedynczego agenta i zwraca jego output jako Dict.

        Args:
            agent: LlmAgent do wywołania
            initial_message: Wiadomość początkowa (z danymi jako f-string)
            app_name: Nazwa aplikacji dla sesji
            state: Opcjonalny state dla sesji

        Returns:
            Dict z outputem agenta (Pydantic model lub parsed JSON)
        """
        # Create session
        session = await self.session_service.create_session(
            app_name=app_name,
            user_id="system",
            state=state or {}
        )

        # Create runner
        runner = Runner(
            agent=agent,
            app_name=app_name,
            session_service=self.session_service
        )

        # Prepare message
        content = types.Content(
            role='user',
            parts=[types.Part(text=initial_message)]
        )

        # Run agent
        raw_output = None
        text_buffer = ""

        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content
        ):
            # Przechwytuj output
            if hasattr(event, 'data') and event.data is not None:
                raw_output = event.data
                logger.info(f"✅ Przechwycono output z event.data (Pydantic)")

            # Fallback: zbieraj tekst
            if hasattr(event, 'text') and event.text:
                text_buffer += event.text

            if hasattr(event, 'content') and event.content:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        text_buffer += part.text

            # Debug: log event type
            if hasattr(event, '__class__'):
                logger.debug(f"Event type: {event.__class__.__name__}")

        # Parse output
        if not raw_output and text_buffer:
            logger.info(f"⚠️ Brak event.data, próbuję wydobyć JSON z tekstu...")
            logger.info(f"   Text buffer length: {len(text_buffer)} chars")
            logger.info(f"   Text buffer preview: {text_buffer[:200]}...")
            raw_output = extract_json_from_text(text_buffer)
        elif not raw_output and not text_buffer:
            logger.error(f"❌ Brak outputu! Ani event.data, ani text_buffer!")
            return {}

        # Convert to Dict
        if hasattr(raw_output, 'model_dump'):
            return raw_output.model_dump()
        elif hasattr(raw_output, 'dict'):
            return raw_output.dict()
        elif isinstance(raw_output, dict):
            return raw_output
        else:
            logger.error(f"❌ Nieznany typ raw_output: {type(raw_output)}")
            return {}

    async def _phase_1_ingestion(self) -> Dict[str, Any]:
        """
        FAZA 1: Ingestion
        Agent 1 grupuje URL-e według struktury URI.

        Returns:
            Dict z grupami dokumentów
        """
        logger.info("\n" + "=" * 80)
        logger.info("📥 FAZA 1: INGESTION")
        logger.info("=" * 80)

        # Create agent
        planner = get_planner_if_enabled()
        agent = create_documentation_ingestion_agent(
            model=MODEL_PRO,
            tools=None,
            planner=planner
        )

        # Prepare message (przekazujemy listę URL-i jako f-string!)
        urls_text = "\n".join(self.urls)
        initial_message = f"""Zgrupuj poniższe URL-e według struktury URI:

{urls_text}

Zwróć strukturyzowany JSON zgodny z modelem IngestionResult.
"""

        # Run agent
        result = await self._run_single_agent(
            agent=agent,
            initial_message=initial_message,
            app_name="course_generator_ingestion"
        )

        logger.info(f"✅ Ingestion completed. Groups: {len(result.get('groups', {}))}")

        return result

    def _phase_1_5_web_fetching(self, ingestion_result: Dict[str, Any]) -> Dict[str, Dict]:
        """
        FAZA 1.5: Web Fetching (Python function, bez LLM)
        Pobiera treści dokumentacji PRZED Agentem 2.

        Args:
            ingestion_result: Output z Fazy 1

        Returns:
            Dict mapujący URL -> parsed content
        """
        logger.info("\n" + "=" * 80)
        logger.info("🌐 FAZA 1.5: WEB FETCHING")
        logger.info("=" * 80)

        # Zbierz wszystkie URL-e z grup
        all_urls = []
        groups = ingestion_result.get('groups', {})
        for group_name, group_data in groups.items():
            urls = group_data.get('urls', [])
            all_urls.extend(urls)

        logger.info(f"📥 Fetching {len(all_urls)} URLs...")

        # Fetch (z delay 1s między requestami)
        fetched_content = fetch_multiple_urls(all_urls, delay=1.0)

        # Count successes
        success_count = sum(1 for content in fetched_content.values() if content.get('error') is None)
        logger.info(f"✅ Successfully fetched {success_count}/{len(all_urls)} URLs")

        return fetched_content

    async def _phase_2_evaluation(
        self,
        ingestion_result: Dict[str, Any],
        fetched_content: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        FAZA 2: Evaluation
        Agent 2 ocenia dokumenty w paczkach po 5 (unikanie lost in the middle).

        Args:
            ingestion_result: Output z Fazy 1
            fetched_content: Output z Fazy 1.5

        Returns:
            Dict z ocenami wszystkich dokumentów
        """
        logger.info("\n" + "=" * 80)
        logger.info("⭐ FAZA 2: EVALUATION")
        logger.info("=" * 80)

        # Create agent
        planner = get_planner_if_enabled()
        agent = create_documentation_evaluator_agent(
            model=MODEL_PRO,
            tools=None,
            planner=planner
        )

        # Zbierz wszystkie URL-e
        all_urls = []
        groups = ingestion_result.get('groups', {})
        for group_name, group_data in groups.items():
            urls = group_data.get('urls', [])
            all_urls.extend(urls)

        # Podziel na paczki po 5
        batch_size = 5
        batches = [all_urls[i:i+batch_size] for i in range(0, len(all_urls), batch_size)]

        logger.info(f"📦 Evaluating {len(all_urls)} URLs in {len(batches)} batches (batch_size={batch_size})")

        all_evaluations = []

        for batch_idx, batch_urls in enumerate(batches):
            logger.info(f"\n📦 Batch {batch_idx+1}/{len(batches)}: {len(batch_urls)} URLs")

            # Prepare batch data (URL + content)
            batch_data = []
            for url in batch_urls:
                content_data = fetched_content.get(url, {})
                batch_data.append({
                    "url": url,
                    "title": content_data.get('title', ''),
                    "content_preview": content_data.get('content', '')[:2000],  # First 2000 chars
                    "headings": content_data.get('headings', []),
                    "code_blocks": content_data.get('code_blocks', 0)
                })

            # Prepare message
            batch_json = json.dumps(batch_data, indent=2, ensure_ascii=False)
            initial_message = f"""Oceń poniższe dokumenty według 4 kryteriów (practical_value, complexity, uniqueness, exercise_potential).

Dokumenty do oceny:
{batch_json}

Zwróć strukturyzowany JSON zgodny z modelem EvaluationResult.
"""

            # Run agent
            batch_result = await self._run_single_agent(
                agent=agent,
                initial_message=initial_message,
                app_name=f"course_generator_evaluation_batch_{batch_idx}"
            )

            # Collect evaluations
            batch_evaluations = batch_result.get('evaluations', [])
            all_evaluations.extend(batch_evaluations)

            logger.info(f"✅ Batch {batch_idx+1} completed: {len(batch_evaluations)} evaluations")

        # Aggregate results
        tier_1_count = sum(1 for e in all_evaluations if e.get('final_weight') == 5)
        tier_2_count = sum(1 for e in all_evaluations if e.get('final_weight') == 3)
        tier_3_count = sum(1 for e in all_evaluations if e.get('final_weight') == 1)

        result = {
            "evaluations": all_evaluations,
            "tier_1_count": tier_1_count,
            "tier_2_count": tier_2_count,
            "tier_3_count": tier_3_count,
            "summary": f"Evaluated {len(all_evaluations)} documents: Tier 1={tier_1_count}, Tier 2={tier_2_count}, Tier 3={tier_3_count}"
        }

        logger.info(f"✅ Evaluation completed: {result['summary']}")

        return result

    async def _phase_3_planning(self, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        FAZA 3: Planning
        Agent 3 tworzy plan szkolenia z priorytetami.

        Args:
            evaluation_result: Output z Fazy 2

        Returns:
            Dict z planem szkolenia (moduły, lekcje, ćwiczenia)
        """
        logger.info("\n" + "=" * 80)
        logger.info("📚 FAZA 3: PLANNING")
        logger.info("=" * 80)

        # Create agent
        planner = get_planner_if_enabled()
        agent = create_priority_aware_syllabus_planner(
            model=MODEL_PRO,
            tools=None,
            planner=planner
        )

        # Prepare message (przekazujemy oceny jako f-string!)
        evaluations_json = json.dumps(evaluation_result, indent=2, ensure_ascii=False)
        initial_message = f"""Stwórz plan szkolenia GitHub Copilot na podstawie poniższych ocen dokumentacji.

Oceny dokumentów:
{evaluations_json}

Zastosuj alokację 80/15/5 (Tier 1/2/3).
Zwróć strukturyzowany JSON zgodny z modelem SyllabusResult.
"""

        # Run agent
        result = await self._run_single_agent(
            agent=agent,
            initial_message=initial_message,
            app_name="course_generator_planning"
        )

        modules_count = len(result.get('modules', []))
        total_hours = result.get('total_estimated_hours', 0)

        logger.info(f"✅ Planning completed: {modules_count} modules, {total_hours}h total")

        return result

    async def _phase_4_repository(self, syllabus_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        FAZA 4: Repository
        Agent 4 znajduje optymalne repozytorium Java.

        Args:
            syllabus_result: Output z Fazy 3

        Returns:
            Dict z wybranym repozytorium
        """
        logger.info("\n" + "=" * 80)
        logger.info("🔍 FAZA 4: REPOSITORY")
        logger.info("=" * 80)

        # Create agent
        agent = create_repository_finder_agent(
            model=MODEL_FLASH,
            tools=[search_github, find_best_java_repository],
            planner=None
        )

        # Prepare message (przekazujemy sylabus jako f-string!)
        # Ale tylko kluczowe info (nie cały JSON - za duży)
        modules_summary = []
        for module in syllabus_result.get('modules', []):
            modules_summary.append({
                "name": module.get('name'),
                "priority": module.get('priority'),
                "concepts": [lesson.get('concepts', []) for lesson in module.get('lessons', [])]
            })

        summary_json = json.dumps(modules_summary, indent=2, ensure_ascii=False)
        initial_message = f"""Znajdź optymalne repozytorium Java do ćwiczeń dla poniższego planu szkolenia.

Plan szkolenia (podsumowanie):
{summary_json}

Użyj narzędzia search_github aby znaleźć najlepsze repo (np. spring-petclinic).
Zwróć strukturyzowany JSON zgodny z modelem RepositorySearchResult.
"""

        # Run agent
        result = await self._run_single_agent(
            agent=agent,
            initial_message=initial_message,
            app_name="course_generator_repository"
        )

        selected_repo = result.get('selected_repository', {})
        repo_name = selected_repo.get('name', 'N/A')
        repo_stars = selected_repo.get('stars', 0)

        logger.info(f"✅ Repository selected: {repo_name} ({repo_stars} stars)")

        return result

    async def _phase_5_content_generation(
        self,
        syllabus_result: Dict[str, Any],
        repository_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        FAZA 5: Content Generation
        Agent 5 generuje materiały DLA KAŻDEGO MODUŁU OSOBNO (pętla!).

        Args:
            syllabus_result: Output z Fazy 3
            repository_result: Output z Fazy 4

        Returns:
            Dict z listą wygenerowanych plików
        """
        logger.info("\n" + "=" * 80)
        logger.info("📝 FAZA 5: CONTENT GENERATION")
        logger.info("=" * 80)

        # Create agent
        agent = create_priority_aware_content_generator(
            model=MODEL_FLASH,
            tools=[create_file, create_directory],
            planner=None
        )

        # Extract repo info
        selected_repo = repository_result.get('selected_repository', {})
        repo_name = selected_repo.get('name', 'spring-petclinic')
        repo_url = selected_repo.get('url', 'https://github.com/spring-projects/spring-petclinic')

        # Get modules
        modules = syllabus_result.get('modules', [])

        logger.info(f"📦 Generating content for {len(modules)} modules...")
        logger.info(f"📁 Output directory: {self.output_dir}")

        all_generated_files = []

        # PĘTLA PO MODUŁACH (kluczowe!)
        for module_idx, module in enumerate(modules):
            module_id = module.get('id', f'module_{module_idx+1}')
            module_name = module.get('name', 'Unknown')
            module_tier = module.get('tier', 'tier_1_critical')
            module_priority = module.get('priority', 3)

            logger.info(f"\n📦 Module {module_idx+1}/{len(modules)}: {module_name} (tier={module_tier}, priority={module_priority})")

            # Prepare message (tylko TEN moduł!)
            module_json = json.dumps(module, indent=2, ensure_ascii=False)
            initial_message = f"""Wygeneruj materiały TYLKO dla poniższego modułu.

Moduł:
{module_json}

Repozytorium do ćwiczeń:
- Nazwa: {repo_name}
- URL: {repo_url}

Output directory: {self.output_dir}

Wygeneruj pliki zgodnie z priorytetem modułu:
- Priority 5: README 3000 słów, 10-15 ćwiczeń, 5 plików config
- Priority 3: README 1200 słów, 3-5 ćwiczeń, 2 pliki config
- Priority 1: README 400 słów, 1-2 ćwiczenia

Użyj narzędzi create_file i create_directory.
Ścieżki plików: {self.output_dir}/{module_tier}/{module_id}/README.md

Zwróć strukturyzowany JSON zgodny z modelem ContentGenerationResult.
"""

            # Run agent
            module_result = await self._run_single_agent(
                agent=agent,
                initial_message=initial_message,
                app_name=f"course_generator_content_{module_id}"
            )

            # Collect generated files
            module_files = module_result.get('generated_files', [])
            all_generated_files.extend(module_files)

            logger.info(f"✅ Module {module_idx+1} completed: {len(module_files)} files generated")

        # Aggregate results
        tier_1_files = sum(1 for f in all_generated_files if 'tier_1' in f.get('path', ''))
        tier_2_files = sum(1 for f in all_generated_files if 'tier_2' in f.get('path', ''))
        tier_3_files = sum(1 for f in all_generated_files if 'tier_3' in f.get('path', ''))

        result = {
            "generated_files": all_generated_files,
            "total_files": len(all_generated_files),
            "tier_1_files": tier_1_files,
            "tier_2_files": tier_2_files,
            "tier_3_files": tier_3_files,
            "summary": f"Generated {len(all_generated_files)} files: Tier 1={tier_1_files}, Tier 2={tier_2_files}, Tier 3={tier_3_files}"
        }

        logger.info(f"✅ Content generation completed: {result['summary']}")

        return result

    async def generate(self):
        """
        Główna metoda orkiestrująca wszystkie 5 faz.

        Wzorzec Orchestrator:
        1. Faza 1: Ingestion (Agent 1)
        2. Faza 1.5: Web Fetching (Python function)
        3. Faza 2: Evaluation (Agent 2 w pętli po paczkach)
        4. Faza 3: Planning (Agent 3)
        5. Faza 4: Repository (Agent 4)
        6. Faza 5: Content (Agent 5 w pętli po modułach)

        Returns:
            Dict z podsumowaniem
        """
        logger.info("=" * 80)
        logger.info("🚀 STARTING COURSE GENERATION (Orchestrator Pattern)")
        logger.info("=" * 80)

        try:
            # FAZA 1: Ingestion
            ingestion_result = await self._phase_1_ingestion()

            # FAZA 1.5: Web Fetching (Python, bez LLM)
            fetched_content = self._phase_1_5_web_fetching(ingestion_result)

            # FAZA 2: Evaluation (w pętli po paczkach)
            evaluation_result = await self._phase_2_evaluation(ingestion_result, fetched_content)

            # FAZA 3: Planning
            syllabus_result = await self._phase_3_planning(evaluation_result)

            # FAZA 4: Repository
            repository_result = await self._phase_4_repository(syllabus_result)

            # FAZA 5: Content (w pętli po modułach)
            content_result = await self._phase_5_content_generation(syllabus_result, repository_result)

            # Save metadata
            metadata = {
                "ingestion": ingestion_result,
                "evaluation": evaluation_result,
                "syllabus": syllabus_result,
                "repository": repository_result,
                "content": content_result
            }

            metadata_path = self.output_dir / "training_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"\n💾 Metadata saved to: {metadata_path}")

            logger.info("\n" + "=" * 80)
            logger.info("✅ GENERATION COMPLETED!")
            logger.info("=" * 80)
            logger.info(f"📁 Output: {self.output_dir}")
            logger.info(f"📊 Modules: {len(syllabus_result.get('modules', []))}")
            logger.info(f"📄 Files: {content_result.get('total_files', 0)}")
            logger.info("=" * 80)

            return {
                "status": "success",
                "output_dir": str(self.output_dir),
                "modules_count": len(syllabus_result.get('modules', [])),
                "files_count": content_result.get('total_files', 0)
            }

        except Exception as e:
            logger.error(f"❌ Error during generation: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }



async def main_async():
    """Main entry point (async)"""
    parser = argparse.ArgumentParser(
        description="GitHub Copilot Course Generator"
    )
    parser.add_argument(
        "--doc-links",
        default="doc_links",
        help="Path to doc_links file"
    )
    parser.add_argument(
        "--output-dir",
        default="./output/copilot_training",
        help="Output directory"
    )
    
    args = parser.parse_args()
    
    # Create generator
    generator = CopilotCourseGenerator(
        doc_links_path=args.doc_links,
        output_dir=args.output_dir
    )
    
    # Generate course
    result = await generator.generate()
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 GENERATION SUMMARY")
    print("=" * 80)
    print(f"Status: {result.get('status', 'N/A')}")
    print(f"Output: {result.get('output_dir', 'N/A')}")
    print("=" * 80)


def main():
    """Synchronous wrapper"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

