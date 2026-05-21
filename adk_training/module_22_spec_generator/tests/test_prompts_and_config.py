"""Testy offline - prompts i config."""

from __future__ import annotations

import pytest

from agents.prompt_loader import load_prompt


def test_load_prompt_hld_pl_has_sections():
    text = load_prompt("hld_pl")
    assert "Cel biznesowy" in text
    assert "Security" in text
    assert "Ryzyka" in text


def test_load_prompt_critic_pl_contains_lgtm_token():
    text = load_prompt("critic_pl")
    assert "LGTM" in text


def test_load_prompt_epic_decomposer_enforces_json():
    text = load_prompt("epic_decomposer_pl")
    assert "DOKLADNIE JSON" in text
    assert "acceptance_criteria" in text


def test_load_prompt_missing_raises():
    with pytest.raises(FileNotFoundError):
        load_prompt("nie_istnieje_xyz")


def test_config_defaults():
    import os
    # zapewniamy ze wartosci default nie krzyczą o braku ENV
    for k in [
        "SPEC_GEN_LLM_MODEL", "SPEC_GEN_MAX_CRITIQUE_ITERATIONS",
        "COMARCH_MCP_JIRA_URL", "COMARCH_MCP_JIRA_TOKEN",
        "NOTEBOOKLM_ENABLED",
    ]:
        os.environ.pop(k, None)

    # lru_cache na get_settings — wyczysc
    from config import get_settings
    get_settings.cache_clear()
    s = get_settings()
    assert s.llm_model == "gemini-2.5-pro"
    assert s.max_critique_iterations == 3
    assert s.has_mcp_jira is False
    assert s.notebooklm_enabled is False
