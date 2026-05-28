"""Unit tests for DORA-001b Track 2 dashboard ingest + Azure reconciliation.

Tests the manifest-ingest classification contract, idempotent dedup,
graceful degradation of Azure reconciliation, and the confidence-upgrade
path. Covers Codex GO `-006` implementation conditions 1-4.

Created 2026-04-25 (S308) per
`bridge/gtkb-dora-001b-track2-implementation-003.md` (Codex GO at `-004`).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gtkb_dashboard.refresh_dashboard_db import (  # noqa: E402
    _REQUIRED_MIGRATION_COLUMNS,
    _classify_manifest,
    _ingest_canonical_pipeline_manifests,
    _is_deployment_event,
    _migrate_schema,
    _reconcile_against_azure_revisions,
    initialize_database,
)


def _make_conn() -> sqlite3.Connection:
    """Create an in-memory SQLite DB with the delivery_timeline_events table
    matching production schema, including the Track 2 additive columns."""
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE delivery_timeline_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sort_order INTEGER,
            stage TEXT,
            stage_label TEXT,
            event TEXT,
            timestamp TEXT,
            date_label TEXT,
            version TEXT,
            commit_sha TEXT,
            branch TEXT,
            result TEXT,
            result_color TEXT,
            test_results TEXT,
            source TEXT,
            url TEXT,
            notes TEXT,
            environment TEXT,
            event_kind TEXT NOT NULL DEFAULT 'change',
            deployable_change_id TEXT NOT NULL DEFAULT '',
            commit_range_start TEXT NOT NULL DEFAULT '',
            commit_range_end TEXT NOT NULL DEFAULT '',
            rollback_of_deploy_id TEXT NOT NULL DEFAULT '',
            hotfix_of_deploy_id TEXT NOT NULL DEFAULT '',
            _authority_source TEXT NOT NULL DEFAULT 'heuristic',
            _image_ref TEXT NOT NULL DEFAULT '',
            _image_tag TEXT NOT NULL DEFAULT '',
            _revision_name TEXT NOT NULL DEFAULT '',
            _deployed_at TEXT NOT NULL DEFAULT '',
            _consistency TEXT NOT NULL DEFAULT 'unknown',
            _confidence TEXT NOT NULL DEFAULT 'low'
        )
        """
    )
    return conn


