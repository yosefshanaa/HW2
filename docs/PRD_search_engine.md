# PRD Search Engine

## Purpose
Provide internet research through DuckDuckGo without requiring an additional API key.

## Requirements
- All search execution goes through `ApiGatekeeper` under the `search` service.
- Results are normalized to title, URL, and snippet fields.
- Search failures degrade gracefully through skills so agents may continue with available knowledge.
- Result count is configured by `config/setup.json`.

## Interface
- `DuckDuckGoSearcher.search(query: str) -> list[SearchResult]`
- `UrlFetcher.fetch(url: str) -> str`

## Acceptance
- Mocked search returns structured results.
- Fetching extracts readable text and strips scripts/styles.
- Gatekeeper records the `search` service for search and fetch operations.
