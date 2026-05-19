import json
import multiprocessing as mp
import os
import time
from collections.abc import Callable
from multiprocessing import Process
from pathlib import Path
from typing import Any

from debate_simulator.models.agent import AgentResponse
from debate_simulator.models.debate import Penalty
from debate_simulator.shared.constants import FallbackText, FifoDefault, PenaltyPoints, PenaltyType


class ProcessManager:
    """Manage agent subprocesses, timeouts, watchdog pings, and penalties."""

    def __init__(self, timeout_seconds: float, keepalive_interval_seconds: float) -> None:
        """Create a process manager."""
        self.timeout_seconds = timeout_seconds
        self.keepalive_interval_seconds = keepalive_interval_seconds
        self.penalties: dict[str, list[Penalty]] = {}
        self._context = _process_context()

    def spawn_agent(self, target: Callable[..., Any], *args: Any) -> Process:
        """Spawn an agent process."""
        process = self._context.Process(target=_discarding_runner, args=(target, args))
        process.start()
        return process

    def run_with_timeout(self, target: Callable[..., AgentResponse], agent: str) -> AgentResponse:
        """Run an agent callable in a subprocess and enforce timeout."""
        output = self._context.Queue()
        process = self._context.Process(target=_queue_runner, args=(target, output))
        started = time.perf_counter()
        process.start()
        process.join(timeout=self.timeout_seconds)
        if process.is_alive():
            process.kill()
            process.join()
            return self._timeout_response(agent, time.perf_counter() - started)
        result = output.get()
        if isinstance(result, Exception):
            raise result
        return result

    def watchdog_ping(self, process: Process) -> bool:
        """Return whether a managed process is alive."""
        return process.is_alive()

    def _timeout_response(self, agent: str, elapsed: float) -> AgentResponse:
        penalty = Penalty(
            type=PenaltyType.EXCEED_TIME,
            points=PenaltyPoints.EXCEED_TIME.value,
            reason=FallbackText.AGENT_TIMEOUT.value,
            agent=agent,
        )
        self.penalties.setdefault(agent, []).append(penalty)
        return AgentResponse.from_text(FallbackText.AGENT_TIMEOUT.value, elapsed, [penalty])


class JsonFifo:
    """JSONL transport over a FIFO named pipe."""

    def __init__(self, path: str | Path) -> None:
        """Create a JSON FIFO helper."""
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            os.mkfifo(self.path)
        self._descriptor = os.open(self.path, os.O_RDWR | os.O_NONBLOCK)

    def write(self, payload: dict[str, Any]) -> None:
        """Write one JSON payload to the FIFO."""
        os.write(self._descriptor, f"{json.dumps(payload)}\n".encode())

    def read(self, timeout_seconds: float = FifoDefault.READ_TIMEOUT_SECONDS.value) -> dict[str, Any]:
        """Read one JSON payload from the FIFO."""
        deadline = time.perf_counter() + timeout_seconds
        buffer = b""
        while time.perf_counter() < deadline:
            try:
                chunk = os.read(self._descriptor, 4096)
            except BlockingIOError:
                chunk = b""
            if chunk:
                buffer += chunk
                if b"\n" in buffer:
                    return json.loads(buffer.split(b"\n", maxsplit=1)[0].decode())
            time.sleep(0.01)
        raise TimeoutError(self.path)


def _queue_runner(target: Callable[..., AgentResponse], output: Any) -> None:
    try:
        output.put(target())
    except Exception as error:
        output.put(error)


def _discarding_runner(target: Callable[..., Any], args: tuple[Any, ...]) -> None:
    target(*args)


def _process_context() -> Any:
    try:
        return mp.get_context("fork")
    except ValueError:
        return mp.get_context()


__all__ = ["JsonFifo", "ProcessManager"]
