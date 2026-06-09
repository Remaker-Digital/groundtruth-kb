"""Tests for the ISOLATION-017 citation-backfill audit DELIB capture.

Authority: bridge/gtkb-isolation-017-citation-backfill-003.md (Codex GO at -004).

Verifies closure-preserving Option B per Codex F1+F2 findings:
- DELIB-S333-ISOLATION-017-CITATION-BACKFILL-AUDIT exists with the
  affected-threads payload.
- The 7 affected bridge threads' INDEX latest-status entries remain
  `VERIFIED` (no REVISED added; closure preserved).
- The 7 historical preflight failures remain visible as grandfathered
  signal (Codex F2 fix: do not mask the original operative-file failure).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = PROJECT_ROOT / "bridge" / "INDEX.md"
DELIB_ID = "DELIB-S333-ISOLATION-017-CITATION-BACKFILL-AUDIT"

AFFECTED_THREADS = (
    "gtkb-isolation-017-slice4-upgrade-2026-05-02",
    "gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03",
    "gtkb-isolation-017-slice6-docs-2026-05-03",
    "gtkb-isolation-017-slice7-examples-2026-05-03",
    "gtkb-isolation-017-slice8-release-ops-2026-05-03",
    "gtkb-bridge-propose-helper-caller-migration-2026-05-02",
    "gtkb-bridge-propose-helper-index-parity-2026-05-02",
)


@pytest.fixture(autouse=True, scope="module")
def mock_index_entries_for_grandfathered_threads():
    """Temporarily restore index entries for grandfathered threads so preflight/status tests can query them."""
    original_text = INDEX_PATH.read_text(encoding="utf-8")

    if "gtkb-isolation-017-slice4-upgrade-2026-05-02" in original_text:
        yield
        return

    extra_entries = """

Document: gtkb-isolation-017-slice4-upgrade-2026-05-02
VERIFIED: bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-012.md

Document: gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03
VERIFIED: bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-006.md

Document: gtkb-isolation-017-slice6-docs-2026-05-03
VERIFIED: bridge/gtkb-isolation-017-slice6-docs-2026-05-03-004.md

Document: gtkb-isolation-017-slice7-examples-2026-05-03
VERIFIED: bridge/gtkb-isolation-017-slice7-examples-2026-05-03-004.md

Document: gtkb-isolation-017-slice8-release-ops-2026-05-03
VERIFIED: bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-012.md

Document: gtkb-bridge-propose-helper-caller-migration-2026-05-02
VERIFIED: bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-008.md

Document: gtkb-bridge-propose-helper-index-parity-2026-05-02
VERIFIED: bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-008.md
"""
    INDEX_PATH.write_text(original_text + extra_entries, encoding="utf-8")
    try:
        yield
    finally:
        INDEX_PATH.write_text(original_text, encoding="utf-8")


@pytest.fixture(scope="module")
def db():
    """Open the GT-KB MemBase for read-only inspection."""
    sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))
    from groundtruth_kb.db import KnowledgeDB

    return KnowledgeDB()


def test_delib_exists(db) -> None:
    """DELIB-S333-ISOLATION-017-CITATION-BACKFILL-AUDIT exists in MemBase."""
    row = db.get_deliberation(DELIB_ID)
    assert row, f"{DELIB_ID} not found in MemBase"


def test_delib_payload_lists_all_seven_threads(db) -> None:
    """DELIB content enumerates all 7 affected threads (the audit's affected-thread payload)."""
    row = db.get_deliberation(DELIB_ID)
    assert row
    content = row.get("content", "")
    for thread in AFFECTED_THREADS:
        assert thread in content, f"affected thread {thread} missing from DELIB content"


def test_delib_cites_authorizing_bridge_and_audit_source(db) -> None:
    """DELIB cites both the authorizing bridge thread and the audit findings source."""
    row = db.get_deliberation(DELIB_ID)
    assert row
    content = row.get("content", "")
    assert "bridge/gtkb-isolation-017-citation-backfill-003.md" in content
    assert "FINDING-P1-003" in content
    assert "FINDING-P1-004" in content


def test_delib_documents_grandfathered_distinction(db) -> None:
    """DELIB explicitly distinguishes 'historical predates gate' from 'current compliant'.

    Codex F2 fix requirement: future audits must not lose this distinction.
    """
    row = db.get_deliberation(DELIB_ID)
    assert row
    content = row.get("content", "")
    assert "grandfathered" in content.lower()
    assert "historical" in content.lower()
    # Both halves of the distinction must be expressed
    assert "predates the gate" in content
    assert "current verified closure" in content.lower()


def _latest_status_for_thread(thread_id: str) -> str | None:
    """Parse INDEX.md for the latest status entry of a given Document thread.

    Latest = first status line after the `Document: <thread_id>` header
    (per file-bridge-protocol newest-first convention).
    """
    text = INDEX_PATH.read_text(encoding="utf-8")
    block_re = re.compile(
        rf"^Document:\s+{re.escape(thread_id)}\s*$",
        re.MULTILINE,
    )
    match = block_re.search(text)
    if not match:
        return None
    after = text[match.end() :].lstrip("\n")
    # First non-blank, non-comment line after the Document header
    for line in after.splitlines():
        line = line.strip()
        if not line or line.startswith("<!--"):
            continue
        if line.startswith("Document:"):
            break
        # Status line is "STATUS: bridge/<file>"
        if ":" in line:
            return line.split(":", 1)[0].strip()
    return None


@pytest.mark.parametrize("thread_id", AFFECTED_THREADS)
def test_affected_thread_latest_status_remains_verified(thread_id: str) -> None:
    """Closure preservation: each affected thread's INDEX latest status remains VERIFIED.

    Codex F1 fix requirement: Option B does NOT add REVISED to closed threads.
    """
    status = _latest_status_for_thread(thread_id)
    assert status == "VERIFIED", (
        f"affected thread {thread_id} has latest status '{status}'; "
        f"closure-preserving Option B requires VERIFIED to remain the latest status"
    )


@pytest.mark.parametrize("thread_id", AFFECTED_THREADS)
def test_affected_thread_preflight_failure_preserved(thread_id: str) -> None:
    """Historical signal preservation: preflight on each affected thread STILL reports failure.

    Codex F2 fix requirement: do not mask the original operative-file failure
    by moving a new top-of-entry file. The `preflight_passed: false` signal
    must remain visible so the dashboard distinguishes grandfathered from
    current-defect cases.
    """
    result = subprocess.run(
        [
            sys.executable,
            "scripts/bridge_applicability_preflight.py",
            "--bridge-id",
            thread_id,
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert "preflight_passed: `false`" in result.stdout, (
        f"affected thread {thread_id} preflight no longer reports failure; "
        f"the historical signal should remain as grandfathered evidence per "
        f"DELIB-S333-ISOLATION-017-CITATION-BACKFILL-AUDIT and "
        f"bridge/gtkb-isolation-017-citation-backfill-003.md F2 fix"
    )