def _write_manifest(tmp_path: Path, env: str, ts: int, body: dict[str, Any]) -> Path:
    """Write a deploy-result manifest under tmp_path/logs/."""
    logs = tmp_path / "logs"
    logs.mkdir(exist_ok=True)
    path = logs / f"deploy-result-{env}-{ts}.json"
    path.write_text(json.dumps(body), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# T1-T6: _classify_manifest() — classification contract per scoping sec 5.5
# ---------------------------------------------------------------------------


def test_t1_dry_run_is_pipeline_dry_run() -> None:
    """T1: dry_run=true maps to canonical_pipeline_dry_run, never canonical_deploy."""
    assert _classify_manifest({"dry_run": True}) == "canonical_pipeline_dry_run"
    assert (
        _classify_manifest(
            {
                "dry_run": True,
                "phases": [{"phase": 9, "status": "PASS"}],
            }
        )
        == "canonical_pipeline_dry_run"
    )


def test_t2_no_deploy_phase_is_pipeline_run() -> None:
    """T2: manifest with no phase 9 maps to canonical_pipeline_run."""
    assert _classify_manifest({}) == "canonical_pipeline_run"
    assert _classify_manifest({"phases": []}) == "canonical_pipeline_run"
    assert (
        _classify_manifest(
            {
                "phases": [{"phase": 0, "status": "FAIL"}],
            }
        )
        == "canonical_pipeline_run"
    )


def test_t3_deploy_phase_fail_is_attempted_failed() -> None:
    """T3: phase 9 status=FAIL maps to canonical_deploy_attempted_failed."""
    assert (
        _classify_manifest(
            {
                "phases": [{"phase": 9, "status": "FAIL"}],
            }
        )
        == "canonical_deploy_attempted_failed"
    )


def test_t4_deploy_phase_pass_pretrack1_is_canonical_deploy() -> None:
    """T4: phase 9 status=PASS without deploy_evidence maps to canonical_deploy
    (pre-Track-1 manifest; will be at _confidence='medium' on ingest)."""
    assert (
        _classify_manifest(
            {
                "phases": [{"phase": 9, "status": "PASS"}],
            }
        )
        == "canonical_deploy"
    )


def test_t5_deploy_evidence_target_succeeded_is_canonical_deploy() -> None:
    """T5: phase 9 PASS with deploy_evidence(target_update_succeeded=true)
    maps to canonical_deploy."""
    assert (
        _classify_manifest(
            {
                "phases": [{"phase": 9, "status": "PASS"}],
                "deploy_evidence": {
                    "target_update_attempted": True,
                    "target_update_succeeded": True,
                },
            }
        )
        == "canonical_deploy"
    )


def test_t6_deploy_evidence_target_failed_is_attempted_failed() -> None:
    """T6: phase 9 PASS with deploy_evidence(target_update_succeeded=false)
    maps to canonical_deploy_attempted_failed."""
    assert (
        _classify_manifest(
            {
                "phases": [{"phase": 9, "status": "PASS"}],
                "deploy_evidence": {
                    "target_update_attempted": True,
                    "target_update_succeeded": False,
                },
            }
        )
        == "canonical_deploy_attempted_failed"
    )


# ---------------------------------------------------------------------------
# T7: query-before-insert idempotence per Codex F1 Option 2
# ---------------------------------------------------------------------------


def test_t7_ingest_is_idempotent_via_source_dedup(tmp_path: Path) -> None:
    """T7: second call to _ingest_canonical_pipeline_manifests skips manifests
    already inserted (dedup via _authority_source + source). Per Codex `-002`
    F1 Option 2 (query-before-insert)."""
    _write_manifest(
        tmp_path,
        "production",
        1700000000,
        {
            "dry_run": False,
            "version": "v1.99.0",
            "environment": "production",
            "status": "SUCCESS",
            "repo_commit": "abc12345",
            "started_at": "2026-04-25T00:00:00Z",
            "phases": [{"phase": 9, "status": "PASS"}],
        },
    )

    conn = _make_conn()
    counts1 = _ingest_canonical_pipeline_manifests(conn, tmp_path)
    counts2 = _ingest_canonical_pipeline_manifests(conn, tmp_path)

    assert counts1["rows_inserted"] == 1
    assert counts1["rows_skipped"] == 0
    assert counts2["rows_inserted"] == 0
    assert counts2["rows_skipped"] == 1

    # Total canonical_manifest rows must remain exactly 1.
    total = conn.execute(
        "SELECT COUNT(*) FROM delivery_timeline_events WHERE _authority_source = 'canonical_manifest'"
    ).fetchone()[0]
    assert total == 1


# ---------------------------------------------------------------------------
# T8-T9: graceful degradation per scoping sec 6 + Codex condition 4
# ---------------------------------------------------------------------------


def test_t8_reconcile_az_returncode_nonzero_degrades_to_unknown() -> None:
    """T8: az returns nonzero -> affected rows _consistency='unknown',
    refresh_runs.status NOT touched (function returns counts; never raises)."""
    conn = _make_conn()
    conn.execute(
        """
        INSERT INTO delivery_timeline_events
        (source, environment, event_kind, _authority_source, _image_ref, _confidence)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            "logs/deploy-result-production-1.json",
            "production",
            "canonical_deploy",
            "canonical_manifest",
            "acragentredeastus.azurecr.io/agent-red:v1.99.0",
            "medium",
        ),
    )
    conn.commit()

    fake_result = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="auth")
    with patch("subprocess.run", return_value=fake_result):
        counts = _reconcile_against_azure_revisions(conn, ["production"])

    assert counts["rows_unknown"] == 1
    assert counts["rows_matched"] == 0
    consistency = conn.execute("SELECT _consistency FROM delivery_timeline_events").fetchone()[0]
    assert consistency == "unknown"


def test_t9_reconcile_az_not_installed_degrades_to_unknown() -> None:
    """T9: az CLI missing (FileNotFoundError) -> graceful degradation."""
    conn = _make_conn()
    conn.execute(
        """
        INSERT INTO delivery_timeline_events
        (source, environment, event_kind, _authority_source, _confidence)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("logs/deploy-result-production-1.json", "production", "canonical_deploy", "canonical_manifest", "medium"),
    )
    conn.commit()

    with patch("subprocess.run", side_effect=FileNotFoundError("az not installed")):
        counts = _reconcile_against_azure_revisions(conn, ["production"])

    assert counts["rows_unknown"] == 1
    consistency = conn.execute("SELECT _consistency FROM delivery_timeline_events").fetchone()[0]
    assert consistency == "unknown"


# ---------------------------------------------------------------------------
# T10-T11: reconciliation success cases
# ---------------------------------------------------------------------------


def test_t10_reconcile_match_sets_both_match() -> None:
    """T10: matching Azure revision -> _consistency='both_match';
    _revision_name populated."""
    conn = _make_conn()
    conn.execute(
        """
        INSERT INTO delivery_timeline_events
        (source, environment, event_kind, _authority_source, _image_ref,
         _image_tag, _revision_name, _confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "logs/deploy-result-production-1.json",
            "production",
            "canonical_deploy",
            "canonical_manifest",
            "acragentredeastus.azurecr.io/agent-red:v1.99.0",
            "v1.99.0",
            "agent-red-api-gateway--abc12",
            "medium",
        ),
    )
    conn.commit()

    fake_az = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=json.dumps(
            [
                {
                    "name": "agent-red-api-gateway--abc12",
                    "properties": {
                        "template": {"containers": [{"image": "acragentredeastus.azurecr.io/agent-red:v1.99.0"}]}
                    },
                }
            ]
        ),
        stderr="",
    )
    with patch("subprocess.run", return_value=fake_az):
        counts = _reconcile_against_azure_revisions(conn, ["production"])

    assert counts["rows_matched"] == 1
    row = conn.execute("SELECT _consistency, _revision_name, _confidence FROM delivery_timeline_events").fetchone()
    assert row[0] == "both_match"
    assert row[1] == "agent-red-api-gateway--abc12"
    # Confidence upgrade rule: image_ref AND revision_name present -> high.
    assert row[2] == "high"


def test_t11_reconcile_drift_sets_manifest_only() -> None:
    """T11: no matching Azure revision -> _consistency='manifest_only';
    _confidence stays at medium (or downgrades)."""
    conn = _make_conn()
    conn.execute(
        """
        INSERT INTO delivery_timeline_events
        (source, environment, event_kind, _authority_source, _image_ref,
         _image_tag, _confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "logs/deploy-result-production-1.json",
            "production",
            "canonical_deploy",
            "canonical_manifest",
            "acragentredeastus.azurecr.io/agent-red:v1.99.0",
            "v1.99.0",
            "medium",
        ),
    )
    conn.commit()

    fake_az = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=json.dumps(
            [
                {
                    "name": "agent-red-api-gateway--xyz99",
                    "properties": {
                        "template": {"containers": [{"image": "acragentredeastus.azurecr.io/agent-red:v1.98.0"}]}
                    },
                }
            ]
        ),
        stderr="",
    )
    with patch("subprocess.run", return_value=fake_az):
        counts = _reconcile_against_azure_revisions(conn, ["production"])

    assert counts["rows_drift"] == 1
    consistency = conn.execute("SELECT _consistency FROM delivery_timeline_events").fetchone()[0]
    assert consistency == "manifest_only"


