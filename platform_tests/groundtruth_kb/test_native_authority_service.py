"""Behavioral qualification on an explicitly selected disposable PostgreSQL.

Exercises native domain transactions, concurrent changes, HTTP validation and
separate ordinary CLI processes with no PostgreSQL credentials in their env.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from threading import Event
from uuid import uuid4

import groundtruth_kb
import psycopg
import pytest
from fastapi.testclient import TestClient
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import PostgreSQLConfig
from groundtruth_kb.native_authority import AuthorityService, WorkItemMutation
from groundtruth_kb.postgres_kernel import (
    TABLE_SPECS,
    PostgresKernel,
    PostgresKernelError,
    PostgresTransaction,
    canonical_json_bytes,
    parse_json_bytes,
)
from psycopg import sql

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


@pytest.fixture
def native(monkeypatch):
    if os.environ.get("GTKB_RUN_POSTGRES_INTEGRATION") != "1":
        pytest.fail("Explicitly select a disposable PostgreSQL installation")
    service_name = os.environ.get("GTKB_TEST_POSTGRES_SERVICE")
    if not service_name:
        pytest.fail("GTKB_TEST_POSTGRES_SERVICE is required")
    # Every CLI/service child must use the same package as the parent test.
    # This also preserves installed-package isolation in a separate checkout.
    monkeypatch.setenv("PYTHONPATH", str(Path(groundtruth_kb.__file__).resolve().parent.parent))
    schema = f"gtkb_test_{uuid4().hex}"
    with psycopg.connect(service=service_name, autocommit=True) as connection:
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
    monkeypatch.setenv("PGOPTIONS", f"-c search_path={schema}")
    try:
        with psycopg.connect(service=service_name) as connection:
            assert connection.execute("SELECT current_schema()").fetchone()[0] == schema
        kernel = PostgresKernel(PostgreSQLConfig(service=service_name))
        kernel.initialize()
        service = AuthorityService(kernel)
        with TestClient(create_authority_app(service)) as client:
            yield service, client, schema, service_name
    finally:
        with psycopg.connect(service=service_name, autocommit=True) as connection:
            connection.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))


def put(client, domain, record_id, fields, *, expected_version=0, **extra):
    return client.put(
        f"/v1/{domain}/{record_id}",
        json={
            "expected_version": expected_version,
            "actor": "qualification",
            "reason": "Exercise native domain behavior",
            "fields": fields,
            **extra,
        },
    )


@pytest.mark.parametrize("column", ["formal_roots", "terminal_author_session_context_id"])
def test_an_older_v1_bridge_catalog_cannot_start_or_serve_as_current(native, column):
    service, _, schema, service_name = native
    with psycopg.connect(service=service_name) as connection:
        connection.execute(
            sql.SQL("ALTER TABLE {}.bridge_attempts DROP COLUMN {}").format(
                sql.Identifier(schema), sql.Identifier(column)
            )
        )
    with pytest.raises(PostgresKernelError) as startup:
        service.kernel.initialize()
    assert startup.value.code == "schema_drift"
    with pytest.raises(PostgresKernelError) as serving, service.kernel.transaction(read_only=True):
        pytest.fail("An older schema must not serve current operations")
    assert serving.value.code == "schema_drift"
    with psycopg.connect(service=service_name) as connection:
        columns = [
            row[0]
            for row in connection.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND table_name='bridge_attempts'",
                (schema,),
            )
        ]
        assert column not in columns  # No guessed backfill or silent schema upgrade.


def seed(client):
    inputs = [
        (
            "specifications",
            "SPEC-1",
            {"title": "Required effect", "description": "Preserve complete work", "status": "active"},
            {},
        ),
        (
            "tests",
            "TEST-1",
            {
                "title": "Effect test",
                "spec_id": "SPEC-1",
                "test_type": "integration",
                "test_file": "tests/test_effect.py",
                "expected_outcome": "Effect observed",
            },
            {},
        ),
        ("test-plans", "PLAN-1", {"title": "Behavioral qualification"}, {}),
        (
            "test-phases",
            "PHASE-1",
            {
                "title": "Native effects",
                "plan_id": "PLAN-1",
                "phase_order": 10,
                "gate_criteria": "Observable result",
                "test_ids": ["TEST-1"],
            },
            {},
        ),
        ("projects", "PROGRAM-1", {"name": "Coherent platform"}, {"kind": "program"}),
        (
            "projects",
            "PROJECT-1",
            {
                "name": "Complete outcome",
                "parent_project_id": "PROGRAM-1",
                "target_outcome": "Complete native authority",
            },
            {},
        ),
        ("projects", "PROJECT-GTKB-NEW-WORK-INTAKE", {"name": "Standing intake"}, {}),
    ]
    for domain, record_id, fields, extra in inputs:
        result = put(client, domain, record_id, fields, **extra)
        assert result.status_code == 200, result.text


def work_fields(**extra):
    return {"title": "Artifact correction", "source_spec_id": "SPEC-1", "source_test_id": "TEST-1", **extra}


def history_count(service):
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(sql.SQL("SELECT count(*) AS n FROM {}.record_history").format(sql.Identifier(tx.schema)))
        return tx.cursor.fetchone()["n"]


def test_harness_installation_reads_current_metadata_without_role_or_history_writes(native, monkeypatch):
    service, client, _, _ = native
    for harness_id, status in [("A", "active"), ("B", "active"), ("C", "suspended")]:
        row = {column: None for column in TABLE_SPECS["harnesses"].columns}
        row.update(
            id=harness_id,
            version=1,
            harness_name=f"installation-{harness_id}",
            harness_type="qualification",
            status=status,
            invocation_surfaces={"headless": {"argv": [sys.executable]}},
            changed_at=datetime.now(UTC).isoformat(),
            changed_by="qualification",
            change_reason="Isolated metadata",
        )
        service.kernel.mutate_current(
            table="harnesses",
            identity={"id": harness_id},
            expected_version=0,
            new_state=row,
            actor="qualification",
            reason="Isolated metadata",
        )
    before = history_count(service)

    def no_sqlite(*args, **kwargs):
        pytest.fail("Native harness reads must not use SQLite")

    monkeypatch.setattr("sqlite3.connect", no_sqlite)
    first = client.get("/v1/harnesses", params={"status": "active", "limit": 1})
    assert first.status_code == 200, first.text
    assert [row["id"] for row in first.json()["records"]] == ["A"]
    second = client.get("/v1/harnesses", params={"status": "active", "after": first.json()["next_after"]})
    assert second.status_code == 200 and [row["id"] for row in second.json()["records"]] == ["B"]
    assert second.json()["next_after"] is None
    current = client.get("/v1/harnesses/A")
    assert current.status_code == 200 and current.json()["harness_name"] == "installation-A"
    assert not {"role", "reviewer_precedence", "can_receive_dispatch", "event_driven_hooks"} & current.json().keys()
    assert client.get("/v1/harnesses", params={"role": "lo"}).status_code == 422
    assert client.get("/v1/harnesses/missing").status_code == 404
    # The native harness record path exists (phase M) but a role is never a harness field: the boundary refuses it
    # and neither the row nor its history changes.
    refused = client.put(
        "/v1/harnesses/A",
        json={"expected_version": 1, "actor": "qualification", "reason": "role write", "fields": {"role": "lo"}},
    )
    assert refused.status_code == 422, refused.text
    assert client.get("/v1/harnesses/A").json()["version"] == 1
    assert history_count(service) == before


def test_registry_path_inventory_reads_typed_current_fields_without_history_writes(native):
    service, client, _schema, _service_name = native
    seed(client)
    updated = put(
        client,
        "specifications",
        "SPEC-1",
        {
            "source_paths": ["src/current.py", "src/current.py"],
            "description": "Narrative mention of src/not-an-inventory-path.py",
        },
        expected_version=1,
    )
    assert updated.status_code == 200, updated.text
    for table, fields in (
        (
            "documents",
            {
                "id": "DOC-1",
                "title": "Reference",
                "category": "reference",
                "status": "active",
                "source_path": "docs/reference.md",
            },
        ),
        (
            "project_artifact_links",
            {
                "id": "LINK-1",
                "project_id": "PROJECT-1",
                "artifact_type": "file",
                "artifact_ref": "src/linked.py",
                "relationship": "implements",
                "status": "active",
            },
        ),
        (
            "project_artifact_links",
            {
                "id": "LINK-2",
                "project_id": "PROJECT-1",
                "artifact_type": "file",
                "artifact_ref": "src/obsolete.py",
                "relationship": "implements",
                "status": "retired",
            },
        ),
    ):
        row = {column: None for column in TABLE_SPECS[table].columns}
        row.update(
            fields,
            version=1,
            changed_at=datetime.now(UTC).isoformat(),
            changed_by="qualification",
            change_reason="Typed inventory fixture",
        )
        service.kernel.mutate_current(
            table=table,
            identity={"id": row["id"]},
            expected_version=0,
            new_state=row,
            actor="qualification",
            reason="Typed inventory fixture",
        )
    before = history_count(service)

    response = client.get("/v1/registry/path-observations")

    assert response.status_code == 200, response.text
    rows = response.json()
    assert {row["path"] for row in rows} == {
        "src/current.py",
        "tests/test_effect.py",
        "docs/reference.md",
        "src/linked.py",
    }
    assert len(rows) == 4
    assert all(set(row) == {"path", "source_kind", "source_id", "field"} for row in rows)
    assert history_count(service) == before


def test_registry_path_inventory_does_not_truncate_at_one_domain_page(native):
    service, client, _schema, _service_name = native
    with service.kernel.transaction() as tx:
        for index in range(1001):
            row = {column: None for column in TABLE_SPECS["documents"].columns}
            row.update(
                id=f"DOC-{index:04}",
                version=1,
                title="Reference",
                category="reference",
                status="active",
                source_path=f"docs/{index:04}.md",
                changed_at=datetime.now(UTC).isoformat(),
                changed_by="qualification",
                change_reason="Complete inventory fixture",
            )
            tx.mutate(
                table="documents",
                identity={"id": row["id"]},
                expected_version=0,
                new_state=row,
                actor="qualification",
                reason="Complete inventory fixture",
            )
    before = history_count(service)
    response = client.get("/v1/registry/path-observations")
    assert response.status_code == 200, response.text
    rows = response.json()
    assert len(rows) == 1001
    assert rows[-1]["path"] == "docs/1000.md"
    assert history_count(service) == before


def test_registry_path_inventory_reads_one_snapshot_during_concurrent_changes(native, monkeypatch):
    service, client, _schema, _service_name = native
    seed(client)
    assert (
        put(client, "specifications", "SPEC-1", {"source_paths": ["src/old.py"]}, expected_version=1).status_code == 200
    )
    started, changed = Event(), Event()
    original_list = PostgresTransaction.list

    def pause_after_specifications(tx, table, **kwargs):
        rows = original_list(tx, table, **kwargs)
        if table == "specifications" and not started.is_set():
            started.set()
            assert changed.wait(15), "Concurrent path changes did not finish"
        return rows

    monkeypatch.setattr(PostgresTransaction, "list", pause_after_specifications)
    with ThreadPoolExecutor(max_workers=1) as workers:
        reading = workers.submit(client.get, "/v1/registry/path-observations")
        try:
            assert started.wait(15)
            assert (
                put(
                    client, "specifications", "SPEC-1", {"source_paths": ["src/new.py"]}, expected_version=2
                ).status_code
                == 200
            )
            assert (
                put(client, "tests", "TEST-1", {"test_file": "tests/test_new.py"}, expected_version=1).status_code
                == 200
            )
        finally:
            changed.set()
        response = reading.result(timeout=15)
    assert response.status_code == 200, response.text
    assert {row["path"] for row in response.json()} == {"src/old.py", "tests/test_effect.py"}
    before = history_count(service)
    fresh = client.get("/v1/registry/path-observations")
    assert {row["path"] for row in fresh.json()} == {"src/new.py", "tests/test_new.py"}
    assert history_count(service) == before


def link_project_formal(service, spec_id):
    """Set up an existing canonical relationship, without a second test registry."""
    row = {column: None for column in TABLE_SPECS["project_artifact_links"].columns}
    row.update(
        id=f"LINK-{spec_id}",
        version=1,
        project_id="PROJECT-1",
        artifact_type="spec",
        artifact_ref=spec_id,
        relationship="governs",
        status="active",
        changed_at=datetime.now(UTC).isoformat(),
        changed_by="qualification",
        change_reason="Current project requirement",
    )
    service.kernel.mutate_current(
        table="project_artifact_links",
        identity={"id": row["id"]},
        expected_version=0,
        new_state=row,
        actor="qualification",
        reason="Current project requirement",
    )


def test_atomic_membership_and_program_semantics(native):
    service, client, _, _ = native
    seed(client)
    program = client.get("/v1/projects/PROGRAM-1").json()["project"]
    assert program["kind"] == "program" and program["authorization"] is None
    bad = put(client, "work-items", "WI-1", work_fields(), project_id="PROGRAM-1")
    assert bad.status_code == 422
    assert bad.json()["error"]["code"] == "program_cannot_contain_work"
    assert client.get("/v1/work-items/WI-1").status_code == 404
    result = put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1")
    assert result.status_code == 200, result.text
    initial = result.json()["membership"]
    request = {
        "expected_version": initial["version"],
        "source_project_id": "PROJECT-1",
        "destination_project_id": "PROJECT-GTKB-NEW-WORK-INTAKE",
        "actor": "another-context",
        "reason": "Move work without changing authorization",
        "membership_order": 20,
    }
    before = history_count(service)
    # The source removal is already written in the transaction when destination
    # normalization rejects this out-of-range order. Both changes must roll back.
    invalid_order = client.post("/v1/work-items/WI-1/move", json={**request, "membership_order": 2**63})
    assert invalid_order.status_code == 422
    assert history_count(service) == before
    assert client.get("/v1/work-items/WI-1").json()["membership"] == initial
    result = client.post("/v1/work-items/WI-1/move", json=request)
    assert result.status_code == 200, result.text
    assert history_count(service) == before + 2
    current = result.json()["membership"]
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["authorization"] == "authorized"
    assert (
        client.get("/v1/projects/PROJECT-GTKB-NEW-WORK-INTAKE").json()["project"]["authorization"] == "not authorized"
    )
    # A stale replay produces no membership or history mutation.
    stale = client.post("/v1/work-items/WI-1/move", json=request)
    assert stale.status_code == 409
    assert history_count(service) == before + 2
    request.update(
        source_project_id=request["destination_project_id"],
        destination_project_id="PROJECT-1",
        expected_version=current["version"],
    )
    back = client.post("/v1/work-items/WI-1/move", json=request)
    assert back.status_code == 200, back.text
    assert back.json()["membership"]["id"] == initial["id"]
    assert back.json()["membership"]["version"] == 3


def test_failed_domain_change_leaves_no_partial_work_or_history(native):
    service, client, _, _ = native
    seed(client)
    before = history_count(service)
    missing = put(client, "work-items", "WI-INVALID", work_fields(title=None), project_id="PROJECT-1")
    assert missing.status_code == 422
    assert history_count(service) == before
    assert client.get("/v1/work-items/WI-INVALID").status_code == 404
    result = put(
        client,
        "tests",
        "TEST-NO-PHASE",
        {
            "title": "Not scheduled",
            "spec_id": "SPEC-1",
            "test_type": "unit",
            "test_file": "test_missing.py",
            "expected_outcome": "Required effect",
        },
    )
    assert result.status_code == 200
    before = history_count(service)
    refused = put(
        client, "work-items", "WI-NO-PHASE", work_fields(source_test_id="TEST-NO-PHASE"), project_id="PROJECT-1"
    )
    assert refused.status_code == 422
    assert refused.json()["error"]["code"] == "test_phase_required"
    assert history_count(service) == before
    # The current record remains byte-for-byte unchanged after a stale amendment.
    before_record = client.get("/v1/specifications/SPEC-1").content
    refusal = put(client, "specifications", "SPEC-1", {"title": "stale"})
    assert refusal.status_code == 409
    assert client.get("/v1/specifications/SPEC-1").content == before_record


def test_concurrent_creation_and_dependency_write_skew(native):
    service, client, _, _ = native
    seed(client)
    request = WorkItemMutation(
        expected_version=0, actor="worker", reason="New work", project_id="PROJECT-1", fields=work_fields()
    )

    def create():
        try:
            return service.amend_work_item("WI-1", request)
        except PostgresKernelError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as workers:
        outcomes = list(workers.map(lambda _: create(), range(2)))
    assert sum(isinstance(value, dict) for value in outcomes) == 1
    assert any(value in ("cas_conflict", "retryable_conflict") for value in outcomes if isinstance(value, str))
    assert put(client, "work-items", "WI-2", work_fields(), project_id="PROJECT-1").status_code == 200

    def depend(pair):
        own, other = pair
        try:
            return service.amend_work_item(
                own,
                WorkItemMutation(
                    expected_version=1,
                    actor="worker",
                    reason="Sequence related effects",
                    fields={"depends_on_work_items": [other]},
                ),
            )
        except PostgresKernelError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as workers:
        outcomes = list(workers.map(depend, [("WI-1", "WI-2"), ("WI-2", "WI-1")]))
    assert sum(isinstance(value, dict) for value in outcomes) == 1
    assert any(value in ("dependency_cycle", "retryable_conflict") for value in outcomes if isinstance(value, str))


def test_work_item_dependency_replacement_refuses_invalid_graph_without_partial_effects(native):
    service, client, _, _ = native
    seed(client)
    for item in ("WI-1", "WI-2"):
        assert put(client, "work-items", item, work_fields(), project_id="PROJECT-1").status_code == 200
    for dependencies, code in (
        (["MISSING"], "missing_work_item_dependency"),
        (["WI-2", "WI-2"], "duplicate_work_item_dependency"),
        (["WI-1"], "dependency_cycle"),
    ):
        before = client.get("/v1/work-items/WI-1").content
        count = history_count(service)
        refused = put(client, "work-items", "WI-1", {"depends_on_work_items": dependencies}, expected_version=1)
        assert refused.json()["error"]["code"] == code, refused.text
        assert "WI-1" in str(refused.json()["error"]["details"])
        assert client.get("/v1/work-items/WI-1").content == before
        assert history_count(service) == count
    result = put(client, "work-items", "WI-1", {"depends_on_work_items": ["WI-2"]}, expected_version=1)
    assert result.status_code == 200, result.text
    assert [row["id"] for row in client.get("/v1/work-items/WI-1/context").json()["predecessors"]] == ["WI-2"]
    before = history_count(service)
    refused = put(client, "work-items", "WI-2", {"depends_on_work_items": ["WI-1"]}, expected_version=1)
    assert refused.json()["error"]["code"] == "dependency_cycle"
    assert history_count(service) == before
    result = put(client, "work-items", "WI-1", {"depends_on_work_items": []}, expected_version=2)
    assert result.status_code == 200, result.text
    assert client.get("/v1/work-items/WI-1/context").json()["predecessors"] == []


def test_transport_rejects_foreign_authority_fields_and_preserves_json_precision(native):
    _, client, _, _ = native
    seed(client)
    before = client.get("/v1/projects/PROJECT-1").content
    for fields in ({"authorization": "not authorized"}, {"status": "verified"}, {"pauth_id": "obsolete"}):
        result = put(client, "projects", "PROJECT-1", fields, expected_version=1)
        assert result.status_code == 422
    assert client.get("/v1/projects/PROJECT-1").content == before
    refused = client.put("/v1/projects/PROJECT-1", json={"secret": "do-not-echo"})
    assert refused.status_code == 422 and "do-not-echo" not in refused.text
    assert client.get("/v1/projects", headers={"Origin": "https://unrelated.example"}).status_code == 403
    for query in ("?ignored_filter=value", "?status=active&status=retired"):
        refused = client.get("/v1/projects" + query)
        assert refused.status_code == 422
        assert refused.json()["error"]["code"] == "invalid_query"
    assert client.post("/v1/work-items/WI-1/move", content="{}").status_code == 415
    number = Decimal("0.123456789012345678901234567890123456789")
    body = {
        "expected_version": 1,
        "actor": "worker",
        "reason": "Preserve exact threshold",
        "fields": {"constraints": {"threshold": number}},
    }
    amended = client.put(
        "/v1/specifications/SPEC-1", content=canonical_json_bytes(body), headers={"Content-Type": "application/json"}
    )
    assert amended.status_code == 200, amended.text
    assert parse_json_bytes(amended.content)["constraints"]["threshold"] == number
    duplicate = client.put(
        "/v1/specifications/SPEC-1",
        content=b'{"expected_version":1,"expected_version":2}',
        headers={"Content-Type": "application/json"},
    )
    assert duplicate.status_code == 400


def test_fresh_task_context_uses_current_canon_and_rejects_retired_source(native):
    _, client, _, _ = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    initial = client.get("/v1/work-items/WI-1/context")
    assert initial.status_code == 200
    assert initial.json()["program"]["id"] == "PROGRAM-1"
    assert initial.json()["test"]["id"] == "TEST-1"
    assert (
        put(
            client, "specifications", "SPEC-1", {"description": "Owner's current direction"}, expected_version=1
        ).status_code
        == 200
    )
    fresh = client.get("/v1/work-items/WI-1/context").json()
    assert fresh["specifications"][0]["description"] == "Owner's current direction"
    assert fresh["specifications"][0]["version"] == 2
    assert fresh["work_item"]["origin"] == "manual"
    assert put(client, "specifications", "SPEC-1", {"status": "retired"}, expected_version=2).status_code == 200
    refused = client.get("/v1/work-items/WI-1/context")
    assert refused.status_code == 422
    assert refused.json()["error"]["code"] == "inactive_context_source"


def test_task_context_loads_transitive_formals_and_current_test_instructions(native):
    service, client, _, _ = native
    seed(client)
    for key in ("GOV-ROOT", "GOV-MIDDLE", "SPEC-PARENT", "SPEC-TEST", "SPEC-PROJECT"):
        assert put(client, "specifications", key, {"title": key, "status": "active"}).status_code == 200
    for key, fields in (
        ("GOV-MIDDLE", {"affected_by": ["GOV-ROOT"]}),
        ("GOV-ROOT", {"affected_by": ["GOV-MIDDLE"]}),
        ("SPEC-1", {"affected_by": ["GOV-MIDDLE"], "parent": "SPEC-PARENT"}),
        ("SPEC-PROJECT", {"affected_by": ["GOV-ROOT"]}),
    ):
        assert put(client, "specifications", key, fields, expected_version=1).status_code == 200
    assert put(client, "tests", "TEST-1", {"spec_id": "SPEC-TEST"}, expected_version=1).status_code == 200
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    link_project_formal(service, "SPEC-PROJECT")
    before = history_count(service)

    result = client.get("/v1/work-items/WI-1/context")
    assert result.status_code == 200, result.text
    context = result.json()
    assert [row["id"] for row in context["specifications"]] == [
        "GOV-MIDDLE",
        "GOV-ROOT",
        "SPEC-1",
        "SPEC-PARENT",
        "SPEC-PROJECT",
        "SPEC-TEST",
    ]
    assert context["test"]["spec_id"] == "SPEC-TEST"
    assert [row["id"] for row in context["test_phases"]] == ["PHASE-1"]
    assert context["test_phases"][0]["gate_criteria"] == "Observable result"
    assert [row["id"] for row in context["test_plans"]] == ["PLAN-1"]
    assert history_count(service) == before

    assert (
        put(
            client, "test-phases", "PHASE-1", {"gate_criteria": "Corrected observable result"}, expected_version=1
        ).status_code
        == 200
    )
    fresh = client.get("/v1/work-items/WI-1/context").json()
    assert fresh["test_phases"][0]["gate_criteria"] == "Corrected observable result"
    assert context["test_phases"][0]["gate_criteria"] == "Observable result"


@pytest.mark.parametrize("status", ["retired", "superseded", "specified"])
def test_task_context_refuses_inactive_transitive_requirement(native, status):
    service, client, _, _ = native
    seed(client)
    assert (
        put(client, "specifications", "GOV-1", {"title": "Required constraint", "status": "active"}).status_code == 200
    )
    assert put(client, "specifications", "SPEC-1", {"affected_by": ["GOV-1"]}, expected_version=1).status_code == 200
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    assert put(client, "specifications", "GOV-1", {"status": status}, expected_version=1).status_code == 200
    before = history_count(service)
    result = client.get("/v1/work-items/WI-1/context")
    assert result.status_code == 422, result.text
    assert result.json()["error"]["code"] == "inactive_context_source"
    assert result.json()["error"]["details"]["ids"] == ["GOV-1"]
    assert "gt context work-item WI-1" in result.json()["error"]["details"]["recovery_route"]
    assert history_count(service) == before


def test_task_context_does_not_replay_prior_success_when_authority_fails(native, monkeypatch):
    service, client, _, _ = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    assert client.get("/v1/work-items/WI-1/context").status_code == 200

    def unavailable():
        raise PostgresKernelError("postgres_unavailable", "Canonical source unavailable")

    monkeypatch.setattr(service.kernel, "_connect", unavailable)
    result = client.get("/v1/work-items/WI-1/context")
    assert result.status_code == 503
    assert result.json()["error"]["code"] == "postgres_unavailable"
    assert "specifications" not in result.json()
    assert result.headers["cache-control"] == "no-store"


def test_task_context_reads_one_snapshot_during_concurrent_canonical_changes(native, monkeypatch):
    _, client, _, _ = native
    seed(client)
    assert put(client, "specifications", "GOV-1", {"title": "Constraint", "status": "active"}).status_code == 200
    assert put(client, "specifications", "SPEC-1", {"affected_by": ["GOV-1"]}, expected_version=1).status_code == 200
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    started, changed = Event(), Event()
    original_get = PostgresTransaction.get

    def pause_after_work_read(tx, table, identity, **kwargs):
        row = original_get(tx, table, identity, **kwargs)
        if table == "work_items" and identity == {"id": "WI-1"} and not started.is_set():
            started.set()
            assert changed.wait(15), "Concurrent canonical amendments did not complete"
        return row

    monkeypatch.setattr(PostgresTransaction, "get", pause_after_work_read)
    with ThreadPoolExecutor(max_workers=1) as workers:
        reading = workers.submit(client.get, "/v1/work-items/WI-1/context")
        try:
            assert started.wait(15), "The context did not read its canonical work item"
            assert (
                put(
                    client, "specifications", "SPEC-1", {"description": "New required effect"}, expected_version=2
                ).status_code
                == 200
            )
            assert (
                put(
                    client, "specifications", "GOV-1", {"description": "New constraint"}, expected_version=1
                ).status_code
                == 200
            )
        finally:
            changed.set()
        result = reading.result(timeout=15)
    assert result.status_code == 200, result.text
    prior = {row["id"]: row for row in result.json()["specifications"]}
    assert prior["SPEC-1"]["version"] == 2 and prior["GOV-1"]["version"] == 1
    fresh = {row["id"]: row for row in client.get("/v1/work-items/WI-1/context").json()["specifications"]}
    assert fresh["SPEC-1"]["description"] == "New required effect"
    assert fresh["GOV-1"]["description"] == "New constraint"


def test_task_context_reports_missing_linked_source_without_partial_context(native):
    service, client, _, _ = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    # An incomplete imported relationship must be diagnosed even though the
    # ordinary formal writer refuses to introduce this missing reference.
    link_project_formal(service, "SPEC-MISSING")
    before = history_count(service)
    result = client.get("/v1/work-items/WI-1/context")
    assert result.status_code == 404, result.text
    error = result.json()["error"]
    assert error["code"] == "not_found"
    assert error["details"]["id"] == "SPEC-MISSING"
    assert "gt context work-item WI-1" in error["details"]["recovery_route"]
    assert "work_item" not in result.json()
    assert history_count(service) == before


def test_task_context_requires_current_test_plan_instructions(native):
    service, client, _, _ = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    assert put(client, "test-plans", "PLAN-1", {"status": "retired"}, expected_version=1).status_code == 200
    before = history_count(service)
    result = client.get("/v1/work-items/WI-1/context")
    assert result.status_code == 422, result.text
    assert result.json()["error"]["code"] == "test_phase_required"
    assert history_count(service) == before


def test_separate_ordinary_cli_processes_use_http_and_never_sqlite(native, tmp_path):
    service, client, _, service_name = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "code.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "tests/test_effect.py").write_text("def test_effect(): assert 1 == 1\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text(".worktrees/\n", encoding="utf-8")
    for arguments in (
        ["config", "user.name", "Qualification"],
        ["config", "user.email", "qualification@example.invalid"],
        ["add", "--", "code.py", "tests/test_effect.py", ".gitignore"],
        ["commit", "-qm", "Isolated CLI preimage"],
    ):
        subprocess.run(["git", "-C", str(tmp_path), *arguments], check=True, capture_output=True)
    # Install the same native callback as the real checkout. Full baseline
    # policy-hook qualification is separate from this HTTP/no-SQLite workflow.
    hooks = tmp_path / ".githooks"
    hooks.mkdir()
    reference_hook = hooks / "reference-transaction"
    reference_hook.write_bytes((Path(__file__).resolve().parents[2] / ".githooks/reference-transaction").read_bytes())
    reference_hook.chmod(0o755)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "core.hooksPath", ".githooks"], check=True, capture_output=True
    )
    harness = {column: None for column in TABLE_SPECS["harnesses"].columns}
    harness.update(
        id="HARNESS-CLI",
        version=1,
        harness_name="cli-qualification",
        harness_type="test",
        status="registered",
        changed_at=datetime.now(UTC).isoformat(),
        changed_by="qualification",
        change_reason="CLI bridge test",
    )
    service.kernel.mutate_current(
        table="harnesses",
        identity={"id": harness["id"]},
        expected_version=0,
        new_state=harness,
        actor="qualification",
        reason="CLI bridge test",
    )
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    sentinel = tmp_path / "must-not-open.db"
    sentinel.write_bytes(b"This is not a SQLite database; opening it is a test failure.")
    server_config = tmp_path / "server.toml"
    server_config.write_text(
        f'[groundtruth]\nproject_root="."\n[postgresql]\nservice="{service_name}"\n', encoding="utf-8"
    )
    client_config = tmp_path / "client.toml"
    client_config.write_text(
        f'[groundtruth]\nauthority_url="{url}"\ndb_path="must-not-open.db"\nproject_root="."\n', encoding="utf-8"
    )
    base_env = os.environ.copy()
    base_env.pop("GT_AUTHORITY_URL", None)
    base_env["GT_DB_PATH"] = str(sentinel)
    base_env["GT_PROJECT_ROOT"] = str(tmp_path)
    # An isolated parent interpreter's sys.path is not inherited by children.
    # Bind subprocesses to the package under test, including editable-source runs.
    import groundtruth_kb

    package_file = Path(groundtruth_kb.__file__).resolve()
    base_env["PYTHONPATH"] = str(package_file.parent.parent)
    client_env = {key: value for key, value in base_env.items() if not key.startswith(("PG", "GT_POSTGRES_"))}
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    package_probe = subprocess.run(
        [sys.executable, "-c", "import groundtruth_kb; print(groundtruth_kb.__file__)"],
        cwd=tmp_path,
        env=client_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        creationflags=flags,
    )
    assert package_probe.returncode == 0, package_probe.stderr
    assert Path(package_probe.stdout.strip()).resolve() == package_file

    def cli(*arguments):
        return subprocess.run(
            [sys.executable, "-m", "groundtruth_kb", "--config", str(client_config), *arguments],
            cwd=tmp_path,
            env=client_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            creationflags=flags,
        )

    with (tmp_path / "service.log").open("wb") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "groundtruth_kb",
                "--config",
                str(server_config),
                "service",
                "serve",
                "--port",
                str(port),
            ],
            cwd=tmp_path,
            env=base_env,
            stdout=log,
            stderr=log,
            creationflags=flags,
        )
        try:
            deadline = time.monotonic() + 30
            http = AuthorityClient(url, timeout=1)
            while True:
                try:
                    http.request("GET", "/v1/status")
                    break
                except AuthorityClientError:
                    if process.poll() is not None or time.monotonic() >= deadline:
                        pytest.fail("Native authority did not start; inspect disposable service.log")
                    time.sleep(0.1)
            # Test-phase listing is a current native domain read, not a legacy
            # SQLite history query under the backlog command. Exercise several
            # real revisions and both ordinary CLI output modes.
            phase_two = put(
                client,
                "test-phases",
                "PHASE-2",
                {
                    "title": "Earlier phase two",
                    "plan_id": "PLAN-1",
                    "phase_order": 20,
                    "test_ids": [],
                    "gate_criteria": "Second observable result",
                },
            )
            assert phase_two.status_code == 200, phase_two.text
            for phase_id, last_version in (("PHASE-1", 4), ("PHASE-2", 3)):
                phase = client.get(f"/v1/test-phases/{phase_id}").json()
                for version in range(2, last_version + 1):
                    final = version == last_version
                    phase = {
                        **phase,
                        **{
                            "version": version,
                            "title": f"Current {phase_id}" if final else f"Earlier {phase_id}",
                            "last_result": "pass" if final else "obsolete-result",
                            "changed_at": datetime.now(UTC).isoformat(),
                            "changed_by": "qualification",
                            "change_reason": "Phase-listing fixture",
                        },
                    }
                    # Seed result history through the native kernel fixture;
                    # phase-definition authors cannot set execution results.
                    service.kernel.mutate_current(
                        table="test_plan_phases",
                        identity={"id": phase_id},
                        expected_version=version - 1,
                        new_state=phase,
                        actor="qualification",
                        reason="Phase-listing fixture",
                    )
            phase_history_before = history_count(service)
            phase_json = cli("test-phases", "list", "--json")
            assert phase_json.returncode == 0, phase_json.stderr
            phases = json.loads(phase_json.stdout)
            assert [p["id"] for p in phases] == ["PHASE-1", "PHASE-2"]
            assert [p["version"] for p in phases] == [4, 3]
            assert {p["last_result"] for p in phases} == {"pass"}
            phase_text = cli("test-phases", "list")
            assert phase_text.returncode == 0, phase_text.stderr
            phase_lines = [line for line in phase_text.stdout.splitlines() if line.strip()]
            assert phase_lines == ["PHASE-1 v4: Current PHASE-1", "PHASE-2 v3: Current PHASE-2"]
            assert history_count(service) == phase_history_before
            observation_fields = {
                "title": "Read-only CLI observation",
                "status": "active",
                "assertions": [{"type": "file_exists", "file": "code.py"}],
            }
            declaration = tmp_path / "config/registry/sot-artifacts.toml"
            declaration.parent.mkdir(parents=True)
            declaration.write_text("artifacts = []\n", encoding="utf-8")
            before_inventory = history_count(service)
            listed = cli("registry", "list", "--json")
            assert listed.returncode == 0 and json.loads(listed.stdout) == []
            inventory = cli("registry", "reconcile", "--json")
            inventory_report = json.loads(inventory.stdout)
            governed = next(
                item for item in inventory_report["observers"] if item["observer_class"] == "governed_knowledge"
            )
            assert governed["succeeded"] is True, governed
            assert "tests/test_effect.py" in {item["relative_path"] for item in governed["observations"]}
            assert history_count(service) == before_inventory
            assert declaration.read_text(encoding="utf-8") == "artifacts = []\n"
            assert (
                put(
                    client, "specifications", "GOV-REGISTRY", {"title": "Registry contract", "status": "active"}
                ).status_code
                == 200
            )
            registry_record = {
                "id": "registry",
                "domain": "control_surface",
                "lifecycle": "active",
                "storage_path": "config/registry/sot-artifacts.toml",
                "coverage_mode": "exact",
                "authority_spec_id": "GOV-REGISTRY",
                "mutation_api": "gt registry amend",
                "versioning_policy": "git_tracked",
                "backup_policy": "git_tracked",
                "health_check_function": "",
                "owner_role": "shared",
                "restore_action": "git_restore",
            }
            before_registry_mutation = history_count(service)
            registered = cli("registry", "register", "--record-json", json.dumps(registry_record))
            assert registered.returncode == 0, registered.stderr
            assert json.loads(registered.stdout)["changed"] is True
            amended = cli("registry", "amend", "registry", "--changes-json", '{"notes":"current native authority"}')
            assert amended.returncode == 0, amended.stderr
            assert history_count(service) == before_registry_mutation
            shown = cli("registry", "show", "registry", "--json")
            assert json.loads(shown.stdout)["notes"] == "current native authority"
            assert not (tmp_path / ".gtkb-state").exists()
            term_file = tmp_path / "term.json"
            term_file.write_text(json.dumps(term_fields()), encoding="utf-8")
            term_record = cli(
                "terms",
                "record",
                "--id",
                "PROJECT",
                "--fields-file",
                str(term_file),
                "--expected-version",
                "0",
                "--actor",
                "qualification",
                "--change-reason",
                "Current canonical terminology",
                "--json",
            )
            assert term_record.returncode == 0, term_record.stderr
            assert json.loads(term_record.stdout)["version"] == 1
            term_before = history_count(service)
            term_show = cli("terms", "show", "PROJECT", "--json")
            assert term_show.returncode == 0
            assert json.loads(term_show.stdout)["source_authority"] == "SPEC-1"
            term_list = cli("terms", "list", "--status", "active", "--scope", "platform", "--json")
            assert term_list.returncode == 0
            assert [r["id"] for r in json.loads(term_list.stdout)] == ["PROJECT"]
            resolved = cli("authority", "resolve", "Work Group", "--scope", "platform", "--json")
            assert resolved.returncode == 0 and json.loads(resolved.stdout)["record"]["id"] == "PROJECT"
            unknown = cli("authority", "resolve", "absent term", "--json")
            assert unknown.returncode == 1 and json.loads(unknown.stdout)["status"] == "not_found"
            term_status = cli("authority", "status", "--json")
            assert term_status.returncode == 0 and json.loads(term_status.stdout)["status"] == "pass"
            assert history_count(service) == term_before
            for version, expected_result in ((0, "PASS"), (1, "PARTIAL")):
                if version:
                    observation_fields["constraints"] = {"behavioral_validation_required": True}
                recorded = put(
                    client, "specifications", "SPEC-OBSERVATION", observation_fields, expected_version=version
                )
                assert recorded.status_code == 200, recorded.text
                before_observation = history_count(service)
                observation = cli("assert", "--spec", "SPEC-OBSERVATION", "--json")
                assert observation.returncode == version, observation.stderr
                report = json.loads(observation.stdout)
                assert report["aggregate_result"] == expected_result
                assert report["details"][0]["spec_version"] == version + 1
                assert history_count(service) == before_observation
            result = cli("projects", "show", "PROJECT-1", "--json")
            assert result.returncode == 0, result.stderr
            assert json.loads(result.stdout)["project"]["authorization"] == "authorized"
            dependency_file = tmp_path / "dependency.json"
            dependency_file.write_text(
                json.dumps(
                    {
                        "dependent_project_id": "PROJECT-1",
                        "prerequisite_project_id": "PROJECT-GTKB-NEW-WORK-INTAKE",
                        "required_prerequisite_state": "verified",
                        "affected_gate": "readiness",
                        "rationale": "Qualify prerequisite diagnostics and canonical correction through ordinary CLI",
                    }
                ),
                encoding="utf-8",
            )

            def dependency_record(version):
                return cli(
                    "projects",
                    "dependencies",
                    "record",
                    "--id",
                    "DEP-CLI",
                    "--fields-file",
                    str(dependency_file),
                    "--expected-version",
                    str(version),
                    "--actor",
                    "qualification",
                    "--change-reason",
                    "Current dependency correction",
                    "--json",
                )

            created = dependency_record(0)
            assert created.returncode == 0, created.stderr
            listed = cli("projects", "dependencies", "list", "--dependent-project", "PROJECT-1", "--json")
            assert listed.returncode == 0 and json.loads(listed.stdout)[0]["id"] == "DEP-CLI", listed.stderr
            readiness = cli("projects", "readiness", "PROJECT-1", "--json")
            assert readiness.returncode == 0 and json.loads(readiness.stdout)["ready"] is False, readiness.stderr
            shown = cli("projects", "dependencies", "show", "DEP-CLI")
            assert shown.returncode == 0 and "PROJECT-GTKB-NEW-WORK-INTAKE = verified" in shown.stdout, shown.stderr
            dependency_file.write_text('{"status":"retired"}', encoding="utf-8")
            retired = dependency_record(1)
            assert retired.returncode == 0 and json.loads(retired.stdout)["status"] == "retired", retired.stderr
            assert put(client, "projects", "PROJECT-DEPENDENT", {"name": "Downstream project"}).status_code == 200
            assert (
                put(
                    client,
                    "work-items",
                    "WI-DEPENDENT",
                    work_fields(depends_on_work_items=["WI-1"]),
                    project_id="PROJECT-DEPENDENT",
                ).status_code
                == 200
            )
            work_readiness = cli("backlog", "readiness", "WI-DEPENDENT", "--json")
            assert work_readiness.returncode == 0, work_readiness.stderr
            assert json.loads(work_readiness.stdout)["ready"] is False
            work_context = cli("context", "work-item", "WI-DEPENDENT", "--json")
            assert json.loads(work_context.stdout)["work_item_readiness"] == json.loads(work_readiness.stdout)
            assert (
                put(
                    client,
                    "specifications",
                    "GOV-CLI",
                    {"title": "Constraint loaded by each fresh context", "status": "active"},
                ).status_code
                == 200
            )
            amendment = tmp_path / "fields.json"
            amendment.write_text(
                json.dumps({"description": "Fresh context reads current canon: 漢字 café", "affected_by": ["GOV-CLI"]}),
                encoding="utf-8",
            )
            result = cli(
                "spec",
                "record",
                "--id",
                "SPEC-1",
                "--fields-file",
                str(amendment),
                "--expected-version",
                "1",
                "--actor",
                "interactive-correction",
                "--change-reason",
                "Current direction",
                "--json",
            )
            assert result.returncode == 0, result.stderr
            result = cli("context", "work-item", "WI-1", "--json")
            assert result.returncode == 0, result.stderr
            loaded = json.loads(result.stdout)
            assert [row["id"] for row in loaded["specifications"]] == ["GOV-CLI", "SPEC-1"]
            assert loaded["specifications"][1]["description"].endswith("漢字 café")
            assert loaded["test_phases"][0]["gate_criteria"] == "Observable result"
            readable = cli("context", "work-item", "WI-1")
            assert readable.returncode == 0, readable.stderr
            assert all(
                value in readable.stdout
                for value in ("GOV-CLI", "test_phases:", "Observable result", "test_plans:", "PLAN-1")
            )
            # Each call starts a fresh CLI process without PostgreSQL credentials.
            for version, (role, status) in enumerate(
                (("pb", "NEW"), ("lo", "GO"), ("pb", "READY"), ("lo", "VERIFIED")), 1
            ):
                context = f"qualification-{role}-{version}"
                bound = cli(
                    "session", "bind", "--native-context-id", context, "--init-keyword", f"::init gtkb {role}", "--json"
                )
                assert bound.returncode == 0, bound.stderr
                session_id = json.loads(bound.stdout)["session_context_id"]
                claim = cli(
                    "bridge",
                    "claim",
                    "cli-chain",
                    "--work-item-id",
                    "WI-1",
                    "--native-context-id",
                    context,
                    "--expected-version",
                    str(version - 1),
                    "--status",
                    status,
                    "--request-id",
                    str(uuid4()),
                    "--json",
                )
                assert claim.returncode == 0, claim.stderr
                fence = json.loads(claim.stdout)["fence"]
                receiver = "lo" if status in {"NEW", "READY"} else "pb" if status == "GO" else None
                lines = [f"::init gtkb {receiver}", "::open build", status] if receiver else [status]
                kind = (
                    "implementation_proposal"
                    if status == "NEW"
                    else "implementation_report"
                    if status == "READY"
                    else "lo_verdict"
                )
                metadata = {
                    "bridge_kind": kind,
                    "Document": "cli-chain",
                    "Version": str(version),
                    "Date": datetime.now(UTC).date().isoformat(),
                    "author_identity": "qualified-agent",
                    "author_harness_id": "HARNESS-CLI",
                    "author_session_context_id": session_id,
                    "author_model": "qualification",
                    "Project": "PROJECT-1",
                    "Work Item": "WI-1",
                }
                if receiver:
                    metadata["recipient_role"] = "loyal-opposition" if receiver == "lo" else "prime-builder"
                if status == "NEW":
                    metadata.update(
                        work_item_version=loaded["work_item"]["version"],
                        target_paths='["code.py"]',
                        test_artifact_targets='["tests/test_effect.py"]',
                        spec_versions=json.dumps({row["id"]: row["version"] for row in loaded["specifications"]}),
                    )
                if status == "READY":
                    checked = cli(
                        "bridge", "check", "cli-chain", "--native-context-id", context, "--fence", str(fence), "--json"
                    )
                    assert checked.returncode == 0, checked.stderr
                    opened = cli(
                        "bridge",
                        "worktree",
                        "cli-chain",
                        "--native-context-id",
                        context,
                        "--fence",
                        str(fence),
                        "--json",
                    )
                    assert opened.returncode == 0, opened.stderr
                    checkout = json.loads(opened.stdout)
                    (Path(checkout["path"]) / "code.py").write_text("value = 2\n", encoding="utf-8")
                    preimages = tmp_path / "preimages.json"
                    preimages.write_text(json.dumps(checkout["artifact_preimages"]), encoding="utf-8")
                    published = cli(
                        "bridge",
                        "publish-work",
                        "cli-chain",
                        "--native-context-id",
                        context,
                        "--fence",
                        str(fence),
                        "--preimages-file",
                        str(preimages),
                        "--json",
                    )
                    assert published.returncode == 0, published.stderr
                    assert (tmp_path / "code.py").read_text() == "value = 1\n"
                if status == "VERIFIED":
                    opened = cli(
                        "bridge",
                        "worktree",
                        "cli-chain",
                        "--native-context-id",
                        context,
                        "--fence",
                        str(fence),
                        "--json",
                    )
                    assert opened.returncode == 0, opened.stderr
                    assert (Path(json.loads(opened.stdout)["path"]) / "code.py").read_text() == "value = 2\n"
                    snapshot = cli("bridge", "artifacts", "cli-chain", "--json")
                    assert snapshot.returncode == 0, snapshot.stderr
                    metadata["verified_artifacts"] = json.dumps(json.loads(snapshot.stdout))
                artifact = tmp_path / f"authored-{version}.md"
                artifact.write_bytes(
                    "\r\n".join(
                        [
                            *lines,
                            *(f"{key}: {value}" for key, value in metadata.items()),
                            "",
                            "Complete authored message.",
                        ]
                    ).encode("utf-8")
                )
                delivered = cli(
                    "bridge",
                    "deliver",
                    "cli-chain",
                    "--native-context-id",
                    context,
                    "--fence",
                    str(fence),
                    "--content-file",
                    str(artifact),
                    "--json",
                )
                assert delivered.returncode == 0, delivered.stderr
                report_result = cli("bridge", "state-report", "--json")
                assert report_result.returncode == 0, report_result.stderr
                report = json.loads(report_result.stdout)
                assert report["active_status_mix"] == [{"status": status, "count": 1}]
                assert report["active_claim_count"] == 0
                assert not {"harnesses", "registry_publication"} & report.keys()
                if status == "VERIFIED":
                    assert json.loads(delivered.stdout)["project_ready_for_commit"] is True
            message = tmp_path / "project-commit.txt"
            message.write_text("Complete the CLI qualification project (WI-1)\n", encoding="utf-8")
            committed = cli(
                "projects",
                "commit",
                "PROJECT-1",
                "--native-context-id",
                context,
                "--expected-version",
                "1",
                "--message-file",
                str(message),
                "--json",
            )
            assert committed.returncode == 0, committed.stderr
            result = json.loads(committed.stdout)
            assert result["status"] == "confirmed"
            actual_head = subprocess.run(
                ["git", "-C", str(tmp_path), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
            ).stdout.strip()
            assert actual_head == result["commit_id"]
            assert (tmp_path / "code.py").read_text() == "value = 2\n"
            terminal = cli("projects", "show", "PROJECT-1", "--json")
            assert json.loads(terminal.stdout)["project"]["status"] == "verified"
            work_readiness = cli("backlog", "readiness", "WI-DEPENDENT", "--json")
            assert work_readiness.returncode == 0, work_readiness.stderr
            assert json.loads(work_readiness.stdout)["ready"] is True
            disabled = cli("seed")
            assert disabled.returncode != 0 and "fallback is disabled" in disabled.stderr
        finally:
            process.terminate()
            process.wait(timeout=15)
    unavailable = cli("projects", "show", "PROJECT-1", "--json")
    assert unavailable.returncode != 0 and "authority_unavailable" in unavailable.stderr
    unavailable_context = cli("context", "work-item", "WI-1", "--json")
    assert unavailable_context.returncode != 0 and "authority_unavailable" in unavailable_context.stderr
    assert unavailable_context.stdout == ""
    unavailable_inventory = cli("registry", "reconcile", "--json")
    inventory_report = json.loads(unavailable_inventory.stdout)
    governed = next(item for item in inventory_report["observers"] if item["observer_class"] == "governed_knowledge")
    assert governed["succeeded"] is False
    assert any("configured authority is unavailable" in item for item in governed["diagnostics"])
    assert inventory_report["sweep_eligible"] is False
    before_failed_mutation = declaration.read_bytes()
    unavailable_mutation = cli("registry", "amend", "registry", "--changes-json", '{"notes":"must not write"}')
    assert unavailable_mutation.returncode != 0 and "authority_unavailable" in unavailable_mutation.stderr
    assert declaration.read_bytes() == before_failed_mutation
    assert sentinel.read_bytes() == b"This is not a SQLite database; opening it is a test failure."
    assert service.show("specifications", "SPEC-1")["version"] == 2


def term_fields(**extra):
    return dict(
        canonical_term="project",
        definition="A complete interdependent outcome.",
        scope="platform",
        authority_level="platform_core",
        lifecycle_status="active",
        source_authority="SPEC-1",
        accepted_synonyms=["work group"],
        **extra,
    )


def test_native_terms_resolve_current_source_and_retire_without_historical_fallback(
    native,
):
    service, client, *_ = native
    seed(client)
    created = put(client, "terms", "PROJECT", term_fields())
    assert created.status_code == 200, created.text
    assert created.json()["version"] == 1
    resolved = client.get("/v1/authority/resolve", params={"subject": "Work Group", "scope": "platform"})
    assert resolved.status_code == 200, resolved.text
    assert resolved.json()["record"]["id"] == "PROJECT"
    assert client.get("/v1/authority/status").json()["status"] == "pass"
    before = history_count(service)
    stale = put(client, "terms", "PROJECT", {"definition": "Must not land"})
    assert stale.status_code == 409 and history_count(service) == before
    retired = put(client, "terms", "PROJECT", {"lifecycle_status": "retired"}, expected_version=1)
    assert retired.status_code == 200
    assert client.get("/v1/authority/resolve", params={"subject": "project"}).json()["status"] == "not_found"
    assert client.get("/v1/terms/PROJECT").json()["version"] == 2


@pytest.mark.parametrize("source_status", ["retired", "superseded"])
def test_retired_source_blocks_only_its_term_and_status_stays_available(native, source_status):
    service, client, *_ = native
    seed(client)
    assert put(client, "terms", "PROJECT", term_fields()).status_code == 200
    assert (
        put(
            client,
            "specifications",
            "SPEC-2",
            {"title": "Other meaning", "status": "active"},
        ).status_code
        == 200
    )
    other = term_fields()
    other.update(canonical_term="other", accepted_synonyms=[], source_authority="SPEC-2")
    assert put(client, "terms", "OTHER", other).status_code == 200
    assert (
        put(
            client,
            "specifications",
            "SPEC-2",
            {"status": source_status},
            expected_version=1,
        ).status_code
        == 200
    )
    before = history_count(service)
    assert client.get("/v1/authority/resolve", params={"subject": "project"}).json()["status"] == "resolved"
    refused = client.get("/v1/authority/resolve", params={"subject": "other"})
    assert refused.status_code == 422 and refused.json()["error"]["code"] == "invalid_term_source"
    status = client.get("/v1/authority/status")
    assert status.status_code == 200
    assert status.json()["source_issues"] == [{"id": "OTHER", "source_authority": "SPEC-2", "status": source_status}]
    assert history_count(service) == before


@pytest.mark.parametrize("change", [{"source_authority": "MISSING"}, {"accepted_synonyms": [" "]}])
def test_invalid_term_mutation_rolls_back_record_and_history(native, change):
    service, client, *_ = native
    seed(client)
    value = term_fields()
    value.update(change)
    before = history_count(service)
    refused = put(client, "terms", "BAD", value)
    assert refused.status_code == 422, refused.text
    assert client.get("/v1/terms/BAD").status_code == 404
    assert history_count(service) == before


def test_a_malformed_imported_entry_does_not_break_valid_lookup_or_status(native):
    from psycopg import sql

    service, client, *_ = native
    seed(client)
    assert put(client, "terms", "PROJECT", term_fields()).status_code == 200
    other = term_fields()
    other.update(canonical_term="other", accepted_synonyms=[])
    assert put(client, "terms", "OTHER", other).status_code == 200
    # Corrupt only the disposable fixture: model an older/imported bad record.
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("UPDATE {}.canonical_terms SET accepted_synonyms='{{}}'::jsonb WHERE id='OTHER'").format(
                sql.Identifier(tx.schema)
            )
        )
    before = history_count(service)
    assert client.get("/v1/authority/resolve", params={"subject": "project"}).json()["status"] == "resolved"
    refused = client.get("/v1/authority/resolve", params={"subject": "other"})
    assert refused.status_code == 422 and refused.json()["error"]["code"] == "invalid_terminology"
    status = client.get("/v1/authority/status")
    assert status.status_code == 200 and status.json()["status"] == "fail"
    assert [r["id"] for r in status.json()["validation_issues"]] == ["OTHER"]
    assert history_count(service) == before
