"""Bounded startup reads through real PostgreSQL, HTTP and ordinary CLI.

Host tool inventories, token counts and transient activity are not observed by
the authority service. These tests do not qualify a real host's startup.
"""

from __future__ import annotations

import hashlib
import json
import os
import socket
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.postgres_kernel import PostgresTransaction
from psycopg import sql

from platform_tests.groundtruth_kb.native_fixtures import (
    BASELINE,
    FORMALS,
    _serve_authority,
    database_contents,
    files,
    put,
    seed_startup_sources,
)
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


@pytest.fixture
def startup(native, tmp_path):
    service, _, _, _ = native
    with TestClient(create_authority_app(service, project_root=tmp_path)) as client:
        seed_startup_sources(client, tmp_path)
        result = client.post("/v1/sessions/bind", json={"native_context_id": "own", "init_command": "::init gtkb pb"})
        assert result.status_code == 200
        yield service, client, tmp_path, result.json()["binding"]


@pytest.mark.parametrize("subject,role", [("gtkb", "pb"), ("gtkb", "lo"), ("application", "pb"), ("application", "lo")])
def test_startup_reads_exact_binding_current_sources_and_truthful_host_limits(startup, subject, role, monkeypatch):
    service, client, root, _ = startup
    binding = client.post(
        "/v1/sessions/bind",
        json={
            "native_context_id": "selected",
            "init_command": f"::init {subject} {role}",
        },
    ).json()["binding"]
    foreign = root / "foreign-cwd"
    foreign.mkdir()
    (foreign / "session-bootstrap.md").write_text("Must not load this source", encoding="utf-8")
    monkeypatch.chdir(foreign)
    monkeypatch.setenv("GTKB_SESSION_ROLE", "lo" if role == "pb" else "pb")
    before, disk = database_contents(service), files(root)
    response = client.get("/v1/sessions/context", params={"native_context_id": "selected"})
    assert response.status_code == 200, response.text
    view = response.json()
    assert view["binding"] == binding
    assert {r["id"] for r in view["specifications"]} == set(FORMALS)
    assert all(r["status"] == "active" and r["version"] == 1 for r in view["specifications"])
    assert {r["path"]: r["content"] for r in view["baseline"]} == {
        p: (root / p).read_bytes().decode("utf-8-sig") for p in BASELINE
    }
    assert set(view["host_observations"]) == {"activity", "tools_skills_plugins_hooks", "startup_tokens"}
    assert all(v["status"] == "unavailable" and v["reason"] for v in view["host_observations"].values())
    assert "gt context work-item" in json.dumps(view["retrieval_routes"])
    assert "complete" in view["scope"] and "does not" in view["scope"]
    assert response.headers["cache-control"] == "no-store"
    assert database_contents(service) == before and files(root) == disk


def test_startup_requeries_current_formals_and_authored_baseline_without_changing_binding(startup):
    service, client, root, binding = startup
    first = client.get("/v1/sessions/context", params={"native_context_id": "own"})
    assert first.status_code == 200
    update = put(
        client, "specifications", FORMALS[0], {"description": "Reconciled current requirement"}, expected_version=1
    )
    assert update.status_code == 200, update.text
    (root / BASELINE[0]).write_text("Reconciled authored baseline", encoding="utf-8")
    before = database_contents(service)
    second = client.get("/v1/sessions/context", params={"native_context_id": "own"}).json()
    assert second["binding"] == binding
    record = next(r for r in second["specifications"] if r["id"] == FORMALS[0])
    assert record["version"] == 2 and record["description"] == "Reconciled current requirement"
    assert second["baseline"][0]["content"] == "Reconciled authored baseline"
    assert database_contents(service) == before


def test_startup_canonical_sources_share_one_read_snapshot(startup, monkeypatch):
    _, client, _, _ = startup
    original = PostgresTransaction.get
    updated = False

    def concurrent_get(tx, table, key, **kwargs):
        nonlocal updated
        result = original(tx, table, key, **kwargs)
        if table == "specifications" and key == {"id": FORMALS[0]} and not updated:
            updated = True
            response = put(
                client, "specifications", FORMALS[1], {"description": "Concurrent change"}, expected_version=1
            )
            assert response.status_code == 200, response.text
        return result

    monkeypatch.setattr(PostgresTransaction, "get", concurrent_get)
    first = client.get("/v1/sessions/context", params={"native_context_id": "own"})
    assert first.status_code == 200, first.text
    assert updated and all(r["version"] == 1 for r in first.json()["specifications"])
    second = client.get("/v1/sessions/context", params={"native_context_id": "own"}).json()
    assert next(r for r in second["specifications"] if r["id"] == FORMALS[1])["version"] == 2


