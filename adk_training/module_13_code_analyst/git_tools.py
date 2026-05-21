"""
Git Tools — bezpieczne lokalne operacje git (subprocess, shell=False).
======================================================================
Agent tworzy branche i commituje, NIGDY nie mergeuje i nie pushuje.
Nazwa brancha i wiadomość commita walidowane w :mod:`security`.
"""

from __future__ import annotations

import subprocess
from typing import Any

from config import get_settings
from logging_config import get_logger
from security import (
    is_protected_branch,
    validate_branch_name,
    validate_commit_message,
)

log = get_logger(__name__)


def _ok(**payload: Any) -> dict:
    return {"ok": True, **payload}


def _err(message: str, **extra: Any) -> dict:
    return {"ok": False, "error": message, **extra}


def _run_git(repo_path: str, *args: str, check: bool = True) -> str:
    """Uruchom `git <args>` w repo. shell=False. Timeout z konfiguracji."""
    settings = get_settings()
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True,
        timeout=settings.git_timeout,
        shell=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def git_status(repo_path: str) -> dict:
    """Status git: branch, zmodyfikowane/untracked pliki."""
    try:
        branch = _run_git(repo_path, "rev-parse", "--abbrev-ref", "HEAD")
    except (RuntimeError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        return _err(f"Nie git repo lub git niedostępny: {e}", is_git=False)

    try:
        status_raw = _run_git(repo_path, "status", "--porcelain")
    except (RuntimeError, subprocess.TimeoutExpired) as e:
        return _err(f"git status failed: {e}", is_git=True)

    lines = [l for l in status_raw.splitlines() if l.strip()]
    changed = [l[3:] for l in lines if l[:2].strip() and l[0] != "?"]
    untracked = [l[3:] for l in lines if l.startswith("??")]
    return _ok(
        is_git=True,
        branch=branch,
        changed_files=changed,
        untracked_files=untracked,
        is_clean=len(lines) == 0,
    )


def git_create_branch(repo_path: str, branch_name: str) -> dict:
    """Utwórz i przejdź na nowy feature branch. Waliduje nazwę."""
    try:
        branch_name = validate_branch_name(branch_name)
    except ValueError as e:
        log.warning("git_create_branch rejected name %r: %s", branch_name, e)
        return _err(str(e))

    try:
        prev_branch = _run_git(repo_path, "rev-parse", "--abbrev-ref", "HEAD")
        existing = _run_git(repo_path, "branch", "--list", branch_name, check=False)
        if existing.strip():
            return _err(
                f"Branch '{branch_name}' już istnieje",
                previous_branch=prev_branch,
            )
        _run_git(repo_path, "checkout", "-b", branch_name)
    except (RuntimeError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return _err(f"git create branch failed: {e}")

    log.info("git_create_branch: %s -> %s", prev_branch, branch_name)
    return _ok(
        branch=branch_name,
        previous_branch=prev_branch,
        message=f"Utworzono i przełączono na branch '{branch_name}'",
    )


def git_commit(repo_path: str, message: str, files: str = "") -> dict:
    """Commit na aktualnym (feature) branchu. Blokada main/master/develop/release."""
    try:
        message = validate_commit_message(message)
    except ValueError as e:
        return _err(str(e))

    try:
        branch = _run_git(repo_path, "rev-parse", "--abbrev-ref", "HEAD")
    except (RuntimeError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return _err(f"git rev-parse failed: {e}")

    if is_protected_branch(branch):
        return _err(
            f"ZABRONIONE: commit na chronionym branchu '{branch}'. "
            "Najpierw utwórz feature branch.",
            branch=branch,
        )

    try:
        if files.strip():
            for f in files.split(","):
                f = f.strip()
                if f:
                    _run_git(repo_path, "add", "--", f)
        else:
            _run_git(repo_path, "add", "-A")

        staged = _run_git(repo_path, "diff", "--cached", "--name-only")
        if not staged.strip():
            return _err("Brak zmian do commitowania", branch=branch)

        _run_git(repo_path, "commit", "-m", message)
        commit_hash = _run_git(repo_path, "rev-parse", "--short", "HEAD")
    except (RuntimeError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return _err(f"git commit failed: {e}", branch=branch)

    log.info("git_commit: %s @ %s", commit_hash, branch)
    return _ok(
        branch=branch,
        commit=commit_hash,
        message=message,
        files=staged.strip().splitlines(),
    )


def git_diff(repo_path: str, file_path: str = "") -> dict:
    """Diff bieżących zmian (staged + unstaged)."""
    base_args = ["diff"]
    target_args: list[str] = []
    if file_path.strip():
        target_args = ["--", file_path.strip()]

    try:
        diff_unstaged = _run_git(repo_path, *base_args, *target_args, check=False)
        diff_staged = _run_git(repo_path, *base_args, "--cached", *target_args, check=False)
    except (RuntimeError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return _err(f"git diff failed: {e}")

    combined = ""
    if diff_staged:
        combined += "=== STAGED ===\n" + diff_staged + "\n"
    if diff_unstaged:
        combined += "=== UNSTAGED ===\n" + diff_unstaged + "\n"

    return _ok(
        diff=combined or "(brak zmian)",
        has_changes=bool(diff_staged or diff_unstaged),
    )


def git_log(repo_path: str, count: int = 10) -> dict:
    """Ostatnie commity (max 50)."""
    count = max(1, min(count, 50))
    try:
        log_out = _run_git(
            repo_path, "log", f"-{count}", "--oneline", "--decorate", check=False
        )
    except (RuntimeError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return _err(f"git log failed: {e}")
    lines = log_out.splitlines() if log_out else []
    return _ok(commits=lines, count=len(lines))


def git_checkout_back(repo_path: str, branch_name: str) -> dict:
    """Przełącz na istniejący branch (np. main) po skończeniu pracy."""
    try:
        branch_name = branch_name.strip()
        if not branch_name:
            return _err("Nazwa brancha pusta.")
        # Dla checkout_back dopuszczamy chronione nazwy (powrót na main)
        if any(c in branch_name for c in (" ", "\n", "\t", "\\", "..", ";", "|", "&")):
            return _err("Niedozwolone znaki w nazwie brancha.")
        _run_git(repo_path, "checkout", branch_name)
        current = _run_git(repo_path, "rev-parse", "--abbrev-ref", "HEAD")
    except (RuntimeError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return _err(f"git checkout failed: {e}")
    return _ok(branch=current, message=f"Przełączono na '{current}'")
