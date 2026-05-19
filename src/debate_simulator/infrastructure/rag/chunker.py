class DocumentChunker:
    """Word-based document chunker with configurable overlap."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        """Create a chunker with chunk size and overlap measured in words."""
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> list[str]:
        """Split text into overlapping word chunks."""
        words = text.split()
        if not words:
            return []
        chunks: list[str] = []
        start = 0
        step = self.chunk_size - self.chunk_overlap
        while start < len(words):
            chunk_words = words[start : start + self.chunk_size]
            chunks.append(" ".join(chunk_words))
            if start + self.chunk_size >= len(words):
                break
            start += step
        return chunks


__all__ = ["DocumentChunker"]
