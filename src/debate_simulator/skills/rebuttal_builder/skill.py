from typing import Any

from debate_simulator.skills.base_skill import BaseSkill, SkillResult


class RebuttalBuilderSkill(BaseSkill):
    """Skill that asks the LLM to build a targeted rebuttal."""

    name = "rebuttal_builder"
    description = "Build a rebuttal targeting an opponent argument."

    def __init__(self, llm_client: Any) -> None:
        """Create a rebuttal builder skill."""
        self.llm_client = llm_client

    def execute(self, payload: dict[str, Any]) -> SkillResult:
        """Build a rebuttal through the LLM client.

        When a fully-rendered ``prompt`` is supplied (the Con debater routes its own
        system prompt through this skill), it is completed directly; otherwise a
        rebuttal prompt is composed from the opponent argument and context.
        """
        if "prompt" in payload:
            rebuttal = self.llm_client.complete(str(payload["prompt"]))
        else:
            opponent_argument = str(payload.get("opponent_argument", ""))
            context = str(payload.get("context", ""))
            rebuttal = self.llm_client.complete(
                f"Rebut opponent: {opponent_argument}\nContext: {context}"
            )
        return SkillResult.ok({"rebuttal": rebuttal})


__all__ = ["RebuttalBuilderSkill"]
