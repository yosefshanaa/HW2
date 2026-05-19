import time
from abc import ABC, abstractmethod
from typing import Any, final

from debate_simulator.mixins import LoggingMixin, SkillRegistryMixin, TimeoutMixin
from debate_simulator.models.agent import AgentResponse, Message, TurnContext
from debate_simulator.shared.constants import AgentRole
from debate_simulator.skills.base_skill import SkillResult


class BaseAgent(LoggingMixin, TimeoutMixin, SkillRegistryMixin, ABC):
    """Abstract agent governed by a Template Method turn flow."""

    def __init__(
        self,
        name: str,
        role: AgentRole,
        llm_client: Any,
        skills: dict[str, Any] | None = None,
        logger: Any | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        """Create a base agent."""
        self.name = name
        self.role = role
        self.llm_client = llm_client
        self.skills = skills or {}
        self.logger = logger
        self.memory: list[Message] = []
        self.last_skill_results: dict[str, SkillResult] = {}
        self.timeout_seconds = timeout_seconds

    @final
    def run_turn(self, context: TurnContext) -> AgentResponse:
        """Run one governed agent turn using the Template Method hooks."""
        started = time.perf_counter()
        prompt = self._build_prompt(context)
        self.last_skill_results = self._execute_skills(context)
        raw_response = self._call_llm(prompt)
        response = self._validate_response(raw_response)
        if response.time_seconds == 0:
            response.time_seconds = time.perf_counter() - started
        self.memory.append(Message(role=self.role, content=response.text))
        return response

    @abstractmethod
    def _build_prompt(self, context: TurnContext) -> str:
        """Build the LLM prompt for the turn."""

    @abstractmethod
    def _execute_skills(self, context: TurnContext) -> dict[str, SkillResult]:
        """Execute skills needed for the turn."""

    @abstractmethod
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM for the turn."""

    @abstractmethod
    def _validate_response(self, response: str) -> AgentResponse:
        """Validate and structure the LLM response."""


__all__ = ["BaseAgent"]
