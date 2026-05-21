"""
Health check + config validator.

Uruchom:  python health_check.py
Sprawdza:
  - SDK zainstalowane
  - CLI auggie dostępne (which)
  - Auth skonfigurowany (session.json LUB env)
  - Workspace path istnieje
  - Model zdefiniowany
  - (opcjonalnie) ping Auggie z trywialnym promptem

Exit code 0 = healthy, 1 = problemy.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import sys

from dotenv import load_dotenv

_HERE = pathlib.Path(__file__).parent
load_dotenv(_HERE / ".env")
load_dotenv(_HERE.parent / ".env", override=False)


def _check(name: str, ok: bool, detail: str = "") -> dict:
    return {"check": name, "ok": ok, "detail": detail}


def run_checks(*, ping: bool = False) -> tuple[list[dict], bool]:
    results: list[dict] = []

    # 1. SDK
    try:
        import auggie_sdk  # noqa: F401
        results.append(_check("auggie_sdk_installed", True, getattr(auggie_sdk, "__version__", "unknown")))
    except ImportError as e:
        results.append(_check("auggie_sdk_installed", False, str(e)))

    # 2. CLI
    cli = None
    for name in ("auggie.cmd", "auggie.exe", "auggie"):
        if (p := shutil.which(name)):
            cli = p
            break
    results.append(_check("auggie_cli_found", cli is not None, cli or "not in PATH"))

    # 3. Auth
    has_session_env = bool(os.getenv("AUGMENT_SESSION_AUTH"))
    session_file = pathlib.Path.home() / ".augment" / "session.json"
    has_session_file = session_file.exists()
    has_api_key = bool(os.getenv("AUGMENT_API_KEY"))
    auth_ok = has_session_env or has_session_file or has_api_key
    detail = []
    if has_session_env: detail.append("env:AUGMENT_SESSION_AUTH")
    if has_session_file:
        try:
            data = json.loads(session_file.read_text(encoding="utf-8"))
            scopes = data.get("scopes", [])
            detail.append(f"file:~/.augment/session.json (scopes={scopes})")
            if not any(s in scopes for s in ("write", "read")):
                auth_ok = False
                detail.append("WARNING: session has no read/write scopes")
        except Exception as e:  # noqa: BLE001
            detail.append(f"file:invalid ({e})")
            auth_ok = False
    if has_api_key: detail.append("env:AUGMENT_API_KEY")
    results.append(_check("auth_configured", auth_ok, "; ".join(detail) or "NO AUTH FOUND"))

    # 4. Workspace
    ws = pathlib.Path(os.getenv("AUGGIE_WORKSPACE", str(_HERE)))
    results.append(_check("workspace_exists", ws.exists(), str(ws)))

    # 5. Model
    model = os.getenv("AUGGIE_MODEL", "sonnet4.5")
    results.append(_check("model_configured", True, model))

    # 6. ADK
    try:
        import google.adk  # noqa: F401
        results.append(_check("google_adk_installed", True, ""))
    except ImportError as e:
        results.append(_check("google_adk_installed", False, str(e)))

    # 7. Optional ping
    if ping:
        try:
            from auggie_factory import auggie_call
            with auggie_call("health_ping", extra_cli=["--quiet", "--max-turns", "1"]) as a:
                out = a.run("Reply with the single word: pong", return_type=str)
            ok = "pong" in out.lower()
            results.append(_check("auggie_ping", ok, out[:80]))
        except Exception as e:  # noqa: BLE001
            results.append(_check("auggie_ping", False, f"{type(e).__name__}: {e}"))

    healthy = all(r["ok"] for r in results)
    return results, healthy


def main() -> int:
    ping = "--ping" in sys.argv
    results, healthy = run_checks(ping=ping)

    print("\n" + "=" * 60)
    print(f"HEALTH CHECK — module_23 ({'HEALTHY' if healthy else 'UNHEALTHY'})")
    print("=" * 60)
    for r in results:
        mark = "[OK]" if r["ok"] else "[FAIL]"
        print(f"  {mark:6} {r['check']:30} {r['detail']}")
    print("=" * 60 + "\n")
    return 0 if healthy else 1


if __name__ == "__main__":
    sys.exit(main())
