"""c123 (batch design WP5, G43): the retired flow engine's SQLite substrate is gone.

The knowledge database carried the retired flow engine's eight tables, six current-version views, 36 public methods and
11 private helpers, none of them called. They are deleted; a database file created earlier keeps its tables inert,
because nothing drops them. The environment migration no longer counts the retired engine's key prefix as a platform
key, so a leftover key is ambiguous and blocks apply, and the diagnostic names it without its value.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import groundtruth_kb.db as db_module
import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.env_sot import EnvSotError, build_plan, migrate, render_plan

RETIRED_TABLES = (
    "flow_definitions",
    "flow_instances",
    "stage_instances",
    "flow_events",
    "flow_artifacts",
    "stage_leases",
    "stage_attempt_telemetry",
    "agent_capability_snapshots",
)
RETIRED_VIEWS = (
    "current_flow_definitions",
    "current_flow_instances",
    "current_stage_instances",
    "current_stage_leases",
    "current_stage_attempt_telemetry",
    "current_agent_capability_snapshots",
)
RETIRED_PUBLIC_METHODS = (
    "insert_flow_definition",
    "get_flow_definition",
    "list_flow_definitions",
    "get_flow_definition_history",
    "insert_flow_instance",
    "insert_bridge_thread_atomic",
    "get_flow_instance",
    "get_flow_instance_history",
    "list_flow_instances",
    "insert_stage_instance",
    "get_stage_instance",
    "get_stage_instance_history",
    "list_stage_instances",
    "insert_stage_lease",
    "get_stage_lease",
    "get_stage_lease_history",
    "list_stage_leases",
    "insert_stage_attempt_telemetry",
    "get_stage_attempt_telemetry",
    "get_stage_attempt_telemetry_history",
    "list_stage_attempt_telemetry",
    "list_expired_stage_leases",
    "claim_stage_lease",
    "release_stage_lease",
    "recover_expired_stage_leases",
    "heartbeat_stage_lease",
    "insert_agent_capability_snapshot",
    "get_agent_capability_snapshot",
    "get_agent_capability_snapshot_history",
    "list_agent_capability_snapshots",
    "insert_flow_event",
    "get_flow_event",
    "list_flow_events",
    "insert_flow_artifact",
    "get_flow_artifact",
    "list_flow_artifacts",
)
RETIRED_PRIVATE_HELPERS = (
    "_next_flow_definition_version",
    "_next_flow_instance_version",
    "_insert_flow_instance_row",
    "_next_stage_instance_version",
    "_next_stage_lease_version",
    "_next_stage_attempt_telemetry_version",
    "_expired_active_stage_lease_rows",
    "_active_stage_lease_row",
    "_append_stage_claim_state",
    "_next_agent_capability_snapshot_version",
    "_insert_flow_artifact_row",
)


def _schema_names(path: Path) -> set[str]:
    with sqlite3.connect(path) as conn:
        return {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")}


def test_the_retired_names_are_counted_as_the_design_states() -> None:
    assert (len(RETIRED_TABLES), len(RETIRED_VIEWS)) == (8, 6)
    assert (len(set(RETIRED_PUBLIC_METHODS)), len(set(RETIRED_PRIVATE_HELPERS))) == (36, 11)


def test_a_fresh_database_has_no_retired_flow_tables_or_views(tmp_path: Path) -> None:
    path = tmp_path / "fresh.db"
    KnowledgeDB(db_path=path).close()

    names = _schema_names(path)

    assert {"projects", "current_projects", "work_items"} <= names, "control: the current schema was created"
    assert sorted(names & {*RETIRED_TABLES, *RETIRED_VIEWS}) == []


def test_the_knowledge_db_has_no_retired_flow_methods() -> None:
    assert callable(getattr(KnowledgeDB, "insert_project", None)), "control: a current writer exists"
    present = [name for name in (*RETIRED_PUBLIC_METHODS, *RETIRED_PRIVATE_HELPERS) if hasattr(KnowledgeDB, name)]
    assert present == []
    assert not hasattr(db_module, "_parse_iso_utc") and not hasattr(db_module, "_iso_plus_seconds")


def test_an_earlier_database_keeps_its_retired_tables_inert(tmp_path: Path) -> None:
    path = tmp_path / "earlier.db"
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE flow_definitions (rowid INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL, version INTEGER)"
        )
        conn.execute("INSERT INTO flow_definitions (id, version) VALUES ('FLOW-EARLIER', 1)")

    KnowledgeDB(db_path=path).close()

    names = _schema_names(path)
    assert "projects" in names, "control: opening the file applied the current schema"
    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT id, version FROM flow_definitions").fetchall() == [("FLOW-EARLIER", 1)]
        columns = [row[1] for row in conn.execute("PRAGMA table_info(flow_definitions)").fetchall()]
    assert columns == ["rowid", "id", "version"], "nothing migrates the retired table any more"


def test_a_leftover_retired_engine_key_is_ambiguous_and_blocks_apply(tmp_path: Path) -> None:
    secret = "a-value-that-must-not-be-rendered"
    (tmp_path / ".env.local").write_text(f"GTKB_MODE=platform\nTAFE_EXAMPLE={secret}\n", encoding="utf-8")

    plan = build_plan(tmp_path)

    assert plan.platform_key_count == 1, "control: GTKB_ keys stay platform keys"
    assert plan.ambiguous_root_keys == ("TAFE_EXAMPLE",)
    assert not plan.ok_for_apply
    assert any("TAFE_EXAMPLE" in line for line in plan.diagnostics)
    assert secret not in render_plan(plan)
    with pytest.raises(EnvSotError):
        migrate(tmp_path, apply=True)
    assert (tmp_path / ".env.local").read_text(encoding="utf-8") == f"GTKB_MODE=platform\nTAFE_EXAMPLE={secret}\n"