# ---------------------------------------------------------------------------
# T12: DORA KPI exclusion contract per Codex condition 2
# ---------------------------------------------------------------------------


def test_t12_only_canonical_deploy_counts_as_deployment_event() -> None:
    """T12: _is_deployment_event helper returns True only for canonical_deploy.
    Future GTKB-DORA-002 deployment-frequency math uses this to exclude
    canonical_pipeline_run and canonical_pipeline_dry_run."""
    assert _is_deployment_event("canonical_deploy") is True
    assert _is_deployment_event("canonical_deploy_attempted_failed") is False
    assert _is_deployment_event("canonical_pipeline_run") is False
    assert _is_deployment_event("canonical_pipeline_dry_run") is False
    assert _is_deployment_event("change") is False
    assert _is_deployment_event("workflow_run") is False


# ---------------------------------------------------------------------------
# T13: confidence-upgrade path (Codex condition 3 cap)
# ---------------------------------------------------------------------------


def test_t13_ingest_emits_medium_then_reconcile_upgrades_to_high(tmp_path: Path) -> None:
    """T13: with full deploy_evidence(target_update_succeeded=true), ingest
    emits _confidence='medium' (per Codex condition 3 cap). Subsequent
    reconciliation with matching Azure revision upgrades to 'high'."""
    _write_manifest(
        tmp_path,
        "production",
        1700000001,
        {
            "dry_run": False,
            "version": "v1.99.0",
            "environment": "production",
            "status": "SUCCESS",
            "repo_commit": "abc12345",
            "started_at": "2026-04-25T00:00:00Z",
            "phases": [{"phase": 9, "status": "PASS"}],
            "deploy_evidence": {
                "image": "acragentredeastus.azurecr.io/agent-red:v1.99.0",
                "image_tag": "v1.99.0",
                "revision_name": "agent-red-api-gateway--abc12",
                "target_verified_at": "2026-04-25T00:01:00Z",
                "target_update_attempted": True,
                "target_update_succeeded": True,
            },
        },
    )

    conn = _make_conn()
    _ingest_canonical_pipeline_manifests(conn, tmp_path)

    confidence_after_ingest = conn.execute("SELECT _confidence FROM delivery_timeline_events").fetchone()[0]
    assert confidence_after_ingest == "medium", (
        "Ingest must cap confidence at medium per Codex condition 3, even with full deploy_evidence."
    )

    # Now reconcile with matching Azure revision -> upgrade to high.
    fake_az = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=json.dumps(
            [
                {
                    "name": "agent-red-api-gateway--abc12",
                    "properties": {
                        "template": {"containers": [{"image": "acragentredeastus.azurecr.io/agent-red:v1.99.0"}]}
                    },
                }
            ]
        ),
        stderr="",
    )
    with patch("subprocess.run", return_value=fake_az):
        _reconcile_against_azure_revisions(conn, ["production"])

    confidence_after_reconcile = conn.execute("SELECT _confidence FROM delivery_timeline_events").fetchone()[0]
    assert confidence_after_reconcile == "high", (
        "Reconciliation with matching Azure revision must upgrade _confidence from medium to high."
    )


