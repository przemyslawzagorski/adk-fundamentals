"""Playwright executor — runs scenario steps and emits live events.

Designed for SSE streaming: each step yields an `event` dict via the
`on_event` async callback. Steps are tiny declarative DSL described in
`attack_library.py`. Failed *security expectations* become FINDINGS;
runtime errors become step ERRORS (and abort the scenario).

Playwright is imported lazily so module imports work even when it is not
installed; the runner will then return a clear error from `available()`.
"""
from __future__ import annotations

import asyncio
import logging
import os
import pathlib
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .config import AuditConfig
from .auth import AuthContext
from .dsl import ALLOWED_ACTIONS, DSLValidationError, validate_scenario
from .safety import RateLimiter, assert_url_allowed

logger = logging.getLogger(__name__)


EventFn = Callable[[Dict[str, Any]], Awaitable[None]]


def available() -> Dict[str, Any]:
    """Return install status for Playwright Python + browsers."""
    info: Dict[str, Any] = {"installed": False, "version": None, "browsers_ok": False, "error": None}
    try:
        import playwright  # type: ignore
        info["installed"] = True
        info["version"] = getattr(playwright, "__version__", "unknown")
        # Browsers presence isn't trivially detectable; we trust install
        info["browsers_ok"] = True
    except Exception as e:  # pragma: no cover
        info["error"] = f"Playwright is not installed: {e}. Run: pip install playwright && playwright install chromium"
    return info


@dataclass
class StepEvidence:
    screenshots: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class Finding:
    title: str
    severity: str  # critical | high | medium | low | info
    scenario_id: str = ""
    owasp: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    repro_steps: List[Dict] = field(default_factory=list)


@dataclass
class ScenarioResult:
    id: str
    name: str
    owasp: str
    severity: str
    passed: bool = True
    error: Optional[str] = None
    findings: List[Finding] = field(default_factory=list)
    duration_s: float = 0.0
    video_path: Optional[str] = None
    har_path: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)


# ----------------------------- helpers ---------------------------------------


async def _emit(on_event: Optional[EventFn], **kw: Any) -> None:
    if on_event is None:
        return
    kw.setdefault("ts", time.time())
    try:
        await on_event(kw)
    except Exception:
        logger.exception("on_event handler raised; swallowing")


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "_", s.lower())[:64]


# ----------------------------- runner ----------------------------------------


