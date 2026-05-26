import json

import pytest

from debate_simulator.agents.judge_prompts import (
    build_final_prompt,
    build_round_prompt,
    parse_json_response,
    score_from_data,
)


def test_score_from_data_valid_dict() -> None:
    score = score_from_data({"total": 85.0, "breakdown": {"content": 85.0}})
    assert score.total == 85.0


def test_score_from_data_clamps_above_100() -> None:
    score = score_from_data({"total": 150.0, "breakdown": {}})
    assert score.total == 100.0


def test_score_from_data_clamps_below_0() -> None:
    score = score_from_data({"total": -10.0, "breakdown": {}})
    assert score.total == 0.0


def test_score_from_data_non_dict() -> None:
    score = score_from_data("not a dict")
    assert score.total == 0.0


def test_build_round_prompt_includes_arguments() -> None:
    prompt = build_round_prompt("template", 1, "pro arg", "con arg")
    assert "pro arg" in prompt and "con arg" in prompt


def test_build_round_prompt_alternates_order() -> None:
    odd = build_round_prompt("t", 1, "pro", "con")
    even = build_round_prompt("t", 2, "pro", "con")
    assert odd.index("Pro speech") < odd.index("Con speech")
    assert even.index("Con speech") < even.index("Pro speech")


def test_build_round_prompt_includes_history() -> None:
    prompt = build_round_prompt("t", 1, "p", "c", ["Round 1 history"])
    assert "Round 1 history" in prompt


def test_build_final_prompt_includes_transcript() -> None:
    prompt = build_final_prompt("template", ["round1", "round2"])
    assert "round1" in prompt and "round2" in prompt


def test_parse_json_response_valid() -> None:
    result = parse_json_response('{"key": "value"}')
    assert result == {"key": "value"}


def test_parse_json_response_with_markdown_fence() -> None:
    result = parse_json_response('```json\n{"key": "value"}\n```')
    assert result == {"key": "value"}


def test_parse_json_response_embedded_in_text() -> None:
    raw = 'Here is my analysis:\n{"notes": "good"}\nDone.'
    result = parse_json_response(raw)
    assert result == {"notes": "good"}


def test_parse_json_response_non_dict_raises() -> None:
    with pytest.raises(ValueError):
        parse_json_response("[1, 2, 3]")


def test_parse_json_response_invalid_json_raises() -> None:
    with pytest.raises(json.JSONDecodeError):
        parse_json_response("not json")
