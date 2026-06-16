# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shared context key derivation for governance hooks.

Both delib-search-gate.py (UserPromptSubmit) and delib-search-tracker.py
(PostToolUse) must compute identical keys for the same governance context.
The key is derived from the active bridge document names, not from
event-specific payload fields that differ between hook events.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

_BRIDGE_FILE_STATUS = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|DEFERRED|WITHDRAWN)\b",
    re.IGNORECASE,
)


def _status_from_bridge_file(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = _BRIDGE_FILE_STATUS.match(stripped)
        return match.group(1).upper() if match else None
    return None


def _read_active_bridge_docs_from_files(bridge_dir: Path) -> list[str]:
    latest: dict[str, tuple[int, str]] = {}
    for path in bridge_dir.glob("*.md"):
        match = re.match(r"^(.+)-(\d+)\.md$", path.name)
        if not match:
            continue
        slug = match.group(1)
        version = int(match.group(2))
        status = _status_from_bridge_file(path)
        if status is None:
            continue
        if slug not in latest or version > latest[slug][0]:
            latest[slug] = (version, status)
    return sorted(
        slug for slug, (_version, status) in latest.items() if status in ("NEW", "REVISED", "NO-GO", "ADVISORY")
    )


def _read_active_bridge_docs(cwd: str) -> list[str]:
    """Extract active (non-terminal) bridge document names from bridge state.

    Active means the latest status for a document is NEW, REVISED, NO-GO, or ADVISORY
    (i.e., not yet GO or VERIFIED — work is still in flight).
    """
    bridge_dir = Path(cwd) / "bridge"
    return _read_active_bridge_docs_from_files(bridge_dir)


def compute_context_key(cwd: str) -> str:
    """Compute a governance context key from the active bridge documents.

    Returns a 16-char hex digest. Both the gate and tracker use this function
    so their keys always match for the same bridge state.

    When no active bridge documents exist, falls back to a cwd-only key
    so the gate/tracker cycle still works for projects without an active
    bridge thread.
    """
    active_docs = _read_active_bridge_docs(cwd)
    if active_docs:
        raw = (cwd + ":" + ",".join(active_docs)).encode("utf-8")
    else:
        raw = (cwd + ":_no_active_docs").encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]
