# PRD RAG System

## Purpose
Store session research locally and retrieve relevant context for debaters.

## Requirements
- Documents are chunked with configurable size and overlap.
- Embeddings use sentence-transformers.
- Vector storage uses ChromaDB with a session-scoped persist directory.
- Retrieval failures degrade gracefully through skills.

## Interface
- `DocumentChunker.chunk(text: str) -> list[str]`
- `SentenceTransformerEmbedder.embed(texts: list[str]) -> list[list[float]]`
- `ChromaVectorStore.add(...)`, `query(...)`, `reset()`

## Acceptance
- Unit tests verify overlap, embedding delegation, add/query/reset, and mocked round trip.
