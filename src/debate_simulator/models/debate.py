from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field

from debate_simulator.shared.constants import PenaltyType
from debate_simulator.shared.version import VERSION


class Penalty(BaseModel):
    """Penalty applied to a debater."""

    type: PenaltyType
    points: int
    reason: str
    agent: str


class Score(BaseModel):
    """Final score with dimension breakdown and penalties."""

    total: float
    breakdown: dict[str, float]
    penalties_applied: list[Penalty] = Field(default_factory=list)


class RoundEvaluation(BaseModel):
    """Judge notes and penalties for a debate round."""

    pro_notes: str = ""
    con_notes: str = ""
    pro_penalties: list[Penalty] = Field(default_factory=list)
    con_penalties: list[Penalty] = Field(default_factory=list)
    judge_message: str | None = None


class Round(BaseModel):
    """One debate ping containing con, pro, and judge data."""

    round_number: int
    con_argument: str
    pro_argument: str
    judge_notes: RoundEvaluation
    penalties: list[Penalty] = Field(default_factory=list)


class DebateResult(BaseModel):
    """Full debate result exported as JSON."""

    debate_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    topic: str
    version: str = VERSION
    rounds: list[Round] = Field(default_factory=list)
    final_scores: dict[str, Score]
    winner: str
    token_usage: dict[str, float] = Field(default_factory=dict)


__all__ = ["DebateResult", "Penalty", "Round", "RoundEvaluation", "Score"]
