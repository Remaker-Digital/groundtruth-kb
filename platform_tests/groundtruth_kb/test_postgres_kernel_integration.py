"""Destructive tests for one host-prepared, disposable PostgreSQL service.

This module is intentionally excluded from WI-6252's source-only selectors.
Its one approved invocation must set ``GTKB_RUN_POSTGRES_INTEGRATION=1`` and
``GTKB_TEST_POSTGRES_SERVICE``.  Missing prerequisites are failures, never
skips.  Every test uses and permanently removes a unique PostgreSQL schema.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import threading
import time
import uuid
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import groundtruth_kb.postgres_kernel as kernel_module
import psycopg
import pytest
from click.testing import CliRunner
from fastapi.testclient import TestClient
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.cli import main
from groundtruth_kb.config import GTConfig, PostgreSQLConfig
from groundtruth_kb.db_snapshot import create_snapshot
from groundtruth_kb.native_authority import AuthorityService
from groundtruth_kb.postgres_kernel import (
    ALL_TABLES,
    COORDINATION_TABLES,
    CURRENT_FORMAT,
    CURRENT_TABLES,
    FORBIDDEN_COLUMNS,
    FORBIDDEN_TABLES,
    MIGRATION_TABLES,
    REBUILT_LATER_TABLES,
    RETIRED_TABLES,
    SCHEMA_VERSION,
    SOURCE_TABLES,
    TABLE_SPECS,
    TRANSFORM_FORMAT,
    PostgresKernel,
    PostgresKernelError,
    canonical_json_bytes,
    parse_json_bytes,
)
from psycopg import sql

from platform_tests.groundtruth_kb.test_native_authority_service import put

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]

#: Always-present maintenance database, used only as the connection target for
#: CREATE/DROP DATABASE. A session cannot drop the database its own connection has open,
#: and PGDATABASE is redirected to the disposable database for the duration of a test.
_MAINTENANCE_DATABASE = "postgres"

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

assert set(CURRENT_TABLES) == EXPECTED_CURRENT_SOURCE
assert REBUILT_LATER_TABLES == EXPECTED_REBUILT_SOURCE
assert RETIRED_TABLES == EXPECTED_RETIRED_SOURCE
assert SOURCE_TABLES == EXPECTED_SOURCE_TABLES


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


def _invoke(*arguments: str) -> tuple[int, dict[str, Any], str]:
    result = CliRunner().invoke(main, list(arguments))
    try:
        payload = json.loads(result.output)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"CLI did not emit one JSON object: {result.output!r}") from exc
    assert result.output.count("\n") == 1
    assert result.output == canonical_json_bytes(payload).decode("utf-8")
    lowered = result.output.lower()
    assert not any(
        token in lowered
        for token in (
            "password=",
            "dsn=",
            "dbname=",
            "host=",
            "user=",
            "sslmode=",
            '"password":',
            '"service":',
            '"host":',
            '"user":',
        )
    )
    return result.exit_code, payload, result.output


def _empty_manifest() -> dict[str, Any]:
    return {
        "format": CURRENT_FORMAT,
        "schema_version": 1,
        "tables": {table_name: [] for table_name in MIGRATION_TABLES},
    }


def test_init_status_idempotency_exact_layout_and_drift_refusal(
    isolated_postgres: tuple[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    service, schema_name = isolated_postgres
    first_code, first, first_raw = _invoke("db", "postgres", "init")
    second_code, second, second_raw = _invoke("db", "postgres", "init")
    status_code, status, status_raw = _invoke("db", "postgres", "status")

    assert first_code == second_code == status_code == 0
    assert first["status"] == "initialized"
    assert second["status"] == "already_current"
    assert status["ready"] is True
    assert status["reachable"] is True
    assert status["missing_tables"] == status["unexpected_tables"] == []
    assert status["forbidden_tables"] == status["forbidden_columns"] == []
    assert not any(
        secret in (first_raw + second_raw + status_raw).lower()
        for secret in ("password=", "dsn=", "dbname=", "host=", "user=", "sslmode=")
    )

    with psycopg.connect(service=service, autocommit=True) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema=%s AND table_type='BASE TABLE'",
                (schema_name,),
            ).fetchall()
        }
        columns = {
            (row[0], row[1])
            for row in connection.execute(
                "SELECT table_name,column_name FROM information_schema.columns WHERE table_schema=%s",
                (schema_name,),
            ).fetchall()
        }
    assert set(ALL_TABLES) == EXPECTED_TABLES
    assert tables == EXPECTED_TABLES
    assert not (tables & FORBIDDEN_TABLES)
    assert not {column for _table, column in columns} & FORBIDDEN_COLUMNS

    with psycopg.connect(service=service, autocommit=True) as connection:
        connection.execute(
            sql.SQL("ALTER TABLE {}.projects ALTER COLUMN name DROP NOT NULL").format(sql.Identifier(schema_name))
        )
    layout_code, layout, _ = _invoke("db", "postgres", "status")
    assert layout_code == 0
    assert layout["ready"] is False
    assert layout["schema_catalog_matches"] is False
    with psycopg.connect(service=service, autocommit=True) as connection:
        connection.execute(
            sql.SQL("ALTER TABLE {}.projects ALTER COLUMN name SET NOT NULL").format(sql.Identifier(schema_name))
        )
    assert _invoke("db", "postgres", "init")[1]["status"] == "already_current"

    with psycopg.connect(service=service, autocommit=True) as connection:
        stored_comment = connection.execute(
            "SELECT obj_description(%s::regnamespace, 'pg_namespace')",
            (schema_name,),
        ).fetchone()[0]
        drifted_metadata = json.loads(stored_comment)
        assert set(drifted_metadata) == {
            "catalog_sha256",
            "format",
            "schema_sha256",
            "schema_version",
        }
        drifted_metadata["schema_sha256"] = "0" * 64
        # COMMENT ON takes no placeholders, so the comment is composed as a
        # literal rather than bound. This is the kernel's own composition in
        # postgres_kernel.py initialize(); the test exercises the pattern the
        # code under test uses instead of a second form invented here.
        connection.execute(
            sql.SQL("COMMENT ON SCHEMA {} IS {}").format(
                sql.Identifier(schema_name),
                sql.Literal(canonical_json_bytes(drifted_metadata).decode("utf-8").removesuffix("\n")),
            )
        )

    drift_code, drift, _ = _invoke("db", "postgres", "init")
    assert drift_code == 1
    assert drift["error"]["code"] == "schema_drift"

    # Status is an observer: on a fresh schema it must not create anything.
    observer_schema = f"gtkb_test_{uuid.uuid4().hex}"
    with psycopg.connect(service=service, autocommit=True) as connection:
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(observer_schema)))
    monkeypatch.setenv("PGOPTIONS", f"-c search_path={observer_schema}")
    observer_code, observer, _ = _invoke("db", "postgres", "status")
    assert observer_code == 0
    assert observer["ready"] is False
    with psycopg.connect(service=service, autocommit=True) as connection:
        assert (
            connection.execute(
                "SELECT count(*) FROM information_schema.tables WHERE table_schema=%s", (observer_schema,)
            ).fetchone()[0]
            == 0
        )
        connection.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(observer_schema)))


def test_empty_import_roundtrip_already_current_and_atomic_failure(
    isolated_postgres: tuple[str, str], tmp_path: Path
) -> None:
    service, schema_name = isolated_postgres
    assert _invoke("db", "postgres", "init")[0] == 0
    manifest_path = tmp_path / "current.json"
    manifest_bytes = canonical_json_bytes(_empty_manifest())
    manifest_path.write_bytes(manifest_bytes)

    imported_code, imported, _ = _invoke(
        "db",
        "postgres",
        "import-current",
        "--input",
        str(manifest_path),
        "--actor",
        "integration-test",
        "--reason",
        "empty round trip",
    )
    repeated_code, repeated, _ = _invoke(
        "db",
        "postgres",
        "import-current",
        "--input",
        str(manifest_path),
        "--actor",
        "integration-test",
        "--reason",
        "empty round trip",
    )
    readback_path = tmp_path / "readback.json"
    readback_code, readback, _ = _invoke("db", "postgres", "readback-current", "--output", str(readback_path))
    assert imported_code == repeated_code == readback_code == 0
    assert imported["status"] == "already_current"
    assert repeated["status"] == "already_current"
    assert readback["status"] == "ok"
    assert readback_path.read_bytes() == manifest_bytes

    # One directly injected partial current row makes a later full import fail
    # closed with no additional rows or history.
    with psycopg.connect(service=service, autocommit=True) as connection:
        connection.execute(
            sql.SQL(
                "INSERT INTO {}.test_plans "
                "(id,version,title,description,status,changed_by,changed_at,change_reason) "
                "VALUES ('PLAN-PARTIAL',1,'partial',NULL,'active','test',transaction_timestamp(),'test')"
            ).format(sql.Identifier(schema_name))
        )
    refused_code, refused, _ = _invoke(
        "db",
        "postgres",
        "import-current",
        "--input",
        str(manifest_path),
        "--actor",
        "integration-test",
        "--reason",
        "must refuse partial",
    )
    assert refused_code == 1
    assert refused["error"]["code"] == "target_not_empty"
    with psycopg.connect(service=service, autocommit=True) as connection:
        assert (
            connection.execute(
                sql.SQL("SELECT count(*) FROM {}.test_plans").format(sql.Identifier(schema_name))
            ).fetchone()[0]
            == 1
        )
        assert (
            connection.execute(
                sql.SQL("SELECT count(*) FROM {}.record_history").format(sql.Identifier(schema_name))
            ).fetchone()[0]
            == 0
        )


@pytest.mark.parametrize("occupied_table", ["session_init_bindings", "bridge_attempts"])
def test_import_refuses_an_operating_coordination_target_even_for_an_identical_empty_manifest(
    isolated_postgres: tuple[str, str], tmp_path: Path, occupied_table: str
) -> None:
    service, schema_name = isolated_postgres
    kernel = PostgresKernel(PostgreSQLConfig(service=service))
    kernel.initialize()
    with psycopg.connect(service=service) as connection:
        if occupied_table == "session_init_bindings":
            connection.execute(
                sql.SQL("INSERT INTO {}.session_init_bindings VALUES (%s,%s,%s,%s,clock_timestamp(),%s)").format(
                    sql.Identifier(schema_name)
                ),
                ("existing-context", "SENV-" + "a" * 32, "gtkb", "prime-builder", "existing-idempotency"),
            )
        else:
            connection.execute(
                sql.SQL(
                    "INSERT INTO {}.bridge_attempts (id,head_status,head_version) VALUES ('existing-advisory','ADVISORY',1)"
                ).format(sql.Identifier(schema_name))
            )
    manifest = tmp_path / "empty-current.json"
    manifest.write_bytes(canonical_json_bytes(_empty_manifest()))
    with pytest.raises(PostgresKernelError) as refused:
        kernel.import_current(input_path=manifest, actor="qualification", reason="Refuse live target")
    assert refused.value.code == "target_coordination_not_empty"
    assert refused.value.to_json_dict()["error"]["details"]["table"] == occupied_table
    with psycopg.connect(service=service) as connection:
        assert (
            connection.execute(
                sql.SQL("SELECT count(*) FROM {}.{}").format(
                    sql.Identifier(schema_name), sql.Identifier(occupied_table)
                )
            ).fetchone()[0]
            == 1
        )
        assert (
            connection.execute(
                sql.SQL("SELECT count(*) FROM {}.record_history").format(sql.Identifier(schema_name))
            ).fetchone()[0]
            == 0
        )


def test_import_waits_for_an_inflight_binding_and_reads_its_committed_state(
    isolated_postgres: tuple[str, str], tmp_path: Path
) -> None:
    service, schema_name = isolated_postgres
    kernel = PostgresKernel(PostgreSQLConfig(service=service))
    kernel.initialize()
    manifest = tmp_path / "empty-current.json"
    manifest.write_bytes(canonical_json_bytes(_empty_manifest()))
    with psycopg.connect(service=service) as writer, psycopg.connect(service=service, autocommit=True) as observer:
        writer.execute(
            sql.SQL("INSERT INTO {}.session_init_bindings VALUES (%s,%s,%s,%s,clock_timestamp(),%s)").format(
                sql.Identifier(schema_name)
            ),
            ("inflight-context", "SENV-" + "b" * 32, "gtkb", "prime-builder", "inflight-idempotency"),
        )
        with ThreadPoolExecutor(max_workers=1) as workers:
            result = workers.submit(
                kernel.import_current, input_path=manifest, actor="qualification", reason="Competing import"
            )
            waiting = False
            deadline = time.monotonic() + 10
            try:
                while time.monotonic() < deadline and not result.done():
                    waiting = observer.execute(
                        "SELECT EXISTS(SELECT 1 FROM pg_locks WHERE relation=to_regclass(%s) AND mode='ShareRowExclusiveLock' AND NOT granted)",
                        (schema_name + ".session_init_bindings",),
                    ).fetchone()[0]
                    if waiting:
                        break
                    threading.Event().wait(0.01)
            finally:
                writer.commit()
            assert waiting, "The import did not wait for the in-flight coordination writer"
            with pytest.raises(PostgresKernelError) as refused:
                result.result(timeout=10)
            assert refused.value.code == "target_coordination_not_empty"
        assert (
            observer.execute(
                sql.SQL("SELECT count(*) FROM {}.session_init_bindings").format(sql.Identifier(schema_name))
            ).fetchone()[0]
            == 1
        )
        assert (
            observer.execute(
                sql.SQL("SELECT count(*) FROM {}.record_history").format(sql.Identifier(schema_name))
            ).fetchone()[0]
            == 0
        )


def test_migrated_bindings_roundtrip_without_history_and_keep_the_original_role(
    isolated_postgres: tuple[str, str], tmp_path: Path
) -> None:
    from groundtruth_kb.bridge.native import BindSession, NativeBridgeService

    service, schema_name = isolated_postgres
    kernel = PostgresKernel(PostgreSQLConfig(service=service))
    kernel.initialize()
    original = {
        "native_context_id": "original-native",
        "session_context_id": "SENV-" + "c" * 32,
        "subject": "gtkb",
        "role": "prime-builder",
        "created_at": "2026-09-01T01:02:03.123456+00:00",
        "minimum_idempotency_identity": "original-idempotency",
    }
    manifest = _empty_manifest()
    manifest["tables"]["session_init_bindings"] = [original]
    path = tmp_path / "current.json"
    path.write_bytes(canonical_json_bytes(manifest))
    assert (
        kernel.import_current(input_path=path, actor="qualification", reason="Preserve immutable attribution")["status"]
        == "imported"
    )
    bridge = NativeBridgeService(kernel, tmp_path)
    binding = bridge.bind(BindSession(native_context_id="original-native", init_command="::init gtkb pb"))
    assert binding["status"] == "already_initialized_idempotent"
    assert binding["binding"] == original
    with pytest.raises(PostgresKernelError):
        bridge.bind(BindSession(native_context_id="original-native", init_command="::init gtkb lo"))
    assert (
        kernel.import_current(input_path=path, actor="qualification", reason="Exact retry")["status"]
        == "already_current"
    )
    readback = tmp_path / "readback.json"
    kernel.readback_current(output=readback)
    assert readback.read_bytes() == path.read_bytes()
    with psycopg.connect(service=service) as connection:
        assert (
            connection.execute(
                sql.SQL("SELECT count(*) FROM {}.record_history").format(sql.Identifier(schema_name))
            ).fetchone()[0]
            == 0
        )


def test_literal_concurrent_cas_has_one_winner_and_no_lost_update(isolated_postgres: tuple[str, str]) -> None:
    service, schema_name = isolated_postgres
    assert _invoke("db", "postgres", "init")[0] == 0
    kernel = PostgresKernel(PostgreSQLConfig(service=service))
    base = {
        "id": "PLAN-CAS",
        "version": 1,
        "title": "CAS",
        "description": None,
        "status": "active",
        "changed_by": "integration-test",
        "changed_at": "2026-09-01T00:00:00+00:00",
        "change_reason": "create",
    }
    assert (
        kernel.mutate_current(
            table="test_plans",
            identity={"id": "PLAN-CAS"},
            expected_version=0,
            new_state=base,
            actor="integration-test",
            reason="create",
        )["status"]
        == "created"
    )

    barrier = threading.Barrier(2)
    outcomes: list[str] = []
    outcome_lock = threading.Lock()

    def writer(label: str) -> None:
        state = dict(base)
        state["status"] = label
        state["change_reason"] = label
        barrier.wait()
        try:
            result = kernel.mutate_current(
                table="test_plans",
                identity={"id": "PLAN-CAS"},
                expected_version=1,
                new_state=state,
                actor=f"integration-{label}",
                reason=label,
            )
            outcome = result["status"]
        except PostgresKernelError as exc:
            outcome = exc.code
        with outcome_lock:
            outcomes.append(outcome)

    threads = [threading.Thread(target=writer, args=(label,)) for label in ("writer-a", "writer-b")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
        assert not thread.is_alive()

    assert sorted(outcomes) == ["cas_conflict", "updated"]

    config_state = {
        "id": "CONFIG-1",
        "version": 1,
        "environment": "test",
        "category": "kernel",
        "key": "mode",
        "value": "one",
        "sensitive": False,
        "notes": None,
        "changed_by": "integration-test",
        "changed_at": "2026-09-01T00:00:00+00:00",
        "change_reason": "create",
    }
    assert (
        kernel.mutate_current(
            table="environment_config",
            identity={"id": "CONFIG-1"},
            expected_version=0,
            new_state=config_state,
            actor="integration-test",
            reason="create",
        )["status"]
        == "created"
    )
    duplicate_config = dict(config_state)
    duplicate_config["id"] = "CONFIG-2"
    with pytest.raises(PostgresKernelError) as duplicate_error:
        kernel.mutate_current(
            table="environment_config",
            identity={"id": "CONFIG-2"},
            expected_version=0,
            new_state=duplicate_config,
            actor="integration-test",
            reason="duplicate business key",
        )
    assert duplicate_error.value.code == "retryable_conflict"

    with psycopg.connect(service=service, autocommit=True) as connection:
        row = connection.execute(
            sql.SQL("SELECT version,status FROM {}.test_plans WHERE id='PLAN-CAS'").format(sql.Identifier(schema_name))
        ).fetchone()
        history = connection.execute(
            sql.SQL("SELECT prior_version,new_version FROM {}.record_history WHERE record_type='test_plans'").format(
                sql.Identifier(schema_name)
            )
        ).fetchall()
        environment_count = connection.execute(
            sql.SQL("SELECT count(*) FROM {}.environment_config").format(sql.Identifier(schema_name))
        ).fetchone()[0]
        environment_history_count = connection.execute(
            sql.SQL("SELECT count(*) FROM {}.record_history WHERE record_type='environment_config'").format(
                sql.Identifier(schema_name)
            )
        ).fetchone()[0]
    assert row[0] == 2
    assert row[1] in {"writer-a", "writer-b"}
    # The first element is None on the initial transition, and Python 3 refuses
    # to order None against int. The key reproduces the ordering the expected
    # value already encodes: one None -> 1 transition, then 1 -> 2.
    assert sorted(history, key=lambda t: (t[0] is not None, t[0], t[1])) == [(None, 1), (1, 2)]
    assert environment_count == environment_history_count == 1


def test_import_rolls_back_an_injected_mid_transaction_failure(
    isolated_postgres: tuple[str, str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service, schema_name = isolated_postgres
    assert _invoke("db", "postgres", "init")[0] == 0
    manifest = _empty_manifest()
    spec = TABLE_SPECS["test_plans"]
    rows = []
    for suffix in ("A", "B"):
        values = {
            "id": f"PLAN-{suffix}",
            "version": 1,
            "title": f"Plan {suffix}",
            "description": None,
            "status": "active",
            "changed_by": "integration-test",
            "changed_at": "2026-09-01T00:00:00+00:00",
            "change_reason": "rollback fixture",
        }
        rows.append({column: values.get(column) for column in spec.columns})
    manifest["tables"]["test_plans"] = rows
    manifest_path = tmp_path / "rollback-manifest.json"
    manifest_path.write_bytes(canonical_json_bytes(manifest))

    original = PostgresKernel._adapt_value
    call_count = 0

    def injected(column: str, value: object, table_spec: object) -> object:
        nonlocal call_count
        call_count += 1
        if call_count > len(spec.columns):
            raise RuntimeError("injected after first current row")
        return original(column, value, table_spec)  # type: ignore[arg-type]

    monkeypatch.setattr(PostgresKernel, "_adapt_value", staticmethod(injected))
    code, payload, _ = _invoke(
        "db",
        "postgres",
        "import-current",
        "--input",
        str(manifest_path),
        "--actor",
        "integration-test",
        "--reason",
        "rollback injection",
    )
    assert code == 1
    assert payload["error"]["code"] == "postgres_operation_failed"
    with psycopg.connect(service=service, autocommit=True) as connection:
        assert (
            connection.execute(
                sql.SQL("SELECT count(*) FROM {}.test_plans").format(sql.Identifier(schema_name))
            ).fetchone()[0]
            == 0
        )
        assert (
            connection.execute(
                sql.SQL("SELECT count(*) FROM {}.record_history").format(sql.Identifier(schema_name))
            ).fetchone()[0]
            == 0
        )


def _work_model_rows(open_parents: int) -> dict[str, list[dict[str, object]]]:
    """Two execution projects, one closed work item with two active parents (recorded history), and one
    open work item with ``open_parents`` active parents; every column of each table spec is present."""
    from groundtruth_kb.postgres_kernel import TABLE_SPECS

    metadata = {
        "version": 1,
        "changed_by": "test",
        "changed_at": "2026-09-01T00:00:00+00:00",
        "change_reason": "fixture",
    }

    def row(table: str, **values: object) -> dict[str, object]:
        return {column: {**metadata, **values}.get(column) for column in TABLE_SPECS[table].columns}

    projects = [
        row("projects", id=pid, name=pid, kind="project", status="active", authorization="authorized")
        for pid in ("PROJECT-ONE", "PROJECT-TWO")
    ]
    work_items = [
        row(
            "work_items",
            id="WI-CLOSED",
            title="Closed history",
            origin="owner",
            component="kernel",
            resolution_status="resolved",
            stage="created",
        ),
        row(
            "work_items",
            id="WI-OPEN",
            title="Open work",
            origin="owner",
            component="kernel",
            resolution_status="open",
            stage="created",
        ),
    ]
    memberships = [
        row(
            "project_work_item_memberships",
            id="M-CLOSED-ONE",
            project_id="PROJECT-ONE",
            work_item_id="WI-CLOSED",
            status="active",
        ),
        row(
            "project_work_item_memberships",
            id="M-CLOSED-TWO",
            project_id="PROJECT-TWO",
            work_item_id="WI-CLOSED",
            status="active",
        ),
        row(
            "project_work_item_memberships",
            id="M-OPEN-ONE",
            project_id="PROJECT-ONE",
            work_item_id="WI-OPEN",
            status="active",
        ),
    ]
    if open_parents == 2:
        memberships.append(
            row(
                "project_work_item_memberships",
                id="M-OPEN-TWO",
                project_id="PROJECT-TWO",
                work_item_id="WI-OPEN",
                status="active",
            )
        )
    return {"projects": projects, "work_items": work_items, "project_work_item_memberships": memberships}


def test_closed_history_with_several_active_parents_imports_and_open_work_keeps_one(
    isolated_postgres: tuple[str, str], tmp_path: Path
) -> None:
    """Owner decision 2026-09-10: closed work migrates with its recorded membership history exactly, so the
    schema carries no uniqueness over every work item's active membership; exactly one active parent per
    OPEN work item is enforced by the validator on import and readback (and by the native service's
    membership writes), and the packaged schema stays declarative."""
    service, schema_name = isolated_postgres
    code, payload, _ = _invoke("db", "postgres", "init")
    assert code == 0 and payload["status"] == "initialized", payload

    refused_manifest = _empty_manifest()
    refused_manifest["tables"].update(_work_model_rows(open_parents=2))
    refused_path = tmp_path / "refused.json"
    refused_path.write_bytes(canonical_json_bytes(refused_manifest))
    refused_code, refused, _ = _invoke(
        "db", "postgres", "import-current", "--input", str(refused_path), "--actor", "test", "--reason", "must refuse"
    )
    assert refused_code == 1 and refused["error"]["code"] == "invalid_manifest", refused
    assert "open work item" in refused["error"]["message"]

    manifest = _empty_manifest()
    manifest["tables"].update(_work_model_rows(open_parents=1))
    manifest_bytes = canonical_json_bytes(manifest)
    manifest_path = tmp_path / "current.json"
    manifest_path.write_bytes(manifest_bytes)
    imported_code, imported, _ = _invoke(
        "db",
        "postgres",
        "import-current",
        "--input",
        str(manifest_path),
        "--actor",
        "test",
        "--reason",
        "closed history",
    )
    assert imported_code == 0 and imported["status"] == "imported" and imported["row_count"] == 7, imported
    readback_path = tmp_path / "readback.json"
    readback_code, readback, _ = _invoke("db", "postgres", "readback-current", "--output", str(readback_path))
    assert readback_code == 0 and readback["status"] == "ok"
    assert readback_path.read_bytes() == manifest_bytes
    with psycopg.connect(service=service, autocommit=True) as connection:
        counts = connection.execute(
            sql.SQL(
                "SELECT work_item_id, count(*)::int FROM {}.project_work_item_memberships"
                " WHERE status = 'active' GROUP BY 1 ORDER BY 1"
            ).format(sql.Identifier(schema_name))
        ).fetchall()
        assert counts == [("WI-CLOSED", 2), ("WI-OPEN", 1)]
        procedural = connection.execute(
            "SELECT count(*) FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid"
            " JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = %s AND NOT t.tgisinternal",
            (schema_name,),
        ).fetchone()[0]
        assert procedural == 0
    status_code, status, _ = _invoke("db", "postgres", "status")
    assert status_code == 0 and status["ready"] is True and status["schema_catalog_matches"] is True, status


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


def test_snapshot_wal_export_authorization_dependency_and_immutable_boundaries(
    isolated_postgres: tuple[str, str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, schema_name = isolated_postgres
    monkeypatch.delenv("GT_DB_PATH", raising=False)
    source = tmp_path / "source.db"
    writer = _create_sqlite_fixture(source)
    for status in ("removed", "retired", "moved", "superseded", "completed", "excluded", "rehomed"):
        writer.execute(
            "INSERT INTO project_work_item_memberships VALUES (?,?,?,?,?,?,?,?)",
            (
                "HISTORICAL-" + status,
                3,
                "PROJECT-A",
                "WI-OPAQUE",
                status,
                "integration",
                "2026-09-01T00:00:00+00:00",
                "old parent association",
            ),
        )
    writer.commit()
    config = tmp_path / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\ndb_path="{source.as_posix()}"\nproject_root="{tmp_path.as_posix()}"\n'
        "[backup]\ninclude_chroma=false\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "snapshots"
    staging_dir = tmp_path / "staging"
    output_dir.mkdir()
    staging_dir.mkdir()
    try:
        # Migration owns this explicit SQLite source snapshot; ordinary domain
        # CLI operations no longer expose SQLite backup/fallback routes.
        snapshot_result = create_snapshot(
            GTConfig(db_path=source, project_root=tmp_path),
            output_dir=output_dir,
            staging_dir=staging_dir,
            retain_recent=1,
            retain_daily_days=0,
            include_chroma=False,
        )
        snapshot_payload = snapshot_result.to_json_dict()
        assert snapshot_payload["status"] == "ok"
        assert snapshot_payload["method"] == "vacuum"
        assert snapshot_payload["integrity_result"] == "ok"
        snapshot = Path(snapshot_payload["final_path"])
        assert not snapshot.with_name(snapshot.name + "-wal").exists()
        assert not snapshot.with_name(snapshot.name + "-shm").exists()
        preflight_code, preflight_source, _ = _invoke(
            "--config",
            str(config),
            "db",
            "postgres",
            "export-current",
            "--sqlite-snapshot",
            str(snapshot),
            "--preflight-only",
        )
        assert preflight_code == 0
        assert set(preflight_source) == {
            "expected_pragma_user_version",
            "expected_table_inventory_sha256",
            "sqlite_snapshot_sha256",
            "sqlite_snapshot_size_bytes",
        }

        plan = {
            "format": TRANSFORM_FORMAT,
            "project_dependencies": {
                "affected_gate_from": "authorization",
                "affected_gate_to": "readiness",
                "expected_active_after": 1,
                "expected_gate_transition_count": 1,
                "expected_retired_after": 1,
                "expected_source_count": 2,
                "preserve_dependency_ids": ["opaque-preserve"],
                "retire_dependency_ids": ["opaque-retire"],
            },
            "projects": {
                "expected_programs": 0,
                "expected_authorized": 1,
                "expected_not_authorized": 1,
                "expected_total": 2,
            },
            "schema_version": 1,
            "source": preflight_source,
        }
        plan_path = tmp_path / "plan.json"
        plan_path.write_bytes(canonical_json_bytes(plan))

        def refused_export(
            label: str,
            candidate_plan: dict[str, Any],
            expected_code: str,
            *,
            candidate_snapshot: Path = snapshot,
        ) -> None:
            candidate_plan_path = tmp_path / f"{label}-plan.json"
            candidate_plan_path.write_bytes(canonical_json_bytes(candidate_plan))
            candidate_output = tmp_path / f"{label}-must-not-exist.json"
            candidate_code, candidate_payload, _ = _invoke(
                "--config",
                str(config),
                "db",
                "postgres",
                "export-current",
                "--sqlite-snapshot",
                str(candidate_snapshot),
                "--transform-plan",
                str(candidate_plan_path),
                "--output",
                str(candidate_output),
            )
            assert candidate_code == 1
            assert candidate_payload["error"]["code"] == expected_code
            assert not candidate_output.exists()

        refused_export("live-source", plan, "live_source_forbidden", candidate_snapshot=source)

        wrong_hash = json.loads(json.dumps(plan))
        wrong_hash["source"]["sqlite_snapshot_sha256"] = "0" * 64
        refused_export("wrong-hash", wrong_hash, "snapshot_preimage_mismatch")

        wrong_size = json.loads(json.dumps(plan))
        wrong_size["source"]["sqlite_snapshot_size_bytes"] += 1
        refused_export("wrong-size", wrong_size, "snapshot_preimage_mismatch")

        wrong_user_version = json.loads(json.dumps(plan))
        wrong_user_version["source"]["expected_pragma_user_version"] = 8
        refused_export("wrong-user-version", wrong_user_version, "snapshot_user_version_mismatch")

        wrong_inventory = json.loads(json.dumps(plan))
        wrong_inventory["source"]["expected_table_inventory_sha256"] = "0" * 64
        refused_export("wrong-inventory", wrong_inventory, "snapshot_inventory_mismatch")

        wrong_authorization_count = json.loads(json.dumps(plan))
        wrong_authorization_count["projects"]["expected_authorized"] = 2
        wrong_authorization_count["projects"]["expected_not_authorized"] = 0
        refused_export(
            "wrong-authorization-count",
            wrong_authorization_count,
            "transform_precondition_failed",
        )

        original_hash_file = kernel_module._hash_file
        hash_calls = 0

        def changed_after_open(path: Path) -> str:
            nonlocal hash_calls
            hash_calls += 1
            digest = original_hash_file(path)
            return digest if hash_calls == 1 else ("f" * 64 if digest != "f" * 64 else "e" * 64)

        with monkeypatch.context() as changed_context:
            changed_context.setattr(kernel_module, "_hash_file", changed_after_open)
            refused_export("changed-during-read", plan, "snapshot_changed")

        manifest_path = tmp_path / "manifest.json"
        code, exported, _ = _invoke(
            "--config",
            str(config),
            "db",
            "postgres",
            "export-current",
            "--sqlite-snapshot",
            str(snapshot),
            "--transform-plan",
            str(plan_path),
            "--output",
            str(manifest_path),
        )
        assert code == 0
        assert exported["status"] == "ok"
        manifest = parse_json_bytes(manifest_path.read_bytes())
        project_statuses = {row["id"]: row["authorization"] for row in manifest["tables"]["projects"]}
        assert project_statuses == {
            "PROJECT-A": "authorized",
            "PROJECT-GTKB-NEW-WORK-INTAKE": "not authorized",
        }
        dependency_rows = {row["id"]: row for row in manifest["tables"]["project_dependencies"]}
        assert set(dependency_rows) == {"opaque-preserve", "opaque-retire"}
        assert dependency_rows["opaque-preserve"]["affected_gate"] == "readiness"
        assert dependency_rows["opaque-retire"]["status"] == "retired"
        assert manifest["tables"]["specifications"][0]["title"] == "Current spec"
        current_spec = manifest["tables"]["specifications"][0]
        assert {
            key: current_spec[key]
            for key in (
                "type",
                "authority",
                "constraints",
                "affected_by",
                "testability",
                "source_paths",
                "application_scope",
            )
        } == {
            "type": "architecture_decision",
            "authority": "stated",
            "constraints": {"atomic": True},
            "affected_by": [],
            "testability": "observable",
            "source_paths": ["groundtruth-kb/src/groundtruth_kb/db.py"],
            "application_scope": "gtkb_platform",
        }
        assert manifest["tables"]["tests"][0]["application_scope"] == "gtkb_platform"
        assert manifest["tables"]["tests"][0]["last_executed_at"] is None
        assert manifest["tables"]["tests"][0]["last_executed_on"] == "2026-03-04"
        assert canonical_json_bytes(manifest["tables"]["specifications"][0]["tags"]) == (
            b"[0.123456789012345678901234567890,100,0.0]\n"
        )
        assert manifest["tables"]["specification_deliberation_sources"] == [
            {
                "added_at": "2026-09-01T00:00:00+00:00",
                "added_by": "integration",
                "deliberation_id": "DELIB-1",
                "source_role": "current",
                "spec_id": "SPEC-1",
                "version": 1,
            }
        ]
        assert manifest["tables"]["environment_config"][0]["sensitive"] is True
        assert manifest["tables"]["work_items"][0]["depends_on_work_items"] == []
        assert "related_bridge_threads" not in manifest["tables"]["work_items"][0]
        assert [row["id"] for row in manifest["tables"]["project_work_item_memberships"]] == ["MEMBER-OPAQUE"]
        assert writer.execute("SELECT COUNT(*) FROM project_work_item_memberships").fetchone()[0] == 8
        assert (
            next(row for row in manifest["tables"]["projects"] if row["id"] == "PROJECT-A")["start_date"]
            == "2026-09-01"
        )
        assert all(row["version"] == 1 for table in CURRENT_TABLES for row in manifest["tables"][table])
        assert manifest["tables"]["session_init_bindings"] == [
            {
                "native_context_id": "native-context-original",
                "session_context_id": "SENV-" + "d" * 32,
                "subject": "gtkb",
                "role": "prime-builder",
                "created_at": "2026-09-01T01:02:03.456789+00:00",
                "minimum_idempotency_identity": "original-idempotency",
            }
        ]

        assert _invoke("db", "postgres", "init")[0] == 0
        import_code, imported, _ = _invoke(
            "db",
            "postgres",
            "import-current",
            "--input",
            str(manifest_path),
            "--actor",
            "integration-test",
            "--reason",
            "nonempty current-state round trip",
        )
        assert import_code == 0
        assert imported["status"] == "imported"
        postgres_readback = tmp_path / "postgres-readback.json"
        readback_code, readback, _ = _invoke("db", "postgres", "readback-current", "--output", str(postgres_readback))
        assert readback_code == 0
        assert readback["status"] == "ok"
        assert postgres_readback.read_bytes() == manifest_path.read_bytes()
        repeated_code, repeated, _ = _invoke(
            "db",
            "postgres",
            "import-current",
            "--input",
            str(manifest_path),
            "--actor",
            "integration-test",
            "--reason",
            "nonempty current-state round trip",
        )
        assert repeated_code == 0
        assert repeated["status"] == "already_current"
        with psycopg.connect(service=service, autocommit=True) as connection:
            history_before = connection.execute(
                sql.SQL("SELECT count(*) FROM {}.record_history").format(sql.Identifier(schema_name))
            ).fetchone()[0]
            row_count_before = connection.execute(
                sql.SQL("SELECT count(*) FROM {}.projects").format(sql.Identifier(schema_name))
            ).fetchone()[0]
            with pytest.raises(psycopg.errors.CheckViolation):
                connection.execute(
                    sql.SQL("UPDATE {}.tests SET last_executed_at='2026-03-04T12:00:00Z' WHERE id='TEST-1'").format(
                        sql.Identifier(schema_name)
                    )
                )
            stored = connection.execute(
                sql.SQL("SELECT last_executed_at,last_executed_on FROM {}.tests WHERE id='TEST-1'").format(
                    sql.Identifier(schema_name)
                )
            ).fetchone()
            assert stored[0] is None and stored[1].isoformat() == "2026-03-04"
        assert history_before == 11  # Includes TEST and parent membership; immutable binding adds no history.

        different_manifest = parse_json_bytes(manifest_path.read_bytes())
        next(row for row in different_manifest["tables"]["projects"] if row["id"] == "PROJECT-A")["name"] = (
            "Different current state"
        )
        different_path = tmp_path / "different-manifest.json"
        different_path.write_bytes(canonical_json_bytes(different_manifest))
        different_code, different, _ = _invoke(
            "db",
            "postgres",
            "import-current",
            "--input",
            str(different_path),
            "--actor",
            "integration-test",
            "--reason",
            "different target refusal",
        )
        assert different_code == 1
        assert different["error"]["code"] == "target_not_empty"
        with psycopg.connect(service=service, autocommit=True) as connection:
            assert (
                connection.execute(
                    sql.SQL("SELECT count(*) FROM {}.record_history").format(sql.Identifier(schema_name))
                ).fetchone()[0]
                == history_before
            )
            assert (
                connection.execute(
                    sql.SQL("SELECT count(*) FROM {}.projects").format(sql.Identifier(schema_name))
                ).fetchone()[0]
                == row_count_before
            )

        for suffix in ("-wal", "-shm"):
            sidecar = snapshot.parent / f"{snapshot.name}{suffix}"
            sidecar.write_bytes(b"forbidden")
            refused_export(f"sidecar-{suffix[1:]}", plan, "snapshot_sidecar_present")
            sidecar.unlink()
    finally:
        writer.close()


class TestPublicSchemaCommentInitialization:
    """WI-7690: a table-free ``public`` schema carrying only PostgreSQL's stock comment is an
    uninitialized target, not kernel metadata drift.

    The module's ``isolated_postgres`` fixture always creates a randomly named schema, so it can
    never reach the ``public`` case this class exists to cover. These cases therefore create a
    uniquely named disposable DATABASE, verify its identity and stock preconditions before any
    effect, and drop only that exact database afterwards. Per the reviewed conditions they never
    adopt, clear, or drop a pre-existing database, and never terminate foreign sessions.
    """

    STOCK_PUBLIC_COMMENT = "standard public schema"

    @pytest.fixture
    def disposable_database(self, monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[str, str]]:
        service = _required_service()
        database_name = f"gtkb_wi7690_{uuid.uuid4().hex}"
        created = False
        # Maintenance connections pin dbname explicitly: CREATE/DROP DATABASE cannot run from a
        # session whose own connection has the target database open, and PGDATABASE is redirected
        # to the disposable database for the duration of the test.
        with psycopg.connect(service=service, dbname=_MAINTENANCE_DATABASE, autocommit=True) as connection:
            existing = connection.execute("SELECT 1 FROM pg_database WHERE datname=%s", (database_name,)).fetchone()
            if existing is not None:
                pytest.fail("refusing to adopt a pre-existing database; the unique name collided")
            connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
            created = True
        try:
            # Cleanup protection begins immediately after successful creation.
            monkeypatch.setenv("GT_POSTGRES_SERVICE", service)
            monkeypatch.setenv("PGDATABASE", database_name)
            monkeypatch.delenv("PGOPTIONS", raising=False)
            with psycopg.connect(service=service, dbname=database_name, autocommit=True) as connection:
                selected = connection.execute("SELECT current_database(), current_schema()").fetchone()
                if selected[0] != database_name:
                    pytest.fail("the libpq service overrides PGDATABASE; refusing an unisolated run")
                if selected[1] != "public":
                    pytest.fail("a freshly created database must select the public schema")
                comment = connection.execute(
                    "SELECT obj_description(oid, 'pg_namespace') AS comment "
                    "FROM pg_catalog.pg_namespace WHERE nspname='public'"
                ).fetchone()[0]
                if comment != self.STOCK_PUBLIC_COMMENT:
                    pytest.skip(f"server public-schema comment is {comment!r}, not the stock string")
                tables = connection.execute(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_type='BASE TABLE'"
                ).fetchone()[0]
                if tables:
                    pytest.fail("a freshly created database must have no base tables in public")
            yield service, database_name
        finally:
            if created:
                with psycopg.connect(service=service, dbname=_MAINTENANCE_DATABASE, autocommit=True) as connection:
                    connection.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(database_name)))
                # Prove exact-database absence here rather than via request.addfinalizer.
                # Finalizers run LIFO, so one registered inside a test body would execute
                # BEFORE this teardown and could only ever observe the database still present.
                self._assert_database_absent(service, database_name)

    @staticmethod
    def _assert_database_absent(service: str, database_name: str) -> None:
        with psycopg.connect(service=service, dbname=_MAINTENANCE_DATABASE, autocommit=True) as connection:
            remaining = connection.execute("SELECT 1 FROM pg_database WHERE datname=%s", (database_name,)).fetchone()
        assert remaining is None, "the exact disposable database must not survive the case"

    def test_stock_public_schema_initializes_instead_of_reporting_drift(
        self, disposable_database: tuple[str, str]
    ) -> None:
        """The repair: initialization proceeds rather than refusing the stock comment as drift."""
        _service, _database_name = disposable_database
        exit_code, payload, _raw = _invoke("db", "postgres", "init")
        assert exit_code == 0, payload
        assert payload["status"] == "initialized"
        assert payload["schema_version"] == SCHEMA_VERSION
        assert payload["table_count"] == len(ALL_TABLES)

    def test_initialization_is_idempotent_on_the_stock_public_schema(
        self, disposable_database: tuple[str, str]
    ) -> None:
        _service, _database_name = disposable_database
        first_code, first, _raw = _invoke("db", "postgres", "init")
        assert first_code == 0 and first["status"] == "initialized"
        second_code, second, _raw2 = _invoke("db", "postgres", "init")
        assert second_code == 0
        assert second["status"] == "already_current"
        assert second["schema_sha256"] == first["schema_sha256"]

    def test_the_exact_disposable_database_is_absent_after_success(self, disposable_database: tuple[str, str]) -> None:
        """Success path plus cleanup proof.

        The absence assertion itself lives in the fixture teardown, which is the only point
        that runs after the drop. This case establishes the precondition that teardown proves
        something: the exact database exists and carries the initialized kernel while the test
        is running, so the subsequent drop and absence check are not vacuous.
        """
        service, database_name = disposable_database
        exit_code, payload, _raw = _invoke("db", "postgres", "init")
        assert exit_code == 0 and payload["status"] == "initialized"
        with psycopg.connect(service=service, autocommit=True) as connection:
            present = connection.execute("SELECT 1 FROM pg_database WHERE datname=%s", (database_name,)).fetchone()
        assert present is not None, "the disposable database must exist before teardown drops it"


# Explicit transition from the installed repository/scope predecessor.
PREDECESSOR = "2f25071544591b01b44e0da491a19bd9adee509627114a4dad528205a8f6e2ca"


def predecessor_sql():
    """Reconstruct the exact measured predecessor; the hash prevents a moving fixture."""
    current = kernel_module.schema_sql_bytes()
    new_scope = (
        b"application_scope TEXT CHECK (application_scope ~ '^(gtkb_platform|application:[A-Za-z][A-Za-z0-9_-]*)$')"
    )
    old_scope = b"application_scope TEXT CHECK (application_scope IN ('gtkb_platform', 'agent_red_application'))"
    assert current.count(new_scope) == 2
    current = current.replace(new_scope, old_scope)
    lines = current.splitlines(keepends=True)
    assert sum(line.startswith(b"    repository_ref TEXT CHECK") for line in lines) == 1
    current = b"".join(line for line in lines if not line.startswith(b"    repository_ref TEXT CHECK"))
    assert current.count(b" AND repository_ref IS NULL") == 1
    current = current.replace(b" AND repository_ref IS NULL", b"")
    assert hashlib.sha256(current).hexdigest() == PREDECESSOR
    return current


@pytest.fixture
def predecessor(isolated_postgres, monkeypatch):
    service, schema = isolated_postgres
    kernel = PostgresKernel(PostgreSQLConfig(service=service))
    old_sql = predecessor_sql()
    with monkeypatch.context() as patch:
        patch.setattr(kernel_module, "schema_sql_bytes", lambda: old_sql)
        patch.setattr(kernel_module, "schema_sql_sha256", lambda: PREDECESSOR)
        kernel.initialize()
    with psycopg.connect(service=service) as connection:
        connection.execute(
            'INSERT INTO projects(id,version,name,kind,"authorization",changed_by,changed_at,change_reason) '
            "VALUES ('PROGRAM-EXISTING',3,'Existing program','program',NULL,'fixture',now(),'Existing state'),"
            "('PROJECT-EXISTING',7,'Existing project','project','authorized','fixture',now(),'Existing state')"
        )
        connection.execute(
            "INSERT INTO specifications(id,version,title,status,application_scope,changed_by,changed_at,change_reason) "
            "VALUES ('SPEC-EXISTING',4,'Existing requirement','active',NULL,'fixture',now(),'Existing state')"
        )
        connection.execute(
            "INSERT INTO record_history(record_type,record_id,prior_version,new_version,prior_state,new_state,"
            "actor,changed_at,reason) SELECT 'projects',jsonb_build_object('id',id),version-1,version,"
            "jsonb_build_object('id',id,'version',version-1),to_jsonb(p),'fixture',now(),'Preserve historical payload' "
            "FROM projects p"
        )
    return kernel, service, schema


def snapshot(service):
    with psycopg.connect(service=service) as connection:
        rows = {}
        for table in ALL_TABLES:
            rows[table] = connection.execute(
                sql.SQL("SELECT to_jsonb(t) FROM {} t ORDER BY to_jsonb(t)::text").format(sql.Identifier(table))
            ).fetchall()
        comment = connection.execute("SELECT obj_description(current_schema()::regnamespace,'pg_namespace')").fetchone()
        columns = connection.execute(
            "SELECT table_name,column_name,ordinal_position FROM information_schema.columns "
            "WHERE table_schema=current_schema() ORDER BY table_name,ordinal_position"
        ).fetchall()
        return {"rows": rows, "comment": comment, "columns": columns}


def test_ordinary_initialization_still_refuses_the_supported_predecessor(predecessor):
    kernel, service, _ = predecessor
    before = snapshot(service)
    with pytest.raises(PostgresKernelError) as error:
        kernel.initialize()
    assert error.value.code == "schema_drift"
    assert snapshot(service) == before


def test_explicit_transition_preserves_versions_history_and_unresolved_repository(predecessor):
    kernel, service, _ = predecessor
    before = snapshot(service)
    result = kernel.upgrade_schema(expected_schema_sha256=PREDECESSOR)
    assert result["status"] == "upgraded"
    assert result["unresolved_project_repositories"] == 1
    assert result["schema_sha256"] == kernel_module.schema_sql_sha256()
    after = snapshot(service)
    for row in after["rows"]["projects"]:
        assert row[0].pop("repository_ref") is None
    assert after["rows"] == before["rows"]
    assert kernel.status()["ready"] is True
    assert kernel.initialize()["status"] == "already_current"
    settled = snapshot(service)
    assert kernel.upgrade_schema(expected_schema_sha256=PREDECESSOR)["status"] == "already_current"
    assert snapshot(service) == settled
    with TestClient(create_authority_app(AuthorityService(kernel))) as client:
        project = client.get("/v1/projects/PROJECT-EXISTING")
        assert project.status_code == 200
        assert project.json()["project"]["repository_ref"] is None and project.json()["project"]["version"] == 7


@pytest.mark.parametrize("domain", ["specifications", "tests"])
@pytest.mark.parametrize("name", ["Alpha", "Beta"])
def test_upgraded_schema_accepts_native_catalog_scopes_with_existing_history(predecessor, tmp_path, domain, name):
    kernel, service, _ = predecessor
    history = snapshot(service)["rows"]["record_history"]
    kernel.upgrade_schema(expected_schema_sha256=PREDECESSOR)
    host = tmp_path / "host"
    (host / "applications").mkdir(parents=True)
    (host / "applications/registry.toml").write_text(
        '[applications]\nAlpha={slot="Alpha"}\nBeta={slot="Beta"}\n', encoding="utf-8"
    )
    with TestClient(create_authority_app(AuthorityService(kernel), project_root=host)) as client:
        fields = {"title": "Current scoped record", "application_scope": "application:" + name}
        if domain == "tests":
            fields.update(spec_id="SPEC-EXISTING", test_type="integration", expected_outcome="Current contract")
        response = put(client, domain, "CURRENT-" + name, fields)
        assert response.status_code == 200, response.text
        assert response.json()["application_scope"] == "application:" + name
        before = snapshot(service)
        refused = put(client, domain, "RETIRED-MARKER", {**fields, "application_scope": "agent_red_application"})
        assert refused.status_code == 422
        assert snapshot(service) == before
    current_history = snapshot(service)["rows"]["record_history"]
    assert all(row in current_history for row in history)


@pytest.mark.parametrize("record_id,reference", [("PROGRAM-EXISTING", "platform"), ("PROJECT-EXISTING", "../outside")])
def test_upgraded_program_and_repository_constraints_reject_invalid_rows(predecessor, record_id, reference):
    kernel, service, _ = predecessor
    kernel.upgrade_schema(expected_schema_sha256=PREDECESSOR)
    before = snapshot(service)
    with pytest.raises(psycopg.errors.CheckViolation), psycopg.connect(service=service) as connection:
        connection.execute("UPDATE projects SET repository_ref=%s WHERE id=%s", (reference, record_id))
    assert snapshot(service) == before


def test_current_schema_and_empty_schema_use_their_declared_initialization_paths(isolated_postgres):
    service, _ = isolated_postgres
    kernel = PostgresKernel(PostgreSQLConfig(service=service))
    with pytest.raises(PostgresKernelError) as error:
        kernel.upgrade_schema(expected_schema_sha256=PREDECESSOR)
    assert error.value.code == "schema_upgrade_preimage_mismatch"
    assert kernel.initialize()["status"] == "initialized"
    before = snapshot(service)
    assert kernel.upgrade_schema(expected_schema_sha256=PREDECESSOR)["status"] == "already_current"
    assert snapshot(service) == before


@pytest.mark.parametrize("change", ["column", "metadata", "metadata-shape"])
def test_unknown_or_drifted_catalog_is_refused_without_repair(predecessor, change):
    kernel, service, schema = predecessor
    with psycopg.connect(service=service) as connection:
        if change == "column":
            connection.execute("ALTER TABLE projects ADD COLUMN unreviewed TEXT")
        else:
            metadata = json.loads(
                connection.execute("SELECT obj_description(current_schema()::regnamespace,'pg_namespace')").fetchone()[
                    0
                ]
            )
            if change == "metadata":
                metadata["schema_sha256"] = "f" * 64
            else:
                metadata["extra"] = "unrecognized"
            connection.execute(
                sql.SQL("COMMENT ON SCHEMA {} IS {}").format(sql.Identifier(schema), sql.Literal(json.dumps(metadata)))
            )
    before = snapshot(service)
    with pytest.raises(PostgresKernelError) as error:
        kernel.upgrade_schema(expected_schema_sha256=PREDECESSOR)
    assert error.value.code == "schema_upgrade_preimage_mismatch"
    assert snapshot(service) == before


def test_unknown_requested_predecessor_never_opens_a_connection(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Unsupported upgrade attempted a database connection")

    monkeypatch.setattr(PostgresKernel, "_connect", forbidden)
    with pytest.raises(PostgresKernelError) as error:
        PostgresKernel(PostgreSQLConfig(service="unused")).upgrade_schema(expected_schema_sha256="0" * 64)
    assert error.value.code == "unsupported_schema_upgrade"


def test_legacy_scope_requires_explicit_record_reconciliation_before_ddl(predecessor):
    kernel, service, _ = predecessor
    with psycopg.connect(service=service) as connection:
        connection.execute(
            "UPDATE specifications SET application_scope='agent_red_application' WHERE id='SPEC-EXISTING'"
        )
    before = snapshot(service)
    with pytest.raises(PostgresKernelError) as error:
        kernel.upgrade_schema(expected_schema_sha256=PREDECESSOR)
    assert error.value.code == "application_scope_reconciliation_required"
    assert error.value.details == {"specifications": ["SPEC-EXISTING"], "tests": []}
    assert snapshot(service) == before


def test_failure_after_ddl_rolls_back_columns_constraints_metadata_and_rows(predecessor, monkeypatch):
    kernel, service, _ = predecessor
    before = snapshot(service)

    def refuse(*args, **kwargs):
        raise PostgresKernelError("qualification_injected", "Refuse final schema readback")

    monkeypatch.setattr(PostgresKernel, "_require_exact_schema", refuse)
    with pytest.raises(PostgresKernelError) as error:
        kernel.upgrade_schema(expected_schema_sha256=PREDECESSOR)
    assert error.value.code == "qualification_injected"
    assert snapshot(service) == before


def test_held_write_lock_refuses_boundedly_without_partial_ddl(predecessor):
    _, service, _ = predecessor
    kernel = PostgresKernel(PostgreSQLConfig(service=service, lock_timeout_ms=100))
    before = snapshot(service)
    with psycopg.connect(service=service) as blocker:
        blocker.execute("LOCK TABLE projects IN ROW EXCLUSIVE MODE")
        with pytest.raises(PostgresKernelError) as error:
            kernel.upgrade_schema(expected_schema_sha256=PREDECESSOR)
        assert error.value.code == "retryable_conflict"
    assert snapshot(service) == before


def test_concurrent_explicit_transitions_have_one_effect_and_idempotent_readback(predecessor):
    kernel, service, _ = predecessor
    history = snapshot(service)["rows"]["record_history"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: kernel.upgrade_schema(expected_schema_sha256=PREDECESSOR), range(2)))
    assert sorted(row["status"] for row in results) == ["already_current", "upgraded"]
    assert snapshot(service)["rows"]["record_history"] == history
    assert kernel.status()["ready"] is True


def test_ordinary_cli_process_uses_explicit_predecessor_and_reports_unresolved_rows(predecessor, tmp_path):
    _, service, _ = predecessor
    config = tmp_path / "selected.toml"
    config.write_text(f'[postgresql]\nservice="{service}"\n', encoding="utf-8")
    run = subprocess.run(
        [
            sys.executable,
            "-P",
            "-m",
            "groundtruth_kb",
            "--config",
            str(config),
            "db",
            "postgres",
            "init",
            "--upgrade-from",
            PREDECESSOR,
        ],
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        timeout=40,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    result = json.loads(run.stdout)
    assert result["status"] == "upgraded" and result["unresolved_project_repositories"] == 1
    assert run.stdout == canonical_json_bytes(result).decode("utf-8")
