"""NotebookLM Agent V2 — główny moduł agenta ADK."""

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
from .prompts import NOTEBOOKLM_SYSTEM_PROMPT
from .tools.notebook_library import NotebookLibrary
from .tools.conversation_store import ConversationStore

logger = logging.getLogger("notebooklm_agent")


# ── root_agent dla adk web ──────────────────────────────────────────────────
# adk web szuka zmiennej `root_agent` (LlmAgent) na poziomie modułu.
# PlaywrightComputer z lazy init — browser startuje dopiero przy pierwszym użyciu narzędzia.

_computer = PlaywrightComputer(headless=CONFIG.headless)
_toolset = ComputerUseToolset(computer=_computer)

_library = NotebookLibrary()


def _build_instruction() -> str:
    """Dynamicznie buduj system prompt z aktualną biblioteką notebooków."""
    library_info = _library.describe_for_prompt()
    parts = [NOTEBOOKLM_SYSTEM_PROMPT, f"\n\n## Biblioteka notebooków\n{library_info}"]
    if CONFIG.default_notebook_url:
        parts.append(f"\n\n## Aktywny notebook\nDomyślny URL: {CONFIG.default_notebook_url}")
    return "".join(parts)


# ── Safety decision handling ────────────────────────────────────────────────
# Computer Use model może zwrócić safety_decision w args function call.
# API wymaga safety_acknowledgement w function response — ADK tego nie obsługuje
# out-of-the-box, więc robimy to przez before/after tool callbacks.

_SAFETY_KEY = "_pending_safety"


def _before_tool_cb(tool, args: dict, tool_context) -> Optional[dict]:
    """Strip safety_decision from args and store flag in session state."""
    safety = args.pop("safety_decision", None)
    if safety:
        logger.info("Safety decision received: %s", safety)
        tool_context.state[_SAFETY_KEY] = True
    return None  # continue normal execution


def _after_tool_cb(tool, args: dict, tool_context, tool_response) -> Optional[dict]:
    """Inject safety_acknowledgement into function response if needed."""
    if tool_context.state.get(_SAFETY_KEY, False):
        tool_context.state[_SAFETY_KEY] = False
        if isinstance(tool_response, dict):
            tool_response["safety_acknowledgement"] = "true"
            logger.info("Added safety_acknowledgement to response")
            return tool_response
    return None  # no modification


root_agent = LlmAgent(
    model=CONFIG.computer_use_model,
    name="notebooklm_agent",
    instruction=_build_instruction(),
    tools=[_toolset],
    before_tool_callback=_before_tool_cb,
    after_tool_callback=_after_tool_cb,
)


