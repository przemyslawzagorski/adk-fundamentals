"""Notebook Library — zarządzanie katalogiem notebooków."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict

from ..config import CONFIG


@dataclass
class NotebookEntry:
    id: str
    url: str
    name: str
    description: str = ""
    topics: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    added_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used: str = field(default_factory=lambda: datetime.now().isoformat())
    use_count: int = 0


@dataclass
class Library:
    notebooks: list[NotebookEntry] = field(default_factory=list)
    active_notebook_id: Optional[str] = None
    version: str = "2.0.0"


class NotebookLibrary:
    """Zarządzanie katalogiem notebooków NotebookLM."""

    def __init__(self, library_path: Optional[str] = None):
        self._path = Path(library_path or CONFIG.library_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._library = self._load()

    def _load(self) -> Library:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                notebooks = [NotebookEntry(**n) for n in data.get("notebooks", [])]
                return Library(
                    notebooks=notebooks,
                    active_notebook_id=data.get("active_notebook_id"),
                    version=data.get("version", "2.0.0"),
                )
            except Exception:
                pass

        lib = Library()
        # Import domyślnego notebooka z konfiguracji
        if CONFIG.default_notebook_url:
            lib.notebooks.append(NotebookEntry(
                id="default",
                url=CONFIG.default_notebook_url,
                name="Default Notebook",
                description="Domyślny notebook z konfiguracji",
            ))
            lib.active_notebook_id = "default"
        self._save(lib)
        return lib

    def _save(self, lib: Optional[Library] = None) -> None:
        lib = lib or self._library
        data = {
            "notebooks": [asdict(n) for n in lib.notebooks],
            "active_notebook_id": lib.active_notebook_id,
            "version": lib.version,
        }
        self._path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _gen_id(self, name: str) -> str:
        import re
        base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:30]
        candidate = base
        counter = 1
        existing = {n.id for n in self._library.notebooks}
        while candidate in existing:
            candidate = f"{base}-{counter}"
            counter += 1
        return candidate

    def add(self, url: str, name: str, description: str = "", topics: list[str] | None = None, tags: list[str] | None = None) -> NotebookEntry:
        entry = NotebookEntry(
            id=self._gen_id(name),
            url=url,
            name=name,
            description=description,
            topics=topics or [],
            tags=tags or [],
        )
        self._library.notebooks.append(entry)
        if len(self._library.notebooks) == 1:
            self._library.active_notebook_id = entry.id
        self._save()
        return entry

    def list_all(self) -> list[NotebookEntry]:
        return self._library.notebooks

    def get(self, notebook_id: str) -> Optional[NotebookEntry]:
        return next((n for n in self._library.notebooks if n.id == notebook_id), None)

    def get_active(self) -> Optional[NotebookEntry]:
        if not self._library.active_notebook_id:
            return None
        return self.get(self._library.active_notebook_id)

    def select(self, notebook_id: str) -> NotebookEntry:
        entry = self.get(notebook_id)
        if not entry:
            raise ValueError(f"Notebook '{notebook_id}' not found")
        self._library.active_notebook_id = notebook_id
        entry.last_used = datetime.now().isoformat()
        self._save()
        return entry

    def remove(self, notebook_id: str) -> bool:
        before = len(self._library.notebooks)
        self._library.notebooks = [n for n in self._library.notebooks if n.id != notebook_id]
        if self._library.active_notebook_id == notebook_id:
            self._library.active_notebook_id = (
                self._library.notebooks[0].id if self._library.notebooks else None
            )
        if len(self._library.notebooks) < before:
            self._save()
            return True
        return False

    def increment_use(self, notebook_id: str) -> None:
        entry = self.get(notebook_id)
        if entry:
            entry.use_count += 1
            entry.last_used = datetime.now().isoformat()
            self._save()

    def describe_for_prompt(self) -> str:
        """Generuje opis biblioteki do wstrzyknięcia w prompt agenta."""
        if not self._library.notebooks:
            return "Brak notebooków w bibliotece."
        lines = ["Dostępne notebooki NotebookLM:"]
        for n in self._library.notebooks:
            active = " [AKTYWNY]" if n.id == self._library.active_notebook_id else ""
            lines.append(f"  - {n.name} (id={n.id}){active}: {n.description}")
            if n.topics:
                lines.append(f"    Tematy: {', '.join(n.topics)}")
        return "\n".join(lines)
