from typing import Any


class LoggingMixin:
    """Mixin that provides a lightweight logging hook."""

    logger: Any | None = None

    def log(self, level: str, message: str) -> None:
        """Log a message when a logger is configured."""
        if self.logger:
            self.logger(level, self.__class__.__name__, message)


__all__ = ["LoggingMixin"]
