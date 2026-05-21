import random
from pathlib import Path
from typing import Any

from debate_simulator.agents.base_agent import BaseAgent
from debate_simulator.agents.judge_helpers import (
    average_round_scores,
    build_final_prompt,
    build_round_prompt,
    detect_repetition,
    fallback_round_data,
    map_penalties,
    parse_json_response,
)
from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import RoundEvaluation, Score
from debate_simulator.shared.constants import AgentRole
from debate_simulator.skills.base_skill import SkillResult

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_JUDGE_PROMPT = (_PROMPTS_DIR / "judge_system.md").read_text(encoding="utf-8")
_SPEAKER_MIN = 50.0
_SPEAKER_MAX = 100.0


class JudgeAgent(BaseAgent):
    """Judge agent that evaluates rounds and final scores without coaching debaters."""

    def __init__(self, name: str, llm_client: Any, skills: dict[str, Any] | None = None) -> None:
        """Create a judge agent."""
        super().__init__(name=name, role=AgentRole.JUDGE, llm_client=llm_client, skills=skills)
        self._pro_history: list[str] = []
        self._con_history: list[str] = []
        self._pro_round_scores: list[float] = []
        self._con_round_scores: list[float] = []

    def observe_round(
        self,
        round_number: int,
        pro_argument: str,
        con_argument: str,
        debate_history: list[str] | None = None,
    ) -> RoundEvaluation:
        """Observe one round and return private judge notes with speaker scores."""
        try:
            data = parse_json_response(
                self.llm_client.complete(
                    build_round_prompt(
                        _JUDGE_PROMPT, round_number, pro_argument, con_argument, debate_history
                    )
                )
            )
        except Exception:
            data = fallback_round_data(pro_argument, con_argument)
        self._pro_history.append(pro_argument)
        self._con_history.append(con_argument)
        penalties = list(data.get("con_penalties", [])) + list(data.get("pro_penalties", []))
        penalties += detect_repetition(
            pro_argument, con_argument, self._pro_history, self._con_history
        )
        con_pen = [p for p in penalties if isinstance(p, str)]
        pro_score = _clamp(float(data.get("pro_speaker_score", 70)))
        con_score = _clamp(float(data.get("con_speaker_score", 70)))
        pro_score += random.uniform(-2.5, 2.5)
        con_score += random.uniform(-2.5, 2.5)
        pro_score = _clamp(pro_score)
        con_score = _clamp(con_score)
        self._pro_round_scores.append(pro_score)
        self._con_round_scores.append(con_score)
        return RoundEvaluation(
            pro_notes=str(data.get("pro_notes", "")),
            con_notes=str(data.get("con_notes", "")),
            pro_penalties=map_penalties("pro", []),
            con_penalties=map_penalties("con", con_pen),
            pro_speaker_score=pro_score,
            con_speaker_score=con_score,
            judge_message=None,
        )

    def evaluate_debate(self, transcript: list[str]) -> dict[str, Score]:
        """Average per-round speaker scores into final quality scores (50-100 scale)."""
        return average_round_scores(self._pro_round_scores, self._con_round_scores)

    def declare_winner(self, scores: dict[str, Score]) -> str:
        """Declare pro, con, or tie based on quality scores."""
        if abs(scores["pro"].total - scores["con"].total) < 2.0:
            return "tie"
        return "pro" if scores["pro"].total > scores["con"].total else "con"

    def _build_prompt(self, context: TurnContext) -> str:
        return _JUDGE_PROMPT.replace("{topic}", context.topic)

    def _execute_skills(self, context: TurnContext) -> dict[str, SkillResult]:
        return {}

    def _call_llm(self, prompt: str) -> str:
        return self.llm_client.complete(prompt)

    def _validate_response(self, response: str) -> AgentResponse:
        return AgentResponse.from_text(response, time_seconds=0)

    def _final_prompt(self, transcript: list[str]) -> str:
        return build_final_prompt(_JUDGE_PROMPT, transcript)

    def _fallback_scores(self, transcript: list[str]) -> dict[str, Score]:
        return average_round_scores(self._pro_round_scores, self._con_round_scores)


def _clamp(score: float) -> float:
    return max(_SPEAKER_MIN, min(_SPEAKER_MAX, score))


__all__ = ["JudgeAgent"]
