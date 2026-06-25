# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Gate parity tests for DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001 assertion A4."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AUTH_SCRIPT = REPO_ROOT / "scripts" / "implementation_authorization.py"
ACTIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"

_PROJECT_ID = "PROJECT-PARITY"
_AUTH_ID = "PAUTH-PARITY"
_WI_LISTED = "WI-9001"
_WI_OTHER = "WI-9002"


def _load_auth():
    spec = importlib.util.spec_from_file_location("implementation_authorization_parity", AUTH_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["implementation_authorization_parity"] = module
    spec.loader.exec_module(module)
    return module


def _load_gate():
    spec = importlib.util.spec_from_file_location("bridge_compliance_gate_parity", ACTIVE_HOOK)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed_db(
    root: Path,
    *,
    membership_wi: str | None,
    included: list[str] | None,
    excluded: list[str] | None = None,
) -> None:
    (root / "groundtruth.toml").write_text('[project]\nproject_name = "Parity"\n', encoding="utf-8")
    db_path = root / "groundtruth.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("CREATE TABLE current_projects (id TEXT PRIMARY KEY, status TEXT)")
        conn.execute(
            "CREATE TABLE current_project_work_item_memberships (work_item_id TEXT, project_id TEXT, status TEXT)"
        )
        conn.execute(
            "CREATE TABLE current_project_authorizations "
            "(id TEXT, project_id TEXT, status TEXT, expires_at TEXT, "
            "included_work_item_ids TEXT, excluded_work_item_ids TEXT, "
            "authorization_name TEXT, owner_decision_deliberation_id TEXT, "
            "scope_summary TEXT, allowed_mutation_classes TEXT, included_spec_ids TEXT, excluded_spec_ids TEXT)"
        )
        conn.execute("INSERT INTO current_projects VALUES (?, 'active')", (_PROJECT_ID,))
        if membership_wi is not None:
            conn.execute(
                "INSERT INTO current_project_work_item_memberships VALUES (?, ?, 'active')",
                (membership_wi, _PROJECT_ID),
            )
        conn.execute(
            "INSERT INTO current_project_authorizations "
            "(id, project_id, status, expires_at, included_work_item_ids, excluded_work_item_ids, "
            "authorization_name, owner_decision_deliberation_id, scope_summary, "
            "allowed_mutation_classes, included_spec_ids, excluded_spec_ids) "
            "VALUES (?, ?, 'active', NULL, ?, ?, 'parity', 'DELIB-PARITY', 'parity', '[]', '[]', '[]')",
            (
                _AUTH_ID,
                _PROJECT_ID,
                json.dumps(included) if included is not None else None,
                json.dumps(excluded) if excluded is not None else None,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def _proposal(wi: str) -> str:
    return (
        "NEW\n"
        "author_session_context_id: parity-session\n\n"
        f"Project Authorization: {_AUTH_ID}\n"
        f"Project: {_PROJECT_ID}\n"
        f"Work Item: {wi}\n"
    )


def _impl_verdict(auth, root: Path, wi: str) -> str:
    row = auth._project_authorization_row(root, _AUTH_ID)
    try:
        auth.validate_project_authorization_row(root, row, work_item_id=wi)
        return "authorize"
    except auth.AuthorizationError:
        return "block"


def _write_verdict(gate, root: Path, wi: str) -> str:
    original = gate._canonical_project_root
    gate._canonical_project_root = lambda cwd_path: cwd_path
    try:
        gap = gate._wi_project_membership_gap(_proposal(wi), root)
        return "authorize" if gap is None else "block"
    finally:
        gate._canonical_project_root = original


@pytest.mark.parametrize(
    ("wi", "membership_wi", "included", "expected"),
    [
        (_WI_LISTED, _WI_LISTED, [_WI_LISTED, _WI_OTHER], "authorize"),
        (_WI_LISTED, None, [_WI_LISTED], "authorize"),
        (_WI_OTHER, _WI_OTHER, [_WI_LISTED], "block"),
        (_WI_OTHER, None, [_WI_LISTED], "block"),
        (_WI_LISTED, _WI_LISTED, None, "authorize"),
        (_WI_OTHER, None, None, "block"),
    ],
)
def test_gate_parity_truth_table(
    tmp_path: Path,
    wi: str,
    membership_wi: str | None,
    included: list[str] | None,
    expected: str,
) -> None:
    auth = _load_auth()
    gate = _load_gate()
    _seed_db(tmp_path, membership_wi=membership_wi, included=included)
    assert _impl_verdict(auth, tmp_path, wi) == expected
    assert _write_verdict(gate, tmp_path, wi) == expected


def test_excluded_precedence_blocks_both_gates(tmp_path: Path) -> None:
    auth = _load_auth()
    gate = _load_gate()
    _seed_db(
        tmp_path,
        membership_wi=_WI_LISTED,
        included=[_WI_LISTED],
        excluded=[_WI_LISTED],
    )
    assert _impl_verdict(auth, tmp_path, _WI_LISTED) == "block"
    assert _write_verdict(gate, tmp_path, _WI_LISTED) == "block"