# ---------------------------------------------------------------------------
# Schema migration sanity check
# ---------------------------------------------------------------------------


def test_migration_columns_include_track2_seven() -> None:
    """Sanity: the 7 Track 2 columns are present in _REQUIRED_MIGRATION_COLUMNS."""
    column_names = {name for name, _ in _REQUIRED_MIGRATION_COLUMNS}
    track2_columns = {
        "_authority_source",
        "_image_ref",
        "_image_tag",
        "_revision_name",
        "_deployed_at",
        "_consistency",
        "_confidence",
    }
    assert track2_columns.issubset(column_names), f"Missing Track 2 columns: {track2_columns - column_names}"


# ---------------------------------------------------------------------------
# T14: real-schema reproduction — addresses Codex `-006` F1
# ---------------------------------------------------------------------------
#
# The bespoke `_make_conn()` fixture above carries an `environment` column
# matching what Codex `-006` proved was MISSING from production schema.sql +
# migration. T14 exercises the production initialize+migrate path so a future
# regression of either path fails here, not silently in production.


def test_t14_real_schema_supports_canonical_manifest_ingest_and_reconcile(
    tmp_path: Path,
) -> None:
    """T14: production `initialize_database` + `_migrate_schema` produces a
    `delivery_timeline_events` table that accepts canonical-manifest ingestion
    and Azure reconciliation end-to-end.

    Codex `-006` reproduction: the prior implementation passed all 13 unit
    tests via the bespoke in-memory fixture but failed against real schema
    because `environment` was absent from both `schema.sql` and
    `_REQUIRED_MIGRATION_COLUMNS`. This test creates a DB through the
    production code paths only — no bespoke CREATE TABLE — and would have
    failed with `OperationalError: table delivery_timeline_events has no
    column named environment` against the prior implementation.
    """
    db_path = tmp_path / "production-like.sqlite"
    initialize_database(db_path)
    _migrate_schema(db_path)

    # Sanity: confirm the production paths produced a table with `environment`
    # plus all Track 2 columns. Probing column metadata catches both fresh-DB
    # and migration regressions in a single assertion.
    with sqlite3.connect(db_path) as probe:
        cols = {row[1] for row in probe.execute("PRAGMA table_info('delivery_timeline_events')").fetchall()}
    required = {
        "environment",
        "event_kind",
        "deployable_change_id",
        "commit_range_start",
        "commit_range_end",
        "rollback_of_deploy_id",
        "hotfix_of_deploy_id",
        "_authority_source",
        "_image_ref",
        "_image_tag",
        "_revision_name",
        "_deployed_at",
        "_consistency",
        "_confidence",
    }
    missing = required - cols
    assert not missing, (
        f"Production schema/migration missing columns: {missing}. "
        "schema.sql and _REQUIRED_MIGRATION_COLUMNS must agree."
    )

    # Exercise ingest end-to-end against the real DB.
    _write_manifest(
        tmp_path,
        "production",
        1700000099,
        {
            "dry_run": False,
            "version": "v1.99.0",
            "environment": "production",
            "status": "SUCCESS",
            "repo_commit": "abc12345",
            "started_at": "2026-04-25T00:00:00Z",
            "phases": [{"phase": 9, "status": "PASS"}],
            "deploy_evidence": {
                "image": "acragentredeastus.azurecr.io/agent-red:v1.99.0",
                "image_tag": "v1.99.0",
                "revision_name": "agent-red-api-gateway--abc12",
                "target_verified_at": "2026-04-25T00:01:00Z",
                "target_update_attempted": True,
                "target_update_succeeded": True,
            },
        },
    )

    with sqlite3.connect(db_path) as conn:
        counts = _ingest_canonical_pipeline_manifests(conn, tmp_path)
        assert counts["rows_inserted"] == 1
        assert counts["rows_skipped"] == 0

        # Verify the row landed with environment populated from the manifest.
        env_value = conn.execute(
            "SELECT environment FROM delivery_timeline_events WHERE _authority_source = 'canonical_manifest'"
        ).fetchone()[0]
        assert env_value == "production"

        # Reconcile against a matching Azure revision through the real DB.
        fake_az = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                [
                    {
                        "name": "agent-red-api-gateway--abc12",
                        "properties": {
                            "template": {"containers": [{"image": "acragentredeastus.azurecr.io/agent-red:v1.99.0"}]}
                        },
                    }
                ]
            ),
            stderr="",
        )
        with patch("subprocess.run", return_value=fake_az):
            reconcile_counts = _reconcile_against_azure_revisions(conn, ["production"])
        assert reconcile_counts["rows_matched"] == 1
        assert reconcile_counts["rows_unknown"] == 0