class NotebookLMAgentSystem:
    """Pełny system agenta NotebookLM z Computer Use.

    Udostępnia:
    - PlaywrightComputer (sterowanie przeglądarką)
    - LlmAgent z ComputerUseToolset
    - Runner do obsługi sesji
    - NotebookLibrary do zarządzania notebookami
    - ConversationStore do zapisu konwersacji
    """

    def __init__(
        self,
        model: Optional[str] = None,
        headless: Optional[bool] = None,
        notebook_url: Optional[str] = None,
    ):
        self.model = model or CONFIG.computer_use_model
        self._headless = headless if headless is not None else CONFIG.headless
        self._notebook_url = notebook_url or CONFIG.default_notebook_url

        # Komponenty
        self.library = NotebookLibrary()
        self.conversations = ConversationStore()
        self.computer: Optional[PlaywrightComputer] = None
        self.agent: Optional[LlmAgent] = None
        self.runner: Optional[Runner] = None
        self._session_service = InMemorySessionService()
        self._initialized = False

    async def initialize(self) -> None:
        """Inicjalizuj agenta i przeglądarkę."""
        if self._initialized:
            return

        # 1. Utwórz i zainicjalizuj PlaywrightComputer
        self.computer = PlaywrightComputer(headless=self._headless)
        await self.computer.initialize()

        # 2. Utwórz ComputerUseToolset
        toolset = ComputerUseToolset(computer=self.computer)

        # 3. Buduj system prompt z informacjami o notebookach
        library_info = self.library.describe_for_prompt()
        full_prompt = f"{NOTEBOOKLM_SYSTEM_PROMPT}\n\n## Biblioteka notebooków\n{library_info}"

        if self._notebook_url:
            full_prompt += f"\n\n## Aktywny notebook\nDomyślny URL: {self._notebook_url}"

        # 4. Utwórz agenta
        self.agent = LlmAgent(
            model=self.model,
            name="notebooklm_agent",
            instruction=full_prompt,
            tools=[toolset],
        )

        # 5. Runner
        self.runner = Runner(
            agent=self.agent,
            app_name="notebooklm_agent",
            session_service=self._session_service,
        )

        self._initialized = True
        logger.info("NotebookLM Agent initialized (model=%s)", self.model)

    async def ensure_logged_in(self) -> bool:
        """Sprawdź czy sesja Google jest aktywna. Jeśli nie — otwórz stronę logowania.

        Returns:
            True jeśli zalogowano, False jeśli użytkownik musi się zalogować ręcznie.
        """
        if not self.computer:
            return False

        # Nawiguj do NotebookLM żeby sprawdzić czy redirect do logowania
        test_url = self._notebook_url or "https://notebooklm.google.com"
        state = await self.computer.navigate(test_url)

        current_url = state.url
        if "accounts.google.com" in current_url:
            logger.info("Not logged in — redirected to Google Sign-in.")
            print("\n⚠️  Nie jesteś zalogowany do Google w tej przeglądarce.")
            print("   Zaloguj się w otwartym oknie przeglądarki,")
            print("   a następnie naciśnij ENTER tutaj.\n")
            # Czekaj aż user się zaloguje
            try:
                input("   [Naciśnij ENTER po zalogowaniu] ")
            except (EOFError, KeyboardInterrupt):
                return False
            # Sprawdź ponownie
            state = await self.computer.navigate(test_url)
            current_url = state.url
            if "accounts.google.com" in current_url:
                print("   ❌ Nadal nie zalogowano. Spróbuj ponownie.")
                return False
            print("   ✅ Zalogowano pomyślnie!")
        else:
            logger.info("Already logged in: %s", current_url[:80])
        return True

    async def ask(
        self,
        question: str,
        session_id: str = "default",
        user_id: str = "user",
        conversation_id: Optional[str] = None,
    ) -> str:
        """Zadaj pytanie — agent nawiguje do NotebookLM i zwraca odpowiedź."""
        if not self._initialized:
            await self.initialize()

        # Sprawdź aktywny notebook
        active = self.library.get_active()
        notebook_url = self._notebook_url
        if active:
            notebook_url = active.url
            self.library.increment_use(active.id)

        # Buduj wiadomość dla agenta
        if notebook_url:
            user_message = (
                f"Otwórz notebook pod adresem {notebook_url} i zadaj pytanie:\n\n{question}\n\n"
                f"Odczytaj i zwróć pełną odpowiedź z NotebookLM."
            )
        else:
            user_message = question

        # Zapisz pytanie
        conv_id = conversation_id or session_id
        self.conversations.save_turn(conv_id, "user", question, notebook_id=active.id if active else "")

        # Uruchom agenta
        session = await self._session_service.get_session(
            app_name="notebooklm_agent",
            user_id=user_id,
            session_id=session_id,
        )
        if session is None:
            session = await self._session_service.create_session(
                app_name="notebooklm_agent",
                user_id=user_id,
                session_id=session_id,
            )

        from google.genai.types import Content, Part
        user_content = Content(role="user", parts=[Part(text=user_message)])

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

        # Zapisz odpowiedź
        if response_text:
            self.conversations.save_turn(conv_id, "assistant", response_text, notebook_id=active.id if active else "")

        return response_text

    async def close(self) -> None:
        """Zamknij przeglądarkę i zwolnij zasoby."""
        if self.computer:
            await self.computer.close()
            self.computer = None
        self._initialized = False
        logger.info("NotebookLM Agent closed.")
