from debate_simulator.agents.judge_agent import JudgeAgent
from debate_simulator.models.debate import RoundEvaluation, Score
from debate_simulator.shared.constants import AgentRole


class FakeLlm:
    """LLM test double."""

    def complete(self, prompt: str) -> str:
        """Return deterministic text."""
        return "judge text"


def test_judge_observes_without_replying_to_debaters() -> None:
    """Judge observation produces notes and no debater message."""
    judge = JudgeAgent(name="father", llm_client=FakeLlm())

    evaluation = judge.observe_round(round_number=1, pro_argument="pro", con_argument="con")

    assert isinstance(evaluation, RoundEvaluation) and evaluation.judge_message is None


def test_judge_declares_tie_for_equal_scores() -> None:
    """Judge winner declaration allows ties."""
    judge = JudgeAgent(name="father", llm_client=FakeLlm())
    score = Score(total=70.0, breakdown={}, penalties_applied=[])

    winner = judge.declare_winner({"pro": score, "con": score})

    assert winner == "tie" and judge.role == AgentRole.JUDGE
