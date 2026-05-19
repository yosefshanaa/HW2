import time

import pytest

from debate_simulator.mixins.logging_mixin import LoggingMixin
from debate_simulator.mixins.timeout_mixin import TimeoutMixin


def test_logging_mixin_delegates_to_configured_logger() -> None:
    """LoggingMixin.log() forwards when a logger is set."""
    received: list[tuple[str, str, str]] = []

    class Agent(LoggingMixin):
        pass

    agent = Agent()
    agent.logger = lambda level, name, msg: received.append((level, name, msg))
    agent.log("INFO", "hello")

    assert received == [("INFO", "Agent", "hello")]


def test_logging_mixin_noop_without_logger() -> None:
    """LoggingMixin.log() silently does nothing when no logger is configured."""
    class Agent(LoggingMixin):
        pass

    agent = Agent()
    agent.logger = None
    agent.log("ERROR", "should not crash")


def test_timeout_mixin_passes_fast_operations() -> None:
    """TimeoutMixin.enforce_timeout() returns result for fast operations."""
    class Agent(TimeoutMixin):
        pass

    agent = Agent()
    agent.timeout_seconds = 5.0
    result = agent.enforce_timeout(lambda: 42)

    assert result == 42


def test_timeout_mixin_raises_on_slow_operations() -> None:
    """TimeoutMixin.enforce_timeout() raises TimeoutError if budget exceeded."""
    class Agent(TimeoutMixin):
        pass

    agent = Agent()
    agent.timeout_seconds = 0.0

    with pytest.raises(TimeoutError):
        agent.enforce_timeout(lambda: time.sleep(0.01))
