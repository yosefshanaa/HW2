from debate_simulator.models.agent import AgentResponse, Message, TurnContext
from debate_simulator.models.debate import DebateResult, Penalty, Score
from debate_simulator.shared.constants import AgentRole, PenaltyType, Stance


def test_agent_models_validate_core_fields() -> None:
    """Agent models compute line counts and preserve typed roles."""
    message = Message(role=AgentRole.PRO, content="hello")
    context = TurnContext(topic="AI", stance=Stance.PRO, round_number=1, memory=[message])
    response = AgentResponse.from_text("one\ntwo", time_seconds=1.5)

    assert context.memory[0].role == AgentRole.PRO and response.lines == 2


def test_debate_result_accepts_tie_winner() -> None:
    """DebateResult supports tie outcomes."""
    penalty = Penalty(type=PenaltyType.EXCEED_LINES, points=-5, reason="too long", agent="pro")
    score = Score(total=80.0, breakdown={"compliance": 85.0}, penalties_applied=[penalty])
    result = DebateResult(topic="AI", final_scores={"pro": score, "con": score}, winner="tie")

    assert result.winner == "tie"
