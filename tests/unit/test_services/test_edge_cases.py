import pytest

from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import RoundEvaluation, Score
from debate_simulator.services.debate_engine import DebateEngine
from debate_simulator.shared.llm_client import LlmClient
from debate_simulator.skills.rag_retrieve.skill import RagRetrieveSkill
from debate_simulator.skills.web_search.skill import WebSearchSkill


class BrokenSearch:
    """Search dependency that fails."""

    def search(self, query: str):
        """Raise a search failure."""
        raise RuntimeError("search down")


class BrokenStore:
    """RAG store dependency that fails."""

    def query(self, embeddings, top_k: int):
        """Raise a RAG failure."""
        raise RuntimeError("rag down")


class FakeEmbedder:
    """Embedder test double."""

    def embed(self, texts: list[str]):
        """Return deterministic embeddings."""
        return [[1.0] for _ in texts]


class CrashingDebater:
    """Debater that crashes during its turn."""

    def research(self, topic: str) -> None:
        """No-op research."""

    def run_turn(self, context: TurnContext) -> AgentResponse:
        """Crash during turn."""
        raise RuntimeError("agent crashed")


class StableDebater:
    """Debater that returns a stable response."""

    def research(self, topic: str) -> None:
        """No-op research."""

    def run_turn(self, context: TurnContext) -> AgentResponse:
        """Return a response."""
        return AgentResponse.from_text("stable", time_seconds=0.01)


class Judge:
    """Judge test double."""

    def observe_round(self, round_number: int, pro_argument: str, con_argument: str) -> RoundEvaluation:
        """Return empty notes."""
        return RoundEvaluation()

    def evaluate_debate(self, transcript):
        """Return tied scores."""
        score = Score(total=1, breakdown={}, penalties_applied=[])
        return {"pro": score, "con": score}

    def declare_winner(self, scores):
        """Return a tie."""
        return "tie"


def test_search_skill_gracefully_degrades_on_failure() -> None:
    """Search failure returns a failed SkillResult rather than raising."""
    result = WebSearchSkill(searcher=BrokenSearch()).execute({"query": "AI"})

    assert result.success is False


def test_rag_retrieve_gracefully_degrades_on_failure() -> None:
    """RAG retrieval failure returns a failed SkillResult rather than raising."""
    result = RagRetrieveSkill(store=BrokenStore(), embedder=FakeEmbedder()).execute({"query": "AI"})

    assert result.success is False


def test_llm_client_rejects_empty_response() -> None:
    """Null or empty LLM responses raise a clear error."""
    client = LlmClient(openai_client=type("Client", (), {"responses": type("R", (), {"create": lambda self, **kw: object()})()})(), gatekeeper=type("G", (), {"execute": lambda self, service, call, *args: call(*args)})(), model="m", temperature=0.7)

    with pytest.raises(ValueError):
        client.complete("prompt")


def test_debate_engine_continues_after_agent_crash(tmp_path) -> None:
    """Agent crash produces a fallback response and debate continues."""
    engine = DebateEngine(
        pro_agent=StableDebater(),
        con_agent=CrashingDebater(),
        judge_agent=Judge(),
        results_path=tmp_path,
    )

    rounds = engine.run_debate_pings("AI", pings=1)

    assert rounds[0].con_argument == "Agent crashed" and rounds[0].penalties
