from typing import Any

from debate_simulator.skills.base_skill import BaseSkill, SkillResult


class FactCheckSkill(BaseSkill):
    """Skill that asks the LLM to verify a claim."""

    name = "fact_check"
    description = "Verify factual claims against available context."

    def __init__(self, llm_client: Any) -> None:
        """Create a fact-check skill."""
        self.llm_client = llm_client

    def execute(self, payload: dict[str, Any]) -> SkillResult:
        """Verify a claim using the LLM client."""
        claim = str(payload.get("claim", ""))
        context = str(payload.get("context", ""))
        verdict = self.llm_client.complete(f"Verify claim: {claim}\nContext: {context}")
        return SkillResult.ok({"verdict": verdict})


__all__ = ["FactCheckSkill"]
