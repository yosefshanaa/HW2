"""Shared helpers for safe agent turns, scoring, and graceful shutdown."""

from __future__ import annotations

import signal
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import DebateResult, Penalty
from debate_simulator.shared.constants import FallbackText, PenaltyPoints, PenaltyType

_graceful_shutdown = False


def enable_graceful_shutdown() -> None:
    """Register SIGINT handler for Ctrl+C graceful shutdown."""

    def _handle_sigint(signum: int, frame: Any) -> None:
        global _graceful_shutdown
        _graceful_shutdown = True
        print("\nGraceful shutdown requested. Finishing current round...", file=sys.stderr)

    signal.signal(signal.SIGINT, _handle_sigint)


def is_shutdown_requested() -> bool:
    """Return whether a graceful shutdown has been requested."""
    return _graceful_shutdown


def safe_turn(agent: Any, context: TurnContext, agent_name: str, hooks: Any) -> AgentResponse:
    """Run an agent turn, catching errors and applying timeout penalties."""
    try:
        return agent.run_turn(context)
    except Exception as error:
        penalty = Penalty(
            type=PenaltyType.EXCEED_TIME,
            points=PenaltyPoints.EXCEED_TIME.value,
            reason=str(error),
            agent=agent_name,
        )
        hooks.emit("on_penalty", agent=agent_name, penalty=penalty)
        return AgentResponse.from_text(FallbackText.AGENT_CRASH.value, 0.0, [penalty])


def export_result(result: DebateResult, results_path: str | Path) -> Path:
    """Export a debate result to JSON and return the file path."""
    path = Path(results_path)
    path.mkdir(parents=True, exist_ok=True)
    file_path = (
        path / f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{result.debate_id}.json"
    )
    file_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return file_path


def apply_final_penalties(rounds: list[Any], scores: dict[str, Any]) -> dict[str, Any]:
    """Attach round penalties to the appropriate score records."""
    for round_model in rounds:
        for penalty in round_model.penalties:
            score = scores.get(penalty.agent)
            if score is None:
                continue
            score.penalties_applied.append(penalty)
            score.penalty_total += penalty.points
    return scores


def build_result(
    topic: str, rounds: list[Any], scores: dict[str, Any], winner: str, config: dict[str, Any]
) -> DebateResult:
    """Construct a DebateResult from already-penalized scores.

    Penalties are applied once in DebateEngine.run_final_scoring (before the winner
    is declared), so this constructor must not re-apply them.
    """
    return DebateResult(
        topic=topic, rounds=rounds, final_scores=scores, winner=winner, config=config
    )


__all__ = [
    "apply_final_penalties",
    "build_result",
    "enable_graceful_shutdown",
    "export_result",
    "is_shutdown_requested",
    "safe_turn",
]
