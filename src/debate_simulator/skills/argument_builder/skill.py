from typing import Any

from debate_simulator.skills.base_skill import BaseSkill, SkillResult


class ArgumentBuilderSkill(BaseSkill):
    """Skill that asks the LLM to build an evidence-based argument."""

    name = "argument_builder"
    description = "Build a structured argument from topic, stance, and evidence."

    def __init__(self, llm_client: Any) -> None:
        """Create an argument builder skill."""
        self.llm_client = llm_client

    def execute(self, payload: dict[str, Any]) -> SkillResult:
        """Build an argument through the LLM client."""
        topic = str(payload.get("topic", ""))
        stance = str(payload.get("stance", ""))
        evidence = str(payload.get("evidence", ""))
        argument = self.llm_client.complete(
            f"Build argument for {stance}: {topic}\nEvidence: {evidence}"
        )
        return SkillResult.ok({"argument": argument})


__all__ = ["ArgumentBuilderSkill"]
