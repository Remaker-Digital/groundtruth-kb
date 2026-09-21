"""Shared fixtures and helpers of the PostgreSQL kernel qualification (c102, Q-3, owner ruling D23).

Moved verbatim from ``test_postgres_kernel_integration.py`` (the expected table sets, the
``isolated_postgres`` fixture and the SQLite source fixture builder) and
``test_postgres_export_source_set.py`` (``snapshot``, ``preflight``) so that no test module
imports another test module. Not collected; defines no test.
"""

from __future__ import annotations

import os
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import psycopg
import pytest
from groundtruth_kb.config import PostgreSQLConfig
from groundtruth_kb.postgres_kernel import COORDINATION_TABLES, PostgresKernel
from psycopg import sql

EXPECTED_TABLES = {
    "canonical_terms",
    "deliberation_specs",
    "deliberation_work_items",
    "deliberations",
    "documents",
    "environment_config",
    "harnesses",
    "operational_procedures",
    "project_artifact_links",
    "project_dependencies",
    "project_work_item_memberships",
    "projects",
    "record_history",
    "specification_deliberation_sources",
    "specifications",
    "test_plan_phases",
    "test_plans",
    "test_procedures",
    "testable_elements",
    "tests",
    "work_items",
    "session_init_bindings",
    "bridge_attempts",
    "bridge_items",
    "work_intent_claims",
}
EXPECTED_CURRENT_SOURCE = EXPECTED_TABLES - {"record_history", *COORDINATION_TABLES}
EXPECTED_REBUILT_SOURCE = {
    "assertion_runs",
    "pipeline_events",
    "sot_quarantine_receipts",
    "work_intent_claims",
}
EXPECTED_RETIRED_SOURCE = {
    "sot_artifact_revisions",
    "sot_artifacts",
    "sot_registry_transaction_journal",
    "dispatch_default_metric_events",
    "dispatch_default_metrics_snapshots",
    "dispatch_lane_matrix",
    "dispatch_lane_projection_metadata",
    "emergency_bootstrap_operational_event_tombstones",
    "emergency_bootstrap_operational_events",
    "governed_operational_events",
    "operational_event_tombstones",
    "operational_event_versions",
    "operational_events",
    "session_context_envelope_terminal_facts",
    "session_context_envelopes",
    "session_role_attestations",
    "sot_registry_bridge_publication_capabilities",
    "sot_registry_bridge_recovery_receipts",
    "sot_registry_transition_requests",
    "test_artifact_update_requests",
    "agent_capability_snapshots",
    "backlog_snapshots",
    "dispatch_events",
    "dispatch_lane_projection_snapshots",
    "dispatch_lane_score_dimensions",
    "dispatch_lane_score_snapshots",
    "dispatch_lane_scoring_evidence",
    "dispatch_lanes",
    "flow_artifacts",
    "flow_definitions",
    "flow_events",
    "flow_instances",
    "project_authorizations",
    "quality_scores",
    "session_prompts",
    "session_snapshots",
    "sot_registry_observation_capabilities",
    "spec_quality_scores",
    "stage_attempt_telemetry",
    "stage_instances",
    "stage_leases",
    "test_coverage",
}
EXPECTED_SOURCE_TABLES = (
    EXPECTED_CURRENT_SOURCE | EXPECTED_REBUILT_SOURCE | EXPECTED_RETIRED_SOURCE | {"session_init_bindings"}
)


def _required_service() -> str:
    if os.environ.get("GTKB_RUN_POSTGRES_INTEGRATION") != "1":
        pytest.fail("set GTKB_RUN_POSTGRES_INTEGRATION=1 for the reviewed disposable-PostgreSQL operation")
    service = os.environ.get("GTKB_TEST_POSTGRES_SERVICE")
    if not service:
        pytest.fail("GTKB_TEST_POSTGRES_SERVICE must name the host-prepared disposable libpq service")
    return service


@pytest.fixture
def isolated_postgres(monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[str, str]]:
    service = _required_service()
    schema_name = f"gtkb_test_{uuid.uuid4().hex}"
    with psycopg.connect(service=service, autocommit=True) as connection:
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema_name)))
    monkeypatch.setenv("GT_POSTGRES_SERVICE", service)
    monkeypatch.setenv("PGOPTIONS", f"-c search_path={schema_name}")
    try:
        with psycopg.connect(service=service, autocommit=True) as connection:
            selected_schema = connection.execute("SELECT current_schema()").fetchone()[0]
        if selected_schema != schema_name:
            pytest.fail("The disposable libpq service overrides PGOPTIONS; refusing an unisolated integration run")
        yield service, schema_name
    finally:
        with psycopg.connect(service=service, autocommit=True) as connection:
            connection.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema_name)))


