import errno
import os
from pathlib import Path

from debate_simulator.infrastructure.logging.fifo_support import ensure_fifo_path


class FifoLogger:
    """Non-blocking writer for FIFO-based log messages."""

    def __init__(self, fifo_path: str | Path) -> None:
        """Create the FIFO if needed."""
        self.fifo_path = ensure_fifo_path(fifo_path)

    def log(self, level: str, component: str, message: str) -> bool:
        """Write one raw log message to the FIFO without blocking."""
        payload = f"{level}|{component}|{message}\n".encode()
        try:
            descriptor = os.open(self.fifo_path, os.O_WRONLY | os.O_NONBLOCK)
        except OSError as error:
            if error.errno == errno.ENXIO:
                return False
            raise
        with os.fdopen(descriptor, "wb", closefd=True) as pipe:
            pipe.write(payload)
        return True


__all__ = ["FifoLogger"]
