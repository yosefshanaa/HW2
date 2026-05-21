from abc import ABC
from pathlib import Path
from typing import Any

from debate_simulator.agents.base_agent import BaseAgent
from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import Penalty
from debate_simulator.shared.constants import AgentRole, PenaltyPoints, PenaltyType, Stance
from debate_simulator.skills.base_skill import SkillResult

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_DEBATER_PROMPT = (_PROMPTS_DIR / "debater_system.md").read_text(encoding="utf-8")
_REPETITION_OVERLAP_THRESHOLD = 0.5
_WORD_COUNT_PENALTY_THRESHOLD = 90


def _count_words(text: str) -> int:
    """Count words excluding URL tokens."""
    return sum(1 for w in text.split() if "://" not in w)


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
        notes = self.research_notes or context.research or ["No external notes."]
        research_notes = "\n".join(notes)
        debate_history = "\n---\n".join(context.debate_history) if context.debate_history else "No prior rounds."
        prev_args = "\n".join(f"- {arg}" for arg in self.previous_arguments) if self.previous_arguments else "None yet."
        used_sources = "\n".join(f"- {s}" for s in self.used_sources) if self.used_sources else "None yet."
        judge_feedback_block = ""
        if context.judge_feedback:
            judge_feedback_block = (
                f"Judge feedback on your previous round:\n{context.judge_feedback}\n"
                "Improve based on this feedback. Do not repeat the same weaknesses."
            )
        return (
            _DEBATER_PROMPT
            .replace("{agent_name}", self.name)
            .replace("{topic}", context.topic)
            .replace("{round_number}", str(context.round_number))
            .replace("{total_rounds}", str(total_rounds))
            .replace("{stance}", self.stance.value)
            .replace(
                "{opponent_last_argument}",
                context.opponent_last_argument or "No previous argument. Open with your strongest case.",
            )
            .replace("{your_previous_arguments}", prev_args)
            .replace("{used_sources}", used_sources)
            .replace("{debate_history}", debate_history)
            .replace("{research_notes}", research_notes)
            .replace("{judge_feedback_block}", judge_feedback_block)
            .replace("{max_lines}", str(max_lines))
            .replace("{max_words}", str(max_words))
        )

    def _execute_skills(self, context: TurnContext) -> dict[str, SkillResult]:
        return {}

    def _call_llm(self, prompt: str) -> str:
        return self.llm_client.complete(prompt)

    def _validate_response(self, response: str) -> AgentResponse:
        text = self._sanitize_response(response)
        penalties = []
        word_count = _count_words(text)
        if word_count > self.current_max_words:
            penalties.append(
                Penalty(
                    type=PenaltyType.EXCEED_LINES,
                    points=-5,
                    reason=f"response exceeded {self.current_max_words} word limit ({word_count} words, URLs excluded)",
                    agent=self.role.value,
                )
            )
        if len(text.splitlines()) > self.current_max_lines:
            penalties.append(
                Penalty(
                    type=PenaltyType.EXCEED_LINES,
                    points=-5,
                    reason="response exceeded the line limit",
                    agent=self.role.value,
                )
            )
        rep_penalty = self._check_repetition(text)
        if rep_penalty:
            penalties.append(rep_penalty)
        src_penalty = self._check_source_reuse(text)
        if src_penalty:
            penalties.append(src_penalty)
        self.previous_arguments.append(text)
        self._extract_sources(text)
        return AgentResponse.from_text(text, time_seconds=0, penalties=penalties)

    def _check_repetition(self, text: str) -> Penalty | None:
        """Detect if response reuses phrases from any prior argument via bigram overlap."""
        if not self.previous_arguments:
            return None
        current_bigrams = set(zip(text.lower().split(), text.lower().split()[1:], strict=False))
        if not current_bigrams:
            return None
        for prev in self.previous_arguments:
            prev_bigrams = set(zip(prev.lower().split(), prev.lower().split()[1:], strict=False))
            if not prev_bigrams:
                continue
            overlap = len(current_bigrams & prev_bigrams) / len(current_bigrams | prev_bigrams)
            if overlap > _REPETITION_OVERLAP_THRESHOLD:
                return Penalty(
                    type=PenaltyType.REPETITION,
                    points=PenaltyPoints.REPETITION.value,
                    reason=f"argument bigram overlap {overlap:.0%} with a prior round",
                    agent=self.role.value,
                )
        return None

    def _extract_sources(self, text: str) -> None:
        """Extract cited source names from response for reuse tracking."""
        import re

        for pattern in [r'"([^"]+)"', r"'([^']+)'"]:
            for match in re.findall(pattern, text):
                if len(match) > 4 and match not in self.used_sources:
                    self.used_sources.append(match)
        for word in text.split():
            if word.startswith("http") and word not in self.used_sources:
                self.used_sources.append(word)
        for source in self.known_sources:
            if source in text and source not in self.used_sources:
                self.used_sources.append(source)
        inline_names = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', text)
        for name in inline_names:
            if len(name) > 5 and name not in self.used_sources:
                self.used_sources.append(name)

    def _check_source_reuse(self, text: str) -> Penalty | None:
        """Penalize if a previously used citation appears again."""
        for source in self.used_sources[:-1]:
            if len(source) < 4:
                continue
            if source in text:
                return Penalty(
                    type=PenaltyType.REPETITION,
                    points=PenaltyPoints.REPETITION.value,
                    reason=f"reused citation: {source[:60]}",
                    agent=self.role.value,
                )
            if len(source.split()) >= 2 and source.split()[0] in text:
                short = source.split()[0]
                prior_first_words = [s.split()[0] for s in self.used_sources[:-1] if len(s.split()) >= 2]
                if short in prior_first_words and short not in ["The", "This", "According"]:
                    return Penalty(
                        type=PenaltyType.REPETITION,
                        points=PenaltyPoints.REPETITION.value,
                        reason=f"reused citation: {source[:60]}",
                        agent=self.role.value,
                    )
        return None

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
