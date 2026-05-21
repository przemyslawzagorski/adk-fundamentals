"""Testy konfiguracji (pydantic-settings walidacja)."""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("CODE_ANALYST_PORT", raising=False)
    monkeypatch.delenv("CODE_ANALYST_CHUNK_SIZE", raising=False)
    # Importuj po wyczyszczeniu ENV
    from config import Settings  # noqa: WPS433
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.port == 8088
    assert s.chunk_size == 768
    assert 0.0 <= s.similarity_cutoff <= 1.0


def test_settings_invalid_port(monkeypatch: pytest.MonkeyPatch):
    from config import Settings  # noqa: WPS433
    with pytest.raises(Exception):
        Settings(_env_file=None, CODE_ANALYST_PORT=99999)  # type: ignore[call-arg]


def test_settings_invalid_loglevel(monkeypatch: pytest.MonkeyPatch):
    from config import Settings  # noqa: WPS433
    with pytest.raises(Exception):
        Settings(_env_file=None, CODE_ANALYST_LOG_LEVEL="BOGUS")  # type: ignore[call-arg]
