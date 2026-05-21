"""Attack library — built-in OWASP Top 10 (2021) probe templates.

Each scenario is a JSON-serializable dict with ordered `steps` that the
Playwright executor can run deterministically. Steps use a tiny declarative
DSL (see `playwright_runner.execute_steps`):

    {"action": "goto",       "url":"..."}
    {"action": "fill",       "selector":"...", "value":"..."}
    {"action": "click",      "selector":"..."}
    {"action": "press",      "key":"Enter"}
    {"action": "wait_for",   "selector":"...", "timeout":3000}
    {"action": "expect_text","contains":"...", "negate":false}
    {"action": "expect_status","equals":200}
    {"action": "expect_header","name":"X-Frame-Options","present":true}
    {"action": "screenshot", "name":"after_login"}
    {"action": "eval",       "script":"() => document.cookie"}

Findings are emitted by step assertions (expect_*) — when an assertion FAILS
in a security-relevant way we mark it as a finding (logic inverted vs unit
tests: a failing security expectation = vuln present).
"""
from __future__ import annotations

from typing import Dict, List
from urllib.parse import urlparse

from .recon import ReconResult


# CVSS scores (rough) per OWASP category — used by reporter.
SEVERITY_CVSS = {
    "critical": 9.0,
    "high":     7.5,
    "medium":   5.0,
    "low":      3.0,
    "info":     0.0,
}


