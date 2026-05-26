import random

from debate_simulator.models.debate import Penalty, Score


class ScoringService:
    """Compute weighted scores, apply penalties, and determine winners."""

    def __init__(self, weights: dict[str, float]) -> None:
        """Create a scoring service with dimension weights."""
        self.weights = weights

    def compute_score(self, breakdown: dict[str, float], penalties: list[Penalty]) -> Score:
        """Compute a final score from weighted dimensions and penalties."""
        weighted_total = sum(
            breakdown.get(dimension, 0.0) * weight for dimension, weight in self.weights.items()
        )
        penalty_total = sum(penalty.points for penalty in penalties)
        return Score(
            total=max(weighted_total + penalty_total, 0.0),
            breakdown=breakdown,
            penalties_applied=penalties,
        )

    def determine_winner(self, pro_total: float, con_total: float) -> str:
        """Return a decisive winner from score totals."""
        if pro_total == con_total:
            return random.choice(["pro", "con"])
        return "pro" if pro_total > con_total else "con"


__all__ = ["ScoringService"]
