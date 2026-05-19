from debate_simulator.infrastructure.search.fetcher import UrlFetcher
from debate_simulator.infrastructure.search.searcher import DuckDuckGoSearcher, SearchResult
from debate_simulator.shared.version import VERSION

__version__ = VERSION
__all__ = ["DuckDuckGoSearcher", "SearchResult", "UrlFetcher", "__version__"]
