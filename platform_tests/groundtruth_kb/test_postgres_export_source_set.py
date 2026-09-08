"""Export accounts for required current state and optional retired storage (WI-7694)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from groundtruth_kb.config import PostgreSQLConfig
from groundtruth_kb.postgres_kernel import MIGRATION_TABLES, SOURCE_TABLES, PostgresKernel, PostgresKernelError


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
