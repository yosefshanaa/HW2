from debate_simulator.shared.config import (
    DebateConfig,
    LlmConfig,
    LoggingConfig,
    RagConfig,
    RateLimitsConfig,
    SearchConfig,
    ServiceRateLimit,
    Settings,
    SetupConfig,
)


def validate_config(config: Settings) -> list[str]:
    """Return a list of validation warnings for the loaded configuration."""
    warnings: list[str] = []
    if config.setup.version != "1.00":
        warnings.append(f"Unexpected version: {config.setup.version}")
    if config.setup.llm.temperature < 0.0 or config.setup.llm.temperature > 2.0:
        warnings.append(f"Temperature out of range: {config.setup.llm.temperature}")
    if config.setup.debate.max_pings < 1:
        warnings.append("max_pings must be at least 1")
    if config.setup.rag.chunk_overlap >= config.setup.rag.chunk_size:
        warnings.append("chunk_overlap must be less than chunk_size")
    return warnings


__all__ = [
    "DebateConfig",
    "LlmConfig",
    "LoggingConfig",
    "RagConfig",
    "RateLimitsConfig",
    "SearchConfig",
    "ServiceRateLimit",
    "Settings",
    "SetupConfig",
    "validate_config",
]
