"""Shared I/O helpers for the wrap scanner suite.

Extracted from `session_self_initialization.py` (S309 GTKB-STARTUP-ENHANCEMENTS
Phase 1 helper) so multiple scanners can share the atomic-write contract
without re-implementing it. See bridge/gtkb-wrapup-enhancements-slice1-006.md
(GO) and bridge/gtkb-wrapup-enhancements-slice1-005.md (REVISED-2 binding).
"""

from __future__ import annotations

import os
from pathlib import Path


def _atomic_write_text(path: Path, content: str) -> None:
    """Write text to ``path`` atomically via write-to-.tmp + os.replace.

    Why-atomic: prevents partial writes from corrupting downstream consumers
    (Grafana dashboard reading dashboard-data.json, Claude Code reading
    session-startup-report.md as additionalContext, scanners reading their
    own output) when a process crashes or the system loses power mid-write.

    On Windows, ``os.replace`` is atomic for same-filesystem moves since
    Python 3.3; cross-filesystem moves degrade to copy-then-delete which
    is not atomic. Callers should ensure ``path`` and its ``.tmp`` sibling
    live on the same filesystem (the default under a single ``Path`` parent).
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
