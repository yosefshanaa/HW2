from debate_simulator.infrastructure.rag.chunker import DocumentChunker
from debate_simulator.infrastructure.rag.embedder import SentenceTransformerEmbedder
from debate_simulator.infrastructure.rag.vector_store import ChromaVectorStore


class FakeModel:
    """Embedding model test double."""

    def encode(self, texts: list[str]) -> list[list[float]]:
        """Return simple deterministic embeddings."""
        return [[float(len(text))] for text in texts]


class FakeCollection:
    """Chroma collection test double."""

    def __init__(self) -> None:
        """Create empty collection storage."""
        self.documents: list[str] = []
        self.embeddings: list[list[float]] = []

    def add(self, ids, documents, embeddings, metadatas):
        """Store documents and embeddings."""
        self.documents.extend(documents)
        self.embeddings.extend(embeddings)

    def query(self, query_embeddings, n_results: int):
        """Return stored documents."""
        return {"documents": [self.documents[:n_results]], "distances": [[0.0] * n_results]}

    def delete(self):
        """Reset stored documents."""
        self.documents.clear()
        self.embeddings.clear()


class FakeClient:
    """Chroma client test double."""

    def __init__(self) -> None:
        """Create one reusable collection."""
        self.collection = FakeCollection()

    def get_or_create_collection(self, name: str):
        """Return the fake collection."""
        return self.collection


def test_chunker_preserves_overlap_and_content() -> None:
    """Chunker splits words while preserving configured overlap."""
    chunks = DocumentChunker(chunk_size=4, chunk_overlap=2).chunk("one two three four five six")

    assert chunks == ["one two three four", "three four five six"]


def test_embedder_delegates_to_sentence_transformer_model() -> None:
    """Embedder returns model embeddings as plain float lists."""
    embedder = SentenceTransformerEmbedder(
        model_name="fake-model", model_factory=lambda name: FakeModel()
    )

    embeddings = embedder.embed(["abc", "de"])

    assert embeddings == [[3.0], [2.0]]


def test_vector_store_add_query_and_reset_round_trip(tmp_path) -> None:
    """Vector store wraps collection add, query, and reset operations."""
    client = FakeClient()
    store = ChromaVectorStore(
        persist_directory=tmp_path,
        collection_name="test",
        client_factory=lambda path: client,
    )

    store.add(["alpha", "beta"], [[1.0], [2.0]], [{"source": "a"}, {"source": "b"}])
    results = store.query([[1.0]], top_k=1)
    store.reset()

    assert results == ["alpha"] and client.collection.documents == []


def test_mocked_rag_round_trip(tmp_path) -> None:
    """Chunking, embedding, storing, and retrieval work together with mocks."""
    chunker = DocumentChunker(chunk_size=3, chunk_overlap=1)
    embedder = SentenceTransformerEmbedder(
        model_name="fake-model", model_factory=lambda name: FakeModel()
    )
    store = ChromaVectorStore(tmp_path, "roundtrip", client_factory=lambda path: FakeClient())
    chunks = chunker.chunk("alpha beta gamma delta")

    store.add(chunks, embedder.embed(chunks), [{"source": "test"} for _ in chunks])
    results = store.query(embedder.embed(["alpha"]), top_k=2)

    assert results == ["alpha beta gamma", "gamma delta"]
