import os
from pathlib import Path

import pytest

from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import Penalty, RoundEvaluation
from debate_simulator.services.debate_engine import DebateEngine
from debate_simulator.services.scoring_service import ScoringService
from debate_simulator.shared.constants import PenaltyType
from debate_simulator.shared.process_manager import ProcessManager


class Debater:
    """Debater integration double."""

    def __init__(self, label: str) -> None:
        """Create a debater with a label."""
        self.label = label
        self.turns: list[str] = []

    def research(self, topic: str) -> None:
        """No-op research."""

    def run_turn(self, context: TurnContext) -> AgentResponse:
        """Return the label and record opponent input."""
        self.turns.append(context.opponent_last_argument)
        return AgentResponse.from_text(self.label, time_seconds=0.01)


class Judge:
    """Judge integration double that only observes."""

    def __init__(self) -> None:
        """Create observation records."""
        self.messages_to_sons: list[str] = []
        self.observed: list[tuple[str, str]] = []

    def observe_round(
        self, round_number: int, pro_argument: str, con_argument: str
    ) -> RoundEvaluation:
        """Observe without replying."""
        self.observed.append((con_argument, pro_argument))
        return RoundEvaluation(judge_message=None)

    def evaluate_debate(self, transcript):
        """Return tied scores."""
        return {}

    def declare_winner(self, scores):
        """Return tie."""
        return "tie"


def test_full_mocked_debate_exports_json(tmp_path: Path) -> None:
    """A mocked full debate completes and exports parseable JSON."""
    engine = DebateEngine(Debater("pro"), Debater("con"), Judge(), results_path=tmp_path)

    result = engine.start_debate("AI", {"pings": 2})

    assert len(result.rounds) == 2 and len(list(tmp_path.glob("*.json"))) == 1


def test_con_speaks_first_and_father_does_not_intervene(tmp_path: Path) -> None:
    """Con speaks first and judge never sends a debate message back."""
    judge = Judge()
    engine = DebateEngine(Debater("pro"), Debater("con"), judge, results_path=tmp_path)

    rounds = engine.run_debate_pings("AI", 1)

    assert judge.observed == [("con", "pro")] and rounds[0].judge_notes.judge_message is None


def test_penalty_and_tie_paths() -> None:
    """Penalties affect scores and equal totals produce a tie."""
    service = ScoringService({"compliance": 1.0})
    penalty = Penalty(type=PenaltyType.EXCEED_LINES, points=-5, reason="long", agent="pro")

    score = service.compute_score({"compliance": 90}, [penalty])

    assert score.total == 85 and service.determine_winner(85, 85) == "tie"


def test_timeout_records_penalty() -> None:
    """Process timeout returns an exceed-time penalty."""
    manager = ProcessManager(timeout_seconds=0.01, keepalive_interval_seconds=0.01)

    response = manager.run_with_timeout(_slow_response, "pro")

    assert response.penalties[0].type == PenaltyType.EXCEED_TIME


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY is not configured")
def test_real_api_e2e_placeholder() -> None:
    """Placeholder for real API E2E runs when a key is supplied."""
    assert os.getenv("OPENAI_API_KEY")


def _slow_response() -> AgentResponse:
    import time

    time.sleep(1)
    return AgentResponse.from_text("late", time_seconds=1)
