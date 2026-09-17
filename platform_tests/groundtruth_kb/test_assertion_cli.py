"""Ordinary assertion observations use the selected authority without writes."""

from __future__ import annotations

import json
import os
import re
import socket
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

import groundtruth_kb
import pytest
import uvicorn
from click.testing import CliRunner
from groundtruth_kb import assertions
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from psycopg import sql

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_authority_service import put

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


@pytest.fixture(params=["absent", "stale"])
def assertion_source(request, monkeypatch, tmp_path):
    """Current native input wins over absent or contradictory local SQLite data."""
    for name in ("GT_DB_PATH", "GT_PROJECT_ROOT", "GT_AUTHORITY_URL"):
        monkeypatch.delenv(name, raising=False)
    (tmp_path / "effect.py").write_text("value = 1\n", encoding="utf-8")
    database = tmp_path / "selected.db"
    config = tmp_path / "groundtruth.toml"
    settings = '[groundtruth]\ndb_path = "selected.db"\nproject_root = "."\nauthority_url = "http://127.0.0.1:8765"\n'
    if request.param == "stale":
        with sqlite3.connect(database) as connection:
            connection.execute(
                "CREATE TABLE specifications (id TEXT, version INTEGER, title TEXT, status TEXT, "
                "assertions TEXT, constraints TEXT, priority TEXT)"
            )
            connection.execute("CREATE VIEW current_specifications AS SELECT * FROM specifications")
            connection.execute(
                "INSERT INTO specifications VALUES (?,?,?,?,?,?,?)",
                (
                    "SPEC-1",
                    99,
                    "Conflicting local copy",
                    "active",
                    json.dumps([{"type": "file_exists", "file": "missing.py"}]),
                    "null",
                    "P1",
                ),
            )
    service, client, _, _ = request.getfixturevalue("native")
    calls = []
    original_request = AuthorityClient.request

    def transport(_self, method, path, *, body=None, query=None):
        calls.append((method, path))
        return original_request(_self, method, path, body=body, query=query)

    monkeypatch.setattr(AuthorityClient, "request", transport)

    def record(ident, fields, version=0):
        response = put(client, "specifications", ident, fields, expected_version=version)
        assert response.status_code == 200, response.text

    def snapshot():
        with service.kernel.transaction(read_only=True) as tx:
            tx.cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname=%s ORDER BY tablename", (tx.schema,))
            tables = [r["tablename"] for r in tx.cursor.fetchall()]
            records = {}
            for name in tables:
                tx.cursor.execute(
                    sql.SQL("SELECT * FROM {}.{}").format(sql.Identifier(tx.schema), sql.Identifier(name))
                )
                records[name] = sorted(
                    json.dumps(dict(row), default=str, sort_keys=True) for row in tx.cursor.fetchall()
                )
            return records, database.read_bytes() if database.is_file() else None

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        settings = settings.replace("http://127.0.0.1:8765", f"http://127.0.0.1:{port}")
        config.write_text(settings, encoding="utf-8")
        server = uvicorn.Server(uvicorn.Config(client.app, host="127.0.0.1", port=port, log_level="error"))
        worker = threading.Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
        worker.start()
        deadline = time.monotonic() + 10
        try:
            while not server.started and worker.is_alive() and time.monotonic() < deadline:
                time.sleep(0.01)
            assert server.started, "Disposable assertion authority did not start"
            yield config, record, snapshot, calls
        finally:
            server.should_exit = True
            worker.join(10)
            assert not worker.is_alive()


@pytest.mark.parametrize("behavior_required", [False, True])
def test_cli_observes_current_definitions_without_recording_or_schema_bootstrap(assertion_source, behavior_required):
    config, record, snapshot, calls = assertion_source
    fields = {
        "title": "Current effect",
        "status": "active",
        "assertions": [{"type": "file_exists", "file": "effect.py"}],
    }
    if behavior_required:
        fields["constraints"] = {"behavioral_validation_required": True}
    record("SPEC-1", fields)
    record(
        "SPEC-OLD",
        {
            "title": "Inert old requirement",
            "status": "retired",
            "assertions": [{"type": "file_exists", "file": "missing.py"}],
        },
    )
    before = snapshot()
    result = CliRunner().invoke(main, ["--config", str(config), "assert", "--json"])
    assert result.exit_code == (1 if behavior_required else 0), result.output
    report = json.loads(result.output)
    assert report["aggregate_result"] == ("PARTIAL" if behavior_required else "PASS")
    assert report["failed"] == 0
    assert report["partial"] == int(behavior_required)
    assert report["total_specs"] == 1
    assert report["details"][0]["spec_version"] == 1
    assert snapshot() == before
    assert all(method == "GET" for method, _ in calls)
    retired = CliRunner().invoke(main, ["--config", str(config), "assert", "--spec", "SPEC-OLD", "--json"])
    assert retired.exit_code == 1
    assert json.loads(retired.output)["aggregate_result"] == "NOT_APPLICABLE"
    assert snapshot() == before


