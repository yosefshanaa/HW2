import pytest

from debate_simulator.models.agent import AgentResponse, Message, TurnContext
from debate_simulator.models.config_models import validate_config
from debate_simulator.models.debate import DebateResult, Penalty, Round, RoundEvaluation, Score
from debate_simulator.shared.config import Settings
from debate_simulator.shared.constants import AgentRole, PenaltyType, Stance


def test_agent_models_validate_core_fields() -> None:
    """Agent models compute line counts and preserve typed roles."""
    message = Message(role=AgentRole.PRO, content="hello")
    context = TurnContext(topic="AI", stance=Stance.PRO, round_number=1, memory=[message])
    response = AgentResponse.from_text("one\ntwo", time_seconds=1.5)

    assert context.memory[0].role == AgentRole.PRO and response.lines == 2


def test_debate_result_rejects_tie_winner() -> None:
    """DebateResult requires a decisive Father verdict."""
    penalty = Penalty(type=PenaltyType.EXCEED_LINES, points=-5, reason="too long", agent="pro")
    score = Score(total=80.0, breakdown={"compliance": 85.0}, penalties_applied=[penalty])

    with pytest.raises(ValueError):
        DebateResult(topic="AI", final_scores={"pro": score, "con": score}, winner="tie")


def test_round_and_round_evaluation_models() -> None:
    """Round and RoundEvaluation models hold per-round debate data."""
    evaluation = RoundEvaluation(
        pro_notes="Strong opening", con_notes="Weak rebuttal", judge_message=None,
    )
    round_model = Round(
        round_number=1,
        con_argument="Con says no",
        pro_argument="Pro says yes",
        judge_notes=evaluation,
        penalties=[],
    )

    assert round_model.round_number == 1 and round_model.judge_notes.judge_message is None


def test_penalty_model_fields() -> None:
    """Penalty model stores type, points, reason, and agent."""
    penalty = Penalty(type=PenaltyType.DISRESPECT, points=-5, reason="rude", agent="con")

    assert penalty.points == -5 and penalty.agent == "con"


def test_validate_config_returns_warnings_for_bad_settings() -> None:
    """validate_config detects temperature out of range and overlap >= chunk_size."""
    settings = Settings.model_construct(
        setup=type("S", (), {
            "version": "0.50",
            "llm": type("L", (), {"temperature": 3.0})(),
            "debate": type("D", (), {"max_pings": 0})(),
            "rag": type("R", (), {"chunk_size": 100, "chunk_overlap": 100})(),
        })(),
        rate_limits=type("R", (), {})(),
        openai_api_key=None,
    )
    warnings = validate_config(settings)

    assert len(warnings) >= 3
