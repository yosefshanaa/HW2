from debate_simulator.shared.constants import (
    AgentRole,
    LogLevel,
    PenaltyType,
    ScoreDimension,
    SessionState,
    Stance,
)


def test_required_enum_values_are_stable() -> None:
    """Foundation enums expose the fixed vocabulary required by the project."""
    assert AgentRole.JUDGE.value == "judge"
    assert Stance.PRO.value == "pro"
    assert PenaltyType.EXCEED_TIME.value == "exceed_time"
    assert SessionState.FINISHED.value == "finished"
    assert ScoreDimension.COMPLIANCE.value == "compliance"
    assert LogLevel.INFO.value == "INFO"
