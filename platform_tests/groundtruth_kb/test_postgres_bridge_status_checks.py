"""Storage accepts only the twelve canonical bridge statuses (c123; batch design WP5 G17).

SPEC-BRIDGE-STATUS-PHASE-DISTINCT-001 v2 makes bridge/vocabulary.py the one enumeration. The writers already accept only
its twelve statuses, but storage did not: bridge_attempts.head_status, bridge_items.status and
work_intent_claims.intended_status had no CHECK. This release's schema constrains all three, and the explicit
transition from the c121 and c122 schema (4b5f8275...) adds the same constraints after refusing any stored value
outside the twelve, without rewriting a row.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterator
from contextlib import contextmanager

import groundtruth_kb.postgres_kernel as kernel_module
import psycopg
import pytest
from click.testing import CliRunner
from groundtruth_kb.bridge.vocabulary import CANONICAL_STATUSES
from groundtruth_kb.cli import main
from groundtruth_kb.config import PostgreSQLConfig
from groundtruth_kb.postgres_kernel import (
    BRIDGE_STATUS_PREDECESSOR_SHA256,
    PostgresKernel,
    PostgresKernelError,
    bridge_status_check_values,
)
from psycopg import errors, sql

from platform_tests.groundtruth_kb.postgres_fixtures import c121_schema_sql
from platform_tests.groundtruth_kb.postgres_fixtures import isolated_postgres as isolated_postgres

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]

CONSTRAINTS = (
    "bridge_attempts_head_status_check",
    "bridge_items_status_check",
    "work_intent_claims_intended_status_check",
)
REFUSED = ("NO-ACTION", "DEFERRED", "ACCEPTED", "verified")


def test_the_schema_lists_exactly_the_canonical_statuses():
    assert bridge_status_check_values() == tuple(sorted(CANONICAL_STATUSES))


def _seed_work(connection, suffix: str) -> tuple[str, str]:
    """A project and a work item, so an attempt can carry any head status (the ADVISORY check needs a work item)."""
    project, work_item = f"PROJECT-{suffix}", f"WI-{suffix}"
    connection.execute(
        'INSERT INTO projects(id,version,name,kind,"authorization",changed_by,changed_at,change_reason) '
        "VALUES (%s,1,'Fixture project','project','authorized','fixture',now(),'fixture')",
        (project,),
    )
    connection.execute(
        "INSERT INTO work_items(id,version,title,origin,component,resolution_status,changed_by,changed_at,"
        "change_reason) VALUES (%s,1,'Fixture item','test','test','open','fixture',now(),'fixture')",
        (work_item,),
    )
    return project, work_item


def _attempt(connection, suffix: str, head_status: str | None) -> str:
    project, work_item = _seed_work(connection, suffix)
    attempt = f"ATTEMPT-{suffix}"
    connection.execute(
        "INSERT INTO bridge_attempts(id,work_item_id,project_id,head_status) VALUES (%s,%s,%s,%s)",
        (attempt, work_item, project, head_status),
    )
    return attempt


def _item(connection, attempt: str, status: str) -> None:
    connection.execute(
        "INSERT INTO bridge_items(attempt_id,version,status,author_session_context_id,delivery_fence,content) "
        "VALUES (%s,1,%s,'SENV-fixture',1,'fixture content')",
        (attempt, status),
    )


def _claim(connection, attempt: str, status: str) -> None:
    connection.execute(
        "INSERT INTO work_intent_claims(attempt_id,next_version,intended_status,claimant_session_context_id,request_id) "
        "VALUES (%s,1,%s,'SENV-fixture','fixture-request')",
        (attempt, status),
    )


def _constraints(service: str) -> list[tuple]:
    with psycopg.connect(service=service) as connection:
        return connection.execute(
            "SELECT c.conname, c.contype, c.convalidated, pg_get_constraintdef(c.oid) FROM pg_constraint c "
            "JOIN pg_class t ON t.oid = c.conrelid JOIN pg_namespace n ON n.oid = t.relnamespace "
            "WHERE n.nspname = current_schema() AND c.conname = ANY(%s) ORDER BY c.conname",
            (list(CONSTRAINTS),),
        ).fetchall()


def _rows(service: str) -> dict[str, list]:
    with psycopg.connect(service=service) as connection:
        return {
            table: connection.execute(
                sql.SQL("SELECT to_jsonb(t) FROM {} t ORDER BY to_jsonb(t)::text").format(sql.Identifier(table))
            ).fetchall()
            for table in ("bridge_attempts", "bridge_items", "work_intent_claims", "record_history")
        }


@contextmanager
def _fresh_schema(service: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """A second disposable schema with this release's catalog, for comparing an upgraded catalog with a fresh one."""
    name = f"gtkb_test_{uuid.uuid4().hex}"
    with psycopg.connect(service=service, autocommit=True) as connection:
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(name)))
    try:
        with monkeypatch.context() as patch:
            patch.setenv("PGOPTIONS", f"-c search_path={name}")
            PostgresKernel(PostgreSQLConfig(service=service)).initialize()
            yield
    finally:
        with psycopg.connect(service=service, autocommit=True) as connection:
            connection.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(name)))


