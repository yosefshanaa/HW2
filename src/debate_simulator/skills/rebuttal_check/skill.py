from typing import Any

from debate_simulator.skills.base_skill import BaseSkill, SkillResult


class RebuttalCheckSkill(BaseSkill):
    """Skill that verifies a response addresses the previous argument."""

    name = "rebuttal_check"
    description = "Verify that a response addresses the opponent's previous point."

    def execute(self, payload: dict[str, Any]) -> SkillResult:
        """Check whether previous and response text overlap."""
        previous_terms = set(str(payload.get("previous", "")).lower().split())
        response_terms = set(str(payload.get("response", "")).lower().split())
        addressed = bool(previous_terms & response_terms)
        return SkillResult.ok({"addressed": addressed})


__all__ = ["RebuttalCheckSkill"]
