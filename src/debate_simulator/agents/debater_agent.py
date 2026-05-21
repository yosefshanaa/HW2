from abc import ABC
from pathlib import Path
from typing import Any

from debate_simulator.agents.base_agent import BaseAgent
from debate_simulator.agents.debater_helpers import (
    apply_limits,
    build_debater_prompt,
)
from debate_simulator.agents.repetition import check_repetition, check_source_reuse, extract_sources
from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.shared.constants import AgentRole, Stance
from debate_simulator.skills.base_skill import SkillResult

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_DEBATER_PROMPT = (_PROMPTS_DIR / "debater_system.md").read_text(encoding="utf-8")
_WORD_COUNT_PENALTY_THRESHOLD = 90


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
        self.current_max_lines = 2
        self.current_max_words = _WORD_COUNT_PENALTY_THRESHOLD
        self.previous_arguments: list[str] = []
        self.used_sources: list[str] = []
        self.known_sources: list[str] = []

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
            if title and len(title) > 3:
                self.known_sources.append(title)
        return self.research_notes

    def build_argument(self, topic: str) -> str:
        """Build an argument for the configured stance."""
        return self.llm_client.complete(f"Build {self.stance.value} argument: {topic}")

    def build_rebuttal(self, opponent_argument: str) -> str:
        """Build a rebuttal to the opponent's argument."""
        return self.llm_client.complete(f"Rebut: {opponent_argument}")

    def _build_prompt(self, context: TurnContext) -> str:
        max_lines = int(context.metadata.get("max_lines", 2))
        total_rounds = int(context.metadata.get("total_rounds", 6))
        max_words = int(context.metadata.get("max_words", _WORD_COUNT_PENALTY_THRESHOLD))
        self.current_max_lines = max_lines
        self.current_max_words = max_words
        return build_debater_prompt(
            template=_DEBATER_PROMPT,
            agent_name=self.name,
            topic=context.topic,
            round_number=context.round_number,
            total_rounds=total_rounds,
            stance=self.stance.value,
            opponent_last_argument=context.opponent_last_argument,
            previous_arguments=self.previous_arguments,
            used_sources=self.used_sources,
            debate_history=context.debate_history or [],
            research_notes=self.research_notes or context.research or [],
            judge_feedback=context.judge_feedback or "",
            max_lines=max_lines,
            max_words=max_words,
        )

    def _execute_skills(self, context: TurnContext) -> dict[str, SkillResult]:
        return {}

    def _call_llm(self, prompt: str) -> str:
        return self.llm_client.complete(prompt)

    def _validate_response(self, response: str) -> AgentResponse:
        text = self._sanitize_response(response)
        penalties = apply_limits(text, self.current_max_words, self.current_max_lines, self.role)
        rep_penalty = check_repetition(text, self.previous_arguments, self.role.value)
        if rep_penalty:
            penalties.append(rep_penalty)
        src_penalty = check_source_reuse(text, self.used_sources, self.role.value)
        if src_penalty:
            penalties.append(src_penalty)
        self.previous_arguments.append(text)
        extract_sources(text, self.used_sources, self.known_sources)
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
