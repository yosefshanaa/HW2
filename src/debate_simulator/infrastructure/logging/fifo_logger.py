import errno
import os
from pathlib import Path


class FifoLogger:
    """Non-blocking writer for FIFO-based log messages."""

    def __init__(self, fifo_path: str | Path) -> None:
        """Create the FIFO if needed."""
        self.fifo_path = Path(fifo_path)
        self.fifo_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.fifo_path.exists():
            os.mkfifo(self.fifo_path)

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
