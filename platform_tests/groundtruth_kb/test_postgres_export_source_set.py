"""Export accounts for required current state and optional retired storage (WI-7694)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from groundtruth_kb.postgres_kernel import MIGRATION_TABLES, SOURCE_TABLES, PostgresKernelError, _current_sqlite_rows

from platform_tests.groundtruth_kb.postgres_fixtures import preflight, snapshot


def test_current_sqlite_rows_preserves_unversioned_links_and_rejects_version_tie():
    with sqlite3.connect(":memory:") as connection:
        connection.row_factory = sqlite3.Row
        connection.execute(
            "CREATE TABLE specification_deliberation_sources "
            "(spec_id TEXT,deliberation_id TEXT,spec_version INTEGER,source_role TEXT,added_at TEXT,added_by TEXT)"
        )
        rows = [
            ("SPEC-1", "DELIB-1", version, role, "2026-09-01T00:00:00+00:00", "actor")
            for version, role in ((1, "historical"), (2, "current"))
        ]
        connection.executemany("INSERT INTO specification_deliberation_sources VALUES (?,?,?,?,?,?)", rows)
        assert [
            tuple(row.values()) for row in _current_sqlite_rows(connection, "specification_deliberation_sources")
        ] == rows
        connection.execute("CREATE TABLE projects (id TEXT,version INTEGER)")
        connection.executemany(
            "INSERT INTO projects VALUES (?,?)", [("PROJECT-1", 3), ("PROJECT-1", 2), ("PROJECT-1", 2)]
        )
        # Even a historical tie is inconsistent source lineage.
        with pytest.raises(PostgresKernelError, match="Duplicate source identity/version"):
            _current_sqlite_rows(connection, "projects")


def test_current_sqlite_rows_does_not_materialize_historical_payloads():
    with sqlite3.connect(":memory:") as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("CREATE TABLE projects (id TEXT,version INTEGER,payload TEXT)")
        connection.executemany(
            "INSERT INTO projects VALUES (?,?,?)",
            [("P1", 1, "historical-body" * 1000), ("P1", 2, "current-one"), ("P2", 7, "current-two")],
        )

        def decode_current(value: bytes) -> str:
            assert not value.startswith(b"historical-body"), "Exporter materialized an obsolete payload"
            return value.decode("utf-8")

        connection.text_factory = decode_current
        assert {row["id"]: row["payload"] for row in _current_sqlite_rows(connection, "projects")} == {
            "P1": "current-one",
            "P2": "current-two",
        }


@pytest.mark.parametrize("version", [None, 0, -1, 1.5, "not-a-version"])
def test_current_sqlite_rows_rejects_invalid_source_version(version):
    with sqlite3.connect(":memory:") as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("CREATE TABLE projects (id TEXT,version)")
        connection.execute("INSERT INTO projects VALUES (?,?)", ("P1", version))
        with pytest.raises(PostgresKernelError, match="Invalid source version"):
            _current_sqlite_rows(connection, "projects")


@pytest.mark.parametrize("mode", ["all-known", "current-only", "authorization-table-removed"])
def test_export_accepts_accounted_source_with_or_without_retired_storage(tmp_path: Path, mode: str):
    tables = set(MIGRATION_TABLES) if mode == "current-only" else set(SOURCE_TABLES)
    if mode == "authorization-table-removed":
        tables.remove("project_authorizations")
    path = snapshot(tmp_path / "source.db", tables)
    before = path.read_bytes()
    result = preflight(path)
    assert result["sqlite_snapshot_size_bytes"] == len(before)
    assert len(result["expected_table_inventory_sha256"]) == 64
    assert path.read_bytes() == before


@pytest.mark.parametrize("missing", ["specifications", "session_init_bindings"])
def test_export_refuses_missing_migratable_state(tmp_path: Path, missing: str):
    path = snapshot(tmp_path / "source.db", set(SOURCE_TABLES) - {missing})
    with pytest.raises(PostgresKernelError) as refused:
        preflight(path)
    assert refused.value.code == "snapshot_table_set_mismatch"
    assert refused.value.details == {"missing": [missing], "unclassified": []}


def test_export_refuses_unknown_storage_instead_of_silently_omitting_it(tmp_path: Path):
    path = snapshot(tmp_path / "source.db", set(SOURCE_TABLES) | {"undeclared_work_state"})
    with pytest.raises(PostgresKernelError) as refused:
        preflight(path)
    assert refused.value.code == "snapshot_table_set_mismatch"
    assert refused.value.details == {"missing": [], "unclassified": ["undeclared_work_state"]}
