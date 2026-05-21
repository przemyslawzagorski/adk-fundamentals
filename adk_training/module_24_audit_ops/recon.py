"""Passive reconnaissance — gather information without aggressive probing.

Returns a structured profile of the target so the LLM can plan attacks intelligently.
"""
from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import httpx

from .config import AuditConfig
from .safety import assert_url_allowed

logger = logging.getLogger(__name__)


# Common paths that often leak sensitive info (read-only HEAD/GET, no auth bypass)
_INFO_PATHS = [
    "/robots.txt",
    "/sitemap.xml",
    "/.git/config",
    "/.env",
    "/.well-known/security.txt",
    "/admin",
    "/api/",
    "/swagger.json",
    "/openapi.json",
    "/graphql",
    "/login",
    "/healthz",
    "/health",
]

# Heuristic tech-stack fingerprints (very small subset — realistic alternative is wappalyzer)
_FINGERPRINTS = {
    "react":        [r"__REACT_DEVTOOLS_GLOBAL_HOOK__", r"data-reactroot", r'_next/static'],
    "next.js":      [r'_next/static', r'__NEXT_DATA__'],
    "vue":          [r"data-v-[0-9a-f]{8}", r"__VUE_DEVTOOLS_GLOBAL_HOOK__"],
    "angular":      [r"ng-app", r"ng-version", r"\[ng-"],
    "jquery":       [r"jquery[-.]([0-9.]+)\.js"],
    "wordpress":    [r"wp-content/", r"/wp-includes/"],
    "django":       [r"csrfmiddlewaretoken"],
    "express":      [r"X-Powered-By: Express"],
    "fastapi":      [r"FastAPI", r"/openapi.json"],
    "spring":       [r"X-Application-Context"],
    "laravel":      [r"laravel_session", r"XSRF-TOKEN"],
    "asp.net":      [r"X-AspNet-Version", r"__VIEWSTATE"],
    "nginx":        [r"Server: nginx"],
    "apache":       [r"Server: Apache"],
    "cloudflare":   [r"cf-ray", r"__cfduid"],
}

# Security headers we want to verify
_SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "Cross-Origin-Opener-Policy",
]


@dataclass
class ReconResult:
    target_url: str
    final_url: str = ""
    status_code: int = 0
    response_time_ms: int = 0
    server_header: str = ""
    technologies: List[str] = field(default_factory=list)
    title: str = ""
    forms: List[Dict] = field(default_factory=list)
    interesting_paths: List[Dict] = field(default_factory=list)
    security_headers: Dict[str, Optional[str]] = field(default_factory=dict)
    cookies: List[Dict] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    def summary(self) -> str:
        techs = ", ".join(self.technologies) or "unknown"
        missing_headers = [h for h, v in self.security_headers.items() if not v]
        return (
            f"Target: {self.final_url} ({self.status_code})\n"
            f"Stack: {techs}\n"
            f"Server: {self.server_header}\n"
            f"Forms: {len(self.forms)}\n"
            f"Missing security headers: {', '.join(missing_headers) or '(none)'}\n"
            f"Interesting paths: {len(self.interesting_paths)}"
        )


def _detect_tech(html: str, headers: httpx.Headers) -> List[str]:
    detected: List[str] = []
    headers_str = "\n".join(f"{k}: {v}" for k, v in headers.items())
    haystack = html + "\n" + headers_str
    for tech, patterns in _FINGERPRINTS.items():
        for pat in patterns:
            if re.search(pat, haystack, re.IGNORECASE):
                detected.append(tech)
                break
    return detected


