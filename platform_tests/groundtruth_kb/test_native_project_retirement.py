"""Ordinary program/project retirement (owner ruling D32): status-only, with history, relationships kept.

POST /v1/projects/{id}/retire changes ``status`` from ``active`` to ``retired`` at version+1 with one
history row; authorization, kind, parent, ``completed_at``, memberships (including closed members'
active parent rows), formal links, dependencies and child projects are untouched (GOV-STANDING-BACKLOG-001:
a current parent relationship survives retirement; GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001:
retiring a project never collectively rewrites members). The route refuses open members (open work items
of a project; active child projects of a program), the standing intake project, active bridge attempts and
active dependants. Shared fixtures come from the c102 layout, so this module imports only after the c104
draft is rebased onto the main candidate.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from groundtruth_kb.native_authority import ProjectRetirement
from groundtruth_kb.postgres_kernel import PostgresKernelError
from psycopg import sql

from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.bridge_fixtures import deliver
from platform_tests.groundtruth_kb.native_fixtures import history_count, project, put, seed, work_fields
from platform_tests.groundtruth_kb.native_fixtures import membership_cli as membership_cli
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]

REASON = "Compatibility project; no residual work"
WORK_REASON = "Obsolete scope; no residual work"
STAMPED = {"version", "status", "changed_at", "changed_by", "change_reason"}


def retire(client, record_id, *, version, actor="qualification", reason=REASON, **extra):
    """POST the status-only retirement; ``extra`` models a malformed body."""
    return client.post(
        f"/v1/projects/{record_id}/retire",
        json={"expected_version": version, "actor": actor, "reason": reason, **extra},
    )


def retire_work(client, record_id, *, version):
    return client.post(
        f"/v1/work-items/{record_id}/retire",
        json={"expected_version": version, "actor": "qualification", "reason": WORK_REASON},
    )


def error(response):
    body = response.json()
    if body.get("code") == "invalid_request":
        assert set(body) == {"code", "message", "fields"}
        assert body["message"] == "Request does not match the domain contract"
        assert isinstance(body["fields"], list) and body["fields"]
        assert all(set(field) == {"location", "type"} for field in body["fields"])
        return body
    assert set(body) == {"error"}
    result = body["error"]
    assert set(result) in ({"code", "message"}, {"code", "message", "details"})
    assert isinstance(result["code"], str) and isinstance(result["message"], str)
    if "details" in result:
        assert isinstance(result["details"], dict) and result["details"]
    return result


def assert_cli_json(result, expected=None):
    assert result.returncode == 0 and result.stderr == "", result.stderr
    parsed = json.loads(result.stdout)
    assert isinstance(parsed, dict)
    if expected is not None:
        assert parsed == expected
    assert result.stdout == json.dumps(parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    assert result.stdout.count("\n") == 1
    return parsed


def assert_cli_error(result, code, message, details=None):
    assert result.returncode == 1 and result.stdout == "", result.stdout + result.stderr
    expected = f"Error: {code}: {message}\n"
    if details is not None:
        expected += json.dumps(details, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    assert result.stderr == expected


def assert_cli_unavailable(result, path):
    assert result.returncode == 1 and result.stdout == "", result.stdout + result.stderr
    lines = result.stderr.splitlines()
    assert len(lines) == 2
    details = json.loads(lines[1])
    assert set(details) == {"cause", "cause_message", "elapsed_seconds", "timeout_seconds", "method", "path"}
    assert isinstance(details["cause"], str) and details["cause"]
    assert isinstance(details["cause_message"], str)
    assert isinstance(details["elapsed_seconds"], (int, float)) and details["elapsed_seconds"] >= 0
    assert details["timeout_seconds"] == 40 and details["method"] == "POST" and details["path"] == path
    assert_cli_error(
        result,
        "authority_unavailable",
        "The configured authority is unavailable. Restore the service and read current state before retrying.",
        details,
    )


def unchanged(record):
    return {key: value for key, value in record.items() if key not in STAMPED}


def state(client, service, *project_ids):
    """Project reads (row, children, memberships, dependencies, links) and the history count."""
    return [client.get(f"/v1/projects/{record_id}").json() for record_id in project_ids], history_count(service)


def attempt_row(service, document):
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(
            sql.SQL("SELECT * FROM {}.bridge_attempts WHERE id=%s").format(sql.Identifier(tx.schema)), (document,)
        )
        return dict(tx.cursor.fetchone())


def plant(service, client, record_id, **updates):
    """Model legacy imported work state in the disposable database, never through intake."""
    current = client.get(f"/v1/work-items/{record_id}").json()["work_item"]
    service.kernel.mutate_current(
        table="work_items",
        identity={"id": record_id},
        expected_version=current["version"],
        new_state={**current, **updates},
        actor="qualification",
        reason="Imported-state fixture",
    )
    return client.get(f"/v1/work-items/{record_id}").json()


def close_project(service, record_id, status):
    with service.kernel.transaction() as tx:
        current = tx.get("projects", {"id": record_id})
        tx.mutate(
            table="projects",
            identity={"id": record_id},
            expected_version=current["version"],
            new_state={**current, "status": status},
            actor="qualification",
            reason="Closed state fixture",
        )


def add_dependency(client, record_id, *, dependent, prerequisite="PROJECT-1", state="verified", gate="readiness"):
    created = put(
        client,
        "project-dependencies",
        record_id,
        {
            "dependent_project_id": dependent,
            "prerequisite_project_id": prerequisite,
            "required_prerequisite_state": state,
            "affected_gate": gate,
            "rationale": "The downstream artifacts require the predecessor result",
        },
    )
    assert created.status_code == 200, created.text
    return created.json()


def test_project_retirement_is_status_only_and_refuses_open_members_first(native):
    service, client, _, _ = native
    seed(client)
    link = put(client, "project-formal-links", "LINK-1", {"project_id": "PROJECT-1", "artifact_ref": "SPEC-1"})
    assert link.status_code == 200, link.text
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    before = state(client, service, "PROGRAM-1", "PROJECT-1")
    # Open members refuse first: the program holds an active child, the project an open item.
    program = retire(client, "PROGRAM-1", version=1)
    assert program.status_code == 422 and error(program)["code"] == "members_open", program.text
    assert error(program)["details"] == {"id": "PROGRAM-1", "work_item_ids": [], "project_ids": ["PROJECT-1"]}
    blocked = retire(client, "PROJECT-1", version=1)
    assert blocked.status_code == 422 and error(blocked)["code"] == "members_open", blocked.text
    assert error(blocked)["details"] == {"id": "PROJECT-1", "work_item_ids": ["WI-1"], "project_ids": []}
    assert state(client, service, "PROGRAM-1", "PROJECT-1") == before
    # Close the member through its own route; its active membership stays (the preserved parent).
    assert retire_work(client, "WI-1", version=1).status_code == 200
    shown = client.get("/v1/projects/PROJECT-1").json()
    work = client.get("/v1/work-items/WI-1").json()
    history = history_count(service)
    assert [row["work_item_id"] for row in shown["memberships"]] == ["WI-1"]
    assert [row["id"] for row in shown["artifact_links"]] == ["LINK-1"]
    result = retire(client, "PROJECT-1", version=shown["project"]["version"])
    assert result.status_code == 200, result.text
    row = result.json()
    assert row["status"] == "retired" and row["version"] == shown["project"]["version"] + 1
    assert row["changed_by"] == "qualification" and row["change_reason"] == REASON
    assert unchanged(row) == unchanged(shown["project"])
    assert (row["kind"], row["authorization"], row["parent_project_id"]) == ("project", "authorized", "PROGRAM-1")
    assert row["completed_at"] is None
    # Memberships, links, dependencies and children are exactly as before; only the row changed.
    assert client.get("/v1/projects/PROJECT-1").json() == {**shown, "project": row}
    assert client.get("/v1/work-items/WI-1").json() == work
    assert client.get("/v1/project-formal-links/LINK-1").json() == link.json()
    versions = client.get("/v1/projects/PROJECT-1/history").json()
    assert versions["current"] == row
    last = versions["history"][-1]
    assert (last["version"], last["prior_version"], last["reason"]) == (row["version"], row["version"] - 1, REASON)
    assert last["state"]["status"] == "retired"
    assert history_count(service) == history + 1
    # Re-retiring is a refusal, never a silent no-op.
    again = retire(client, "PROJECT-1", version=row["version"])
    assert again.status_code == 422 and error(again)["code"] == "project_closed", again.text
    assert error(again)["details"] == {"id": "PROJECT-1", "status": "retired"}
    assert client.get("/v1/projects/PROJECT-1").json() == {**shown, "project": row}
    assert history_count(service) == history + 1
    # The program retires once its only child is closed; the child keeps its parent_project_id.
    program_before = client.get("/v1/projects/PROGRAM-1").json()
    closed = retire(client, "PROGRAM-1", version=1)
    assert closed.status_code == 200, closed.text
    assert (closed.json()["kind"], closed.json()["authorization"], closed.json()["status"]) == (
        "program",
        None,
        "retired",
    )
    assert unchanged(closed.json()) == unchanged(program_before["project"])
    assert client.get("/v1/projects/PROGRAM-1").json() == {**program_before, "project": closed.json()}
    assert [child["id"] for child in program_before["projects"]] == ["PROJECT-1"]
    assert history_count(service) == history + 2
    listed = client.get("/v1/projects", params={"status": "retired"}).json()["records"]
    assert [item["id"] for item in listed] == ["PROGRAM-1", "PROJECT-1"]


def test_project_retirement_refusals_leave_row_and_history_unchanged(native):
    service, client, _, _ = native
    seed(client)
    before = state(client, service, "PROJECT-1", "PROJECT-GTKB-NEW-WORK-INTAKE")

    def refused(response, status, code):
        assert response.status_code == status and error(response)["code"] == code, response.text
        assert state(client, service, "PROJECT-1", "PROJECT-GTKB-NEW-WORK-INTAKE") == before
        return error(response)

    refused(retire(client, "PROJECT-MISSING", version=1), 404, "not_found")
    conflict = refused(retire(client, "PROJECT-1", version=5), 409, "cas_conflict")
    assert conflict["details"] == {"id": "PROJECT-1", "expected": 5, "actual": 1}
    extra = refused(retire(client, "PROJECT-1", version=1, status="retired"), 422, "invalid_request")
    assert extra["fields"] == [{"location": ["body", "status"], "type": "extra_forbidden"}]
    missing = client.post("/v1/projects/PROJECT-1/retire", json={"expected_version": 1, "actor": "qualification"})
    assert refused(missing, 422, "invalid_request")["fields"] == [{"location": ["body", "reason"], "type": "missing"}]
    coerced = client.post(
        "/v1/projects/PROJECT-1/retire", json={"expected_version": "1", "actor": "qualification", "reason": REASON}
    )
    assert refused(coerced, 422, "invalid_request")["fields"] == [
        {"location": ["body", "expected_version"], "type": "int_type"}
    ]
    for field in ("actor", "reason"):
        empty = client.post(
            "/v1/projects/PROJECT-1/retire",
            json={"expected_version": 1, "actor": "qualification", "reason": REASON, field: ""},
        )
        assert refused(empty, 422, "invalid_request")["fields"] == [
            {"location": ["body", field], "type": "string_too_short"}
        ]
    # The standing intake destination is never retirable (GOV-STANDING-BACKLOG-001).
    refused(retire(client, "PROJECT-GTKB-NEW-WORK-INTAKE", version=1), 422, "project_structure_frozen")
    # A closed member's active membership is preserved history and does not block.
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    planted = plant(service, client, "WI-1", resolution_status="wont_fix")
    assert planted["membership"]["status"] == "active"
    result = retire(client, "PROJECT-1", version=1)
    assert result.status_code == 200, result.text
    assert client.get("/v1/work-items/WI-1").json() == planted
    assert client.get("/v1/projects/PROJECT-1").json()["memberships"] == [planted["membership"]]


@pytest.mark.parametrize("status", ["verified", "retired", "cancelled"])
def test_project_retirement_refuses_an_already_closed_project(native, status):
    service, client, _, _ = native
    seed(client)
    close_project(service, "PROJECT-1", status)
    before = state(client, service, "PROJECT-1")
    result = retire(client, "PROJECT-1", version=before[0][0]["project"]["version"])
    assert result.status_code == 422 and error(result)["code"] == "project_closed", result.text
    assert error(result)["details"] == {"id": "PROJECT-1", "status": status}
    assert state(client, service, "PROJECT-1") == before


def test_project_retirement_refuses_active_dependants_until_they_are_retired_or_closed(native):
    service, client, _, _ = native
    seed(client)
    project(client, "PROJECT-2")
    project(client, "PROJECT-3")
    add_dependency(client, "DEP-1", dependent="PROJECT-2")
    # A dependency that only needs the prerequisite retired is satisfied by the retirement and never blocks.
    add_dependency(client, "DEP-2", dependent="PROJECT-2", state="retired", gate="closure")
    add_dependency(client, "DEP-3", dependent="PROJECT-3")
    before = state(client, service, "PROJECT-1", "PROJECT-2", "PROJECT-3")
    result = retire(client, "PROJECT-1", version=1)
    assert result.status_code == 422 and error(result)["code"] == "dependants_open", result.text
    assert error(result)["details"] == {
        "id": "PROJECT-1",
        "dependency_ids": ["DEP-1", "DEP-3"],
        "dependent_project_ids": ["PROJECT-2", "PROJECT-3"],
    }
    assert state(client, service, "PROJECT-1", "PROJECT-2", "PROJECT-3") == before
    # A retired dependency no longer blocks.
    assert put(client, "project-dependencies", "DEP-1", {"status": "retired"}, expected_version=1).status_code == 200
    result = retire(client, "PROJECT-1", version=1)
    assert result.status_code == 422 and error(result)["code"] == "dependants_open", result.text
    assert error(result)["details"] == {
        "id": "PROJECT-1",
        "dependency_ids": ["DEP-3"],
        "dependent_project_ids": ["PROJECT-3"],
    }
    # A closed dependent project no longer blocks either; nothing but the prerequisite's row changes.
    close_project(service, "PROJECT-3", "cancelled")
    dependencies = {key: client.get(f"/v1/project-dependencies/{key}").json() for key in ("DEP-1", "DEP-2", "DEP-3")}
    others = state(client, service, "PROJECT-2", "PROJECT-3")
    result = retire(client, "PROJECT-1", version=1)
    assert result.status_code == 200, result.text
    assert result.json()["status"] == "retired" and result.json()["version"] == 2
    assert {key: client.get(f"/v1/project-dependencies/{key}").json() for key in dependencies} == dependencies
    assert state(client, service, "PROJECT-2", "PROJECT-3") == (others[0], others[1] + 1)


def test_project_retirement_refuses_an_active_attempt_held_for_the_project_commit(bridge):
    service, client, contexts, _ = bridge
    deliver(client, contexts, "cohort", "pb1", 1, "NEW")
    version = client.get("/v1/projects/PROJECT-1").json()["project"]["version"]
    # The open member refuses first; a VERIFIED-but-uncommitted member keeps its attempt active until the commit.
    open_member = retire(client, "PROJECT-1", version=version)
    assert open_member.status_code == 422 and error(open_member)["code"] == "members_open", open_member.text
    plant(service, client, "WI-1", resolution_status="verified")
    attempt = attempt_row(service, "cohort")
    assert attempt["disposition"] == "active" and attempt["project_id"] == "PROJECT-1"
    before = state(client, service, "PROJECT-1")
    result = retire(client, "PROJECT-1", version=version)
    assert result.status_code == 422 and error(result)["code"] == "attempt_active", result.text
    assert error(result)["details"] == {"id": "PROJECT-1", "attempt_ids": ["cohort"]}
    assert state(client, service, "PROJECT-1") == before
    assert attempt_row(service, "cohort") == attempt


def test_concurrent_project_retirement_records_one_transition(native):
    service, client, _, _ = native
    seed(client)
    project(client, "PROJECT-2")
    barrier = Barrier(2)
    history = history_count(service)

    def attempt(_):
        barrier.wait(timeout=10)
        try:
            return service.retire_project(
                "PROJECT-2", ProjectRetirement(expected_version=1, actor="qualification", reason=REASON)
            )
        except PostgresKernelError as failure:
            return failure.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(attempt, range(2)))
    assert sum(isinstance(result, dict) for result in outcomes) == 1, outcomes
    assert next(result for result in outcomes if isinstance(result, str)) in {"cas_conflict", "retryable_conflict"}
    assert history_count(service) == history + 1
    row = client.get("/v1/projects/PROJECT-2").json()["project"]
    assert row["version"] == 2 and row["status"] == "retired"


def test_real_cli_projects_retire_reads_back_and_refuses_when_authority_is_unavailable(membership_cli):
    service, client, cli, stop = membership_cli
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200

    def command(record_id, version, *extra, reason=REASON):
        return cli(
            "projects",
            "retire",
            "--id",
            record_id,
            "--reason",
            reason,
            "--expected-version",
            str(version),
            "--actor",
            "qualification",
            *extra,
        )

    before = state(client, service, "PROJECT-1")
    # Usage errors exit 2 before any request: every option is required and the version is at least 1.
    for arguments in (
        ("--reason", REASON, "--expected-version", "1", "--actor", "qualification"),
        ("--id", "PROJECT-1", "--expected-version", "1", "--actor", "qualification"),
        ("--id", "PROJECT-1", "--reason", REASON, "--actor", "qualification"),
        ("--id", "PROJECT-1", "--reason", REASON, "--expected-version", "1"),
        ("--id", "PROJECT-1", "--reason", REASON, "--expected-version", "0", "--actor", "qualification"),
    ):
        usage = cli("projects", "retire", *arguments)
        assert usage.returncode == 2 and usage.stdout == "", arguments
        assert usage.stderr.startswith("Usage:") and "\nError: " in usage.stderr
    invalid = command("PROJECT-1", 1, "--json", reason="")
    # Validation is a top-level API fields schema; the current client emits its code/message, without details.
    assert_cli_error(invalid, "invalid_request", "Request does not match the domain contract")
    stale = command("PROJECT-1", 9, "--json")
    assert_cli_error(
        stale,
        "cas_conflict",
        "Read the current project before retiring it",
        {"id": "PROJECT-1", "expected": 9, "actual": 1},
    )
    members = command("PROJECT-1", 1, "--json")
    assert_cli_error(
        members,
        "members_open",
        "Retire or re-home the open members first; retirement never closes them collectively",
        {"id": "PROJECT-1", "work_item_ids": ["WI-1"], "project_ids": []},
    )
    assert state(client, service, "PROJECT-1") == before
    # Retire the open member through its own verb, then the project; readback through gt projects show.
    member = cli(
        "backlog",
        "retire",
        "--id",
        "WI-1",
        "--reason",
        WORK_REASON,
        "--expected-version",
        "1",
        "--actor",
        "qualification",
        "--json",
    )
    assert_cli_json(member)
    shown_before = client.get("/v1/projects/PROJECT-1").json()
    result = command("PROJECT-1", shown_before["project"]["version"], "--json")
    row = assert_cli_json(result)
    assert row["status"] == "retired" and row["version"] == shown_before["project"]["version"] + 1
    shown = cli("projects", "show", "PROJECT-1", "--json")
    assert_cli_json(shown, {**shown_before, "project": row})
    versions = cli("projects", "show", "PROJECT-1", "--history")
    assert versions.returncode == 0 and f"v{row['version']}" in versions.stdout and REASON in versions.stdout
    text = command("PROGRAM-1", 1)
    assert text.returncode == 0 and text.stderr == "", text.stderr
    assert "PROGRAM-1 v2: Coherent platform" in text.stdout and 'status: "retired"' in text.stdout
    assert client.get("/v1/projects/PROGRAM-1").json()["project"]["status"] == "retired"
    rows = state(client, service, "PROGRAM-1", "PROJECT-1", "PROJECT-GTKB-NEW-WORK-INTAKE")
    stop()
    unavailable = command("PROJECT-GTKB-NEW-WORK-INTAKE", 1, "--json")
    assert_cli_unavailable(unavailable, "/v1/projects/PROJECT-GTKB-NEW-WORK-INTAKE/retire")
    assert state(client, service, "PROGRAM-1", "PROJECT-1", "PROJECT-GTKB-NEW-WORK-INTAKE") == rows
