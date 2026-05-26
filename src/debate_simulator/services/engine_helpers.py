"""Shared helpers for safe agent turns, scoring, and graceful shutdown."""

from __future__ import annotations

import signal
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import DebateResult, Penalty
from debate_simulator.shared.constants import ConfigFile, FallbackText, PenaltyPoints, PenaltyType

_graceful_shutdown = False
_DEBATE_FALLBACKS = {
    "max_pings": 10,
    "agent_timeout_seconds": 60,
    "keepalive_interval_seconds": 10,
    "max_lines_per_response": 2,
    "max_words_per_response": 90,
}


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


_STATE_ATTRS = (
    "memory",
    "last_skill_results",
    "previous_arguments",
    "used_sources",
    "known_sources",
    "research_notes",
)


def safe_turn(
    agent: Any, context: TurnContext, agent_name: str, hooks: Any, process_manager: Any = None
) -> AgentResponse:
    """Run an agent turn, catching errors and applying timeout penalties."""
    try:
        if process_manager is None:
            response = agent.run_turn(context)
        else:
            result = process_manager.run_with_timeout(
                lambda: _run_turn_with_state(agent, context), agent_name
            )
            if isinstance(result, AgentResponse):
                response = result
            else:
                response, state = result
                _restore_agent_state(agent, state)
        for penalty in response.penalties:
            hooks.emit("on_penalty", agent=agent_name, penalty=penalty)
        return response
    except Exception as error:
        penalty = Penalty(
            type=PenaltyType.EXCEED_TIME,
            points=PenaltyPoints.EXCEED_TIME.value,
            reason=str(error),
            agent=agent_name,
        )
        hooks.emit("on_penalty", agent=agent_name, penalty=penalty)
        return AgentResponse.from_text(FallbackText.AGENT_CRASH.value, 0.0, [penalty])


def father_relay(speaker: str, text: str) -> str:
    """Wrap a child message as a Father-mediated relay."""
    return f"Father relay from {speaker}: {text}"


def load_debate_defaults() -> dict[str, Any]:
    """Read debate defaults from the versioned setup config."""
    import json

    try:
        data = json.loads(Path(ConfigFile.SETUP.value).read_text(encoding="utf-8")).get("debate", {})
        return {**_DEBATE_FALLBACKS, **data}
    except (FileNotFoundError, ValueError, KeyError):
        return _DEBATE_FALLBACKS.copy()


def _run_turn_with_state(agent: Any, context: TurnContext) -> tuple[AgentResponse, dict[str, Any]]:
    response = agent.run_turn(context)
    return response, _snapshot_agent_state(agent)


def _snapshot_agent_state(agent: Any) -> dict[str, Any]:
    return {attr: getattr(agent, attr) for attr in _STATE_ATTRS if hasattr(agent, attr)}


def _restore_agent_state(agent: Any, state: dict[str, Any]) -> None:
    for attr, value in state.items():
        setattr(agent, attr, value)


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
    topic: str, rounds: list[Any], scores: dict[str, Any], winner: str,
    config: dict[str, Any], token_usage: dict[str, float] | None = None,
) -> DebateResult:
    """Construct a DebateResult from already-penalized scores.

    Penalties are applied once in DebateEngine.run_final_scoring (before the winner
    is declared), so this constructor must not re-apply them.
    """
    return DebateResult(
        topic=topic, rounds=rounds, final_scores=scores, winner=winner,
        config=config, token_usage=token_usage or {},
    )


__all__ = ["apply_final_penalties", "build_result", "enable_graceful_shutdown", "export_result", "father_relay", "is_shutdown_requested", "load_debate_defaults", "safe_turn"]
