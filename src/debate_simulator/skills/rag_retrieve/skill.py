from typing import Any

from debate_simulator.skills.base_skill import BaseSkill, SkillResult


class RagRetrieveSkill(BaseSkill):
    """Skill that retrieves relevant documents from the vector store."""

    name = "rag_retrieve"
    description = "Retrieve relevant context from the local vector store."

    def __init__(self, store: Any, embedder: Any) -> None:
        """Create a RAG retrieval skill."""
        self.store = store
        self.embedder = embedder

    def execute(self, payload: dict[str, Any]) -> SkillResult:
        """Retrieve documents for the provided query."""
        query = str(payload.get("query", ""))
        top_k = int(payload.get("top_k", 1))
        try:
            documents = self.store.query(self.embedder.embed([query]), top_k)
        except Exception as error:
            return SkillResult.fail(str(error))
        return SkillResult.ok({"documents": documents})


__all__ = ["RagRetrieveSkill"]