def _extract_forms(html: str, base_url: str) -> List[Dict]:
    forms: List[Dict] = []
    for m in re.finditer(r"<form\b([^>]*)>(.*?)</form>", html, re.IGNORECASE | re.DOTALL):
        attrs_raw, body = m.group(1), m.group(2)
        action = (re.search(r'action=["\']([^"\']*)["\']', attrs_raw) or [None, ""])[1]
        method = (re.search(r'method=["\']([^"\']*)["\']', attrs_raw) or [None, "GET"])[1].upper()
        inputs: List[Dict] = []
        for im in re.finditer(r'<input\b([^>]*)>', body, re.IGNORECASE):
            iattrs = im.group(1)
            inputs.append({
                "name": (re.search(r'name=["\']([^"\']*)["\']', iattrs) or [None, ""])[1],
                "type": (re.search(r'type=["\']([^"\']*)["\']', iattrs) or [None, "text"])[1],
            })
        forms.append({
            "action": urljoin(base_url, action),
            "method": method,
            "inputs": inputs,
        })
    return forms


async def _check_path(client: httpx.AsyncClient, base: str, path: str) -> Optional[Dict]:
    try:
        url = urljoin(base, path)
        r = await client.get(url, follow_redirects=False)
        if r.status_code in (200, 301, 302, 401, 403):
            content_type = r.headers.get("content-type", "")
            return {
                "path": path,
                "url": url,
                "status": r.status_code,
                "content_type": content_type,
                "size": len(r.content) if r.content else 0,
            }
    except Exception:
        return None
    return None


async def passive_recon(target_url: str, cfg: AuditConfig) -> ReconResult:
    """Passive recon via httpx — single GET to root, extract forms/tech, then probe common paths."""
    assert_url_allowed(target_url, cfg)
    result = ReconResult(target_url=target_url)

    timeout = httpx.Timeout(connect=8.0, read=10.0, write=8.0, pool=8.0)
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        verify=True,
        headers={"User-Agent": "AuditOps/0.1 (+https://example.local/auditops)"},
    ) as client:
        # 1) Root request
        try:
            import time
            t0 = time.perf_counter()
            r = await client.get(target_url)
            result.response_time_ms = int((time.perf_counter() - t0) * 1000)
            result.final_url = str(r.url)
            result.status_code = r.status_code
            result.server_header = r.headers.get("server", "")
            html = r.text or ""
            # Title
            title_m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            if title_m:
                result.title = title_m.group(1).strip()[:200]
            # Tech
            result.technologies = _detect_tech(html, r.headers)
            # Forms
            result.forms = _extract_forms(html, str(r.url))
            # Security headers
            for h in _SECURITY_HEADERS:
                result.security_headers[h] = r.headers.get(h)
            # Cookies
            for c in r.cookies.jar:
                result.cookies.append({
                    "name": c.name,
                    "domain": c.domain,
                    "secure": bool(getattr(c, "secure", False)),
                    "httponly": bool(c._rest.get("HttpOnly")) if hasattr(c, "_rest") else False,
                    "samesite": c._rest.get("SameSite") if hasattr(c, "_rest") else None,
                })
        except Exception as e:
            result.error = f"root request failed: {e}"
            logger.warning("recon root failed: %s", e)
            return result

        # 2) Probe interesting paths in parallel (rate-limited)
        base = f"{urlparse(result.final_url).scheme}://{urlparse(result.final_url).netloc}"
        tasks = [_check_path(client, base, p) for p in _INFO_PATHS]
        path_results = await asyncio.gather(*tasks, return_exceptions=False)
        result.interesting_paths = [p for p in path_results if p is not None]

    # 3) Notes / heuristics
    if not result.security_headers.get("Content-Security-Policy"):
        result.notes.append("No CSP — XSS impact will be higher.")
    if not result.security_headers.get("Strict-Transport-Security") and result.final_url.startswith("https"):
        result.notes.append("HTTPS without HSTS — TLS downgrade risk.")
    insecure_cookies = [c["name"] for c in result.cookies if not c.get("secure")]
    if insecure_cookies:
        result.notes.append(f"Cookies without Secure flag: {', '.join(insecure_cookies)}")
    if any(p["path"] in ("/.git/config", "/.env") for p in result.interesting_paths):
        result.notes.append("CRITICAL: VCS or env file may be exposed.")

    return result
