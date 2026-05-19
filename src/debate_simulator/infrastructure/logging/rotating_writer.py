from pathlib import Path
from threading import Lock


class RotatingWriter:
    """Thread-safe circular writer for fixed-size log files."""

    def __init__(self, directory: str | Path, max_files: int, max_lines_per_file: int) -> None:
        """Create a rotating writer with configured file and line limits."""
        self.directory = Path(directory)
        self.max_files = max_files
        self.max_lines_per_file = max_lines_per_file
        self._lock = Lock()
        self._current_index = 0
        self._current_line_count = 0
        self.directory.mkdir(parents=True, exist_ok=True)
        self._initialize_files()

    def write(self, entry: str) -> None:
        """Write one log entry, rotating when the active file is full."""
        with self._lock:
            if self._current_line_count >= self.max_lines_per_file:
                self._rotate()
            with self._active_path().open("a", encoding="utf-8") as log_file:
                log_file.write(f"{entry.rstrip()}\n")
            self._current_line_count += 1

    def _initialize_files(self) -> None:
        for index in range(self.max_files):
            self._path_for(index).touch(exist_ok=True)

    def _rotate(self) -> None:
        self._current_index = (self._current_index + 1) % self.max_files
        self._active_path().write_text("", encoding="utf-8")
        self._current_line_count = 0

    def _active_path(self) -> Path:
        return self._path_for(self._current_index)

    def _path_for(self, index: int) -> Path:
        return self.directory / f"log_{index + 1:03d}.log"


__all__ = ["RotatingWriter"]
