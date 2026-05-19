import time
from pathlib import Path

from debate_simulator.infrastructure.logging import FifoLogger, LogConsumer, RotatingWriter


def test_logging_pipeline_end_to_end(tmp_path: Path) -> None:
    """FIFO logger, consumer, and rotating writer work end to end."""
    fifo_path = tmp_path / "fifo"
    writer = RotatingWriter(tmp_path / "logs", max_files=20, max_lines_per_file=500)
    consumer = LogConsumer(fifo_path, writer)
    logger = FifoLogger(fifo_path)

    consumer.start()
    logger.log("INFO", "SDK", "integration")
    for _ in range(100):
        output = (tmp_path / "logs" / "log_001.log").read_text(encoding="utf-8")
        if "integration" in output:
            break
        time.sleep(0.01)
    consumer.stop()

    assert "integration" in output
