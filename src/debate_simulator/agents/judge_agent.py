from typing import Any

from debate_simulator.agents.base_agent import BaseAgent
from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import RoundEvaluation, Score
from debate_simulator.shared.constants import AgentRole
from debate_simulator.skills.base_skill import SkillResult


class JudgeAgent(BaseAgent):
    """Judge agent that listens, evaluates, and never replies during debate."""

    def __init__(self, name: str, llm_client: Any, skills: dict[str, Any] | None = None) -> None:
        """Create a judge agent."""
        super().__init__(name=name, role=AgentRole.JUDGE, llm_client=llm_client, skills=skills)
        self.rubric = ""

    def observe_round(self, round_number: int, pro_argument: str, con_argument: str) -> RoundEvaluation:
        """Observe one round and return private judge notes."""
        notes = f"Round {round_number}: pro={pro_argument}; con={con_argument}"
        return RoundEvaluation(pro_notes=notes, con_notes=notes, judge_message=None)

    def evaluate_debate(self, transcript: list[str]) -> dict[str, Score]:
        """Evaluate a transcript with neutral default scores."""
        score = Score(total=0.0, breakdown={}, penalties_applied=[])
        return {"pro": score, "con": score}

    def declare_winner(self, scores: dict[str, Score]) -> str:
        """Declare pro, con, or tie from final scores."""
        pro_total = scores["pro"].total
        con_total = scores["con"].total
        if pro_total == con_total:
            return "tie"
        return "pro" if pro_total > con_total else "con"

    def _build_prompt(self, context: TurnContext) -> str:
        return f"Judge debate technique for {context.topic}"

    def _execute_skills(self, context: TurnContext) -> dict[str, SkillResult]:
        return {}

    def _call_llm(self, prompt: str) -> str:
        return self.llm_client.complete(prompt)

    def _validate_response(self, response: str) -> AgentResponse:
        return AgentResponse.from_text(response, time_seconds=0)


__all__ = ["JudgeAgent"]
