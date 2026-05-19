import re
from collections.abc import Callable
from html import unescape
from html.parser import HTMLParser
from typing import Any
from urllib.request import urlopen


class UrlFetcher:
    """URL text fetcher executed through the API gatekeeper."""

    def __init__(
        self, gatekeeper: Any, timeout_seconds: int, opener: Callable[..., Any] = urlopen
    ) -> None:
        """Create a fetcher with a timeout and opener."""
        self.gatekeeper = gatekeeper
        self.timeout_seconds = timeout_seconds
        self.opener = opener

    def fetch(self, url: str) -> str:
        """Fetch a URL and extract readable text."""
        return self.gatekeeper.execute("search", self._fetch, url)

    def _fetch(self, url: str) -> str:
        response = self.opener(url, timeout=self.timeout_seconds)
        try:
            raw = response.read()
        finally:
            close = getattr(response, "close", None)
            if close:
                close()
        parser = _TextExtractor()
        parser.feed(raw.decode(errors="ignore"))
        return _normalize_text(" ".join(parser.text_parts))


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text_parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.text_parts.append(unescape(data))


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


__all__ = ["UrlFetcher"]
