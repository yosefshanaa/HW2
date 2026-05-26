import random
from pathlib import Path
from typing import Any

from debate_simulator.agents.base_agent import BaseAgent
from debate_simulator.agents.judge_helpers import (
    average_round_scores,
    fallback_round_data,
    map_penalties,
)
from debate_simulator.agents.judge_prompts import (
    build_final_prompt,
    build_round_prompt,
    parse_json_response,
)
from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import RoundEvaluation, Score
from debate_simulator.shared.constants import AgentRole, ScoreDefault
from debate_simulator.skills.base_skill import SkillResult

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_JUDGE_PROMPT = (_PROMPTS_DIR / "judge_system.md").read_text(encoding="utf-8")


class JudgeAgent(BaseAgent):
    """Judge agent that evaluates rounds and final scores without coaching debaters."""

    def __init__(self, name: str, llm_client: Any, skills: dict[str, Any] | None = None) -> None:
        """Create a judge agent."""
        super().__init__(name=name, role=AgentRole.JUDGE, llm_client=llm_client, skills=skills)
        self._pro_history: list[str] = []
        self._con_history: list[str] = []
        self._pro_round_scores: list[float] = []
        self._con_round_scores: list[float] = []
        self.rubric_notes: list[str] = []

    def research(self, topic: str) -> list[str]:
        """Search for debate judging criteria without researching the debate topic."""
        if "web_search" not in self.skills:
            return self.rubric_notes
        result = self.skills["web_search"].execute(
            {"query": "competitive debate judging criteria claim warrant impact rebuttal"}
        )
        if not result.success:
            self.rubric_notes.append(f"Judge rubric search unavailable: {result.error}")
            return self.rubric_notes
        for item in result.data.get("results", [])[:3]:
            title = getattr(item, "title", "")
            snippet = getattr(item, "snippet", "")
            self.rubric_notes.append(f"{title}: {snippet}")
        return self.rubric_notes

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
                        self._template(), round_number, pro_argument, con_argument, debate_history
                    )
                )
            )
        except Exception:
            data = fallback_round_data(pro_argument, con_argument)
        self._pro_history.append(pro_argument)
        self._con_history.append(con_argument)
        pro_raw_pen = [p for p in data.get("pro_penalties", []) if isinstance(p, str)]
        con_raw_pen = [p for p in data.get("con_penalties", []) if isinstance(p, str)]
        default_score = ScoreDefault.DEFAULT_SPEAKER_SCORE.value
        pro_score = _clamp(float(data.get("pro_speaker_score", default_score)))
        con_score = _clamp(float(data.get("con_speaker_score", default_score)))
        jitter = ScoreDefault.JITTER_RANGE.value
        pro_score = _clamp(pro_score + random.uniform(-jitter, jitter))
        con_score = _clamp(con_score + random.uniform(-jitter, jitter))
        self._pro_round_scores.append(pro_score)
        self._con_round_scores.append(con_score)
        return RoundEvaluation(
            pro_notes=str(data.get("pro_notes", "")),
            con_notes=str(data.get("con_notes", "")),
            pro_penalties=map_penalties("pro", pro_raw_pen),
            con_penalties=map_penalties("con", con_raw_pen),
            pro_speaker_score=pro_score,
            con_speaker_score=con_score,
            judge_message=None,
        )

    def evaluate_debate(self, transcript: list[str]) -> dict[str, Score]:
        """Average per-round speaker scores into final quality scores."""
        return average_round_scores(self._pro_round_scores, self._con_round_scores)

    def declare_winner(self, scores: dict[str, Score]) -> str:
        """Declare a decisive winner. Totals already include averaged penalties."""
        pro, con = scores["pro"].total, scores["con"].total
        if pro == con:
            return random.choice(["pro", "con"])
        return "pro" if pro > con else "con"

    def _build_prompt(self, context: TurnContext) -> str:
        return self._template().replace("{topic}", context.topic)

    def _execute_skills(self, context: TurnContext) -> dict[str, SkillResult]:
        return {}

    def _call_llm(self, prompt: str) -> str:
        return self.llm_client.complete(prompt)

    def _validate_response(self, response: str) -> AgentResponse:
        return AgentResponse.from_text(response, time_seconds=0)

    def _final_prompt(self, transcript: list[str]) -> str:
        return build_final_prompt(self._template(), transcript)

    def _fallback_scores(self, transcript: list[str]) -> dict[str, Score]:
        return average_round_scores(self._pro_round_scores, self._con_round_scores)

    def _template(self) -> str:
        if not self.rubric_notes:
            return _JUDGE_PROMPT
        return _JUDGE_PROMPT + "\n\nInternet-derived judging criteria:\n" + "\n".join(
            self.rubric_notes
        )


def _clamp(score: float) -> float:
    return max(ScoreDefault.SPEAKER_MIN.value, min(ScoreDefault.SPEAKER_MAX.value, score))


__all__ = ["JudgeAgent"]