async def run_scenario(
    scenario: Dict,
    cfg: AuditConfig,
    rate_limiter: RateLimiter,
    run_id: str,
    on_event: Optional[EventFn] = None,
    auth: Optional[AuthContext] = None,
) -> ScenarioResult:
    """Run a single declarative scenario in a fresh browser context with video."""
    res = ScenarioResult(
        id=scenario["id"],
        name=scenario["name"],
        owasp=scenario.get("owasp", ""),
        severity=scenario.get("severity", "info"),
    )
    started = time.perf_counter()

    # Strict DSL validation up-front — fail fast on hallucinated actions.
    try:
        validate_scenario(scenario)
    except DSLValidationError as e:
        res.passed = False
        res.error = f"DSL validation failed: {e}"
        await _emit(on_event, type="error", scenario=scenario.get("id"), message=res.error)
        res.duration_s = time.perf_counter() - started
        return res

    avail = available()
    if not avail["installed"]:
        res.passed = False
        res.error = avail["error"]
        await _emit(on_event, type="error", scenario=scenario["id"], message=avail["error"])
        res.duration_s = time.perf_counter() - started
        return res

    from playwright.async_api import async_playwright  # local import (lazy)

    artifacts_dir = cfg.artifacts_dir / run_id / _slug(scenario["id"])
    video_dir = artifacts_dir / "video"
    screenshots_dir = artifacts_dir / "screens"
    video_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    har_path = artifacts_dir / "trace.har"

    await _emit(on_event, type="scenario_started", scenario=scenario["id"], name=scenario["name"])

    last_response_headers: Dict[str, str] = {}
    page_html_cache: str = ""

    try:
        async with async_playwright() as pw:
            browser_factory = getattr(pw, cfg.browser, pw.chromium)
            browser = await browser_factory.launch(headless=cfg.headless)
            try:
                context_kwargs: Dict[str, Any] = {
                    "viewport": {"width": cfg.viewport_width, "height": cfg.viewport_height},
                    "user_agent": "AuditOps/0.1 Playwright Audit Bot",
                    "ignore_https_errors": True,
                    "record_har_path": str(har_path),
                    "record_har_omit_content": True,
                }
                if cfg.record_video:
                    context_kwargs["record_video_dir"] = str(video_dir)
                    context_kwargs["record_video_size"] = {
                        "width": cfg.viewport_width, "height": cfg.viewport_height,
                    }
                # Auth context: extra HTTP headers + basic auth
                if auth:
                    if auth.headers:
                        context_kwargs["extra_http_headers"] = dict(auth.headers)
                    if auth.basic_auth:
                        u, p = auth.basic_auth
                        context_kwargs["http_credentials"] = {"username": u, "password": p}
                context = await browser.new_context(**context_kwargs)
                # Cookies must be added after context creation
                if auth and auth.cookies:
                    try:
                        await context.add_cookies(auth.cookies)
                    except Exception as e:
                        logger.warning("failed to add auth cookies: %s", e)
                context.set_default_navigation_timeout(cfg.nav_timeout_ms)
                context.set_default_timeout(cfg.action_timeout_ms)
                page = await context.new_page()

                # Capture last response headers per navigation for header assertions
                async def _on_response(response):
                    nonlocal last_response_headers
                    try:
                        if response.url == page.url or response.frame == page.main_frame:
                            last_response_headers = dict(response.headers)
                    except Exception:
                        pass

                page.on("response", lambda r: asyncio.create_task(_on_response(r)))

                for idx, step in enumerate(scenario.get("steps", [])):
                    if idx >= cfg.max_steps_per_scenario:
                        await _emit(on_event, type="step_skipped", scenario=scenario["id"],
                                    reason="max_steps_per_scenario reached")
                        break
                    await rate_limiter.wait()
                    action = step.get("action")
                    await _emit(on_event, type="step_started", scenario=scenario["id"],
                                step_idx=idx, action=action)

                    try:
                        # ---------------- navigation / interaction ---------------
                        if action == "goto":
                            assert_url_allowed(step["url"], cfg)
                            await page.goto(step["url"], wait_until=step.get("wait_until", "load"))
                            try:
                                page_html_cache = await page.content()
                            except Exception:
                                page_html_cache = ""

                        elif action == "fill":
                            await page.fill(step["selector"], step.get("value", ""))
                        elif action == "click":
                            await page.click(step["selector"])
                        elif action == "press":
                            await page.keyboard.press(step.get("key", "Enter"))
                        elif action == "wait_for":
                            await page.wait_for_selector(step["selector"], timeout=step.get("timeout", 5000))
                        elif action == "wait_for_load_state":
                            await page.wait_for_load_state(step.get("state", "networkidle"))
                        elif action == "fetch_url":
                            assert_url_allowed(step["url"], cfg)
                            r = await context.request.get(step["url"])
                            if r.status == 200 and "fail_finding" in step:
                                _add_finding(res, scenario, step["fail_finding"],
                                             evidence={"url": step["url"], "status": r.status})
                                await _emit_finding(on_event, scenario["id"], step["fail_finding"])
                        elif action == "screenshot":
                            name = step.get("name") or f"shot_{idx}"
                            shot = screenshots_dir / f"{idx:02d}_{_slug(name)}.png"
                            await page.screenshot(path=str(shot), full_page=False)
                            res.screenshots.append(str(shot))
                        elif action == "eval":
                            value = await page.evaluate(step.get("script", "() => null"))
                            await _emit(on_event, type="eval_result", scenario=scenario["id"],
                                        value=str(value)[:200])
                        elif action == "note":
                            await _emit(on_event, type="note", scenario=scenario["id"],
                                        message=step.get("message", ""))

                        # ----------------- assertions / findings -----------------
                        elif action == "expect_status":
                            # We rely on last_response_headers via response handler — no direct status here.
                            # If `equals_any` provided, treat 4xx/5xx differently
                            allowed = step.get("equals_any") or [step.get("equals", 200)]
                            cur = page.url
                            r = await context.request.get(cur)
                            if r.status not in allowed and "fail_finding" in step:
                                _add_finding(res, scenario, step["fail_finding"],
                                             evidence={"url": cur, "status": r.status, "expected": allowed})
                                await _emit_finding(on_event, scenario["id"], step["fail_finding"])
                        elif action == "expect_header":
                            present = bool(last_response_headers.get(step["name"].lower())
                                           or last_response_headers.get(step["name"]))
                            ok = present if step.get("present", True) else not present
                            if not ok and "fail_finding" in step:
                                _add_finding(res, scenario, step["fail_finding"],
                                             evidence={"header": step["name"], "present": present})
                                await _emit_finding(on_event, scenario["id"], step["fail_finding"])
                        elif action == "expect_text":
                            html = page_html_cache or await page.content()
                            page_html_cache = html
                            contains = step.get("contains", "")
                            present = contains in html
                            negate = step.get("negate", False)
                            ok = (not present) if negate else present
                            if not ok and "fail_finding" in step:
                                _add_finding(res, scenario, step["fail_finding"],
                                             evidence={"contains": contains, "negate": negate, "found": present})
                                await _emit_finding(on_event, scenario["id"], step["fail_finding"])
                        elif action == "expect_origin":
                            from urllib.parse import urlparse
                            cur = urlparse(page.url)
                            actual_origin = f"{cur.scheme}://{cur.netloc}"
                            if actual_origin != step["equals"] and "fail_finding" in step:
                                _add_finding(res, scenario, step["fail_finding"],
                                             evidence={"expected_origin": step["equals"], "actual": actual_origin})
                                await _emit_finding(on_event, scenario["id"], step["fail_finding"])
                        elif action == "expect_frame_ancestors_or_xfo":
                            csp = (last_response_headers.get("content-security-policy", "")).lower()
                            xfo = (last_response_headers.get("x-frame-options", "")).lower()
                            ok = "frame-ancestors" in csp or xfo in ("deny", "sameorigin")
                            if not ok and "fail_finding" in step:
                                _add_finding(res, scenario, step["fail_finding"],
                                             evidence={"x-frame-options": xfo, "csp_has_fa": "frame-ancestors" in csp})
                                await _emit_finding(on_event, scenario["id"], step["fail_finding"])
                        elif action == "expect_cookies_secure":
                            cookies = await context.cookies()
                            bad = [c["name"] for c in cookies
                                   if not c.get("secure") or not c.get("httpOnly")]
                            if bad and "fail_finding" in step:
                                f = dict(step["fail_finding"])
                                f["title"] = f.get("title") + f" ({', '.join(bad[:3])})"
                                _add_finding(res, scenario, f,
                                             evidence={"insecure_cookies": bad})
                                await _emit_finding(on_event, scenario["id"], f)
                        elif action == "expect_cors_open":
                            probe = step.get("probe_origin", "https://attacker.example.test")
                            r = await context.request.get(page.url, headers={"Origin": probe})
                            allow_origin = r.headers.get("access-control-allow-origin", "")
                            allow_creds = r.headers.get("access-control-allow-credentials", "").lower() == "true"
                            reflected = allow_origin == probe
                            wildcard_with_creds = allow_origin == "*" and allow_creds
                            if (reflected or wildcard_with_creds) and "fail_finding" in step:
                                _add_finding(res, scenario, step["fail_finding"],
                                             evidence={"probe_origin": probe,
                                                       "allow_origin": allow_origin,
                                                       "allow_credentials": allow_creds})
                                await _emit_finding(on_event, scenario["id"], step["fail_finding"])
                        elif action == "expect_no_sql_error":
                            html = (await page.content()).lower()
                            page_html_cache = html
                            patterns = [
                                "sql syntax", "sqlstate", "psql:", "ora-", "mysql_fetch",
                                "unclosed quotation mark", "syntax error at or near",
                                "warning: mysql", "odbc driver", "pg_query",
                            ]
                            hit = next((p for p in patterns if p in html), None)
                            if hit and "fail_finding" in step:
                                _add_finding(res, scenario, step["fail_finding"],
                                             evidence={"matched_pattern": hit, "url": page.url})
                                await _emit_finding(on_event, scenario["id"], step["fail_finding"])
                        elif action == "expect_no_mixed_content":
                            from urllib.parse import urlparse
                            cur = urlparse(page.url)
                            if cur.scheme == "https":
                                html = page_html_cache or await page.content()
                                page_html_cache = html
                                refs = re.findall(r'(?:src|href)\s*=\s*[\"\'](http://[^\"\'\s>]+)', html)
                                refs = [r for r in refs if not r.startswith("http://localhost")]
                                if refs and "fail_finding" in step:
                                    _add_finding(res, scenario, step["fail_finding"],
                                                 evidence={"sample_refs": refs[:5], "count": len(refs)})
                                    await _emit_finding(on_event, scenario["id"], step["fail_finding"])
                        elif action == "expect_storage_clean":
                            storage = await page.evaluate(
                                "() => ({local: Object.assign({}, localStorage), session: Object.assign({}, sessionStorage)})"
                            )
                            suspect_key = re.compile(r"(token|secret|password|auth|jwt|bearer|api[_-]?key)", re.I)
                            suspect_val = re.compile(r"^(eyJ[A-Za-z0-9_-]{10,}|[A-Fa-f0-9]{32,})$")
                            hits: List[Dict[str, str]] = []
                            for scope in ("local", "session"):
                                for k, v in (storage.get(scope) or {}).items():
                                    sv = str(v)
                                    if suspect_key.search(k) or suspect_val.match(sv):
                                        hits.append({"scope": scope, "key": k, "value_preview": sv[:24] + "…"})
                            if hits and "fail_finding" in step:
                                _add_finding(res, scenario, step["fail_finding"],
                                             evidence={"hits": hits[:10]})
                                await _emit_finding(on_event, scenario["id"], step["fail_finding"])
                        else:
                            await _emit(on_event, type="step_skipped", scenario=scenario["id"],
                                        reason=f"unknown action: {action}")

                        await _emit(on_event, type="step_passed", scenario=scenario["id"],
                                    step_idx=idx, action=action)
                    except Exception as step_err:
                        await _emit(on_event, type="step_error", scenario=scenario["id"],
                                    step_idx=idx, action=action, error=str(step_err))
                        # S-7 fix: navigation OR assertion errors fail the scenario, so
                        # we never silently report "no findings" because of a runtime crash.
                        if action in ("goto", "fetch_url") or action.startswith("expect_"):
                            res.passed = False
                            res.error = f"{action} failed: {step_err}"
                            break

                # Persist video path if recording
                try:
                    video = page.video
                    if video:
                        await context.close()
                        try:
                            res.video_path = str(await video.path())
                        except Exception:
                            res.video_path = None
                    else:
                        await context.close()
                except Exception:
                    pass
                res.har_path = str(har_path)
            finally:
                await browser.close()
    except Exception as e:
        res.passed = False
        res.error = f"runner failed: {e}"
        logger.exception("run_scenario crashed: %s", e)

    res.duration_s = time.perf_counter() - started
    res.passed = res.passed and not res.findings
    await _emit(on_event, type="scenario_finished", scenario=scenario["id"],
                passed=res.passed, findings=len(res.findings),
                duration_s=res.duration_s, video=res.video_path)
    return res


