"""Ordinary work-item retirement (owner ruling D32): status-only, with history, parent preserved.

POST /v1/work-items/{id}/retire changes ``resolution_status`` from ``open`` to ``retired`` at version+1
with one history row and nothing else (GOV-WORK-ITEM-TERMINAL-STATE-001: the active membership describes
the current parent, including for closed work; siblings are never retired collectively). The route
refuses already-terminal items, open dependants (open items whose ``depends_on_work_items`` names the id;
``blocks_work_items`` is legacy data and not consulted) and an active bridge attempt. Shared fixtures
come from the c102 layout (``native_fixtures``/``bridge_fixtures``), so this module imports only after
the c104 draft is rebased onto the main candidate.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from threading import Barrier

import pytest
from groundtruth_kb.native_authority import WorkItemRetirement
from groundtruth_kb.postgres_kernel import TABLE_SPECS, PostgresKernelError
from psycopg import sql

from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.bridge_fixtures import deliver
from platform_tests.groundtruth_kb.native_fixtures import history_count, put, seed, work_fields
from platform_tests.groundtruth_kb.native_fixtures import membership_cli as membership_cli
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]

REASON = "Obsolete scope; surviving work WI-2"
# The columns a retirement stamps; every other column reads back unchanged.
STAMPED = {"version", "resolution_status", "changed_at", "changed_by", "change_reason"}


def retire(client, record_id, *, version, actor="qualification", reason=REASON, **extra):
    """POST the status-only retirement; ``extra`` models a malformed body."""
    return client.post(
        f"/v1/work-items/{record_id}/retire",
        json={"expected_version": version, "actor": actor, "reason": reason, **extra},
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


def unchanged(record, *more):
    return {key: value for key, value in record.items() if key not in STAMPED | set(more)}


def state(client, service, *work_item_ids):
    """Rows with memberships, the parent project and the history count, for unchanged-after-refusal checks."""
    return (
        [client.get(f"/v1/work-items/{record_id}").json() for record_id in work_item_ids],
        client.get("/v1/projects/PROJECT-1").json(),
        history_count(service),
    )


def kernel_row(service, table, record_id):
    with service.kernel.transaction(read_only=True) as tx:
        return tx.get(table, {"id": record_id})


def attempt_row(service, document):
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(
            sql.SQL("SELECT * FROM {}.bridge_attempts WHERE id=%s").format(sql.Identifier(tx.schema)), (document,)
        )
        return dict(tx.cursor.fetchone())


def intake(client, *record_ids, **fields):
    for record_id in record_ids:
        created = put(client, "work-items", record_id, work_fields(**fields), project_id="PROJECT-1")
        assert created.status_code == 200, created.text


def plant(service, client, record_id, **updates):
    """Model legacy imported state in the disposable database, never through intake."""
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


def plant_membership(service, membership, **updates):
    """Rewrite one membership row (or add one at expected_version 0) as imported irregular history."""
    row = {column: None for column in TABLE_SPECS["project_work_item_memberships"].columns}
    row.update(membership)
    row.update(updates)
    row.update(changed_at=datetime.now(UTC).isoformat(), changed_by="migration-fixture", change_reason="Imported")
    version = membership.get("version", 0) if membership.get("id") == row["id"] else 0
    row["version"] = version + 1
    service.kernel.mutate_current(
        table="project_work_item_memberships",
        identity={"id": row["id"]},
        expected_version=version,
        new_state=row,
        actor="qualification",
        reason="Imported membership fixture",
    )


def close_project(service, record_id, status):
    with service.kernel.transaction() as tx:
        project = tx.get("projects", {"id": record_id})
        tx.mutate(
            table="projects",
            identity={"id": record_id},
            expected_version=project["version"],
            new_state={**project, "status": status},
            actor="qualification",
            reason="Closed state fixture",
        )


def test_work_item_retirement_is_status_only_with_history_and_preserved_parent(native):
    service, client, _, _ = native
    seed(client)
    intake(client, "WI-1", "WI-2")
    before = client.get("/v1/work-items/WI-1").json()
    sibling = client.get("/v1/work-items/WI-2").json()
    project = client.get("/v1/projects/PROJECT-1").content
    history = history_count(service)
    result = retire(client, "WI-1", version=1)
    assert result.status_code == 200, result.text
    row = result.json()["work_item"]
    assert row["resolution_status"] == "retired" and row["version"] == 2
    assert row["changed_by"] == "qualification" and row["change_reason"] == REASON
    # Exactly one field changes: stage, evidence links, predecessors, notes and identity are untouched.
    assert unchanged(row) == unchanged(before["work_item"])
    assert row["stage"] == before["work_item"]["stage"] == "created"
    assert result.json()["membership"] == before["membership"]
    assert result.json()["memberships"] == before["memberships"]
    assert client.get("/v1/work-items/WI-1").json() == result.json()
    versions = client.get("/v1/work-items/WI-1/history").json()
    assert versions["current"] == row and len(versions["history"]) == 2
    last = versions["history"][-1]
    assert (last["version"], last["prior_version"], last["actor"], last["reason"]) == (2, 1, "qualification", REASON)
    assert last["state"]["resolution_status"] == "retired"
    assert history_count(service) == history + 1
    # Never collective: the sibling and the parent project are byte-identical.
    assert client.get("/v1/projects/PROJECT-1").content == project
    assert client.get("/v1/work-items/WI-2").json() == sibling
    retired = client.get("/v1/work-items", params={"resolution_status": "retired"}).json()["records"]
    assert [item["id"] for item in retired] == ["WI-1"]
    open_items = client.get("/v1/work-items", params={"resolution_status": "open"}).json()["records"]
    assert [item["id"] for item in open_items] == ["WI-2"]


def test_work_item_retirement_refusals_leave_row_and_history_unchanged(native):
    service, client, _, _ = native
    seed(client)
    intake(client, "WI-1")
    intake(client, "WI-2", "WI-3", depends_on_work_items=["WI-1"])
    # A dependant that is already terminal never blocks; only open dependants count.
    plant(service, client, "WI-3", resolution_status="verified")
    before = state(client, service, "WI-1", "WI-2", "WI-3")

    def refused(response, status, code):
        assert response.status_code == status and error(response)["code"] == code, response.text
        assert state(client, service, "WI-1", "WI-2", "WI-3") == before
        return error(response)

    refused(retire(client, "WI-MISSING", version=1), 404, "not_found")
    conflict = refused(retire(client, "WI-1", version=7), 409, "cas_conflict")
    assert conflict["details"] == {"id": "WI-1", "expected": 7, "actual": 1}
    extra = refused(retire(client, "WI-1", version=1, resolution_status="retired"), 422, "invalid_request")
    assert extra["fields"] == [{"location": ["body", "resolution_status"], "type": "extra_forbidden"}]
    missing = client.post("/v1/work-items/WI-1/retire", json={"expected_version": 1, "actor": "qualification"})
    assert refused(missing, 422, "invalid_request")["fields"] == [{"location": ["body", "reason"], "type": "missing"}]
    coerced = client.post(
        "/v1/work-items/WI-1/retire", json={"expected_version": "1", "actor": "qualification", "reason": REASON}
    )
    assert refused(coerced, 422, "invalid_request")["fields"] == [
        {"location": ["body", "expected_version"], "type": "int_type"}
    ]
    for field in ("actor", "reason"):
        empty = client.post(
            "/v1/work-items/WI-1/retire",
            json={"expected_version": 1, "actor": "qualification", "reason": REASON, field: ""},
        )
        assert refused(empty, 422, "invalid_request")["fields"] == [
            {"location": ["body", field], "type": "string_too_short"}
        ]
    blocked = refused(retire(client, "WI-1", version=1), 422, "dependants_open")
    assert blocked["details"] == {"id": "WI-1", "dependant_work_item_ids": ["WI-2"]}
    # Retire the open dependant first; a closed dependant does not block its predecessor.
    assert retire(client, "WI-2", version=1).status_code == 200
    freed = retire(client, "WI-1", version=1)
    assert freed.status_code == 200, freed.text
    assert freed.json()["work_item"]["resolution_status"] == "retired"
    assert client.get("/v1/work-items/WI-2").json()["work_item"]["depends_on_work_items"] == ["WI-1"]
    assert history_count(service) == before[2] + 2


@pytest.mark.parametrize("resolution", ["retired", "verified", "resolved", "wont_fix"])
def test_work_item_retirement_refuses_already_terminal_items(native, resolution):
    service, client, _, _ = native
    seed(client)
    intake(client, "WI-1")
    planted = plant(service, client, "WI-1", resolution_status=resolution)
    version = planted["work_item"]["version"]
    before = state(client, service, "WI-1")
    result = retire(client, "WI-1", version=version)
    assert result.status_code == 422 and error(result)["code"] == "work_item_frozen", result.text
    assert error(result)["details"] == {"id": "WI-1", "resolution_status": resolution}
    assert state(client, service, "WI-1") == before
    # Terminality is judged before membership: closed work with irregular memberships is frozen, not invalid.
    plant_membership(
        service, planted["membership"], id="PWM-IMPORTED", project_id="PROJECT-GTKB-NEW-WORK-INTAKE", status="active"
    )
    again = retire(client, "WI-1", version=version)
    assert again.status_code == 422 and error(again)["code"] == "work_item_frozen", again.text
    assert client.get("/v1/work-items/WI-1").json()["membership"] is None
    assert kernel_row(service, "work_items", "WI-1")["version"] == version


@pytest.mark.parametrize("status", ["verified", "retired", "cancelled"])
def test_work_item_retirement_refuses_a_closed_parent_project(native, status):
    service, client, _, _ = native
    seed(client)
    intake(client, "WI-1")
    close_project(service, "PROJECT-1", status)
    before = state(client, service, "WI-1")
    result = retire(client, "WI-1", version=1)
    assert result.status_code == 422 and error(result)["code"] == "project_closed", result.text
    assert state(client, service, "WI-1") == before


def test_work_item_retirement_refuses_a_program_parent_or_irregular_membership(native):
    service, client, _, _ = native
    seed(client)
    intake(client, "WI-1")
    membership = client.get("/v1/work-items/WI-1").json()["membership"]
    plant_membership(service, membership, project_id="PROGRAM-1")
    row, history = kernel_row(service, "work_items", "WI-1"), history_count(service)
    result = retire(client, "WI-1", version=1)
    assert result.status_code == 422 and error(result)["code"] == "program_cannot_contain_work", result.text
    assert kernel_row(service, "work_items", "WI-1") == row and history_count(service) == history
    # Open work with two active parents is refused exactly like every other mutation of it.
    plant_membership(service, membership, id="PWM-IMPORTED", project_id="PROJECT-GTKB-NEW-WORK-INTAKE")
    history = history_count(service)
    result = retire(client, "WI-1", version=1)
    assert result.status_code == 422 and error(result)["code"] == "invalid_membership", result.text
    assert error(result)["details"] == {"work_item_id": "WI-1"}
    assert kernel_row(service, "work_items", "WI-1") == row and history_count(service) == history


def test_work_item_retirement_refuses_an_active_bridge_attempt(bridge):
    service, client, contexts, _ = bridge
    deliver(client, contexts, "retire-guard", "pb1", 1, "NEW")
    before = client.get("/v1/work-items/WI-1").json()
    attempt = attempt_row(service, "retire-guard")
    assert attempt["disposition"] == "active" and attempt["work_item_id"] == "WI-1"
    history = history_count(service)
    result = retire(client, "WI-1", version=before["work_item"]["version"])
    assert result.status_code == 422 and error(result)["code"] == "attempt_active", result.text
    assert error(result)["details"] == {"id": "WI-1", "attempt_ids": ["retire-guard"]}
    assert client.get("/v1/work-items/WI-1").json() == before
    assert attempt_row(service, "retire-guard") == attempt
    assert history_count(service) == history


def test_concurrent_work_item_retirement_records_one_transition(native):
    service, client, _, _ = native
    seed(client)
    intake(client, "WI-1")
    barrier = Barrier(2)
    history = history_count(service)

    def attempt(_):
        barrier.wait(timeout=10)
        try:
            return service.retire_work_item(
                "WI-1", WorkItemRetirement(expected_version=1, actor="qualification", reason=REASON)
            )
        except PostgresKernelError as failure:
            return failure.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(attempt, range(2)))
    assert sum(isinstance(result, dict) for result in outcomes) == 1, outcomes
    assert next(result for result in outcomes if isinstance(result, str)) in {"cas_conflict", "retryable_conflict"}
    assert history_count(service) == history + 1
    row = client.get("/v1/work-items/WI-1").json()["work_item"]
    assert row["version"] == 2 and row["resolution_status"] == "retired"


def test_real_cli_backlog_retire_reads_back_and_refuses_when_authority_is_unavailable(membership_cli):
    service, client, cli, stop = membership_cli
    intake(client, "WI-1", "WI-2")

    def command(record_id, version, *extra, reason=REASON):
        return cli(
            "backlog",
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

    before = state(client, service, "WI-1", "WI-2")
    # Usage errors exit 2 before any request: every option is required and the version is at least 1.
    for arguments in (
        ("--reason", REASON, "--expected-version", "1", "--actor", "qualification"),
        ("--id", "WI-1", "--expected-version", "1", "--actor", "qualification"),
        ("--id", "WI-1", "--reason", REASON, "--actor", "qualification"),
        ("--id", "WI-1", "--reason", REASON, "--expected-version", "1"),
        ("--id", "WI-1", "--reason", REASON, "--expected-version", "0", "--actor", "qualification"),
    ):
        usage = cli("backlog", "retire", *arguments)
        assert usage.returncode == 2 and usage.stdout == "", arguments
        assert usage.stderr.startswith("Usage:") and "\nError: " in usage.stderr
    invalid = command("WI-1", 1, "--json", reason="")
    # Validation is a top-level API fields schema; the current client emits its code/message, without details.
    assert_cli_error(invalid, "invalid_request", "Request does not match the domain contract")
    stale = command("WI-1", 4, "--json")
    assert_cli_error(
        stale,
        "cas_conflict",
        "Read the current work item before retiring it",
        {"id": "WI-1", "expected": 4, "actual": 1},
    )
    assert state(client, service, "WI-1", "WI-2") == before
    result = command("WI-1", 1, "--json")
    output = assert_cli_json(result)
    assert output["work_item"]["resolution_status"] == "retired" and output["work_item"]["version"] == 2
    assert output["membership"] == before[0][0]["membership"]
    assert client.get("/v1/work-items/WI-1").json() == output
    shown = cli("backlog", "show", "WI-1", "--json")
    assert_cli_json(shown, output)
    versions = cli("backlog", "show", "WI-1", "--history")
    assert versions.returncode == 0 and "v2" in versions.stdout and REASON in versions.stdout
    text = command("WI-2", 1)
    assert text.returncode == 0 and text.stderr == "", text.stderr
    assert "WI-2 v2: Artifact correction" in text.stdout and 'resolution_status: "retired"' in text.stdout
    assert history_count(service) == before[2] + 2
    rows = state(client, service, "WI-1", "WI-2")
    stop()
    unavailable = command("WI-1", 2, "--json")
    assert_cli_unavailable(unavailable, "/v1/work-items/WI-1/retire")
    assert state(client, service, "WI-1", "WI-2") == rows


def test_real_cli_dependency_amendment_reads_back_and_orders_retirement(membership_cli, tmp_path):
    """TEST-12254 (GOV-STANDING-BACKLOG-001): a governed `gt backlog record` sets depends_on_work_items on an
    existing work item without database access, `gt backlog show` reads the exact list back, and the recorded
    predecessor list then governs retirement order (an open dependant refuses, a closed one does not)."""
    service, client, cli, _ = membership_cli
    intake(client, "WI-1", "WI-2")
    before = client.get("/v1/work-items/WI-2").json()
    predecessor = client.get("/v1/work-items/WI-1").json()
    history = history_count(service)
    fields = tmp_path / "dependency.json"
    fields.write_text(json.dumps({"depends_on_work_items": ["WI-1"]}), encoding="utf-8")
    recorded = cli(
        "backlog",
        "record",
        "--id",
        "WI-2",
        "--fields-file",
        str(fields),
        "--expected-version",
        "1",
        "--actor",
        "qualification",
        "--change-reason",
        "Record the predecessor",
        "--json",
    )
    after = assert_cli_json(recorded)
    assert after["work_item"]["depends_on_work_items"] == ["WI-1"] and after["work_item"]["version"] == 2
    assert unchanged(after["work_item"], "depends_on_work_items") == unchanged(
        before["work_item"], "depends_on_work_items"
    )
    assert after["work_item"]["resolution_status"] == "open" and after["membership"] == before["membership"]
    shown = cli("backlog", "show", "WI-2", "--json")
    assert_cli_json(shown, after)
    assert client.get("/v1/work-items/WI-1").json() == predecessor
    assert history_count(service) == history + 1

    def command(record_id, version):
        return cli(
            "backlog",
            "retire",
            "--id",
            record_id,
            "--reason",
            REASON,
            "--expected-version",
            str(version),
            "--actor",
            "qualification",
            "--json",
        )

    blocked = command("WI-1", 1)
    assert_cli_error(
        blocked,
        "dependants_open",
        "Open work still depends on this item; retire or re-point the dependants first",
        {"id": "WI-1", "dependant_work_item_ids": ["WI-2"]},
    )
    assert client.get("/v1/work-items/WI-1").json() == predecessor
    assert_cli_json(command("WI-2", 2))
    freed = command("WI-1", 1)
    assert assert_cli_json(freed)["work_item"]["resolution_status"] == "retired"
    assert history_count(service) == history + 3
