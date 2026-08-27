"""WI-7232: stale-authorization refusals identify a sole live PAUTH."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

from scripts import implementation_authorization

ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / ".harness-baseline-configuration" / "hooks" / "bridge-compliance-gate.py"
PROJECT_ID = "PROJECT-TEST"
STALE_ID = "PAUTH-STALE"
LIVE_ID = "PAUTH-LIVE"


def _load_gate():
    spec = importlib.util.spec_from_file_location("wi7232_bridge_compliance_gate", GATE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute(
            """CREATE TABLE current_project_authorizations (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                status TEXT NOT NULL,
                expires_at TEXT,
                included_work_item_ids TEXT,
                excluded_work_item_ids TEXT
            )"""
        )
        conn.execute(
            """INSERT INTO current_project_authorizations
               (id, project_id, status, included_work_item_ids, excluded_work_item_ids)
               VALUES (?, ?, 'revoked', '[]', '[]')""",
            (STALE_ID, PROJECT_ID),
        )
        conn.commit()
    finally:
        conn.close()
    return tmp_path


def _insert_authorization(project_root: Path, authorization_id: str, *, status: str = "active") -> None:
    conn = sqlite3.connect(project_root / "groundtruth.db")
    try:
        conn.execute(
            """INSERT INTO current_project_authorizations
               (id, project_id, status, included_work_item_ids, excluded_work_item_ids)
               VALUES (?, ?, ?, '[]', '[]')""",
            (authorization_id, PROJECT_ID, status),
        )
        conn.commit()
    finally:
        conn.close()


def _source_refusal(project_root: Path) -> str:
    row = implementation_authorization._project_authorization_row(project_root, STALE_ID)
    with pytest.raises(implementation_authorization.AuthorizationError) as caught:
        implementation_authorization.validate_project_authorization_row(project_root, row)
    return str(caught.value)


def _gate_refusal(project_root: Path) -> str:
    gate = _load_gate()
    gate._canonical_project_root = lambda _cwd: project_root
    content = "\n".join(
        [
            "NEW",
            "::init gtkb lo",
            "::open build",
            "bridge_kind: implementation_proposal",
            f"Project Authorization: {STALE_ID}",
            f"Project: {PROJECT_ID}",
            "Work Item: WI-7232",
        ]
    )
    gap = gate._wi_project_membership_gap(content, project_root)
    assert gap == "authorization-inactive"
    return gate._project_membership_refusal_message(content, project_root, gap)


def test_refusals_name_the_same_sole_live_authorization(project_root: Path) -> None:
    _insert_authorization(project_root, LIVE_ID)

    source_reason = _source_refusal(project_root)
    gate_reason = _gate_refusal(project_root)

    expected = f"Current active authorization for project {PROJECT_ID}: {LIVE_ID}."
    assert expected in source_reason
    assert expected in gate_reason
    assert "is not active" in source_reason
    assert "membership check: authorization-inactive" in gate_reason


def test_no_live_authorization_preserves_source_refusal_bytes(project_root: Path) -> None:
    assert _source_refusal(project_root) == f"Project authorization {STALE_ID} is not active"
    gate_reason = _gate_refusal(project_root)
    assert "membership check: authorization-inactive" in gate_reason
    assert "Current active authorization" not in gate_reason
    assert "multiple current active authorizations" not in gate_reason


def test_ambiguous_live_authorizations_name_no_canonical_id(project_root: Path) -> None:
    _insert_authorization(project_root, "PAUTH-A")
    _insert_authorization(project_root, "PAUTH-B")

    source_reason = _source_refusal(project_root)
    gate_reason = _gate_refusal(project_root)

    expected = f"Project {PROJECT_ID} has multiple current active authorizations; none is named as canonical."
    assert expected in source_reason
    assert expected in gate_reason
    for authorization_id in ("PAUTH-A", "PAUTH-B"):
        assert authorization_id not in source_reason
        assert authorization_id not in gate_reason


def test_gate_not_found_branch_keeps_classification_and_names_live(project_root: Path) -> None:
    _insert_authorization(project_root, LIVE_ID)
    gate = _load_gate()
    gate._canonical_project_root = lambda _cwd: project_root
    content = "\n".join(
        [
            "NEW",
            "::init gtkb lo",
            "::open build",
            "bridge_kind: implementation_proposal",
            "Project Authorization: PAUTH-MISSING",
            f"Project: {PROJECT_ID}",
            "Work Item: WI-7232",
        ]
    )

    gap = gate._wi_project_membership_gap(content, project_root)
    assert gap == "authorization-not-found"
    reason = gate._project_membership_refusal_message(content, project_root, gap)

    assert "membership check: authorization-not-found" in reason
    assert f"Current active authorization for project {PROJECT_ID}: {LIVE_ID}." in reason
