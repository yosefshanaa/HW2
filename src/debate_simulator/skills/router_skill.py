from pathlib import Path
from typing import Any

from debate_simulator.skills.base_skill import BaseSkill, SkillResult


class RouterSkill(BaseSkill):
    """Router skill that selects a skill from local skill descriptions."""

    name = "router"
    description = "Selects an appropriate project-local skill."

    def __init__(self, skills_path: str | Path) -> None:
        """Create a router for a skills directory."""
        self.skills_path = Path(skills_path)

    def execute(self, payload: dict[str, Any]) -> SkillResult:
        """Select a skill whose description overlaps the context."""
        context = str(payload.get("context", "")).lower()
        descriptions = self._load_descriptions()
        if not descriptions:
            return SkillResult.fail("no skills available")
        selected = max(descriptions, key=lambda item: self._score(context, item[1]))
        return SkillResult.ok({"skill": selected[0]})

    def _load_descriptions(self) -> list[tuple[str, str]]:
        descriptions: list[tuple[str, str]] = []
        for skill_file in sorted(self.skills_path.glob("*/skill.md")):
            descriptions.append(
                (skill_file.parent.name, skill_file.read_text(encoding="utf-8").lower())
            )
        return descriptions

    def _score(self, context: str, description: str) -> int:
        context_terms = set(context.split())
        description_terms = set(description.split())
        return len(context_terms & description_terms)


__all__ = ["RouterSkill"]
