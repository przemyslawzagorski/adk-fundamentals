"""
Jira REST API Client

Wrapper for Jira REST API v2.
Based on: https://developer.atlassian.com/cloud/jira/platform/rest/v2/intro
"""

import requests
import json
import os
import sys
import base64
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()


class JiraClient:
    """Client for Jira REST API v2. Supports Basic Auth (Atlassian Cloud) and Bearer Auth (on-premise)."""

    def __init__(self, base_url: str = None, token: str = None):
        """
        Initialize Jira client.

        Auth modes (controlled by JIRA_AUTH_TYPE env var):
          - "basic" (default for Atlassian Cloud): uses JIRA_USER_EMAIL + JIRA_API_TOKEN
          - "bearer": uses JIRA_BEARER_TOKEN (PAT / on-premise)

        Args:
            base_url: Jira base URL (e.g., https://mysite.atlassian.net/rest/api/2)
            token: Bearer token (used only when auth_type=bearer)
        """
        self.base_url = base_url or os.getenv("JIRA_BASE_URL")
        auth_type = os.getenv("JIRA_AUTH_TYPE", "basic").lower()

        if not self.base_url:
            raise ValueError("JIRA_BASE_URL must be set")

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if auth_type == "basic":
            email = os.getenv("JIRA_USER_EMAIL")
            api_token = os.getenv("JIRA_API_TOKEN")
            if not email or not api_token:
                raise ValueError(
                    "JIRA_AUTH_TYPE=basic requires JIRA_USER_EMAIL and JIRA_API_TOKEN. "
                    "Generate token at https://id.atlassian.com/manage-profile/security/api-tokens"
                )
            credentials = base64.b64encode(f"{email}:{api_token}".encode()).decode()
            self.headers["Authorization"] = f"Basic {credentials}"
        else:
            bearer = token or os.getenv("JIRA_BEARER_TOKEN")
            if not bearer:
                raise ValueError("JIRA_AUTH_TYPE=bearer requires JIRA_BEARER_TOKEN")
            self.headers["Authorization"] = f"Bearer {bearer}"

    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """
        Get info about a Jira ticket by ID.

        Args:
            ticket_id: Ticket ID (e.g., "CLM6-11588")

        Returns:
            dict: Ticket information
        """
        url = f"{self.base_url}/issue/{ticket_id}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            print(f"[OK] Successfully fetched ticket {ticket_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error fetching ticket {ticket_id}: {e}")
            return {"error": str(e), "ticket_id": ticket_id}

    def _get_api3_search_url(self) -> str:
        """Derive the /rest/api/3/search/jql URL from the configured base_url."""
        # base_url is e.g. https://x.atlassian.net/rest/api/2
        # We need       https://x.atlassian.net/rest/api/3/search/jql
        import re
        return re.sub(r'/rest/api/\d+$', '/rest/api/3', self.base_url)

    def search(self, jql: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search Jira tickets using JQL (Jira Query Language).

        Uses the new /rest/api/3/search/jql endpoint (GET) because
        the legacy POST /rest/api/2/search was removed (410 Gone) in 2025+.

        Args:
            jql: JQL query string (e.g., "project = CLM6 AND status = Open")
            limit: Maximum number of results (default: 10)

        Returns:
            list: List of matching tickets
        """
        api3_base = self._get_api3_search_url()
        url = f"{api3_base}/search/jql"
        params = {
            "jql": jql,
            "maxResults": limit,
            "fields": "summary,status,assignee,priority,created,updated"
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            issues = data.get("issues", [])
            print(f"[OK] Found {len(issues)} tickets matching JQL: {jql}")
            return issues
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error searching tickets: {e}")
            return []

    def my_open_tickets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get unresolved tickets assigned to current user, sorted by update.

        Args:
            limit: Maximum number of results (default: 10)

        Returns:
            list: List of open tickets
        """
        jql = "assignee = currentUser() AND resolution = Unresolved ORDER BY updated DESC"
        return self.search(jql, limit)

    def create_ticket(
        self,
        summary: str,
        description: str,
        project_key: str = None,
        issue_type: str = None,
        label: str = None
    ) -> Dict[str, Any]:
        """
        Create a new Jira ticket.

        Args:
            summary: Ticket summary/title
            description: Ticket description
            project_key: Project key (e.g., "CLM6"). Uses JIRA_DEFAULT_PROJECT_KEY if not provided
            issue_type: Issue type (e.g., "Story", "Task", "Bug"). Uses JIRA_DEFAULT_ISSUE_TYPE if not provided
            label: Label to add. Uses JIRA_DEFAULT_LABEL if not provided

        Returns:
            dict: Created ticket information
        """
        url = f"{self.base_url}/issue"

        project_key = project_key or os.getenv("JIRA_DEFAULT_PROJECT_KEY")
        issue_type = issue_type or os.getenv("JIRA_DEFAULT_ISSUE_TYPE", "Story")
        label = label or os.getenv("JIRA_DEFAULT_LABEL")

        if not project_key:
            return {"error": "project_key is required (set JIRA_DEFAULT_PROJECT_KEY or provide it)"}

        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type}
            }
        }

        if label:
            payload["fields"]["labels"] = [label]

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            print(f"[OK] Successfully created ticket: {data.get('key')}")
            return data
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error creating ticket: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return {"error": str(e)}

    def add_comment(self, ticket_id: str, comment: str) -> Dict[str, Any]:
        """
        Add a comment to a Jira ticket.

        Args:
            ticket_id: Ticket ID (e.g., "CLM6-11588")
            comment: Comment text

        Returns:
            dict: Comment information
        """
        url = f"{self.base_url}/issue/{ticket_id}/comment"
        payload = {"body": comment}

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            print(f"[OK] Successfully added comment to {ticket_id}")
            return data
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error adding comment to {ticket_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return {"error": str(e), "ticket_id": ticket_id}

