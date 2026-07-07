"""PlaywrightComputer — adapter BaseComputer dla ADK Web Tester.

Playwright sync API w dedykowanym wątku (obejście SelectorEventLoop na Windows).
Uproszczona wersja z notebooklm_agent — bez Google auth, bez persistent profile.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import os
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright
from playwright._impl._errors import TargetClosedError

from google.adk.tools.computer_use.base_computer import BaseComputer, ComputerState, ComputerEnvironment

from ..config import CONFIG

logger = logging.getLogger("adk_tester.computer")


class PlaywrightComputer(BaseComputer):
    """BaseComputer z Playwright sync API + asyncio.to_thread().

    Testuje agentów ADK web na localhost — nie wymaga logowania Google.
    """

    def __init__(
        self,
        headless: Optional[bool] = None,
        width: int = 0,
        height: int = 0,
        record_video: Optional[bool] = None,
    ):
        self._headless = headless if headless is not None else CONFIG.headless
        self._width = width or CONFIG.screen_width
        self._height = height or CONFIG.screen_height
        self._record_video = record_video if record_video is not None else CONFIG.record_video

        self._pw: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._lock = threading.Lock()
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="pw-sync"
        )
        self._video_path: Optional[str] = None

    async def _run(self, fn, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, fn, *args)

    # ── Lifecycle ───────────────────────────────────────────────────────────

    def _sync_initialize(self) -> None:
        with self._lock:
            if self._page is not None:
                return

            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(
                headless=self._headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-first-run",
                ],
            )
            ctx_kwargs = dict(
                viewport={"width": self._width, "height": self._height},
                locale="pl-PL",
                timezone_id="Europe/Warsaw",
            )
            if self._record_video:
                ctx_kwargs["record_video_dir"] = CONFIG.videos_dir
                ctx_kwargs["record_video_size"] = {
                    "width": self._width, "height": self._height,
                }
                logger.info("Video recording ENABLED → %s", CONFIG.videos_dir)
            self._context = self._browser.new_context(**ctx_kwargs)
            self._page = self._context.new_page()
            # Navigate to ADK web immediately so agent never sees blank page
            try:
                self._page.goto(CONFIG.adk_web_url, timeout=15000)
                logger.info("Navigated to %s", CONFIG.adk_web_url)
            except Exception as e:
                logger.warning("Could not navigate to %s: %s", CONFIG.adk_web_url, e)
            logger.info("Browser ready (%dx%d, headless=%s)", self._width, self._height, self._headless)

    def _sync_close(self) -> None:
        # Finalize video before closing context
        if self._page and self._record_video:
            try:
                video = self._page.video
                if video:
                    tmp_path = video.path()
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    final_name = f"test_session_{ts}.webm"
                    final_path = str(Path(CONFIG.videos_dir) / final_name)
                    # Video file is finalized after context.close(), so save path for rename
                    self._video_tmp = str(tmp_path)
                    self._video_final = final_path
            except Exception as e:
                logger.warning("Could not get video path: %s", e)
        if self._context:
            try:
                self._context.close()
            except Exception:
                pass
            # Rename temp video to nice name after context closes
            if self._record_video and hasattr(self, "_video_tmp") and self._video_tmp:
                try:
                    if Path(self._video_tmp).exists():
                        shutil.move(self._video_tmp, self._video_final)
                        self._video_path = self._video_final
                        logger.info("Video saved: %s", self._video_path)
                except Exception as e:
                    logger.warning("Could not rename video: %s", e)
                    self._video_path = self._video_tmp
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

    @property
    def video_path(self) -> Optional[str]:
        """Ścieżka do nagranego pliku video (dostępna po close())."""
        return self._video_path

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

    def _relaunch_browser(self) -> None:
        """Relaunch Chromium browser (keeps Playwright instance)."""
        # Close old browser gracefully
        for obj in (self._context, self._browser):
            if obj:
                try:
                    obj.close()
                except Exception:
                    pass
        self._context = None
        self._page = None
        self._browser = self._pw.chromium.launch(
            headless=self._headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-first-run",
            ],
        )
        logger.info("Browser relaunched.")

    def _new_context_and_page(self) -> None:
        """Create a new browser context + page on existing browser."""
        ctx_kwargs = dict(
            viewport={"width": self._width, "height": self._height},
            locale="pl-PL",
            timezone_id="Europe/Warsaw",
        )
        if self._record_video:
            ctx_kwargs["record_video_dir"] = CONFIG.videos_dir
            ctx_kwargs["record_video_size"] = {
                "width": self._width, "height": self._height,
            }
        self._context = self._browser.new_context(**ctx_kwargs)
        self._page = self._context.new_page()
        try:
            self._page.goto(CONFIG.adk_web_url, timeout=15000)
        except Exception:
            pass

    def _browser_is_alive(self) -> bool:
        """Check if the browser process is still running."""
        try:
            return self._browser is not None and self._browser.is_connected()
        except Exception:
            return False

    def _sync_ensure_ready(self) -> Page:
        if self._page is None or not self._browser_is_alive():
            if self._pw:
                if not self._browser_is_alive():
                    logger.warning("Browser is dead, relaunching...")
                    self._relaunch_browser()
                self._new_context_and_page()
                logger.info("Browser context recreated.")
            else:
                self._sync_initialize()
            return self._page
        # Check if existing page is still alive
        try:
            self._page.url
        except Exception:
            logger.warning("Page/context is dead, recovering...")
            if not self._browser_is_alive():
                self._relaunch_browser()
            else:
                # Just close old context
                if self._context:
                    try:
                        self._context.close()
                    except Exception:
                        pass
            self._context = None
            self._page = None
            self._new_context_and_page()
            logger.info("Browser context recreated.")
        return self._page

    def _with_retry(self, fn, *args, max_retries: int = 2):
        """Execute fn with retry on TargetClosedError (browser crash recovery)."""
        for attempt in range(max_retries + 1):
            try:
                return fn(*args)
            except TargetClosedError as e:
                if attempt < max_retries:
                    logger.warning("TargetClosedError in %s, recovering (attempt %d)...", fn.__name__, attempt + 1)
                    self._page = None
                    self._context = None
                    # Browser might be dead too — _sync_ensure_ready will detect and relaunch
                    time.sleep(1)
                else:
                    raise

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

    def get_page_text(self) -> str:
        """Ekstrakcja widocznego tekstu z DOM (do raportów)."""
        page = self._sync_ensure_ready()
        return page.inner_text("body")

    def save_screenshot(self, path: str) -> None:
        """Zapisz screenshot do pliku."""
        page = self._sync_ensure_ready()
        page.screenshot(path=path, type="png")

    # ── BaseComputer async interface ────────────────────────────────────────

    async def environment(self) -> ComputerEnvironment:
        return ComputerEnvironment.ENVIRONMENT_BROWSER

    async def screen_size(self) -> tuple[int, int]:
        return (self._width, self._height)

    async def current_state(self) -> ComputerState:
        return await self._run(self._do_current_state)

    def _do_current_state(self) -> ComputerState:
        def _inner():
            self._sync_ensure_ready()
            return self._sync_current_state()
        return self._with_retry(_inner)

    async def open_web_browser(self) -> ComputerState:
        return await self.current_state()

    async def click_at(self, x: int, y: int) -> ComputerState:
        return await self._run(self._do_click_at, x, y)

    def _do_click_at(self, x: int, y: int) -> ComputerState:
        def _inner():
            page = self._sync_ensure_ready()
            page.mouse.click(x, y)
            self._sync_wait_stable()
            return self._sync_current_state()
        return self._with_retry(_inner)

    async def hover_at(self, x: int, y: int) -> ComputerState:
        return await self._run(self._do_hover_at, x, y)

    def _do_hover_at(self, x: int, y: int) -> ComputerState:
        def _inner():
            page = self._sync_ensure_ready()
            page.mouse.move(x, y)
            time.sleep(0.5)
            return self._sync_current_state()
        return self._with_retry(_inner)

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
        def _inner():
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
        return self._with_retry(_inner)

    async def scroll_document(
        self, direction: Literal["up", "down", "left", "right"]
    ) -> ComputerState:
        return await self._run(self._do_scroll_document, direction)

    def _do_scroll_document(self, direction: str) -> ComputerState:
        def _inner():
            self._sync_ensure_ready()
            dx, dy = self._scroll_delta(direction, 600)
            self._page.mouse.wheel(dx, dy)
            time.sleep(0.5)
            return self._sync_current_state()
        return self._with_retry(_inner)

    async def scroll_at(
        self,
        x: int,
        y: int,
        direction: Literal["up", "down", "left", "right"],
        magnitude: int = 800,
    ) -> ComputerState:
        return await self._run(self._do_scroll_at, x, y, direction, magnitude)

    def _do_scroll_at(self, x: int, y: int, direction: str, magnitude: int) -> ComputerState:
        def _inner():
            page = self._sync_ensure_ready()
            page.mouse.move(x, y)
            pixels = int(magnitude / 1000 * self._height)
            dx, dy = self._scroll_delta(direction, pixels)
            page.mouse.wheel(dx, dy)
            time.sleep(0.5)
            return self._sync_current_state()
        return self._with_retry(_inner)

    async def wait(self, seconds: int) -> ComputerState:
        await asyncio.sleep(seconds)
        return await self._run(self._do_current_state)

    async def go_back(self) -> ComputerState:
        return await self._run(self._do_go_back)

    def _do_go_back(self) -> ComputerState:
        def _inner():
            page = self._sync_ensure_ready()
            page.go_back(timeout=10000)
            self._sync_wait_stable()
            return self._sync_current_state()
        return self._with_retry(_inner)

    async def go_forward(self) -> ComputerState:
        return await self._run(self._do_go_forward)

    def _do_go_forward(self) -> ComputerState:
        def _inner():
            page = self._sync_ensure_ready()
            page.go_forward(timeout=10000)
            self._sync_wait_stable()
            return self._sync_current_state()
        return self._with_retry(_inner)

    async def search(self) -> ComputerState:
        return await self._run(self._do_search)

    def _do_search(self) -> ComputerState:
        def _inner():
            page = self._sync_ensure_ready()
            page.goto("https://www.google.com", timeout=15000)
            self._sync_wait_stable()
            return self._sync_current_state()
        return self._with_retry(_inner)

    async def navigate(self, url: str) -> ComputerState:
        return await self._run(self._do_navigate, url)

    def _do_navigate(self, url: str) -> ComputerState:
        def _inner():
            page = self._sync_ensure_ready()
            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
            except Exception as e:
                if "interrupted by another navigation" in str(e):
                    logger.info("Navigation redirect detected, waiting...")
                else:
                    raise
            self._sync_wait_stable()
            return self._sync_current_state()
        return self._with_retry(_inner)

    async def key_combination(self, keys: list[str]) -> ComputerState:
        return await self._run(self._do_key_combination, keys)

    def _do_key_combination(self, keys: list[str]) -> ComputerState:
        def _inner():
            page = self._sync_ensure_ready()
            combo = "+".join(keys)
            page.keyboard.press(combo)
            time.sleep(0.3)
            return self._sync_current_state()
        return self._with_retry(_inner)

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