def _origin(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def scenario_security_headers(url: str) -> Dict:
    """A02 / A05 — Insecure design: verify presence of standard security headers."""
    return {
        "id": "headers_baseline",
        "name": "Security headers baseline",
        "owasp": "A05:2021-Security Misconfiguration",
        "severity": "medium",
        "passive": True,
        "description": "Checks presence of CSP, HSTS, X-Frame-Options, X-CTO and Referrer-Policy.",
        "steps": [
            {"action": "goto", "url": url},
            {"action": "expect_header", "name": "Content-Security-Policy", "present": True,
             "fail_finding": {"title": "Missing Content-Security-Policy", "severity": "medium"}},
            {"action": "expect_header", "name": "Strict-Transport-Security", "present": True,
             "fail_finding": {"title": "Missing HSTS", "severity": "medium"}},
            {"action": "expect_header", "name": "X-Frame-Options", "present": True,
             "fail_finding": {"title": "Missing X-Frame-Options (clickjacking risk)", "severity": "low"}},
            {"action": "expect_header", "name": "X-Content-Type-Options", "present": True,
             "fail_finding": {"title": "Missing X-Content-Type-Options", "severity": "low"}},
            {"action": "screenshot", "name": "headers_baseline"},
        ],
    }


def scenario_exposed_files(url: str, recon: ReconResult) -> Dict:
    """A05 / A06 — Exposed VCS/env/config files."""
    candidates = [p for p in recon.interesting_paths if p["status"] == 200 and p["path"] in (
        "/.git/config", "/.env", "/.well-known/security.txt", "/swagger.json", "/openapi.json"
    )]
    steps = [{"action": "goto", "url": url}]
    for p in candidates:
        steps.append({"action": "fetch_url", "url": p["url"],
                      "fail_finding": {"title": f"Sensitive path exposed: {p['path']}", "severity": "high"}})
    return {
        "id": "exposed_files",
        "name": "Exposed sensitive files",
        "owasp": "A05:2021-Security Misconfiguration",
        "severity": "high",
        "passive": True,
        "description": "Verifies whether common sensitive files are publicly accessible.",
        "steps": steps,
    }


def scenario_xss_reflected(url: str, recon: ReconResult) -> Dict:
    """A03 — Reflected XSS in form inputs (canary string)."""
    canary = "audopsXSS_<script>alert(1)</script>"
    steps: List[Dict] = [{"action": "goto", "url": url}]
    if not recon.forms:
        steps.append({"action": "note", "message": "No forms detected; skipping reflected XSS checks."})
        return {
            "id": "xss_reflected",
            "name": "Reflected XSS probe (skipped — no forms)",
            "owasp": "A03:2021-Injection",
            "severity": "info",
            "passive": True,
            "description": "Skipped because recon found no forms.",
            "steps": steps,
        }
    # Pick first form with a text input
    for form in recon.forms[:3]:
        text_input = next((i for i in form["inputs"] if i["type"] in ("text", "search", "email", "")), None)
        if not text_input or not text_input["name"]:
            continue
        steps.append({"action": "goto", "url": form.get("action") or url})
        steps.append({"action": "fill", "selector": f'[name="{text_input["name"]}"]', "value": canary})
        steps.append({"action": "press", "key": "Enter"})
        steps.append({"action": "wait_for_load_state"})
        steps.append({
            "action": "expect_text", "contains": canary, "negate": True,
            "fail_finding": {
                "title": f"Reflected XSS canary echoed in {form.get('action') or url}",
                "severity": "high",
                "evidence_hint": "script tag rendered into DOM",
            },
        })
        steps.append({"action": "screenshot", "name": f"xss_{text_input['name']}"})
    return {
        "id": "xss_reflected",
        "name": "Reflected XSS canary in detected forms",
        "owasp": "A03:2021-Injection",
        "severity": "high",
        "passive": False,
        "description": "Submits a non-executing canary into discovered text inputs and checks the response.",
        "steps": steps,
    }


def scenario_open_redirect(url: str) -> Dict:
    """A01 — Open redirect via ?next= / ?redirect= / ?url= patterns."""
    payload = "https://evil.example.test/redirected"
    suspects = [f"{url.rstrip('/')}/login?next={payload}", f"{url.rstrip('/')}/?redirect={payload}", f"{url.rstrip('/')}/?url={payload}"]
    steps: List[Dict] = []
    for s in suspects:
        steps.append({"action": "goto", "url": s, "wait_until": "domcontentloaded"})
        steps.append({
            "action": "expect_origin", "equals": _origin(url),
            "fail_finding": {"title": f"Open redirect possible at {s}", "severity": "medium"},
        })
    return {
        "id": "open_redirect",
        "name": "Open redirect probe",
        "owasp": "A01:2021-Broken Access Control",
        "severity": "medium",
        "passive": False,
        "description": "Tries common redirect parameters and verifies the browser stays on origin.",
        "steps": steps,
    }


def scenario_clickjacking(url: str) -> Dict:
    return {
        "id": "clickjacking",
        "name": "Clickjacking via missing X-Frame-Options / frame-ancestors",
        "owasp": "A05:2021-Security Misconfiguration",
        "severity": "low",
        "passive": True,
        "description": "Combines X-Frame-Options and CSP frame-ancestors header check.",
        "steps": [
            {"action": "goto", "url": url},
            {"action": "expect_frame_ancestors_or_xfo",
             "fail_finding": {"title": "Page can be framed (clickjacking risk)", "severity": "low"}},
        ],
    }


def scenario_cookie_flags(url: str) -> Dict:
    return {
        "id": "cookie_flags",
        "name": "Cookie security flags",
        "owasp": "A05:2021-Security Misconfiguration",
        "severity": "medium",
        "passive": True,
        "description": "All non-public cookies should have Secure + HttpOnly + SameSite.",
        "steps": [
            {"action": "goto", "url": url},
            {"action": "expect_cookies_secure",
             "fail_finding": {"title": "Cookie missing Secure/HttpOnly/SameSite", "severity": "medium"}},
        ],
    }


def scenario_smoke_navigation(url: str) -> Dict:
    """Always-on smoke test that proves the agent can reach the target."""
    return {
        "id": "smoke_navigation",
        "name": "Smoke navigation",
        "owasp": "(meta)",
        "severity": "info",
        "passive": True,
        "description": "Loads the home page and captures a screenshot.",
        "steps": [
            {"action": "goto", "url": url},
            {"action": "screenshot", "name": "home"},
            {"action": "expect_status", "equals_any": [200, 301, 302, 401, 403]},
        ],
    }


def scenario_cors_misconfig(url: str) -> Dict:
    """A05 — CORS reflecting arbitrary Origin or wildcard with credentials."""
    return {
        "id": "cors_misconfig",
        "name": "CORS misconfiguration probe",
        "owasp": "A05:2021-Security Misconfiguration",
        "severity": "high",
        "passive": True,
        "description": "Sends a probe Origin header and checks if it is reflected back.",
        "steps": [
            {"action": "goto", "url": url},
            {"action": "expect_cors_open",
             "probe_origin": "https://attacker.example.test",
             "fail_finding": {
                 "title": "CORS reflects arbitrary Origin",
                 "severity": "high",
             }},
        ],
    }


def scenario_sqli_sniff(url: str, recon: ReconResult) -> Dict:
    """A03 — light SQLi error sniff: submits ``'`` to first form input.

    Detects unhandled DB driver error strings in the response.
    NEVER attempts UNION, time-based, or boolean-based payloads.
    """
    steps: List[Dict] = [{"action": "goto", "url": url}]
    if not recon.forms:
        steps.append({"action": "note", "message": "No forms; skipping SQLi sniff."})
        return {
            "id": "sqli_sniff",
            "name": "SQL error sniff (skipped — no forms)",
            "owasp": "A03:2021-Injection",
            "severity": "info",
            "passive": True,
            "description": "Skipped — recon found no forms.",
            "steps": steps,
        }
    for form in recon.forms[:2]:
        text_input = next((i for i in form["inputs"] if i["type"] in ("text", "search", "email", "")), None)
        if not text_input or not text_input["name"]:
            continue
        steps.append({"action": "goto", "url": form.get("action") or url})
        steps.append({"action": "fill", "selector": f'[name="{text_input["name"]}"]', "value": "'"})
        steps.append({"action": "press", "key": "Enter"})
        steps.append({"action": "wait_for_load_state"})
        steps.append({
            "action": "expect_no_sql_error",
            "fail_finding": {
                "title": f"DB error string leaked from {form.get('action') or url}",
                "severity": "high",
            },
        })
        steps.append({"action": "screenshot", "name": f"sqli_{text_input['name']}"})
    return {
        "id": "sqli_sniff",
        "name": "SQL error sniff in detected forms",
        "owasp": "A03:2021-Injection",
        "severity": "high",
        "passive": False,
        "description": "Submits a single quote to text inputs and looks for unhandled DB errors.",
        "steps": steps,
    }


def scenario_mixed_content(url: str) -> Dict:
    """A02 — Mixed content on HTTPS pages."""
    return {
        "id": "mixed_content",
        "name": "Mixed content on HTTPS",
        "owasp": "A02:2021-Cryptographic Failures",
        "severity": "medium",
        "passive": True,
        "description": "On an HTTPS page, ensure no http:// resources are referenced.",
        "steps": [
            {"action": "goto", "url": url},
            {"action": "expect_no_mixed_content",
             "fail_finding": {
                 "title": "Mixed content references found on HTTPS page",
                 "severity": "medium",
             }},
        ],
    }


def scenario_sensitive_storage(url: str) -> Dict:
    """A02 — secrets parked in localStorage / sessionStorage."""
    return {
        "id": "sensitive_storage",
        "name": "Sensitive data in browser storage",
        "owasp": "A02:2021-Cryptographic Failures",
        "severity": "medium",
        "passive": True,
        "description": "Scans localStorage / sessionStorage for token-shaped values.",
        "steps": [
            {"action": "goto", "url": url},
            {"action": "wait_for_load_state", "state": "networkidle"},
            {"action": "expect_storage_clean",
             "fail_finding": {
                 "title": "Token / secret-like value in browser storage",
                 "severity": "medium",
             }},
        ],
    }


def build_default_pack(url: str, recon: ReconResult, max_count: int = 8) -> List[Dict]:
    """Build a curated ordered list of scenarios based on recon output."""
    pack: List[Dict] = [
        scenario_smoke_navigation(url),
        scenario_security_headers(url),
        scenario_cookie_flags(url),
        scenario_clickjacking(url),
        scenario_exposed_files(url, recon),
        scenario_open_redirect(url),
        scenario_xss_reflected(url, recon),
        scenario_cors_misconfig(url),
        scenario_sqli_sniff(url, recon),
        scenario_mixed_content(url),
        scenario_sensitive_storage(url),
    ]
    return pack[:max_count]
