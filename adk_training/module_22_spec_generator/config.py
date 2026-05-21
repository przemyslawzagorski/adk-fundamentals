"""Konfiguracja modulu 22 - Spec Generator."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class SpecGenSettings:
    # --- Gemini / Vertex ---
    llm_model: str = os.environ.get("SPEC_GEN_LLM_MODEL", "gemini-2.5-pro")
    judge_model: str = os.environ.get("SPEC_GEN_JUDGE_MODEL", "gemini-2.0-flash")

    # --- Critique loop ---
    max_critique_iterations: int = int(
        os.environ.get("SPEC_GEN_MAX_CRITIQUE_ITERATIONS", "3")
    )

    # --- Comarch MCP ---
    jira_url: str = os.environ.get("COMARCH_MCP_JIRA_URL", "")
    jira_token: str = os.environ.get("COMARCH_MCP_JIRA_TOKEN", "")
    wiki_url: str = os.environ.get("COMARCH_MCP_WIKI_URL", "")
    wiki_token: str = os.environ.get("COMARCH_MCP_WIKI_TOKEN", "")
    gitlab_url: str = os.environ.get("COMARCH_MCP_GITLAB_URL", "")
    gitlab_token: str = os.environ.get("COMARCH_MCP_GITLAB_TOKEN", "")

    # --- NotebookLM (opcjonalne) ---
    notebooklm_enabled: bool = os.environ.get("NOTEBOOKLM_ENABLED", "0") == "1"
    notebooklm_notebook_id: str = os.environ.get("NOTEBOOKLM_NOTEBOOK_ID", "")

    @property
    def notebooklm_notebook_url(self) -> str:
        """Pelny URL notebooka — z ID lub z NOTEBOOK_URL env."""
        nid = self.notebooklm_notebook_id
        if nid:
            if nid.startswith("http"):
                return nid
            return f"https://notebooklm.google.com/notebook/{nid}"
        return os.environ.get("NOTEBOOK_URL", "")

    # --- Target Jira ---
    target_jira_project: str = os.environ.get("SPEC_GEN_TARGET_JIRA_PROJECT", "SANDBOX")

    # --- Web UI ---
    web_host: str = os.environ.get("SPEC_GEN_WEB_HOST", "127.0.0.1")
    web_port: int = int(os.environ.get("SPEC_GEN_WEB_PORT", "8766"))

    @property
    def has_mcp_jira(self) -> bool:
        return bool(self.jira_url and self.jira_token)

    @property
    def has_mcp_wiki(self) -> bool:
        return bool(self.wiki_url and self.wiki_token)

    @property
    def has_mcp_gitlab(self) -> bool:
        return bool(self.gitlab_url and self.gitlab_token)


@lru_cache(maxsize=1)
def get_settings() -> SpecGenSettings:
    return SpecGenSettings()