@pytest.fixture
def c121(isolated_postgres, monkeypatch):
    """A schema initialized with the c121 and c122 catalog, holding one attempt, item and claim per column."""
    service, _schema = isolated_postgres
    kernel = PostgresKernel(PostgreSQLConfig(service=service))
    old_sql = c121_schema_sql()
    with monkeypatch.context() as patch:
        patch.setattr(kernel_module, "schema_sql_bytes", lambda: old_sql)
        patch.setattr(kernel_module, "schema_sql_sha256", lambda: BRIDGE_STATUS_PREDECESSOR_SHA256)
        kernel.initialize()
    with psycopg.connect(service=service) as connection:
        attempt = _attempt(connection, "C121", "READY")
        _item(connection, attempt, "NEW")
        _claim(connection, attempt, "VERIFIED")
    return kernel, service


@pytest.mark.parametrize("value", REFUSED)
@pytest.mark.parametrize("column", ["head_status", "status", "intended_status"])
def test_a_fresh_schema_refuses_every_noncanonical_status(isolated_postgres, column, value):
    service, _schema = isolated_postgres
    PostgresKernel(PostgreSQLConfig(service=service)).initialize()
    # Autocommit: the seed rows commit, and the refused insert fails alone.
    with psycopg.connect(service=service, autocommit=True) as connection:
        with pytest.raises(errors.CheckViolation) as error:
            if column == "head_status":
                _attempt(connection, "BAD", value)
            else:
                attempt = _attempt(connection, "BAD", None)
                (_item if column == "status" else _claim)(connection, attempt, value)
        expected = {"head_status": CONSTRAINTS[0], "status": CONSTRAINTS[1], "intended_status": CONSTRAINTS[2]}
        assert error.value.diag.constraint_name == expected[column]


def test_a_fresh_schema_accepts_a_canonical_status_and_an_unset_head(isolated_postgres):
    service, _schema = isolated_postgres
    PostgresKernel(PostgreSQLConfig(service=service)).initialize()
    with psycopg.connect(service=service) as connection:
        _attempt(connection, "UNSET", None)
        attempt = _attempt(connection, "SET", "NOT-READY")
        _item(connection, attempt, "VERDICT-REJECTED")
        _claim(connection, attempt, "NO-GO")
    assert [row[0] for row in _constraints(service)] == list(CONSTRAINTS)


def test_the_transition_from_c121_adds_the_fresh_constraints_and_rewrites_nothing(c121, monkeypatch):
    kernel, service = c121
    before = _rows(service)
    assert _constraints(service) == []
    result = kernel.upgrade_schema(expected_schema_sha256=BRIDGE_STATUS_PREDECESSOR_SHA256)
    assert (result["status"], result["steps"]) == ("upgraded", ["bridge_status"])
    assert result["schema_sha256"] == kernel_module.schema_sql_sha256()
    assert _rows(service) == before
    assert kernel.status()["ready"] is True
    assert kernel.initialize()["status"] == "already_current"
    assert kernel.upgrade_schema(expected_schema_sha256=BRIDGE_STATUS_PREDECESSOR_SHA256)["status"] == "already_current"
    upgraded = _constraints(service)
    with _fresh_schema(service, monkeypatch):
        fresh = _constraints(service)
    assert upgraded == fresh
    assert [(row[0], row[1], row[2]) for row in upgraded] == [(name, "c", True) for name in CONSTRAINTS]


@pytest.mark.parametrize("column", ["head_status", "status", "intended_status"])
def test_a_stored_noncanonical_status_refuses_the_transition_and_changes_nothing(c121, column):
    kernel, service = c121
    with psycopg.connect(service=service) as connection:
        attempt = _attempt(connection, "LEGACY", "DEFERRED" if column == "head_status" else "NEW")
        if column == "status":
            _item(connection, attempt, "NO-ACTION")
        elif column == "intended_status":
            _claim(connection, attempt, "ACCEPTED")
    before = _rows(service)
    with pytest.raises(PostgresKernelError) as error:
        kernel.upgrade_schema(expected_schema_sha256=BRIDGE_STATUS_PREDECESSOR_SHA256)
    assert error.value.code == "bridge_status_reconciliation_required"
    table = {"head_status": "bridge_attempts", "status": "bridge_items", "intended_status": "work_intent_claims"}
    detail = error.value.details[f"{table[column]}.{column}"]
    assert detail["attempt_ids"] == ["ATTEMPT-LEGACY"]
    assert detail["values"] == [
        {"head_status": "DEFERRED", "status": "NO-ACTION", "intended_status": "ACCEPTED"}[column]
    ]
    assert "fixture content" not in json.dumps(error.value.details)
    assert _rows(service) == before
    assert _constraints(service) == []


def test_the_cli_reports_the_transition_from_c121(c121):
    _kernel, _service = c121
    result = CliRunner().invoke(main, ["db", "postgres", "init", "--upgrade-from", BRIDGE_STATUS_PREDECESSOR_SHA256])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert (payload["status"], payload["upgraded_from"]) == ("upgraded", BRIDGE_STATUS_PREDECESSOR_SHA256)
