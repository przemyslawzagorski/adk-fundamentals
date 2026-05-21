"""Quick test: verify PlaywrightComputer uses a single-thread executor."""
import sys, asyncio, threading
sys.path.insert(0, r"c:\Users\NBPZAGORSKI\IdeaProjects\spectrum-project")

from notebooklm_agent.computer.playwright_computer import PlaywrightComputer

pc = PlaywrightComputer(headless=True)
print(f"Has _executor: {hasattr(pc, '_executor')}")
print(f"Has _run: {hasattr(pc, '_run')}")
print(f"Executor max_workers: {pc._executor._max_workers}")

async def test():
    tids = []
    def get_tid():
        tids.append(threading.current_thread().ident)
    loop = asyncio.get_running_loop()
    for _ in range(5):
        await loop.run_in_executor(pc._executor, get_tid)
    unique = set(tids)
    print(f"{len(tids)} calls -> {len(unique)} unique thread(s)")
    assert len(unique) == 1, f"Expected 1 thread, got {len(unique)}"
    print("SINGLE THREAD OK")

asyncio.run(test())
print("ALL TESTS PASSED")
