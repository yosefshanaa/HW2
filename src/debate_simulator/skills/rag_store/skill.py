from typing import Any

from debate_simulator.infrastructure.rag.chunker import DocumentChunker
from debate_simulator.skills.base_skill import BaseSkill, SkillResult


class RagStoreSkill(BaseSkill):
    """Skill that chunks, embeds, and stores documents in RAG."""

    name = "rag_store"
    description = "Store research documents in the local vector store."

    def __init__(self, store: Any, embedder: Any, chunk_size: int, chunk_overlap: int) -> None:
        """Create a RAG storage skill."""
        self.store = store
        self.embedder = embedder
        self.chunker = DocumentChunker(chunk_size, chunk_overlap)

    def execute(self, payload: dict[str, Any]) -> SkillResult:
        """Store the provided text in chunked form."""
        text = str(payload.get("text", ""))
        source = str(payload.get("source", ""))
        chunks = self.chunker.chunk(text)
        if chunks:
            metadatas = [{"source": source} for _ in chunks]
            self.store.add(chunks, self.embedder.embed(chunks), metadatas)
        return SkillResult.ok({"stored": len(chunks)})


__all__ = ["RagStoreSkill"]
