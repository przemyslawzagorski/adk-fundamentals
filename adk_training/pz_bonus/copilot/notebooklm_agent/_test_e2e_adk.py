"""E2E test: Playwright browser + ADK agent import.

Testuje cały flow:
1. PlaywrightComputer z dedykowanym profilem — launch, navigate, screenshot, close
2. Import root_agent z callbacks
3. Symulacja ADK callback flow z prawdziwym State
"""
import asyncio
import os
import sys
import tempfile

# Upewnij się, że importujemy z właściwego katalogu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASSED = 0
FAILED = 0


def ok(name: str):
    global PASSED
    PASSED += 1
    print(f"  [PASS] {name}")


def fail(name: str, err: str):
    global FAILED
    FAILED += 1
    print(f"  [FAIL] {name}: {err}")


# ─── Test 1: Playwright browser lifecycle ──────────────────────────────────

async def test_browser_lifecycle():
    print("\n=== Test 1: Browser lifecycle ===")
    from notebooklm_agent.computer.playwright_computer import PlaywrightComputer

    # Dedykowany temp profil, żeby nie kolidować z niczym
    profile_dir = tempfile.mkdtemp(prefix="nlm-test-profile-")
    computer = PlaywrightComputer(
        chrome_profile_dir=profile_dir,
        headless=True,  # headless w testach
        width=1280,
        height=720,
    )

    # 1a. Initialize
    try:
        await computer.initialize()
        ok("initialize")
    except Exception as e:
        fail("initialize", str(e))
        return  # Reszta nie ma sensu

    # 1b. Screen size
    try:
        w, h = await computer.screen_size()
        assert w == 1280 and h == 720, f"got {w}x{h}"
        ok(f"screen_size ({w}x{h})")
    except Exception as e:
        fail("screen_size", str(e))

    # 1c. Navigate to NotebookLM
    try:
        state = await computer.navigate("https://notebooklm.google.com")
        assert state.screenshot is not None and len(state.screenshot) > 1000, \
            f"screenshot too small: {len(state.screenshot)} bytes"
        assert state.url is not None and len(state.url) > 0
        ok(f"navigate (url={state.url[:60]}..., screenshot={len(state.screenshot)} bytes)")
    except Exception as e:
        fail("navigate", str(e))

    # 1d. Current state
    try:
        state = await computer.current_state()
        assert state.screenshot is not None
        ok(f"current_state ({len(state.screenshot)} bytes)")
    except Exception as e:
        fail("current_state", str(e))

    # 1e. Click (should not crash)
    try:
        state = await computer.click_at(100, 100)
        assert state.screenshot is not None
        ok("click_at")
    except Exception as e:
        fail("click_at", str(e))

    # 1f. Close
    try:
        await computer.close()
        ok("close")
    except Exception as e:
        fail("close", str(e))

    # 1g. Re-init after close (lazy init)
    try:
        await computer.initialize()
        state = await computer.current_state()
        assert state.screenshot is not None
        ok("re-initialize after close")
        await computer.close()
    except Exception as e:
        fail("re-initialize after close", str(e))


# ─── Test 2: ADK root_agent import + callbacks ───────────────────────────

def test_adk_agent_import():
    print("\n=== Test 2: ADK agent import ===")

    try:
        from notebooklm_agent.agent import root_agent, _before_tool_cb, _after_tool_cb

        assert root_agent.name == "notebooklm_agent", f"unexpected name: {root_agent.name}"
        assert "computer-use" in root_agent.model, f"unexpected model: {root_agent.model}"
        ok(f"root_agent import (name={root_agent.name}, model={root_agent.model})")
    except Exception as e:
        fail("root_agent import", str(e))
        return

    # Test callbacks z prawdziwym ADK State
    try:
        from google.adk.sessions.state import State

        # 2a. before_tool_cb — bez safety
        class FakeTool:
            name = "click_at"

        class FakeToolContext:
            def __init__(self):
                self.state = State(value={}, delta={})

        ctx = FakeToolContext()
        r = _before_tool_cb(tool=FakeTool(), args={"x": 1, "y": 2}, tool_context=ctx)
        assert r is None, f"expected None, got {r}"
        ok("before_tool_cb (no safety) -> None")

        # 2b. before_tool_cb — z safety_decision
        ctx = FakeToolContext()
        args = {"x": 1, "safety_decision": "approved"}
        r = _before_tool_cb(tool=FakeTool(), args=args, tool_context=ctx)
        assert r is None
        assert ctx.state.get("_pending_safety") is True
        assert "safety_decision" not in args, "safety_decision should be popped"
        ok("before_tool_cb (with safety) -> state set")

        # 2c. after_tool_cb — z pending safety
        r = _after_tool_cb(
            tool=FakeTool(), args={}, tool_context=ctx,
            tool_response={"img": "screenshot_data"}
        )
        assert r is not None
        assert r.get("safety_acknowledgement") == "true"
        assert r.get("img") == "screenshot_data"
        ok("after_tool_cb (pending safety) -> acknowledgement added")

        # 2d. after_tool_cb — bez pending safety
        ctx2 = FakeToolContext()
        r = _after_tool_cb(
            tool=FakeTool(), args={}, tool_context=ctx2,
            tool_response={"img": "data"}
        )
        assert r is None
        ok("after_tool_cb (no safety) -> None passthrough")

    except Exception as e:
        fail("callbacks", str(e))
        import traceback
        traceback.print_exc()


# ─── Test 3: Config defaults ─────────────────────────────────────────────

def test_config_defaults():
    print("\n=== Test 3: Config defaults ===")
    from notebooklm_agent.config import CONFIG

    try:
        # Profile dir should NOT be Chrome User Data (that's locked)
        assert "Google\\Chrome\\User Data" not in CONFIG.chrome_profile_dir, \
            f"DANGER: profile dir points to Chrome User Data: {CONFIG.chrome_profile_dir}"
        assert "browser-profile" in CONFIG.chrome_profile_dir or ".notebooklm-agent" in CONFIG.chrome_profile_dir
        ok(f"chrome_profile_dir = {CONFIG.chrome_profile_dir}")
    except Exception as e:
        fail("chrome_profile_dir", str(e))

    try:
        assert CONFIG.google_cloud_location == "global"
        ok(f"location = {CONFIG.google_cloud_location}")
    except Exception as e:
        fail("location", str(e))

    try:
        assert "computer-use" in CONFIG.computer_use_model
        ok(f"model = {CONFIG.computer_use_model}")
    except Exception as e:
        fail("model", str(e))


# ─── Main ────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("NotebookLM Agent V2 — E2E Test Suite")
    print("=" * 60)

    test_config_defaults()
    test_adk_agent_import()
    asyncio.run(test_browser_lifecycle())

    print("\n" + "=" * 60)
    print(f"Results: {PASSED} passed, {FAILED} failed")
    print("=" * 60)

    if FAILED > 0:
        sys.exit(1)
    print("\nALL TESTS PASSED!")


if __name__ == "__main__":
    main()
