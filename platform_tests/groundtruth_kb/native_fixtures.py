"""Shared fixtures and helpers of the native authority qualification (c102, Q-3, owner ruling D23).

Moved verbatim from the test modules that defined them so that no test module imports another
test module: the ``native`` disposable-PostgreSQL fixture and its record helpers, the served
authority launcher, the session-context sources, the harness diagnostic helpers, the membership
CLI fixture and the assertion-source fixture. This module is not collected (its name does not
start with ``test_``) and defines no test; a test module binds a fixture by importing it under
its own name (``from ... import native as native``), which is what pytest registers.
"""

from __future__ import annotations

import json
import os
import socket
import sqlite3
import subprocess
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import groundtruth_kb
import psycopg
import pytest
import uvicorn
from fastapi.testclient import TestClient
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import PostgreSQLConfig
from groundtruth_kb.native_authority import AuthorityService
from groundtruth_kb.postgres_kernel import TABLE_SPECS, PostgresKernel
from psycopg import sql


@pytest.fixture
def native(monkeypatch):
    if os.environ.get("GTKB_RUN_POSTGRES_INTEGRATION") != "1":
        pytest.fail("Explicitly select a disposable PostgreSQL installation")
    service_name = os.environ.get("GTKB_TEST_POSTGRES_SERVICE")
    if not service_name:
        pytest.fail("GTKB_TEST_POSTGRES_SERVICE is required")
    # Every CLI/service child must use the same package as the parent test.
    # This also preserves installed-package isolation in a separate checkout.
    monkeypatch.setenv("PYTHONPATH", str(Path(groundtruth_kb.__file__).resolve().parent.parent))
    schema = f"gtkb_test_{uuid4().hex}"
    with psycopg.connect(service=service_name, autocommit=True) as connection:
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
    monkeypatch.setenv("PGOPTIONS", f"-c search_path={schema}")
    try:
        with psycopg.connect(service=service_name) as connection:
            assert connection.execute("SELECT current_schema()").fetchone()[0] == schema
        kernel = PostgresKernel(PostgreSQLConfig(service=service_name))
        kernel.initialize()
        service = AuthorityService(kernel)
        with TestClient(create_authority_app(service)) as client:
            yield service, client, schema, service_name
    finally:
        with psycopg.connect(service=service_name, autocommit=True) as connection:
            connection.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))


def put(client, domain, record_id, fields, *, expected_version=0, **extra):
    # Existing platform fixtures declare their repository explicitly. Tests of
    # omitted references submit the raw native request instead of this helper.
    if domain == "projects" and expected_version == 0 and extra.get("kind", "project") == "project":
        fields = {"repository_ref": "platform", **fields}
    return client.put(
        f"/v1/{domain}/{record_id}",
        json={
            "expected_version": expected_version,
            "actor": "qualification",
            "reason": "Exercise native domain behavior",
            "fields": fields,
            **extra,
        },
    )


def seed(client):
    inputs = [
        (
            "specifications",
            "SPEC-1",
            {"title": "Required effect", "description": "Preserve complete work", "status": "active"},
            {},
        ),
        (
            "tests",
            "TEST-1",
            {
                "title": "Effect test",
                "spec_id": "SPEC-1",
                "test_type": "integration",
                "test_file": "tests/test_effect.py",
                "expected_outcome": "Effect observed",
            },
            {},
        ),
        ("test-plans", "PLAN-1", {"title": "Behavioral qualification"}, {}),
        (
            "test-phases",
            "PHASE-1",
            {
                "title": "Native effects",
                "plan_id": "PLAN-1",
                "phase_order": 10,
                "gate_criteria": "Observable result",
                "test_ids": ["TEST-1"],
            },
            {},
        ),
        ("projects", "PROGRAM-1", {"name": "Coherent platform"}, {"kind": "program"}),
        (
            "projects",
            "PROJECT-1",
            {
                "name": "Complete outcome",
                "parent_project_id": "PROGRAM-1",
                "target_outcome": "Complete native authority",
            },
            {},
        ),
        ("projects", "PROJECT-GTKB-NEW-WORK-INTAKE", {"name": "Standing intake"}, {}),
    ]
    for domain, record_id, fields, extra in inputs:
        result = put(client, domain, record_id, fields, **extra)
        assert result.status_code == 200, result.text


def work_fields(**extra):
    return {"title": "Artifact correction", "source_spec_id": "SPEC-1", "source_test_id": "TEST-1", **extra}


def history_count(service):
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(sql.SQL("SELECT count(*) AS n FROM {}.record_history").format(sql.Identifier(tx.schema)))
        return tx.cursor.fetchone()["n"]


def link_project_formal(service, spec_id):
    """Set up an existing canonical relationship, without a second test registry."""
    row = {column: None for column in TABLE_SPECS["project_artifact_links"].columns}
    row.update(
        id=f"LINK-{spec_id}",
        version=1,
        project_id="PROJECT-1",
        artifact_type="spec",
        artifact_ref=spec_id,
        relationship="governs",
        status="active",
        changed_at=datetime.now(UTC).isoformat(),
        changed_by="qualification",
        change_reason="Current project requirement",
    )
    service.kernel.mutate_current(
        table="project_artifact_links",
        identity={"id": row["id"]},
        expected_version=0,
        new_state=row,
        actor="qualification",
        reason="Current project requirement",
    )


FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _serve_authority(tmp_path, port):
    config = tmp_path / "server.toml"
    config.write_text(
        '[groundtruth]\nproject_root="."\n[postgresql]\nservice="' + os.environ["GTKB_TEST_POSTGRES_SERVICE"] + '"\n',
        encoding="utf-8",
    )
    env = dict(
        os.environ, GT_PROJECT_ROOT=str(tmp_path), PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent)
    )
    env.pop("GT_AUTHORITY_URL", None)
    log = (tmp_path / "service.log").open("wb")
    process = subprocess.Popen(
        [sys.executable, "-m", "groundtruth_kb", "--config", str(config), "service", "serve", "--port", str(port)],
        cwd=tmp_path,
        env=env,
        stdout=log,
        stderr=log,
        creationflags=FLAGS,
    )
    http = AuthorityClient(f"http://127.0.0.1:{port}", timeout=1)
    deadline = time.monotonic() + 25
    while True:
        try:
            http.request("GET", "/v1/status")
            return process, env
        except AuthorityClientError:
            assert process.poll() is None and time.monotonic() < deadline, "Isolated authority failed to start"
            time.sleep(0.1)


def harness_fields(**extra):
    fields = {"harness_name": "qualification", "harness_type": "test", "capabilities_ref": "qualification.json"}
    fields.update(extra)
    return fields


FORMALS = (
    "GOV-SESSION-SELF-INITIALIZATION-001",
    "DCL-SESSION-ROLE-RESOLUTION-001",
    "GOV-HARNESS-ISOLATION-001",
)
BASELINE = (
    ".harness-baseline-configuration/rules/session-bootstrap.md",
    ".harness-baseline-configuration/rules/operating-model.md",
)


def seed_startup_sources(client, root):
    """Declare owned sources; never borrow production state or generated files."""
    for record_id in FORMALS:
        result = put(
            client,
            "specifications",
            record_id,
            {"title": record_id, "description": f"Current requirement: {record_id}", "status": "active"},
        )
        assert result.status_code == 200, result.text
    for relative in BASELINE:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"Authored role-neutral source: {relative}\n", encoding="utf-8")


def database_contents(service):
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname=%s ORDER BY tablename", (tx.schema,))
        tables = [row["tablename"] for row in tx.cursor.fetchall()]
        result = {}
        for table in tables:
            tx.cursor.execute(sql.SQL("SELECT * FROM {}.{}").format(sql.Identifier(tx.schema), sql.Identifier(table)))
            result[table] = sorted(json.dumps(dict(row), default=str, sort_keys=True) for row in tx.cursor.fetchall())
        return result


def files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def register(client, identifier="A", *, active=True):
    row = put(
        client,
        "harnesses",
        identifier,
        {
            "harness_name": "harness-" + identifier,
            "harness_type": "test",
            "capabilities_ref": "public-declared-capabilities",
            "invocation_surfaces": {
                "headless": {
                    "argv": ["runner", "--model", "private-model", "private-prompt"],
                    "env": {"TOKEN": "private-credential"},
                },
                "private-surface-content": {"role": "loyal-opposition", "output": "private-generated-text"},
            },
        },
    )
    assert row.status_code == 200, row.text
    if active:
        assert put(client, "harnesses", identifier, {"status": "active"}, expected_version=1).status_code == 200


def bind(client, name, role):
    response = client.post("/v1/sessions/bind", json={"native_context_id": name, "init_command": "::init gtkb " + role})
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "init_requested"
    return response.json()["binding"]


def project(client, record_id="PROJECT-2"):
    response = put(client, "projects", record_id, {"name": record_id, "target_outcome": "A complete test outcome"})
    assert response.status_code == 200, response.text


@pytest.fixture
def membership_cli(native, tmp_path):
    service, client, _, service_name = native
    seed(client)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(b"Native membership must never open or amend this SQLite substitute.")
    server = tmp_path / "server.toml"
    server.write_text(f'[groundtruth]\nproject_root="."\n[postgresql]\nservice="{service_name}"\n', encoding="utf-8")
    config = tmp_path / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\nproject_root="."\nauthority_url="{url}"\ndb_path="groundtruth.db"\n', encoding="utf-8"
    )
    base_env = dict(os.environ, PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent))
    base_env.pop("GT_AUTHORITY_URL", None)
    base_env["GT_PROJECT_ROOT"] = str(tmp_path)
    base_env["GT_DB_PATH"] = str(sentinel)
    client_env = {k: v for k, v in base_env.items() if not k.startswith(("PG", "GT_POSTGRES_"))}
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    def cli(*args):
        return subprocess.run(
            [sys.executable, "-m", "groundtruth_kb", "--config", str(config), *args],
            cwd=tmp_path,
            env=client_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            creationflags=flags,
        )

    original = sentinel.read_bytes()
    with (tmp_path / "service.log").open("wb") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "groundtruth_kb", "--config", str(server), "service", "serve", "--port", str(port)],
            cwd=tmp_path,
            env=base_env,
            stdout=log,
            stderr=log,
            creationflags=flags,
        )

        def stop():
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=15)

        try:
            deadline = time.monotonic() + 30
            http = AuthorityClient(url, timeout=1)
            while True:
                try:
                    http.request("GET", "/v1/status")
                    break
                except AuthorityClientError:
                    if process.poll() is not None or time.monotonic() >= deadline:
                        pytest.fail("Native membership authority did not start; inspect service.log")
                    time.sleep(0.1)
            yield service, client, cli, stop
        finally:
            stop()
            assert sentinel.read_bytes() == original


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
    service, _, _, _ = request.getfixturevalue("native")
    # The disposable authority serves from a catalog host so records may carry application:<name> scopes.
    host = tmp_path / "authority-host"
    (host / "applications").mkdir(parents=True)
    (host / "applications/registry.toml").write_text(
        '[applications]\nAlpha={slot="Alpha"}\nBeta={slot="Beta"}\n', encoding="utf-8"
    )
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

    with TestClient(create_authority_app(service, project_root=host)) as client, socket.socket() as listener:
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