def _create_sqlite_fixture(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA wal_autocheckpoint=0")
    for table_name in sorted(EXPECTED_SOURCE_TABLES):
        if table_name == "session_init_bindings":
            definition = "native_context_id TEXT PRIMARY KEY, session_context_id TEXT UNIQUE, subject TEXT, role TEXT, created_at TEXT, minimum_idempotency_identity TEXT"
        elif table_name == "specifications":
            definition = (
                "id TEXT, version INTEGER, title TEXT, status TEXT, tags TEXT, changed_by TEXT, "
                "changed_at TEXT, change_reason TEXT"
            )
        elif table_name == "tests":
            definition = (
                "id TEXT, version INTEGER, title TEXT, spec_id TEXT, test_type TEXT, "
                "expected_outcome TEXT, application_scope TEXT, changed_by TEXT, changed_at TEXT, change_reason TEXT"
            )
        elif table_name == "deliberations":
            definition = (
                "id TEXT, version INTEGER, source_type TEXT, title TEXT, summary TEXT, content TEXT, "
                "changed_by TEXT, changed_at TEXT, change_reason TEXT"
            )
        elif table_name == "specification_deliberation_sources":
            definition = (
                "spec_id TEXT, deliberation_id TEXT, spec_version INTEGER, "
                "source_role TEXT, added_at TEXT, added_by TEXT"
            )
        elif table_name == "environment_config":
            definition = (
                "id TEXT, version INTEGER, environment TEXT, category TEXT, key TEXT, value TEXT, "
                "sensitive INTEGER, changed_by TEXT, changed_at TEXT, change_reason TEXT"
            )
        elif table_name == "work_items":
            definition = (
                "id TEXT, version INTEGER, title TEXT, origin TEXT, component TEXT, resolution_status TEXT, "
                "stage TEXT, depends_on_work_items TEXT, changed_by TEXT, changed_at TEXT, change_reason TEXT, "
                "related_bridge_threads TEXT"
            )
        elif table_name == "projects":
            definition = (
                "id TEXT, version INTEGER, name TEXT, kind TEXT, authorization TEXT, status TEXT, start_date TEXT, changed_by TEXT, "
                "changed_at TEXT, change_reason TEXT"
            )
        elif table_name == "project_work_item_memberships":
            definition = (
                "id TEXT, version INTEGER, project_id TEXT, work_item_id TEXT, status TEXT, "
                "changed_by TEXT, changed_at TEXT, change_reason TEXT"
            )
        elif table_name == "project_dependencies":
            definition = (
                "id TEXT, version INTEGER, dependent_project_id TEXT, prerequisite_project_id TEXT, "
                "dependency_kind TEXT, required_prerequisite_state TEXT, affected_gate TEXT, provenance TEXT, "
                "registry_version INTEGER, blocking_status TEXT, status TEXT, changed_by TEXT, changed_at TEXT, "
                "change_reason TEXT, rationale TEXT"
            )
        else:
            definition = "marker TEXT"
        connection.execute(f'CREATE TABLE "{table_name}" ({definition})')
    connection.execute(
        "INSERT INTO session_init_bindings VALUES (?,?,?,?,?,?)",
        (
            "native-context-original",
            "SENV-" + "d" * 32,
            "gtkb",
            "prime-builder",
            "2026-09-01T01:02:03.456789+00:00",
            "original-idempotency",
        ),
    )
    connection.execute("PRAGMA user_version=7")
    connection.commit()
    connection.execute("INSERT INTO session_prompts(marker) VALUES ('wal-visible-marker')")
    connection.execute(
        "INSERT INTO specifications VALUES "
        "('SPEC-1',1,'Historical spec','active','[]','integration',"
        "'2026-08-31T00:00:00+00:00','fixture'),"
        "('SPEC-1',2,'Current spec','active','[0.123456789012345678901234567890,1e2,-0.0]',"
        "'integration','2026-09-01T00:00:00+00:00','fixture')"
    )
    for column in (
        "type",
        "authority",
        "provisional_until",
        "constraints",
        "affected_by",
        "testability",
        "source_paths",
        "application_scope",
    ):
        connection.execute(f'ALTER TABLE specifications ADD COLUMN "{column}" TEXT')
    connection.execute(
        "UPDATE specifications SET type=?,authority=?,constraints=?,affected_by=?,testability=?,source_paths=?,application_scope=? WHERE version=2",
        (
            "architecture_decision",
            "stated",
            '{"atomic":true}',
            "[]",
            "observable",
            '["groundtruth-kb/src/groundtruth_kb/db.py"]',
            "gtkb_platform",
        ),
    )
    connection.execute(
        "INSERT INTO tests VALUES ('TEST-1',1,'Behavior','SPEC-1','integration','Current behavior is preserved',"
        "'gtkb_platform','integration','2026-09-01T00:00:00+00:00','fixture')"
    )
    connection.execute("ALTER TABLE tests ADD COLUMN last_executed_at TEXT")
    connection.execute("UPDATE tests SET last_executed_at='2026-03-04' WHERE id='TEST-1'")
    connection.execute(
        "INSERT INTO deliberations VALUES "
        "('DELIB-1',1,'integration','Deliberation','Summary','Content','integration',"
        "'2026-09-01T00:00:00+00:00','fixture')"
    )
    connection.execute(
        "INSERT INTO specification_deliberation_sources VALUES "
        "('SPEC-1','DELIB-1',1,'historical','2026-08-31T00:00:00+00:00','integration'),"
        "('SPEC-1','DELIB-1',2,'current','2026-09-01T00:00:00+00:00','integration')"
    )
    connection.execute(
        "INSERT INTO environment_config VALUES "
        "('CONFIG-1',1,'test','kernel','mode','shadow',1,'integration',"
        "'2026-09-01T00:00:00+00:00','fixture')"
    )
    connection.execute(
        "INSERT INTO work_items VALUES "
        "('WI-OPAQUE',1,'Opaque work','owner','kernel','open','created','[]','integration',"
        "'2026-09-01T00:00:00+00:00','fixture','[bridge/obsolete-payload-001.md]')"
    )
    connection.execute(
        "INSERT INTO projects VALUES "
        "('PROJECT-A',1,'A','project','authorized','active','2026-09-01','integration','2026-09-01T00:00:00+00:00','fixture')"
    )
    connection.execute(
        "INSERT INTO project_work_item_memberships VALUES "
        "('MEMBER-OPAQUE',1,'PROJECT-A','WI-OPAQUE','active','integration','2026-09-01T00:00:00+00:00','fixture')"
    )
    connection.execute(
        "INSERT INTO projects VALUES "
        "('PROJECT-GTKB-NEW-WORK-INTAKE',1,'Intake','project','not authorized','active',NULL,'integration',"
        "'2026-09-01T00:00:00+00:00','fixture')"
    )
    connection.execute(
        "INSERT INTO project_dependencies VALUES "
        "('opaque-preserve',1,'PROJECT-A','PROJECT-GTKB-NEW-WORK-INTAKE','requires_project_state','retired',"
        "'authorization','integration',1,'open','active','integration','2026-09-01T00:00:00+00:00','fixture','Wait for the required retirement outcome')"
    )
    connection.execute(
        "INSERT INTO project_dependencies VALUES "
        "('opaque-retire',1,'PROJECT-GTKB-NEW-WORK-INTAKE','PROJECT-A','requires_project_state','retired',"
        "'readiness','integration',1,'open','active','integration','2026-09-01T00:00:00+00:00','fixture','Obsolete reverse ordering to retire')"
    )
    connection.commit()
    return connection


def snapshot(path: Path, tables: set[str]) -> Path:
    with sqlite3.connect(path) as connection:
        for table in sorted(tables):
            connection.execute(f'CREATE TABLE "{table}" (marker TEXT)')
    return path


def preflight(path: Path):
    def no_postgres(**_kwargs):
        raise AssertionError("Source classification must not contact PostgreSQL")

    kernel = PostgresKernel(PostgreSQLConfig(service="unused"), connector=no_postgres)
    return kernel.preflight_export_current(sqlite_snapshot=path, live_sqlite_source=None)
