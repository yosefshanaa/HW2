from typing import Any

from debate_simulator.skills.base_skill import BaseSkill, SkillResult


class RespectCheckSkill(BaseSkill):
    """Skill that checks text against configured disrespect terms."""

    name = "respect_check"
    description = "Detect disrespectful or ad hominem language."

    def __init__(self, disallowed_terms: list[str] | None = None) -> None:
        """Create a respect check skill."""
        self.disallowed_terms = [term.lower() for term in disallowed_terms or []]

    def execute(self, payload: dict[str, Any]) -> SkillResult:
        """Check whether text contains configured disrespect terms."""
        text = str(payload.get("text", "")).lower()
        matches = [term for term in self.disallowed_terms if term in text]
        return SkillResult.ok({"respectful": not matches, "matches": matches})


__all__ = ["RespectCheckSkill"]
