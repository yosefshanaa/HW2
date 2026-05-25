"""Judge prompt construction and JSON response parsing."""

from __future__ import annotations

import json
from typing import Any

from debate_simulator.shared.constants import ContextWindow, ScoreDefault

_DIMENSIONS = ["content", "style", "strategy"]


def score_from_data(data: Any) -> Any:
    """Parse a score dict from LLM JSON output, clamping to 0-100."""
    from debate_simulator.models.debate import Score

    if not isinstance(data, dict):
        data = {}
    breakdown = data.get("breakdown", {})
    if not isinstance(breakdown, dict):
        breakdown = {}
    fallback_total = sum(float(breakdown.get(key, 0.0)) for key in _DIMENSIONS) / len(_DIMENSIONS)
    total = float(data.get("total", fallback_total))
    return Score(total=max(min(total, 100.0), 0.0), breakdown=breakdown)


def build_round_prompt(
    template: str, round_number: int, pro_arg: str, con_arg: str, history: list[str] | None = None
) -> str:
    """Render the judge round-evaluation prompt, alternating speaker order by round."""
    window = ContextWindow.JUDGE_HISTORY_ROUNDS.value
    h = "\nDebate history (prior rounds):\n" + "\n".join(history[-window:]) + "\n" if history else ""
    if round_number % 2 == 0:
        first_name, first_arg, second_name, second_arg = "Con", con_arg, "Pro", pro_arg
    else:
        first_name, first_arg, second_name, second_arg = "Pro", pro_arg, "Con", con_arg
    # Neutral, EQUAL example scores: the example must carry no signal about which
    # side should score higher. Asymmetric example values anchor the LLM toward
    # one side every round and systematically bias the verdict.
    neutral = int(ScoreDefault.DEFAULT_SPEAKER_SCORE.value)
    first_lo, second_lo = first_name.lower(), second_name.lower()
    json_example = (
        f'{{"{first_lo}_notes":"...","{second_lo}_notes":"...",'
        f'"{first_lo}_speaker_score":{neutral},"{second_lo}_speaker_score":{neutral},'
        f'"{first_lo}_penalties":[],"{second_lo}_penalties":[]}}'
    )
    return (
        f"{template}\n\n{h}Evaluate round {round_number}.\n"
        f"{first_name} speech:\n{first_arg}\n\n"
        f"{second_name} speech:\n{second_arg}\n\n"
        f"Return JSON only: {json_example}."
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


__all__ = ["build_final_prompt", "build_round_prompt", "parse_json_response", "score_from_data"]
