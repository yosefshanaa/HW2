from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from debate_simulator.shared.constants import AgentRole, Stance


class Message(BaseModel):
    """Conversation message stored in agent memory."""

    role: AgentRole
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TurnContext(BaseModel):
    """Structured context for one agent turn."""

    topic: str
    round_number: int
    stance: Stance | None = None
    opponent_last_argument: str = ""
    research: list[str] = Field(default_factory=list)
    memory: list[Message] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Structured response returned by an agent turn."""

    text: str
    lines: int
    time_seconds: float
    penalties: list[Any] = Field(default_factory=list)

    @classmethod
    def from_text(
        cls, text: str, time_seconds: float, penalties: list[Any] | None = None
    ) -> "AgentResponse":
        """Create an agent response and compute line count."""
        return cls(
            text=text,
            lines=len(text.splitlines()),
            time_seconds=time_seconds,
            penalties=penalties or [],
        )


__all__ = ["AgentResponse", "Message", "TurnContext"]
