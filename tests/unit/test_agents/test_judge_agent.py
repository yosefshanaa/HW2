from debate_simulator.agents.debater_agent import ProDebaterAgent
from debate_simulator.agents.judge_agent import JudgeAgent
from debate_simulator.models.agent import TurnContext
from debate_simulator.models.debate import RoundEvaluation, Score
from debate_simulator.services.debater_service import DebaterService
from debate_simulator.services.judge_service import JudgeService
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

    assert winner == "tie"


def test_judge_service_delegates_observe_and_score() -> None:
    """JudgeService passes through to the underlying judge agent."""
    judge = JudgeAgent(name="father", llm_client=FakeLlm())
    service = JudgeService(judge_agent=judge)

    evaluation = service.observe_round(1, "pro arg", "con arg")
    scores = service.score([])

    assert isinstance(evaluation, RoundEvaluation) and "pro" in scores


def test_debater_service_delegates_research_and_turn() -> None:
    """DebaterService passes through to the underlying debater agent."""
    agent = ProDebaterAgent(name="son1", llm_client=FakeLlm())
    service = DebaterService(debater_agent=agent)

    notes = service.research("AI ethics")
    response = service.run_turn(TurnContext(topic="AI", stance=AgentRole.PRO, round_number=1))

    assert notes == ["AI ethics"] and response.text == "judge text"
