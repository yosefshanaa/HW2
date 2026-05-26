import os
import stat
import threading
import time
from pathlib import Path

from debate_simulator.infrastructure.logging.fifo_logger import FifoLogger
from debate_simulator.infrastructure.logging.fifo_support import ensure_fifo_path
from debate_simulator.infrastructure.logging.log_consumer import LogConsumer
from debate_simulator.infrastructure.logging.rotating_writer import RotatingWriter


def test_rotating_writer_enforces_configured_line_limit(tmp_path: Path) -> None:
    """Rotating writer keeps each file within the configured line cap."""
    writer = RotatingWriter(tmp_path, max_files=20, max_lines_per_file=500)

    for line_number in range(10_001):
        writer.write(f"entry {line_number}")

    files = sorted(tmp_path.glob("log_*.log"))
    line_counts = [len(path.read_text(encoding="utf-8").splitlines()) for path in files]

    assert len(files) == 20
    assert max(line_counts) <= 500


def test_rotating_writer_circularly_overwrites_oldest_file(tmp_path: Path) -> None:
    """Rotation wraps to the first file and overwrites earlier content."""
    writer = RotatingWriter(tmp_path, max_files=2, max_lines_per_file=2)

    for entry in ["one", "two", "three", "four", "five"]:
        writer.write(entry)

    first_file = tmp_path / "log_001.log"

    assert first_file.read_text(encoding="utf-8").splitlines() == ["five"]


def test_fifo_logger_creates_pipe_and_writes_non_blocking(tmp_path: Path) -> None:
    """FIFO logger creates a named pipe and sends messages without blocking."""
    fifo_path = tmp_path / "debate_fifo"
    received: list[str] = []

    logger = FifoLogger(fifo_path)
    reader = threading.Thread(target=_read_one_fifo_line, args=(fifo_path, received))
    reader.start()
    time.sleep(0.05)

    logger.log("INFO", "TEST", "hello")
    reader.join(timeout=1)

    assert stat_is_fifo(fifo_path) and received == ["INFO|TEST|hello"]


def test_log_consumer_formats_and_dispatches_messages(tmp_path: Path) -> None:
    """Log consumer reads FIFO messages and writes formatted entries."""
    fifo_path = tmp_path / "debate_fifo"
    writer = RotatingWriter(tmp_path / "logs", max_files=2, max_lines_per_file=10)
    consumer = LogConsumer(fifo_path=fifo_path, writer=writer)
    logger = FifoLogger(fifo_path)

    consumer.start()
    time.sleep(0.1)
    logger.log("WARNING", "JUDGE", "watching")
    _wait_for_line_count(tmp_path / "logs" / "log_001.log", expected=1)
    consumer.stop()

    line = (tmp_path / "logs" / "log_001.log").read_text(encoding="utf-8").strip()

    assert "[WARNING] [JUDGE] watching" in line


def test_logging_pipeline_preserves_concurrent_messages(tmp_path: Path) -> None:
    """Concurrent loggers preserve every message through the FIFO pipeline."""
    fifo_path = tmp_path / "debate_fifo"
    writer = RotatingWriter(tmp_path / "logs", max_files=20, max_lines_per_file=500)
    consumer = LogConsumer(fifo_path=fifo_path, writer=writer)
    consumer.start()

    threads = [
        threading.Thread(target=_write_many, args=(fifo_path, agent, 50))
        for agent in ["CON", "PRO", "JUDGE", "SDK"]
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    _wait_for_total_lines(tmp_path / "logs", expected=200)
    consumer.stop()

    assert _total_lines(tmp_path / "logs") == 200


def test_fifo_path_falls_back_when_configured_filesystem_rejects_pipe(
    monkeypatch, tmp_path: Path
) -> None:
    """Unsupported project filesystems use a real FIFO in /tmp instead of crashing."""
    monkeypatch.setenv("TMPDIR", str(tmp_path / "tmp"))

    def fake_mkfifo(path: str | Path) -> None:
        target = Path(path)
        if target.parent == tmp_path:
            raise OSError(95, "Operation not supported")
        original_mkfifo(path)

    original_mkfifo = os.mkfifo
    monkeypatch.setattr(os, "mkfifo", fake_mkfifo)

    fifo = ensure_fifo_path(tmp_path / "debate_fifo")

    assert fifo.parent != tmp_path and stat.S_ISFIFO(fifo.stat().st_mode)


def _read_one_fifo_line(fifo_path: Path, received: list[str]) -> None:
    with fifo_path.open(encoding="utf-8") as pipe:
        received.append(pipe.readline().strip())


def _write_many(fifo_path: Path, agent: str, count: int) -> None:
    logger = FifoLogger(fifo_path)
    for index in range(count):
        logger.log("INFO", agent, f"message-{index}")


def _wait_for_line_count(path: Path, expected: int) -> None:
    for _ in range(100):
        if path.exists() and len(path.read_text(encoding="utf-8").splitlines()) >= expected:
            return
        time.sleep(0.02)


def _wait_for_total_lines(directory: Path, expected: int) -> None:
    for _ in range(200):
        if _total_lines(directory) >= expected:
            return
        time.sleep(0.02)


def _total_lines(directory: Path) -> int:
    return sum(
        len(path.read_text(encoding="utf-8").splitlines()) for path in directory.glob("*.log")
    )


def stat_is_fifo(path: Path) -> bool:
    """Return whether a path is a FIFO."""
    return os.stat(path).st_mode & 0o170000 == 0o010000
