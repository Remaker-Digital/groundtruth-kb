"""Spec-derived tests for WI-5044 restore-action registry metadata."""

from __future__ import annotations

import sqlite3
import sys
import textwrap
import tomllib
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.project.sot_registry import (  # noqa: E402
    InvalidSoTRecord,
    load_projection,
    load_toml,
    sync_projection,
)

_REGISTRY = _REPO_ROOT / "config" / "registry" / "sot-artifacts.toml"
_VALID_ACTIONS = {
    "manual",
    "visibility_only",
    "git_restore",
    "membase_export_restore",
    "regenerate_from_source",
    "ensure_alive",
    "noop",
}


def _write_registry(tmp_path: Path, *, restore_action: str = "ensure_alive") -> Path:
    path = tmp_path / "registry.toml"
    path.write_text(
        textwrap.dedent(
            f"""
            [[artifacts]]
            id = "dispatcher-state"
            domain = "bridge_protocol"
            lifecycle = "active"
            storage_path = ".gtkb-state/bridge-poller/dispatch-state.json"
            coverage_mode = "exact"
            authority_spec_id = "GOV-FILE-BRIDGE-AUTHORITY-001"
            mutation_api = "gt bridge dispatch daemon"
            versioning_policy = "overwrite_single_writer"
            backup_policy = "gitignored_runtime"
            restore_action = "{restore_action}"
            health_check_function = "_check_bridge_dispatch_liveness"
            owner_role = "automated_only"
            """
        ),
        encoding="utf-8",
    )
    return path


def _init_legacy_projection_schema(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(
            """
            CREATE TABLE sot_artifacts (
                id TEXT NOT NULL,
                version INTEGER NOT NULL,
                domain TEXT NOT NULL,
                lifecycle TEXT NOT NULL,
                storage_path TEXT NOT NULL,
                authority_spec_id TEXT NOT NULL,
                mutation_api TEXT NOT NULL,
                versioning_policy TEXT NOT NULL,
                backup_policy TEXT NOT NULL,
                health_check_function TEXT,
                owner_role TEXT NOT NULL,
                depends_on TEXT,
                forbidden_substitutes TEXT,
                notes TEXT,
                changed_by TEXT NOT NULL,
                changed_at TEXT NOT NULL,
                change_reason TEXT NOT NULL,
                PRIMARY KEY (id, version)
            );
            CREATE VIEW current_sot_artifacts AS
            SELECT a.* FROM sot_artifacts a
            INNER JOIN (SELECT id, MAX(version) AS max_v FROM sot_artifacts GROUP BY id) m
            ON a.id = m.id AND a.version = m.max_v;
            """
        )
        conn.commit()
    finally:
        conn.close()


def test_shipped_registry_declares_restore_action_for_every_record() -> None:
    raw_records = tomllib.loads(_REGISTRY.read_text(encoding="utf-8"))["artifacts"]
    by_id = {record["id"]: record for record in raw_records}

    assert raw_records
    assert all("restore_action" in record for record in raw_records)
    assert {record["restore_action"] for record in raw_records} <= _VALID_ACTIONS
    assert {
        "manual",
        "visibility_only",
        "git_restore",
        "membase_export_restore",
        "regenerate_from_source",
        "ensure_alive",
        "noop",
    } <= {record["restore_action"] for record in raw_records}
    assert by_id["dispatcher-supervisor-task"]["restore_action"] == "ensure_alive"
    assert by_id["dispatcher-supervisor-task"]["health_check_function"] == "_check_dispatcher_daemon_supervisor_task"
    assert by_id["dispatcher-storm-watchdog-task"]["restore_action"] == "ensure_alive"
    assert by_id["dispatcher-storm-watchdog-task"]["health_check_function"] == "_check_dispatcher_daemon_watchdog_task"


def test_loader_rejects_invalid_restore_action(tmp_path: Path) -> None:
    path = _write_registry(tmp_path, restore_action="run-anything")

    with pytest.raises(InvalidSoTRecord, match="restore_action"):
        load_toml(path)


def test_projection_sync_preserves_restore_action_on_legacy_schema(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path, restore_action="ensure_alive")
    db_path = tmp_path / "projection.db"
    _init_legacy_projection_schema(db_path)

    records = load_toml(registry_path)
    report = sync_projection(records, db_path)
    projection = load_projection(db_path)

    assert report.inserted == ("dispatcher-state",)
    assert projection[0].restore_action == "ensure_alive"

    conn = sqlite3.connect(str(db_path))
    try:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(sot_artifacts)").fetchall()}
    finally:
        conn.close()
    assert "restore_action" in columns