@pytest.mark.parametrize("state", ["missing", "retired"])
def test_startup_refuses_missing_or_inactive_formals_without_partial_context(startup, state):
    service, client, root, _ = startup
    if state == "retired":
        result = put(client, "specifications", FORMALS[1], {"status": "retired"}, expected_version=1)
        assert result.status_code == 200, result.text
    else:
        # Removing an owned fixture row models unavailable canonical input.
        with service.kernel.transaction() as tx:
            tx.cursor.execute(
                sql.SQL("DELETE FROM {}.specifications WHERE id=%s").format(sql.Identifier(tx.schema)), (FORMALS[1],)
            )
    before, disk = database_contents(service), files(root)
    response = client.get("/v1/sessions/context", params={"native_context_id": "own"})
    assert response.status_code == 422, response.text
    error = response.json()["error"]
    assert error["code"] == "startup_source_unavailable"
    assert FORMALS[1] in json.dumps(error) and "gt spec show" in json.dumps(error)
    assert "binding" not in error and "baseline" not in error
    assert database_contents(service) == before and files(root) == disk


@pytest.mark.parametrize("state", ["missing", "directory", "invalid_utf8", "too_large", "redirected"])
def test_startup_refuses_unavailable_baseline_without_projection_fallback(startup, state):
    service, client, root, _ = startup
    path = root / BASELINE[0]
    if state in ("missing", "directory", "redirected"):
        path.unlink()
    if state == "directory":
        path.mkdir()
    elif state == "invalid_utf8":
        path.write_bytes(b"\xff")
    elif state == "too_large":
        path.write_bytes(b"x" * (65536 + 1))
    elif state == "redirected":
        # Redirect a whole directory; Windows junctions do not require symlink privilege.
        rules = path.parent
        target = root / "redirected-rules"
        assert rules.resolve().is_relative_to(root.resolve())
        assert target.resolve().is_relative_to(root.resolve())
        rules.rename(target)
        (target / path.name).write_text("Foreign baseline must not be disclosed", encoding="utf-8")
        if os.name == "nt":
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(rules), str(target)], capture_output=True)
            assert result.returncode == 0, result.stderr
        else:
            rules.symlink_to(target, target_is_directory=True)
    projection = root / ".codex" / "AGENTS.md"
    projection.parent.mkdir()
    projection.write_text("Generated fallback must not be loaded", encoding="utf-8")
    before, disk = database_contents(service), files(root)
    response = client.get("/v1/sessions/context", params={"native_context_id": "own"})
    assert response.status_code == 422, response.text
    error = response.json()["error"]
    assert error["code"] == "startup_source_unavailable" and BASELINE[0] in json.dumps(error)
    assert "Foreign baseline" not in response.text and "Generated fallback" not in response.text
    assert database_contents(service) == before and files(root) == disk


@pytest.mark.parametrize(
    "query",
    [
        "",
        "native_context_id=",
        "native_context_id=%20",
        "native_context_id=own&native_context_id=other",
        "native_context_id=own&root=foreign",
    ],
)
def test_startup_rejects_missing_blank_repeated_or_unknown_query_fields(startup, query):
    service, client, root, _ = startup
    before, disk = database_contents(service), files(root)
    response = client.get("/v1/sessions/context?" + query)
    assert response.status_code == 422, response.text
    assert database_contents(service) == before and files(root) == disk


def test_startup_requires_existing_exact_binding_without_initializing_or_falling_back(startup, monkeypatch):
    service, client, root, _ = startup
    monkeypatch.setenv("GTKB_NATIVE_CONTEXT_ID", "own")
    before, disk = database_contents(service), files(root)
    response = client.get("/v1/sessions/context", params={"native_context_id": "unbound"})
    assert response.status_code == 422 and response.json()["error"]["code"] == "no_session_binding"
    assert database_contents(service) == before and files(root) == disk


