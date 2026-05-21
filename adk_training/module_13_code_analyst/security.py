"""
Security helpers — walidacja ścieżek, nazw branchy, sanityzacja wejść.
=====================================================================
Moduł centralizuje kontrole bezpieczeństwa używane przez narzędzia agenta
(file_tools, git_tools, build_tools) oraz warstwę web.
"""

from __future__ import annotations

import os
import re
from typing import Optional


# =============================================================================
# Path safety
# =============================================================================

class PathSecurityError(ValueError):
    """Naruszenie granic bezpieczeństwa ścieżki (traversal / symlink / absolute)."""


def safe_resolve(repo_path: str, relative_path: str) -> str:
    """
    Rozwiąż ścieżkę względną do absolutnej w obrębie `repo_path`, odpornie na symlinki.

    Używa ``os.path.realpath`` po obu stronach i porównuje z separatorem, aby
    zapobiec atakom typu ``/repo_prefix_evil`` współdzielącym prefiks.

    Args:
        repo_path: Absolutna ścieżka do repozytorium (zostanie przerobiona przez realpath).
        relative_path: Ścieżka użytkownika — może być relatywna lub absolutna (odrzucona).

    Returns:
        Absolutna, realna ścieżka w obrębie repo.

    Raises:
        PathSecurityError: gdy ścieżka wychodzi poza repo, jest pusta lub zawiera NUL.
    """
    if not relative_path or "\x00" in relative_path:
        raise PathSecurityError("Niepoprawna ścieżka (pusta lub zawiera NUL).")

    # Odrzuć ścieżki absolutne (agent nie powinien nigdy podać /etc/passwd itp.)
    if os.path.isabs(relative_path):
        raise PathSecurityError("Ścieżka absolutna jest niedozwolona — użyj relatywnej.")

    repo_real = os.path.realpath(repo_path)
    candidate = os.path.realpath(os.path.join(repo_real, relative_path))

    # `os.sep` zapewnia że /repo/x nie jest prefiksem /repo-evil/y
    if not (candidate == repo_real or candidate.startswith(repo_real + os.sep)):
        raise PathSecurityError(
            f"Ścieżka poza repozytorium — odmowa dostępu: {relative_path}"
        )
    return candidate


def is_within(repo_path: str, candidate_path: str) -> bool:
    """Zwraca True gdy `candidate_path` leży wewnątrz `repo_path` (po realpath)."""
    try:
        safe_resolve(repo_path, os.path.relpath(candidate_path, repo_path))
        return True
    except (PathSecurityError, ValueError):
        return False


# =============================================================================
# Branch / commit message validation (git)
# =============================================================================

_BRANCH_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_./-]{1,99}$")
_BRANCH_FORBIDDEN_SUBSTR = ("..", " ", "\t", "\n", "\\")
_BRANCH_PROTECTED = frozenset(
    {"main", "master", "develop", "release", "production", "prod"}
)


def validate_branch_name(name: str) -> str:
    """
    Waliduj nazwę gałęzi git. Zwraca oczyszczoną nazwę lub rzuca ValueError.
    """
    if not name:
        raise ValueError("Nazwa brancha nie może być pusta.")
    name = name.strip()
    if len(name) > 100:
        raise ValueError("Nazwa brancha za długa (max 100 znaków).")
    if any(s in name for s in _BRANCH_FORBIDDEN_SUBSTR):
        raise ValueError("Nazwa brancha zawiera niedozwolone znaki.")
    if not _BRANCH_PATTERN.match(name):
        raise ValueError(
            "Nazwa brancha musi pasować do [A-Za-z0-9][A-Za-z0-9_./-]{1,99}"
        )
    if name.lower() in _BRANCH_PROTECTED:
        raise ValueError(f"Branch '{name}' jest chroniony — wybierz inną nazwę.")
    return name


def is_protected_branch(name: str) -> bool:
    return name.strip().lower() in _BRANCH_PROTECTED


_COMMIT_MSG_MAX = 2000


def validate_commit_message(msg: str) -> str:
    if not msg or not msg.strip():
        raise ValueError("Wiadomość commita nie może być pusta.")
    msg = msg.strip()
    if len(msg) > _COMMIT_MSG_MAX:
        raise ValueError(f"Wiadomość commita za długa (max {_COMMIT_MSG_MAX} znaków).")
    # Zablokuj znaki kontrolne (poza \n, \t)
    if any((ord(c) < 32 and c not in "\n\t") for c in msg):
        raise ValueError("Wiadomość commita zawiera niedozwolone znaki kontrolne.")
    return msg


# =============================================================================
# User input sanitization (prompt injection mitigation)
# =============================================================================

_USER_INPUT_MAX = 2000


def sanitize_user_input(text: str) -> str:
    """
    Oczyść input użytkownika przed wstrzyknięciem do promptu LLM.

    - Przycina do ``_USER_INPUT_MAX`` znaków.
    - Usuwa znaki kontrolne (poza whitespace).
    - Zamienia ``{`` i ``}`` na bezpieczne odpowiedniki (ochrona przed .format()).

    Nie zastępuje warstwy "user content as data" — to komplementarna ochrona.
    """
    if text is None:
        return ""
    text = str(text)[:_USER_INPUT_MAX]
    text = "".join(c for c in text if c.isprintable() or c in "\n\t ")
    text = text.replace("{", "{{").replace("}", "}}")
    return text.strip()


# =============================================================================
# Repo path scan exclusions (nie indeksuj sekretów)
# =============================================================================

SECRET_FILE_NAMES = frozenset({
    ".env", ".env.local", ".env.production", ".env.template",
    "credentials.json", "service-account.json", "id_rsa", "id_ed25519",
    ".netrc", ".pgpass",
})


def is_secret_file(filename: str) -> bool:
    """Czy plik wygląda jak plik z sekretami (do pominięcia w indeksacji)."""
    base = os.path.basename(filename).lower()
    return base in SECRET_FILE_NAMES or base.endswith(".pem") or base.endswith(".key")
