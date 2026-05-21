"""Confluence Data Center REST client (PAT auth).

Endpoint base: /rest/api/content (DC) — różny od Cloud (/wiki/rest/api).

ENV:
    CONFLUENCE_DC_BASE_URL    np. https://confluence.example.com
    CONFLUENCE_DC_PAT         Personal Access Token (Bearer)
    CONFLUENCE_DC_VERIFY_SSL  true|false|<path-to-CA-bundle> (default true)
    CONFLUENCE_DC_TIMEOUT_S   default 15
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ConfluenceError(RuntimeError):
    """Błąd komunikacji z Confluence."""


@dataclass(frozen=True)
class ConfluencePage:
    """Znormalizowana strona Confluence (storage XHTML zostaje w `body_storage`)."""

    id: str
    title: str
    space_key: str
    body_storage: str = ""
    body_view: str = ""
    url: Optional[str] = None
    version: int = 1
    labels: list[str] = field(default_factory=list)


def _bool_env(name: str, default: bool = True) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _resolve_verify(value: Optional[str]) -> bool | str:
    if value is None or value.strip() == "":
        return True
    v = value.strip()
    if v.lower() in ("1", "true", "yes", "on"):
        return True
    if v.lower() in ("0", "false", "no", "off"):
        logger.warning("CONFLUENCE_DC_VERIFY_SSL=false — TLS verification DISABLED.")
        return False
    return v


class ConfluenceDCClient:
    def __init__(
        self,
        base_url: str,
        pat: str,
        *,
        verify: bool | str = True,
        timeout_s: float = 15.0,
        user_agent: str = "adk-fundamentals/module_20-analyst",
    ) -> None:
        if not base_url:
            raise ValueError("ConfluenceDCClient: base_url required")
        if not pat:
            raise ValueError("ConfluenceDCClient: pat required")
        import requests

        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {pat}",
                "Accept": "application/json",
                "User-Agent": user_agent,
            }
        )
        self._session.verify = verify

    # ---- low-level ----

    def _request(self, method: str, path: str, *, params: Optional[dict] = None,
                 payload: Optional[dict] = None) -> Any:
        import requests

        url = f"{self.base_url}{path}"
        try:
            r = self._session.request(
                method,
                url,
                params=params,
                json=payload,
                headers=({"Content-Type": "application/json"} if payload else None),
                timeout=self.timeout_s,
            )
        except requests.RequestException as e:
            raise ConfluenceError(f"{method} {path}: network error: {e}") from e
        if r.status_code >= 400:
            raise ConfluenceError(f"{method} {path}: HTTP {r.status_code}: {r.text[:300]}")
        if not r.text:
            return None
        try:
            return r.json()
        except ValueError as e:
            raise ConfluenceError(f"{method} {path}: invalid JSON: {e}") from e

    # ---- high-level ----

    def search(self, *, cql: str, limit: int = 10) -> list[dict]:
        """CQL search. Zwraca listę: [{id, title, space, type, url}].

        Przykład CQL: `type = page AND text ~ "moduł rozliczeń"`
        """
        if not cql:
            raise ValueError("search: cql required")
        limit = max(1, min(int(limit), 50))
        data = self._request("GET", "/rest/api/content/search",
                             params={"cql": cql, "limit": limit})
        results = (data or {}).get("results", []) or []
        out = []
        for r in results:
            out.append(
                {
                    "id": str(r.get("id") or ""),
                    "title": r.get("title") or "",
                    "space": ((r.get("space") or {}).get("key") or ""),
                    "type": r.get("type") or "",
                    "url": (
                        f"{self.base_url}{(r.get('_links') or {}).get('webui', '')}"
                        if (r.get("_links") or {}).get("webui") else None
                    ),
                }
            )
        return out

    def get_page(self, page_id: str, *, expand_body: bool = True) -> ConfluencePage:
        """Pobierz stronę po ID."""
        if not page_id:
            raise ValueError("get_page: page_id required")
        expand = "version,space,metadata.labels"
        if expand_body:
            expand += ",body.storage,body.view"
        data = self._request("GET", f"/rest/api/content/{page_id}",
                             params={"expand": expand})
        return self._parse_page(data)

    def get_page_by_title(self, *, space_key: str, title: str) -> Optional[ConfluencePage]:
        """Lookup po (space, title). None gdy brak."""
        if not (space_key and title):
            raise ValueError("get_page_by_title: space_key, title required")
        data = self._request(
            "GET", "/rest/api/content",
            params={
                "spaceKey": space_key,
                "title": title,
                "expand": "version,space,body.storage,body.view,metadata.labels",
                "limit": 1,
            },
        )
        results = (data or {}).get("results", []) or []
        if not results:
            return None
        return self._parse_page(results[0])

    def create_page(
        self,
        *,
        space_key: str,
        title: str,
        body_storage_xhtml: str,
        parent_id: Optional[str] = None,
        labels: Optional[list[str]] = None,
    ) -> ConfluencePage:
        """Utwórz stronę. body w formacie storage XHTML."""
        if not (space_key and title):
            raise ValueError("create_page: space_key, title required")
        payload: dict[str, Any] = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {"storage": {"value": body_storage_xhtml or "", "representation": "storage"}},
        }
        if parent_id:
            payload["ancestors"] = [{"id": str(parent_id)}]
        data = self._request("POST", "/rest/api/content", payload=payload)
        page = self._parse_page(data or {})
        if labels:
            self.add_labels(page.id, labels)
        return page

    def update_page(
        self,
        *,
        page_id: str,
        title: str,
        body_storage_xhtml: str,
        new_version: int,
    ) -> ConfluencePage:
        """Aktualizuj stronę (musisz znać aktualną wersję + 1)."""
        if not page_id:
            raise ValueError("update_page: page_id required")
        payload = {
            "id": page_id,
            "type": "page",
            "title": title,
            "version": {"number": int(new_version)},
            "body": {"storage": {"value": body_storage_xhtml, "representation": "storage"}},
        }
        data = self._request("PUT", f"/rest/api/content/{page_id}", payload=payload)
        return self._parse_page(data or {})

    def add_labels(self, page_id: str, labels: list[str]) -> None:
        if not (page_id and labels):
            return
        payload = [{"prefix": "global", "name": str(label)} for label in labels]
        self._request("POST", f"/rest/api/content/{page_id}/label", payload=payload)

    # ---- internal ----

    def _parse_page(self, raw: dict) -> ConfluencePage:
        body = (raw.get("body") or {})
        webui = ((raw.get("_links") or {}).get("webui")) or ""
        return ConfluencePage(
            id=str(raw.get("id") or ""),
            title=str(raw.get("title") or ""),
            space_key=str(((raw.get("space") or {}).get("key")) or ""),
            body_storage=str((body.get("storage") or {}).get("value") or ""),
            body_view=str((body.get("view") or {}).get("value") or ""),
            url=(f"{self.base_url}{webui}" if webui else None),
            version=int(((raw.get("version") or {}).get("number")) or 1),
            labels=[
                lbl.get("name")
                for lbl in (((raw.get("metadata") or {}).get("labels") or {}).get("results") or [])
                if lbl.get("name")
            ],
        )


_CLIENT_SINGLETON: Optional[ConfluenceDCClient] = None


def get_confluence_client() -> Optional[ConfluenceDCClient]:
    """Singleton z ENV; None gdy niekompletny config (graceful fallback)."""
    global _CLIENT_SINGLETON
    if _CLIENT_SINGLETON is not None:
        return _CLIENT_SINGLETON

    base_url = os.getenv("CONFLUENCE_DC_BASE_URL", "").strip()
    pat = os.getenv("CONFLUENCE_DC_PAT", "").strip()
    if not (base_url and pat):
        logger.info("ConfluenceDCClient: not configured (set CONFLUENCE_DC_BASE_URL + CONFLUENCE_DC_PAT).")
        return None
    verify = _resolve_verify(os.getenv("CONFLUENCE_DC_VERIFY_SSL"))
    timeout_s = float(os.getenv("CONFLUENCE_DC_TIMEOUT_S", "15"))
    try:
        _CLIENT_SINGLETON = ConfluenceDCClient(
            base_url=base_url, pat=pat, verify=verify, timeout_s=timeout_s,
        )
        logger.info("ConfluenceDCClient initialized (base=%s).", base_url)
        return _CLIENT_SINGLETON
    except Exception as e:
        logger.error("ConfluenceDCClient init failed: %s", e)
        return None
