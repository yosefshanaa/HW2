from typing import Any


class SkillRegistryMixin:
    """Mixin that stores and executes named skills."""

    skills: dict[str, Any]

    def register_skill(self, name: str, skill: Any) -> None:
        """Register a skill by name."""
        self.skills[name] = skill

    def use_skill(self, name: str, payload: dict[str, Any]) -> Any:
        """Execute a registered skill."""
        return self.skills[name].execute(payload)


__all__ = ["SkillRegistryMixin"]
