"""Native field types and SQLite-to-PostgreSQL fidelity (WI-7714 / TEST-12601)."""

from __future__ import annotations

import json
import re
import sqlite3
from importlib.resources import files

import psycopg
import pytest
from groundtruth_kb.config import PostgreSQLConfig
from groundtruth_kb.native_authority import SpecFields, TermFields, TestFields, TestPhaseFields, WorkItemFields
from groundtruth_kb.postgres_kernel import (
    CURRENT_FORMAT,
    MIGRATION_TABLES,
    TABLE_SPECS,
    TRANSFORM_FORMAT,
    PostgresKernel,
    PostgresKernelError,
    canonical_json_bytes,
    normalize_manifest,
    parse_json_bytes,
)
from psycopg import sql

from platform_tests.groundtruth_kb.test_postgres_kernel_integration import _create_sqlite_fixture
from platform_tests.groundtruth_kb.test_postgres_kernel_integration import isolated_postgres as isolated_postgres


def ddl_columns():
    text = files("groundtruth_kb").joinpath("postgresql_v1.sql").read_text(encoding="utf-8")
    tables = {
        match.group(1): dict(
            re.findall(r"^\s*([a-z_]+)\s+(JSONB|TEXT|INTEGER|BIGINT|BOOLEAN|DATE|TIMESTAMPTZ)\b", match.group(2), re.M)
        )
        for match in re.finditer(r"CREATE TABLE \{schema\}\.([a-z_]+)\s*\((.*?)\n\);", text, re.S)
    }
    assert tables and "work_items" in tables, "Selected package DDL was not parsed"
    return tables


@pytest.mark.parametrize(
    "table,model",
    [
        ("specifications", SpecFields),
        ("tests", TestFields),
        ("test_plan_phases", TestPhaseFields),
        ("work_items", WorkItemFields),
        ("canonical_terms", TermFields),
    ],
)
def test_native_request_collection_types_match_selected_package_ddl(table, model):
    columns = ddl_columns()[table]
    for name, declaration in model.model_json_schema()["properties"].items():
        variants = declaration.get("anyOf", [declaration])
        types = {variant.get("type") for variant in variants} - {"null"}
        assert name in columns, (table, name)
        assert (columns[name] == "JSONB") == bool(types & {"array", "object"}), (table, name, types)
        if columns[name] == "JSONB":
            assert types <= {"array", "object"}, (table, name, types)


def test_selected_package_ddl_and_kernel_json_columns_agree_without_exemptions():
    declared = ddl_columns()
    for name, spec in TABLE_SPECS.items():
        assert name in declared
        assert {column for column, kind in declared[name].items() if kind == "JSONB"} == set(spec.json_columns)
    assert declared["specifications"]["application_scope"] == "TEXT"
    assert declared["tests"]["application_scope"] == "TEXT"
    assert "related_bridge_threads" not in declared["work_items"]


@pytest.mark.parametrize(
    "column",
    [
        "related_deliberation_ids",
        "related_spec_ids_at_creation",
        "depends_on_work_items",
        "blocks_work_items",
        "supersedes",
        "superseded_by",
    ],
)
@pytest.mark.parametrize("value", ["unexpected scalar", {}, [1], [""], [None]])
def test_reference_list_fields_refuse_scalars_objects_and_nonreferences(column, value):
    manifest = {"format": CURRENT_FORMAT, "schema_version": 1, "tables": {name: [] for name in MIGRATION_TABLES}}
    metadata = {
        "version": 1,
        "changed_by": "qualification",
        "changed_at": "2026-09-10T00:00:00+00:00",
        "change_reason": "Reference-list validation",
    }
    for table, fields in [
        (
            "projects",
            {"id": "P", "name": "Project", "kind": "project", "authorization": "authorized", "status": "active"},
        ),
        (
            "work_items",
            {
                "id": "W",
                "title": "Work",
                "origin": "owner",
                "component": "platform",
                "resolution_status": "open",
                "stage": "created",
            },
        ),
        ("project_work_item_memberships", {"id": "M", "project_id": "P", "work_item_id": "W", "status": "active"}),
    ]:
        row = {name: None for name in TABLE_SPECS[table].columns}
        row.update(metadata, **fields)
        manifest["tables"][table].append(row)
    assert normalize_manifest(manifest) == manifest
    manifest["tables"]["work_items"][0][column] = value
    before = canonical_json_bytes(manifest)
    with pytest.raises(PostgresKernelError) as error:
        normalize_manifest(manifest)
    assert error.value.code == (
        "invalid_work_item_dependencies" if column == "depends_on_work_items" else "invalid_manifest"
    )
    if column != "depends_on_work_items":
        assert f"work_items.{column}" in str(error.value)
    assert canonical_json_bytes(manifest) == before


