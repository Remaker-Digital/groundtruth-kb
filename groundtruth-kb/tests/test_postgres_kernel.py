"""Database-free contract tests for the PostgreSQL shadow kernel."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

import groundtruth_kb.cli as cli_module
import groundtruth_kb.postgres_kernel as kernel_module
from groundtruth_kb.cli import main
from groundtruth_kb.config import PostgreSQLConfig
from groundtruth_kb.postgres_kernel import (
    ALL_TABLES,
    CURRENT_FORMAT,
    CURRENT_TABLES,
    MIGRATION_TABLES,
    SQLITE_INVENTORY_FORMAT,
    TABLE_SPECS,
    TRANSFORM_FORMAT,
    PostgresKernel,
    PostgresKernelError,
    canonical_json_bytes,
    canonical_sha256,
    normalize_manifest,
    normalize_table_inventory,
    parse_json_bytes,
    schema_sql_bytes,
    schema_sql_sha256,
    validate_transform_plan,
)


@pytest.fixture(autouse=True)
def no_real_database_connections(monkeypatch):
    """Every source-only test fails immediately if production I/O is attempted."""

    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("database connection attempted in database-free selector")

    monkeypatch.setattr(kernel_module.psycopg, "connect", forbidden)
    monkeypatch.setattr(kernel_module.sqlite3, "connect", forbidden)


def _plan(snapshot: bytes = b"snapshot") -> dict[str, Any]:
    return {
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
        "source": {
            "expected_pragma_user_version": 7,
            "expected_table_inventory_sha256": "0" * 64,
            "sqlite_snapshot_sha256": hashlib.sha256(snapshot).hexdigest(),
            "sqlite_snapshot_size_bytes": len(snapshot),
        },
    }


def _empty_manifest() -> dict[str, Any]:
    return {
        "format": CURRENT_FORMAT,
        "schema_version": 1,
        "tables": {table_name: [] for table_name in MIGRATION_TABLES},
    }


def _row(table_name: str, **values: object) -> dict[str, Any]:
    if table_name == "projects":
        values.setdefault("kind", "project")
    return {column: values.get(column) for column in TABLE_SPECS[table_name].columns}


def test_source_transform_preserves_formal_semantics_and_scalar_application_scope():
    source = {name: [] for name in MIGRATION_TABLES}
    metadata = dict(version=9, changed_by="fixture", changed_at="2026-09-01T00:00:00Z", change_reason="source")
    source["specifications"] = [
        dict(
            id="SPEC-1",
            title="Formal behavior",
            status="active",
            type="design_constraint",
            authority="stated",
            provisional_until=None,
            constraints='{"atomic":true}',
            affected_by='["SPEC-1"]',
            testability="observable",
            source_paths='["groundtruth-kb/src/groundtruth_kb/db.py"]',
            application_scope="gtkb_platform",
            **metadata,
        )
    ]
    source["tests"] = [
        dict(
            id="TEST-1",
            title="Behavior",
            spec_id="SPEC-1",
            test_type="integration",
            expected_outcome="Correct effect",
            application_scope="agent_red_application",
            last_executed_at="2026-03-04",
            **metadata,
        )
    ]
    plan = _plan()
    plan["projects"] = dict(expected_total=0, expected_authorized=0, expected_not_authorized=0, expected_programs=0)
    plan["project_dependencies"].update(
        preserve_dependency_ids=[],
        retire_dependency_ids=[],
        expected_source_count=0,
        expected_active_after=0,
        expected_retired_after=0,
        expected_gate_transition_count=0,
    )
    transformed = kernel_module._transform_source_rows(source, plan)
    spec = transformed["specifications"][0]
    assert {
        key: spec[key]
        for key in (
            "type",
            "authority",
            "constraints",
            "affected_by",
            "testability",
            "source_paths",
            "application_scope",
        )
    } == dict(
        type="design_constraint",
        authority="stated",
        constraints={"atomic": True},
        affected_by=["SPEC-1"],
        testability="observable",
        source_paths=["groundtruth-kb/src/groundtruth_kb/db.py"],
        application_scope="gtkb_platform",
    )
    assert spec["version"] == 1
    assert transformed["tests"][0]["application_scope"] == "agent_red_application"
    assert transformed["tests"][0]["last_executed_at"] is None
    assert transformed["tests"][0]["last_executed_on"] == "2026-03-04"
    assert source["tests"][0]["last_executed_at"] == "2026-03-04"
    assert source["specifications"][0]["version"] == 9
    assert source["specifications"][0]["constraints"] == '{"atomic":true}'


@pytest.mark.parametrize("table", ["specifications", "tests"])
@pytest.mark.parametrize("value", ['"gtkb_platform"', "unknown", [], {}, 7])
def test_application_scope_is_an_enum_not_arbitrary_json(table, value):
    row = _row(table, id="EXAMPLE-1", version=1, application_scope=value)
    with pytest.raises(PostgresKernelError, match="application_scope"):
        kernel_module._normalize_manifest_row(table, row, require_version_one=True)


@pytest.mark.parametrize(
    "table,timestamp,calendar_date",
    [
        ("tests", "last_executed_at", "last_executed_on"),
        ("test_procedures", "last_executed_at", "last_executed_on"),
        ("test_plan_phases", "last_executed_at", "last_executed_on"),
        ("operational_procedures", "last_verified_at", "last_verified_on"),
        ("operational_procedures", "last_corrected_at", "last_corrected_on"),
    ],
)
def test_event_date_and_instant_cannot_compete(table, timestamp, calendar_date):
    row = _row(
        table, id="EXAMPLE-1", version=1, **{timestamp: "2026-03-04T11:00:00+00:00", calendar_date: "2026-03-04"}
    )
    with pytest.raises(PostgresKernelError, match="not both"):
        kernel_module._normalize_manifest_row(table, row, require_version_one=True)


def test_packaged_schema_matches_the_native_domain_contract():
    raw = schema_sql_bytes()
    text = raw.decode("utf-8")
    created = re.findall(r"CREATE TABLE \{schema\}\.([a-z_]+)", text)

    assert tuple(created) == ALL_TABLES
    assert schema_sql_sha256() == hashlib.sha256(raw).hexdigest()
    for token in ("TIMESTAMPTZ", "JSONB", "BOOLEAN", "FOR UPDATE", "AUTOINCREMENT", "PRAGMA"):
        if token in {"FOR UPDATE", "AUTOINCREMENT", "PRAGMA"}:
            assert token not in text
        else:
            assert token in text
    assert "kind TEXT NOT NULL" in text
    assert '"authorization" TEXT,' in text
    assert "'authorized', 'not authorized'" in text
    assert "CREATE TABLE {schema}.record_history" in text

    def ddl_columns(table_name: str) -> tuple[str, ...]:
        block = text.split(f"CREATE TABLE {{schema}}.{table_name} (", 1)[1].split("\n);", 1)[0]
        ignored = {"PRIMARY", "FOREIGN", "UNIQUE", "CHECK", "CONSTRAINT"}
        return tuple(
            token
            for line in block.splitlines()
            if re.match(r'"?[a-z_]+"?\s+[A-Z]', line.strip())
            and (token := line.strip().split()[0].rstrip(",").strip('"')) not in ignored
        )

    assert tuple(TABLE_SPECS) == CURRENT_TABLES
    for table_name in CURRENT_TABLES:
        assert ddl_columns(table_name) == TABLE_SPECS[table_name].columns

        block = text.split(f"CREATE TABLE {{schema}}.{table_name} (", 1)[1].split("\n);", 1)[0]
        declarations = {
            line.strip().split()[0].rstrip(",").strip('"'): line.strip()
            for line in block.splitlines()
            if re.match(r'"?[a-z_]+"?\s+[A-Z]', line.strip())
            and line.strip().split()[0].rstrip(",").strip('"')
            not in {"PRIMARY", "FOREIGN", "UNIQUE", "CHECK", "CONSTRAINT"}
        }
        spec = TABLE_SPECS[table_name]
        inline_primary_key = tuple(
            column for column, declaration in declarations.items() if "PRIMARY KEY" in declaration
        )
        table_primary_key_lines = [
            line.strip() for line in block.splitlines() if line.strip().startswith("PRIMARY KEY")
        ]
        assert not (inline_primary_key and table_primary_key_lines), f"{table_name} primary-key form"
        assert len(table_primary_key_lines) <= 1, f"{table_name} primary-key count"
        if table_primary_key_lines:
            primary_key_columns = tuple(
                column.strip() for column in table_primary_key_lines[0].split("(", 1)[1].split(")", 1)[0].split(",")
            )
        else:
            primary_key_columns = inline_primary_key
        assert primary_key_columns == spec.identity_columns, f"{table_name} primary key"
        required = kernel_module._REQUIRED_COLUMNS[table_name] | frozenset(spec.identity_columns)
        for column in spec.columns:
            declaration = declarations[column]
            expected_type = (
                "JSONB"
                if column in spec.json_columns
                else "BOOLEAN"
                if column in spec.boolean_columns
                else "TIMESTAMPTZ"
                if column in kernel_module._TIMESTAMP_COLUMNS
                else "DATE"
                if column in kernel_module._DATE_COLUMNS
                else "INTEGER"
                if column in kernel_module._INTEGER_COLUMNS
                else "TEXT"
            )
            assert declaration.split()[1].rstrip(",") == expected_type, f"{table_name}.{column} type"
            actual_not_null = "NOT NULL" in declaration or "PRIMARY KEY" in declaration
            assert actual_not_null == (column in required), f"{table_name}.{column} nullability"
    assert ddl_columns("record_history") == (
        "history_id",
        "record_type",
        "record_id",
        "prior_version",
        "new_version",
        "prior_state",
        "new_state",
        "actor",
        "changed_at",
        "reason",
    )
    history_block = text.split("CREATE TABLE {schema}.record_history (", 1)[1].split("\n);", 1)[0]
    history_declarations = {
        line.strip().split()[0].rstrip(",").strip('"'): line.strip()
        for line in history_block.splitlines()
        if line.strip()
    }
    history_contract = {
        "history_id": ("BIGINT", True),
        "record_type": ("TEXT", True),
        "record_id": ("JSONB", True),
        "prior_version": ("INTEGER", False),
        "new_version": ("INTEGER", True),
        "prior_state": ("JSONB", False),
        "new_state": ("JSONB", True),
        "actor": ("TEXT", True),
        "changed_at": ("TIMESTAMPTZ", True),
        "reason": ("TEXT", True),
    }
    for column, (expected_type, required) in history_contract.items():
        declaration = history_declarations[column]
        assert declaration.split()[1].rstrip(",") == expected_type, f"record_history.{column} type"
        actual_not_null = "NOT NULL" in declaration or "PRIMARY KEY" in declaration
        assert actual_not_null == required, f"record_history.{column} nullability"
    assert "GENERATED ALWAYS AS IDENTITY PRIMARY KEY" in history_declarations["history_id"]
    assert sum("PRIMARY KEY" in declaration for declaration in history_declarations.values()) == 1


def test_schema_resource_hash_input_is_checkout_line_ending_invariant():
    lf = b"CREATE TABLE example (id INTEGER);\n"
    crlf = lf.replace(b"\n", b"\r\n")
    assert kernel_module._canonical_sql_resource_bytes(lf) == lf
    assert kernel_module._canonical_sql_resource_bytes(crlf) == lf
    with pytest.raises(PostgresKernelError, match="bare CR"):
        kernel_module._canonical_sql_resource_bytes(b"SELECT 1;\r")


@pytest.mark.parametrize(
    "forbidden",
    [
        "project_authorizations",
        "approval_state",
        "membership_role",
        "reviewer_precedence",
        "related_bridge_threads",
        "CREATE VIEW",
        "CREATE TRIGGER",
        "CREATE FUNCTION",
        "CREATE EXTENSION",
        "sqlite_",
    ],
)
def test_packaged_schema_has_no_legacy_or_compatibility_surface(forbidden):
    assert forbidden.lower() not in schema_sql_bytes().decode("utf-8").lower()


def test_schema_encodes_relationship_and_authorization_boundaries():
    text = schema_sql_bytes().decode("utf-8")
    work_items = text.split("CREATE TABLE {schema}.work_items", 1)[1].split("CREATE TABLE", 1)[0]
    memberships = text.split("CREATE TABLE {schema}.project_work_item_memberships", 1)[1].split("CREATE TABLE", 1)[0]
    harnesses = text.split("CREATE TABLE {schema}.harnesses", 1)[1].split("CREATE TABLE", 1)[0]

    assert "project_name" not in work_items
    assert "subproject_name" not in work_items
    assert "UNIQUE (project_id, work_item_id)" in memberships
    assert "membership_role" not in memberships
    assert "role " not in harnesses
    assert "reviewer_precedence" not in harnesses


def test_canonical_json_is_compact_sorted_unicode_preserving_and_lf_terminated():
    value = {"z": "Ã©", "a": [True, None, 3]}

    assert canonical_json_bytes(value) == '{"a":[true,null,3],"z":"Ã©"}\n'.encode()
    assert canonical_sha256(value) == hashlib.sha256(canonical_json_bytes(value)).hexdigest()
    assert canonical_json_bytes({"value": "Ã©"}) != canonical_json_bytes({"value": "e\u0301"})


def test_canonical_json_preserves_precise_fractional_numbers_without_exponents():
    value = parse_json_bytes(b'{"n":0.123456789012345678901234567890,"e":1e2,"z":-0.0}')

    assert value == {
        "n": Decimal("0.123456789012345678901234567890"),
        "e": Decimal("1E+2"),
        "z": Decimal("-0.0"),
    }
    assert canonical_json_bytes(value) == (b'{"e":100,"n":0.123456789012345678901234567890,"z":0.0}\n')
    assert kernel_module._postgres_json_dumps(value) == ('{"e":100,"n":0.123456789012345678901234567890,"z":0.0}')


def test_canonical_json_rejects_numbers_outside_postgresql_jsonb_numeric_range():
    with pytest.raises(PostgresKernelError, match="PostgreSQL numeric range"):
        parse_json_bytes(b'{"n":1e131072}')


def test_canonical_json_integer_parsing_is_independent_of_python_digit_limit():
    digits = b"9" * 5000
    value = parse_json_bytes(b'{"n":' + digits + b"}")

    assert canonical_json_bytes(value) == b'{"n":' + digits + b"}\n"


def test_canonical_json_round_trips_postgresql_maximum_integer_digits():
    digits = b"9" * 131_072
    value = parse_json_bytes(b'{"n":' + digits + b"}")

    assert canonical_json_bytes(value) == b'{"n":' + digits + b"}\n"


@pytest.mark.parametrize(
    "token,accepted",
    [
        ("1e131071", True),
        ("1e131072", False),
        ("1e-16383", True),
        ("1e-16384", False),
    ],
)
def test_canonical_json_enforces_exact_postgresql_numeric_boundaries(token, accepted):
    raw = f'{{"n":{token}}}'.encode()
    if not accepted:
        with pytest.raises(PostgresKernelError, match="PostgreSQL numeric range"):
            parse_json_bytes(raw)
        return

    parsed = parse_json_bytes(raw)
    rendered = canonical_json_bytes(parsed)
    assert b"e" not in rendered.lower()
    assert len(rendered) > 16_000


def test_canonical_json_huge_exponent_has_stable_invalid_json_error():
    with pytest.raises(PostgresKernelError) as error:
        parse_json_bytes(b'{"n":1e999999999999999999999999999999999999999999}')
    assert error.value.code == "invalid_json"


def test_postgresql_json_text_readback_preserves_precise_fractional_numbers():
    spec = TABLE_SPECS["documents"]
    raw = _row(
        "documents",
        id="DOC-1",
        version=1,
        title="Document",
        category="test",
        tags="[0.123456789012345678901234567890, 100, 0.0]",
        status="active",
        changed_by="actor",
        changed_at="2026-09-01T00:00:00+00:00",
        change_reason="test",
    )

    row = kernel_module._normalize_pg_row(raw, spec)

    assert canonical_json_bytes(row["tags"]) == b"[0.123456789012345678901234567890,100,0.0]\n"


@pytest.mark.parametrize(
    "raw,code",
    [
        (b'{"x":1,"x":2}', "duplicate_json_key"),
        (b'{"x":NaN}', "invalid_json"),
        (b"\xef\xbb\xbf{}", "invalid_json"),
        (b'{"x":"\\ud800"}', "invalid_text"),
    ],
)
def test_strict_json_parser_rejects_ambiguous_or_non_rfc_input(raw, code):
    with pytest.raises(PostgresKernelError) as error:
        parse_json_bytes(raw)
    assert error.value.code == code


@pytest.mark.parametrize(
    "raw",
    [
        '{"value":' + ("9" * 131_073) + "}",
        ("[" * 1100) + "0" + ("]" * 1100),
    ],
    ids=["oversized-integer", "excessive-nesting"],
)
def test_json_resource_limits_are_stable_at_cli_boundary(tmp_path, raw):
    snapshot = tmp_path / "snapshot.db"
    snapshot.write_bytes(b"snapshot")
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(raw, encoding="utf-8")
    result = CliRunner().invoke(
        main,
        [
            "db",
            "postgres",
            "export-current",
            "--sqlite-snapshot",
            str(snapshot),
            "--transform-plan",
            str(plan_path),
            "--output",
            str(tmp_path / "out.json"),
        ],
    )
    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["error"]["code"] == "invalid_json"
    assert result.output == canonical_json_bytes(payload).decode("utf-8")


def test_sqlite_inventory_has_exact_shape_ordering_and_hash_contract():
    tables = [
        {"name": "zeta", "type": "table", "ncol": 1, "wr": 0, "strict": 1},
        {"name": "Alpha", "type": "virtual", "ncol": 1, "wr": 1, "strict": 0},
    ]
    columns = {
        "zeta": [{"cid": 0, "name": "id", "type": "TEXT", "notnull": 1, "dflt_value": None, "pk": 1, "hidden": 0}],
        "Alpha": [
            {"cid": 0, "name": "value", "type": "BLOB", "notnull": 0, "dflt_value": "x'00'", "pk": 0, "hidden": 2}
        ],
    }

    inventory = normalize_table_inventory(tables, columns)

    assert inventory["format"] == SQLITE_INVENTORY_FORMAT
    assert [row["name"] for row in inventory["tables"]] == ["Alpha", "zeta"]
    assert inventory["tables"][0]["columns"][0] == {
        "cid": 0,
        "declared_type": "BLOB",
        "default_sql": "x'00'",
        "hidden": 2,
        "name": "value",
        "not_null": False,
        "primary_key_ordinal": 0,
    }
    assert canonical_sha256(inventory) == hashlib.sha256(canonical_json_bytes(inventory)).hexdigest()


def test_sqlite_inventory_rejects_ascii_case_duplicate_names():
    tables = [
        {"name": "Records", "type": "table", "ncol": 0, "wr": 0, "strict": 0},
        {"name": "records", "type": "table", "ncol": 0, "wr": 0, "strict": 0},
    ]
    with pytest.raises(PostgresKernelError, match="Duplicate SQLite table name"):
        normalize_table_inventory(tables, {"Records": [], "records": []})


@pytest.mark.parametrize(
    "column_update",
    [
        {"cid": -1},
        {"notnull": 2},
        {"notnull": 1.0},
        {"hidden": 4},
        {"pk": -1},
        {"name": "bad\x00name"},
    ],
)
def test_sqlite_inventory_rejects_invalid_column_metadata(column_update):
    table = {"name": "records", "type": "table", "ncol": 1, "wr": 0, "strict": 0}
    column = {"cid": 0, "name": "id", "type": "TEXT", "notnull": 1, "dflt_value": None, "pk": 1, "hidden": 0}
    column.update(column_update)
    with pytest.raises(PostgresKernelError):
        normalize_table_inventory([table], {"records": [column]})


def test_transform_plan_accepts_only_complete_exact_counted_partition():
    plan = _plan()
    assert validate_transform_plan(plan) == plan

    plan["project_dependencies"]["preserve_dependency_ids"] = ["opaque-retire"]
    with pytest.raises(PostgresKernelError, match="Duplicate dependency id"):
        validate_transform_plan(plan)


def test_transform_plan_rejects_unknown_key_and_boolean_count():
    plan = _plan()
    plan["unexpected"] = True
    with pytest.raises(PostgresKernelError, match="missing or unknown keys"):
        validate_transform_plan(plan)

    plan = _plan()
    plan["projects"]["expected_total"] = True
    with pytest.raises(PostgresKernelError, match="nonnegative integer"):
        validate_transform_plan(plan)

    plan = _plan()
    plan["schema_version"] = True
    with pytest.raises(PostgresKernelError, match="Unsupported transform-plan"):
        validate_transform_plan(plan)


def test_empty_manifest_is_complete_and_canonical():
    manifest = normalize_manifest(_empty_manifest())
    assert tuple(manifest["tables"]) == MIGRATION_TABLES
    assert parse_json_bytes(canonical_json_bytes(manifest)) == manifest


def test_immutable_bindings_preserve_identity_precision_and_have_no_version_history():
    original = {
        "native_context_id": "native-original",
        "session_context_id": "SENV-original",
        "subject": "gtkb",
        "role": "prime-builder",
        "created_at": "2026-09-01T00:00:00.123456Z",
        "minimum_idempotency_identity": "original-request",
    }
    manifest = _empty_manifest()
    manifest["tables"]["session_init_bindings"] = [original]
    normalized = normalize_manifest(manifest)["tables"]["session_init_bindings"]
    assert normalized == [{**original, "created_at": "2026-09-01T00:00:00.123456+00:00"}]
    assert "version" not in normalized[0] and "changed_at" not in normalized[0]
    for invalid in (
        {**original, "version": 1},
        {**original, "role": "pb"},
        {**original, "subject": "unspecified"},
        {**original, "created_at": "2026-09-01T00:00:00"},
        {**original, "created_at": None},
        {**original, "minimum_idempotency_identity": ""},
    ):
        manifest["tables"]["session_init_bindings"] = [invalid]
        with pytest.raises(PostgresKernelError):
            normalize_manifest(manifest)
    for duplicate in (original, {**original, "native_context_id": "another-native-context"}):
        manifest["tables"]["session_init_bindings"] = [original, duplicate]
        with pytest.raises(PostgresKernelError, match="identities must be unique"):
            normalize_manifest(manifest)


def test_manifest_rejects_missing_table_and_historical_version():
    manifest = _empty_manifest()
    del manifest["tables"][CURRENT_TABLES[-1]]
    with pytest.raises(PostgresKernelError, match="missing or unknown keys"):
        normalize_manifest(manifest)

    manifest = _empty_manifest()
    spec = TABLE_SPECS["test_plans"]
    manifest["tables"]["test_plans"] = [
        {
            column: ({"id": "PLAN-1", "version": 2, "title": "Plan", "status": "active"}.get(column))
            for column in spec.columns
        }
    ]
    with pytest.raises(PostgresKernelError, match="restart at 1"):
        normalize_manifest(manifest)

    manifest = _empty_manifest()
    manifest["schema_version"] = True
    with pytest.raises(PostgresKernelError, match="Unsupported migration-manifest"):
        normalize_manifest(manifest)


def test_manifest_rejects_required_type_range_and_missing_reference():
    manifest = _empty_manifest()
    manifest["tables"]["test_plans"] = [
        _row(
            "test_plans",
            id="PLAN-1",
            version=2**31,
            title="Plan",
            status="active",
            changed_by="actor",
            changed_at="2026-09-01T00:00:00+00:00",
            change_reason="reason",
        )
    ]
    with pytest.raises(PostgresKernelError, match="outside PostgreSQL range"):
        normalize_manifest(manifest, require_version_one=False)

    manifest = _empty_manifest()
    manifest["tables"]["tests"] = [
        _row(
            "tests",
            id="TEST-1",
            version=1,
            title="Test",
            spec_id="SPEC-MISSING",
            test_type="pytest",
            expected_outcome="pass",
            changed_by="actor",
            changed_at="2026-09-01T00:00:00+00:00",
            change_reason="reason",
        )
    ]
    with pytest.raises(PostgresKernelError, match="references a missing current record"):
        normalize_manifest(manifest)

    manifest = _empty_manifest()
    manifest["tables"]["test_plans"] = [
        _row(
            "test_plans",
            id="PLAN-1",
            version=1,
            title=None,
            status="active",
            changed_by="actor",
            changed_at="2026-09-01T00:00:00+00:00",
            change_reason="reason",
        )
    ]
    with pytest.raises(PostgresKernelError, match="title must not be null"):
        normalize_manifest(manifest)


def test_manifest_rejects_duplicate_relationship_pair():
    manifest = _empty_manifest()
    manifest["tables"]["projects"] = [
        _row(
            "projects",
            id="PROJECT-1",
            version=1,
            name="Project",
            status="active",
            authorization="authorized",
            changed_by="actor",
            changed_at="2026-09-01T00:00:00+00:00",
            change_reason="reason",
        )
    ]
    manifest["tables"]["work_items"] = [
        _row(
            "work_items",
            id="WI-1",
            version=1,
            title="Work",
            origin="owner",
            component="kernel",
            resolution_status="open",
            stage="created",
            changed_by="actor",
            changed_at="2026-09-01T00:00:00+00:00",
            change_reason="reason",
        )
    ]
    manifest["tables"]["project_work_item_memberships"] = [
        _row(
            "project_work_item_memberships",
            id=membership_id,
            version=1,
            project_id="PROJECT-1",
            work_item_id="WI-1",
            status="active",
            changed_by="actor",
            changed_at="2026-09-01T00:00:00+00:00",
            change_reason="reason",
        )
        for membership_id in ("MEMBERSHIP-1", "MEMBERSHIP-2")
    ]
    with pytest.raises(PostgresKernelError, match="Duplicate current project/work-item relationship"):
        normalize_manifest(manifest)


def _work_model_manifest():
    manifest = _empty_manifest()
    metadata = {
        "version": 1,
        "changed_by": "test",
        "changed_at": "2026-09-01T00:00:00+00:00",
        "change_reason": "fixture",
    }
    manifest["tables"]["projects"] = [
        _row("projects", id=pid, name=pid, status="active", authorization="authorized", **metadata)
        for pid in ["PROJECT-ONE", "PROJECT-TWO"]
    ]
    manifest["tables"]["work_items"] = [
        _row(
            "work_items",
            id="WI-ONE",
            title="One",
            origin="owner",
            component="kernel",
            resolution_status="open",
            stage="created",
            **metadata,
        )
    ]
    manifest["tables"]["project_work_item_memberships"] = [
        _row(
            "project_work_item_memberships",
            id="MEMBER-ONE",
            project_id="PROJECT-ONE",
            work_item_id="WI-ONE",
            status="active",
            **metadata,
        )
    ]
    return manifest


def test_manifest_rejects_two_active_parents_even_with_distinct_pairs():
    manifest = _work_model_manifest()
    first = manifest["tables"]["project_work_item_memberships"][0]
    manifest["tables"]["project_work_item_memberships"].append(
        {**first, "id": "MEMBER-TWO", "project_id": "PROJECT-TWO"}
    )
    with pytest.raises(PostgresKernelError, match="multiple active parent"):
        normalize_manifest(manifest)
    first["status"] = "removed"
    assert normalize_manifest(manifest)["tables"]["project_work_item_memberships"]


@pytest.mark.parametrize("membership_status", [None, "removed"])
@pytest.mark.parametrize("work_status", ["open", "verified"])
def test_manifest_requires_one_active_parent_for_every_work_item(membership_status, work_status):
    manifest = _work_model_manifest()
    manifest["tables"]["work_items"][0]["resolution_status"] = work_status
    if membership_status is None:
        manifest["tables"]["project_work_item_memberships"] = []
    else:
        manifest["tables"]["project_work_item_memberships"][0]["status"] = membership_status
    with pytest.raises(PostgresKernelError, match="requires one active parent") as refused:
        normalize_manifest(manifest)
    assert refused.value.details == {"missing_parent_count": 1, "work_item_ids": ["WI-ONE"]}


def test_manifest_rejects_program_work_item_membership():
    manifest = _work_model_manifest()
    manifest["tables"]["projects"][0].update(kind="program", authorization=None)
    with pytest.raises(PostgresKernelError, match="program cannot contain work items"):
        normalize_manifest(manifest)


def test_manifest_requires_a_program_parent_for_execution_projects():
    manifest = _work_model_manifest()
    manifest["tables"]["projects"][0]["parent_project_id"] = "PROJECT-TWO"
    with pytest.raises(PostgresKernelError, match="Only a program"):
        normalize_manifest(manifest)
    manifest["tables"]["projects"][1].update(kind="program", authorization=None)
    assert normalize_manifest(manifest)["tables"]["projects"]


def test_source_transform_preserves_project_authorization_and_program_kind():
    source = {name: [] for name in MIGRATION_TABLES}
    metadata = {
        "version": 7,
        "changed_by": "test",
        "changed_at": "2026-09-01T00:00:00+00:00",
        "change_reason": "source",
    }
    source["projects"] = [
        _row(
            "projects",
            id="PROJECT-A",
            name="A",
            kind="project",
            authorization="not authorized",
            status="active",
            **metadata,
        ),
        _row(
            "projects",
            id="PROJECT-B",
            name="B",
            kind="project",
            authorization="authorized",
            status="active",
            **metadata,
        ),
        _row("projects", id="PROGRAM-C", name="C", kind="program", authorization=None, status="active", **metadata),
    ]
    plan = _plan()
    plan["projects"] = {
        "expected_total": 3,
        "expected_authorized": 1,
        "expected_not_authorized": 1,
        "expected_programs": 1,
    }
    plan["project_dependencies"].update(
        expected_source_count=0,
        expected_active_after=0,
        expected_retired_after=0,
        expected_gate_transition_count=0,
        retire_dependency_ids=[],
        preserve_dependency_ids=[],
    )
    result = kernel_module._transform_source_rows(source, plan)
    assert {row["id"]: (row["kind"], row["authorization"]) for row in result["projects"]} == {
        "PROJECT-A": ("project", "not authorized"),
        "PROJECT-B": ("project", "authorized"),
        "PROGRAM-C": ("program", None),
    }
    assert {row["version"] for row in result["projects"]} == {1}
    validate_transform_plan(plan)
    plan["projects"]["authorization_default"] = "authorized"
    with pytest.raises(PostgresKernelError, match="keys"):
        validate_transform_plan(plan)


def test_manifest_canonicalizes_timestamps_to_utc_and_rejects_naive_values():
    manifest = _empty_manifest()
    spec = TABLE_SPECS["test_plans"]
    row = {
        "id": "PLAN-1",
        "version": 1,
        "title": "Plan",
        "description": None,
        "status": "active",
        "changed_by": "actor",
        "changed_at": "2026-09-01T01:00:00+01:00",
        "change_reason": "reason",
    }
    manifest["tables"]["test_plans"] = [{column: row.get(column) for column in spec.columns}]
    normalized = normalize_manifest(manifest)
    assert normalized["tables"]["test_plans"][0]["changed_at"] == "2026-09-01T00:00:00+00:00"

    manifest = _empty_manifest()
    row["changed_at"] = "2026-09-01T00:00:00"
    manifest["tables"]["test_plans"] = [{column: row.get(column) for column in spec.columns}]
    with pytest.raises(PostgresKernelError, match="must include an offset"):
        normalize_manifest(manifest)


@pytest.mark.parametrize(
    "changed_at",
    ["0001-01-01T00:00:00+14:00", "9999-12-31T23:59:59-14:00"],
)
def test_manifest_rejects_timestamp_that_overflows_when_normalized_to_utc(changed_at):
    manifest = _empty_manifest()
    manifest["tables"]["test_plans"] = [
        _row(
            "test_plans",
            id="PLAN-1",
            version=1,
            title="Plan",
            status="active",
            changed_by="actor",
            changed_at=changed_at,
            change_reason="reason",
        )
    ]
    with pytest.raises(PostgresKernelError) as error:
        normalize_manifest(manifest)
    assert error.value.code == "invalid_timestamp"


def test_export_rejects_noncanonical_plan_before_sqlite_connection(tmp_path):
    snapshot = tmp_path / "snapshot.db"
    snapshot.write_bytes(b"snapshot")
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(_plan(), indent=2), encoding="utf-8")
    output = tmp_path / "manifest.json"

    with pytest.raises(PostgresKernelError) as error:
        PostgresKernel(PostgreSQLConfig()).export_current(
            sqlite_snapshot=snapshot,
            transform_plan=plan_path,
            output=output,
            live_sqlite_source=None,
        )
    assert error.value.code == "transform_plan_not_canonical"
    assert not output.exists()


def test_export_rejects_live_source_and_sidecar_before_sqlite_connection(tmp_path):
    snapshot = tmp_path / "snapshot.db"
    snapshot.write_bytes(b"snapshot")
    plan_path = tmp_path / "plan.json"
    plan_path.write_bytes(canonical_json_bytes(_plan()))

    with pytest.raises(PostgresKernelError) as live_error:
        PostgresKernel(PostgreSQLConfig()).export_current(
            sqlite_snapshot=snapshot,
            transform_plan=plan_path,
            output=tmp_path / "out.json",
            live_sqlite_source=snapshot,
        )
    assert live_error.value.code == "live_source_forbidden"

    (tmp_path / "snapshot.db-wal").write_bytes(b"sidecar")
    with pytest.raises(PostgresKernelError) as sidecar_error:
        PostgresKernel(PostgreSQLConfig()).export_current(
            sqlite_snapshot=snapshot,
            transform_plan=plan_path,
            output=tmp_path / "out.json",
            live_sqlite_source=None,
        )
    assert sidecar_error.value.code == "snapshot_sidecar_present"


def test_export_rejects_hard_link_to_live_source_before_sqlite_connection(tmp_path):
    live_source = tmp_path / "live.db"
    live_source.write_bytes(b"snapshot")
    snapshot = tmp_path / "alias.db"
    os.link(live_source, snapshot)
    plan_path = tmp_path / "plan.json"
    plan_path.write_bytes(canonical_json_bytes(_plan()))

    with pytest.raises(PostgresKernelError) as error:
        PostgresKernel(PostgreSQLConfig()).export_current(
            sqlite_snapshot=snapshot,
            transform_plan=plan_path,
            output=tmp_path / "out.json",
            live_sqlite_source=live_source,
        )
    assert error.value.code == "live_source_forbidden"


def test_export_wraps_snapshot_filesystem_errors_without_output(tmp_path, monkeypatch):
    snapshot = tmp_path / "snapshot.db"
    snapshot.write_bytes(b"snapshot")
    plan_path = tmp_path / "plan.json"
    plan_path.write_bytes(canonical_json_bytes(_plan()))
    output = tmp_path / "out.json"

    def unreadable(_path: object) -> str:
        raise OSError("injected read failure")

    monkeypatch.setattr(kernel_module, "_hash_file", unreadable)
    with pytest.raises(PostgresKernelError) as error:
        PostgresKernel(PostgreSQLConfig()).export_current(
            sqlite_snapshot=snapshot,
            transform_plan=plan_path,
            output=output,
            live_sqlite_source=None,
        )
    assert error.value.code == "snapshot_preflight_failed"
    assert not output.exists()


def test_export_translates_close_only_failure_without_publishing(tmp_path, monkeypatch):
    snapshot = tmp_path / "snapshot.db"
    snapshot.write_bytes(b"snapshot")
    inventory = {
        "format": SQLITE_INVENTORY_FORMAT,
        "tables": [{"name": table_name} for table_name in sorted(kernel_module.SOURCE_TABLES)],
    }
    plan = _plan(snapshot.read_bytes())
    plan["source"]["expected_table_inventory_sha256"] = canonical_sha256(inventory)
    plan_path = tmp_path / "plan.json"
    plan_path.write_bytes(canonical_json_bytes(plan))
    output = tmp_path / "out.json"

    class ClosingFailure:
        row_factory: object = None

        def execute(self, query: str) -> ClosingFailure:
            self.query = query
            return self

        def fetchone(self) -> tuple[object, ...]:
            return (1,) if self.query == "PRAGMA query_only" else (7,)

        def fetchall(self) -> list[tuple[str]]:
            return [("ok",)]

        def close(self) -> None:
            raise sqlite3.OperationalError("injected close failure")

    monkeypatch.setattr(kernel_module, "_sqlite_inventory", lambda _connection: inventory)
    monkeypatch.setattr(
        kernel_module,
        "_transform_source_rows",
        lambda _source, _plan_value: {table_name: [] for table_name in MIGRATION_TABLES},
    )
    monkeypatch.setattr(kernel_module, "_current_sqlite_rows", lambda _connection, _table: [])
    kernel = PostgresKernel(
        PostgreSQLConfig(),
        sqlite_connector=lambda *_args, **_kwargs: ClosingFailure(),  # type: ignore[arg-type]
    )

    with pytest.raises(PostgresKernelError) as error:
        kernel.export_current(
            sqlite_snapshot=snapshot,
            transform_plan=plan_path,
            output=output,
            live_sqlite_source=None,
        )

    assert error.value.code == "snapshot_read_failed"
    assert str(error.value) == "Immutable SQLite snapshot close failed"
    assert not output.exists()


def test_export_preflight_returns_exact_source_after_shared_immutable_inspection(tmp_path, monkeypatch):
    snapshot = tmp_path / "snapshot with space.db"
    snapshot.write_bytes(b"immutable-snapshot")
    inventory = {
        "format": SQLITE_INVENTORY_FORMAT,
        "tables": [{"name": table_name} for table_name in sorted(kernel_module.SOURCE_TABLES)],
    }
    queries: list[str] = []
    closed = False
    connector_calls: list[tuple[str, bool]] = []

    class Connection:
        row_factory: object = None

        def execute(self, query: str) -> Connection:
            queries.append(query)
            return self

        def fetchone(self) -> tuple[int]:
            return (1,) if queries[-1] == "PRAGMA query_only" else (7,)

        def fetchall(self) -> list[tuple[str]]:
            return [("ok",)]

        def close(self) -> None:
            nonlocal closed
            closed = True

    def connect(database_uri: str, *, uri: bool) -> Connection:
        connector_calls.append((database_uri, uri))
        return Connection()

    monkeypatch.setattr(kernel_module, "_sqlite_inventory", lambda _connection: inventory)
    result = PostgresKernel(
        PostgreSQLConfig(),
        sqlite_connector=connect,  # type: ignore[arg-type]
    ).preflight_export_current(sqlite_snapshot=snapshot, live_sqlite_source=None)

    assert result == {
        "expected_pragma_user_version": 7,
        "expected_table_inventory_sha256": canonical_sha256(inventory),
        "sqlite_snapshot_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        "sqlite_snapshot_size_bytes": snapshot.stat().st_size,
    }
    assert connector_calls == [(snapshot.resolve().as_uri() + "?mode=ro&immutable=1", True)]
    assert queries == [
        "PRAGMA query_only=ON",
        "PRAGMA query_only",
        "PRAGMA integrity_check",
        "PRAGMA user_version",
    ]
    assert closed is True


def test_preflight_and_export_dispatch_through_one_inspection_implementation(tmp_path, monkeypatch):
    snapshot = tmp_path / "snapshot.db"
    snapshot.write_bytes(b"snapshot")
    source = _plan(snapshot.read_bytes())["source"]
    plan_path = tmp_path / "plan.json"
    plan_path.write_bytes(canonical_json_bytes(_plan(snapshot.read_bytes())))
    output = tmp_path / "manifest.json"
    calls: list[tuple[Path, Path | None]] = []
    connection = object()

    @contextmanager
    def shared_inspector(*, sqlite_snapshot: Path, live_sqlite_source: Path | None):
        calls.append((sqlite_snapshot, live_sqlite_source))
        yield connection, source

    kernel = PostgresKernel(PostgreSQLConfig())
    monkeypatch.setattr(kernel, "_inspect_sqlite_snapshot", shared_inspector)
    monkeypatch.setattr(kernel_module, "_current_sqlite_rows", lambda seen, _table: [] if seen is connection else 1 / 0)
    monkeypatch.setattr(
        kernel_module,
        "_transform_source_rows",
        lambda _rows, _plan_value: {table_name: [] for table_name in MIGRATION_TABLES},
    )

    assert (
        kernel.preflight_export_current(
            sqlite_snapshot=snapshot,
            live_sqlite_source=tmp_path / "live.db",
        )
        == source
    )
    export_result = kernel.export_current(
        sqlite_snapshot=snapshot,
        transform_plan=plan_path,
        output=output,
        live_sqlite_source=tmp_path / "live.db",
    )

    assert calls == [(snapshot, tmp_path / "live.db"), (snapshot, tmp_path / "live.db")]
    assert export_result["status"] == "ok"
    assert output.exists()


def test_export_preflight_propagates_post_read_snapshot_drift(tmp_path, monkeypatch):
    snapshot = tmp_path / "snapshot.db"
    snapshot.write_bytes(b"snapshot")
    inventory = {
        "format": SQLITE_INVENTORY_FORMAT,
        "tables": [{"name": table_name} for table_name in sorted(kernel_module.SOURCE_TABLES)],
    }
    digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    hash_calls = 0

    class Connection:
        row_factory: object = None
        query = ""

        def execute(self, query: str) -> Connection:
            self.query = query
            return self

        def fetchone(self) -> tuple[int]:
            return (1,) if self.query == "PRAGMA query_only" else (7,)

        def fetchall(self) -> list[tuple[str]]:
            return [("ok",)]

        def close(self) -> None:
            return None

    def changed_hash(_path: Path) -> str:
        nonlocal hash_calls
        hash_calls += 1
        return digest if hash_calls == 1 else "f" * 64

    monkeypatch.setattr(kernel_module, "_hash_file", changed_hash)
    monkeypatch.setattr(kernel_module, "_sqlite_inventory", lambda _connection: inventory)
    kernel = PostgresKernel(
        PostgreSQLConfig(),
        sqlite_connector=lambda *_args, **_kwargs: Connection(),  # type: ignore[arg-type]
    )

    with pytest.raises(PostgresKernelError) as error:
        kernel.preflight_export_current(sqlite_snapshot=snapshot, live_sqlite_source=None)
    assert error.value.code == "snapshot_changed"


def test_export_preflight_rejects_incomplete_source_inventory(tmp_path, monkeypatch):
    snapshot = tmp_path / "snapshot.db"
    snapshot.write_bytes(b"snapshot")

    class Connection:
        row_factory: object = None
        query = ""

        def execute(self, query: str) -> Connection:
            self.query = query
            return self

        def fetchone(self) -> tuple[int]:
            return (1,) if self.query == "PRAGMA query_only" else (7,)

        def fetchall(self) -> list[tuple[str]]:
            return [("ok",)]

        def close(self) -> None:
            return None

    monkeypatch.setattr(
        kernel_module,
        "_sqlite_inventory",
        lambda _connection: {"format": SQLITE_INVENTORY_FORMAT, "tables": []},
    )
    kernel = PostgresKernel(
        PostgreSQLConfig(),
        sqlite_connector=lambda *_args, **_kwargs: Connection(),  # type: ignore[arg-type]
    )

    with pytest.raises(PostgresKernelError) as error:
        kernel.preflight_export_current(sqlite_snapshot=snapshot, live_sqlite_source=None)
    assert error.value.code == "snapshot_table_set_mismatch"


def test_output_publication_never_overwrites_a_racing_writer(tmp_path, monkeypatch):
    output = tmp_path / "out.json"

    def racing_link(_source: object, destination: object) -> None:
        Path(destination).write_bytes(b"rival\n")
        raise FileExistsError

    monkeypatch.setattr(kernel_module.os, "link", racing_link)
    with pytest.raises(PostgresKernelError) as error:
        kernel_module._publish_bytes(output, b"ours\n")
    assert error.value.code == "output_exists"
    assert output.read_bytes() == b"rival\n"


def test_output_publication_does_not_report_failure_after_final_link(tmp_path, monkeypatch):
    output = tmp_path / "out.json"
    original_unlink = Path.unlink
    failed_once = False

    def transient_unlink(path: Path, *args: object, **kwargs: object) -> None:
        nonlocal failed_once
        if path.name.startswith(".out.json.") and path.suffix == ".tmp" and not failed_once:
            failed_once = True
            raise PermissionError("injected transient cleanup failure")
        original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", transient_unlink)

    assert kernel_module._publish_bytes(output, b"ours\n") == "ok"
    assert output.read_bytes() == b"ours\n"
    assert not list(tmp_path.glob(".out.json.*.tmp"))


def test_transform_surfaces_unknown_specification_source_link():
    source_rows = {table_name: [] for table_name in MIGRATION_TABLES}
    source_rows["specification_deliberation_sources"] = [{"spec_id": "SPEC-MISSING", "spec_version": 1}]
    plan = _plan()
    plan["projects"].update(
        expected_total=0,
        expected_authorized=0,
        expected_not_authorized=0,
        expected_programs=0,
    )
    plan["project_dependencies"].update(
        expected_source_count=0,
        expected_active_after=0,
        expected_retired_after=0,
        expected_gate_transition_count=0,
        preserve_dependency_ids=[],
        retire_dependency_ids=[],
    )
    with pytest.raises(PostgresKernelError, match="unknown current specification"):
        kernel_module._transform_source_rows(source_rows, plan)


class _FakeCursor:
    def __init__(self, existing: dict[str, Any]) -> None:
        self.existing = existing
        self.statements: list[str] = []
        self._next: dict[str, Any] | None = None
        self.final = dict(existing)

    def execute(self, query: object, _params: object = None) -> None:
        rendered = query.as_string() if hasattr(query, "as_string") else str(query)
        self.statements.append(rendered)
        if "current_schema()" in rendered:
            self._next = {"schema_name": "isolated"}
        elif "FOR UPDATE" in rendered:
            self._next = dict(self.existing)
        elif rendered.startswith("UPDATE") or 'UPDATE "isolated"' in rendered:
            self.final["version"] = int(self.existing["version"]) + 1
            self.final["status"] = "verified"
        elif rendered.startswith("SELECT") and "set_config" not in rendered:
            self._next = dict(self.final)

    def fetchone(self) -> dict[str, Any] | None:
        result = self._next
        self._next = None
        return result


class _FakeConnection:
    def __init__(self, cursor: _FakeCursor) -> None:
        self._cursor = cursor

    def __enter__(self) -> _FakeConnection:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def transaction(self) -> _FakeConnection:
        return self

    def cursor(self) -> _FakeCursor:
        return self._cursor


def _test_plan_state(version: int, status: str) -> dict[str, Any]:
    return {
        "id": "PLAN-1",
        "version": version,
        "title": "Plan",
        "description": None,
        "status": status,
        "changed_by": "actor",
        "changed_at": "2026-09-01T00:00:00+00:00",
        "change_reason": "reason",
    }


def test_mutation_locks_then_histories_then_updates_then_reads_back(monkeypatch):
    cursor = _FakeCursor(_test_plan_state(1, "active"))
    connection = _FakeConnection(cursor)
    kernel = PostgresKernel(PostgreSQLConfig(), connector=lambda **_kwargs: connection)
    monkeypatch.setattr(kernel, "_require_exact_schema", lambda *_args: None)

    result = kernel.mutate_current(
        table="test_plans",
        identity={"id": "PLAN-1"},
        expected_version=1,
        new_state=_test_plan_state(1, "verified"),
        actor="actor",
        reason="verified",
    )

    lock_index = next(index for index, statement in enumerate(cursor.statements) if "FOR UPDATE" in statement)
    history_index = next(index for index, statement in enumerate(cursor.statements) if "record_history" in statement)
    update_index = next(index for index, statement in enumerate(cursor.statements) if statement.startswith("UPDATE"))
    assert lock_index < history_index < update_index
    assert cursor.statements[-1].startswith("SELECT")
    assert result["status"] == "updated"
    assert result["record"]["version"] == 2


def test_stale_mutation_is_cas_conflict_with_no_history_or_update(monkeypatch):
    cursor = _FakeCursor(_test_plan_state(2, "active"))
    connection = _FakeConnection(cursor)
    kernel = PostgresKernel(PostgreSQLConfig(), connector=lambda **_kwargs: connection)
    monkeypatch.setattr(kernel, "_require_exact_schema", lambda *_args: None)

    with pytest.raises(PostgresKernelError) as error:
        kernel.mutate_current(
            table="test_plans",
            identity={"id": "PLAN-1"},
            expected_version=1,
            new_state=_test_plan_state(1, "verified"),
            actor="actor",
            reason="verified",
        )
    assert error.value.code == "cas_conflict"
    assert not any("record_history" in statement for statement in cursor.statements)
    assert not any(statement.startswith("UPDATE") for statement in cursor.statements)


@pytest.mark.parametrize(
    "identity,state_update",
    [
        ({"id": ""}, {"id": ""}),
        ({"id": "PLAN-1"}, {"title": None}),
        ({"id": "PLAN-1"}, {"status": 7}),
    ],
)
def test_invalid_mutation_state_refuses_before_connection(identity, state_update):
    state = _test_plan_state(1, "active")
    state.update(state_update)
    with pytest.raises(PostgresKernelError) as error:
        PostgresKernel(PostgreSQLConfig()).mutate_current(
            table="test_plans",
            identity=identity,
            expected_version=0,
            new_state=state,
            actor="actor",
            reason="reason",
        )
    assert error.value.code in {"invalid_identity", "invalid_state"}


def test_postgres_cli_exposes_exact_five_commands_and_no_json_switch():
    result = CliRunner().invoke(main, ["db", "postgres", "--help"])
    assert result.exit_code == 0
    postgres_group = main.commands["db"].commands["postgres"]  # type: ignore[attr-defined]
    commands = set(postgres_group.commands)  # type: ignore[attr-defined]
    assert commands == {"init", "status", "export-current", "import-current", "readback-current"}
    assert "--json" not in result.output


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["--transform-plan", "missing-plan.json"],
        ["--output", "must-not-exist.json"],
        ["--preflight-only", "--transform-plan", "missing-plan.json"],
        ["--preflight-only", "--output", "must-not-exist.json"],
        [
            "--preflight-only",
            "--transform-plan",
            "missing-plan.json",
            "--output",
            "must-not-exist.json",
        ],
    ],
)
def test_export_cli_invalid_mode_is_typed_before_config_or_path_io(tmp_path, monkeypatch, arguments):
    def forbidden_config(_ctx: object) -> None:
        raise AssertionError("configuration resolved before export mode validation")

    monkeypatch.setattr(cli_module, "_resolve_config", forbidden_config)
    missing_snapshot = tmp_path / "missing-snapshot.db"
    result = CliRunner().invoke(
        main,
        ["db", "postgres", "export-current", "--sqlite-snapshot", str(missing_snapshot), *arguments],
    )

    assert result.exit_code == 1
    assert result.output == (
        '{"error":{"code":"invalid_export_mode","message":"export-current requires '
        "--sqlite-snapshot with either --preflight-only alone or both --transform-plan and "
        '--output"}}\n'
    )
    assert not (tmp_path / "must-not-exist.json").exists()


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["--preflight-only"],
        ["--transform-plan", "missing-plan.json", "--output", "must-not-exist.json"],
    ],
)
def test_export_cli_missing_snapshot_is_typed_before_config_or_path_io(tmp_path, monkeypatch, arguments):
    def forbidden_config(_ctx: object) -> None:
        raise AssertionError("configuration resolved before export mode validation")

    monkeypatch.setattr(cli_module, "_resolve_config", forbidden_config)
    result = CliRunner().invoke(main, ["db", "postgres", "export-current", *arguments])

    assert result.exit_code == 1
    assert result.output == (
        '{"error":{"code":"invalid_export_mode","message":"export-current requires '
        "--sqlite-snapshot with either --preflight-only alone or both --transform-plan and "
        '--output"}}\n'
    )
    assert not (tmp_path / "must-not-exist.json").exists()


def test_export_cli_preflight_emits_only_exact_canonical_source_json(tmp_path, monkeypatch):
    snapshot = tmp_path / "snapshot.db"
    snapshot.write_bytes(b"not-opened-by-cli-dispatch-test")
    expected = {
        "expected_pragma_user_version": 7,
        "expected_table_inventory_sha256": "a" * 64,
        "sqlite_snapshot_sha256": "b" * 64,
        "sqlite_snapshot_size_bytes": 31,
    }
    calls: list[tuple[Path, Path | None]] = []

    def preflight(
        _self: PostgresKernel,
        *,
        sqlite_snapshot: Path,
        live_sqlite_source: Path | None,
    ) -> dict[str, Any]:
        calls.append((sqlite_snapshot, live_sqlite_source))
        return expected

    monkeypatch.setattr(PostgresKernel, "preflight_export_current", preflight)
    monkeypatch.setattr(
        PostgresKernel,
        "export_current",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("normal export dispatched")),
    )

    result = CliRunner().invoke(
        main,
        ["db", "postgres", "export-current", "--sqlite-snapshot", str(snapshot), "--preflight-only"],
    )

    assert result.exit_code == 0
    assert result.output == canonical_json_bytes(expected).decode("utf-8")
    assert len(calls) == 1
    assert calls[0][0] == snapshot
    assert not list(tmp_path.glob("*.json"))


def test_export_cli_preflight_preserves_typed_inspection_error(tmp_path, monkeypatch):
    snapshot = tmp_path / "snapshot.db"
    snapshot.write_bytes(b"snapshot")

    def fail(_self: PostgresKernel, **_kwargs: object) -> dict[str, Any]:
        raise PostgresKernelError("snapshot_changed", "SQLite snapshot changed during immutable read")

    monkeypatch.setattr(PostgresKernel, "preflight_export_current", fail)
    result = CliRunner().invoke(
        main,
        ["db", "postgres", "export-current", "--sqlite-snapshot", str(snapshot), "--preflight-only"],
    )

    assert result.exit_code == 1
    assert result.output == (
        '{"error":{"code":"snapshot_changed","message":"SQLite snapshot changed during immutable read"}}\n'
    )


def test_postgres_cli_success_and_failure_are_one_compact_json_line(monkeypatch):
    monkeypatch.setattr(
        PostgresKernel,
        "initialize",
        lambda _self: {"schema_version": 1, "status": "initialized"},
    )
    success = CliRunner().invoke(main, ["db", "postgres", "init"])
    assert success.exit_code == 0
    assert success.output == '{"schema_version":1,"status":"initialized"}\n'

    def fail(_self: PostgresKernel) -> dict[str, Any]:
        raise PostgresKernelError("schema_drift", "PostgreSQL schema does not match")

    monkeypatch.setattr(PostgresKernel, "initialize", fail)
    failure = CliRunner().invoke(main, ["db", "postgres", "init"])
    assert failure.exit_code == 1
    assert json.loads(failure.output) == {
        "error": {"code": "schema_drift", "message": "PostgreSQL schema does not match"}
    }
    assert failure.output.count("\n") == 1


def test_postgres_cli_translates_directory_config_path_to_canonical_error(tmp_path):
    result = CliRunner().invoke(main, ["--config", str(tmp_path), "db", "postgres", "status"])
    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["error"]["code"] == "invalid_postgresql_config"
    assert result.output == canonical_json_bytes(payload).decode("utf-8")


@pytest.mark.parametrize(
    "content",
    [
        'groundtruth="not-a-table"\n',
        "gates=1\n[groundtruth]\n",
        "search=[]\n[groundtruth]\n",
        'backup="not-a-table"\n[groundtruth]\n',
        "[groundtruth]\n[gates]\nconfig=1\n",
    ],
)
def test_postgres_cli_translates_non_table_config_sections_to_canonical_error(tmp_path, content):
    config = tmp_path / "groundtruth.toml"
    config.write_text(content, encoding="utf-8")

    result = CliRunner().invoke(main, ["--config", str(config), "db", "postgres", "status"])

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["error"]["code"] == "invalid_postgresql_config"
    assert result.output == canonical_json_bytes(payload).decode("utf-8")


@pytest.mark.parametrize(
    "extra",
    [
        "",
        "\n[backup]\ninclude_chroma=false\n",
        "\n[gates]\nplugins=[]\n",
        "\n[search]\nchroma_path='chroma'\n",
    ],
)
def test_postgres_cli_postgresql_config_emits_one_json_line(tmp_path, monkeypatch, extra):
    config = tmp_path / "groundtruth.toml"
    config.write_text(f"[postgresql]\nservice='reviewed'\n{extra}", encoding="utf-8")
    monkeypatch.setattr(
        PostgresKernel,
        "status",
        lambda _self: {"schema_version": 1, "status": "initialized"},
    )

    result = CliRunner().invoke(main, ["--config", str(config), "db", "postgres", "status"])

    assert result.exit_code == 0
    assert result.output == '{"schema_version":1,"status":"initialized"}\n'
    assert result.stderr == ""


def test_postgres_cli_usage_error_remains_click_exit_two():
    result = CliRunner().invoke(main, ["db", "postgres", "import-current"])
    assert result.exit_code == 2


# --- WI-7690: stock public-schema initialization classification (database-free) ---------------
#
# These cases probe only the prior-initialization classification predicate in
# PostgresKernel.initialize. They never connect to PostgreSQL. Each case reports which branch the
# predicate selects -- exact-schema validation, or the uninitialized path -- by replacing the two
# branch entry points with typed sentinels. They also assert zero mutation on refusal, so a case
# that reaches exact-schema validation cannot have written schema SQL or a schema comment.

_STOCK_PUBLIC_COMMENT = "standard public schema"


class _RecordingCursor:
    def __init__(self) -> None:
        self.executed: list[str] = []

    def execute(self, query: Any, params: Any = None) -> None:
        self.executed.append(str(query))

    def fetchone(self) -> dict[str, Any]:
        return {}

    def fetchall(self) -> list[dict[str, Any]]:
        return []


class _RecordingConnection:
    def __init__(self, cursor: _RecordingCursor) -> None:
        self._cursor = cursor

    def __enter__(self) -> _RecordingConnection:
        return self

    def __exit__(self, *_exc: object) -> bool:
        return False

    @contextmanager
    def transaction(self):
        yield self

    def cursor(self) -> _RecordingCursor:
        return self._cursor


def _classify_initialize(monkeypatch, *, schema_name: str, tables: set[str], comment: object):
    """Return (branch, executed_queries) for one initialize classification case."""
    cursor = _RecordingCursor()

    def _branch(name: str):
        def _raise(*_args: object, **_kwargs: object):
            raise PostgresKernelError(name, f"branch sentinel: {name}")

        return _raise

    monkeypatch.setattr(PostgresKernel, "_current_schema", staticmethod(lambda _c: schema_name))
    monkeypatch.setattr(PostgresKernel, "_table_names", staticmethod(lambda _c, _s: set(tables)))
    monkeypatch.setattr(PostgresKernel, "_schema_comment", staticmethod(lambda _c, _s: comment))
    monkeypatch.setattr(
        PostgresKernel, "_require_exact_schema", classmethod(lambda _cls, *a, **k: _branch("branch_exact_schema")())
    )
    monkeypatch.setattr(PostgresKernel, "_schema_has_relations", staticmethod(_branch("branch_uninitialized")))

    kernel = PostgresKernel(PostgreSQLConfig(), connector=lambda **_kwargs: _RecordingConnection(cursor))
    with pytest.raises(PostgresKernelError) as excinfo:
        kernel.initialize()
    return excinfo.value.code, cursor.executed


def _assert_no_mutation(executed: list[str]) -> None:
    joined = " ".join(executed).upper()
    assert "COMMENT ON SCHEMA" not in joined
    assert "CREATE TABLE" not in joined


def test_absent_comment_reaches_the_uninitialized_path(monkeypatch):
    branch, executed = _classify_initialize(monkeypatch, schema_name="public", tables=set(), comment=None)
    assert branch == "branch_uninitialized"
    _assert_no_mutation(executed)


def test_exact_stock_public_comment_reaches_the_uninitialized_path(monkeypatch):
    """The WI-7690 repair: a table-free public schema carrying only PostgreSQL's stock comment
    is not kernel metadata drift; it is an uninitialized target."""
    branch, executed = _classify_initialize(
        monkeypatch, schema_name="public", tables=set(), comment=_STOCK_PUBLIC_COMMENT
    )
    assert branch == "branch_uninitialized"
    _assert_no_mutation(executed)


def test_arbitrary_comment_still_requires_exact_schema(monkeypatch):
    branch, executed = _classify_initialize(
        monkeypatch, schema_name="public", tables=set(), comment="something else entirely"
    )
    assert branch == "branch_exact_schema"
    _assert_no_mutation(executed)


def test_empty_comment_still_requires_exact_schema(monkeypatch):
    branch, executed = _classify_initialize(monkeypatch, schema_name="public", tables=set(), comment="")
    assert branch == "branch_exact_schema"
    _assert_no_mutation(executed)


def test_whitespace_padded_stock_comment_is_not_the_exception(monkeypatch):
    """No stripping: only the exact stock string qualifies."""
    branch, executed = _classify_initialize(
        monkeypatch, schema_name="public", tables=set(), comment=f" {_STOCK_PUBLIC_COMMENT} "
    )
    assert branch == "branch_exact_schema"
    _assert_no_mutation(executed)


def test_stock_comment_text_on_another_schema_is_not_the_exception(monkeypatch):
    """The same string on a differently named schema remains metadata drift."""
    branch, executed = _classify_initialize(
        monkeypatch, schema_name="gtkb", tables=set(), comment=_STOCK_PUBLIC_COMMENT
    )
    assert branch == "branch_exact_schema"
    _assert_no_mutation(executed)


def test_stock_comment_with_an_unrelated_table_still_requires_exact_schema(monkeypatch):
    """Tables short-circuit the exception: a table-bearing schema is never adopted."""
    branch, executed = _classify_initialize(
        monkeypatch, schema_name="public", tables={"unrelated"}, comment=_STOCK_PUBLIC_COMMENT
    )
    assert branch == "branch_exact_schema"
    _assert_no_mutation(executed)


def test_valid_kernel_metadata_comment_still_requires_exact_schema(monkeypatch):
    metadata = canonical_json_bytes(
        {
            "catalog_sha256": "0" * 64,
            "format": kernel_module.SCHEMA_FORMAT,
            "schema_sha256": "1" * 64,
            "schema_version": kernel_module.SCHEMA_VERSION,
        }
    ).decode("utf-8")
    branch, executed = _classify_initialize(monkeypatch, schema_name="public", tables=set(ALL_TABLES), comment=metadata)
    assert branch == "branch_exact_schema"
    _assert_no_mutation(executed)


# --- WI-7670: SQLite inventory reserved-word quoting ------------------------------------------
#
# ``notnull`` is a reserved word in the pragma_table_xinfo column list. Unquoted it is a syntax
# error, which is why export-current can report a snapshot as ok while its own --preflight-only
# then rejects that same snapshot. Both cases own their temporary SQLite fixtures and neither
# contacts a live MemBase, PostgreSQL, or Docker surface.


def test_export_preflight_reaches_table_set_check_after_inventory_query(tmp_path):
    """GOV-SOT-SINGLETON-001: the real inventory reader reaches table validation."""
    from sqlite3.dbapi2 import connect as fixture_connect

    snapshot = tmp_path / "inventory.db"
    connection = fixture_connect(snapshot)
    try:
        connection.execute("CREATE TABLE inventory_probe (required INTEGER NOT NULL, optional TEXT)")
        connection.commit()
    finally:
        connection.close()
    before = snapshot.read_bytes()

    def connect_snapshot(database_uri, *, uri):
        assert uri is True
        assert database_uri == snapshot.resolve().as_uri() + "?mode=ro&immutable=1"
        return fixture_connect(database_uri, uri=uri)

    kernel = PostgresKernel(PostgreSQLConfig(), sqlite_connector=connect_snapshot)
    with pytest.raises(PostgresKernelError) as error:
        kernel.preflight_export_current(sqlite_snapshot=snapshot, live_sqlite_source=None)
    assert error.value.code == "snapshot_table_set_mismatch"
    assert snapshot.read_bytes() == before
    assert not snapshot.with_name(snapshot.name + "-wal").exists()
    assert not snapshot.with_name(snapshot.name + "-shm").exists()


def test_sqlite_inventory_reads_not_null_column_values():
    """GOV-SOT-SINGLETON-001: the canonical reader preserves SQLite nullability."""
    import sqlite3
    from sqlite3.dbapi2 import connect as fixture_connect

    connection = fixture_connect(":memory:")
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("CREATE TABLE inventory_probe (required INTEGER NOT NULL, optional TEXT)")
        with pytest.raises(sqlite3.OperationalError, match="notnull"):
            connection.execute(
                "SELECT cid,name,type,notnull,dflt_value,pk,hidden FROM pragma_table_xinfo(?)",
                ("inventory_probe",),
            ).fetchall()
        rows = connection.execute(
            'SELECT cid,name,type,"notnull",dflt_value,pk,hidden FROM pragma_table_xinfo(?)',
            ("inventory_probe",),
        ).fetchall()
        assert {row["name"]: row["notnull"] for row in rows} == {"required": 1, "optional": 0}
        inventory = kernel_module._sqlite_inventory(connection)
        table = next(row for row in inventory["tables"] if row["name"] == "inventory_probe")
        assert {column["name"]: column["not_null"] for column in table["columns"]} == {
            "required": True,
            "optional": False,
        }
    finally:
        connection.close()


@pytest.mark.parametrize("status", ["removed", "retired", "moved", "superseded", "completed", "excluded", "rehomed"])
def test_membership_migration_keeps_only_actual_current_parent(status):
    source = {name: [] for name in MIGRATION_TABLES}
    current = dict(id="CURRENT", version=8, project_id="PROJECT-1", work_item_id="WI-1", status="active")
    historical = dict(current, id="OLD", status=status)
    source["project_work_item_memberships"] = [historical, current]
    plan = _plan()
    plan["projects"] = dict(expected_total=0, expected_authorized=0, expected_not_authorized=0, expected_programs=0)
    plan["project_dependencies"].update(
        preserve_dependency_ids=[],
        retire_dependency_ids=[],
        expected_source_count=0,
        expected_active_after=0,
        expected_retired_after=0,
        expected_gate_transition_count=0,
    )
    result = kernel_module._transform_source_rows(source, plan)
    assert [(r["id"], r["version"], r["project_id"], r["status"]) for r in result["project_work_item_memberships"]] == [
        ("CURRENT", 1, "PROJECT-1", "active")
    ]
    assert source["project_work_item_memberships"] == [historical, current]


@pytest.mark.parametrize("status", [None, "", "actve", "inactive", "RETIRED"])
def test_membership_migration_refuses_unrecognized_status_instead_of_dropping_it(status):
    source = {name: [] for name in MIGRATION_TABLES}
    source["project_work_item_memberships"] = [dict(id="AMBIGUOUS", status=status)]
    plan = _plan()
    plan["project_dependencies"].update(preserve_dependency_ids=[], retire_dependency_ids=[])
    with pytest.raises(PostgresKernelError) as failure:
        kernel_module._transform_source_rows(source, plan)
    assert failure.value.code == "invalid_source"
    assert failure.value.details == {"membership_id": "AMBIGUOUS", "status": status}


@pytest.mark.parametrize(
    "defect,code",
    [
        ("completed_alias", "invalid_dependency_contract"),
        ("promotion_gate", "invalid_dependency_contract"),
        ("cycle", "dependency_cycle"),
        ("duplicate", "duplicate_dependency"),
        ("program_endpoint", "invalid_dependency_endpoint"),
    ],
)
def test_migration_refuses_invalid_native_dependency_graph(defect, code):
    manifest = _work_model_manifest()
    metadata = dict(version=1, changed_by="test", changed_at="2026-09-01T00:00:00Z", change_reason="fixture")
    dependency = _row(
        "project_dependencies",
        id="DEP-ONE",
        dependent_project_id="PROJECT-ONE",
        prerequisite_project_id="PROJECT-TWO",
        dependency_kind="requires_project_state",
        required_prerequisite_state="verified",
        affected_gate="readiness",
        status="active",
        rationale="The successor needs the complete predecessor result",
        provenance="test",
        registry_version=1,
        blocking_status="open",
        **metadata,
    )
    manifest["tables"]["project_dependencies"] = [dependency]
    # A valid graph may be unready; import does not claim prerequisite completion.
    assert normalize_manifest(manifest)["tables"]["project_dependencies"][0]["id"] == "DEP-ONE"
    if defect == "completed_alias":
        dependency["required_prerequisite_state"] = "completed"
    elif defect == "promotion_gate":
        dependency["affected_gate"] = "promotion"
    elif defect in {"cycle", "duplicate"}:
        second = {**dependency, "id": "DEP-TWO"}
        if defect == "cycle":
            second.update(dependent_project_id="PROJECT-TWO", prerequisite_project_id="PROJECT-ONE")
        manifest["tables"]["project_dependencies"].append(second)
    else:
        manifest["tables"]["projects"][1].update(kind="program", authorization=None)
    with pytest.raises(PostgresKernelError) as error:
        normalize_manifest(manifest)
    assert error.value.code == code


@pytest.mark.parametrize(
    "dependencies,code",
    [
        ([{"work_item_id": "WI-TWO", "required_state": "terminal_published"}], "invalid_work_item_dependencies"),
        ([42], "invalid_work_item_dependencies"),
        ([" WI-TWO"], "invalid_work_item_dependencies"),
        ([""], "invalid_work_item_dependencies"),
        (["WI-MISSING"], "missing_work_item_dependency"),
        (["WI-TWO", "WI-TWO"], "duplicate_work_item_dependency"),
        (["WI-ONE"], "dependency_cycle"),
    ],
)
def test_migration_checks_work_item_dependency_elements_and_endpoints(dependencies, code):
    manifest = _work_model_manifest()
    first = manifest["tables"]["work_items"][0]
    manifest["tables"]["work_items"].append({**first, "id": "WI-TWO"})
    membership = manifest["tables"]["project_work_item_memberships"][0]
    manifest["tables"]["project_work_item_memberships"].append(
        {**membership, "id": "MEMBER-TWO", "work_item_id": "WI-TWO", "project_id": "PROJECT-TWO"}
    )
    first["depends_on_work_items"] = ["WI-TWO"]
    assert normalize_manifest(manifest)["tables"]["work_items"][0]["depends_on_work_items"] == ["WI-TWO"]
    first["depends_on_work_items"] = dependencies
    before = canonical_json_bytes(manifest)
    with pytest.raises(PostgresKernelError) as refused:
        normalize_manifest(manifest)
    assert refused.value.code == code
    assert "WI-ONE" in str(refused.value.details)
    assert canonical_json_bytes(manifest) == before


@pytest.mark.parametrize("status", ["open", "verified"])
def test_migration_refuses_closed_or_open_work_item_cycles(status):
    manifest = _work_model_manifest()
    first = manifest["tables"]["work_items"][0]
    first.update(depends_on_work_items=["WI-TWO"], resolution_status=status)
    manifest["tables"]["work_items"].append({**first, "id": "WI-TWO", "depends_on_work_items": ["WI-ONE"]})
    membership = manifest["tables"]["project_work_item_memberships"][0]
    manifest["tables"]["project_work_item_memberships"].append(
        {**membership, "id": "MEMBER-TWO", "work_item_id": "WI-TWO"}
    )
    with pytest.raises(PostgresKernelError) as refused:
        normalize_manifest(manifest)
    assert refused.value.code == "dependency_cycle"
    assert set(refused.value.details["work_item_ids"]) == {"WI-ONE", "WI-TWO"}


def test_work_item_dependency_graph_handles_deep_shared_predecessors():
    # Longer than Python's recursion limit, with shared predecessors and no cycle.
    rows = [{"id": "WI-0", "depends_on_work_items": None}]
    for index in range(1, 3000):
        rows.append({"id": f"WI-{index}", "depends_on_work_items": list({"WI-0", f"WI-{index - 1}"})})
    kernel_module.validate_work_item_dependencies(rows)
    rows[0]["depends_on_work_items"] = ["WI-2999"]
    with pytest.raises(PostgresKernelError) as refused:
        kernel_module.validate_work_item_dependencies(rows)
    assert refused.value.code == "dependency_cycle"
