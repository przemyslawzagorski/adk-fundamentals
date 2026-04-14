"""ADK Web Tester — orchestrator + browser sub-agent do testowania agentów ADK.

Dwa tryby:
  1. Standardowy — testy agentów ADK przez `adk web` (dropdown + chat)
  2. PRO — auto-discovery + testy dowolnej web aplikacji (FastAPI, HTMX, itp.)
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.computer_use.computer_use_toolset import ComputerUseToolset
from google.genai import types as genai_types

from .computer.playwright_computer import PlaywrightComputer
from .config import CONFIG
from .prompts import ADK_TESTER_SYSTEM_PROMPT, BROWSER_TESTER_PROMPT, ORCHESTRATOR_PROMPT
from .pro_prompts import DISCOVERY_PROMPT, PRO_BROWSER_TESTER_PROMPT, PRO_ORCHESTRATOR_PROMPT
from .tools.test_scenarios import get_available_modules, get_test_plan
from .tools.test_report import save_test_result, generate_report, generate_summary_report
from .tools.conversation_store import ConversationStore
from .tools.webapp_profile import save_discovered_profile, get_profile_briefing
from .tools.pro_report import (
    init_pro_report, save_pro_test_result, generate_pro_report,
    list_saved_profiles, load_profile,
)

logger = logging.getLogger("adk_tester")


# ── Safety decision handling (wzorzec z notebooklm_agent) ──────────────────
_SAFETY_KEY = "_pending_safety"


def _before_tool_cb(tool, args: dict, tool_context) -> Optional[dict]:
    safety = args.pop("safety_decision", None)
    if safety:
        logger.info("Safety decision received: %s", safety)
        tool_context.state[_SAFETY_KEY] = True
    return None


def _after_tool_cb(tool, args: dict, tool_context, tool_response) -> Optional[dict]:
    if tool_context.state.get(_SAFETY_KEY, False):
        tool_context.state[_SAFETY_KEY] = False
        if isinstance(tool_response, dict):
            tool_response["safety_acknowledgement"] = "true"
            logger.info("Added safety_acknowledgement to response")
            return tool_response
    return None


# ── root_agent dla adk web (orchestrator + browser sub-agent) ───────────────
_computer = PlaywrightComputer(headless=CONFIG.headless)
_toolset = ComputerUseToolset(computer=_computer)

# Sub-agent: steruje przeglądarką przez Computer Use
_browser_tester = LlmAgent(
    model=CONFIG.computer_use_model,
    name="browser_tester",
    description="Agent z Computer Use — steruje przeglądarką, nawiguje po ADK web, "
                "wpisuje prompty testowe i odczytuje odpowiedzi agentów. "
                "Deleguj do niego gdy masz gotowy plan testów do wykonania w przeglądarce.",
    instruction=BROWSER_TESTER_PROMPT.format(adk_web_url=CONFIG.adk_web_url),
    tools=[
        _toolset,
        save_test_result,
    ],
    before_tool_callback=_before_tool_cb,
    after_tool_callback=_after_tool_cb,
    output_key="browser_test_results",
)

# Root agent: orkiestruje testy, deleguje do browser_tester
root_agent = LlmAgent(
    model=CONFIG.orchestrator_model,
    name="adk_web_tester",
    instruction=ORCHESTRATOR_PROMPT.format(adk_web_url=CONFIG.adk_web_url),
    tools=[
        get_available_modules,
        get_test_plan,
        generate_report,
        generate_summary_report,
    ],
    sub_agents=[_browser_tester],
)


# ── AgentTesterSystem dla CLI ───────────────────────────────────────────────

class AgentTesterSystem:
    """System agenta do testowania ADK web z poziomu CLI."""

    def __init__(
        self,
        model: Optional[str] = None,
        headless: Optional[bool] = None,
        adk_web_url: Optional[str] = None,
    ):
        self.model = model or CONFIG.computer_use_model
        self._headless = headless if headless is not None else CONFIG.headless
        self._adk_web_url = adk_web_url or CONFIG.adk_web_url

        self.conversations = ConversationStore()
        self.computer: Optional[PlaywrightComputer] = None
        self.agent: Optional[LlmAgent] = None
        self.runner: Optional[Runner] = None
        self._session_service = InMemorySessionService()
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return

        self.computer = PlaywrightComputer(headless=self._headless)
        await self.computer.initialize()

        toolset = ComputerUseToolset(computer=self.computer)

        instruction = ADK_TESTER_SYSTEM_PROMPT.format(adk_web_url=self._adk_web_url)

        self.agent = LlmAgent(
            model=self.model,
            name="adk_web_tester",
            instruction=instruction,
            tools=[
                toolset,
                get_available_modules,
                get_test_plan,
                save_test_result,
                generate_report,
                generate_summary_report,
            ],
            before_tool_callback=_before_tool_cb,
            after_tool_callback=_after_tool_cb,
        )

        self.runner = Runner(
            agent=self.agent,
            app_name="adk_web_tester",
            session_service=self._session_service,
        )

        self._initialized = True
        logger.info("ADK Web Tester initialized (model=%s, url=%s)", self.model, self._adk_web_url)

    async def run_test(
        self,
        command: str,
        session_id: str = "default",
        user_id: str = "tester",
    ) -> str:
        """Wyślij komendę do agenta testera i zwróć odpowiedź."""
        if not self._initialized:
            await self.initialize()

        session = await self._session_service.get_session(
            app_name="adk_web_tester", user_id=user_id, session_id=session_id,
        )
        if session is None:
            session = await self._session_service.create_session(
                app_name="adk_web_tester", user_id=user_id, session_id=session_id,
            )

        user_content = genai_types.Content(
            role="user", parts=[genai_types.Part(text=command)]
        )

        response_text = ""
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_content,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    response_text = "\n".join(
                        p.text for p in event.content.parts if p.text
                    )

        return response_text

    async def test_modules(self, module_ids: list[str]) -> str:
        """Testuj podane moduły — agent sam nawiguje, wysyła prompty, generuje raport."""
        modules_str = ", ".join(module_ids)
        command = (
            f"Przetestuj następujące moduły: {modules_str}\n\n"
            f"Dla każdego modułu:\n"
            f"1. Wywołaj get_test_plan(module_id) aby poznać scenariusze\n"
            f"2. Otwórz {self._adk_web_url} w przeglądarce\n"
            f"3. Wybierz odpowiedniego agenta z dropdown\n"
            f"4. Wykonaj każdy scenariusz testowy\n"
            f"5. Zapisz wyniki przez save_test_result\n"
            f"6. Wygeneruj raport przez generate_report\n\n"
            f"Na koniec wygeneruj zbiorczy raport przez generate_summary_report."
        )
        return await self.run_test(command)

    async def close(self) -> None:
        video_path = None
        if self.computer:
            await self.computer.close()
            video_path = self.computer.video_path
            self.computer = None
        self._initialized = False
        if video_path:
            logger.info("Video recorded: %s", video_path)
        logger.info("ADK Web Tester closed.")
        return video_path


# ── ProTesterSystem — tryb PRO: discovery + test dowolnych web app ──────────

class ProTesterSystem:
    """System PRO do testowania dowolnych web aplikacji.

    Fazy:
      1. Discovery — Computer Use eksploruje stronę, buduje profil UI
      2. Testing   — Computer Use wykonuje scenariusze z profilu
      3. Report    — generuje szczegółowy raport
    """

    def __init__(
        self,
        model: Optional[str] = None,
        headless: Optional[bool] = None,
        app_url: Optional[str] = None,
    ):
        self.model = model or CONFIG.computer_use_model
        self._headless = headless if headless is not None else CONFIG.headless
        self._app_url = app_url or "http://localhost:8088"

        self.computer: Optional[PlaywrightComputer] = None
        self._session_service = InMemorySessionService()
        self._runner: Optional[Runner] = None
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return

        self.computer = PlaywrightComputer(headless=self._headless)
        await self.computer.initialize()

        toolset = ComputerUseToolset(computer=self.computer)

        # Discovery agent — eksploruje UI, buduje profil
        discovery_agent = LlmAgent(
            model=self.model,
            name="discovery_agent",
            description="Agent odkrywczy — eksploruje web aplikację przez Computer Use, "
                        "mapuje wszystkie strony i elementy UI, generuje profil testowy.",
            instruction=DISCOVERY_PROMPT.format(app_url=self._app_url),
            tools=[
                toolset,
                save_discovered_profile,
            ],
            before_tool_callback=_before_tool_cb,
            after_tool_callback=_after_tool_cb,
            output_key="discovery_results",
        )

        # Browser tester PRO — wykonuje testy wg profilu
        pro_browser_tester = LlmAgent(
            model=self.model,
            name="pro_browser_tester",
            description="Agent tester PRO — wykonuje scenariusze testowe z profilu web aplikacji "
                        "przez Computer Use. Deleguj do niego po discovery z gotowym profilem.",
            instruction=PRO_BROWSER_TESTER_PROMPT.format(
                profile_briefing="(profil zostanie dostarczony przez orchestratora)"
            ),
            tools=[
                toolset,
                save_pro_test_result,
            ],
            before_tool_callback=_before_tool_cb,
            after_tool_callback=_after_tool_cb,
            output_key="pro_test_results",
        )

        # Orchestrator PRO
        orchestrator = LlmAgent(
            model=CONFIG.orchestrator_model,
            name="pro_tester",
            instruction=PRO_ORCHESTRATOR_PROMPT.format(app_url=self._app_url),
            tools=[
                get_profile_briefing,
                init_pro_report,
                generate_pro_report,
                list_saved_profiles,
                load_profile,
            ],
            sub_agents=[discovery_agent, pro_browser_tester],
        )

        self._runner = Runner(
            agent=orchestrator,
            app_name="pro_tester",
            session_service=self._session_service,
        )

        self._initialized = True
        logger.info("PRO Tester initialized (model=%s, url=%s)", self.model, self._app_url)

    async def run_command(
        self,
        command: str,
        session_id: str = "pro_default",
        user_id: str = "tester",
    ) -> str:
        """Wyślij komendę do PRO testera."""
        if not self._initialized:
            await self.initialize()

        session = await self._session_service.get_session(
            app_name="pro_tester", user_id=user_id, session_id=session_id,
        )
        if session is None:
            session = await self._session_service.create_session(
                app_name="pro_tester", user_id=user_id, session_id=session_id,
            )

        user_content = genai_types.Content(
            role="user", parts=[genai_types.Part(text=command)]
        )

        response_text = ""
        async for event in self._runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_content,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    response_text = "\n".join(
                        p.text for p in event.content.parts if p.text
                    )

        return response_text

    async def discover_and_test(self, app_url: Optional[str] = None) -> str:
        """Pełny cykl: discovery → testy → raport."""
        url = app_url or self._app_url
        command = (
            f"Tryb PRO — pełny cykl dla {url}:\n\n"
            f"1. DISCOVERY: Deleguj do discovery_agent — niech otworzy {url}, "
            f"zbada KAŻDĄ stronę, każdy element, każdy formularz. "
            f"Na koniec discovery_agent MUSI wywołać save_discovered_profile() z pełnym JSON.\n\n"
            f"2. Po discovery wywołaj init_pro_report(app_name=..., app_url='{url}') "
            f"i get_profile_briefing() aby pobrać profil.\n\n"
            f"3. TESTY: Deleguj do pro_browser_tester z briefingiem profilu. "
            f"Agent MUSI wykonać KAŻDY flow z profilu i zapisać wyniki przez save_pro_test_result().\n\n"
            f"4. RAPORT: Po testach wywołaj generate_pro_report() aby wygenerować pełen raport.\n\n"
            f"Odpowiedz z podsumowaniem wyników."
        )
        return await self.run_command(command)

    async def discover_only(self, app_url: Optional[str] = None) -> str:
        """Tylko discovery — eksploracja UI bez testów."""
        url = app_url or self._app_url
        command = (
            f"Wykonaj TYLKO DISCOVERY dla {url}:\n"
            f"Deleguj do discovery_agent — niech otworzy {url} w przeglądarce, "
            f"zbada wszystkie strony i elementy, i zapisze profil przez save_discovered_profile().\n"
            f"NIE uruchamiaj testów. Zwróć podsumowanie odkrytego profilu."
        )
        return await self.run_command(command)

    async def test_from_profile(self, profile_path: str) -> str:
        """Testy z gotowego profilu (bez discovery)."""
        command = (
            f"Załaduj profil z pliku: {profile_path}\n"
            f"Wywołaj load_profile('{profile_path}'), potem init_pro_report() i get_profile_briefing().\n"
            f"Deleguj do pro_browser_tester z briefingiem. Wykonaj KAŻDY flow z profilu.\n"
            f"Na koniec generate_pro_report()."
        )
        return await self.run_command(command)

    async def close(self) -> Optional[str]:
        video_path = None
        if self.computer:
            await self.computer.close()
            video_path = self.computer.video_path
            self.computer = None
        self._initialized = False
        if video_path:
            logger.info("PRO video recorded: %s", video_path)
        logger.info("PRO Tester closed.")
        return video_path