def _add_finding(res: ScenarioResult, scenario: Dict, fail_data: Dict, evidence: Dict[str, Any]) -> None:
    res.findings.append(Finding(
        title=fail_data.get("title", "Security expectation failed"),
        severity=fail_data.get("severity", scenario.get("severity", "info")),
        scenario_id=scenario["id"],
        owasp=scenario.get("owasp", ""),
        evidence=evidence,
        repro_steps=scenario.get("steps", []),
    ))


async def _emit_finding(on_event: Optional[EventFn], scenario_id: str, fail_data: Dict) -> None:
    await _emit(
        on_event,
        type="finding",
        scenario=scenario_id,
        title=fail_data.get("title"),
        severity=fail_data.get("severity"),
    )


# ----------------------------- run dir ---------------------------------------


def new_run_id() -> str:
    return f"{int(time.time())}_{uuid.uuid4().hex[:8]}"


def video_url_from_path(p: Optional[str], cfg: AuditConfig) -> Optional[str]:
    """Translate an absolute filesystem path to an /artifacts/<run>/<scenario>/... URL
    that our FastAPI static mount exposes. Returns None if the path is outside artifacts dir."""
    if not p:
        return None
    try:
        rel = pathlib.Path(p).resolve().relative_to(cfg.artifacts_dir)
        return f"/artifacts/{rel.as_posix()}"
    except Exception:
        return None
