"""Foundation existence test for the cross-harness parity program (WI-4875, F1).

Closes the Slice-1 GO finding F1: a committed test asserting the foundation
``ADR-CROSS-HARNESS-PARITY-001`` and ``DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001``
exist in MemBase with the required fields. Follows the established
live-DB-or-skip idiom (``platform_tests/scripts/test_check_obsolete_reference_purge.py``):
the canonical ``groundtruth.db`` is gitignored, so the test enforces wherever the
DB is present (dev + the Slice-6 release/CI gate) and skips on a DB-less checkout
rather than false-failing. Read-only; never mutates MemBase.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC = _PROJECT_ROOT / "groundtruth-kb" / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

ADR_ID = "ADR-CROSS-HARNESS-PARITY-001"
DCL_ID = "DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001"
ADR_REQUIRED_SECTIONS = (
    "## Decision",
    "## Context",
    "## Rejected alternatives",
    "## Consequences",
    "## Rationale",
)
DCL_ASSERTION_IDS = (
    "PARITY-DIFF-EXISTS",
    "PARITY-WAIVER-SCHEMA",
    "PARITY-DISPOSITION-GATE",
    "PARITY-APPLICABILITY-RULE",
    "PARITY-DIFF-WIRED",
)


def _live_db() -> KnowledgeDB:
    root_db = _PROJECT_ROOT / "groundtruth.db"
    if not root_db.is_file():
        pytest.skip("live MemBase not present")
    return KnowledgeDB(root_db)


def test_parity_adr_exists_with_required_fields() -> None:
    db = _live_db()
    try:
        adr = db.get_spec(ADR_ID)
        assert adr is not None, f"{ADR_ID} not found in MemBase"
        assert adr.get("type") == "architecture_decision"
        assert adr.get("status") == "accepted"
        body = adr.get("description") or ""
        for section in ADR_REQUIRED_SECTIONS:
            assert section in body, f"{ADR_ID} body missing required section {section!r}"
    finally:
        db.close()


def test_parity_dcl_exists_with_required_fields() -> None:
    db = _live_db()
    try:
        dcl = db.get_spec(DCL_ID)
        assert dcl is not None, f"{DCL_ID} not found in MemBase"
        assert dcl.get("type") == "design_constraint"
        assert dcl.get("status") == "specified"
        body = dcl.get("description") or ""
        for assertion_id in DCL_ASSERTION_IDS:
            assert assertion_id in body, f"{DCL_ID} body missing assertion id {assertion_id!r}"
    finally:
        db.close()


# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
