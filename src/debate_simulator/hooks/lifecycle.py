from collections.abc import Callable
from typing import Any


class HookRegistry:
    """Project-local lifecycle hook registry."""

    def __init__(self) -> None:
        """Create an empty registry."""
        self._hooks: dict[str, list[Callable[..., None]]] = {}

    def register_hook(self, event: str, callback: Callable[..., None]) -> None:
        """Register a callback for a lifecycle event."""
        self._hooks.setdefault(event, []).append(callback)

    def emit(self, event: str, **data: Any) -> None:
        """Emit a lifecycle event to registered callbacks."""
        for callback in self._hooks.get(event, []):
            callback(**data)


__all__ = ["HookRegistry"]
