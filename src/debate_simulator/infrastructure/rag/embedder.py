from collections.abc import Callable
from typing import Any


class SentenceTransformerEmbedder:
    """Sentence-transformers embedding wrapper."""

    def __init__(self, model_name: str, model_factory: Callable[[str], Any] | None = None) -> None:
        """Create an embedder for a sentence-transformers model."""
        self.model_name = model_name
        self.model_factory = model_factory or self._default_factory
        self._model: Any | None = None

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts as plain Python float lists."""
        vectors = self._load_model().encode(texts)
        return [[float(value) for value in vector] for vector in vectors]

    def _load_model(self) -> Any:
        if self._model is None:
            self._model = self.model_factory(self.model_name)
        return self._model

    def _default_factory(self, model_name: str) -> Any:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(model_name)


__all__ = ["SentenceTransformerEmbedder"]
