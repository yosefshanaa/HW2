"""Helper utilities for judge repetition detection, penalty mapping, and fallback scoring."""

from __future__ import annotations

from typing import Any

from debate_simulator.models.debate import Penalty, Score
from debate_simulator.shared.constants import (
    PenaltyPoints,
    PenaltyType,
    RepetitionThreshold,
    ScoreDefault,
)

_DIMENSIONS = ["content", "style", "strategy"]


def detect_repetition(
    pro_arg: str, con_arg: str, pro_hist: list[str], con_hist: list[str]
) -> tuple[list[str], list[str]]:
    """Auto-detect repetition when the LLM judge misses it. Returns (pro_flags, con_flags)."""
    threshold = RepetitionThreshold.JUDGE_BIGRAM_OVERLAP.value
    pro_flagged = ["repetition"] if _is_repetitive(pro_arg, pro_hist[:-1], threshold) else []
    con_flagged = ["repetition"] if _is_repetitive(con_arg, con_hist[:-1], threshold) else []
    return pro_flagged, con_flagged


def _is_repetitive(text: str, history: list[str], threshold: float) -> bool:
    """Check if *text* reuses phrases from prior arguments via bigram overlap."""
    if not history:
        return False
    words = text.lower().split()
    if len(words) < 5:
        return False
    current_bigrams = set(zip(words, words[1:], strict=False))
    for prev in history:
        prev_words = prev.lower().split()
        if len(prev_words) < 5:
            continue
        prev_bigrams = set(zip(prev_words, prev_words[1:], strict=False))
        union = len(current_bigrams | prev_bigrams)
        if union and len(current_bigrams & prev_bigrams) / union > threshold:
            return True
    return False


def analytical_note(agent: str, argument: str, opponent: str) -> str:
    """Generate a brief analytical note when the LLM judge fails."""
    addressed = bool(set(argument.lower().split()) & set(opponent.lower().split()))
    has_evidence = any(
        t in argument.lower() for t in ("because", "evidence", "source", "data", "according")
    )
    wc = len(argument.split())
    parts = [
        f"{agent} {'addressed the opponent' if addressed else 'needs a more direct rebuttal'}."
    ]
    parts.append(f"Uses {'some' if has_evidence else 'no'} supporting evidence.")
    parts.append(f"Argument length: {wc} words.")
    return " ".join(parts)


def fallback_round_data(pro_argument: str, con_argument: str) -> dict[str, Any]:
    """Return fallback round data when the LLM judge response cannot be parsed."""
    fallback = ScoreDefault.FALLBACK_ROUND_SCORE.value
    return {
        "pro_notes": analytical_note("Pro", pro_argument, con_argument),
        "con_notes": analytical_note("Con", con_argument, pro_argument),
        "pro_speaker_score": fallback,
        "con_speaker_score": fallback,
        "pro_penalties": [],
        "con_penalties": [],
    }


def average_round_scores(
    pro_round_scores: list[float], con_round_scores: list[float]
) -> dict[str, Score]:
    """Average per-round speaker scores into final quality scores."""
    default = ScoreDefault.DEFAULT_TOTAL.value
    pro_total = sum(pro_round_scores) / len(pro_round_scores) if pro_round_scores else default
    con_total = sum(con_round_scores) / len(con_round_scores) if con_round_scores else default
    return {
        "pro": Score(total=pro_total, breakdown=dict.fromkeys(_DIMENSIONS, pro_total)),
        "con": Score(total=con_total, breakdown=dict.fromkeys(_DIMENSIONS, con_total)),
    }


def map_penalties(agent: str, names: list[Any]) -> list[Penalty]:
    """Convert string penalty names from the LLM into typed Penalty objects."""
    _heavy = {PenaltyType.IGNORE_REBUTTAL, PenaltyType.EXCEED_TIME, PenaltyType.REPETITION}
    penalties = []
    for name in names:
        try:
            pt = PenaltyType(str(name))
        except ValueError:
            continue
        if pt == PenaltyType.STANCE_CONTRADICTION:
            points = PenaltyPoints.STANCE_CONTRADICTION.value
        elif pt in _heavy:
            points = PenaltyPoints[pt.name].value if pt.name in PenaltyPoints.__members__ else PenaltyPoints.DEFAULT.value
        else:
            points = PenaltyPoints.DEFAULT.value
        penalties.append(Penalty(type=pt, points=points, reason=str(name), agent=agent))
    return penalties


__all__ = [
    "analytical_note",
    "average_round_scores",
    "detect_repetition",
    "fallback_round_data",
    "map_penalties",
]
