"""Tests for the bridge-compliance-gate WI-project membership clause.

Covers DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/
CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP: a NEW/REVISED implementation proposal
carrying both project-linkage metadata lines must resolve to an active project
membership in MemBase.

Canon v8.92 section 3 makes authorization a field on the project row that
gates dispatch, not filing, so the gate no longer names or looks up an
authorization record; the tests that asserted that lookup (WI-3315) were
retired with their subject on 2026-09-07 rather than rewritten.
"""

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path
from unittest.mock import patch

from scripts.gtkb_bridge_writer import normalize_bridge_envelope_head

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"


def _load_gate():
    """Import the hyphenated hook module by path."""
    spec = importlib.util.spec_from_file_location("bridge_compliance_gate", ACTIVE_HOOK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_gate = _load_gate()

_SPEC_LINKS = "## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
_PROJECT_ID = "PROJECT-TEST-MEMBERSHIP"
_WI_ID = "WI-7777"
_WI_AUTO_ID = "WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001"


def _make_db(tmp_path: Path, *, membership: tuple[str, str, str] | None) -> None:
    """Build a fixture groundtruth.db with the one MemBase view the hook reads.

    The hook only issues a SELECT against ``current_project_work_item_memberships``;
    creating it as a plain table with the selected columns is behaviorally
    equivalent to the live view. ``membership`` is ``(work_item_id, project_id,
    status)`` or None to omit.
    """
    db_path = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE current_project_work_item_memberships (work_item_id TEXT, project_id TEXT, status TEXT)"
        )
        if membership is not None:
            conn.execute(
                "INSERT INTO current_project_work_item_memberships VALUES (?, ?, ?)",
                membership,
            )
        conn.commit()
    finally:
        conn.close()


def _author_metadata(role: str) -> str:
    """Audit metadata the gate requires; the identity must carry the exact session role."""
    return (
        f"author_identity: {role}/codex\n"
        "author_harness_id: A\n"
        "author_session_context_id: session-123\n"
        "author_model: GPT-5.5\n"
        "author_model_version: 5.5\n"
        "author_model_configuration: Extra High\n"
    )


def _proposal(*, wi: str = _WI_ID, project: str = _PROJECT_ID, status: str = "NEW") -> str:
    return (
        f"{status}\n{_author_metadata('prime-builder')}\n# Test Proposal\n\nProject: {project}\nWork Item: {wi}\n\n"
        + _SPEC_LINKS
    )


def _deny(tmp_path: Path, content: str) -> str | None:
    original_resolver = _gate._canonical_project_root
    _gate._canonical_project_root = lambda cwd_path: cwd_path
    try:
        with patch.object(_gate, "_verdict_self_review_deny", return_value=None):
            return _gate._deny_reason_for_content(
                cwd_path=tmp_path,
                file_path="bridge/test-wi-membership-001.md",
                content=normalize_bridge_envelope_head(content),
                run_pending_preflight=False,
            )
    finally:
        _gate._canonical_project_root = original_resolver


# --- blocked-condition cases ----------------------------------------------------


def test_wi_not_in_any_project_blocked(tmp_path: Path) -> None:
    _make_db(tmp_path, membership=None)
    reason = _deny(tmp_path, _proposal())
    assert reason is not None and "wi-not-found-in-project" in reason


def test_wi_membership_inactive_blocked(tmp_path: Path) -> None:
    _make_db(tmp_path, membership=(_WI_ID, _PROJECT_ID, "revoked"))
    reason = _deny(tmp_path, _proposal())
    assert reason is not None and "wi-membership-inactive" in reason


def test_cited_project_mismatch_with_membership_project_blocked(tmp_path: Path) -> None:
    # The WI is an active member of a DIFFERENT project than the proposal cites.
    _make_db(tmp_path, membership=(_WI_ID, "PROJECT-SOMEWHERE-ELSE", "active"))
    reason = _deny(tmp_path, _proposal(project=_PROJECT_ID))
    assert reason is not None and "wi-not-found-in-project" in reason


# --- passing cases --------------------------------------------------------------


def test_active_membership_passes(tmp_path: Path) -> None:
    _make_db(tmp_path, membership=(_WI_ID, _PROJECT_ID, "active"))
    reason = _deny(tmp_path, _proposal())
    assert reason is None, f"compliant proposal incorrectly denied: {reason}"


def test_verdict_file_passes_through(tmp_path: Path) -> None:
    # A NO-GO verdict file with author metadata: the membership check (which
    # lives inside the NEW/REVISED project-metadata branch) must never run.
    _make_db(tmp_path, membership=None)
    content = "NO-GO\n" + _author_metadata("loyal-opposition") + "\n# Verdict\n\nNo blocking findings.\n"
    reason = _deny(tmp_path, content)
    assert reason is None, f"verdict file incorrectly denied: {reason}"


# --- WI-AUTO-* id regression (WI-3322) ------------------------------------------


def test_extract_project_metadata_captures_wi_auto_id() -> None:
    # WORK_ITEM_VALUE_RE must capture a spec-intake WI-AUTO-* id so the
    # downstream membership check receives a non-None work_item_id.
    # Regression guard for WI-3322.
    content = _proposal(wi=_WI_AUTO_ID)
    project_id, work_item_id = _gate._extract_project_metadata(content)
    assert work_item_id == _WI_AUTO_ID
    assert project_id == _PROJECT_ID


def test_wi_auto_id_membership_check_engages(tmp_path: Path) -> None:
    # A WI-AUTO-* proposal whose work item has NO membership row must be
    # BLOCKED with wi-not-found-in-project. Against the un-widened
    # WORK_ITEM_VALUE_RE the id fails to capture, _wi_project_membership_gap
    # short-circuits on its fail-open guard, and no denial is produced -- so
    # this assertion cannot be satisfied by the silent-skip path.
    _make_db(tmp_path, membership=None)
    reason = _deny(tmp_path, _proposal(wi=_WI_AUTO_ID))
    assert reason is not None and "wi-not-found-in-project" in reason


def test_wi_auto_id_active_membership_passes(tmp_path: Path) -> None:
    _make_db(tmp_path, membership=(_WI_AUTO_ID, _PROJECT_ID, "active"))
    reason = _deny(tmp_path, _proposal(wi=_WI_AUTO_ID))
    assert reason is None, f"compliant WI-AUTO proposal incorrectly denied: {reason}"


def test_block_reason_includes_specific_condition_token(tmp_path: Path) -> None:
    # The denial message must name the specific failed condition AND echo the
    # cited WI / Project so authors can diagnose.
    _make_db(tmp_path, membership=(_WI_ID, _PROJECT_ID, "revoked"))
    reason = _deny(tmp_path, _proposal())
    assert reason is not None
    assert "wi-membership-inactive" in reason
    assert _WI_ID in reason
    assert _PROJECT_ID in reason
    assert "gt projects add-item" in reason
