import json
from pathlib import Path
from typing import Any


class DebateSimulatorSDK:
    """Single SDK entry point for external consumers."""

    def __init__(
        self,
        engine: Any | None = None,
        topics_path: str | Path = "data/topics.json",
        results_path: str | Path = "results",
    ) -> None:
        """Create the SDK with optional domain engine."""
        self.engine = engine
        self.topics_path = Path(topics_path)
        self.results_path = Path(results_path)

    def start_debate(self, topic: str, config: dict[str, Any] | None = None) -> Any:
        """Start a debate by delegating to the domain engine."""
        if self.engine is None:
            raise RuntimeError("debate engine is not configured")
        return self.engine.start_debate(topic, config=config)

    def list_topics(self) -> list[str]:
        """List bundled debate topic titles."""
        topics = json.loads(self.topics_path.read_text(encoding="utf-8"))
        return [str(topic["topic"]) for topic in topics]

    def get_results(self, debate_id: str) -> dict[str, Any]:
        """Load a debate result JSON file by identifier."""
        result_path = self.results_path / f"{debate_id}.json"
        return json.loads(result_path.read_text(encoding="utf-8"))


__all__ = ["DebateSimulatorSDK"]
