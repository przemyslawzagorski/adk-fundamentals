"""PlaywrightComputer — implementacja BaseComputer z Playwright sync API w wątku.

Na Windows uvicorn (adk web) używa SelectorEventLoop, który nie obsługuje
asyncio.create_subprocess_exec(). Playwright async API tego potrzebuje.
Rozwiązanie: sync_playwright w asyncio.to_thread() — sync API zarządza
własnym procesem wewnętrznie i nie zależy od event loop policy.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import os
import threading
import time
from typing import Literal, Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright

from google.adk.tools.computer_use.base_computer import BaseComputer, ComputerState, ComputerEnvironment

from ..config import CONFIG

logger = logging.getLogger("notebooklm_agent.computer")


class PlaywrightComputer(BaseComputer):
    """Implementacja BaseComputer — Playwright sync API + asyncio.to_thread().

    Wszystkie operacje Playwright wykonywane są synchronicznie w wątku
    thread-pool, co omija problem SelectorEventLoop na Windows.
    """

    def __init__(
        self,
        chrome_profile_dir: Optional[str] = None,
        headless: Optional[bool] = None,
        width: int = 0,
        height: int = 0,
        cdp_url: Optional[str] = None,
        cookies_path: Optional[str] = None,
        use_cookie_auth: Optional[bool] = None,
    ):
        self._chrome_profile_dir = chrome_profile_dir or CONFIG.chrome_profile_dir
        self._headless = headless if headless is not None else CONFIG.headless
        self._width = width or CONFIG.screen_width
        self._height = height or CONFIG.screen_height
        self._cdp_url = cdp_url or os.getenv("CHROME_CDP_URL", "")
        # Cookie-based auth: izolowany BrowserContext + add_cookies, zamiast persistent profile.
        # Jedyny tryb, ktory dziala stabilnie w korporacyjnym srodowisku (BeyondCorp, EDR).
        self._cookies_path = cookies_path if cookies_path is not None else CONFIG.cookies_path
        if use_cookie_auth is None:
            self._use_cookie_auth = CONFIG.use_cookie_auth or bool(cookies_path)
        else:
            self._use_cookie_auth = use_cookie_auth

        self._pw: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._lock = threading.Lock()
        # Dedykowany single-thread executor — Playwright sync API wymaga
        # aby WSZYSTKIE operacje szły na tym samym wątku/greenlet.
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="pw-sync"
        )

    async def _run(self, fn, *args):
        """Run sync function on the dedicated Playwright thread."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, fn, *args)

    # ── Lifecycle ───────────────────────────────────────────────────────────

    def _sync_initialize(self) -> None:
        with self._lock:
            if self._page is not None:
                return

            self._pw = sync_playwright().start()

            if self._cdp_url:
                self._sync_init_cdp()
            elif self._use_cookie_auth:
                self._sync_init_cookies()
            else:
                self._sync_init_profile()

            if self._context.pages:
                self._page = self._context.pages[0]
            else:
                self._page = self._context.new_page()

            logger.info("Browser ready (%dx%d, headless=%s)", self._width, self._height, self._headless)

    def _sync_init_cdp(self) -> None:
        logger.info("Connecting to Chrome via CDP: %s", self._cdp_url)
        self._browser = self._pw.chromium.connect_over_cdp(self._cdp_url)
        contexts = self._browser.contexts
        if contexts:
            self._context = contexts[0]
        else:
            self._context = self._browser.new_context(
                viewport={"width": self._width, "height": self._height},
            )

    def _sync_init_profile(self) -> None:
        # Użyj katalogu profilu Chrome z configu (domyślnie prawdziwy profil Chrome)
        profile_dir = self._chrome_profile_dir
        os.makedirs(profile_dir, exist_ok=True)
        logger.info("Using persistent profile: %s", profile_dir)

        extra_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-first-run",
            "--no-default-browser-check",
        ]

        # Korporacyjne EDR/AV (np. CrowdStrike, Defender ATP) zabija chromium
        # z ms-playwright (proces ginie z exit 0x80000003 STATUS_BREAKPOINT
        # od razu po launchu). Workaround: uzyj zainstalowanego, podpisanego
        # Chrome przez channel="chrome". Override:
        #   PLAYWRIGHT_BROWSER_CHANNEL=msedge   -> Edge
        #   PLAYWRIGHT_BROWSER_CHANNEL=         -> bundled chromium (gdy AV pozwala)
        channel = os.getenv("PLAYWRIGHT_BROWSER_CHANNEL", "chrome").strip()
        launch_kwargs: dict = {
            "user_data_dir": profile_dir,
            "headless": self._headless,
            "viewport": {"width": self._width, "height": self._height},
            "args": extra_args,
            "locale": "pl-PL",
            "timezone_id": "Europe/Warsaw",
        }
        if channel:
            launch_kwargs["channel"] = channel
            logger.info("Launching Playwright with channel=%s", channel)
        else:
            logger.info("Launching Playwright with bundled chromium")

        self._context = self._pw.chromium.launch_persistent_context(**launch_kwargs)

    def _sync_init_cookies(self) -> None:
        """Tryb cookie-based: izolowany BrowserContext + add_cookies.

        Eliminuje konflikty z zajetym profilem Chrome (SingletonLock),
        nie wymaga persistent user-data-dir, dziala na maszynach z BeyondCorp.
        Cookies pochodza z `~/.notebooklm-agent/cookies.json` (Playwright storage_state).
        Wygeneruj plik: python -m notebooklm_agent.export_via_devtools
        """
        from ..cookie_manager import load_cookies_from_storage_state

        cookies_path = self._cookies_path
        logger.info("Cookie-based mode: %s", cookies_path)

        if not os.path.exists(cookies_path):
            raise FileNotFoundError(
                f"Brak pliku cookies: {cookies_path}\n"
                f"Wygeneruj go: python -m notebooklm_agent.export_via_devtools"
            )

        cookies = load_cookies_from_storage_state(cookies_path)

        # Korporacyjny EDR zabija ms-playwright chromium (exit 0x80000003).
        # Workaround: channel="chrome" -> uzywamy zainstalowanego, podpisanego Chrome.
        channel = os.getenv("PLAYWRIGHT_BROWSER_CHANNEL", "chrome").strip()
        launch_kwargs: dict = {
            "headless": self._headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
            ],
        }
        if channel:
            launch_kwargs["channel"] = channel
            logger.info("Launching Playwright with channel=%s", channel)

        self._browser = self._pw.chromium.launch(**launch_kwargs)
        self._context = self._browser.new_context(
            viewport={"width": self._width, "height": self._height},
            locale="pl-PL",
            timezone_id="Europe/Warsaw",
        )
        self._context.add_cookies(cookies)
        logger.info("Wstrzyknieto %d ciasteczek do BrowserContext", len(cookies))

    def _sync_save_session(self, out_path: str) -> None:
        if self._context is None:
            raise RuntimeError("Brak aktywnego context")
        os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
        self._context.storage_state(path=out_path)
        logger.info("Storage state zapisany: %s", out_path)

    async def save_session(self, out_path: str) -> None:
        """Eksportuj biezacy stan ciasteczek/sesji do storage_state JSON."""
        await self._run(self._sync_save_session, out_path)

    def _sync_close(self) -> None:
        if self._context:
            try:
                self._context.close()
            except Exception:
                pass
            self._context = None
            self._page = None
        if self._browser:
            try:
                self._browser.close()
            except Exception:
                pass
            self._browser = None
        if self._pw:
            try:
                self._pw.stop()
            except Exception:
                pass
            self._pw = None
        logger.info("Browser closed.")

    async def initialize(self) -> None:
        if self._page is not None:
            return
        await self._run(self._sync_initialize)

    async def close(self) -> None:
        await self._run(self._sync_close)

    # ── Sync helpers ────────────────────────────────────────────────────────

    def _sync_current_state(self) -> ComputerState:
        screenshot = self._page.screenshot(type="png")
        return ComputerState(screenshot=screenshot, url=self._page.url)

    def _sync_wait_stable(self, timeout_ms: int = 3000) -> None:
        try:
            self._page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        except Exception:
            pass
        time.sleep(0.5)

    def _sync_ensure_ready(self) -> Page:
        if self._page is None:
            self._sync_initialize()
        return self._page

    @staticmethod
    def _scroll_delta(direction: str, magnitude: int) -> tuple[int, int]:
        if direction == "down":
            return (0, magnitude)
        elif direction == "up":
            return (0, -magnitude)
        elif direction == "right":
            return (magnitude, 0)
        elif direction == "left":
            return (-magnitude, 0)
        return (0, 0)

    # ── BaseComputer async interface (delegates to sync in thread) ─────────

    async def environment(self) -> ComputerEnvironment:
        return ComputerEnvironment.ENVIRONMENT_BROWSER

    async def screen_size(self) -> tuple[int, int]:
        return (self._width, self._height)

    async def current_state(self) -> ComputerState:
        return await self._run(self._do_current_state)

    def _do_current_state(self) -> ComputerState:
        self._sync_ensure_ready()
        return self._sync_current_state()

    async def open_web_browser(self) -> ComputerState:
        return await self.current_state()

    async def click_at(self, x: int, y: int) -> ComputerState:
        return await self._run(self._do_click_at, x, y)

    def _do_click_at(self, x: int, y: int) -> ComputerState:
        page = self._sync_ensure_ready()
        page.mouse.click(x, y)
        self._sync_wait_stable()
        return self._sync_current_state()

    async def hover_at(self, x: int, y: int) -> ComputerState:
        return await self._run(self._do_hover_at, x, y)

    def _do_hover_at(self, x: int, y: int) -> ComputerState:
        page = self._sync_ensure_ready()
        page.mouse.move(x, y)
        time.sleep(0.5)
        return self._sync_current_state()

    async def type_text_at(
        self,
        x: int,
        y: int,
        text: str,
        press_enter: bool = True,
        clear_before_typing: bool = True,
    ) -> ComputerState:
        return await self._run(
            self._do_type_text_at, x, y, text, press_enter, clear_before_typing
        )

    def _do_type_text_at(
        self, x: int, y: int, text: str, press_enter: bool, clear_before_typing: bool
    ) -> ComputerState:
        page = self._sync_ensure_ready()
        page.mouse.click(x, y)
        time.sleep(0.2)
        if clear_before_typing:
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            time.sleep(0.1)
        page.keyboard.type(text, delay=20)
        if press_enter:
            time.sleep(0.3)
            page.keyboard.press("Enter")
        self._sync_wait_stable()
        return self._sync_current_state()

    async def scroll_document(
        self, direction: Literal["up", "down", "left", "right"]
    ) -> ComputerState:
        return await self._run(self._do_scroll_document, direction)

    def _do_scroll_document(self, direction: str) -> ComputerState:
        self._sync_ensure_ready()
        dx, dy = self._scroll_delta(direction, 600)
        self._page.mouse.wheel(dx, dy)
        time.sleep(0.5)
        return self._sync_current_state()

    async def scroll_at(
        self,
        x: int,
        y: int,
        direction: Literal["up", "down", "left", "right"],
        magnitude: int = 800,
    ) -> ComputerState:
        return await self._run(self._do_scroll_at, x, y, direction, magnitude)

    def _do_scroll_at(self, x: int, y: int, direction: str, magnitude: int) -> ComputerState:
        page = self._sync_ensure_ready()
        page.mouse.move(x, y)
        pixels = int(magnitude / 1000 * self._height)
        dx, dy = self._scroll_delta(direction, pixels)
        page.mouse.wheel(dx, dy)
        time.sleep(0.5)
        return self._sync_current_state()

    async def wait(self, seconds: int) -> ComputerState:
        await asyncio.sleep(seconds)
        return await self._run(self._do_current_state)

    async def go_back(self) -> ComputerState:
        return await self._run(self._do_go_back)

    def _do_go_back(self) -> ComputerState:
        page = self._sync_ensure_ready()
        page.go_back(timeout=10000)
        self._sync_wait_stable()
        return self._sync_current_state()

    async def go_forward(self) -> ComputerState:
        return await self._run(self._do_go_forward)

    def _do_go_forward(self) -> ComputerState:
        page = self._sync_ensure_ready()
        page.go_forward(timeout=10000)
        self._sync_wait_stable()
        return self._sync_current_state()

    async def search(self) -> ComputerState:
        return await self._run(self._do_search)

    def _do_search(self) -> ComputerState:
        page = self._sync_ensure_ready()
        page.goto("https://www.google.com", timeout=15000)
        self._sync_wait_stable()
        return self._sync_current_state()

    async def navigate(self, url: str) -> ComputerState:
        return await self._run(self._do_navigate, url)

    def _do_navigate(self, url: str) -> ComputerState:
        page = self._sync_ensure_ready()
        try:
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
        except Exception as e:
            # Google often redirects (e.g. ?pli=1) which interrupts navigation.
            # If the page landed somewhere valid, that's fine.
            if "interrupted by another navigation" in str(e):
                logger.info("Navigation redirect detected, waiting for page to settle...")
            else:
                raise
        self._sync_wait_stable()
        return self._sync_current_state()

    async def key_combination(self, keys: list[str]) -> ComputerState:
        return await self._run(self._do_key_combination, keys)

    def _do_key_combination(self, keys: list[str]) -> ComputerState:
        page = self._sync_ensure_ready()
        combo = "+".join(keys)
        page.keyboard.press(combo)
        time.sleep(0.3)
        return self._sync_current_state()

    async def drag_and_drop(
        self, x: int, y: int, destination_x: int, destination_y: int
    ) -> ComputerState:
        return await self._run(
            self._do_drag_and_drop, x, y, destination_x, destination_y
        )

    def _do_drag_and_drop(
        self, x: int, y: int, destination_x: int, destination_y: int
    ) -> ComputerState:
        page = self._sync_ensure_ready()
        page.mouse.move(x, y)
        page.mouse.down()
        time.sleep(0.1)
        steps = 10
        for i in range(1, steps + 1):
            ix = x + (destination_x - x) * i // steps
            iy = y + (destination_y - y) * i // steps
            page.mouse.move(ix, iy)
            time.sleep(0.02)
        page.mouse.up()
        self._sync_wait_stable()
        return self._sync_current_state()

    # ── Legacy compatibility ────────────────────────────────────────────────

    def _ensure_page(self) -> Page:
        """Sync access to page (used by agent.py ensure_logged_in)."""
        if self._page is None:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        return self._page
