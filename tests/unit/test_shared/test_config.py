from pathlib import Path

import pytest

from debate_simulator.shared.config import load_settings


def test_load_settings_reads_config_and_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings include JSON config values and the OpenAI key from the environment."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    settings = load_settings(
        setup_path=Path("config/setup.json"),
        rate_limits_path=Path("config/rate_limits.json"),
    )

    assert settings.setup.version == "1.00"
    assert settings.openai_api_key == "test-key"
    assert settings.setup.llm.model == "gpt-4o-mini"
    assert settings.rate_limits.rate_limits["openai"].requests_per_minute == 30


def test_load_settings_rejects_missing_config() -> None:
    """Missing configuration files raise a clear file error."""
    with pytest.raises(FileNotFoundError):
        load_settings(setup_path=Path("missing.json"))


def test_settings_require_openai_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing OpenAI API key raises a clear startup error."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    settings = load_settings()

    with pytest.raises(RuntimeError):
        settings.require_openai_api_key()
