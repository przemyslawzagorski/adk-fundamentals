"""
Rejestr repozytoriow - zarzadza lista repo i ich metadanymi.
Dane persystowane w pliku JSON (repos.json).
"""

import os
import json
import uuid
import time
from dataclasses import dataclass, asdict
from typing import Optional

MAX_PATH_LENGTH = 500
MAX_NAME_LENGTH = 100


@dataclass
class RepoInfo:
    """Informacje o zarejestrowanym repozytorium."""

    id: str
    name: str
    path: str
    created_at: float
    last_indexed: Optional[float] = None
    total_chunks: int = 0
    indexed_files: int = 0
    status: str = "new"  # new | indexing | ready | error


class RepoManager:
    """Zarzadza rejestrem repozytoriow kodu (CRUD + walidacja sciezek)."""

    def __init__(self, data_dir: str):
        self.data_dir = os.path.abspath(data_dir)
        self.indices_dir = os.path.join(self.data_dir, "indices")
        self._registry_path = os.path.join(self.data_dir, "repos.json")
        os.makedirs(self.indices_dir, exist_ok=True)

    # --- Registry I/O ---

    def _load(self) -> dict[str, dict]:
        if os.path.exists(self._registry_path):
            try:
                with open(self._registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save(self, registry: dict[str, dict]):
        with open(self._registry_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)

    # --- Validation ---

    @staticmethod
    def validate_path(path: str) -> tuple[bool, str]:
        """Walidacja sciezki. Zwraca (ok, resolved_path | error_msg)."""
        if not path or not path.strip():
            return False, "Sciezka nie moze byc pusta"

        path = path.strip()
        if len(path) > MAX_PATH_LENGTH:
            return False, f"Sciezka za dluga (max {MAX_PATH_LENGTH} znakow)"

        resolved = os.path.realpath(path)

        if not os.path.exists(resolved):
            return False, f"Sciezka nie istnieje: {resolved}"

        if not os.path.isdir(resolved):
            return False, f"To nie jest katalog: {resolved}"

        return True, resolved

    @staticmethod
    def sanitize_name(name: str) -> str:
        """Oczysc nazwe repo z niebezpiecznych znakow."""
        name = name.strip()[:MAX_NAME_LENGTH]
        return "".join(c for c in name if c.isalnum() or c in " -_.")

    # --- CRUD ---

    def add(self, path: str, name: str = "") -> tuple[Optional[RepoInfo], str]:
        """Dodaj repo. Zwraca (RepoInfo | None, error_msg)."""
        valid, result = self.validate_path(path)
        if not valid:
            return None, result

        resolved = result

        # Duplikat?
        registry = self._load()
        for data in registry.values():
            if os.path.realpath(data["path"]) == resolved:
                return None, f"Repozytorium juz zarejestrowane: {data['name']}"

        repo_id = uuid.uuid4().hex[:8]
        repo_name = self.sanitize_name(name) or os.path.basename(resolved)

        repo = RepoInfo(
            id=repo_id,
            name=repo_name,
            path=resolved,
            created_at=time.time(),
        )

        registry[repo_id] = asdict(repo)
        self._save(registry)
        return repo, ""

    def remove(self, repo_id: str) -> bool:
        """Usun repo z rejestru (nie kasuje indeksu z dysku)."""
        registry = self._load()
        if repo_id not in registry:
            return False
        del registry[repo_id]
        self._save(registry)
        return True

    def get(self, repo_id: str) -> Optional[RepoInfo]:
        """Pobierz info o repo."""
        registry = self._load()
        data = registry.get(repo_id)
        return RepoInfo(**data) if data else None

    def list_all(self) -> list[RepoInfo]:
        """Lista wszystkich repozytoriow."""
        registry = self._load()
        return [RepoInfo(**d) for d in registry.values()]

    def update_stats(self, repo_id: str, stats: dict):
        """Aktualizuj statystyki po indeksowaniu."""
        registry = self._load()
        if repo_id in registry:
            registry[repo_id]["last_indexed"] = time.time()
            registry[repo_id]["total_chunks"] = stats.get("total_chunks", 0)
            registry[repo_id]["indexed_files"] = (
                stats.get("indexed", 0) + stats.get("skipped", 0)
            )
            registry[repo_id]["status"] = "ready"
            self._save(registry)

    def set_status(self, repo_id: str, status: str):
        """Ustaw status repo (new/indexing/ready/error)."""
        registry = self._load()
        if repo_id in registry:
            registry[repo_id]["status"] = status
            self._save(registry)

    def get_index_dir(self, repo_id: str) -> str:
        """Sciezka do katalogu indeksu danego repo."""
        return os.path.join(self.indices_dir, repo_id)
