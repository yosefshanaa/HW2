import json
from pathlib import Path
from typing import Any

from debate_simulator.agents.base_agent import BaseAgent
from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import Penalty, RoundEvaluation, Score
from debate_simulator.shared.constants import AgentRole, PenaltyType
from debate_simulator.skills.base_skill import SkillResult

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_JUDGE_PROMPT = (_PROMPTS_DIR / "judge_system.md").read_text(encoding="utf-8")
_DIMENSIONS = ["argument_strength", "rebuttal_effectiveness", "evidence_research", "rhetorical_quality", "compliance"]
_JUDGE_REPETITION_THRESHOLD = 0.7


class JudgeAgent(BaseAgent):
    """Judge agent that evaluates rounds and final scores without coaching debaters."""

    def __init__(self, name: str, llm_client: Any, skills: dict[str, Any] | None = None) -> None:
        """Create a judge agent."""
        super().__init__(name=name, role=AgentRole.JUDGE, llm_client=llm_client, skills=skills)
        self._pro_history: list[str] = []
        self._con_history: list[str] = []

    def observe_round(
        self,
        round_number: int,
        pro_argument: str,
        con_argument: str,
        debate_history: list[str] | None = None,
    ) -> RoundEvaluation:
        """Observe one round and return private judge notes."""
        try:
            data = self._json_from_llm(
                self._round_prompt(round_number, pro_argument, con_argument, debate_history)
            )
        except Exception:
            data = self._fallback_round(pro_argument, con_argument)
        self._pro_history.append(pro_argument)
        self._con_history.append(con_argument)
        penalties = list(data.get("con_penalties", [])) + list(data.get("pro_penalties", []))
        penalties += self._auto_repetition_penalties(pro_argument, con_argument)
        con_pen = [p for p in penalties if isinstance(p, str)]
        pro_pen = []
        con_penalties = self._penalties("con", con_pen)
        pro_penalties = self._penalties("pro", pro_pen)
        return RoundEvaluation(
            pro_notes=str(data.get("pro_notes", "")),
            con_notes=str(data.get("con_notes", "")),
            pro_penalties=pro_penalties,
            con_penalties=con_penalties,
            judge_message=None,
        )

    def _auto_repetition_penalties(self, pro_argument: str, con_argument: str) -> list[str]:
        """Auto-detect repetition when LLM judge misses it."""
        flagged: list[str] = []
        if self._is_repetitive(pro_argument, self._pro_history[:-1]):
            flagged.append("repetition")
        if self._is_repetitive(con_argument, self._con_history[:-1]):
            flagged.append("repetition")
        return flagged

    def _is_repetitive(self, text: str, history: list[str]) -> bool:
        """Check if text has high word overlap with any prior argument."""
        if not history:
            return False
        current_words = set(text.lower().split())
        if len(current_words) < 5:
            return False
        for prev in history:
            prev_words = set(prev.lower().split())
            if not prev_words:
                continue
            overlap = len(current_words & prev_words) / len(current_words | prev_words)
            if overlap > _JUDGE_REPETITION_THRESHOLD:
                return True
        return False

    def evaluate_debate(self, transcript: list[str]) -> dict[str, Score]:
        """Evaluate a transcript and return final scores."""
        try:
            data = self._json_from_llm(self._final_prompt(transcript))
            return {
                "pro": self._score_from_data(data.get("pro", {})),
                "con": self._score_from_data(data.get("con", {})),
            }
        except Exception:
            return self._fallback_scores(transcript)

    def declare_winner(self, scores: dict[str, Score]) -> str:
        """Declare pro, con, or tie from final scores."""
        pro_total = scores["pro"].total
        con_total = scores["con"].total
        if pro_total == con_total:
            return "tie"
        return "pro" if pro_total > con_total else "con"

    def _build_prompt(self, context: TurnContext) -> str:
        return _JUDGE_PROMPT.replace("{topic}", context.topic)

    def _execute_skills(self, context: TurnContext) -> dict[str, SkillResult]:
        return {}

    def _call_llm(self, prompt: str) -> str:
        return self.llm_client.complete(prompt)

    def _validate_response(self, response: str) -> AgentResponse:
        return AgentResponse.from_text(response, time_seconds=0)

    def _round_prompt(
        self,
        round_number: int,
        pro_argument: str,
        con_argument: str,
        debate_history: list[str] | None = None,
    ) -> str:
        history_block = ""
        if debate_history:
            history_block = "\nDebate history (prior rounds):\n" + "\n".join(debate_history[-4:]) + "\n"
        return (
            f"{_JUDGE_PROMPT}\n\n{history_block}"
            f"Evaluate round {round_number}.\n"
            f"Con speech:\n{con_argument}\n\nPro speech:\n{pro_argument}\n\n"
            'Return JSON only: {"con_notes":"...","pro_notes":"...",'
            '"con_penalties":[],"pro_penalties":[]}.'
        )

    def _final_prompt(self, transcript: list[str]) -> str:
        schema = {side: {"breakdown": dict.fromkeys(_DIMENSIONS, 0), "total": 0} for side in ["pro", "con"]}
        return (
            f"{_JUDGE_PROMPT}\n\nFinal transcript JSON lines:\n"
            + "\n".join(transcript)
            + f"\nReturn JSON only using this schema: {json.dumps(schema)}"
        )

    def _json_from_llm(self, prompt: str) -> dict[str, Any]:
        raw = self.llm_client.complete(prompt).strip()
        if raw.startswith("```"):
            raw = raw.strip("`").removeprefix("json").strip()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("judge response is not a JSON object")
        return data

    def _score_from_data(self, data: Any) -> Score:
        if not isinstance(data, dict):
            data = {}
        breakdown = data.get("breakdown", {})
        if not isinstance(breakdown, dict):
            breakdown = {}
        fallback_total = sum(float(breakdown.get(key, 0.0)) for key in _DIMENSIONS) / len(_DIMENSIONS)
        total = float(data.get("total", fallback_total))
        return Score(total=max(min(total, 100.0), 0.0), breakdown=breakdown)

    def _fallback_round(self, pro_argument: str, con_argument: str) -> dict[str, Any]:
        return {
            "pro_notes": self._short_note("pro", pro_argument, con_argument),
            "con_notes": self._short_note("con", con_argument, pro_argument),
            "pro_penalties": [],
            "con_penalties": [],
        }

    def _fallback_scores(self, transcript: list[str]) -> dict[str, Score]:
        totals = {"pro": 60.0, "con": 60.0}
        for raw_round in transcript:
            try:
                row = json.loads(raw_round)
            except json.JSONDecodeError:
                continue
            totals["pro"] += self._argument_points(str(row.get("pro_argument", "")))
            totals["con"] += self._argument_points(str(row.get("con_argument", "")))
        return {
            side: Score(total=min(total, 100.0), breakdown={"fallback": min(total, 100.0)})
            for side, total in totals.items()
        }

    def _argument_points(self, argument: str) -> float:
        evidence_terms = ["because", "evidence", "source", "data", "history", "record", "example"]
        return min(len(argument.split()) / 80, 5.0) + sum(term in argument.lower() for term in evidence_terms)

    def _short_note(self, agent: str, argument: str, opponent: str) -> str:
        addressed = bool(set(argument.lower().split()) & set(opponent.lower().split()))
        status = "addressed the opponent" if addressed else "needs a more direct rebuttal"
        return f"{agent} {status}; argument length {len(argument.split())} words."

    def _penalties(self, agent: str, names: list[Any]) -> list[Penalty]:
        penalties = []
        for name in names:
            try:
                penalty_type = PenaltyType(str(name))
            except ValueError:
                continue
            points = -15 if penalty_type == PenaltyType.STANCE_CONTRADICTION else -5
            if penalty_type in {PenaltyType.IGNORE_REBUTTAL, PenaltyType.EXCEED_TIME, PenaltyType.REPETITION}:
                points = -10
            penalties.append(Penalty(type=penalty_type, points=points, reason=str(name), agent=agent))
        return penalties


__all__ = ["JudgeAgent"]