def test_changed_canonical_definition_invalidates_an_earlier_passing_observation(assertion_source, monkeypatch):
    config, record, _, _ = assertion_source
    record(
        "SPEC-1",
        {"title": "Original effect", "status": "active", "assertions": [{"type": "file_exists", "file": "effect.py"}]},
    )
    original = assertions._RUNNERS["file_exists"]

    def change_while_checking(definition, context):
        record(
            "SPEC-1",
            {
                "title": "Changed requirement",
                "status": "active",
                "assertions": [{"type": "file_exists", "file": "missing.py"}],
            },
            version=1,
        )
        return original(definition, context)

    monkeypatch.setitem(assertions._RUNNERS, "file_exists", change_while_checking)
    result = CliRunner().invoke(main, ["--config", str(config), "assert", "--spec", "SPEC-1", "--json"])
    assert result.exit_code == 1, result.output
    report = json.loads(result.output)
    assert report["aggregate_result"] == "UNASSESSED"
    assert report["unassessed"] == 1 and report["failed"] == 0
    detail = report["details"][0]
    assert detail["spec_version"] == 1 and not detail["overall_passed"]
    assert detail["results"][-1]["type"] == "source_changed"


def test_read_only_database_refuses_writes_and_does_not_create_a_missing_source(tmp_path):
    path = tmp_path / "source.db"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE retained (value TEXT)")
    before = path.read_bytes()
    db = KnowledgeDB(path, read_only=True)
    try:
        assert db._get_conn().execute("PRAGMA user_version").fetchone()[0] == 0
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            db._get_conn().execute("INSERT INTO retained VALUES ('unwanted')")
    finally:
        db.close()
    assert path.read_bytes() == before
    missing = tmp_path / "absent.db"
    db = KnowledgeDB(missing, read_only=True)
    try:
        with pytest.raises(sqlite3.OperationalError):
            db.get_spec("SPEC-1")
    finally:
        db.close()
    assert not missing.exists()


def test_unavailable_native_authority_does_not_fall_back_to_sqlite(assertion_source, monkeypatch):
    config, record, snapshot, _ = assertion_source
    record("SPEC-1", {"title": "Effect", "status": "active"})
    before = snapshot()

    def unavailable(*args, **kwargs):
        raise AuthorityClientError("authority_unavailable", "Service unavailable")

    monkeypatch.setattr(AuthorityClient, "request", unavailable)
    result = CliRunner().invoke(main, ["--config", str(config), "assert", "--spec", "SPEC-1", "--json"])
    assert result.exit_code == 1 and "authority_unavailable" in result.output
    assert snapshot() == before


def test_missing_native_configuration_refuses_without_using_or_creating_sqlite(assertion_source):
    config, record, snapshot, calls = assertion_source
    record("SPEC-1", {"title": "Canonical effect", "status": "active"})
    config.write_text('[groundtruth]\ndb_path = "selected.db"\nproject_root = "."\n', encoding="utf-8")
    before = snapshot()
    result = CliRunner().invoke(main, ["--config", str(config), "assert", "--spec", "SPEC-1", "--json"])
    assert result.exit_code == 1 and "No authority_url is configured" in result.output
    assert calls == [] and snapshot() == before


@pytest.mark.parametrize("corpus", ["empty", "undefined", "mixed"])
def test_missing_definitions_remain_unassessed_and_cannot_make_a_corpus_pass(assertion_source, corpus):
    config, record, snapshot, _ = assertion_source
    if corpus != "empty":
        record("SPEC-EMPTY", {"title": "Required but undefined", "status": "active"})
    if corpus == "mixed":
        record(
            "SPEC-PASS",
            {
                "title": "Defined effect",
                "status": "active",
                "assertions": [{"type": "grep", "file": "effect.py", "pattern": "value = 1"}],
            },
        )
    before = snapshot()
    result = CliRunner().invoke(main, ["--config", str(config), "assert", "--json"])
    assert result.exit_code == 1, result.output
    report = json.loads(result.output)
    assert report["aggregate_result"] == ("PARTIAL" if corpus == "mixed" else "UNASSESSED")
    assert report["skipped"] == 0 and report["unassessed"] == int(corpus != "empty")
    assert report["specs_with_assertions"] == report["passed"] == int(corpus == "mixed")
    if corpus != "empty":
        missing = next(row for row in report["details"] if row["spec_id"] == "SPEC-EMPTY")
        assert missing["evaluation_result"] == "UNASSESSED" and missing["assertion_count"] == 0
    assert snapshot() == before


