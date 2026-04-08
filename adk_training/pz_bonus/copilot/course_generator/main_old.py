#!/usr/bin/env python3
"""
🎓 GitHub Copilot Course Generator
System agentowy do generowania materiałów szkoleniowych z priorytetyzacją
"""

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Google ADK imports
from google.adk.agents import SequentialAgent
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


class CopilotCourseGenerator:
    """
    Główny orchestrator systemu agentowego.
    Koordynuje 5 agentów w Sequential Flow.
    """
    
    def __init__(self, doc_links_path: str, output_dir: str = "./output"):
        self.doc_links_path = Path(doc_links_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load doc_links
        with open(self.doc_links_path, 'r', encoding='utf-8') as f:
            self.doc_links_content = f.read()
        
        logger.info(f"📋 Loaded doc_links from: {self.doc_links_path}")
        logger.info(f"📁 Output directory: {self.output_dir}")
        
        # Initialize tools
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self):
        """Inicjalizuje narzędzia dla agentów"""
        logger.info("🔧 Initializing tools...")
        
        return {
            "create_file": create_file,
            "create_directory": create_directory,
            "read_file": read_file,
            "fetch_and_parse_url": fetch_and_parse_url,
            "fetch_multiple_urls": fetch_multiple_urls,
            "search_github": search_github,
            "find_best_java_repository": find_best_java_repository,
        }
    
    async def generate(self):
        """
        Uruchamia cały proces generowania kursu.
        
        Sequential Flow:
        1. DocumentationIngestionAgent - grupuje URL-e
        2. DocumentationEvaluatorAgent - ocenia (wagi 1-5)
        3. PriorityAwareSyllabusPlannerAgent - tworzy plan
        4. RepositoryFinderAgent - znajduje repo Java
        5. PriorityAwareContentGeneratorAgent - generuje materiały
        """
        logger.info("=" * 80)
        logger.info("🚀 STARTING COURSE GENERATION")
        logger.info("   Architecture: Sequential Flow (5 Agents)")
        logger.info("=" * 80)
        
        try:
            # Session service
            session_service = InMemorySessionService()
            session = await session_service.create_session(
                app_name="copilot_course_generator",
                user_id="system",
                state={
                    "doc_links_content": self.doc_links_content,
                    "output_dir": str(self.output_dir)
                }
            )
            
            # Planner (thinking mode)
            planner = get_planner_if_enabled()
            
            # Tools list (ADK wymaga listy, nie dict!)
            tools_list = list(self.tools.values())
            
            # Build Sequential Agent
            sequential_agent = SequentialAgent(
                sub_agents=[
                    create_documentation_ingestion_agent(
                        model=MODEL_PRO,
                        tools=None,  # Ten agent nie potrzebuje tools
                        planner=planner
                    ),
                    create_documentation_evaluator_agent(
                        model=MODEL_PRO,
                        tools=None,
                        planner=planner
                    ),
                    create_priority_aware_syllabus_planner(
                        model=MODEL_PRO,
                        tools=None,
                        planner=planner
                    ),
                    create_repository_finder_agent(
                        model=MODEL_FLASH,
                        tools=[search_github, find_best_java_repository],
                        planner=None
                    ),
                    create_priority_aware_content_generator(
                        model=MODEL_FLASH,
                        tools=[create_file, create_directory],
                        planner=None
                    )
                ],
                name="CopilotCourseGeneratorPipeline"
            )
            
            # Runner
            runner = Runner(
                agent=sequential_agent,
                app_name="copilot_course_generator",
                session_service=session_service
            )
            
            # Initial message
            initial_message = f"""
Wygeneruj kompletny kurs GitHub Copilot na podstawie dokumentacji.

Lista URL-i do przetworzenia znajduje się w state.doc_links_content.

Wykonaj wszystkie 5 faz:
1. Ingestion - zgrupuj URL-e
2. Evaluation - oceń (wagi 1-5)
3. Planning - stwórz plan szkolenia
4. Repository - znajdź repo Java
5. Content - wygeneruj materiały

Rozpocznij!
"""
            
            content = types.Content(
                role='user',
                parts=[types.Part(text=initial_message)]
            )
            
            logger.info("🤖 Running sequential agents...")
            
            # Run async
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=content
            ):
                # Log progress
                if hasattr(event, 'author'):
                    logger.info(f"📍 Agent: {event.author}")
            
            logger.info("✅ GENERATION COMPLETED!")
            
            return {
                "status": "success",
                "output_dir": str(self.output_dir)
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

