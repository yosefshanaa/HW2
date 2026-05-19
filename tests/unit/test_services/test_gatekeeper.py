import threading

import pytest

from debate_simulator.shared.config import ServiceRateLimit
from debate_simulator.shared.gatekeeper import ApiGatekeeper, QueueFullError


class FakeClock:
    """Controllable clock and sleeper for gatekeeper tests."""

    def __init__(self) -> None:
        """Create the fake clock at zero."""
        self.now = 0.0
        self.sleeps: list[float] = []

    def time(self) -> float:
        """Return the current fake time."""
        return self.now

    def sleep(self, seconds: float) -> None:
        """Advance fake time instead of blocking."""
        self.sleeps.append(seconds)
        self.now += seconds


class BlockingClock(FakeClock):
    """Fake clock that holds queued requests until explicitly released."""

    def __init__(self) -> None:
        """Create a blocking clock."""
        super().__init__()
        self.release = threading.Event()

    def sleep(self, seconds: float) -> None:
        """Wait for release before advancing fake time."""
        self.sleeps.append(seconds)
        self.release.wait(timeout=1)
        self.now += seconds


def test_rate_limit_queues_requests_in_fifo_order() -> None:
    """Requests beyond the minute limit wait and execute in FIFO order."""
    clock = BlockingClock()
    gatekeeper = ApiGatekeeper(
        rate_limits={"test": _limit(requests_per_minute=1, retry_after_seconds=60)},
        clock=clock.time,
        sleeper=clock.sleep,
    )
    results: list[int] = [gatekeeper.execute("test", lambda: 1)]

    threads = [
        threading.Thread(
            target=lambda value=value: results.append(gatekeeper.execute("test", lambda: value))
        )
        for value in [2, 3]
    ]
    threads[0].start()
    _wait_for_pending(gatekeeper, "test", expected=1)
    threads[1].start()
    _wait_for_pending(gatekeeper, "test", expected=2)
    clock.release.set()
    for thread in threads:
        thread.join()

    assert results == [1, 2, 3]


def test_retry_uses_exponential_backoff() -> None:
    """Transient failures retry with exponential backoff until success."""
    clock = FakeClock()
    gatekeeper = ApiGatekeeper(
        rate_limits={"test": _limit(retry_after_seconds=2, max_retries=3)},
        clock=clock.time,
        sleeper=clock.sleep,
    )
    attempts = {"count": 0}

    def flaky_call() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise TimeoutError("temporary")
        return "ok"

    result = gatekeeper.execute("test", flaky_call)

    assert result == "ok" and clock.sleeps == [2, 4]


def test_backpressure_raises_when_queue_is_full() -> None:
    """Queue backpressure raises a clear exception instead of unbounded growth."""
    clock = FakeClock()
    gatekeeper = ApiGatekeeper(
        rate_limits={"test": _limit(requests_per_minute=0)},
        queue_max_size=1,
        clock=clock.time,
        sleeper=lambda seconds: None,
    )
    gatekeeper._queues["test"].put_nowait(object())

    with pytest.raises(QueueFullError):
        gatekeeper.execute("test", lambda: "never")


def test_api_calls_are_logged() -> None:
    """Every API call emits a gatekeeper log entry."""
    clock = FakeClock()
    messages: list[str] = []
    gatekeeper = ApiGatekeeper(
        rate_limits={"test": _limit()},
        logger=lambda level, component, message: messages.append(f"{level}:{component}:{message}"),
        clock=clock.time,
        sleeper=clock.sleep,
    )

    gatekeeper.execute("test", lambda: "ok")

    assert messages == ["INFO:GATEKEEPER:test call completed"]


def test_queue_status_reports_pending_requests() -> None:
    """Queue status exposes pending count and active service limits."""
    gatekeeper = ApiGatekeeper(rate_limits={"test": _limit()})

    status = gatekeeper.get_queue_status("test")

    assert status["pending"] == 0 and status["requests_per_minute"] == 30


def _limit(
    requests_per_minute: int = 30,
    retry_after_seconds: int = 1,
    max_retries: int = 1,
) -> ServiceRateLimit:
    return ServiceRateLimit(
        requests_per_minute=requests_per_minute,
        requests_per_hour=500,
        concurrent_max=2,
        retry_after_seconds=retry_after_seconds,
        max_retries=max_retries,
    )


def _wait_for_pending(gatekeeper: ApiGatekeeper, service: str, expected: int) -> None:
    for _ in range(100):
        if gatekeeper.get_queue_status(service)["pending"] == expected:
            return
        threading.Event().wait(0.01)
