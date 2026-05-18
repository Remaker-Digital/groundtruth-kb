"""Tests for the bridge-compliance-gate WI-project membership clause (WI-3315).

Covers DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/
CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP and
DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-AUTH-LIVE-CHECK:
a NEW/REVISED implementation proposal carrying all three project-linkage
metadata lines must resolve to an active project membership and an active,
unexpired, including project authorization in MemBase.

New test surface per bridge/gtkb-bridge-compliance-wi-project-membership-005.md
REVISED-2 (Codex GO at -006). Does not regress
test_bridge_compliance_gate_hard_block_workspace.py or
test_bridge_compliance_gate_project_metadata.py.
"""

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

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
_AUTH_ID = "PAUTH-TEST-MEMBERSHIP"
_PROJECT_ID = "PROJECT-TEST-MEMBERSHIP"
_WI_ID = "WI-7777"
_WI_AUTO_ID = "WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001"


def _make_db(
    tmp_path: Path,
    *,
    membership: tuple[str, str, str] | None,
    authorization: dict | None,
) -> None:
    """Build a fixture groundtruth.db with the two MemBase views the hook reads.

    The hook only issues SELECTs against ``current_project_work_item_memberships``
    and ``current_project_authorizations``; creating them as plain tables with the
    selected columns is behaviorally equivalent to the live views.

    ``membership`` is ``(work_item_id, project_id, status)`` or None to omit.
    ``authorization`` is a row dict or None to omit.
    """
    db_path = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE current_project_work_item_memberships "
            "(work_item_id TEXT, project_id TEXT, status TEXT)"
        )
        conn.execute(
            "CREATE TABLE current_project_authorizations "
            "(id TEXT, project_id TEXT, status TEXT, expires_at TEXT, "
            "included_work_item_ids TEXT, excluded_work_item_ids TEXT)"
        )
        if membership is not None:
            conn.execute(
                "INSERT INTO current_project_work_item_memberships VALUES (?, ?, ?)",
                membership,
            )
        if authorization is not None:
            conn.execute(
                "INSERT INTO current_project_authorizations "
                "(id, project_id, status, expires_at, included_work_item_ids, "
                "excluded_work_item_ids) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    authorization["id"],
                    authorization["project_id"],
                    authorization["status"],
                    authorization["expires_at"],
                    authorization["included_work_item_ids"],
                    authorization["excluded_work_item_ids"],
                ),
            )
        conn.commit()
    finally:
        conn.close()


def _auth(**overrides) -> dict:
    base = {
        "id": _AUTH_ID,
        "project_id": _PROJECT_ID,
        "status": "active",
        "expires_at": None,
        "included_work_item_ids": None,
        "excluded_work_item_ids": None,
    }
    base.update(overrides)
    return base


def _proposal(*, wi: str = _WI_ID, project: str = _PROJECT_ID, auth: str = _AUTH_ID,
              status: str = "NEW") -> str:
    return (
        f"{status}\n\n"
        "# Test Proposal\n\n"
        f"Project Authorization: {auth}\n"
        f"Project: {project}\n"
        f"Work Item: {wi}\n\n"
        + _SPEC_LINKS
    )


def _deny(tmp_path: Path, content: str) -> str | None:
    return _gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path="bridge/test-wi-membership-001.md",
        content=content,
        run_pending_preflight=False,
    )


# --- blocked-condition cases ----------------------------------------------------

def test_wi_not_in_any_project_blocked(tmp_path: Path) -> None:
    _make_db(tmp_path, membership=None, authorization=_auth())
    reason = _deny(tmp_path, _proposal())
    assert reason is not None and "wi-not-found-in-project" in reason


def test_wi_membership_inactive_blocked(tmp_path: Path) -> None:
    _make_db(tmp_path, membership=(_WI_ID, _PROJECT_ID, "revoked"), authorization=_auth())
    reason = _deny(tmp_path, _proposal())
    assert reason is not None and "wi-membership-inactive" in reason


def test_wrong_project_authorization_blocked(tmp_path: Path) -> None:
    # Membership is fine; the proposal cites an authorization id with no row.
    _make_db(tmp_path, membership=(_WI_ID, _PROJECT_ID, "active"), authorization=_auth())
    reason = _deny(tmp_path, _proposal(auth="PAUTH-DOES-NOT-EXIST"))
    assert reason is not None and "authorization-not-found" in reason


def test_inactive_authorization_blocked(tmp_path: Path) -> None:
    _make_db(
        tmp_path,
        membership=(_WI_ID, _PROJECT_ID, "active"),
        authorization=_auth(status="revoked"),
    )
    reason = _deny(tmp_path, _proposal())
    assert reason is not None and "authorization-inactive" in reason


