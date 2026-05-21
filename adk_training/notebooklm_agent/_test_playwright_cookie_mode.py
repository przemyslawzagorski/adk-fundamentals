"""Test PlaywrightComputer w trybie cookie-based (headless, bez profilu)."""
import sys, json, asyncio, tempfile, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

from notebooklm_agent.computer.playwright_computer import PlaywrightComputer


FAKE_STORAGE_STATE = {
    "cookies": [
        {
            "name": "COOKIE_A", "value": "val_a", "domain": ".google.com",
            "path": "/", "secure": True, "httpOnly": False,
            "sameSite": "Lax", "expires": 1999999999.0,
        },
        {
            "name": "COOKIE_B", "value": "val_b", "domain": "example.com",
            "path": "/", "secure": False, "httpOnly": True,
            "sameSite": "Strict", "expires": -1,
        },
    ],
    "origins": [],
}


async def test_cookie_mode():
    print("=== Test PlaywrightComputer tryb cookie-based ===\n")

    # Tymczasowy plik storage_state
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(FAKE_STORAGE_STATE, f)
        tmp_path = f.name

    try:
        # --- 1. Initialize ---
        pc = PlaywrightComputer(cookies_path=tmp_path, headless=True)
        await pc.initialize()
        print("[OK] PlaywrightComputer.initialize() — tryb cookie-based")

        assert pc._browser is not None, "Browser nie zostal uruchomiony"
        assert pc._context is not None, "Context nie zostal utworzony"
        assert pc._page is not None, "Page nie zostal utworzony"
        print("[OK] browser, context, page — zainicjalizowane")

        # Tryb cookie-based = nie ma persistent context (BrowserContext, nie PersistentContext)
        ctx_cls = pc._context.__class__.__name__
        print(f"[OK] Context class: {ctx_cls} (brak user_data_dir)")

        # --- 2. Ciasteczka w context ---
        # Playwright sync API wymaga wywołania z dedykowanego wątku greenlet
        ctx_cookies = await pc._run(lambda: pc._context.cookies())
        cookie_names = [c["name"] for c in ctx_cookies]
        print(f"[OK] Ciasteczka wstrzykniete: {cookie_names}")
        assert "COOKIE_A" in cookie_names, f"Brak COOKIE_A w {cookie_names}"
        assert "COOKIE_B" in cookie_names, f"Brak COOKIE_B w {cookie_names}"

        # --- 3. Nawigacja ---
        state = await pc.navigate("about:blank")
        print(f"[OK] navigate(about:blank) — URL: {state.url}")
        assert state.screenshot and len(state.screenshot) > 0
        print(f"[OK] screenshot — {len(state.screenshot)} bytes")

        # --- 4. Screenshot biezacego stanu ---
        state2 = await pc.current_state()
        assert len(state2.screenshot) > 0
        print("[OK] current_state() — screenshot OK")

        # --- 5. save_session (export storage_state) ---
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f2:
            out_path = f2.name
        try:
            await pc.save_session(out_path)
            assert os.path.exists(out_path)
            with open(out_path, encoding="utf-8") as f2:
                exported = json.load(f2)
            assert "cookies" in exported
            exported_count = len(exported["cookies"])
            print(f"[OK] save_session() — {exported_count} ciasteczek wyeksportowanych")
        finally:
            os.unlink(out_path)

        # --- 6. Close ---
        await pc.close()
        assert pc._browser is None
        assert pc._context is None
        assert pc._page is None
        print("[OK] close() — wszystkie zasoby zwolnione")

    finally:
        os.unlink(tmp_path)

    print("\n=== Test PlaywrightComputer cookie-based ZALICZONY ===")


if __name__ == "__main__":
    asyncio.run(test_cookie_mode())
