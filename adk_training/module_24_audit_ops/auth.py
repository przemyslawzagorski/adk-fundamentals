"""Authentication context — lets a scenario reach pages behind a login.

Three modes (combinable):
- ``cookies`` — list of {name, value, domain, path, secure, httpOnly, sameSite}
- ``headers`` — extra HTTP headers (e.g. ``Authorization: Bearer ...``)
- ``basic_auth`` — (username, password) tuple for HTTP Basic

Auth contexts are stored *out-of-band* (POSTed once, referenced by id) so
secrets never appear in run JSON, SSE events or report markdown.
"""
from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


_SECRET_PLACEHOLDER = "[REDACTED]"


@dataclass
class AuthContext:
    id: str
    label: str = ""
    cookies: List[Dict[str, Any]] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    basic_auth: Optional[Tuple[str, str]] = None
    created_at: float = field(default_factory=time.time)

    def fingerprint(self) -> Dict[str, Any]:
        """Safe summary — no values, just shape."""
        return {
            "id": self.id,
            "label": self.label,
            "cookie_names": [c.get("name") for c in self.cookies],
            "header_names": sorted(self.headers.keys()),
            "basic_auth": bool(self.basic_auth),
            "created_at": self.created_at,
        }


class AuthStore:
    """In-process auth vault. Use :class:`SqliteAuthStore` for persistence."""

    def __init__(self) -> None:
        self._items: Dict[str, AuthContext] = {}

    def add(self, ctx: AuthContext) -> str:
        self._items[ctx.id] = ctx
        return ctx.id

    def get(self, auth_id: Optional[str]) -> Optional[AuthContext]:
        if not auth_id:
            return None
        return self._items.get(auth_id)

    def list(self) -> List[Dict[str, Any]]:
        return [ctx.fingerprint() for ctx in self._items.values()]

    def remove(self, auth_id: str) -> bool:
        return self._items.pop(auth_id, None) is not None


def make_auth(
    label: str = "",
    cookies: Optional[List[Dict[str, Any]]] = None,
    headers: Optional[Dict[str, str]] = None,
    basic_auth: Optional[Tuple[str, str]] = None,
) -> AuthContext:
    """Construct an AuthContext with a fresh id and basic validation."""
    cookies = list(cookies or [])
    headers = dict(headers or {})
    for c in cookies:
        if "name" not in c or "value" not in c:
            raise ValueError("cookie entry must have at least name+value")
        # Default fields Playwright requires
        c.setdefault("domain", "")
        c.setdefault("path", "/")
    # Basic header sanity — block control characters (CRLF injection)
    for k, v in headers.items():
        if not _SAFE_HEADER.match(k) or "\r" in v or "\n" in v:
            raise ValueError(f"unsafe header: {k!r}")
    return AuthContext(
        id=uuid.uuid4().hex,
        label=label[:80],
        cookies=cookies,
        headers=headers,
        basic_auth=basic_auth,
    )


_SAFE_HEADER = re.compile(r"^[A-Za-z0-9\-]{1,80}$")


def redact_for_logging(payload: Any) -> Any:
    """Deep-redact strings that look like secrets in nested structures."""
    if isinstance(payload, dict):
        return {k: (_SECRET_PLACEHOLDER if _looks_secret(k) else redact_for_logging(v)) for k, v in payload.items()}
    if isinstance(payload, list):
        return [redact_for_logging(v) for v in payload]
    return payload


_SECRET_KEYS = re.compile(r"(?:auth|token|password|secret|cookie|bearer|api[_-]?key)", re.IGNORECASE)


def _looks_secret(key: str) -> bool:
    return bool(_SECRET_KEYS.search(key or ""))
