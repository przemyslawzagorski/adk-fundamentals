"""
Code Indexer — persistent RAG z inkrementalnym reindeksowaniem.
=================================================================
- LlamaIndex SimpleVectorStore na dysku.
- Chunk size / overlap / similarity cutoff konfigurowalne (``config.Settings``).
- Wsparcie dla inwalidacji pojedynczego pliku (``mark_file_dirty``) —
  potrzebne po ``write_project_file`` aby RAG nie pracował na stale state.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Optional

from llama_index.core import (
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

from config import get_settings
from logging_config import get_logger
from security import is_secret_file

log = get_logger(__name__)

DEFAULT_EXTENSIONS = [
    ".py", ".java", ".ts", ".tsx", ".js", ".jsx",
    ".go", ".rs", ".kt", ".scala", ".rb",
    ".sql", ".yaml", ".yml", ".json", ".toml",
    ".md", ".txt", ".html", ".css",
]

DEFAULT_EXCLUDE_DIRS = frozenset({
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "build", "dist", "target", ".idea", ".vscode",
    ".mypy_cache", ".pytest_cache",
})

METADATA_FILE = "_index_metadata.json"


class CodeIndexer:
    """Indeksuje kod z persystencją (SimpleVectorStore + metadata.json)."""

    def __init__(
        self,
        project_dir: str,
        persist_dir: str = "./index_store",
        collection_name: str = "code_index",
        embedding_model: Optional[str] = None,
    ):
        settings = get_settings()
        self.project_dir = os.path.abspath(project_dir)
        self.persist_dir = os.path.abspath(persist_dir)
        self.collection_name = collection_name
        self.metadata_path = os.path.join(self.persist_dir, METADATA_FILE)

        self.embed_model = GoogleGenAIEmbedding(
            model=embedding_model or settings.embedding_model,
        )
        Settings.embed_model = self.embed_model

        self._chunk_size = settings.chunk_size
        self._chunk_overlap = settings.chunk_overlap
        self._similarity_cutoff = settings.similarity_cutoff
        self._index: Optional[VectorStoreIndex] = None

    # --- helpers ---

    def _has_persisted_index(self) -> bool:
        return os.path.exists(os.path.join(self.persist_dir, "docstore.json"))

    @property
    def index(self) -> Optional[VectorStoreIndex]:
        if self._index is None and self._has_persisted_index():
            storage_context = StorageContext.from_defaults(persist_dir=self.persist_dir)
            self._index = load_index_from_storage(
                storage_context, embed_model=self.embed_model
            )
            log.info("[indexer] loaded index from %s", self.persist_dir)
        return self._index

    @staticmethod
    def _file_hash(filepath: str) -> str:
        hasher = hashlib.md5(usedforsecurity=False)
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _load_metadata(self) -> dict:
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_metadata(self, metadata: dict) -> None:
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def _collect_files(
        self,
        extensions: list[str] | None = None,
        exclude_dirs: set[str] | None = None,
    ) -> list[str]:
        exts = set(extensions or DEFAULT_EXTENSIONS)
        excludes = set(exclude_dirs or DEFAULT_EXCLUDE_DIRS)
        files: list[str] = []
        for root, dirs, filenames in os.walk(self.project_dir, followlinks=False):
            dirs[:] = [d for d in dirs if d not in excludes]
            for filename in filenames:
                if is_secret_file(filename):
                    continue
                ext = os.path.splitext(filename)[1].lower()
                if ext in exts:
                    files.append(os.path.join(root, filename))
        return sorted(files)

    # --- public API ---

    def index_project(
        self,
        extensions: list[str] | None = None,
        exclude_dirs: set[str] | None = None,
        incremental: bool = True,
    ) -> dict:
        """Zindeksuj projekt. Inkrementalnie — tylko zmienione pliki."""
        start_time = time.time()
        all_files = self._collect_files(extensions, exclude_dirs)
        old_metadata = self._load_metadata() if incremental else {}
        new_metadata: dict[str, str] = {}

        files_to_index: list[str] = []
        skipped = 0
        for filepath in all_files:
            fhash = self._file_hash(filepath)
            rel = os.path.relpath(filepath, self.project_dir)
            new_metadata[rel] = fhash
            if incremental and old_metadata.get(rel) == fhash:
                skipped += 1
            else:
                files_to_index.append(filepath)

        removed_files = set(old_metadata.keys()) - set(new_metadata.keys())

        if not files_to_index and not removed_files:
            elapsed = time.time() - start_time
            log.info("[indexer] no changes (%.1fs, skipped=%d)", elapsed, skipped)
            return {
                "indexed": 0,
                "skipped": skipped,
                "removed": 0,
                "total_chunks": self._count_chunks(),
                "time_seconds": round(elapsed, 1),
            }

        log.info(
            "[indexer] indexing %d files (skipped=%d, removed=%d)",
            len(files_to_index), skipped, len(removed_files),
        )

        if files_to_index:
            documents = SimpleDirectoryReader(input_files=files_to_index).load_data()
            for doc in documents:
                rel = os.path.relpath(
                    doc.metadata.get("file_path", ""), self.project_dir
                )
                doc.metadata["relative_path"] = rel
                doc.metadata["extension"] = os.path.splitext(rel)[1]

            parser = SentenceSplitter(
                chunk_size=self._chunk_size,
                chunk_overlap=self._chunk_overlap,
            )
            nodes = parser.get_nodes_from_documents(documents)

            for node in nodes:
                node.embedding = self.embed_model.get_text_embedding(node.get_content())

            if self._index is None and not self._has_persisted_index():
                self._index = VectorStoreIndex(nodes=nodes, embed_model=self.embed_model)
            else:
                if self._index is None:
                    storage_context = StorageContext.from_defaults(
                        persist_dir=self.persist_dir
                    )
                    self._index = load_index_from_storage(
                        storage_context, embed_model=self.embed_model
                    )
                for node in nodes:
                    self._index.insert_nodes([node])

            self._index.storage_context.persist(persist_dir=self.persist_dir)

        self._save_metadata(new_metadata)

        elapsed = time.time() - start_time
        stats = {
            "indexed": len(files_to_index),
            "skipped": skipped,
            "removed": len(removed_files),
            "total_chunks": self._count_chunks(),
            "time_seconds": round(elapsed, 1),
        }
        log.info("[indexer] done: %s", stats)
        return stats

    def mark_file_dirty(self, relative_path: str) -> None:
        """Unieważnij wpis metadata dla pliku — wymusi reindeks przy następnym ``index_project``."""
        metadata = self._load_metadata()
        if relative_path in metadata:
            metadata.pop(relative_path, None)
            self._save_metadata(metadata)
            log.info("[indexer] marked dirty: %s", relative_path)

    def query(self, question: str, top_k: int = 5) -> list[dict]:
        """Semantyczne wyszukiwanie — filtrowane przez ``similarity_cutoff``."""
        idx = self.index
        if idx is None:
            return [{"error": "Indeks nie istnieje. Uruchom index_project() najpierw."}]

        retriever = idx.as_retriever(similarity_top_k=top_k)
        results = retriever.retrieve(question)

        out: list[dict] = []
        for node in results:
            score = float(node.score or 0.0)
            if score < self._similarity_cutoff:
                continue
            out.append({
                "text": node.get_text()[:500],
                "file_path": node.metadata.get("relative_path", "unknown"),
                "score": round(score, 4),
            })
        return out

    def _count_chunks(self) -> int:
        if self._index is not None:
            return len(self._index.docstore.docs)
        if self._has_persisted_index():
            try:
                docstore_path = os.path.join(self.persist_dir, "docstore.json")
                with open(docstore_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return len(data.get("docstore/data", {}))
            except OSError:
                return 0
        return 0

    def get_stats(self) -> dict:
        metadata = self._load_metadata()
        return {
            "total_chunks": self._count_chunks(),
            "indexed_files": len(metadata),
            "persist_dir": self.persist_dir,
            "project_dir": self.project_dir,
            "collection": self.collection_name,
            "chunk_size": self._chunk_size,
            "similarity_cutoff": self._similarity_cutoff,
        }

    def reset_index(self) -> None:
        import shutil
        if os.path.exists(self.persist_dir):
            shutil.rmtree(self.persist_dir)
        self._index = None
        log.info("[indexer] reset")
