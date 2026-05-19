from debate_simulator.skills.base_skill import SkillResult


def test_skill_result_success_factory() -> None:
    """SkillResult.ok creates a successful result with data."""
    result = SkillResult.ok({"value": 1})

    assert result.success is True and result.data == {"value": 1}


def test_skill_result_failure_factory() -> None:
    """SkillResult.fail creates a failed result with an error message."""
    result = SkillResult.fail("bad")

    assert result.success is False and result.error == "bad"
