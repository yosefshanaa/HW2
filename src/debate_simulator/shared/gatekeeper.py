import time
from collections import defaultdict
from collections.abc import Callable
from queue import Queue
from threading import Lock
from typing import Any, TypeVar

from debate_simulator.shared.config import ServiceRateLimit
from debate_simulator.shared.constants import ServiceName, TimeWindowSeconds

ResultT = TypeVar("ResultT")
Logger = Callable[[str, str, str], Any]


class QueueFullError(RuntimeError):
    """Raised when the gatekeeper cannot accept more queued requests."""


class ApiGatekeeper:
    """Centralized rate limiter, FIFO queue, retry wrapper, and API call logger."""

    def __init__(
        self,
        rate_limits: dict[str, ServiceRateLimit],
        logger: Logger | None = None,
        queue_max_size: int | None = None,
        clock: Callable[[], float] = time.time,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        """Create a gatekeeper from service rate-limit settings."""
        self.rate_limits = rate_limits
        self.logger = logger
        self.queue_max_size = queue_max_size
        self.clock = clock
        self.sleeper = sleeper
        self._lock = Lock()
        self._minute_requests: dict[str, list[float]] = defaultdict(list)
        self._hour_requests: dict[str, list[float]] = defaultdict(list)
        self._active: dict[str, int] = defaultdict(int)
        self._queues: dict[str, Queue[object]] = defaultdict(self._new_queue)

    def execute(self, service: str, api_call: Callable[..., ResultT], *args: Any, **kwargs: Any) -> ResultT:
        """Execute an API call when limits allow, retrying transient failures."""
        limit = self._limit_for(service)
        token = self._wait_for_turn(service, limit)
        try:
            result = self._execute_with_retry(limit, api_call, *args, **kwargs)
            self._log("INFO", f"{service} call completed")
            return result
        finally:
            self._finish(service, token)

    def get_queue_status(self, service: str) -> dict[str, int]:
        """Return pending and active request counts for a service."""
        limit = self._limit_for(service)
        queue = self._queues[service]
        return {
            "pending": queue.qsize(),
            "active": self._active[service],
            "requests_per_minute": limit.requests_per_minute,
            "requests_per_hour": limit.requests_per_hour,
            "concurrent_max": limit.concurrent_max,
        }

    def _wait_for_turn(self, service: str, limit: ServiceRateLimit) -> object | None:
        token: object | None = None
        while True:
            with self._lock:
                queue = self._queues[service]
                if self._can_start(service, limit) and self._is_next(queue, token):
                    self._start(service)
                    return token
                if token is None:
                    token = self._enqueue(queue, service)
            self.sleeper(limit.retry_after_seconds)

    def _execute_with_retry(
        self,
        limit: ServiceRateLimit,
        api_call: Callable[..., ResultT],
        *args: Any,
        **kwargs: Any,
    ) -> ResultT:
        attempts = 0
        while True:
            try:
                return api_call(*args, **kwargs)
            except Exception:
                attempts += 1
                if attempts > limit.max_retries:
                    self._log("ERROR", "api call failed")
                    raise
                self.sleeper(limit.retry_after_seconds * (2 ** (attempts - 1)))

    def _finish(self, service: str, token: object | None) -> None:
        with self._lock:
            self._active[service] -= 1
            if token is not None:
                self._queues[service].get_nowait()

    def _can_start(self, service: str, limit: ServiceRateLimit) -> bool:
        now = self.clock()
        self._prune(self._minute_requests[service], now, TimeWindowSeconds.MINUTE.value)
        self._prune(self._hour_requests[service], now, TimeWindowSeconds.HOUR.value)
        return (
            self._active[service] < limit.concurrent_max
            and len(self._minute_requests[service]) < limit.requests_per_minute
            and len(self._hour_requests[service]) < limit.requests_per_hour
        )

    def _start(self, service: str) -> None:
        now = self.clock()
        self._minute_requests[service].append(now)
        self._hour_requests[service].append(now)
        self._active[service] += 1

    def _enqueue(self, queue: Queue[object], service: str) -> object:
        if queue.full():
            raise QueueFullError(service)
        token = object()
        queue.put_nowait(token)
        return token

    def _is_next(self, queue: Queue[object], token: object | None) -> bool:
        if token is None:
            return queue.empty()
        with queue.mutex:
            return bool(queue.queue) and queue.queue[0] is token

    def _limit_for(self, service: str) -> ServiceRateLimit:
        return self.rate_limits.get(service) or self.rate_limits[ServiceName.DEFAULT.value]

    def _new_queue(self) -> Queue[object]:
        maxsize = self.queue_max_size
        if maxsize is None:
            maxsize = max(limit.requests_per_hour for limit in self.rate_limits.values())
        return Queue(maxsize=maxsize)

    def _prune(self, requests: list[float], now: float, window_seconds: int) -> None:
        requests[:] = [requested_at for requested_at in requests if now - requested_at < window_seconds]

    def _log(self, level: str, message: str) -> None:
        if self.logger:
            self.logger(level, "GATEKEEPER", message)


__all__ = ["ApiGatekeeper", "QueueFullError"]
