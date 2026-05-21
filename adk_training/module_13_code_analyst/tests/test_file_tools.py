"""Testy narzedzi file_tools (path traversal, sekrety, limity)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from file_tools import (  # noqa: E402
    list_project_files,
    read_project_file,
    write_project_file,
)


@pytest.fixture
def repo(tmp_path: Path) -> str:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('hi')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# repo\n", encoding="utf-8")
    (tmp_path / ".env").write_text("SECRET=1\n", encoding="utf-8")
    return str(tmp_path)


class TestRead:
    def test_reads_normal(self, repo: str):
        r = read_project_file(repo, "README.md")
        assert r["ok"] is True
        assert "# repo" in r["content"]

    def test_blocks_traversal(self, repo: str):
        r = read_project_file(repo, "../secret.txt")
        assert r["ok"] is False

    def test_blocks_absolute(self, repo: str):
        r = read_project_file(repo, "/etc/passwd")
        assert r["ok"] is False

    def test_blocks_env(self, repo: str):
        r = read_project_file(repo, ".env")
        assert r["ok"] is False

    def test_missing_file(self, repo: str):
        r = read_project_file(repo, "nope.txt")
        assert r["ok"] is False


class TestWrite:
    def test_creates_new(self, repo: str):
        r = write_project_file(repo, "src/new.py", "x = 1\n")
        assert r["ok"] is True
        assert r["is_new"] is True
        assert (Path(repo) / "src" / "new.py").read_text() == "x = 1\n"

    def test_overwrites(self, repo: str):
        r = write_project_file(repo, "README.md", "updated\n")
        assert r["ok"] is True
        assert r["is_new"] is False

    def test_blocks_traversal(self, repo: str):
        r = write_project_file(repo, "../evil.txt", "x")
        assert r["ok"] is False

    def test_blocks_secret(self, repo: str):
        r = write_project_file(repo, ".env", "NEW=2")
        assert r["ok"] is False


class TestList:
    def test_lists_files(self, repo: str):
        r = list_project_files(repo, "", ".md,.py")
        assert r["ok"] is True
        names = r["files"]
        assert "README.md" in names
        assert "src/app.py" in names

    def test_skips_secrets(self, repo: str):
        r = list_project_files(repo, "")
        assert ".env" not in r["files"]

    def test_blocks_traversal(self, repo: str):
        r = list_project_files(repo, "../")
        assert r["ok"] is False
