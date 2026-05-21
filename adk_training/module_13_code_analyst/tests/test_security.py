"""Testy bezpieczenstwa sciezek i walidacji wejsc."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from security import (  # noqa: E402
    PathSecurityError,
    is_protected_branch,
    is_secret_file,
    safe_resolve,
    sanitize_user_input,
    validate_branch_name,
    validate_commit_message,
)


@pytest.fixture
def repo(tmp_path: Path) -> str:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "ok.py").write_text("print('ok')", encoding="utf-8")
    return str(tmp_path)


class TestSafeResolve:
    def test_resolves_normal_file(self, repo: str):
        p = safe_resolve(repo, "src/ok.py")
        assert p.endswith(os.path.join("src", "ok.py"))

    def test_rejects_absolute(self, repo: str):
        with pytest.raises(PathSecurityError):
            safe_resolve(repo, "/etc/passwd")

    def test_rejects_traversal(self, repo: str):
        with pytest.raises(PathSecurityError):
            safe_resolve(repo, "../../etc/passwd")

    def test_rejects_null_byte(self, repo: str):
        with pytest.raises(PathSecurityError):
            safe_resolve(repo, "src/ok\x00.py")

    def test_rejects_empty(self, repo: str):
        with pytest.raises(PathSecurityError):
            safe_resolve(repo, "")

    def test_blocks_symlink_escape(self, tmp_path: Path):
        repo = tmp_path / "repo"
        outside = tmp_path / "outside"
        repo.mkdir()
        outside.mkdir()
        (outside / "secret.txt").write_text("sekret")
        link = repo / "link_to_secret"
        try:
            os.symlink(str(outside / "secret.txt"), str(link))
        except (OSError, NotImplementedError):
            pytest.skip("symlinks nie sa dostepne")
        with pytest.raises(PathSecurityError):
            safe_resolve(str(repo), "link_to_secret")

    def test_prefix_trap(self, tmp_path: Path):
        """`/repo` nie powinno pozwolic na dostep do `/repo-evil`."""
        repo = tmp_path / "repo"
        evil = tmp_path / "repo-evil"
        repo.mkdir()
        evil.mkdir()
        (evil / "f.txt").write_text("x")
        # Odwolanie do siostry przez `..` musi byc zablokowane
        with pytest.raises(PathSecurityError):
            safe_resolve(str(repo), "../repo-evil/f.txt")


class TestBranchName:
    @pytest.mark.parametrize("name", ["feat/nowa", "fix/issue-123", "tests/abc.1"])
    def test_valid(self, name: str):
        assert validate_branch_name(name) == name

    @pytest.mark.parametrize(
        "name",
        ["", "main", "develop", "feat ..etc", "feat/$(whoami)",
         "feat/;rm -rf", "feat\nnewline", "a" * 101],
    )
    def test_invalid(self, name: str):
        with pytest.raises(ValueError):
            validate_branch_name(name)

    def test_protected_detection(self):
        assert is_protected_branch("main")
        assert is_protected_branch("MAIN")
        assert not is_protected_branch("feat/x")


class TestCommitMessage:
    def test_valid(self):
        assert validate_commit_message("feat: ok") == "feat: ok"

    def test_empty(self):
        with pytest.raises(ValueError):
            validate_commit_message("   ")

    def test_too_long(self):
        with pytest.raises(ValueError):
            validate_commit_message("x" * 3000)

    def test_control_chars(self):
        with pytest.raises(ValueError):
            validate_commit_message("ok\x07bell")


class TestSanitizeUserInput:
    def test_truncates(self):
        out = sanitize_user_input("a" * 5000)
        assert len(out) <= 2001  # +- margines po strip

    def test_escapes_braces(self):
        out = sanitize_user_input("{malicious} template")
        assert "{{" in out and "}}" in out

    def test_removes_control(self):
        out = sanitize_user_input("hello\x00world")
        assert "\x00" not in out

    def test_none(self):
        assert sanitize_user_input(None) == ""  # type: ignore[arg-type]


class TestSecretFileDetection:
    @pytest.mark.parametrize(
        "name",
        [".env", ".env.production", "id_rsa", "server.key", "priv.pem"],
    )
    def test_secret_detected(self, name: str):
        assert is_secret_file(name)

    @pytest.mark.parametrize("name", ["README.md", "app.py", "config.toml"])
    def test_normal(self, name: str):
        assert not is_secret_file(name)