def test_t15_migration_is_idempotent_against_real_schema(tmp_path: Path) -> None:
    """T15: running `_migrate_schema` twice on a fresh DB is a no-op.

    Fresh-DB path (`schema.sql`) already declares all columns now, so the
    migration's `ALTER TABLE ADD COLUMN` branch must skip every entry.
    Catches regressions where schema.sql and _REQUIRED_MIGRATION_COLUMNS
    drift apart and a duplicate-column error surfaces.
    """
    db_path = tmp_path / "idempotent.sqlite"
    initialize_database(db_path)
    _migrate_schema(db_path)
    # Second invocation must not raise (would raise on duplicate ADD COLUMN).
    _migrate_schema(db_path)


# ---------------------------------------------------------------------------
# T16-T17: Track 1 backward-compat regression armor
# Per bridge/gtkb-dora-001b-track1-implementation-005.md §3.2
# Per bridge/gtkb-dora-001b-track1-implementation-006.md GO condition: "Add
# the proposed writer tests and the two ingest regression tests."
# ---------------------------------------------------------------------------


def test_t16_pre_track1_manifest_still_classified_as_canonical_deploy(
    tmp_path: Path,
) -> None:
    """T16: a pre-Track-1 manifest (PASS phase 9, NO deploy_evidence block)
    must classify as `canonical_deploy` AND ingest at `_confidence='medium'`.

    Regression armor: if Track 1 ever modifies `_classify_manifest()` to require
    deploy_evidence presence for canonical_deploy classification, this test fails
    immediately. The contract is that pre-Track-1 manifests already on disk
    remain valid canonical_deploy events.
    """
    # Classification side: pre-Track-1 shape (no deploy_evidence) -> canonical_deploy
    assert (
        _classify_manifest(
            {
                "phases": [{"phase": 9, "status": "PASS"}],
            }
        )
        == "canonical_deploy"
    )

    # Ingest side: pre-Track-1 manifest -> _confidence='medium'
    _write_manifest(
        tmp_path,
        "production",
        1700000099,
        {
            "dry_run": False,
            "version": "v1.98.92",
            "environment": "production",
            "status": "SUCCESS",
            "repo_commit": "deadbeef0001",
            "started_at": "2026-04-20T00:00:00Z",
            "phases": [{"phase": 9, "status": "PASS"}],
            # Intentionally NO deploy_evidence block — pre-Track-1 shape.
        },
    )

    conn = _make_conn()
    _ingest_canonical_pipeline_manifests(conn, tmp_path)

    confidence = conn.execute("SELECT _confidence FROM delivery_timeline_events").fetchone()[0]
    assert confidence == "medium", (
        "Pre-Track-1 manifest must ingest at _confidence='medium' per "
        "Codex GO -006 condition 3 cap. If this fails, Track 1 may have "
        "introduced a confidence-contract regression for legacy manifests."
    )


