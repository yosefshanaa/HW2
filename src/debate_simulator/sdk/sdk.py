import json
from pathlib import Path
from typing import Any

from debate_simulator.agents import ConDebaterAgent, JudgeAgent, ProDebaterAgent
from debate_simulator.hooks import HookRegistry
from debate_simulator.infrastructure.logging import FifoLogger, LogConsumer, RotatingWriter
from debate_simulator.infrastructure.search.searcher import DuckDuckGoSearcher
from debate_simulator.services import DebateEngine
from debate_simulator.shared import ApiGatekeeper, LlmClient, load_settings
from debate_simulator.shared.constants import ConfigFile
from debate_simulator.skills.argument_builder import ArgumentBuilderSkill
from debate_simulator.skills.rebuttal_builder import RebuttalBuilderSkill
from debate_simulator.skills.web_search import WebSearchSkill


class DebateSimulatorSDK:
    """Single SDK entry point for external consumers."""

    def __init__(
        self,
        engine: Any | None = None,
        topics_path: str | Path = "data/topics.json",
        results_path: str | Path = "results",
        setup_path: str | Path = ConfigFile.SETUP.value,
        hooks: HookRegistry | None = None,
    ) -> None:
        """Create the SDK with optional domain engine."""
        self.engine = engine
        self.topics_path = Path(topics_path)
        self.results_path = Path(results_path)
        self.setup_path = Path(setup_path)
        self.hooks = hooks
        self._log_consumer: LogConsumer | None = None

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

    def close(self) -> None:
        """Stop the background log consumer so no agent/thread is left orphaned."""
        if self._log_consumer is not None:
            self._log_consumer.stop()
            self._log_consumer = None

    def __enter__(self) -> "DebateSimulatorSDK":
        """Enter the SDK context."""
        return self

    def __exit__(self, *exc: Any) -> None:
        """Guarantee cleanup on context exit, including on error."""
        self.close()

    def _build_default_engine(self) -> DebateEngine:
        settings = load_settings(setup_path=self.setup_path)
        api_key = settings.require_openai_api_key()
        from openai import OpenAI

        logger = self._build_logger(settings)
        gatekeeper = ApiGatekeeper(rate_limits=settings.rate_limits.rate_limits, logger=logger.log)
        client_kwargs = {"api_key": api_key}
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url
        llm = LlmClient(
            openai_client=OpenAI(**client_kwargs),
            gatekeeper=gatekeeper,
            model=settings.setup.llm.model,
            temperature=settings.setup.llm.temperature,
            max_tokens=settings.setup.llm.max_tokens,
            prompt_price_per_million=settings.setup.llm.prompt_price_per_million,
            completion_price_per_million=settings.setup.llm.completion_price_per_million,
        )
        search_skill = WebSearchSkill(
            DuckDuckGoSearcher(gatekeeper, settings.setup.search.max_results_per_query)
        )
        # Each son owns a *different* skill so the two never collapse into identical
        # behavior: Pro builds affirmative arguments, Con builds targeted rebuttals.
        return DebateEngine(
            pro_agent=ProDebaterAgent(
                "pro", llm,
                skills={"web_search": search_skill, "argument_builder": ArgumentBuilderSkill(llm)},
            ),
            con_agent=ConDebaterAgent(
                "con", llm,
                skills={"web_search": search_skill, "rebuttal_builder": RebuttalBuilderSkill(llm)},
            ),
            judge_agent=JudgeAgent("judge", llm, skills={"web_search": search_skill}),
            results_path=self.results_path,
            hooks=self.hooks,
            llm_client=llm,
        )

    def _build_logger(self, settings: Any) -> FifoLogger:
        log_cfg = settings.setup.logging
        writer = RotatingWriter(Path(log_cfg.fifo_path).parent, log_cfg.max_files, log_cfg.max_lines_per_file)
        self._log_consumer = LogConsumer(log_cfg.fifo_path, writer)
        self._log_consumer.start()
        return FifoLogger(log_cfg.fifo_path)


__all__ = ["DebateSimulatorSDK"]
