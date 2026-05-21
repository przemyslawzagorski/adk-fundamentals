"""Jira Data Center REST client (PAT auth).

Cienki, synchroniczny wrapper na `requests`. Zaprojektowany jako alternatywa dla MCP —
wprost wywołuje endpointy Jira DC i zwraca dane domenowe (nie surowy JSON), żeby
agent nie marnował tokenów na parsowanie.

Auth: Personal Access Token (Bearer) — Jira DC 8.14+
Docs: https://docs.atlassian.com/software/jira/docs/api/REST/latest/

ENV:
    JIRA_DC_BASE_URL          np. https://jira.example.com
    JIRA_DC_PAT               Personal Access Token (Bearer)
    JIRA_DC_VERIFY_SSL        true|false|<path-to-CA-bundle>  (default: true)
    JIRA_DC_TIMEOUT_S         default 15
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


class JiraError(RuntimeError):
    """Błąd komunikacji z Jira (sieć, auth, 4xx/5xx)."""


@dataclass(frozen=True)
class JiraIssue:
    """Znormalizowana reprezentacja ticketu — tylko pola istotne dla HLD/epików."""

    key: str
    summary: str
    description: str
    issue_type: str
    status: str
    priority: Optional[str] = None
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    labels: list[str] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    fix_versions: list[str] = field(default_factory=list)
    epic_link: Optional[str] = None
    parent_key: Optional[str] = None
    url: Optional[str] = None

    def to_markdown(self) -> str:
        """Renderuje ticket jako blok kontekstu dla LLM (PL)."""
        meta = [f"**{self.key}** — {self.summary}",
                f"- Typ: {self.issue_type}",
                f"- Status: {self.status}"]
        if self.priority:
            meta.append(f"- Priorytet: {self.priority}")
        if self.assignee:
            meta.append(f"- Przypisany: {self.assignee}")
        if self.labels:
            meta.append(f"- Labels: {', '.join(self.labels)}")
        if self.components:
            meta.append(f"- Komponenty: {', '.join(self.components)}")
        if self.fix_versions:
            meta.append(f"- Fix versions: {', '.join(self.fix_versions)}")
        if self.epic_link:
            meta.append(f"- Epic Link: {self.epic_link}")
        if self.parent_key:
            meta.append(f"- Parent: {self.parent_key}")
        if self.url:
            meta.append(f"- URL: {self.url}")
        body = self.description.strip() or "_(brak opisu)_"
        return "\n".join(meta) + "\n\n---\n\n" + body


def _bool_env(name: str, default: bool = True) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _resolve_verify(value: Optional[str]) -> bool | str:
    """Mapowanie JIRA_DC_VERIFY_SSL na argument `verify=` requests.

    - 'true'/'1'/'yes'/'on'   -> True
    - 'false'/'0'/'no'/'off'  -> False (insecure — log warning)
    - inna wartość = path     -> str (CA bundle)
    """
    if value is None or value.strip() == "":
        return True
    v = value.strip()
    if v.lower() in ("1", "true", "yes", "on"):
        return True
    if v.lower() in ("0", "false", "no", "off"):
        logger.warning("JIRA_DC_VERIFY_SSL=false — TLS verification DISABLED. Use only on trusted networks.")
        return False
    return v  # path to CA bundle


class JiraDCClient:
    """Synchroniczny klient Jira DC. Thread-safe (Session per instance).

    Metody zwracają znormalizowane dane (JiraIssue), nie surowy JSON.
    Błędy: rzucają JiraError z czytelnym komunikatem (status + 200 znaków body).
    """

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
            raise ValueError("JiraDCClient: base_url required")
        if not pat:
            raise ValueError("JiraDCClient: pat required")
        # lazy import — pozwala importować moduł bez `requests` w środowisku testowym
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

    # ----- low-level -----

    def _get(self, path: str, params: Optional[dict] = None) -> Any:
        import requests

        url = f"{self.base_url}{path}"
        try:
            r = self._session.get(url, params=params, timeout=self.timeout_s)
        except requests.RequestException as e:
            raise JiraError(f"GET {path}: network error: {e}") from e
        if r.status_code >= 400:
            raise JiraError(f"GET {path}: HTTP {r.status_code}: {r.text[:200]}")
        try:
            return r.json()
        except ValueError as e:
            raise JiraError(f"GET {path}: invalid JSON: {e}") from e

    def _post(self, path: str, payload: dict) -> Any:
        import requests

        url = f"{self.base_url}{path}"
        try:
            r = self._session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout_s,
            )
        except requests.RequestException as e:
            raise JiraError(f"POST {path}: network error: {e}") from e
        if r.status_code >= 400:
            raise JiraError(f"POST {path}: HTTP {r.status_code}: {r.text[:300]}")
        try:
            return r.json()
        except ValueError:
            return None  # 204 etc.

    # ----- high-level -----

    def get_issue(self, key: str, *, expand: Optional[str] = None) -> JiraIssue:
        """Pobierz ticket po kluczu (np. 'PROJ-123').

        Zwraca znormalizowany JiraIssue. Rzuca JiraError gdy 4xx/5xx.
        """
        if not key or not isinstance(key, str):
            raise ValueError("get_issue: key required")
        params = {"fields": "summary,description,issuetype,status,priority,assignee,reporter,labels,components,fixVersions,parent,customfield_10008,customfield_10014"}
        if expand:
            params["expand"] = expand
        data = self._get(f"/rest/api/2/issue/{key}", params=params)
        return self._parse_issue(data)

    def search(self, jql: str, *, max_results: int = 20, fields: Optional[list[str]] = None) -> list[JiraIssue]:
        """JQL search — zwraca listę JiraIssue (max 50, default 20)."""
        if not jql:
            raise ValueError("search: jql required")
        max_results = max(1, min(int(max_results), 50))
        payload = {
            "jql": jql,
            "maxResults": max_results,
            "fields": fields or [
                "summary", "description", "issuetype", "status", "priority",
                "assignee", "reporter", "labels", "components", "fixVersions", "parent",
            ],
        }
        data = self._post("/rest/api/2/search", payload)
        issues = data.get("issues", []) if isinstance(data, dict) else []
        return [self._parse_issue(i) for i in issues]

    def get_comments(self, key: str, *, max_results: int = 20) -> list[dict]:
        """Pobierz komentarze do ticketu (skrótowo: author, body, created)."""
        if not key:
            raise ValueError("get_comments: key required")
        data = self._get(f"/rest/api/2/issue/{key}/comment", params={"maxResults": max_results})
        out = []
        for c in (data.get("comments", []) or []):
            out.append(
                {
                    "author": (c.get("author") or {}).get("displayName"),
                    "created": c.get("created"),
                    "body": c.get("body", ""),
                }
            )
        return out

    def create_issue(
        self,
        *,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Epic",
        labels: Optional[list[str]] = None,
        priority: Optional[str] = None,
        epic_name: Optional[str] = None,
        parent_key: Optional[str] = None,
        custom_fields: Optional[dict] = None,
    ) -> str:
        """Utwórz issue (epic/story/task). Zwraca klucz nowego issue.

        Dla 'Epic' w Jira DC: pole `Epic Name` jest często wymagane (customfield_10011
        lub podobne — różni się per instancja). Przekaż `epic_name` lub całość przez
        `custom_fields={"customfield_XYZ": "..."}`.
        """
        if not (project_key and summary):
            raise ValueError("create_issue: project_key, summary required")
        fields: dict[str, Any] = {
            "project": {"key": project_key},
            "summary": summary,
            "description": description or "",
            "issuetype": {"name": issue_type},
        }
        if labels:
            fields["labels"] = list(labels)
        if priority:
            fields["priority"] = {"name": priority}
        if parent_key:
            fields["parent"] = {"key": parent_key}
        if epic_name:
            # spróbuj standardowych mappingów dla Epic Name w DC
            fields.setdefault("customfield_10011", epic_name)
        if custom_fields:
            fields.update(custom_fields)
        data = self._post("/rest/api/2/issue", {"fields": fields})
        if not isinstance(data, dict) or "key" not in data:
            raise JiraError(f"create_issue: missing key in response: {data}")
        return str(data["key"])

    # ----- internal -----

    def _parse_issue(self, raw: dict) -> JiraIssue:
        f = (raw or {}).get("fields", {}) or {}
        key = (raw or {}).get("key") or ""
        return JiraIssue(
            key=key,
            summary=str(f.get("summary") or ""),
            description=str(f.get("description") or ""),
            issue_type=((f.get("issuetype") or {}).get("name") or "Unknown"),
            status=((f.get("status") or {}).get("name") or "Unknown"),
            priority=((f.get("priority") or {}).get("name") if f.get("priority") else None),
            assignee=((f.get("assignee") or {}).get("displayName") if f.get("assignee") else None),
            reporter=((f.get("reporter") or {}).get("displayName") if f.get("reporter") else None),
            labels=list(f.get("labels") or []),
            components=[c.get("name") for c in (f.get("components") or []) if c.get("name")],
            fix_versions=[v.get("name") for v in (f.get("fixVersions") or []) if v.get("name")],
            parent_key=((f.get("parent") or {}).get("key") if f.get("parent") else None),
            epic_link=str(f.get("customfield_10014") or "") or None,
            url=f"{self.base_url}/browse/{key}" if key else None,
        )


_CLIENT_SINGLETON: Optional[JiraDCClient] = None


def get_jira_client() -> Optional[JiraDCClient]:
    """Singleton z ENV. Zwraca None gdy konfiguracja niekompletna (graceful fallback)."""
    global _CLIENT_SINGLETON
    if _CLIENT_SINGLETON is not None:
        return _CLIENT_SINGLETON

    base_url = os.getenv("JIRA_DC_BASE_URL", "").strip()
    pat = os.getenv("JIRA_DC_PAT", "").strip()
    if not (base_url and pat):
        logger.info("JiraDCClient: not configured (set JIRA_DC_BASE_URL + JIRA_DC_PAT).")
        return None

    verify = _resolve_verify(os.getenv("JIRA_DC_VERIFY_SSL"))
    timeout_s = float(os.getenv("JIRA_DC_TIMEOUT_S", "15"))
    try:
        _CLIENT_SINGLETON = JiraDCClient(
            base_url=base_url, pat=pat, verify=verify, timeout_s=timeout_s,
        )
        logger.info("JiraDCClient initialized (base=%s, verify=%s).", base_url, verify)
        return _CLIENT_SINGLETON
    except Exception as e:
        logger.error("JiraDCClient init failed: %s", e)
        return None
