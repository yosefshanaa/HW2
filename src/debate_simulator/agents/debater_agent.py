from abc import ABC
from pathlib import Path
from typing import Any

from debate_simulator.agents.base_agent import BaseAgent
from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import Penalty
from debate_simulator.shared.constants import AgentRole, PenaltyType, Stance
from debate_simulator.skills.base_skill import SkillResult

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_DEBATER_PROMPT = (_PROMPTS_DIR / "debater_system.md").read_text(encoding="utf-8")


class DebaterAgent(BaseAgent, ABC):
    """Abstract debater agent with fixed stance behavior."""

    stance: Stance

    def __init__(
        self,
        name: str,
        role: AgentRole,
        stance: Stance,
        llm_client: Any,
        skills: dict[str, Any] | None = None,
    ) -> None:
        """Create a debater agent."""
        super().__init__(name=name, role=role, llm_client=llm_client, skills=skills)
        self.stance = stance
        self.research_notes: list[str] = []
        self.current_max_lines = 8

    def research(self, topic: str) -> list[str]:
        """Run optional project-local web-search research for the topic."""
        if "web_search" not in self.skills:
            self.research_notes.append(topic)
            return self.research_notes
        result = self.skills["web_search"].execute(
            {"query": f"{topic} debate facts evidence {self.stance.value}"}
        )
        if not result.success:
            self.research_notes.append(f"Search unavailable: {result.error}")
            return self.research_notes
        for item in result.data.get("results", [])[:3]:
            title = getattr(item, "title", "")
            snippet = getattr(item, "snippet", "")
            url = getattr(item, "url", "")
            self.research_notes.append(f"{title}: {snippet} ({url})")
        return self.research_notes

    def build_argument(self, topic: str) -> str:
        """Build an argument for the configured stance."""
        return self.llm_client.complete(f"Build {self.stance.value} argument: {topic}")

    def build_rebuttal(self, opponent_argument: str) -> str:
        """Build a rebuttal to the opponent's argument."""
        return self.llm_client.complete(f"Rebut: {opponent_argument}")

    def _build_prompt(self, context: TurnContext) -> str:
        max_lines = int(context.metadata.get("max_lines", 8))
        self.current_max_lines = max_lines
        notes = self.research_notes or context.research or ["No external notes."]
        research_notes = "\n".join(notes)
        return (
            _DEBATER_PROMPT
            .replace("{agent_name}", self.name)
            .replace("{topic}", context.topic)
            .replace("{round_number}", str(context.round_number))
            .replace("{stance}", self.stance.value)
            .replace(
                "{opponent_last_argument}",
                context.opponent_last_argument or "No previous argument. Open with your case.",
            )
            .replace("{research_notes}", research_notes)
            .replace("{max_lines}", str(max_lines))
        )

    def _execute_skills(self, context: TurnContext) -> dict[str, SkillResult]:
        return {}

    def _call_llm(self, prompt: str) -> str:
        return self.llm_client.complete(prompt)

    def _validate_response(self, response: str) -> AgentResponse:
        text = self._sanitize_response(response)
        penalties = []
        if len(text.splitlines()) > self.current_max_lines:
            penalties.append(
                Penalty(
                    type=PenaltyType.EXCEED_LINES,
                    points=-5,
                    reason="response exceeded the default line limit",
                    agent=self.role.value,
                )
            )
        return AgentResponse.from_text(text, time_seconds=0, penalties=penalties)

    def _sanitize_response(self, response: str) -> str:
        text = response.strip()
        echoed_prompt = "You are Son Agent" in text or "Recommended structure:" in text
        if text and not echoed_prompt:
            return text
        side = (
            "the first side in the comparison"
            if self.stance == Stance.PRO
            else "the second side in the comparison"
        )
        return (
            f"I will defend {side} by focusing on stronger evidence and clearer reasoning.\n"
            "The opposing case must prove that its examples outweigh the broader record.\n"
            "My position is stronger because it compares achievements, consistency, and impact together.\n"
            "For that reason, my side currently gives the judge the more complete argument."
        )


class ProDebaterAgent(DebaterAgent):
    """Concrete debater assigned to the pro stance."""

    def __init__(self, name: str, llm_client: Any, skills: dict[str, Any] | None = None) -> None:
        """Create a pro debater."""
        super().__init__(name, AgentRole.PRO, Stance.PRO, llm_client, skills)


class ConDebaterAgent(DebaterAgent):
    """Concrete debater assigned to the con stance."""

    def __init__(self, name: str, llm_client: Any, skills: dict[str, Any] | None = None) -> None:
        """Create a con debater."""
        super().__init__(name, AgentRole.CON, Stance.CON, llm_client, skills)


__all__ = ["ConDebaterAgent", "DebaterAgent", "ProDebaterAgent"]
