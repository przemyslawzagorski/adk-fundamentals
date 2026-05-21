"""Pełny test — browser + nawigacja do NotebookLM."""
import asyncio
import sys
import os

print("Script started", flush=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notebooklm_agent.computer.playwright_computer import PlaywrightComputer
from notebooklm_agent.config import CONFIG


async def main():
    computer = PlaywrightComputer(headless=False)
    try:
        print("Initializing browser...", flush=True)
        await computer.initialize()
        print("Browser ready!", flush=True)

        url = CONFIG.default_notebook_url
        print(f"Navigating to: {url}", flush=True)
        state = await computer.navigate(url)
        print(f"Current URL: {state.url}", flush=True)
        print(f"Screenshot: {len(state.screenshot)} bytes", flush=True)

        # Save screenshot
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_nav_screenshot.png")
        with open(out, "wb") as f:
            f.write(state.screenshot)
        print(f"Screenshot saved: {out}", flush=True)

        # Wait and take second screenshot
        print("Waiting 8s for page to load...", flush=True)
        await asyncio.sleep(8)
        state2 = await computer.current_state()
        out2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_nav_screenshot2.png")
        with open(out2, "wb") as f:
            f.write(state2.screenshot)
        print(f"Screenshot 2: {state2.url}", flush=True)
        print(f"Screenshot 2 saved: {out2}", flush=True)

        # Test ComputerUseToolset
        print("Creating ComputerUseToolset...", flush=True)
        from google.adk.tools.computer_use.computer_use_toolset import ComputerUseToolset
        toolset = ComputerUseToolset(computer=computer)
        tools = await toolset.get_tools()
        tool_names = [t.name for t in tools]
        print(f"Tools ({len(tools)}): {tool_names}", flush=True)

    finally:
        await computer.close()
    print("DONE", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
