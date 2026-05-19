from collections.abc import Callable
from typing import TypeVar

ResultT = TypeVar("ResultT")


class TimeoutMixin:
    """Mixin placeholder for timeout-governed operations."""

    def enforce_timeout(self, operation: Callable[[], ResultT]) -> ResultT:
        """Execute an operation through the timeout boundary."""
        return operation()


__all__ = ["TimeoutMixin"]
