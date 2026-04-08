"""
Code Indexer - Persistent RAG dla kodu źródłowego
==================================================
Indeksuje pliki z lokalnego katalogu z persystencją na dysku.
Przy kolejnym uruchomieniu ładuje istniejący indeks (bez re-indeksowania).
Obsługuje incremental update - indeksuje tylko zmienione pliki.

Używa LlamaIndex SimpleVectorStore z persist() / load_index_from_storage().
Alternatywnie mozna podpiac ChromaDB, FAISS, Qdrant jako vector store backend.
"""

import os
import hashlib
import json
import time
from typing import Optional

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    Settings,
    load_index_from_storage,
)
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

# Domyślne rozszerzenia plików do indeksowania
DEFAULT_EXTENSIONS = [
    ".py", ".java", ".ts", ".tsx", ".js", ".jsx",
    ".go", ".rs", ".kt", ".scala", ".rb",
    ".sql", ".yaml", ".yml", ".json", ".toml",
    ".md", ".txt", ".html", ".css",
]

# Katalogi pomijane przy indeksowaniu
DEFAULT_EXCLUDE_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "build", "dist", "target", ".idea", ".vscode",
    ".mypy_cache", ".pytest_cache", "egg-info",
}

# Plik metadata - przechowuje hashe plików do incremental indexing
METADATA_FILE = "_index_metadata.json"


