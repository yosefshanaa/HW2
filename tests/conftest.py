from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pytest

from debate_simulator.agents import ConDebaterAgent, JudgeAgent, ProDebaterAgent


@dataclass
class MockLlm:
    """Deterministic LLM test double."""

    response: str = "Mock response"

    def complete(self, prompt: str) -> str:
        """Return a configured response for any prompt."""
        return self.response


@dataclass
class MockRag:
    """In-memory RAG test double."""

    documents: list[str]

    def add(self, document: str) -> None:
        """Store one document."""
        self.documents.append(document)

    def query(self, query: str) -> list[str]:
        """Return stored documents for any query."""
        return self.documents


@pytest.fixture
def mock_llm() -> MockLlm:
    """Provide a deterministic LLM test double."""
    return MockLlm()


@pytest.fixture
def mock_search() -> Callable[[str], list[dict[str, str]]]:
    """Provide a deterministic search test double."""
    return lambda query: [{"title": "Result", "url": "https://example.com", "body": query}]


@pytest.fixture
def mock_rag() -> MockRag:
    """Provide an in-memory RAG test double."""
    return MockRag(documents=[])


@pytest.fixture
def sample_topics() -> list[dict[str, Any]]:
    """Provide representative topic records."""
    return [
        {
            "id": 1,
            "category": "Science",
            "topic": "AI will replace most jobs by 2050",
            "pro_position": "For",
            "con_position": "Against",
        }
    ]


@pytest.fixture
def sample_agents(mock_llm: MockLlm):
    """Provide a judge and two debater agents for integration tests."""
    return {
        "judge": JudgeAgent(name="judge", llm_client=mock_llm),
        "pro": ProDebaterAgent(name="pro", llm_client=mock_llm),
        "con": ConDebaterAgent(name="con", llm_client=mock_llm),
    }