def test_t17_track1_manifest_with_full_evidence_capped_at_medium_until_reconcile(
    tmp_path: Path,
) -> None:
    """T17: a Track 1 manifest with target_update_succeeded=true must still
    ingest at `_confidence='medium'` (NOT 'high'). Confidence upgrade to
    'high' is reserved for post-reconciliation when an Azure revision
    matches.

    Regression armor: this is the exact mistake `-003` made in proposing
    `_confidence='high'` for full-evidence manifests at ingest time. If this
    test ever fails, the confidence-contract has regressed in that direction.
    Per `bridge/gtkb-dora-001b-authoritative-deployment-source-007.md` §4.2,
    only Source C reconciliation may upgrade to 'high'.
    """
    _write_manifest(
        tmp_path,
        "production",
        1700000100,
        {
            "dry_run": False,
            "version": "v1.99.0",
            "environment": "production",
            "status": "SUCCESS",
            "repo_commit": "abc12345",
            "started_at": "2026-04-28T00:00:00Z",
            "phases": [{"phase": 9, "status": "PASS"}],
            "deploy_evidence": {
                "image": "acragentredeastus.azurecr.io/agent-red:v1.99.0",
                "image_tag": "v1.99.0",
                "revision_name": "agent-red-api-gateway--xyz99",
                "target_verified_at": "2026-04-28T00:01:00Z",
                "target_update_attempted": True,
                "target_update_succeeded": True,
            },
        },
    )

    conn = _make_conn()
    _ingest_canonical_pipeline_manifests(conn, tmp_path)

    confidence = conn.execute("SELECT _confidence FROM delivery_timeline_events").fetchone()[0]
    assert confidence == "medium", (
        "Full-evidence Track 1 manifests must still ingest at medium "
        "per Source A → Source C reconciliation contract; only Azure "
        "reconciliation may upgrade to high. Regression check against "
        "the confidence-contract mistake from -003."
    )
