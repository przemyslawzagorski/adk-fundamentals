"""ADK FunctionTools wrapping JiraDCClient.

Każda funkcja ma czysty docstring i typed signature — to jest kontrakt dla LLM.
Zwracają dict (nie dataclass) bo ADK serializuje wynik do JSON.

Użycie:
    from .jira_tools import build_jira_tools
    tools = build_jira_tools()  # [] jeśli klient nieskonfigurowany
"""

from __future__ import annotations

import logging
from typing import Any

from google.adk.tools import FunctionTool

from ..clients.jira_dc_client import JiraError, get_jira_client

logger = logging.getLogger(__name__)


def jira_get_issue(issue_key: str) -> dict[str, Any]:
    """Pobiera ticket Jira po kluczu (np. 'SWOK-1234').

    Args:
        issue_key: Klucz ticketu w formacie PROJ-NUM.

    Returns:
        dict ze znormalizowanymi polami:
        {ok, key, summary, description, issue_type, status, priority,
         assignee, reporter, labels, components, fix_versions,
         epic_link, parent_key, url, markdown}
        markdown — gotowy blok kontekstu dla LLM (oszczędza tokeny).
        Przy błędzie: {ok: False, error: str}.
    """
    client = get_jira_client()
    if client is None:
        return {"ok": False, "error": "Jira client not configured (set JIRA_DC_BASE_URL + JIRA_DC_PAT)."}
    try:
        issue = client.get_issue(issue_key)
    except (JiraError, ValueError) as e:
        logger.warning("jira_get_issue(%s) failed: %s", issue_key, e)
        return {"ok": False, "error": str(e)}
    return {
        "ok": True,
        "key": issue.key,
        "summary": issue.summary,
        "description": issue.description,
        "issue_type": issue.issue_type,
        "status": issue.status,
        "priority": issue.priority,
        "assignee": issue.assignee,
        "reporter": issue.reporter,
        "labels": issue.labels,
        "components": issue.components,
        "fix_versions": issue.fix_versions,
        "epic_link": issue.epic_link,
        "parent_key": issue.parent_key,
        "url": issue.url,
        "markdown": issue.to_markdown(),
    }


def jira_search(jql: str, max_results: int = 20) -> dict[str, Any]:
    """Wyszukaj tickety przez JQL.

    Args:
        jql: Zapytanie JQL, np. 'project = SWOK AND status = Open'.
        max_results: 1..50 (default 20).

    Returns:
        {ok, count, issues: [{key, summary, status, issue_type, url}], error?}
    """
    client = get_jira_client()
    if client is None:
        return {"ok": False, "error": "Jira client not configured."}
    try:
        issues = client.search(jql, max_results=max_results)
    except (JiraError, ValueError) as e:
        return {"ok": False, "error": str(e)}
    return {
        "ok": True,
        "count": len(issues),
        "issues": [
            {
                "key": i.key,
                "summary": i.summary,
                "status": i.status,
                "issue_type": i.issue_type,
                "url": i.url,
            }
            for i in issues
        ],
    }


def jira_get_comments(issue_key: str, max_results: int = 20) -> dict[str, Any]:
    """Pobierz komentarze do ticketu.

    Args:
        issue_key: Klucz ticketu.
        max_results: 1..50.

    Returns:
        {ok, count, comments: [{author, created, body}], error?}
    """
    client = get_jira_client()
    if client is None:
        return {"ok": False, "error": "Jira client not configured."}
    try:
        comments = client.get_comments(issue_key, max_results=max_results)
    except (JiraError, ValueError) as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "count": len(comments), "comments": comments}


def build_jira_tools() -> list[FunctionTool]:
    """Zwróć listę FunctionTool dla agenta. [] gdy klient nieskonfigurowany.

    Read-only minimum: get_issue, search, get_comments. Tworzenie epików
    odbywa się osobno (poza pipeline'em LLM) — przez `JiraDCClient.create_issue()`
    wywołane z routera REST po HITL approval.
    """
    if get_jira_client() is None:
        return []
    return [
        FunctionTool(func=jira_get_issue),
        FunctionTool(func=jira_search),
        FunctionTool(func=jira_get_comments),
    ]
