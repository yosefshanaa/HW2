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
        """Build an argument through the LLM client.

        When a fully-rendered ``prompt`` is supplied (the Pro debater routes its own
        system prompt through this skill), it is completed directly; otherwise an
        argument prompt is composed from topic/stance/evidence fields.
        """
        if "prompt" in payload:
            argument = self.llm_client.complete(str(payload["prompt"]))
        else:
            topic = str(payload.get("topic", ""))
            stance = str(payload.get("stance", ""))
            evidence = str(payload.get("evidence", ""))
            argument = self.llm_client.complete(
                f"Build argument for {stance}: {topic}\nEvidence: {evidence}"
            )
        return SkillResult.ok({"argument": argument})


__all__ = ["ArgumentBuilderSkill"]
