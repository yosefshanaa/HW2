from typing import Any


class JudgeService:
    """Service wrapper for judge orchestration."""

    def __init__(self, judge_agent: Any) -> None:
        """Create a judge service."""
        self.judge_agent = judge_agent

    def observe_round(self, round_number: int, pro_argument: str, con_argument: str) -> Any:
        """Delegate round observation to the judge agent."""
        return self.judge_agent.observe_round(round_number, pro_argument, con_argument)

    def score(self, transcript: list[str]) -> Any:
        """Delegate final scoring to the judge agent."""
        return self.judge_agent.evaluate_debate(transcript)


__all__ = ["JudgeService"]
