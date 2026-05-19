from pathlib import Path

from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import RoundEvaluation, Score
from debate_simulator.services.debate_engine import DebateEngine


class FakeDebater:
    """Debater test double."""

    def __init__(self, name: str) -> None:
        """Create a fake debater."""
        self.name = name
        self.calls: list[str] = []

    def research(self, topic: str):
        """Record research."""
        self.calls.append(f"research:{topic}")

    def run_turn(self, context: TurnContext) -> AgentResponse:
        """Return a deterministic argument."""
        self.calls.append(f"turn:{context.opponent_last_argument}")
        return AgentResponse.from_text(self.name, time_seconds=0.01)


class FakeJudge:
    """Judge test double."""

    def __init__(self) -> None:
        """Create fake judge records."""
        self.observed: list[tuple[str, str]] = []

    def observe_round(self, round_number: int, pro_argument: str, con_argument: str) -> RoundEvaluation:
        """Record arguments without replying."""
        self.observed.append((con_argument, pro_argument))
        return RoundEvaluation(pro_notes="pro", con_notes="con", judge_message=None)

    def evaluate_debate(self, transcript):
        """Return tied scores."""
        score = Score(total=50, breakdown={}, penalties_applied=[])
        return {"pro": score, "con": score}

    def declare_winner(self, scores):
        """Return tie."""
        return "tie"


def test_debate_engine_runs_con_then_pro_then_judge(tmp_path: Path) -> None:
    """Debate pings follow Con to Pro to Judge observation order."""
    con = FakeDebater("con")
    pro = FakeDebater("pro")
    judge = FakeJudge()
    engine = DebateEngine(pro_agent=pro, con_agent=con, judge_agent=judge, results_path=tmp_path)

    rounds = engine.run_debate_pings(topic="AI", pings=1)

    assert rounds[0].con_argument == "con" and judge.observed == [("con", "pro")]


def test_debate_engine_exports_result_json(tmp_path: Path) -> None:
    """Engine start_debate exports a JSON result file."""
    engine = DebateEngine(
        pro_agent=FakeDebater("pro"),
        con_agent=FakeDebater("con"),
        judge_agent=FakeJudge(),
        results_path=tmp_path,
    )

    result = engine.start_debate("AI", config={"pings": 1})

    assert result.winner == "tie" and len(list(tmp_path.glob("*.json"))) == 1
