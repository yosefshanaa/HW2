from typing import Any

from debate_simulator.shared.constants import Stance, StanceCue
from debate_simulator.skills.base_skill import BaseSkill, SkillResult


class StanceCheckSkill(BaseSkill):
    """Skill that detects simple contradictions with an assigned stance."""

    name = "stance_check"
    description = "Verify that an argument matches the assigned stance."

    def execute(self, payload: dict[str, Any]) -> SkillResult:
        """Check whether the text contradicts the stance."""
        stance = str(payload.get("stance", "")).lower()
        text = str(payload.get("text", "")).lower()
        contradiction = (
            stance == Stance.PRO.value
            and (Stance.CON.value in text or StanceCue.AGAINST.value in text)
            or stance == Stance.CON.value
            and (Stance.PRO.value in text or StanceCue.FOR.value in text)
        )
        return SkillResult.ok({"contradiction": contradiction})


__all__ = ["StanceCheckSkill"]
