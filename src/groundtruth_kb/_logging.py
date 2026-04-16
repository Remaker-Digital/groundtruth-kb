"""Internal logging configuration for groundtruth-kb.

Two entry paths:

- ``configure_cli_logging()`` — called by ``gt`` CLI (stderr handler,
  default WARNING).
- ``_setup_bridge_logging()`` — called by bridge direct entry points
  (FileHandler to the existing per-agent log file, default INFO).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
"""

from __future__ import annotations

import contextlib
import logging
import os
import sys
from pathlib import Path

_LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"
_LOG_DATEFMT = "%Y-%m-%dT%H:%M:%S"
_PACKAGE_LOGGER = "groundtruth_kb"


def _resolve_level(default: str = "WARNING") -> int:
    """Read GROUNDTRUTH_LOG_LEVEL env var; fall back to *default*.

    Args:
        default: Level name when the env var is unset. CLI passes
            ``"WARNING"``; bridge entry points pass ``"INFO"``.
    """
    name = os.environ.get("GROUNDTRUTH_LOG_LEVEL", default).upper()
    return getattr(logging, name, logging.WARNING)


def configure_cli_logging() -> None:
    """Configure stderr logging for the ``gt`` CLI entry point.

    Default level is WARNING — interactive users see diagnostics via
    explicit ``gt`` output and don't need INFO-level noise on stderr.
    """
    logging.basicConfig(
        level=_resolve_level("WARNING"),
        format=_LOG_FORMAT,
        datefmt=_LOG_DATEFMT,
    )


def _setup_bridge_logging(log_path: Path) -> None:
    """Configure file-based logging for a bridge direct entry point.

    Attaches a FileHandler to the ``groundtruth_kb`` package logger,
    writing to *log_path* (the same file previously written by
    ``_append_log()``).  Creates parent directories if needed.

    Default level is INFO — matching the current unconditional
    ``_append_log()`` behavior where every scan, dispatch, and exit
    event is written to the log file.  ``GROUNDTRUTH_LOG_LEVEL``
    overrides this for operators who want quieter or more verbose
    bridge logs.

    **Startup-safe:** If the log path cannot be created or opened
    (permissions, path collision, read-only filesystem), falls back to
    a NullHandler so the bridge process can still start.  A best-effort
    warning is attempted on stderr, but if stderr is unavailable (e.g.
    ``pythonw.exe``, ``Start-Process -WindowStyle Hidden``), the
    warning is silently skipped.  The bridge process starts either way.

    **Idempotent:** Clears existing handlers on the package logger
    before attaching, so repeated calls (e.g. in tests) do not leak
    file descriptors or duplicate log records.

    Args:
        log_path: Absolute path to the agent-specific log file.
    """
    pkg_logger = logging.getLogger(_PACKAGE_LOGGER)
    pkg_logger.setLevel(_resolve_level("INFO"))

    # Idempotent: remove prior handlers to prevent leaks on repeated calls
    for h in pkg_logger.handlers[:]:
        pkg_logger.removeHandler(h)
        h.close()

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handler: logging.Handler = logging.FileHandler(log_path, encoding="utf-8")
    except OSError as exc:
        # Log path is unwritable — fall back to NullHandler so the
        # bridge process can still start.
        handler = logging.NullHandler()
        # Best-effort diagnostic warning. If stderr is unavailable
        # (None, closed, broken pipe), silently skip — the bridge
        # process starts with NullHandler regardless.
        with contextlib.suppress(Exception):
            sys.stderr.write(
                f"WARNING: bridge logging setup failed for {log_path}: {exc}; falling back to NullHandler\n"
            )

    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATEFMT))
    pkg_logger.addHandler(handler)
