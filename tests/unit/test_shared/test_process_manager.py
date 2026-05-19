import time
from pathlib import Path

from debate_simulator.models.agent import AgentResponse
from debate_simulator.shared.constants import PenaltyType
from debate_simulator.shared.process_manager import JsonFifo, ProcessManager


def test_process_manager_kills_timed_out_agent() -> None:
    """Timeout kills the child process and returns a penalized fallback."""
    manager = ProcessManager(timeout_seconds=0.1, keepalive_interval_seconds=0.01)

    response = manager.run_with_timeout(_sleeping_worker, agent="con")

    assert response.penalties[0].type == PenaltyType.EXCEED_TIME


def test_process_manager_returns_child_response() -> None:
    """Successful child execution returns the child AgentResponse."""
    manager = ProcessManager(timeout_seconds=1.0, keepalive_interval_seconds=0.01)

    response = manager.run_with_timeout(_response_worker, agent="pro")

    assert response.text == "ok"


def test_watchdog_detects_stopped_process() -> None:
    """Watchdog liveness check reports stopped processes."""
    manager = ProcessManager(timeout_seconds=1.0, keepalive_interval_seconds=0.01)
    process = manager.spawn_agent(_response_worker)
    process.join(timeout=1)

    alive = manager.watchdog_ping(process)

    assert alive is False


def test_json_fifo_round_trip(tmp_path: Path) -> None:
    """JSON FIFO transports structured payloads."""
    fifo = JsonFifo(tmp_path / "agent_fifo")
    payload = {"agent": "con", "text": "hello"}

    fifo.write(payload)
    received = fifo.read()

    assert received == payload


def _sleeping_worker() -> AgentResponse:
    time.sleep(1)
    return AgentResponse.from_text("late", time_seconds=1)


def _response_worker() -> AgentResponse:
    return AgentResponse.from_text("ok", time_seconds=0.01)
