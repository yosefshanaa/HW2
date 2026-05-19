import importlib
import json

import pytest

from debate_simulator.shared.config import load_settings

PACKAGES = [
    "debate_simulator.agents",
    "debate_simulator.hooks",
    "debate_simulator.infrastructure",
    "debate_simulator.infrastructure.logging",
    "debate_simulator.infrastructure.rag",
    "debate_simulator.infrastructure.search",
    "debate_simulator.mixins",
    "debate_simulator.models",
    "debate_simulator.sdk",
    "debate_simulator.services",
    "debate_simulator.skills",
    "debate_simulator.skills.argument_builder",
    "debate_simulator.skills.fact_check",
    "debate_simulator.skills.rag_retrieve",
    "debate_simulator.skills.rag_store",
    "debate_simulator.skills.rebuttal_builder",
    "debate_simulator.skills.rebuttal_check",
    "debate_simulator.skills.respect_check",
    "debate_simulator.skills.stance_check",
    "debate_simulator.skills.web_search",
]


@pytest.mark.parametrize("package_name", PACKAGES)
def test_package_exports_version(package_name: str) -> None:
    """Every package initializer exports version metadata."""
    module = importlib.import_module(package_name)

    assert module.__version__ == "1.00"


def test_load_settings_rejects_non_object_json(tmp_path) -> None:
    """Configuration JSON must use an object at the top level."""
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text(json.dumps([]), encoding="utf-8")

    with pytest.raises(ValueError):
        load_settings(setup_path=invalid_path)
