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


def _read_active_bridge_docs(cwd: str) -> list[str]:
    """Extract active (non-terminal) bridge document names from INDEX.md.

    Active means the latest status for a document is NEW, REVISED, or NO-GO
    (i.e., not yet GO or VERIFIED — work is still in flight).
    """
    index_path = Path(cwd) / "bridge" / "INDEX.md"
    if not index_path.exists():
        return []

    try:
        text = index_path.read_text(encoding="utf-8")
    except OSError:
        return []

    active: list[str] = []
    current_doc: str | None = None
    latest_status: str | None = None

    for line in text.splitlines():
        line = line.strip()
        doc_match = re.match(r"^Document:\s*(.+)$", line, re.IGNORECASE)
        if doc_match:
            # Save prior document if active
            if current_doc and latest_status in ("NEW", "REVISED", "NO-GO"):
                active.append(current_doc)
            current_doc = doc_match.group(1).strip()
            latest_status = None
            continue

        status_match = re.match(r"^(NEW|REVISED|GO|NO-GO|VERIFIED):", line, re.IGNORECASE)
        if status_match and latest_status is None:
            latest_status = status_match.group(1).upper()

    # Handle last document
    if current_doc and latest_status in ("NEW", "REVISED", "NO-GO"):
        active.append(current_doc)

    return sorted(active)


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
