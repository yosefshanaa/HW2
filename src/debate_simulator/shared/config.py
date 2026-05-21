import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from debate_simulator.shared.constants import ConfigFile, EnvPlaceholder


class LlmConfig(BaseModel):
    """LLM provider settings loaded from setup configuration."""

    model: str
    temperature: float
    max_tokens: int
    api_key_env: str
    base_url_env: str | None = None


class DebateConfig(BaseModel):
    """Debate timing and turn-limit settings."""

    max_pings: int
    agent_timeout_seconds: int
    keepalive_interval_seconds: int
    max_lines_per_response: int
    max_words_per_response: int = 90
    max_tokens_per_response: int
    research_timeout_seconds: int


class SearchConfig(BaseModel):
    """Search provider settings."""

    engine: str
    max_results_per_query: int
    max_research_queries: int


class RagConfig(BaseModel):
    """RAG storage and retrieval settings."""

    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    top_k_retrieval: int
    persist_directory: str


class LoggingConfig(BaseModel):
    """FIFO logging settings."""

    fifo_path: str
    max_files: int
    max_lines_per_file: int
    log_level: str


class SetupConfig(BaseModel):
    """Main application configuration."""

    version: str
    llm: LlmConfig
    debate: DebateConfig
    search: SearchConfig
    rag: RagConfig
    logging: LoggingConfig
    penalties: dict[str, int]
    scoring: dict[str, dict[str, float]]


class ServiceRateLimit(BaseModel):
    """Rate limit settings for one external service."""

    requests_per_minute: int
    requests_per_hour: int
    concurrent_max: int
    retry_after_seconds: int
    max_retries: int


class RateLimitsConfig(BaseModel):
    """External service rate limit configuration."""

    version: str
    rate_limits: dict[str, ServiceRateLimit] = Field(default_factory=dict)


class Settings(BaseModel):
    """Validated runtime settings with environment-derived secrets."""

    setup: SetupConfig
    rate_limits: RateLimitsConfig
    openai_api_key: str | None
    openai_base_url: str | None = None

    def require_openai_api_key(self) -> str:
        """Return the OpenAI API key or raise a clear startup error."""
        if not self.openai_api_key or self.openai_api_key == EnvPlaceholder.OPENAI_API_KEY.value:
            raise RuntimeError("OPENAI_API_KEY is required")
        return self.openai_api_key


def load_settings(
    setup_path: str | Path = ConfigFile.SETUP.value,
    rate_limits_path: str | Path = ConfigFile.RATE_LIMITS.value,
    env_path: str | Path | None = None,
) -> Settings:
    """Load JSON configuration and environment variables."""
    load_dotenv(dotenv_path=env_path)
    setup = SetupConfig.model_validate(_read_json(Path(setup_path)))
    limits = RateLimitsConfig.model_validate(_read_json(Path(rate_limits_path)))
    return Settings(
        setup=setup,
        rate_limits=limits,
        openai_api_key=os.getenv(setup.llm.api_key_env),
        openai_base_url=os.getenv(setup.llm.base_url_env) if setup.llm.base_url_env else None,
    )


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as config_file:
        data = json.load(config_file)
    if not isinstance(data, dict):
        raise ValueError(path)
    return data


__all__ = ["Settings", "load_settings"]
