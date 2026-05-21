"""Helper utilities for judge repetition detection, penalty mapping, and fallback scoring."""

from __future__ import annotations

import json
from typing import Any

from debate_simulator.models.debate import Penalty, Score
from debate_simulator.shared.constants import PenaltyType

_DIMENSIONS = ["content", "style", "strategy"]
_JUDGE_REPETITION_THRESHOLD = 0.55


def detect_repetition(
    pro_arg: str, con_arg: str, pro_hist: list[str], con_hist: list[str]
) -> list[str]:
    """Auto-detect repetition when the LLM judge misses it."""
    flagged: list[str] = []
    if _is_repetitive(pro_arg, pro_hist[:-1]):
        flagged.append("repetition")
    if _is_repetitive(con_arg, con_hist[:-1]):
        flagged.append("repetition")
    return flagged


def _is_repetitive(text: str, history: list[str]) -> bool:
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
        if union and len(current_bigrams & prev_bigrams) / union > _JUDGE_REPETITION_THRESHOLD:
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
    return {
        "pro_notes": analytical_note("Pro", pro_argument, con_argument),
        "con_notes": analytical_note("Con", con_argument, pro_argument),
        "pro_speaker_score": 65,
        "con_speaker_score": 65,
        "pro_penalties": [],
        "con_penalties": [],
    }


def average_round_scores(
    pro_round_scores: list[float], con_round_scores: list[float]
) -> dict[str, Score]:
    """Average per-round speaker scores into final quality scores."""
    pro_total = sum(pro_round_scores) / len(pro_round_scores) if pro_round_scores else 60.0
    con_total = sum(con_round_scores) / len(con_round_scores) if con_round_scores else 60.0
    return {
        "pro": Score(total=pro_total, breakdown=dict.fromkeys(_DIMENSIONS, pro_total)),
        "con": Score(total=con_total, breakdown=dict.fromkeys(_DIMENSIONS, con_total)),
    }


def score_from_data(data: Any) -> Score:
    """Parse a score dict from LLM JSON output, clamping to 0-100."""
    if not isinstance(data, dict):
        data = {}
    breakdown = data.get("breakdown", {})
    if not isinstance(breakdown, dict):
        breakdown = {}
    fallback_total = sum(float(breakdown.get(key, 0.0)) for key in _DIMENSIONS) / len(_DIMENSIONS)
    total = float(data.get("total", fallback_total))
    return Score(total=max(min(total, 100.0), 0.0), breakdown=breakdown)


def map_penalties(agent: str, names: list[Any]) -> list[Penalty]:
    """Convert string penalty names from the LLM into typed Penalty objects."""
    _heavy = {PenaltyType.IGNORE_REBUTTAL, PenaltyType.EXCEED_TIME, PenaltyType.REPETITION}
    penalties = []
    for name in names:
        try:
            pt = PenaltyType(str(name))
        except ValueError:
            continue
        points = -15 if pt == PenaltyType.STANCE_CONTRADICTION else (-10 if pt in _heavy else -5)
        penalties.append(Penalty(type=pt, points=points, reason=str(name), agent=agent))
    return penalties


def build_round_prompt(
    template: str, round_number: int, pro_arg: str, con_arg: str, history: list[str] | None = None
) -> str:
    """Render the judge round-evaluation prompt."""
    h = "\nDebate history (prior rounds):\n" + "\n".join(history[-4:]) + "\n" if history else ""
    return (
        f"{template}\n\n{h}Evaluate round {round_number}.\n"
        f"Con speech:\n{con_arg}\n\nPro speech:\n{pro_arg}\n\n"
        'Return JSON only: {"con_notes":"...","pro_notes":"...",'
        '"pro_speaker_score":75,"con_speaker_score":70,'
        '"con_penalties":[],"pro_penalties":[]}.'
    )


def build_final_prompt(template: str, transcript: list[str]) -> str:
    """Render the judge final-scoring prompt."""
    schema = {s: {"breakdown": dict.fromkeys(_DIMENSIONS, 0), "total": 0} for s in ("pro", "con")}
    return (
        f"{template}\n\nFinal transcript JSON lines:\n"
        + "\n".join(transcript)
        + f"\nReturn JSON only using this schema: {json.dumps(schema)}"
    )


def parse_json_response(raw_response: str) -> dict[str, Any]:
    """Extract and parse a JSON object from a raw LLM response string."""
    raw = raw_response.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()
    start, end = raw.find("{"), raw.rfind("}") + 1
    if start >= 0 and end > start:
        raw = raw[start:end]
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("judge response is not a JSON object")
    return data


__all__ = [
    "analytical_note",
    "average_round_scores",
    "build_final_prompt",
    "build_round_prompt",
    "detect_repetition",
    "fallback_round_data",
    "map_penalties",
    "parse_json_response",
    "score_from_data",
]
