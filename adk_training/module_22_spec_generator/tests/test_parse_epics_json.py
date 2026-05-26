"""Testy `parse_epics_json` — helper ktory ujednolica wyjscie epic_decomposera."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.spec_generator import parse_epics_json  # noqa: E402


EPIC = {
    "title": "Szkielet API",
    "summary": "Endpoint /api/v1/report.",
    "acceptance_criteria": ["GIVEN ... WHEN ... THEN ..."],
    "priority": "High",
    "labels": ["backend"],
    "estimated_story_points": 8,
    "dependencies": [],
}


def test_should_return_empty_list_for_none():
    assert parse_epics_json(None) == []


def test_should_return_empty_list_for_empty_string():
    assert parse_epics_json("") == []


def test_should_parse_plain_json_list():
    raw = '[{"title":"E1","acceptance_criteria":[]}]'
    out = parse_epics_json(raw)
    assert len(out) == 1
    assert out[0]["title"] == "E1"


def test_should_parse_dict_with_epics_key():
    raw = '{"epics": [{"title":"E1","acceptance_criteria":[]}]}'
    out = parse_epics_json(raw)
    assert len(out) == 1
    assert out[0]["title"] == "E1"


def test_should_strip_markdown_json_fence():
    raw = '```json\n{"epics": [{"title":"E1","acceptance_criteria":[]}]}\n```'
    out = parse_epics_json(raw)
    assert len(out) == 1


def test_should_strip_plain_markdown_fence():
    raw = '```\n[{"title":"E1","acceptance_criteria":[]}]\n```'
    out = parse_epics_json(raw)
    assert len(out) == 1


def test_should_return_empty_for_malformed_json():
    assert parse_epics_json("to nie jest JSON") == []


def test_should_accept_list_directly():
    assert parse_epics_json([EPIC])[0]["title"] == "Szkielet API"


def test_should_accept_dict_directly():
    assert parse_epics_json({"epics": [EPIC]})[0]["title"] == "Szkielet API"


def test_should_filter_non_dict_entries():
    raw = '[{"title":"E1","acceptance_criteria":[]}, "bad", 123]'
    out = parse_epics_json(raw)
    assert len(out) == 1
    assert out[0]["title"] == "E1"


def test_should_handle_real_gemini_output_with_fence_and_epics_wrapper():
    """Odtwarza realny format zwracany przez Gemini (zaobserwowany w live test)."""
    raw = (
        '```json\n'
        '{\n'
        '  "epics": [\n'
        '    {\n'
        '      "title": "Utworzenie szkieletu API",\n'
        '      "summary": "Endpoint szkielet.",\n'
        '      "acceptance_criteria": ["GIVEN a WHEN b THEN c"],\n'
        '      "priority": "High",\n'
        '      "labels": ["api"],\n'
        '      "estimated_story_points": 5,\n'
        '      "dependencies": []\n'
        '    }\n'
        '  ]\n'
        '}\n'
        '```'
    )
    out = parse_epics_json(raw)
    assert len(out) == 1
    assert out[0]["title"] == "Utworzenie szkieletu API"
    assert out[0]["acceptance_criteria"] == ["GIVEN a WHEN b THEN c"]