def test_expired_authorization_blocked(tmp_path: Path) -> None:
    _make_db(
        tmp_path,
        membership=(_WI_ID, _PROJECT_ID, "active"),
        authorization=_auth(expires_at="2020-01-01 00:00:00"),
    )
    reason = _deny(tmp_path, _proposal())
    assert reason is not None and "authorization-expired" in reason


def test_excluded_wi_blocked(tmp_path: Path) -> None:
    _make_db(
        tmp_path,
        membership=(_WI_ID, _PROJECT_ID, "active"),
        authorization=_auth(excluded_work_item_ids='["WI-7777"]'),
    )
    reason = _deny(tmp_path, _proposal())
    assert reason is not None and "wi-excluded-from-authorization" in reason


def test_wi_not_in_included_list_blocked(tmp_path: Path) -> None:
    _make_db(
        tmp_path,
        membership=(_WI_ID, _PROJECT_ID, "active"),
        authorization=_auth(included_work_item_ids='["WI-0001", "WI-0002"]'),
    )
    reason = _deny(tmp_path, _proposal())
    assert reason is not None and "wi-not-included-by-authorization" in reason


# --- passing cases --------------------------------------------------------------

def test_active_membership_active_auth_passes(tmp_path: Path) -> None:
    # Active membership + active, unexpired, including authorization.
    _make_db(
        tmp_path,
        membership=(_WI_ID, _PROJECT_ID, "active"),
        authorization=_auth(included_work_item_ids='["WI-7777"]'),
    )
    reason = _deny(tmp_path, _proposal())
    assert reason is None, f"compliant proposal incorrectly denied: {reason}"


def test_verdict_file_passes_through(tmp_path: Path) -> None:
    # A NO-GO verdict file with no metadata: the membership check (which lives
    # inside the NEW/REVISED metadata branch) must never run.
    _make_db(tmp_path, membership=None, authorization=None)
    content = "NO-GO\n\n# Verdict\n\nNo blocking findings.\n"
    reason = _deny(tmp_path, content)
    assert reason is None, f"verdict file incorrectly denied: {reason}"


def test_cited_project_mismatch_with_membership_project_blocked(tmp_path: Path) -> None:
    # The WI is an active member of a DIFFERENT project than the proposal cites.
    _make_db(
        tmp_path,
        membership=(_WI_ID, "PROJECT-SOMEWHERE-ELSE", "active"),
        authorization=_auth(),
    )
    reason = _deny(tmp_path, _proposal(project=_PROJECT_ID))
    assert reason is not None and "wi-not-found-in-project" in reason


# --- WI-AUTO-* id regression (WI-3322) ------------------------------------------

def test_extract_project_metadata_captures_wi_auto_id() -> None:
    # WORK_ITEM_VALUE_RE must capture a spec-intake WI-AUTO-* id so the
    # downstream membership check receives a non-None work_item_id.
    # Regression guard for WI-3322.
    content = _proposal(wi=_WI_AUTO_ID)
    auth_id, project_id, work_item_id = _gate._extract_project_metadata(content)
    assert work_item_id == _WI_AUTO_ID
    assert auth_id == _AUTH_ID
    assert project_id == _PROJECT_ID


def test_wi_auto_id_membership_check_engages(tmp_path: Path) -> None:
    # A WI-AUTO-* proposal whose work item has NO membership row must be
    # BLOCKED with wi-not-found-in-project. Against the un-widened
    # WORK_ITEM_VALUE_RE the id fails to capture, _wi_project_membership_gap
    # short-circuits on its fail-open guard, and no denial is produced -- so
    # this assertion cannot be satisfied by the silent-skip path.
    _make_db(tmp_path, membership=None, authorization=_auth())
    reason = _deny(tmp_path, _proposal(wi=_WI_AUTO_ID))
    assert reason is not None and "wi-not-found-in-project" in reason


def test_wi_auto_id_active_membership_passes(tmp_path: Path) -> None:
    # A WI-AUTO-* work item with an active membership and an active,
    # including authorization yields a passing proposal.
    _make_db(
        tmp_path,
        membership=(_WI_AUTO_ID, _PROJECT_ID, "active"),
        authorization=_auth(included_work_item_ids=f'["{_WI_AUTO_ID}"]'),
    )
    reason = _deny(tmp_path, _proposal(wi=_WI_AUTO_ID))
    assert reason is None, f"compliant WI-AUTO proposal incorrectly denied: {reason}"


def test_block_reason_includes_specific_condition_token(tmp_path: Path) -> None:
    # The denial message must name the specific failed condition AND echo the
    # cited WI / Project / Project Authorization so authors can diagnose.
    _make_db(
        tmp_path,
        membership=(_WI_ID, _PROJECT_ID, "active"),
        authorization=_auth(excluded_work_item_ids='["WI-7777"]'),
    )
    reason = _deny(tmp_path, _proposal())
    assert reason is not None
    assert "wi-excluded-from-authorization" in reason
    assert _WI_ID in reason
    assert _PROJECT_ID in reason
    assert _AUTH_ID in reason
