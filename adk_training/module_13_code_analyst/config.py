"""
Konfiguracja centralna — pydantic-settings, walidacja przy starcie.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_MODULE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Ustawienia aplikacji ładowane z ENV / .env. Walidowane przy starcie."""

    model_config = SettingsConfigDict(
        env_file=str(_MODULE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Vertex AI ---
    google_cloud_project: str = Field(default="", alias="GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = Field(default="us-central1", alias="GOOGLE_CLOUD_LOCATION")
    google_genai_use_vertexai: str = Field(default="1", alias="GOOGLE_GENAI_USE_VERTEXAI")

    # --- Web server ---
    host: str = Field(default="127.0.0.1", alias="CODE_ANALYST_HOST")
    port: int = Field(default=8088, alias="CODE_ANALYST_PORT", ge=1, le=65535)
    data_dir: str = Field(
        default=str(_MODULE_DIR / "web_data"),
        alias="CODE_ANALYST_DATA",
    )
    reload: bool = Field(default=False, alias="CODE_ANALYST_RELOAD")

    # --- Auth / bezpieczeństwo ---
    api_key: Optional[str] = Field(default=None, alias="CODE_ANALYST_API_KEY")
    require_auth: bool = Field(default=False, alias="CODE_ANALYST_REQUIRE_AUTH")
    allowed_origins: str = Field(default="", alias="CODE_ANALYST_ALLOWED_ORIGINS")

    # --- Rate limits (requests/minute) ---
    rate_limit_index: str = Field(default="2/minute", alias="CODE_ANALYST_RATE_INDEX")
    rate_limit_search: str = Field(default="30/minute", alias="CODE_ANALYST_RATE_SEARCH")
    rate_limit_workflow: str = Field(default="10/minute", alias="CODE_ANALYST_RATE_WORKFLOW")

    # --- Logging ---
    log_level: str = Field(default="INFO", alias="CODE_ANALYST_LOG_LEVEL")
    log_json: bool = Field(default=False, alias="CODE_ANALYST_LOG_JSON")

    # --- RAG / indexing ---
    chunk_size: int = Field(default=768, alias="CODE_ANALYST_CHUNK_SIZE", ge=128, le=4096)
    chunk_overlap: int = Field(default=100, alias="CODE_ANALYST_CHUNK_OVERLAP", ge=0, le=1024)
    similarity_cutoff: float = Field(
        default=0.35,
        alias="CODE_ANALYST_SIMILARITY_CUTOFF",
        ge=0.0,
        le=1.0,
    )
    embedding_model: str = Field(
        default="text-embedding-005",
        alias="CODE_ANALYST_EMBED_MODEL",
    )

    # --- LLM ---
    llm_model: str = Field(default="gemini-2.0-flash", alias="CODE_ANALYST_LLM_MODEL")

    # --- MCP ---
    mcp_enabled: str = Field(default="auto", alias="MCP_ENABLED")
    github_personal_access_token: Optional[str] = Field(
        default=None, alias="GITHUB_PERSONAL_ACCESS_TOKEN"
    )
    jira_base_url: Optional[str] = Field(default=None, alias="JIRA_BASE_URL")
    jira_bearer_token: Optional[str] = Field(default=None, alias="JIRA_BEARER_TOKEN")

    # --- Sesje ---
    session_db_url: Optional[str] = Field(
        default=None, alias="CODE_ANALYST_SESSION_DB_URL",
        description="np. sqlite:///./web_data/sessions.db — jeśli puste używa InMemorySessionService",
    )
    session_ttl_seconds: int = Field(
        default=3600, alias="CODE_ANALYST_SESSION_TTL", ge=60
    )

    # --- Limity wykonania tooli ---
    git_timeout: int = Field(default=30, alias="CODE_ANALYST_GIT_TIMEOUT", ge=5, le=600)
    build_timeout: int = Field(default=180, alias="CODE_ANALYST_BUILD_TIMEOUT", ge=10, le=1800)
    test_timeout: int = Field(default=180, alias="CODE_ANALYST_TEST_TIMEOUT", ge=10, le=1800)
    max_py_compile_files: int = Field(
        default=1000, alias="CODE_ANALYST_MAX_PY_COMPILE", ge=10
    )

    @field_validator("log_level")
    @classmethod
    def _valid_log_level(cls, v: str) -> str:
        v = v.upper()
        if v not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError(f"Nieznany log_level: {v}")
        return v

    @property
    def allowed_origin_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton — walidacja przy pierwszym wywołaniu."""
    return Settings()
