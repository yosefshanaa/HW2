from debate_simulator.models.debate import Penalty
from debate_simulator.services.scoring_service import ScoringService
from debate_simulator.shared.constants import PenaltyType


def test_scoring_service_applies_weights_and_penalties() -> None:
    """Weighted scores subtract penalties from the final total."""
    service = ScoringService(
        weights={
            "argument_strength": 0.5,
            "compliance": 0.5,
        }
    )
    penalty = Penalty(type=PenaltyType.EXCEED_LINES, points=-5, reason="long", agent="pro")

    score = service.compute_score({"argument_strength": 80, "compliance": 100}, [penalty])

    assert score.total == 85.0


def test_scoring_service_detects_tie() -> None:
    """Winner determination supports ties."""
    service = ScoringService(weights={})

    winner = service.determine_winner(pro_total=70, con_total=70)

    assert winner == "tie"
