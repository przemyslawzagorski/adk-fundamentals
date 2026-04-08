"""
Confluence Wiki REST API Client

Wrapper for Confluence Wiki REST API.
Based on: https://developer.atlassian.com/cloud/confluence/rest/v1/intro
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


class WikiClient:
    """Client for Confluence Wiki REST API. Supports Basic Auth (Atlassian Cloud) and Bearer Auth (on-premise)."""

    def __init__(self, base_url: str = None, token: str = None):
        """
        Initialize Wiki client.
        
        Auth modes (controlled by WIKI_AUTH_TYPE env var):
          - "basic" (default for Atlassian Cloud): uses WIKI_USER_EMAIL + WIKI_API_TOKEN
          - "bearer": uses WIKI_BEARER_TOKEN (PAT / on-premise)

        Args:
            base_url: Wiki base URL (e.g., https://mysite.atlassian.net/wiki/rest/api)
            token: Bearer token (used only when auth_type=bearer)
        """
        self.base_url = base_url or os.getenv("WIKI_BASE_URL")
        auth_type = os.getenv("WIKI_AUTH_TYPE", "basic").lower()

        if not self.base_url:
            raise ValueError("WIKI_BASE_URL must be set")

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if auth_type == "basic":
            email = os.getenv("WIKI_USER_EMAIL")
            api_token = os.getenv("WIKI_API_TOKEN")
            if not email or not api_token:
                raise ValueError(
                    "WIKI_AUTH_TYPE=basic requires WIKI_USER_EMAIL and WIKI_API_TOKEN. "
                    "Generate token at https://id.atlassian.com/manage-profile/security/api-tokens"
                )
            credentials = base64.b64encode(f"{email}:{api_token}".encode()).decode()
            self.headers["Authorization"] = f"Basic {credentials}"
        else:
            bearer = token or os.getenv("WIKI_BEARER_TOKEN")
            if not bearer:
                raise ValueError("WIKI_AUTH_TYPE=bearer requires WIKI_BEARER_TOKEN")
            self.headers["Authorization"] = f"Bearer {bearer}"

    def get_page(self, page_id: str) -> Dict[str, Any]:
        """
        Get info about a Confluence Wiki page by ID.
        
        Args:
            page_id: Page ID
            
        Returns:
            dict: Page information
        """
        url = f"{self.base_url}/content/{page_id}"
        params = {
            "expand": "body.storage,version,space"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            print(f"[OK] Successfully fetched page {page_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error fetching page {page_id}: {e}")
            return {"error": str(e), "page_id": page_id}
    
    def search(self, cql: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search Wiki content using CQL (Confluence Query Language).
        
        Args:
            cql: CQL query string (e.g., "type=page AND space=DEV")
            limit: Maximum number of results (default: 10)
            
        Returns:
            list: List of matching pages
        """
        url = f"{self.base_url}/content/search"
        params = {
            "cql": cql,
            "limit": limit,
            "expand": "content.space,content.version"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            print(f"[OK] Found {len(results)} pages matching CQL: {cql}")
            return results
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error searching pages: {e}")
            return []
    
    def get_page_by_url(self, url: str) -> Dict[str, Any]:
        """
        Get Wiki page info by URL.
        
        Args:
            url: Full Wiki page URL
            
        Returns:
            dict: Page information
        """
        # Extract page ID from URL
        # Example URL: https://wiki.example.com/pages/viewpage.action?pageId=123456
        # or: https://wiki.example.com/display/SPACE/Page+Title
        
        try:
            if "pageId=" in url:
                # Extract pageId from URL parameter
                page_id = url.split("pageId=")[1].split("&")[0]
                return self.get_page(page_id)
            elif "/display/" in url:
                # Extract space and title, then search
                parts = url.split("/display/")[1].split("/")
                if len(parts) >= 2:
                    space = parts[0]
                    title = parts[1].replace("+", " ")
                    cql = f'space="{space}" AND title="{title}"'
                    results = self.search(cql, limit=1)
                    if results:
                        return results[0]
                    else:
                        return {"error": "Page not found", "url": url}
            
            return {"error": "Unable to parse URL", "url": url}
        except Exception as e:
            print(f"[ERROR] Error getting page by URL: {e}")
            return {"error": str(e), "url": url}