def test_ordinary_cli_startup_uses_selected_service_root_and_fails_on_outage(startup):
    service, client, root, binding = startup
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process, env = _serve_authority(root, port)
    client_root = root / "foreign-client"
    client_root.mkdir()
    config = client_root / "client.toml"
    config.write_text(
        f'[groundtruth]\nproject_root="."\nauthority_url="http://127.0.0.1:{port}"\ndb_path="sentinel.db"\n',
        encoding="utf-8",
    )
    legacy = client_root / "sentinel.db"
    with sqlite3.connect(legacy) as connection:
        connection.execute(
            "CREATE TABLE session_prompts (rowid INTEGER PRIMARY KEY, session_id TEXT, "
            "version INTEGER, event_type TEXT, prompt_text TEXT, context TEXT)"
        )
        connection.execute(
            "INSERT INTO session_prompts VALUES (1,'foreign-author',1,'created',"
            "'STORED_PROMPT_MUST_NOT_SUPPLY_CONTEXT','{\"role\":\"lo\"}')"
        )
    (client_root / "handoff.json").write_text(
        json.dumps({"native_context_id": "foreign-author", "role": "lo", "prompt": "OLD_HANDOFF_SENTINEL"}),
        encoding="utf-8",
    )
    env = {k: v for k, v in env.items() if not k.startswith(("PG", "GT_POSTGRES_"))}
    env.pop("GT_PROJECT_ROOT", None)
    env["PYTHONIOENCODING"] = "utf-8"
    command = [
        sys.executable,
        "-m",
        "groundtruth_kb",
        "--config",
        str(config),
        "context",
        "session",
        "--native-context-id",
        "own",
    ]

    def run(*args):
        return subprocess.run(
            [*command, *args],
            cwd=client_root,
            env=env,
            capture_output=True,
            encoding="utf-8",
            timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

    try:
        before, disk = database_contents(service), files(client_root)
        result = run("--json")
        assert result.returncode == 0, result.stderr
        view = json.loads(result.stdout)
        assert view["binding"] == binding
        assert view["baseline"][0]["content"] == (root / BASELINE[0]).read_bytes().decode("utf-8-sig")
        human = run()
        assert human.returncode == 0 and binding["session_context_id"] in human.stdout
        assert FORMALS[0] in human.stdout and "unavailable" in human.stdout
        assert database_contents(service) == before and files(client_root) == disk
        assert "STORED_PROMPT_MUST_NOT_SUPPLY_CONTEXT" not in result.stdout
        assert "OLD_HANDOFF_SENTINEL" not in human.stdout

        # A new process cannot adopt an unconsumed prompt or another binding.
        missing = subprocess.run(
            [*command[:-1], "successor", "--json"],
            cwd=client_root,
            env=env,
            capture_output=True,
            encoding="utf-8",
            timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        assert missing.returncode != 0 and not missing.stdout
        assert "no_session_binding" in missing.stderr
        assert database_contents(service) == before and files(client_root) == disk
        bound = subprocess.run(
            [
                *command[:5],
                "session",
                "bind",
                "--native-context-id",
                "successor",
                "--init-keyword",
                "::init gtkb lo",
                "--json",
            ],
            cwd=client_root,
            env=env,
            capture_output=True,
            encoding="utf-8",
            timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        assert bound.returncode == 0, bound.stderr
        successor = json.loads(bound.stdout)["binding"]
        assert (
            successor["role"] == "loyal-opposition" and successor["session_context_id"] != binding["session_context_id"]
        )
        before = database_contents(service)
        current_successor = subprocess.run(
            [*command[:-1], "successor", "--json"],
            cwd=client_root,
            env=env,
            capture_output=True,
            encoding="utf-8",
            timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        assert current_successor.returncode == 0, current_successor.stderr
        assert json.loads(current_successor.stdout)["binding"] == successor
        assert "STORED_PROMPT_MUST_NOT_SUPPLY_CONTEXT" not in current_successor.stdout
        assert database_contents(service) == before and files(client_root) == disk

        # A nonempty old view plus a fresh, self-consistent digest and declared
        # TTL cannot stand in for the next canonical read, even on service loss.
        cached = client_root / "startup-context.json"
        cached.write_text(json.dumps(view), encoding="utf-8")
        (client_root / "startup-context.meta.json").write_text(
            json.dumps(
                {
                    "source_path": str(cached),
                    "canonical_reader_output": True,
                    "generated_at": datetime.now(UTC).isoformat(),
                    "sha256": hashlib.sha256(cached.read_bytes()).hexdigest(),
                    "ttl_declared": True,
                    "ttl_minutes": 60,
                    "ttl_source": "startup-context.meta.json",
                    "fallback_to_canonical": True,
                    "status": "healthy",
                }
            ),
            encoding="utf-8",
        )
        update = put(
            client,
            "specifications",
            FORMALS[0],
            {"description": "Changed canonical requirement after the first CLI observation"},
            expected_version=1,
        )
        assert update.status_code == 200, update.text
        (root / BASELINE[0]).write_text("Changed authored baseline after the first CLI observation", encoding="utf-8")
        before, disk = database_contents(service), files(client_root)
        current = run("--json")
        assert current.returncode == 0, current.stderr
        current_view = json.loads(current.stdout)
        changed = next(r for r in current_view["specifications"] if r["id"] == FORMALS[0])
        assert changed["version"] == 2 and changed["description"] == update.json()["description"]
        assert current_view["binding"] == binding
        assert current_view["baseline"][0]["content"] == (root / BASELINE[0]).read_text(encoding="utf-8")
        assert current_view != view and database_contents(service) == before and files(client_root) == disk
        process.terminate()
        process.wait(timeout=10)
        failed = run("--json")
        assert failed.returncode != 0 and not failed.stdout
        assert database_contents(service) == before and files(client_root) == disk
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
