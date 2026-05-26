from pathlib import Path

import pytest

from debate_simulator.sdk.sdk import DebateSimulatorSDK


class FakeEngine:
    """Debate engine test double."""

    def start_debate(self, topic: str, config=None):
        """Return a deterministic debate payload."""
        return {"topic": topic, "config": config}


def test_sdk_lists_topics_from_data_file() -> None:
    """SDK lists preconfigured topics from JSON data."""
    sdk = DebateSimulatorSDK(topics_path=Path("data/topics.json"))

    topics = sdk.list_topics()

    assert len(topics) == 10


def test_sdk_start_debate_delegates_to_engine() -> None:
    """SDK delegates debate execution to the domain engine."""
    sdk = DebateSimulatorSDK(engine=FakeEngine(), topics_path=Path("data/topics.json"))

    result = sdk.start_debate("AI", config={"pings": 1})

    assert result == {"topic": "AI", "config": {"pings": 1}}


def test_sdk_default_engine_requires_api_key(monkeypatch) -> None:
    """SDK default engine reports missing API key clearly."""
    monkeypatch.setenv("OPENAI_API_KEY", "your_api_key_here")
    sdk = DebateSimulatorSDK(topics_path=Path("data/topics.json"))

    with pytest.raises(RuntimeError) as error:
        sdk.start_debate("AI")

    assert "OPENAI_API_KEY" in str(error.value)


class FakeConsumer:
    """Log-consumer test double that records being stopped."""

    def __init__(self) -> None:
        """Start in the not-stopped state."""
        self.stopped = False

    def stop(self) -> None:
        """Record the stop request."""
        self.stopped = True


def test_sdk_close_stops_log_consumer_no_orphans() -> None:
    """close() stops the background consumer so no thread is left orphaned."""
    sdk = DebateSimulatorSDK(topics_path=Path("data/topics.json"))
    consumer = FakeConsumer()
    sdk._log_consumer = consumer

    sdk.close()

    assert consumer.stopped is True and sdk._log_consumer is None


def test_sdk_context_manager_closes_on_exit() -> None:
    """Using the SDK as a context manager cleans up on exit, even on error."""
    sdk = DebateSimulatorSDK(topics_path=Path("data/topics.json"))
    consumer = FakeConsumer()
    sdk._log_consumer = consumer

    with pytest.raises(ValueError), sdk:
        raise ValueError("boom")

    assert consumer.stopped is True
