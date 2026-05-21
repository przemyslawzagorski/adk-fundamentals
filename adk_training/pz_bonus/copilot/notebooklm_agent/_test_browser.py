"""Test #2 — browser launch with profile cookie copy."""

import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

from notebooklm_agent.config import CONFIG
from notebooklm_agent.computer.playwright_computer import PlaywrightComputer


async def test():
    print("=== Test: Browser launch with profile copy ===")
    print(f"Chrome profile: {CONFIG.chrome_profile_dir}")
    print(f"Notebook URL: {CONFIG.default_notebook_url}")

    computer = PlaywrightComputer(headless=False)
    try:
        await computer.initialize()
        print("Browser launched!")

        print("Navigating to NotebookLM...")
        state = await computer.navigate(CONFIG.default_notebook_url)
        print(f"URL: {state.url}")
        print(f"Screenshot: {len(state.screenshot)} bytes")

        # Save screenshot
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_screenshot.png")
        with open(out, "wb") as f:
            f.write(state.screenshot)
        print(f"Screenshot saved: {out}")

        # Wait to see
        print("Waiting 10 seconds (check browser)...")
        await asyncio.sleep(10)

        # Take another screenshot after page settles
        state2 = await computer.current_state()
        out2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_screenshot2.png")
        with open(out2, "wb") as f:
            f.write(state2.screenshot)
        print(f"Screenshot 2 saved: {out2}")
        print(f"Final URL: {state2.url}")

    finally:
        await computer.close()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(test())
