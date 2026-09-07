"""Typed operational-event service (WI-6992).

Each test maps to a clause in the proposal's spec-derived verification plan at
``bridge/gtkb-wi6992-five-operation-event-service-003.md``.

Authority: ``GOV-GTKB-EMERGENCY-BOOTSTRAP-001`` v4 (the five-operation contract,
the no-raw-storage clause, and the section 9 evidence list); WI-6992 v7 (the
corrected record); ``GOV-SOT-SINGLETON-001``.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from groundtruth_kb import operational_events as oe
from groundtruth_kb.db import KnowledgeDB

BODY = {element: f"<{element}>" for element in oe.BODY_ELEMENTS}

COMMON = {
    "event_type": "emergency_bootstrap",
    "work_item_id": "WI-0001",
    "work_item_version": 1,
    "project_id": "PROJECT-TEST",
    "project_version": 1,
    "project_authorization_value": "authorized",
    "recorder_session_context_id": "session-under-test",
}


@pytest.fixture
def conn(tmp_path: Path) -> sqlite3.Connection:
    """A real database built from SCHEMA_SQL, so the table under test is the declared one."""
    db = KnowledgeDB(db_path=tmp_path / "probe.db")
    connection = db._get_conn()
    connection.row_factory = sqlite3.Row
    return connection


# --- the five-operation contract -------------------------------------------------


def test_exactly_the_five_specified_operations_are_public() -> None:
    """GOV-GTKB-EMERGENCY-BOOTSTRAP-001 v4: only create, inspect, append, show, verify."""
    operations = {n for n in oe.__all__ if callable(getattr(oe, n, None)) and not n[0].isupper()}
    assert operations == {"create", "inspect", "append", "show", "verify"}


def test_no_raw_storage_accessor_is_exported() -> None:
    """ "Agents never access raw storage." No export hands back a connection or cursor."""
    leaks = [n for n in oe.__all__ if "conn" in n.lower() or "cursor" in n.lower() or "raw" in n.lower()]
    assert leaks == []


def test_every_section_9_evidence_element_has_a_declared_home() -> None:
    """The twelve evidence elements are either columns or declared body keys."""
    columns = {
        "work_item_id",
        "work_item_version",
        "project_id",
        "project_version",
        "project_authorization_value",
        "recorder_session_context_id",
    }
    assert len(oe.BODY_ELEMENTS) == 12
    assert not columns & set(oe.BODY_ELEMENTS), "an element is declared in two places"


# --- the corrected record --------------------------------------------------------


def test_record_has_fourteen_named_columns_and_no_membership_columns(conn: sqlite3.Connection) -> None:
    """WI-6992 v7: 3 authorization-object columns collapse to 1 value; 2 membership columns dropped."""
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({oe.TABLE})")]
    named = [c for c in cols if c != "rowid"]
    assert len(named) == 14, named
    assert "project_authorization_value" in named
    for retired in ("project_authorization_id", "project_authorization_version", "project_authorization_state"):
        assert retired not in named, f"{retired} is a retired authorization-object column"
    for retired in ("execution_membership_id", "execution_membership_version"):
        assert retired not in named, f"{retired} belongs to the retired membership model"


@pytest.mark.parametrize("value", ["authorized", "not authorized"])
def test_authorization_value_accepts_the_two_canonical_values(conn: sqlite3.Connection, value: str) -> None:
    event = oe.create(
        conn, event_id=f"OE-{value.replace(' ', '-')}", body=BODY, **{**COMMON, "project_authorization_value": value}
    )
    assert event.project_authorization_value == value


@pytest.mark.parametrize(
    "legacy",
    ["present", "missing_due_to_foundational_deadlock", "sad_absent_foundational_bootstrap_exception"],
)
def test_legacy_authorization_object_states_are_refused(conn: sqlite3.Connection, legacy: str) -> None:
    """The legacy column's values describe an object's presence, not an authorization value."""
    with pytest.raises(oe.OperationalEventError) as excinfo:
        oe.create(conn, event_id="OE-legacy", body=BODY, **{**COMMON, "project_authorization_value": legacy})
    assert excinfo.value.code == "invalid_authorization_value"


# --- append-only discipline ------------------------------------------------------


def test_append_advances_the_version_and_preserves_history(conn: sqlite3.Connection) -> None:
    oe.create(conn, event_id="OE-1", body=BODY, **COMMON)
    oe.append(
        conn,
        event_id="OE-1",
        expected_current_version=1,
        lifecycle_state="independently_verified",
        body={**BODY, "after_action_findings": "changed"},
        recorder_session_context_id="session-under-test",
    )
    history = oe.show(conn, event_id="OE-1")
    assert [e.version for e in history] == [1, 2]
    assert history[0].lifecycle_state == "open"
    assert history[1].lifecycle_state == "independently_verified"


def test_stale_expected_version_is_refused_and_writes_nothing(conn: sqlite3.Connection) -> None:
    """CAS: a stale token must not append."""
    oe.create(conn, event_id="OE-cas", body=BODY, **COMMON)
    before = conn.execute(f'SELECT COUNT(*) FROM "{oe.TABLE}"').fetchone()[0]
    with pytest.raises(oe.OperationalEventError) as excinfo:
        oe.append(
            conn,
            event_id="OE-cas",
            expected_current_version=99,
            lifecycle_state="closed",
            body=BODY,
            recorder_session_context_id="session-under-test",
        )
    assert excinfo.value.code == "version_conflict"
    assert conn.execute(f'SELECT COUNT(*) FROM "{oe.TABLE}"').fetchone()[0] == before


def test_lifecycle_cannot_move_backward(conn: sqlite3.Connection) -> None:
    oe.create(conn, event_id="OE-back", body=BODY, **COMMON)
    oe.append(
        conn,
        event_id="OE-back",
        expected_current_version=1,
        lifecycle_state="closed",
        body=BODY,
        recorder_session_context_id="session-under-test",
    )
    with pytest.raises(oe.OperationalEventError) as excinfo:
        oe.append(
            conn,
            event_id="OE-back",
            expected_current_version=2,
            lifecycle_state="open",
            body=BODY,
            recorder_session_context_id="session-under-test",
        )
    assert excinfo.value.code == "illegal_transition"


# --- verify is integrity checking ------------------------------------------------


def test_verify_reports_ok_for_a_sound_event(conn: sqlite3.Connection) -> None:
    oe.create(conn, event_id="OE-ok", body=BODY, **COMMON)
    report = oe.verify(conn, event_id="OE-ok")
    assert report["ok"] is True
    assert report["problems"] == []
    assert report["versions"] == 1


def test_verify_detects_a_digest_mismatch(conn: sqlite3.Connection) -> None:
    """The settled reading of verify: body_sha256 must agree with body_json."""
    oe.create(conn, event_id="OE-tamper", body=BODY, **COMMON)
    conn.execute(
        f'UPDATE "{oe.TABLE}" SET body_json = ? WHERE id = ? AND version = 1',
        (json.dumps({"tampered": True}), "OE-tamper"),
    )
    conn.commit()
    report = oe.verify(conn, event_id="OE-tamper")
    assert report["ok"] is False
    assert any("body_sha256 mismatch" in p for p in report["problems"])


def test_absent_event_is_refused_by_every_read(conn: sqlite3.Connection) -> None:
    for operation in (oe.inspect, oe.show, oe.verify):
        with pytest.raises(oe.OperationalEventError) as excinfo:
            operation(conn, event_id="OE-absent")
        assert excinfo.value.code == "event_absent"


# --- the legacy table is pre-definition history ----------------------------------


LEGACY_DDL = """
CREATE TABLE operational_events (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL, version INTEGER NOT NULL, schema_version INTEGER NOT NULL,
    event_type TEXT NOT NULL, lifecycle_state TEXT NOT NULL,
    work_item_id TEXT NOT NULL, work_item_version INTEGER NOT NULL,
    execution_membership_id TEXT NOT NULL, execution_membership_version INTEGER NOT NULL,
    project_id TEXT NOT NULL, project_version INTEGER NOT NULL,
    project_authorization_state TEXT NOT NULL,
    body_json TEXT NOT NULL, body_sha256 TEXT NOT NULL,
    recorder_session_context_id TEXT NOT NULL, recorded_at TEXT NOT NULL
);
"""


def _install_legacy_table(connection: sqlite3.Connection) -> None:
    """Create the legacy shape locally.

    ``operational_events`` has no CREATE TABLE anywhere in tracked source -- it
    was created by an untracked writer, which is the condition WI-6992 exists to
    correct. A database built from SCHEMA_SQL therefore does not have it, so
    these isolation tests install the legacy shape themselves rather than
    depending on canonical state.
    """
    connection.executescript(LEGACY_DDL)
    connection.commit()


def test_the_service_never_touches_the_legacy_table(conn: sqlite3.Connection) -> None:
    """Scope item 6: legacy rows are retained, not migrated or reinterpreted."""
    _install_legacy_table(conn)
    before = conn.execute("SELECT COUNT(*) FROM operational_events").fetchone()[0]
    oe.create(conn, event_id="OE-isolation", body=BODY, **COMMON)
    oe.append(
        conn,
        event_id="OE-isolation",
        expected_current_version=1,
        lifecycle_state="closed",
        body=BODY,
        recorder_session_context_id="session-under-test",
    )
    assert conn.execute("SELECT COUNT(*) FROM operational_events").fetchone()[0] == before
    assert oe.TABLE != "operational_events"


def test_no_operation_returns_a_legacy_row(conn: sqlite3.Connection) -> None:
    """A row lacking a declared authorization value is not surfaced through this contract."""
    _install_legacy_table(conn)
    conn.execute(
        "INSERT INTO operational_events (id, version, schema_version, event_type, lifecycle_state,"
        " work_item_id, work_item_version, execution_membership_id, execution_membership_version,"
        " project_id, project_version, project_authorization_state, body_json, body_sha256,"
        " recorder_session_context_id, recorded_at)"
        " VALUES ('LEGACY-1',1,1,'emergency_bootstrap','open','WI-9999',1,'PWM-X',1,'PROJECT-X',1,"
        "'present','{}','x','s','2026-01-01T00:00:00Z')"
    )
    conn.commit()
    with pytest.raises(oe.OperationalEventError) as excinfo:
        oe.inspect(conn, event_id="LEGACY-1")
    assert excinfo.value.code == "event_absent"
