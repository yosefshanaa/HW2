from typing import Any

from debate_simulator.skills.base_skill import BaseSkill, SkillResult


class WebSearchSkill(BaseSkill):
    """Skill that searches the web through the search infrastructure."""

    name = "web_search"
    description = "Search the web for evidence and sources."

    def __init__(self, searcher: Any) -> None:
        """Create a web-search skill."""
        self.searcher = searcher

    def execute(self, payload: dict[str, Any]) -> SkillResult:
        """Search for the provided query."""
        try:
            results = self.searcher.search(str(payload.get("query", "")))
        except Exception as error:
            return SkillResult.fail(str(error))
        return SkillResult.ok({"results": results})


__all__ = ["WebSearchSkill"]
