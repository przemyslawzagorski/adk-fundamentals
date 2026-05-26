"""Test strukturalny: spec_generator factory buduje poprawny SequentialAgent
bez wywolywania LLM (tylko konstruktor).
"""

from __future__ import annotations

import os

import pytest

# zapewniamy deterministyczne ENV
for k in [
    "COMARCH_MCP_JIRA_URL", "COMARCH_MCP_JIRA_TOKEN",
    "NOTEBOOKLM_ENABLED",
]:
    os.environ.pop(k, None)

from config import get_settings  # noqa: E402
get_settings.cache_clear()


def test_build_spec_generator_without_mcp_builds_valid_sequential():
    from agents.spec_generator import build_spec_generator
    agent = build_spec_generator(
        jira_tools=None, wiki_tools=None, gitlab_tools=None,
        notebooklm_tool=None, max_critique_iterations=2,
    )
    assert agent.name == "spec_generator"
    names = [sa.name for sa in agent.sub_agents]
    assert names == [
        "ticket_fetcher",
        "context_gatherer",
        "hld_writer",
        "critique_loop",
        "epic_decomposer",
    ]


def test_critique_loop_respects_max_iterations():
    from agents.critique_loop import build_critique_loop
    loop = build_critique_loop(max_iterations=5)
    assert loop.name == "critique_loop"
    assert loop.max_iterations == 5
    # critic + escalation_checker + reviser
    assert len(loop.sub_agents) == 3
    names = [sa.name for sa in loop.sub_agents]
    assert names == ["critic", "escalation_checker", "reviser"]


def test_critique_loop_clamps_to_safe_range():
    from agents.critique_loop import build_critique_loop
    assert build_critique_loop(max_iterations=0).max_iterations == 1
    assert build_critique_loop(max_iterations=999).max_iterations == 10
