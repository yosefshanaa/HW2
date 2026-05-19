import time
from collections.abc import Callable
from typing import TypeVar

from debate_simulator.shared.constants import FifoDefault

ResultT = TypeVar("ResultT")


class TimeoutMixin:
    """Mixin that enforces a time budget on operations."""

    timeout_seconds: float = FifoDefault.READ_TIMEOUT_SECONDS.value

    def enforce_timeout(self, operation: Callable[[], ResultT]) -> ResultT:
        """Execute *operation* and raise TimeoutError if it exceeds the budget."""
        deadline = time.monotonic() + self.timeout_seconds
        result = operation()
        if time.monotonic() > deadline:
            raise TimeoutError(
                f"{operation.__qualname__} exceeded {self.timeout_seconds}s budget"
            )
        return result


__all__ = ["TimeoutMixin"]
