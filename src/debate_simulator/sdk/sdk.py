import json
from pathlib import Path
from typing import Any

from debate_simulator.agents import ConDebaterAgent, JudgeAgent, ProDebaterAgent
from debate_simulator.services import DebateEngine
from debate_simulator.shared import ApiGatekeeper, LlmClient, load_settings


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
            self.engine = self._build_default_engine()
        return self.engine.start_debate(topic, config=config)

    def list_topics(self) -> list[str]:
        """List bundled debate topic titles."""
        topics = json.loads(self.topics_path.read_text(encoding="utf-8"))
        return [str(topic["topic"]) for topic in topics]

    def get_results(self, debate_id: str) -> dict[str, Any]:
        """Load a debate result JSON file by identifier."""
        result_path = self.results_path / f"{debate_id}.json"
        return json.loads(result_path.read_text(encoding="utf-8"))

    def _build_default_engine(self) -> DebateEngine:
        settings = load_settings()
        api_key = settings.require_openai_api_key()
        from openai import OpenAI

        gatekeeper = ApiGatekeeper(rate_limits=settings.rate_limits.rate_limits)
        llm = LlmClient(
            openai_client=OpenAI(api_key=api_key),
            gatekeeper=gatekeeper,
            model=settings.setup.llm.model,
            temperature=settings.setup.llm.temperature,
            max_tokens=settings.setup.llm.max_tokens,
        )
        return DebateEngine(
            pro_agent=ProDebaterAgent("pro", llm),
            con_agent=ConDebaterAgent("con", llm),
            judge_agent=JudgeAgent("judge", llm),
            results_path=self.results_path,
        )


__all__ = ["DebateSimulatorSDK"]
