"""Replace optional-label diagnostics with native membership and atomic refusal."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import groundtruth_kb
import pytest
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.native_authority import MembershipMove
from groundtruth_kb.postgres_kernel import TABLE_SPECS, PostgresKernelError, PostgresTransaction

from platform_tests.groundtruth_kb.test_native_authority_service import (
    history_count,
    put,
    seed,
    work_fields,
)
from platform_tests.groundtruth_kb.test_native_authority_service import (
    native as native,
)

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


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


def creation(cli, path, *, project=None, **fields):
    path.write_text(json.dumps(work_fields(**fields)), encoding="utf-8")
    args = [
        "backlog",
        "record",
        "--id",
        "WI-NATIVE-MEMBERSHIP",
        "--fields-file",
        str(path),
        "--expected-version",
        "0",
        "--actor",
        "qualification",
        "--change-reason",
        "Exact membership test",
        "--json",
    ]
    if project is not None:
        args.extend(["--project-id", project])
    return cli(*args)


@pytest.mark.parametrize(
    "project, fields, expected_error",
    [
        (None, {}, "project_required"),
        (None, {"project_name": "PROJECT-1"}, "invalid_request"),
        (None, {"project_name": "PROJECT-UNKNOWN"}, "invalid_request"),
        ("PROJECT-UNKNOWN", {}, "not_found"),
        ("PROGRAM-1", {}, "program_cannot_contain_work"),
        ("PROJECT-1", {"project_name": "PROJECT-UNKNOWN"}, "invalid_request"),
        ("PROJECT-1", {}, None),
    ],
)
def test_cli_creation_requires_exact_membership_and_reports_canonical_result(
    membership_cli, tmp_path, project, fields, expected_error
):
    service, client, cli, _ = membership_cli
    before = history_count(service)
    result = creation(cli, tmp_path / "fields.json", project=project, **fields)
    after = client.get("/v1/work-items/WI-NATIVE-MEMBERSHIP")
    if expected_error:
        assert result.returncode != 0, result.stdout
        assert expected_error in result.stdout + result.stderr
        assert after.status_code == 404
        assert history_count(service) == before
        with service.kernel.transaction(read_only=True) as tx:
            assert not tx.list("project_work_item_memberships", filters={"work_item_id": "WI-NATIVE-MEMBERSHIP"})
    else:
        assert result.returncode == 0, result.stderr
        readback = json.loads(result.stdout)
        assert after.status_code == 200 and after.json() == readback
        assert readback["membership"]["project_id"] == "PROJECT-1"
        assert readback["membership"]["work_item_id"] == readback["work_item"]["id"] == "WI-NATIVE-MEMBERSHIP"
        assert readback["membership"]["status"] == "active"
        assert history_count(service) == before + 2
        with service.kernel.transaction(read_only=True) as tx:
            assert (
                len(
                    tx.list(
                        "project_work_item_memberships",
                        filters={"work_item_id": "WI-NATIVE-MEMBERSHIP", "status": "active"},
                    )
                )
                == 1
            )


def test_membership_write_failure_rolls_back_created_work_and_history(native, monkeypatch):
    service, client, _, _ = native
    seed(client)
    before = history_count(service)
    original = PostgresTransaction.mutate
    interrupted = []

    def fail_membership(tx, **request):
        if request["table"] == "project_work_item_memberships":
            # Prove work and history were already written inside this transaction.
            assert tx.get("work_items", {"id": "WI-ATOMIC"}) is not None
            tx.cursor.execute("SELECT count(*) AS n FROM record_history")
            assert tx.cursor.fetchone()["n"] == before + 1
            interrupted.append(True)
            raise PostgresKernelError("fixture_membership_failure", "Qualification fault after work creation")
        return original(tx, **request)

    monkeypatch.setattr(PostgresTransaction, "mutate", fail_membership)
    result = put(client, "work-items", "WI-ATOMIC", work_fields(), project_id="PROJECT-1")
    assert result.status_code == 422 and result.json()["error"]["code"] == "fixture_membership_failure"
    assert interrupted == [True]
    assert history_count(service) == before
    assert client.get("/v1/work-items/WI-ATOMIC").status_code == 404
    with service.kernel.transaction(read_only=True) as tx:
        assert not tx.list("project_work_item_memberships", filters={"work_item_id": "WI-ATOMIC"})


def test_unavailable_authority_never_reports_membership_creation_success(membership_cli, tmp_path):
    service, client, cli, stop = membership_cli
    before = history_count(service)
    stop()
    result = creation(cli, tmp_path / "fields.json", project="PROJECT-1")
    assert result.returncode != 0
    assert "authority_unavailable" in result.stdout + result.stderr
    assert client.get("/v1/work-items/WI-NATIVE-MEMBERSHIP").status_code == 404
    assert history_count(service) == before


def _stamp():
    return datetime.now(UTC).isoformat()


def _record_membership(service, work_item_id, project_id, status, index):
    """Write one membership row directly, the shape the migration preserves as closed history."""
    row = {column: None for column in TABLE_SPECS["project_work_item_memberships"].columns}
    row.update(
        id=f"PWM-HIST-{work_item_id}-{index}",
        version=1,
        project_id=project_id,
        work_item_id=work_item_id,
        status=status,
        source="migration",
        changed_by="qualification",
        changed_at=_stamp(),
        change_reason="Preserved membership history fixture",
    )
    service.kernel.mutate_current(
        table="project_work_item_memberships",
        identity={"id": row["id"]},
        expected_version=0,
        new_state=row,
        actor="qualification",
        reason="Preserved membership history fixture",
    )


def _close_work_item(service, work_item_id):
    with service.kernel.transaction(read_only=True) as tx:
        work = tx.get("work_items", {"id": work_item_id})
    service.kernel.mutate_current(
        table="work_items",
        identity={"id": work_item_id},
        expected_version=work["version"],
        new_state={
            **work,
            "version": work["version"] + 1,
            "resolution_status": "closed",
            "changed_by": "qualification",
            "changed_at": _stamp(),
            "change_reason": "Closed history fixture",
        },
        actor="qualification",
        reason="Closed history fixture",
    )


def _retire_memberships(service, work_item_id):
    with service.kernel.transaction(read_only=True) as tx:
        rows = tx.list("project_work_item_memberships", filters={"work_item_id": work_item_id, "status": "active"})
    for row in rows:
        service.kernel.mutate_current(
            table="project_work_item_memberships",
            identity={"id": row["id"]},
            expected_version=row["version"],
            new_state={
                **row,
                "version": row["version"] + 1,
                "status": "removed",
                "changed_by": "qualification",
                "changed_at": _stamp(),
                "change_reason": "Closed history fixture",
            },
            actor="qualification",
            reason="Closed history fixture",
        )


def _project(client, project_id):
    result = put(
        client,
        "projects",
        project_id,
        {"name": project_id, "parent_project_id": "PROGRAM-1", "target_outcome": "Alternative complete outcome"},
    )
    assert result.status_code == 200, result.text


def test_closed_work_with_no_active_membership_reads_as_recorded(native):
    service, client, _, _ = native
    seed(client)
    assert put(client, "work-items", "WI-CLOSED-NONE", work_fields(), project_id="PROJECT-1").status_code == 200
    _close_work_item(service, "WI-CLOSED-NONE")
    _retire_memberships(service, "WI-CLOSED-NONE")
    result = client.get("/v1/work-items/WI-CLOSED-NONE")
    assert result.status_code == 200, result.text
    body = result.json()
    assert body["work_item"]["resolution_status"] == "closed"
    assert body["membership"] is None
    assert [row["status"] for row in body["memberships"]] == ["removed"]
    with pytest.raises(PostgresKernelError) as refused:
        service.task_context("WI-CLOSED-NONE")
    assert refused.value.code == "invalid_membership"


def test_closed_work_with_several_active_memberships_reads_all_without_inventing_a_parent(native):
    service, client, _, _ = native
    seed(client)
    _project(client, "PROJECT-2")
    assert put(client, "work-items", "WI-CLOSED-TWO", work_fields(), project_id="PROJECT-1").status_code == 200
    _close_work_item(service, "WI-CLOSED-TWO")
    # Memberships are keyed by (project, work item): the service-created PROJECT-1 row stays active and a
    # second active row for PROJECT-2 is recorded, the shape the migration preserves for closed history.
    _record_membership(service, "WI-CLOSED-TWO", "PROJECT-2", "active", 2)
    body = client.get("/v1/work-items/WI-CLOSED-TWO").json()
    assert body["membership"] is None
    assert sorted(row["project_id"] for row in body["memberships"] if row["status"] == "active") == [
        "PROJECT-1",
        "PROJECT-2",
    ]
    assert sorted(row["status"] for row in body["memberships"]) == ["active", "active"]
    with pytest.raises(PostgresKernelError) as context_refused:
        service.task_context("WI-CLOSED-TWO")
    assert context_refused.value.code == "invalid_membership"
    with pytest.raises(PostgresKernelError) as move_refused:
        service.move_work_item(
            "WI-CLOSED-TWO",
            MembershipMove(
                expected_version=1,
                actor="worker",
                reason="Closed history must not move",
                source_project_id="PROJECT-1",
                destination_project_id="PROJECT-2",
            ),
        )
    assert move_refused.value.code == "work_item_frozen"


def test_open_work_with_irregular_membership_is_still_refused_on_read(native):
    service, client, _, _ = native
    seed(client)
    _project(client, "PROJECT-2")
    assert put(client, "work-items", "WI-OPEN-IRREGULAR", work_fields(), project_id="PROJECT-1").status_code == 200
    _record_membership(service, "WI-OPEN-IRREGULAR", "PROJECT-2", "active", 1)
    result = client.get("/v1/work-items/WI-OPEN-IRREGULAR")
    assert result.status_code == 422, result.text
    assert result.json()["error"]["code"] == "invalid_membership"


def test_concurrent_moves_of_one_open_item_leave_exactly_one_active_membership(native):
    service, client, _, _ = native
    seed(client)
    _project(client, "PROJECT-2")
    _project(client, "PROJECT-3")
    assert put(client, "work-items", "WI-MOVE", work_fields(), project_id="PROJECT-1").status_code == 200
    current = client.get("/v1/work-items/WI-MOVE").json()["membership"]

    def move(destination):
        try:
            return service.move_work_item(
                "WI-MOVE",
                MembershipMove(
                    expected_version=current["version"],
                    actor="worker",
                    reason="Concurrent move",
                    source_project_id="PROJECT-1",
                    destination_project_id=destination,
                ),
            )
        except PostgresKernelError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as workers:
        outcomes = list(workers.map(move, ["PROJECT-2", "PROJECT-3"]))
    assert sum(isinstance(value, dict) for value in outcomes) == 1, outcomes
    assert any(value in ("cas_conflict", "retryable_conflict") for value in outcomes if isinstance(value, str)), (
        outcomes
    )
    with service.kernel.transaction(read_only=True) as tx:
        active = tx.list("project_work_item_memberships", filters={"work_item_id": "WI-MOVE", "status": "active"})
    assert len(active) == 1 and active[0]["project_id"] in {"PROJECT-2", "PROJECT-3"}
    assert client.get("/v1/work-items/WI-MOVE").json()["membership"]["id"] == active[0]["id"]


def test_interrupted_move_rolls_back_to_the_original_membership(native, monkeypatch):
    service, client, _, _ = native
    seed(client)
    _project(client, "PROJECT-2")
    assert put(client, "work-items", "WI-INTERRUPTED", work_fields(), project_id="PROJECT-1").status_code == 200
    original = client.get("/v1/work-items/WI-INTERRUPTED").json()["membership"]
    before = history_count(service)
    original_mutate = PostgresTransaction.mutate
    membership_writes = []

    def fail_between_removal_and_insertion(tx, **request):
        if request["table"] == "project_work_item_memberships":
            membership_writes.append(request["new_state"]["status"])
            if len(membership_writes) == 2:
                # The removal is already written inside this transaction; the destination write fails.
                raise PostgresKernelError("fixture_move_failure", "Qualification fault between removal and insertion")
        return original_mutate(tx, **request)

    monkeypatch.setattr(PostgresTransaction, "mutate", fail_between_removal_and_insertion)
    with pytest.raises(PostgresKernelError) as refused:
        service.move_work_item(
            "WI-INTERRUPTED",
            MembershipMove(
                expected_version=original["version"],
                actor="worker",
                reason="Interrupted move",
                source_project_id="PROJECT-1",
                destination_project_id="PROJECT-2",
            ),
        )
    assert refused.value.code == "fixture_move_failure"
    assert membership_writes == ["removed", "active"]
    monkeypatch.setattr(PostgresTransaction, "mutate", original_mutate)
    assert client.get("/v1/work-items/WI-INTERRUPTED").json()["membership"] == original
    assert history_count(service) == before
    with service.kernel.transaction(read_only=True) as tx:
        rows = tx.list("project_work_item_memberships", filters={"work_item_id": "WI-INTERRUPTED"})
    assert [row["status"] for row in rows] == ["active"] and rows[0]["version"] == original["version"]