@pytest.mark.parametrize("changed_field", ["authority_url", "project_root"])
def test_assertion_configuration_changes_invalidate_the_observation(assertion_source, monkeypatch, changed_field):
    config, record, snapshot, calls = assertion_source
    record(
        "SPEC-1",
        {
            "title": "Selected effect",
            "status": "active",
            "assertions": [{"type": "grep", "file": "effect.py", "pattern": "value = 1"}],
        },
    )
    original = assertions._RUNNERS["grep"]
    before = snapshot()

    def change_configuration(definition, context):
        text = config.read_text(encoding="utf-8")
        if changed_field == "authority_url":
            text = re.sub(r'authority_url = "[^"]+"', 'authority_url = "http://127.0.0.1:1"', text)
        else:
            decoy = config.parent / "decoy"
            decoy.mkdir()
            (decoy / "effect.py").write_text("value = 2\n", encoding="utf-8")
            text = text.replace('project_root = "."', 'project_root = "decoy"')
        config.write_text(text, encoding="utf-8")
        return original(definition, context)

    monkeypatch.setitem(assertions._RUNNERS, "grep", change_configuration)
    result = CliRunner().invoke(main, ["--config", str(config), "assert", "--spec", "SPEC-1", "--json"])
    assert result.exit_code == 1 and "assertion_configuration_changed" in result.output, result.output
    assert snapshot() == before and all(method == "GET" for method, _ in calls)


def test_complete_native_assertion_pagination_uses_every_selected_definition(assertion_source, monkeypatch):
    config, record, snapshot, calls = assertion_source
    for ident, filename in (("SPEC-A", "effect.py"), ("SPEC-B", "effect.py"), ("SPEC-C", "missing.py")):
        record(ident, {"title": ident, "status": "active", "assertions": [{"type": "file_exists", "file": filename}]})
    original = AuthorityClient.request
    pages = []

    def one_record_per_page(self, method, path, *, body=None, query=None):
        if method == "GET" and path == "/v1/specifications":
            query = {**(query or {}), "limit": 1}
            pages.append(query.get("after"))
        return original(self, method, path, body=body, query=query)

    monkeypatch.setattr(AuthorityClient, "request", one_record_per_page)
    before = snapshot()
    result = CliRunner().invoke(main, ["--config", str(config), "assert", "--json"])
    assert result.exit_code == 1, result.output
    report = json.loads(result.output)
    assert report["aggregate_result"] == "FAIL" and report["passed"] == 2 and report["failed"] == 1
    assert [row["spec_id"] for row in report["details"]] == ["SPEC-A", "SPEC-B", "SPEC-C"]
    assert pages == [None, "SPEC-A", "SPEC-B", "SPEC-C"]
    assert snapshot() == before and all(method == "GET" for method, _ in calls)


@pytest.mark.parametrize("inactive_status", ["retired", "superseded"])
def test_changed_inactive_definition_cannot_reuse_old_inapplicability(assertion_source, monkeypatch, inactive_status):
    config, record, _, _ = assertion_source
    record("SPEC-OLD", {"title": "Previously inactive", "status": inactive_status})
    original = AuthorityClient.request
    reads = 0

    def change_after_initial_read(self, method, path, *, body=None, query=None):
        nonlocal reads
        result = original(self, method, path, body=body, query=query)
        if method == "GET" and path == "/v1/specifications/SPEC-OLD":
            reads += 1
            if reads == 1:
                record(
                    "SPEC-OLD",
                    {
                        "title": "Current active definition",
                        "status": "active",
                        "assertions": [{"type": "file_exists", "file": "missing.py"}],
                    },
                    version=1,
                )
        return result

    monkeypatch.setattr(AuthorityClient, "request", change_after_initial_read)
    result = CliRunner().invoke(main, ["--config", str(config), "assert", "--spec", "SPEC-OLD", "--json"])
    assert result.exit_code == 1, result.output
    report = json.loads(result.output)
    assert report["aggregate_result"] == "UNASSESSED" and report["skipped"] == 0
    assert report["details"][0]["results"][-1]["type"] == "source_changed"
    assert reads == 2