@pytest.mark.integration
@pytest.mark.timeout(120)
@pytest.mark.parametrize("shape", ["null", "empty", "populated"])
def test_structured_source_fields_import_as_typed_values_and_read_back_exactly(isolated_postgres, tmp_path, shape):
    service, schema = isolated_postgres
    source = tmp_path / "source.db"
    writer = _create_sqlite_fixture(source)
    list_columns = (
        "related_deliberation_ids",
        "related_spec_ids_at_creation",
        "depends_on_work_items",
        "blocks_work_items",
        "supersedes",
        "superseded_by",
    )
    values = {name: None if shape == "null" else [] for name in list_columns}
    if shape == "populated":
        values.update(
            related_deliberation_ids=["DELIB-1"],
            related_spec_ids_at_creation=["SPEC-1"],
            depends_on_work_items=["WI-PREDECESSOR"],
        )
    try:
        for column in list_columns:
            if column != "depends_on_work_items":
                writer.execute(f'ALTER TABLE work_items ADD COLUMN "{column}" TEXT')
        writer.row_factory = sqlite3.Row
        if shape == "populated":
            predecessor = dict(writer.execute("SELECT * FROM work_items WHERE id='WI-OPAQUE'").fetchone())
            predecessor.update(id="WI-PREDECESSOR", title="Predecessor")
            names = list(predecessor)
            writer.execute(
                "INSERT INTO work_items (" + ",".join(names) + ") VALUES (" + ",".join("?" for _ in names) + ")",
                list(predecessor.values()),
            )
            membership = dict(
                writer.execute("SELECT * FROM project_work_item_memberships WHERE id='MEMBER-OPAQUE'").fetchone()
            )
            membership.update(id="MEMBER-PREDECESSOR", work_item_id="WI-PREDECESSOR")
            names = list(membership)
            writer.execute(
                "INSERT INTO project_work_item_memberships ("
                + ",".join(names)
                + ") VALUES ("
                + ",".join("?" for _ in names)
                + ")",
                list(membership.values()),
            )
        for column, value in values.items():
            writer.execute(
                f'UPDATE work_items SET "{column}"=? WHERE id=?',
                (None if value is None else json.dumps(value), "WI-OPAQUE"),
            )
        writer.commit()
        snapshot = tmp_path / "snapshot.db"
        with sqlite3.connect(snapshot) as target:
            writer.backup(target)
    finally:
        writer.close()
    kernel = PostgresKernel(PostgreSQLConfig(service=service))
    plan = {
        "format": TRANSFORM_FORMAT,
        "schema_version": 1,
        "source": kernel.preflight_export_current(sqlite_snapshot=snapshot, live_sqlite_source=source),
        "projects": {
            "expected_programs": 0,
            "expected_authorized": 1,
            "expected_not_authorized": 1,
            "expected_total": 2,
        },
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
    }
    plan_path = tmp_path / "transform.json"
    plan_path.write_bytes(canonical_json_bytes(plan))
    manifest_path = tmp_path / "current.json"
    before = snapshot.read_bytes()
    kernel.export_current(
        sqlite_snapshot=snapshot, transform_plan=plan_path, output=manifest_path, live_sqlite_source=source
    )
    manifest = parse_json_bytes(manifest_path.read_bytes())
    work = next(row for row in manifest["tables"]["work_items"] if row["id"] == "WI-OPAQUE")
    assert {name: work[name] for name in list_columns} == values
    assert "related_bridge_threads" not in work
    assert snapshot.read_bytes() == before
    kernel.initialize()
    result = kernel.import_current(input_path=manifest_path, actor="qualification", reason="Typed source fidelity")
    assert result["status"] == "imported"
    with psycopg.connect(service=service) as connection:
        for column, value in values.items():
            raw, kind = connection.execute(
                sql.SQL("SELECT {},jsonb_typeof({}) FROM {}.work_items WHERE id='WI-OPAQUE'").format(
                    sql.Identifier(column), sql.Identifier(column), sql.Identifier(schema)
                )
            ).fetchone()
            assert raw == value and kind == (None if value is None else "array")
        row = connection.execute(
            sql.SQL(
                "SELECT application_scope,pg_typeof(application_scope)::text,jsonb_typeof(constraints) FROM {}.specifications WHERE id='SPEC-1'"
            ).format(sql.Identifier(schema))
        ).fetchone()
        assert row == ("gtkb_platform", "text", "object")
    readback = tmp_path / "readback.json"
    kernel.readback_current(output=readback)
    assert readback.read_bytes() == manifest_path.read_bytes()
    assert (
        kernel.import_current(input_path=manifest_path, actor="qualification", reason="Exact retry")["status"]
        == "already_current"
    )
