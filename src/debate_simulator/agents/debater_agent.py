from abc import ABC
from pathlib import Path
from typing import Any

from debate_simulator.agents.base_agent import BaseAgent
from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.shared.constants import AgentRole, Stance
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

    def research(self, topic: str) -> list[str]:
        """Run a lightweight research phase placeholder."""
        self.research_notes.append(topic)
        return self.research_notes

    def build_argument(self, topic: str) -> str:
        """Build an argument for the configured stance."""
        return self.llm_client.complete(f"Build {self.stance.value} argument: {topic}")

    def build_rebuttal(self, opponent_argument: str) -> str:
        """Build a rebuttal to the opponent's argument."""
        return self.llm_client.complete(f"Rebut: {opponent_argument}")

    def _build_prompt(self, context: TurnContext) -> str:
        return (
            _DEBATER_PROMPT
            .replace("{topic}", context.topic)
            .replace("{stance}", self.stance.value)
            .replace(
                "{opponent_last_argument}",
                context.opponent_last_argument or "No previous argument",
            )
        )

    def _execute_skills(self, context: TurnContext) -> dict[str, SkillResult]:
        return {}

    def _call_llm(self, prompt: str) -> str:
        return self.llm_client.complete(prompt)

    def _validate_response(self, response: str) -> AgentResponse:
        return AgentResponse.from_text(response, time_seconds=0)


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
