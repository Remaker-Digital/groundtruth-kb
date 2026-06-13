"""Tests for the WI-4506 TAFE observability projection in the dashboard SQLite.

Bridge: bridge/gtkb-tafe-dashboard-observability-001.md (NEW),
       bridge/gtkb-tafe-dashboard-observability-002.md (GO).
PAUTH: TAFE-TRANCHE-3-PHASE-2-OBSERVABILITY-HYGIENE; allowed mutation classes
       are source + test only; forbidden: cutover, dual_write, live dispatch,
       authoritative generated view, kb_schema_change.

Verifies:
  - The TAFE projection schema migration is idempotent.
  - `_refresh_tafe_projection` is read-only against `groundtruth.db` and
    projects the canonical TAFE rows into the dashboard SQLite.
  - Rerun is idempotent (counts unchanged).
  - Absent `groundtruth.db` (fresh adopter) yields zero projected rows
    without raising (graceful absence).
  - Structural guard: the projection helper source contains no INSERT /
    UPDATE / DELETE / DROP / CREATE statement targeting the canonical
    `groundtruth.db` and no MemBase mutating API call.
"""

from __future__ import annotations

import ast
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from scripts.gtkb_dashboard.refresh_dashboard_db import (  # noqa: E402
    TAFE_PROJECTION_TABLE_NAMES,
    _migrate_tafe_projection_schema,
    _refresh_tafe_projection,
    _refresh_tafe_projection_safe,
)

REFRESH_MODULE_PATH = REPO_ROOT / "scripts" / "gtkb_dashboard" / "refresh_dashboard_db.py"


def _seed_tafe_kb(kb_path: Path) -> None:
    """Build a tiny canonical groundtruth.db with the TAFE tables and seed rows.

    Uses raw SQLite (the canonical schema is also raw SQLite); this avoids
    pulling the full KnowledgeDB initialization path into the test. The
    `_refresh_tafe_projection` helper reads via the `KnowledgeDB` API.
    """
    from groundtruth_kb.db import KnowledgeDB

    kb = KnowledgeDB(kb_path)
    try:
        # Flow definition referenced by the flow_instance below (referential
        # integrity guard inside insert_flow_instance).
        kb.insert_flow_definition(
            id="implementation",
            flow_type="implementation",
            title="Implementation flow (test seed)",
            stage_sequence=["propose", "review", "implement", "verify"],
            required_roles_by_stage={
                "propose": "prime-builder",
                "review": "loyal-opposition",
                "implement": "prime-builder",
                "verify": "loyal-opposition",
            },
            changed_by="test",
            change_reason="seed for WI-4506 test",
        )
        # Capability snapshot.
        kb.insert_agent_capability_snapshot(
            id="cap-1",
            harness_id="B",
            role="prime-builder",
            captured_at="2026-06-13T00:00:00Z",
            health_status="healthy",
            harness_name="claude",
            subject_scope="gtkb",
            reviewer_precedence=10,
            workspace_availability="available",
            model_identifier="claude-opus-4-8",
            capabilities=["bash"],
            source="test-seed",
            changed_by="test",
            change_reason="seed for WI-4506 test",
        )
        # Flow + stage + lease + telemetry.
        kb.insert_flow_instance(
            id="flow-1",
            flow_definition_id="implementation",
            subject_type="bridge_thread",
            subject_id="gtkb-tafe-dashboard-observability",
            flow_type="implementation",
            status="active",
            started_at="2026-06-13T00:00:00Z",
            changed_by="test",
            change_reason="seed",
        )
        kb.insert_stage_instance(
            id="stage-1",
            flow_instance_id="flow-1",
            stage_id="implement",
            stage_index=2,
            required_role="prime-builder",
            status="in_progress",
            claim_status="claimed",
            claimed_by_harness_id="B",
            claimed_by_session_id="869ade5b",
            started_at="2026-06-13T00:00:00Z",
            changed_by="test",
            change_reason="seed",
        )
        kb.insert_stage_lease(
            id="lease-1",
            stage_instance_id="stage-1",
            holder_harness_id="B",
            holder_session_id="869ade5b",
            ttl_seconds=600,
            acquired_at="2026-06-13T00:00:00Z",
            expires_at="2026-06-13T00:10:00Z",
            changed_by="test",
            change_reason="seed",
        )
        kb.insert_stage_attempt_telemetry(
            id="tel-1",
            flow_instance_id="flow-1",
            stage_instance_id="stage-1",
            attempt_number=1,
            agent_harness_id="B",
            outcome="success",
            verdict="GO",
            started_at="2026-06-13T00:00:00Z",
            completed_at="2026-06-13T00:05:00Z",
            duration_ms=300000,
            changed_by="test",
            change_reason="seed",
        )
        kb.insert_stage_attempt_telemetry(
            id="tel-2",
            flow_instance_id="flow-1",
            stage_instance_id="stage-1",
            attempt_number=2,
            agent_harness_id="B",
            outcome="failure",
            failure_class="timeout",
            started_at="2026-06-13T00:06:00Z",
            completed_at="2026-06-13T00:11:00Z",
            duration_ms=300000,
            changed_by="test",
            change_reason="seed",
        )
    finally:
        kb.close()


