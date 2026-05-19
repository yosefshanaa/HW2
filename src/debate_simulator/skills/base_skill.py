from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SkillResult:
    """Result returned by every skill execution."""

    success: bool
    data: dict[str, Any]
    error: str | None = None

    @classmethod
    def ok(cls, data: dict[str, Any]) -> "SkillResult":
        """Create a successful skill result."""
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> "SkillResult":
        """Create a failed skill result."""
        return cls(success=False, data={}, error=error)


class BaseSkill(ABC):
    """Abstract base class for project-local skills."""

    name: str
    description: str

    @abstractmethod
    def execute(self, payload: dict[str, Any]) -> SkillResult:
        """Execute the skill with structured input."""


__all__ = ["BaseSkill", "SkillResult"]
