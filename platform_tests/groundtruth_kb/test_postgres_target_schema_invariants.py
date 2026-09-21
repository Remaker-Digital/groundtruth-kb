"""Current migration classification and selected-package target closure (TEST-12537)."""

from __future__ import annotations

import re
from importlib.resources import files

import pytest
from groundtruth_kb.postgres_kernel import (
    ALL_TABLES,
    COORDINATION_TABLES,
    CURRENT_TABLES,
    MIGRATION_TABLES,
    REBUILT_LATER_TABLES,
    RETIRED_TABLES,
    SOURCE_TABLES,
    PostgresKernelError,
)

from platform_tests.groundtruth_kb.postgres_fixtures import preflight, snapshot


def test_migration_classes_are_disjoint_and_preserve_domain_records_and_bindings():
    classes = [set(MIGRATION_TABLES), set(REBUILT_LATER_TABLES), set(RETIRED_TABLES)]
    assert not (classes[0] & classes[1] or classes[0] & classes[2] or classes[1] & classes[2])
    assert set.union(*classes) == set(SOURCE_TABLES)
    assert set(MIGRATION_TABLES) == set(CURRENT_TABLES) | {"session_init_bindings"}
    assert {
        "projects",
        "work_items",
        "specifications",
        "tests",
        "project_work_item_memberships",
        "project_dependencies",
    } <= set(CURRENT_TABLES)
    assert "project_authorizations" in RETIRED_TABLES
    assert {"bridge_attempts", "bridge_items"}.isdisjoint(SOURCE_TABLES)
    assert "work_intent_claims" in REBUILT_LATER_TABLES


def test_selected_package_ddl_matches_current_history_and_coordination_contract():
    text = files("groundtruth_kb").joinpath("postgresql_v1.sql").read_text(encoding="utf-8")
    declared = re.findall(r"CREATE TABLE \{schema\}\.([a-z_]+)\s*\(", text)
    assert declared and len(declared) == len(set(declared))
    assert set(declared) == set(ALL_TABLES) == set(CURRENT_TABLES) | {"record_history"} | set(COORDINATION_TABLES)
    assert not set(RETIRED_TABLES) & set(declared)


@pytest.mark.parametrize("change", ["current-only", "missing-binding", "unknown-record"])
def test_export_classifies_the_supplied_snapshot_without_a_worktree_database(tmp_path, change):
    tables = set(MIGRATION_TABLES)
    if change == "missing-binding":
        tables.remove("session_init_bindings")
    elif change == "unknown-record":
        tables.add("unclassified_current_record")
    source = snapshot(tmp_path / "source.db", tables)
    before = source.read_bytes()
    if change == "current-only":
        result = preflight(source)
        assert result["sqlite_snapshot_size_bytes"] == len(before)
    else:
        with pytest.raises(PostgresKernelError) as error:
            preflight(source)
        assert error.value.code == "snapshot_table_set_mismatch"
        assert error.value.details == {
            "missing": ["session_init_bindings"] if change == "missing-binding" else [],
            "unclassified": ["unclassified_current_record"] if change == "unknown-record" else [],
        }
    assert source.read_bytes() == before