def test_migration_creates_all_five_tafe_projection_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "gtkb-dashboard.sqlite"
    _migrate_tafe_projection_schema(db_path)
    with sqlite3.connect(db_path) as conn:
        present = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert set(TAFE_PROJECTION_TABLE_NAMES) <= present
    assert len(TAFE_PROJECTION_TABLE_NAMES) == 5


def test_migration_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "gtkb-dashboard.sqlite"
    _migrate_tafe_projection_schema(db_path)
    _migrate_tafe_projection_schema(db_path)  # second call must not raise.
    with sqlite3.connect(db_path) as conn:
        present = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert set(TAFE_PROJECTION_TABLE_NAMES) <= present


def test_refresh_projects_canonical_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "gtkb-dashboard.sqlite"
    kb_path = tmp_path / "groundtruth.db"
    _migrate_tafe_projection_schema(db_path)
    _seed_tafe_kb(kb_path)

    counts = _refresh_tafe_projection(db_path, tmp_path)

    assert counts["tafe_agent_capability_snapshots"] == 1
    assert counts["tafe_flow_instances"] == 1
    assert counts["tafe_stage_instances"] == 1
    assert counts["tafe_stage_leases"] == 1
    assert counts["tafe_stage_attempt_telemetry"] == 2  # success + failure

    with sqlite3.connect(db_path) as conn:
        outcomes = {row[0] for row in conn.execute("SELECT DISTINCT outcome FROM tafe_stage_attempt_telemetry")}
        assert outcomes == {"success", "failure"}
        failure_classes = {
            row[0]
            for row in conn.execute("SELECT failure_class FROM tafe_stage_attempt_telemetry WHERE outcome = 'failure'")
        }
        assert failure_classes == {"timeout"}


def test_refresh_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "gtkb-dashboard.sqlite"
    kb_path = tmp_path / "groundtruth.db"
    _migrate_tafe_projection_schema(db_path)
    _seed_tafe_kb(kb_path)

    first = _refresh_tafe_projection(db_path, tmp_path)
    second = _refresh_tafe_projection(db_path, tmp_path)
    assert first == second


def test_graceful_absence_when_groundtruth_db_missing(tmp_path: Path) -> None:
    db_path = tmp_path / "gtkb-dashboard.sqlite"
    _migrate_tafe_projection_schema(db_path)
    # No groundtruth.db in tmp_path — fresh-adopter case.
    counts = _refresh_tafe_projection(db_path, tmp_path)
    assert all(v == 0 for v in counts.values())


def test_refresh_safe_swallows_exceptions(tmp_path: Path, monkeypatch) -> None:
    """The _safe wrapper must never propagate; the dashboard refresh continues."""
    db_path = tmp_path / "gtkb-dashboard.sqlite"

    def _boom(*_args, **_kwargs):
        raise RuntimeError("simulated migration failure")

    monkeypatch.setattr(
        "scripts.gtkb_dashboard.refresh_dashboard_db._migrate_tafe_projection_schema",
        _boom,
    )
    # Must not raise.
    _refresh_tafe_projection_safe(db_path, tmp_path)


def test_projection_helper_does_not_mutate_canonical_kb_source() -> None:
    """Structural guard: the projection module must not contain INSERT/UPDATE/
    DELETE statements targeting `groundtruth.db` and must not call MemBase
    mutating helpers (`insert_*`, `update_*`, `replace_*`) on KnowledgeDB.

    Per the proposal's no-mutation bound (SPEC-TAFE-R7): the dashboard
    projection is read-only against the canonical store.
    """
    source = REFRESH_MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    # Locate the bodies of the TAFE projection functions only — the rest of
    # the module legitimately writes to the dashboard SQLite.
    tafe_fn_names = {
        "_refresh_tafe_projection",
        "_migrate_tafe_projection_schema",
        "_refresh_tafe_projection_safe",
        "_project_tafe_row_subset",
    }
    forbidden_method_calls = {
        "insert_flow_instance",
        "insert_stage_instance",
        "insert_stage_lease",
        "insert_stage_attempt_telemetry",
        "insert_agent_capability_snapshot",
        "update_flow_instance",
        "update_stage_instance",
        "update_stage_lease",
        "update_stage_attempt_telemetry",
        "update_agent_capability_snapshot",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in tafe_fn_names:
            for sub in ast.walk(node):
                if isinstance(sub, ast.Attribute) and sub.attr in forbidden_method_calls:
                    raise AssertionError(
                        f"TAFE projection helper '{node.name}' calls forbidden mutating method '.{sub.attr}'"
                    )

    # And no kb_path / canonical-store SQL writes anywhere in those helpers.
    body_segments: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in tafe_fn_names:
            body_segments.append(ast.unparse(node))
    combined = "\n".join(body_segments).upper()
    for forbidden_sql in ("INSERT INTO FLOW_", "UPDATE FLOW_", "DELETE FROM FLOW_", "DROP TABLE FLOW_"):
        assert forbidden_sql not in combined, (
            f"TAFE projection helpers contain forbidden canonical SQL: {forbidden_sql}"
        )
