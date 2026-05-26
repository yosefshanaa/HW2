from pathlib import Path

from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import RoundEvaluation
from debate_simulator.sdk import DebateSimulatorSDK
from debate_simulator.services.debate_engine import DebateEngine


class Agent:
    """Agent double for SDK integration."""

    def __init__(self, text: str) -> None:
        """Create an agent with fixed text."""
        self.text = text

    def research(self, topic: str) -> None:
        """No-op research."""

    def run_turn(self, context: TurnContext) -> AgentResponse:
        """Return fixed text."""
        return AgentResponse.from_text(self.text, time_seconds=0.01)


class Judge:
    """Judge double for SDK integration."""

    def observe_round(
        self, round_number: int, pro_argument: str, con_argument: str, debate_history=None,
    ) -> RoundEvaluation:
        """Return empty notes."""
        return RoundEvaluation()

    def evaluate_debate(self, transcript):
        """Return empty scores."""
        return {}

    def declare_winner(self, scores):
        """Return a decisive winner."""
        return "pro"


def test_sdk_to_engine_chain(tmp_path: Path) -> None:
    """SDK start_debate delegates to the debate engine."""
    engine = DebateEngine(Agent("pro"), Agent("con"), Judge(), results_path=tmp_path)
    sdk = DebateSimulatorSDK(engine=engine, topics_path=Path("data/topics.json"))

    result = sdk.start_debate("AI", {"pings": 1})

    assert result.winner == "pro"
