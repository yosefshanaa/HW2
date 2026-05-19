from typing import Any

from debate_simulator.models.agent import TurnContext


class DebaterService:
    """Service wrapper for debater orchestration."""

    def __init__(self, debater_agent: Any) -> None:
        """Create a debater service."""
        self.debater_agent = debater_agent

    def research(self, topic: str) -> Any:
        """Delegate research to the debater."""
        return self.debater_agent.research(topic)

    def run_turn(self, context: TurnContext) -> Any:
        """Delegate a turn to the debater."""
        return self.debater_agent.run_turn(context)


__all__ = ["DebaterService"]
