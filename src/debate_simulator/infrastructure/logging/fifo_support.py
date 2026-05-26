import errno
import hashlib
import os
import stat
from pathlib import Path

_UNSUPPORTED_FIFO_ERRNOS = {
    errno.EINVAL,
    errno.EPERM,
    errno.EROFS,
    getattr(errno, "ENOTSUP", 95),
    getattr(errno, "EOPNOTSUPP", 95),
}


def ensure_fifo_path(path: str | Path) -> Path:
    """Create a FIFO, falling back to /tmp when the configured filesystem rejects it."""
    requested = Path(path)
    if _is_fifo(requested):
        return requested
    if requested.exists():
        return _fallback_fifo(requested)
    requested.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.mkfifo(requested)
        return requested
    except OSError as error:
        if error.errno not in _UNSUPPORTED_FIFO_ERRNOS:
            raise
        return _fallback_fifo(requested)


def _fallback_fifo(requested: Path) -> Path:
    digest = hashlib.sha1(str(requested.resolve()).encode()).hexdigest()[:12]
    fallback = Path(os.getenv("TMPDIR", "/tmp")) / "debate_simulator" / f"{digest}_{requested.name}"
    fallback.parent.mkdir(parents=True, exist_ok=True)
    if fallback.exists() and not _is_fifo(fallback):
        fallback.unlink()
    if not fallback.exists():
        os.mkfifo(fallback)
    return fallback


def _is_fifo(path: Path) -> bool:
    return path.exists() and stat.S_ISFIFO(path.stat().st_mode)


__all__ = ["ensure_fifo_path"]