class CodeIndexer:
    """Indeksuje kod źródłowy z persystencją na dysku (SimpleVectorStore)."""

    def __init__(
        self,
        project_dir: str,
        persist_dir: str = "./index_store",
        collection_name: str = "code_index",
        embedding_model: str = "gemini-embedding-2-preview",
    ):
        self.project_dir = os.path.abspath(project_dir)
        self.persist_dir = os.path.abspath(persist_dir)
        self.collection_name = collection_name
        self.metadata_path = os.path.join(self.persist_dir, METADATA_FILE)

        # Konfiguracja embeddingów
        self.embed_model = GoogleGenAIEmbedding(model=embedding_model)
        Settings.embed_model = self.embed_model

        self._index: Optional[VectorStoreIndex] = None

    def _has_persisted_index(self) -> bool:
        """Sprawdź czy istnieje zapisany indeks na dysku."""
        docstore_path = os.path.join(self.persist_dir, "docstore.json")
        return os.path.exists(docstore_path)

    @property
    def index(self) -> VectorStoreIndex:
        """Lazy-load indeksu - ładuje istniejący lub tworzy nowy."""
        if self._index is None:
            if self._has_persisted_index():
                storage_context = StorageContext.from_defaults(
                    persist_dir=self.persist_dir
                )
                self._index = load_index_from_storage(
                    storage_context,
                    embed_model=self.embed_model,
                )
                print(f"[CodeIndexer] Zaladowano istniejacy indeks z {self.persist_dir}")
            else:
                print("[CodeIndexer] Brak indeksu - uruchom index_project() aby zaindeksowac.")
        return self._index

    def _get_file_hash(self, filepath: str) -> str:
        """Oblicz hash MD5 dla pliku (do wykrywania zmian)."""
        hasher = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _load_metadata(self) -> dict:
        """Wczytaj metadane indeksu (hashe plików)."""
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_metadata(self, metadata: dict):
        """Zapisz metadane indeksu."""
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def _collect_files(
        self,
        extensions: list[str] | None = None,
        exclude_dirs: set[str] | None = None,
    ) -> list[str]:
        """Zbierz ścieżki plików do zaindeksowania."""
        exts = set(extensions or DEFAULT_EXTENSIONS)
        excludes = exclude_dirs or DEFAULT_EXCLUDE_DIRS
        files = []

        for root, dirs, filenames in os.walk(self.project_dir):
            # Filtruj katalogi in-place
            dirs[:] = [d for d in dirs if d not in excludes]

            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in exts:
                    files.append(os.path.join(root, filename))

        return sorted(files)

    def index_project(
        self,
        extensions: list[str] | None = None,
        exclude_dirs: set[str] | None = None,
        incremental: bool = True,
    ) -> dict:
        """
        Zaindeksuj projekt. W trybie incremental indeksuje tylko zmienione pliki.

        Returns:
            dict ze statystykami: indexed, skipped, removed, total_chunks, time_seconds
        """
        start_time = time.time()
        all_files = self._collect_files(extensions, exclude_dirs)
        old_metadata = self._load_metadata() if incremental else {}
        new_metadata = {}

        files_to_index = []
        skipped = 0

        for filepath in all_files:
            file_hash = self._get_file_hash(filepath)
            rel_path = os.path.relpath(filepath, self.project_dir)
            new_metadata[rel_path] = file_hash

            if incremental and old_metadata.get(rel_path) == file_hash:
                skipped += 1
            else:
                files_to_index.append(filepath)

        # Wykryj usunięte pliki
        removed_files = set(old_metadata.keys()) - set(new_metadata.keys())

        if not files_to_index and not removed_files:
            elapsed = time.time() - start_time
            print(f"[CodeIndexer] Indeks aktualny. Pominieto {skipped} plikow ({elapsed:.1f}s)")
            return {
                "indexed": 0,
                "skipped": skipped,
                "removed": 0,
                "total_chunks": self._count_chunks(),
                "time_seconds": elapsed,
            }

        print(f"[CodeIndexer] Do indeksowania: {len(files_to_index)} plikow, "
              f"pominieto: {skipped}, usunieto: {len(removed_files)}")

        # Wczytaj i zaindeksuj pliki
        if files_to_index:
            documents = SimpleDirectoryReader(
                input_files=files_to_index,
            ).load_data()

            # Dodaj metadata do dokumentów
            for doc in documents:
                rel = os.path.relpath(doc.metadata.get("file_path", ""), self.project_dir)
                doc.metadata["relative_path"] = rel
                doc.metadata["extension"] = os.path.splitext(rel)[1]

            # Parsuj dokumenty na nodes i oblicz embeddingi ręcznie
            # (workaround dla buga w LlamaIndex 0.14.x z GoogleGenAIEmbedding)
            from llama_index.core.node_parser import SentenceSplitter

            parser = SentenceSplitter(chunk_size=1024, chunk_overlap=100)
            nodes = parser.get_nodes_from_documents(documents)

            # Oblicz embeddingi node po node
            for node in nodes:
                node.embedding = self.embed_model.get_text_embedding(node.get_content())

            if self._index is None and not self._has_persisted_index():
                # Pierwszy raz - buduj indeks z gotowych nodes (embeddingi już obliczone)
                self._index = VectorStoreIndex(
                    nodes=nodes,
                    embed_model=self.embed_model,
                )
            else:
                # Doindeksuj nowe nodes
                if self._index is None:
                    storage_context = StorageContext.from_defaults(
                        persist_dir=self.persist_dir
                    )
                    self._index = load_index_from_storage(
                        storage_context,
                        embed_model=self.embed_model,
                    )
                for node in nodes:
                    self._index.insert_nodes([node])

            # Zapisz indeks na dysk (persystencja!)
            self._index.storage_context.persist(persist_dir=self.persist_dir)

        # Zapisz nowe metadane
        self._save_metadata(new_metadata)

        elapsed = time.time() - start_time
        stats = {
            "indexed": len(files_to_index),
            "skipped": skipped,
            "removed": len(removed_files),
            "total_chunks": self._count_chunks(),
            "time_seconds": round(elapsed, 1),
        }
        print(f"[CodeIndexer] Gotowe: {stats}")
        return stats

    def query(self, question: str, top_k: int = 5) -> list[dict]:
        """
        Semantyczne przeszukiwanie kodu.

        Returns:
            Lista dict z polami: text, file_path, score
        """
        if self.index is None:
            return [{"error": "Indeks nie istnieje. Uruchom index_project() najpierw."}]

        retriever = self.index.as_retriever(similarity_top_k=top_k)
        results = retriever.retrieve(question)

        return [
            {
                "text": node.get_text()[:500],  # Skróć do 500 znaków
                "file_path": node.metadata.get("relative_path", "unknown"),
                "score": round(node.score or 0.0, 4),
            }
            for node in results
        ]

    def _count_chunks(self) -> int:
        """Policz chunki w indeksie."""
        if self._index is not None:
            return len(self._index.docstore.docs)
        if self._has_persisted_index():
            try:
                docstore_path = os.path.join(self.persist_dir, "docstore.json")
                with open(docstore_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return len(data.get("docstore/data", {}))
            except Exception:
                return 0
        return 0

    def get_stats(self) -> dict:
        """Statystyki indeksu."""
        metadata = self._load_metadata()
        return {
            "total_chunks": self._count_chunks(),
            "indexed_files": len(metadata),
            "persist_dir": self.persist_dir,
            "project_dir": self.project_dir,
            "collection": self.collection_name,
        }

    def reset_index(self):
        """Wyczysc indeks i zacznij od nowa."""
        import shutil
        if os.path.exists(self.persist_dir):
            shutil.rmtree(self.persist_dir)
        self._index = None
        print("[CodeIndexer] Indeks wyczyszczony.")
