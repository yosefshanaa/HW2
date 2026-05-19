import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from debate_simulator.infrastructure.logging.rotating_writer import RotatingWriter


class LogConsumer:
    """Background FIFO consumer that formats entries for rotating storage."""

    def __init__(self, fifo_path: str | Path, writer: RotatingWriter) -> None:
        """Create a consumer for a FIFO path and rotating writer."""
        self.fifo_path = Path(fifo_path)
        self.writer = writer
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.fifo_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.fifo_path.exists():
            os.mkfifo(self.fifo_path)

    def start(self) -> None:
        """Start consuming log messages in a background thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._consume, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the background consumer."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)

    def _consume(self) -> None:
        descriptor = os.open(self.fifo_path, os.O_RDONLY | os.O_NONBLOCK)
        with os.fdopen(descriptor, encoding="utf-8") as pipe:
            while not self._stop_event.is_set():
                line = pipe.readline()
                if not line:
                    time.sleep(0.01)
                    continue
                self.writer.write(self._format(line.strip()))

    def _format(self, raw_line: str) -> str:
        level, component, message = self._split_raw_line(raw_line)
        timestamp = datetime.now(timezone.utc).isoformat()
        return f"[{timestamp}] [{level}] [{component}] {message}"

    def _split_raw_line(self, raw_line: str) -> tuple[str, str, str]:
        parts = raw_line.split("|", maxsplit=2)
        if len(parts) == 3:
            return parts[0], parts[1], parts[2]
        return "INFO", "SYSTEM", raw_line


__all__ = ["LogConsumer"]
