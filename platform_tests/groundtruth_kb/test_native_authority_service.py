"""Behavioral qualification on an explicitly selected disposable PostgreSQL.

Exercises native domain transactions, concurrent changes, HTTP validation and
separate ordinary CLI processes with no PostgreSQL credentials in their env.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import PostgreSQLConfig
from groundtruth_kb.native_authority import AuthorityService, WorkItemMutation
from groundtruth_kb.postgres_kernel import (
    TABLE_SPECS,
    PostgresKernel,
    PostgresKernelError,
    canonical_json_bytes,
    parse_json_bytes,
)
from psycopg import sql

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


@pytest.fixture
def native(monkeypatch):
    if os.environ.get("GTKB_RUN_POSTGRES_INTEGRATION") != "1":
        pytest.fail("Explicitly select a disposable PostgreSQL installation")
    service_name = os.environ.get("GTKB_TEST_POSTGRES_SERVICE")
    if not service_name:
        pytest.fail("GTKB_TEST_POSTGRES_SERVICE is required")
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


def test_atomic_membership_and_program_semantics(native):
    service, client, _, _ = native
    seed(client)
    program = client.get("/v1/projects/PROGRAM-1").json()["project"]
    assert program["kind"] == "program" and program["authorization"] is None
    bad = put(client, "work-items", "WI-1", work_fields(), project_id="PROGRAM-1")
    assert bad.status_code == 422
    assert bad.json()["error"]["code"] == "program_cannot_contain_work"
    assert client.get("/v1/work-items/WI-1").status_code == 404
    result = put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1")
    assert result.status_code == 200, result.text
    initial = result.json()["membership"]
    request = {
        "expected_version": initial["version"],
        "source_project_id": "PROJECT-1",
        "destination_project_id": "PROJECT-GTKB-NEW-WORK-INTAKE",
        "actor": "another-context",
        "reason": "Move work without changing authorization",
        "membership_order": 20,
    }
    before = history_count(service)
    # The source removal is already written in the transaction when destination
    # normalization rejects this out-of-range order. Both changes must roll back.
    invalid_order = client.post("/v1/work-items/WI-1/move", json={**request, "membership_order": 2**63})
    assert invalid_order.status_code == 422
    assert history_count(service) == before
    assert client.get("/v1/work-items/WI-1").json()["membership"] == initial
    result = client.post("/v1/work-items/WI-1/move", json=request)
    assert result.status_code == 200, result.text
    assert history_count(service) == before + 2
    current = result.json()["membership"]
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["authorization"] == "authorized"
    assert (
        client.get("/v1/projects/PROJECT-GTKB-NEW-WORK-INTAKE").json()["project"]["authorization"] == "not authorized"
    )
    # A stale replay produces no membership or history mutation.
    stale = client.post("/v1/work-items/WI-1/move", json=request)
    assert stale.status_code == 409
    assert history_count(service) == before + 2
    request.update(
        source_project_id=request["destination_project_id"],
        destination_project_id="PROJECT-1",
        expected_version=current["version"],
    )
    back = client.post("/v1/work-items/WI-1/move", json=request)
    assert back.status_code == 200, back.text
    assert back.json()["membership"]["id"] == initial["id"]
    assert back.json()["membership"]["version"] == 3


def test_failed_domain_change_leaves_no_partial_work_or_history(native):
    service, client, _, _ = native
    seed(client)
    before = history_count(service)
    missing = put(client, "work-items", "WI-INVALID", work_fields(title=None), project_id="PROJECT-1")
    assert missing.status_code == 422
    assert history_count(service) == before
    assert client.get("/v1/work-items/WI-INVALID").status_code == 404
    result = put(
        client,
        "tests",
        "TEST-NO-PHASE",
        {
            "title": "Not scheduled",
            "spec_id": "SPEC-1",
            "test_type": "unit",
            "test_file": "test_missing.py",
            "expected_outcome": "Required effect",
        },
    )
    assert result.status_code == 200
    before = history_count(service)
    refused = put(
        client, "work-items", "WI-NO-PHASE", work_fields(source_test_id="TEST-NO-PHASE"), project_id="PROJECT-1"
    )
    assert refused.status_code == 422
    assert refused.json()["error"]["code"] == "test_phase_required"
    assert history_count(service) == before
    # The current record remains byte-for-byte unchanged after a stale amendment.
    before_record = client.get("/v1/specifications/SPEC-1").content
    refusal = put(client, "specifications", "SPEC-1", {"title": "stale"})
    assert refusal.status_code == 409
    assert client.get("/v1/specifications/SPEC-1").content == before_record


def test_concurrent_creation_and_dependency_write_skew(native):
    service, client, _, _ = native
    seed(client)
    request = WorkItemMutation(
        expected_version=0, actor="worker", reason="New work", project_id="PROJECT-1", fields=work_fields()
    )

    def create():
        try:
            return service.amend_work_item("WI-1", request)
        except PostgresKernelError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as workers:
        outcomes = list(workers.map(lambda _: create(), range(2)))
    assert sum(isinstance(value, dict) for value in outcomes) == 1
    assert any(value in ("cas_conflict", "retryable_conflict") for value in outcomes if isinstance(value, str))
    assert put(client, "work-items", "WI-2", work_fields(), project_id="PROJECT-1").status_code == 200

    def depend(pair):
        own, other = pair
        try:
            return service.amend_work_item(
                own,
                WorkItemMutation(
                    expected_version=1,
                    actor="worker",
                    reason="Sequence related effects",
                    fields={"depends_on_work_items": [other]},
                ),
            )
        except PostgresKernelError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as workers:
        outcomes = list(workers.map(depend, [("WI-1", "WI-2"), ("WI-2", "WI-1")]))
    assert sum(isinstance(value, dict) for value in outcomes) == 1
    assert any(value in ("dependency_cycle", "retryable_conflict") for value in outcomes if isinstance(value, str))


def test_work_item_dependency_replacement_refuses_invalid_graph_without_partial_effects(native):
    service, client, _, _ = native
    seed(client)
    for item in ("WI-1", "WI-2"):
        assert put(client, "work-items", item, work_fields(), project_id="PROJECT-1").status_code == 200
    for dependencies, code in (
        (["MISSING"], "missing_work_item_dependency"),
        (["WI-2", "WI-2"], "duplicate_work_item_dependency"),
        (["WI-1"], "dependency_cycle"),
    ):
        before = client.get("/v1/work-items/WI-1").content
        count = history_count(service)
        refused = put(client, "work-items", "WI-1", {"depends_on_work_items": dependencies}, expected_version=1)
        assert refused.json()["error"]["code"] == code, refused.text
        assert "WI-1" in str(refused.json()["error"]["details"])
        assert client.get("/v1/work-items/WI-1").content == before
        assert history_count(service) == count
    result = put(client, "work-items", "WI-1", {"depends_on_work_items": ["WI-2"]}, expected_version=1)
    assert result.status_code == 200, result.text
    assert [row["id"] for row in client.get("/v1/work-items/WI-1/context").json()["predecessors"]] == ["WI-2"]
    before = history_count(service)
    refused = put(client, "work-items", "WI-2", {"depends_on_work_items": ["WI-1"]}, expected_version=1)
    assert refused.json()["error"]["code"] == "dependency_cycle"
    assert history_count(service) == before
    result = put(client, "work-items", "WI-1", {"depends_on_work_items": []}, expected_version=2)
    assert result.status_code == 200, result.text
    assert client.get("/v1/work-items/WI-1/context").json()["predecessors"] == []


def test_transport_rejects_foreign_authority_fields_and_preserves_json_precision(native):
    _, client, _, _ = native
    seed(client)
    before = client.get("/v1/projects/PROJECT-1").content
    for fields in ({"authorization": "not authorized"}, {"status": "verified"}, {"pauth_id": "obsolete"}):
        result = put(client, "projects", "PROJECT-1", fields, expected_version=1)
        assert result.status_code == 422
    assert client.get("/v1/projects/PROJECT-1").content == before
    refused = client.put("/v1/projects/PROJECT-1", json={"secret": "do-not-echo"})
    assert refused.status_code == 422 and "do-not-echo" not in refused.text
    assert client.get("/v1/projects", headers={"Origin": "https://unrelated.example"}).status_code == 403
    for query in ("?ignored_filter=value", "?status=active&status=retired"):
        refused = client.get("/v1/projects" + query)
        assert refused.status_code == 422
        assert refused.json()["error"]["code"] == "invalid_query"
    assert client.post("/v1/work-items/WI-1/move", content="{}").status_code == 415
    number = Decimal("0.123456789012345678901234567890123456789")
    body = {
        "expected_version": 1,
        "actor": "worker",
        "reason": "Preserve exact threshold",
        "fields": {"constraints": {"threshold": number}},
    }
    amended = client.put(
        "/v1/specifications/SPEC-1", content=canonical_json_bytes(body), headers={"Content-Type": "application/json"}
    )
    assert amended.status_code == 200, amended.text
    assert parse_json_bytes(amended.content)["constraints"]["threshold"] == number
    duplicate = client.put(
        "/v1/specifications/SPEC-1",
        content=b'{"expected_version":1,"expected_version":2}',
        headers={"Content-Type": "application/json"},
    )
    assert duplicate.status_code == 400


def test_fresh_task_context_uses_current_canon_and_rejects_retired_source(native):
    _, client, _, _ = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    initial = client.get("/v1/work-items/WI-1/context")
    assert initial.status_code == 200
    assert initial.json()["program"]["id"] == "PROGRAM-1"
    assert initial.json()["test"]["id"] == "TEST-1"
    assert (
        put(
            client, "specifications", "SPEC-1", {"description": "Owner's current direction"}, expected_version=1
        ).status_code
        == 200
    )
    fresh = client.get("/v1/work-items/WI-1/context").json()
    assert fresh["specifications"][0]["description"] == "Owner's current direction"
    assert fresh["specifications"][0]["version"] == 2
    assert fresh["work_item"]["origin"] == "manual"
    assert put(client, "specifications", "SPEC-1", {"status": "retired"}, expected_version=2).status_code == 200
    refused = client.get("/v1/work-items/WI-1/context")
    assert refused.status_code == 422
    assert refused.json()["error"]["code"] == "inactive_context_source"


def test_separate_ordinary_cli_processes_use_http_and_never_sqlite(native, tmp_path):
    service, client, _, service_name = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "code.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "tests/test_effect.py").write_text("def test_effect(): assert 1 == 1\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text(".worktrees/\n", encoding="utf-8")
    for arguments in (
        ["config", "user.name", "Qualification"],
        ["config", "user.email", "qualification@example.invalid"],
        ["add", "--", "code.py", "tests/test_effect.py", ".gitignore"],
        ["commit", "-qm", "Isolated CLI preimage"],
    ):
        subprocess.run(["git", "-C", str(tmp_path), *arguments], check=True, capture_output=True)
    harness = {column: None for column in TABLE_SPECS["harnesses"].columns}
    harness.update(
        id="HARNESS-CLI",
        version=1,
        harness_name="cli-qualification",
        harness_type="test",
        status="registered",
        changed_at=datetime.now(UTC).isoformat(),
        changed_by="qualification",
        change_reason="CLI bridge test",
    )
    service.kernel.mutate_current(
        table="harnesses",
        identity={"id": harness["id"]},
        expected_version=0,
        new_state=harness,
        actor="qualification",
        reason="CLI bridge test",
    )
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    sentinel = tmp_path / "must-not-open.db"
    sentinel.write_bytes(b"This is not a SQLite database; opening it is a test failure.")
    server_config = tmp_path / "server.toml"
    server_config.write_text(
        f'[groundtruth]\nproject_root="."\n[postgresql]\nservice="{service_name}"\n', encoding="utf-8"
    )
    client_config = tmp_path / "client.toml"
    client_config.write_text(
        f'[groundtruth]\nauthority_url="{url}"\ndb_path="must-not-open.db"\nproject_root="."\n', encoding="utf-8"
    )
    base_env = os.environ.copy()
    base_env.pop("GT_AUTHORITY_URL", None)
    base_env["GT_DB_PATH"] = str(sentinel)
    base_env["GT_PROJECT_ROOT"] = str(tmp_path)
    client_env = {key: value for key, value in base_env.items() if not key.startswith(("PG", "GT_POSTGRES_"))}
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    def cli(*arguments):
        return subprocess.run(
            [sys.executable, "-m", "groundtruth_kb", "--config", str(client_config), *arguments],
            cwd=tmp_path,
            env=client_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            creationflags=flags,
        )

    with (tmp_path / "service.log").open("wb") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "groundtruth_kb",
                "--config",
                str(server_config),
                "service",
                "serve",
                "--port",
                str(port),
            ],
            cwd=tmp_path,
            env=base_env,
            stdout=log,
            stderr=log,
            creationflags=flags,
        )
        try:
            deadline = time.monotonic() + 30
            http = AuthorityClient(url, timeout=1)
            while True:
                try:
                    http.request("GET", "/v1/status")
                    break
                except AuthorityClientError:
                    if process.poll() is not None or time.monotonic() >= deadline:
                        pytest.fail("Native authority did not start; inspect disposable service.log")
                    time.sleep(0.1)
            result = cli("projects", "show", "PROJECT-1", "--json")
            assert result.returncode == 0, result.stderr
            assert json.loads(result.stdout)["project"]["authorization"] == "authorized"
            dependency_file = tmp_path / "dependency.json"
            dependency_file.write_text(
                json.dumps(
                    {
                        "dependent_project_id": "PROJECT-1",
                        "prerequisite_project_id": "PROJECT-GTKB-NEW-WORK-INTAKE",
                        "required_prerequisite_state": "verified",
                        "affected_gate": "readiness",
                        "rationale": "Qualify prerequisite diagnostics and canonical correction through ordinary CLI",
                    }
                ),
                encoding="utf-8",
            )

            def dependency_record(version):
                return cli(
                    "projects",
                    "dependencies",
                    "record",
                    "--id",
                    "DEP-CLI",
                    "--fields-file",
                    str(dependency_file),
                    "--expected-version",
                    str(version),
                    "--actor",
                    "qualification",
                    "--change-reason",
                    "Current dependency correction",
                    "--json",
                )

            created = dependency_record(0)
            assert created.returncode == 0, created.stderr
            listed = cli("projects", "dependencies", "list", "--dependent-project", "PROJECT-1", "--json")
            assert listed.returncode == 0 and json.loads(listed.stdout)[0]["id"] == "DEP-CLI", listed.stderr
            readiness = cli("projects", "readiness", "PROJECT-1", "--json")
            assert readiness.returncode == 0 and json.loads(readiness.stdout)["ready"] is False, readiness.stderr
            shown = cli("projects", "dependencies", "show", "DEP-CLI")
            assert shown.returncode == 0 and "PROJECT-GTKB-NEW-WORK-INTAKE = verified" in shown.stdout, shown.stderr
            dependency_file.write_text('{"status":"retired"}', encoding="utf-8")
            retired = dependency_record(1)
            assert retired.returncode == 0 and json.loads(retired.stdout)["status"] == "retired", retired.stderr
            amendment = tmp_path / "fields.json"
            amendment.write_text(
                json.dumps({"description": "Fresh context reads current canon: æ¼¢å­— cafÃ©"}), encoding="utf-8"
            )
            result = cli(
                "spec",
                "record",
                "--id",
                "SPEC-1",
                "--fields-file",
                str(amendment),
                "--expected-version",
                "1",
                "--actor",
                "interactive-correction",
                "--change-reason",
                "Current direction",
                "--json",
            )
            assert result.returncode == 0, result.stderr
            result = cli("context", "work-item", "WI-1", "--json")
            assert result.returncode == 0, result.stderr
            assert json.loads(result.stdout)["specifications"][0]["description"].endswith("æ¼¢å­— cafÃ©")
            # Each call starts a fresh CLI process without PostgreSQL credentials.
            for version, (role, status) in enumerate(
                (("pb", "NEW"), ("lo", "GO"), ("pb", "READY"), ("lo", "VERIFIED")), 1
            ):
                context = f"qualification-{role}-{version}"
                bound = cli(
                    "session", "bind", "--native-context-id", context, "--init-keyword", f"::init gtkb {role}", "--json"
                )
                assert bound.returncode == 0, bound.stderr
                session_id = json.loads(bound.stdout)["session_context_id"]
                claim = cli(
                    "bridge",
                    "claim",
                    "cli-chain",
                    "--work-item-id",
                    "WI-1",
                    "--native-context-id",
                    context,
                    "--expected-version",
                    str(version - 1),
                    "--status",
                    status,
                    "--request-id",
                    str(uuid4()),
                    "--json",
                )
                assert claim.returncode == 0, claim.stderr
                fence = json.loads(claim.stdout)["fence"]
                receiver = "lo" if status in {"NEW", "READY"} else "pb" if status == "GO" else None
                lines = [f"::init gtkb {receiver}", "::open build", status] if receiver else [status]
                kind = (
                    "implementation_proposal"
                    if status == "NEW"
                    else "implementation_report"
                    if status == "READY"
                    else "lo_verdict"
                )
                metadata = {
                    "bridge_kind": kind,
                    "Document": "cli-chain",
                    "Version": str(version),
                    "Date": datetime.now(UTC).date().isoformat(),
                    "author_identity": "qualified-agent",
                    "author_harness_id": "HARNESS-CLI",
                    "author_session_context_id": session_id,
                    "author_model": "qualification",
                    "Project": "PROJECT-1",
                    "Work Item": "WI-1",
                }
                if receiver:
                    metadata["recipient_role"] = "loyal-opposition" if receiver == "lo" else "prime-builder"
                if status == "NEW":
                    metadata.update(
                        target_paths='["code.py"]',
                        test_artifact_targets='["tests/test_effect.py"]',
                        spec_ids='["SPEC-1"]',
                    )
                if status == "READY":
                    checked = cli(
                        "bridge", "check", "cli-chain", "--native-context-id", context, "--fence", str(fence), "--json"
                    )
                    assert checked.returncode == 0, checked.stderr
                    opened = cli(
                        "bridge",
                        "worktree",
                        "cli-chain",
                        "--native-context-id",
                        context,
                        "--fence",
                        str(fence),
                        "--json",
                    )
                    assert opened.returncode == 0, opened.stderr
                    checkout = json.loads(opened.stdout)
                    (Path(checkout["path"]) / "code.py").write_text("value = 2\n", encoding="utf-8")
                    preimages = tmp_path / "preimages.json"
                    preimages.write_text(json.dumps(checkout["artifact_preimages"]), encoding="utf-8")
                    published = cli(
                        "bridge",
                        "publish-work",
                        "cli-chain",
                        "--native-context-id",
                        context,
                        "--fence",
                        str(fence),
                        "--preimages-file",
                        str(preimages),
                        "--json",
                    )
                    assert published.returncode == 0, published.stderr
                    assert (tmp_path / "code.py").read_text() == "value = 1\n"
                if status == "VERIFIED":
                    opened = cli(
                        "bridge",
                        "worktree",
                        "cli-chain",
                        "--native-context-id",
                        context,
                        "--fence",
                        str(fence),
                        "--json",
                    )
                    assert opened.returncode == 0, opened.stderr
                    assert (Path(json.loads(opened.stdout)["path"]) / "code.py").read_text() == "value = 2\n"
                    snapshot = cli("bridge", "artifacts", "cli-chain", "--json")
                    assert snapshot.returncode == 0, snapshot.stderr
                    metadata["verified_artifacts"] = json.dumps(json.loads(snapshot.stdout))
                artifact = tmp_path / f"authored-{version}.md"
                artifact.write_bytes(
                    "\r\n".join(
                        [
                            *lines,
                            *(f"{key}: {value}" for key, value in metadata.items()),
                            "",
                            "Complete authored message.",
                        ]
                    ).encode("utf-8")
                )
                delivered = cli(
                    "bridge",
                    "deliver",
                    "cli-chain",
                    "--native-context-id",
                    context,
                    "--fence",
                    str(fence),
                    "--content-file",
                    str(artifact),
                    "--json",
                )
                assert delivered.returncode == 0, delivered.stderr
                if status == "VERIFIED":
                    assert json.loads(delivered.stdout)["project_ready_for_commit"] is True
            message = tmp_path / "project-commit.txt"
            message.write_text("Complete the CLI qualification project (WI-1)\n", encoding="utf-8")
            committed = cli(
                "projects",
                "commit",
                "PROJECT-1",
                "--native-context-id",
                context,
                "--expected-version",
                "1",
                "--message-file",
                str(message),
                "--json",
            )
            assert committed.returncode == 0, committed.stderr
            result = json.loads(committed.stdout)
            assert result["status"] == "confirmed"
            actual_head = subprocess.run(
                ["git", "-C", str(tmp_path), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
            ).stdout.strip()
            assert actual_head == result["commit_id"]
            assert (tmp_path / "code.py").read_text() == "value = 2\n"
            terminal = cli("projects", "show", "PROJECT-1", "--json")
            assert json.loads(terminal.stdout)["project"]["status"] == "verified"
            disabled = cli("db", "postgres", "status")
            assert disabled.returncode != 0 and "fallback is disabled" in disabled.stderr
        finally:
            process.terminate()
            process.wait(timeout=15)
    unavailable = cli("projects", "show", "PROJECT-1", "--json")
    assert unavailable.returncode != 0 and "authority_unavailable" in unavailable.stderr
    assert sentinel.read_bytes() == b"This is not a SQLite database; opening it is a test failure."
    assert service.show("specifications", "SPEC-1")["version"] == 2
