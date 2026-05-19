from collections.abc import Callable
from pathlib import Path
from typing import Any
from uuid import uuid4


class ChromaVectorStore:
    """ChromaDB vector-store wrapper for session-scoped RAG documents."""

    def __init__(
        self,
        persist_directory: str | Path,
        collection_name: str,
        client_factory: Callable[[Path], Any] | None = None,
    ) -> None:
        """Create a vector store collection."""
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.client_factory = client_factory or self._default_client_factory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.client = self.client_factory(self.persist_directory)
        self.collection = self.client.get_or_create_collection(collection_name)

    def add(
        self,
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, str]],
    ) -> None:
        """Add documents and embeddings to the vector store."""
        ids = [str(uuid4()) for _ in documents]
        self.collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)

    def query(self, query_embeddings: list[list[float]], top_k: int) -> list[str]:
        """Query the vector store and return matching documents."""
        result = self.collection.query(query_embeddings=query_embeddings, n_results=top_k)
        documents = result.get("documents", [[]])
        return [str(document) for document in documents[0]]

    def reset(self) -> None:
        """Clear the vector store collection."""
        delete = getattr(self.collection, "delete", None)
        if delete:
            delete()

    def _default_client_factory(self, path: Path) -> Any:
        import chromadb

        return chromadb.PersistentClient(path=str(path))


__all__ = ["ChromaVectorStore"]
