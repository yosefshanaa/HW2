from io import BytesIO

from debate_simulator.infrastructure.search.fetcher import UrlFetcher
from debate_simulator.infrastructure.search.searcher import DuckDuckGoSearcher, SearchResult


class FakeGatekeeper:
    """Gatekeeper test double that executes calls immediately."""

    def __init__(self) -> None:
        """Create an empty call log."""
        self.services: list[str] = []

    def execute(self, service: str, api_call, *args, **kwargs):
        """Record the service and execute the wrapped call."""
        self.services.append(service)
        return api_call(*args, **kwargs)


class FakeDuckDuckGo:
    """DuckDuckGo client test double."""

    def text(self, query: str, max_results: int):
        """Return one deterministic search result."""
        return [{"title": query, "href": "https://example.com", "body": "summary"}][:max_results]


def test_searcher_returns_structured_results_through_gatekeeper() -> None:
    """Searcher converts DDG dictionaries into SearchResult records."""
    gatekeeper = FakeGatekeeper()
    searcher = DuckDuckGoSearcher(
        gatekeeper=gatekeeper,
        max_results=1,
        ddgs_factory=lambda: FakeDuckDuckGo(),
    )

    results = searcher.search("debate rubric")

    assert results == [
        SearchResult(title="debate rubric", url="https://example.com", snippet="summary")
    ]


def test_fetcher_extracts_clean_text_through_gatekeeper() -> None:
    """Fetcher strips HTML markup and normalizes whitespace."""
    gatekeeper = FakeGatekeeper()
    html = b"<html><body><h1>Title</h1><script>x()</script><p>Hello&nbsp;world</p></body></html>"

    def opener(url: str, timeout: int):
        return BytesIO(html)

    fetcher = UrlFetcher(gatekeeper=gatekeeper, timeout_seconds=5, opener=opener)

    text = fetcher.fetch("https://example.com")

    assert text == "Title Hello world"
