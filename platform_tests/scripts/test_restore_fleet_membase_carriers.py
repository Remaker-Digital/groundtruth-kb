# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/restore_fleet_membase_carriers.py (WI-5139)."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path
from types import ModuleType

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "restore_fleet_membase_carriers.py"


def _load_module() -> ModuleType:
    module_name = "restore_fleet_membase_carriers"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def restore_module() -> ModuleType:
    return _load_module()


def _create_schema(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        create table work_items (
            rowid integer primary key,
            id text not null,
            version integer not null,
            title text not null,
            source_test_id text,
            resolution_status text not null,
            stage text not null,
            project_name text,
            unique(id, version)
        );
        create table tests (
            rowid integer primary key,
            id text not null,
            version integer not null,
            title text not null,
            spec_id text not null,
            test_file text,
            test_function text,
            unique(id, version)
        );
        create table project_work_item_memberships (
            rowid integer primary key,
            id text not null,
            version integer not null,
            project_id text not null,
            work_item_id text not null,
            status text not null,
            unique(id, version)
        );
        create table project_authorizations (
            rowid integer primary key,
            id text not null,
            version integer not null,
            project_id text not null,
            status text not null,
            included_work_item_ids text,
            unique(id, version)
        );
        """
    )
    conn.close()


def _insert_work_item(conn: sqlite3.Connection, *, rowid: int, wi_id: str, title: str) -> None:
    conn.execute(
        """
        insert into work_items (
            rowid, id, version, title, source_test_id, resolution_status, stage, project_name
        )
        values (?, ?, 1, ?, null, 'open', 'backlogged', 'PROJECT-GTKB-GOOSE-HARNESS-ADOPTION')
        """,
        (rowid, wi_id, title),
    )


def _insert_test(conn: sqlite3.Connection, *, rowid: int, test_id: str, title: str) -> None:
    conn.execute(
        """
        insert into tests (rowid, id, version, title, spec_id, test_file, test_function)
        values (?, ?, 1, ?, 'SPEC-CENTRALIZED-DISPATCH-SERVICE-001', null, null)
        """,
        (rowid, test_id, title),
    )


def _insert_membership(conn: sqlite3.Connection, *, rowid: int, membership_id: str, wi_id: str) -> None:
    conn.execute(
        """
        insert into project_work_item_memberships (
            rowid, id, version, project_id, work_item_id, status
        )
        values (?, ?, 1, 'PROJECT-GTKB-GOOSE-HARNESS-ADOPTION', ?, 'active')
        """,
        (rowid, membership_id, wi_id),
    )


def _insert_pauth(
    conn: sqlite3.Connection,
    *,
    rowid: int,
    pauth_id: str,
    included_work_item_ids: str,
) -> None:
    conn.execute(
        """
        insert into project_authorizations (
            rowid, id, version, project_id, status, included_work_item_ids
        )
        values (?, ?, 1, 'PROJECT-GTKB-GOOSE-HARNESS-ADOPTION', 'active', ?)
        """,
        (rowid, pauth_id, included_work_item_ids),
    )


def _select_values(path: Path, table: str, column: str) -> list[str]:
    conn = sqlite3.connect(path)
    values = [row[0] for row in conn.execute(f"select {column} from {table} order by {column}")]
    conn.close()
    return values


def _count(path: Path, table: str) -> int:
    conn = sqlite3.connect(path)
    value = conn.execute(f"select count(*) from {table}").fetchone()[0]
    conn.close()
    return value


def test_restore_inserts_only_allowlisted_missing_rows(tmp_path: Path, restore_module: ModuleType):
    live_db = tmp_path / "live.db"
    snapshot_db = tmp_path / "snapshot.db"
    _create_schema(live_db)
    _create_schema(snapshot_db)

    conn = sqlite3.connect(snapshot_db)
    _insert_work_item(conn, rowid=77, wi_id="WI-5211", title="allowed work")
    _insert_work_item(conn, rowid=78, wi_id="WI-5217", title="out of scope work")
    _insert_test(conn, rowid=79, test_id="TEST-11370", title="allowed test")
    _insert_test(conn, rowid=80, test_id="TEST-11305", title="out of scope test")
    _insert_membership(conn, rowid=81, membership_id="PWM-ALLOWED", wi_id="WI-5211")
    _insert_membership(conn, rowid=82, membership_id="PWM-BLOCKED", wi_id="WI-5217")
    _insert_pauth(
        conn,
        rowid=83,
        pauth_id=restore_module.PAUTH_IDS[0],
        included_work_item_ids='["WI-5211"]',
    )
    _insert_pauth(
        conn,
        rowid=84,
        pauth_id="PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712",
        included_work_item_ids='["WI-5217"]',
    )
    conn.commit()
    conn.close()

    summary = restore_module.restore_carriers(live_db=live_db, snapshot_db=snapshot_db)

    assert summary["total_inserted"] == 4
    assert _select_values(live_db, "work_items", "id") == ["WI-5211"]
    assert _select_values(live_db, "tests", "id") == ["TEST-11370"]
    assert _select_values(live_db, "project_work_item_memberships", "work_item_id") == ["WI-5211"]
    assert _select_values(live_db, "project_authorizations", "included_work_item_ids") == ['["WI-5211"]']
    conn = sqlite3.connect(live_db)
    restored_rowid = conn.execute("select rowid from work_items where id = 'WI-5211'").fetchone()[0]
    conn.close()
    assert restored_rowid != 77


def test_restore_skips_existing_rows_without_overwrite(tmp_path: Path, restore_module: ModuleType):
    live_db = tmp_path / "live.db"
    snapshot_db = tmp_path / "snapshot.db"
    _create_schema(live_db)
    _create_schema(snapshot_db)

    live = sqlite3.connect(live_db)
    _insert_work_item(live, rowid=1, wi_id="WI-5211", title="keep live title")
    live.commit()
    live.close()

    snapshot = sqlite3.connect(snapshot_db)
    _insert_work_item(snapshot, rowid=77, wi_id="WI-5211", title="snapshot title")
    snapshot.commit()
    snapshot.close()

    summary = restore_module.restore_carriers(live_db=live_db, snapshot_db=snapshot_db)

    assert summary["tables"]["work_items"]["inserted"] == 0
    assert summary["tables"]["work_items"]["skipped_existing"] == 1
    conn = sqlite3.connect(live_db)
    title = conn.execute("select title from work_items where id = 'WI-5211'").fetchone()[0]
    conn.close()
    assert title == "keep live title"


def test_restore_is_idempotent_after_first_run(tmp_path: Path, restore_module: ModuleType):
    live_db = tmp_path / "live.db"
    snapshot_db = tmp_path / "snapshot.db"
    _create_schema(live_db)
    _create_schema(snapshot_db)

    snapshot = sqlite3.connect(snapshot_db)
    _insert_test(snapshot, rowid=79, test_id="TEST-11370", title="allowed test")
    snapshot.commit()
    snapshot.close()

    first = restore_module.restore_carriers(live_db=live_db, snapshot_db=snapshot_db)
    second = restore_module.restore_carriers(live_db=live_db, snapshot_db=snapshot_db)

    assert first["total_inserted"] == 1
    assert second["total_inserted"] == 0
    assert second["total_skipped_existing"] == 1
    assert _count(live_db, "tests") == 1


def test_dry_run_does_not_mutate_live_db(tmp_path: Path, restore_module: ModuleType):
    live_db = tmp_path / "live.db"
    snapshot_db = tmp_path / "snapshot.db"
    _create_schema(live_db)
    _create_schema(snapshot_db)

    snapshot = sqlite3.connect(snapshot_db)
    _insert_work_item(snapshot, rowid=77, wi_id="WI-5211", title="allowed work")
    snapshot.commit()
    snapshot.close()

    summary = restore_module.restore_carriers(
        live_db=live_db,
        snapshot_db=snapshot_db,
        dry_run=True,
    )

    assert summary["total_inserted"] == 1
    assert _count(live_db, "work_items") == 0


def test_pauth_scope_guard_rejects_out_of_scope_included_work_item(
    tmp_path: Path,
    restore_module: ModuleType,
):
    live_db = tmp_path / "live.db"
    snapshot_db = tmp_path / "snapshot.db"
    _create_schema(live_db)
    _create_schema(snapshot_db)

    snapshot = sqlite3.connect(snapshot_db)
    _insert_pauth(
        snapshot,
        rowid=83,
        pauth_id=restore_module.PAUTH_IDS[0],
        included_work_item_ids='["WI-5217"]',
    )
    snapshot.commit()
    snapshot.close()

    with pytest.raises(ValueError, match="out-of-scope work items"):
        restore_module.restore_carriers(live_db=live_db, snapshot_db=snapshot_db)
