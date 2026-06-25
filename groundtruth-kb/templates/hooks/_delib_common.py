#!/usr/bin/env python3
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shared helper module for Deliberation Archive (DA) governance hooks.

Provides DB resolution, source-ref normalization, and DA insertion for
hooks that need to write to the Deliberation Archive (owner-decision-capture,
gov09-capture, and future DA governance hooks).

This module is NOT a hook itself — it is a helper imported by hooks in
this directory.
"""

from __future__ import annotations

import hashlib
import os
import sys
from datetime import UTC, datetime
from pathlib import Path


def find_groundtruth_db() -> Path | None:
    """Locate the canonical groundtruth.db starting from the project root."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if project_dir:
        candidate = Path(project_dir) / "groundtruth.db"
        if candidate.exists():
            return candidate
    for candidate_dir in [Path.cwd(), Path(__file__).resolve().parents[2]]:
        candidate = candidate_dir / "groundtruth.db"
        if candidate.exists():
            return candidate
    return None


def normalize_source_ref(ref: str) -> str:
    """Normalize a source reference for consistent DA lookups."""
    return ref.strip().replace("\\", "/")


def compute_content_hash(content: str) -> str:
    """SHA-256 hex digest of content for dedup."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def insert_deliberation(
    *,
    source_type: str,
    content: str,
    source_ref: str = "",
    outcome: str = "",
    session_id: str = "",
    spec_ids: str = "",
) -> bool:
    """Insert a deliberation record into the DA table.

    Returns True on success, False on any error (fail-open: hooks should
    not block agent work if DA insertion fails).
    """
    db_path = find_groundtruth_db()
    if db_path is None:
        return False
    try:
        sys.path.insert(0, str(db_path.parent / "groundtruth-kb" / "src"))
        from groundtruth_kb.db import KnowledgeDB

        db = KnowledgeDB(str(db_path))
        db.insert_deliberation(
            source_type=source_type,
            content=content,
            source_ref=normalize_source_ref(source_ref),
            outcome=outcome,
            session_id=session_id,
            spec_ids=spec_ids,
            content_hash=compute_content_hash(content),
            changed_by=f"hook/{Path(sys._getframe(1).f_code.co_filename).stem}",
        )
        return True
    except Exception:
        return False
