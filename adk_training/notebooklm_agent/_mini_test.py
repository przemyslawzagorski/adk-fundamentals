"""Minimal test."""
import asyncio
import sys
import os

print("Script started", flush=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Importing...", flush=True)
from notebooklm_agent.computer.playwright_computer import PlaywrightComputer
from notebooklm_agent.config import CONFIG
print(f"Import OK, data_dir={CONFIG.data_dir}", flush=True)


async def main():
    print("Creating computer...", flush=True)
    computer = PlaywrightComputer(headless=False)
    print("Initializing...", flush=True)
    try:
        await computer.initialize()
        print("Browser ready!", flush=True)
    except Exception as e:
        print(f"Init error: {e}", flush=True)
        raise
    finally:
        try:
            await computer.close()
        except Exception:
            pass
    print("DONE", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