@pytest.mark.parametrize(
    "defect",
    ["missing-records", "missing-cursor", "bad-cursor", "empty-continuation", "duplicate-id", "repeated-cursor"],
)
def test_malformed_or_repeating_assertion_pages_fail_before_evaluation(tmp_path, monkeypatch, defect):
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\nproject_root="."\nauthority_url="http://127.0.0.1:1"\n', encoding="utf-8")
    count = 0

    def malformed(self, method, path, **kwargs):
        nonlocal count
        count += 1
        assert method == "GET" and path == "/v1/specifications"
        assert count <= 2, "Pagination retried a non-advancing response"
        row = {"id": f"SPEC-{count}", "version": 1, "status": "active", "title": "Unusable inventory"}
        return {
            "missing-records": {"next_after": None},
            "missing-cursor": {"records": [row]},
            "bad-cursor": {"records": [row], "next_after": 123},
            "empty-continuation": {"records": [], "next_after": "SPEC-1"},
            "duplicate-id": {"records": [row, row], "next_after": None},
            "repeated-cursor": {"records": [row], "next_after": "SAME"},
        }[defect]

    def refuse_evaluation(*args, **kwargs):
        raise AssertionError("Incomplete inventory reached assertion evaluation")

    monkeypatch.setattr(AuthorityClient, "request", malformed)
    monkeypatch.setattr(assertions, "run_spec_assertions", refuse_evaluation)
    result = CliRunner().invoke(main, ["--config", str(config), "assert", "--json"])
    assert result.exit_code == 1 and "invalid_response" in result.output, result.output
    assert count == (2 if defect == "repeated-cursor" else 1)
    assert list(tmp_path.iterdir()) == [config]


def test_cold_assertion_command_uses_real_http_without_database_access(assertion_source, tmp_path):
    config, record, snapshot, _ = assertion_source
    record(
        "SPEC-COLD",
        {
            "title": "Cold selected-root effect",
            "status": "active",
            "assertions": [{"type": "grep", "file": "effect.py", "pattern": "value = 1"}],
        },
    )
    caller = tmp_path / "unrelated caller"
    caller.mkdir()
    (caller / "effect.py").write_text("value = 2\n", encoding="utf-8")
    script = r"""
import json, os, runpy, sqlite3, sqlite3.dbapi2, sys
from pathlib import Path
import psycopg
def deny(*args, **kwargs):
    raise AssertionError("Assertion CLI attempted a direct database connection")
sqlite3.connect = sqlite3.dbapi2.connect = deny
psycopg.connect = psycopg.Connection.connect = psycopg.AsyncConnection.connect = deny
sentinel = Path(os.environ['GTKB_ASSERTION_SENTINEL']).resolve()
def audit(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        if Path(os.fsdecode(args[0])).resolve() == sentinel:
            raise AssertionError("Assertion CLI opened the local database sentinel")
sys.addaudithook(audit)
sys.argv = ['gt', *json.loads(sys.argv[1])]
runpy.run_module('groundtruth_kb', run_name='__main__')
"""
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("PG", "GT_POSTGRES_", "GIT_"))
        and key not in {"GT_AUTHORITY_URL", "GT_PROJECT_ROOT", "GTKB_PROJECT_ROOT", "PYTHONPATH"}
    }
    env.update(
        PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent),
        PYTHONIOENCODING="utf-8",
        PYTHONDONTWRITEBYTECODE="1",
        GTKB_ASSERTION_SENTINEL=str(config.parent / "selected.db"),
        GT_DB_PATH=str(config.parent / "selected.db"),
        PGDATABASE="forbidden",
        GT_POSTGRES_SERVICE="forbidden",
    )
    arguments = ["--config", str(config), "assert", "--spec", "SPEC-COLD", "--json"]
    before = snapshot()
    result = subprocess.run(
        [sys.executable, "-P", "-c", script, json.dumps(arguments)],
        cwd=caller,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["aggregate_result"] == "PASS" and report["details"][0]["spec_version"] == 1
    assert snapshot() == before and (caller / "effect.py").read_text(encoding="utf-8") == "value = 2\n"
