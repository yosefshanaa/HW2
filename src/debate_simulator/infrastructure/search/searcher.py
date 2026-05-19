from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SearchResult:
    """Structured search result returned by the search abstraction."""

    title: str
    url: str
    snippet: str


class DuckDuckGoSearcher:
    """DuckDuckGo search wrapper executed through the API gatekeeper."""

    def __init__(self, gatekeeper: Any, max_results: int, ddgs_factory: Callable[[], Any] | None = None) -> None:
        """Create a DuckDuckGo searcher."""
        self.gatekeeper = gatekeeper
        self.max_results = max_results
        self.ddgs_factory = ddgs_factory or self._default_factory

    def search(self, query: str) -> list[SearchResult]:
        """Search DuckDuckGo and return normalized result records."""
        return self.gatekeeper.execute("search", self._search, query)

    def _search(self, query: str) -> list[SearchResult]:
        client = self.ddgs_factory()
        rows = client.text(query, max_results=self.max_results)
        return [
            SearchResult(
                title=str(row.get("title", "")),
                url=str(row.get("href") or row.get("url", "")),
                snippet=str(row.get("body") or row.get("snippet", "")),
            )
            for row in rows
        ]

    def _default_factory(self) -> Any:
        from duckduckgo_search import DDGS

        return DDGS()


__all__ = ["DuckDuckGoSearcher", "SearchResult"]
