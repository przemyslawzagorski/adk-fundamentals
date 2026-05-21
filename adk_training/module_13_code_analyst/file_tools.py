"""
File Tools — bezpieczny odczyt/zapis plików projektu przez agenta.
==================================================================
RAG zwraca fragmenty; te narzędzia dają pełny plik oraz edycję na dysku.

Każda operacja przechodzi przez :func:`security.safe_resolve` —
ochrona przed path traversal (w tym symlinkami).
"""

from __future__ import annotations

import os

from logging_config import get_logger
from security import PathSecurityError, is_secret_file, safe_resolve

log = get_logger(__name__)

MAX_READ_CHARS = 50_000
MAX_LIST_FILES = 500
MAX_WRITE_BYTES = 2_000_000  # 2 MB

_SKIP_DIRS = frozenset({
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "target", "build", "dist", ".idea", ".vscode",
    ".mypy_cache", ".pytest_cache",
})


def _ok(**payload) -> dict:
    return {"ok": True, **payload}


def _err(message: str, **extra) -> dict:
    return {"ok": False, "error": message, **extra}


def read_project_file(repo_path: str, file_path: str) -> dict:
    """
    Odczytaj pełną zawartość pliku z projektu (z ograniczeniem rozmiaru).

    Args:
        repo_path: Ścieżka do repozytorium.
        file_path: Ścieżka względna (np. ``src/main/java/App.java``).
    """
    try:
        full_path = safe_resolve(repo_path, file_path)
    except PathSecurityError as e:
        log.warning("read_project_file blocked: %s", e)
        return _err(str(e))

    if is_secret_file(full_path):
        return _err("Odmowa odczytu pliku z sekretami.")

    if not os.path.isfile(full_path):
        return _err(f"Plik nie istnieje: {file_path}")

    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError as e:
        return _err(f"Nie można odczytać pliku: {e}")

    truncated = len(content) > MAX_READ_CHARS
    if truncated:
        content = content[:MAX_READ_CHARS] + "\n\n... [PLIK OBCIĘTY — za duży] ..."

    return _ok(
        file_path=file_path,
        content=content,
        lines_count=content.count("\n") + 1,
        truncated=truncated,
    )


def write_project_file(repo_path: str, file_path: str, content: str) -> dict:
    """
    Zapisz lub utwórz plik w projekcie.

    WAŻNE: zawsze sprawdź że jesteś na feature branchu — nie commituj na main.
    Odmawia zapisu plików wyglądających jak sekrety (``.env``, ``id_rsa`` itp.).
    """
    try:
        full_path = safe_resolve(repo_path, file_path)
    except PathSecurityError as e:
        log.warning("write_project_file blocked: %s", e)
        return _err(str(e))

    if is_secret_file(full_path):
        return _err("Odmowa zapisu do pliku z sekretami.")

    if len(content.encode("utf-8", errors="replace")) > MAX_WRITE_BYTES:
        return _err(f"Plik za duży — limit {MAX_WRITE_BYTES} bajtów.")

    is_new = not os.path.exists(full_path)
    dir_path = os.path.dirname(full_path)

    if dir_path:
        try:
            os.makedirs(dir_path, exist_ok=True)
        except OSError as e:
            return _err(f"Nie można utworzyć katalogu: {e}")
        repo_real = os.path.realpath(repo_path)
        if not os.path.realpath(dir_path).startswith(repo_real):
            return _err("Utworzono symlink poza repo — odmowa zapisu.")

    try:
        with open(full_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    except OSError as e:
        return _err(f"Nie można zapisać pliku: {e}")

    log.info("write_project_file: %s (new=%s, %d bytes)", file_path, is_new, len(content))
    return _ok(
        file_path=file_path,
        lines_written=content.count("\n") + 1,
        is_new=is_new,
        message=f"{'Utworzono' if is_new else 'Zaktualizowano'} {file_path}",
    )


def list_project_files(
    repo_path: str,
    directory: str = "",
    extensions: str = "",
) -> dict:
    """
    Wylistuj pliki w katalogu projektu (filtr po rozszerzeniach).
    """
    try:
        target = safe_resolve(repo_path, directory or ".")
    except PathSecurityError as e:
        return _err(str(e))

    if not os.path.isdir(target):
        return _err(f"Katalog nie istnieje: {directory or '(root)'}")

    ext_filter: set[str] = set()
    if extensions.strip():
        for e in extensions.split(","):
            e = e.strip()
            if not e:
                continue
            if not e.startswith("."):
                e = "." + e
            ext_filter.add(e.lower())

    files: list[str] = []
    repo_real = os.path.realpath(repo_path)

    for root, dirs, filenames in os.walk(target, followlinks=False):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for fname in filenames:
            if is_secret_file(fname):
                continue
            if ext_filter and not any(fname.lower().endswith(e) for e in ext_filter):
                continue
            rel = os.path.relpath(os.path.join(root, fname), repo_real)
            files.append(rel.replace("\\", "/"))
            if len(files) > MAX_LIST_FILES:
                break
        if len(files) > MAX_LIST_FILES:
            break

    truncated = len(files) > MAX_LIST_FILES
    return _ok(
        directory=directory or "(root)",
        files=sorted(files[:MAX_LIST_FILES]),
        count=len(files),
        truncated=truncated,
    )
