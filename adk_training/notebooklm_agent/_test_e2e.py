"""Szybki test e2e — inicjalizacja agenta + otwarcie NotebookLM."""

import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

from notebooklm_agent.config import CONFIG
from notebooklm_agent.computer.playwright_computer import PlaywrightComputer


async def test_browser():
    print(f"Config:")
    print(f"  Project: {CONFIG.google_cloud_project}")
    print(f"  Model: {CONFIG.computer_use_model}")
    print(f"  Notebook: {CONFIG.default_notebook_url}")
    print(f"  Chrome: {CONFIG.chrome_profile_dir}")
    print(f"  VERTEXAI env: {os.getenv('GOOGLE_GENAI_USE_VERTEXAI', '(not set)')}")
    print()

    # Test 1: Browser launch
    print("=== Test 1: Launching browser ===")
    computer = PlaywrightComputer(headless=False)
    await computer.initialize()
    print("Browser launched OK")

    # Test 2: Navigate to NotebookLM
    print("=== Test 2: Navigate to NotebookLM ===")
    state = await computer.navigate(CONFIG.default_notebook_url)
    print(f"URL: {state.url}")
    print(f"Screenshot size: {len(state.screenshot)} bytes")

    # Test 3: Screenshot
    print("=== Test 3: Take screenshot ===")
    state = await computer.current_state()
    print(f"URL: {state.url}")

    # Save screenshot locally
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_screenshot.png")
    with open(out, "wb") as f:
        f.write(state.screenshot)
    print(f"Screenshot saved: {out}")

    # Wait a bit to see the browser
    print("Waiting 5 seconds (check the browser)...")
    await asyncio.sleep(5)

    print("=== Test 4: ComputerUseToolset creation ===")
    from google.adk.tools.computer_use.computer_use_toolset import ComputerUseToolset
    toolset = ComputerUseToolset(computer=computer)
    tools = await toolset.get_tools()
    print(f"Tools created: {[t.name for t in tools]}")

    print("=== Test 5: LlmAgent creation ===")
    from google.adk.agents import LlmAgent
    agent = LlmAgent(
        model=CONFIG.computer_use_model,
        name="test_agent",
        instruction="Test",
        tools=[toolset],
    )
    print(f"Agent created: {agent.name}, model={CONFIG.computer_use_model}")

    await computer.close()
    print("\nAll tests passed!")


if __name__ == "__main__":
    asyncio.run(test_browser())
