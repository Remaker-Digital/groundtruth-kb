"""Owner-directed project ordering without permission carriers or chain revocation."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from groundtruth_kb.native_authority import ProjectAuthorizationChange
from groundtruth_kb.postgres_kernel import PostgresKernelError, PostgresTransaction

from platform_tests.groundtruth_kb.bridge_fixtures import authored, claim, deliver, ready_checkout
from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.finalization_fixtures import base, git, integration
from platform_tests.groundtruth_kb.native_fixtures import history_count, put, seed, work_fields
from platform_tests.groundtruth_kb.native_fixtures import membership_cli as membership_cli
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def change(client, value, *, project="PROJECT-1", version=None, **extra):
    if version is None:
        version = client.get(f"/v1/projects/{project}").json()["project"]["version"]
    return client.put(
        f"/v1/projects/{project}/authorization",
        json={
            "expected_version": version,
            "actor": "qualification",
            "reason": "Owner-selected work ordering",
            "authorization": value,
            **extra,
        },
    )


def test_authorization_changes_only_current_project_ordering_and_preserves_membership(native):
    service, client, _, _ = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    work = client.get("/v1/work-items/WI-1").json()
    original = client.get("/v1/projects/PROJECT-1").json()["project"]
    program = client.get("/v1/projects/PROGRAM-1").json()["project"]
    assert original["authorization"] == "authorized" and program["authorization"] is None
    before = history_count(service)
    result = change(client, "not authorized")
    assert result.status_code == 200, result.text
    current = result.json()
    assert current["authorization"] == "not authorized" and current["version"] == original["version"] + 1
    changed = {"authorization", "version", "changed_at", "changed_by", "change_reason"}
    assert {k: v for k, v in current.items() if k not in changed} == {
        k: v for k, v in original.items() if k not in changed
    }
    assert client.get("/v1/projects/PROJECT-1").json()["project"] == current
    assert client.get("/v1/work-items/WI-1").json() == work
    assert history_count(service) == before + 1
    assert change(client, "not authorized").json() == current
    assert history_count(service) == before + 1
    stale = change(client, "authorized", version=original["version"])
    assert stale.status_code == 409 and stale.json()["error"]["code"] == "cas_conflict"
    assert history_count(service) == before + 1
    assert (
        put(
            client, "projects", "PROJECT-1", {"notes": "Current project purpose"}, expected_version=current["version"]
        ).status_code
        == 200
    )
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["authorization"] == "not authorized"
    assert put(client, "projects", "PROJECT-2", {"name": "Receiving project"}).status_code == 200
    moved = client.post(
        "/v1/work-items/WI-1/move",
        json={
            "expected_version": work["membership"]["version"],
            "actor": "qualification",
            "reason": "Reconcile outcome",
            "source_project_id": "PROJECT-1",
            "destination_project_id": "PROJECT-2",
        },
    )
    assert moved.status_code == 200, moved.text
    assert client.get("/v1/work-items/WI-1").json()["membership"]["project_id"] == "PROJECT-2"
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["authorization"] == "not authorized"
    assert client.get("/v1/projects/PROJECT-2").json()["project"]["authorization"] == "authorized"
    assert change(client, "authorized").json()["authorization"] == "authorized"


@pytest.mark.parametrize(
    "project,code",
    [
        ("MISSING", "not_found"),
        ("PROGRAM-1", "program_not_authorizable"),
        ("PROJECT-GTKB-NEW-WORK-INTAKE", "intake_not_authorizable"),
    ],
)
def test_nonexecution_and_intake_projects_cannot_gain_authorization(native, project, code):
    service, client, _, _ = native
    seed(client)
    before = history_count(service)
    observed = client.get(f"/v1/projects/{project}")
    result = change(client, "authorized", project=project, version=1)
    assert result.status_code in {404, 422} and result.json()["error"]["code"] == code
    assert client.get(f"/v1/projects/{project}").json() == observed.json()
    assert history_count(service) == before
    intake = client.get("/v1/projects/PROJECT-GTKB-NEW-WORK-INTAKE").json()["project"]
    assert intake["authorization"] == "not authorized"
    assert change(client, "not authorized", project=intake["id"]).json() == intake
    assert history_count(service) == before


@pytest.mark.parametrize(
    "values",
    [
        {"authorization": True},
        {"authorization": None},
        {"authorization": "approved"},
        {"authorization": "Authorized"},
        {"authorization": "authorized", "permission": True},
        {"authorization": "authorized", "scope": ["code.py"]},
        {"authorization": "authorized", "expiry": "2099-01-01"},
    ],
)
def test_authorization_request_rejects_other_values_and_permission_fields(native, values):
    service, client, _, _ = native
    seed(client)
    before = client.get("/v1/projects/PROJECT-1").json()
    history = history_count(service)
    result = client.put(
        "/v1/projects/PROJECT-1/authorization",
        json={
            "expected_version": 1,
            "actor": "qualification",
            "reason": "Invalid input",
            **values,
        },
    )
    assert result.status_code == 422 and result.json()["code"] == "invalid_request"
    assert client.get("/v1/projects/PROJECT-1").json() == before
    assert history_count(service) == history
    generic = put(client, "projects", "PROJECT-1", {"authorization": "not authorized"}, expected_version=1)
    assert generic.status_code == 422 and generic.json()["code"] == "invalid_request"
    assert history_count(service) == history


@pytest.mark.parametrize("status", ["verified", "retired", "cancelled"])
def test_closed_projects_cannot_change_authorization(native, status):
    service, client, _, _ = native
    seed(client)
    with service.kernel.transaction() as tx:
        current = tx.get("projects", {"id": "PROJECT-1"})
        tx.mutate(
            table="projects",
            identity={"id": "PROJECT-1"},
            expected_version=current["version"],
            new_state={**current, "status": status},
            actor="qualification",
            reason="Closed fixture",
        )
    before = client.get("/v1/projects/PROJECT-1").json()
    history = history_count(service)
    result = change(client, "not authorized")
    assert result.status_code == 422 and result.json()["error"]["code"] == "project_closed"
    assert client.get("/v1/projects/PROJECT-1").json() == before
    assert history_count(service) == history


def test_concurrent_authorization_has_one_version_winner(native):
    service, client, _, _ = native
    seed(client)
    before = history_count(service)
    barrier = Barrier(2)

    def amend(_):
        barrier.wait(timeout=10)
        try:
            return service.set_project_authorization(
                "PROJECT-1",
                ProjectAuthorizationChange(
                    expected_version=1,
                    actor="qualification",
                    reason="Competing current-state correction",
                    authorization="not authorized",
                ),
            )
        except PostgresKernelError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(amend, [1, 2]))
    assert sum(isinstance(value, dict) for value in outcomes) == 1
    assert next(value for value in outcomes if isinstance(value, str)) in {"cas_conflict", "retryable_conflict"}
    assert history_count(service) == before + 1


def test_authorization_failure_rolls_back_project_and_history(native, monkeypatch):
    service, client, _, _ = native
    seed(client)
    before = client.get("/v1/projects/PROJECT-1").json()
    history = history_count(service)
    mutate = PostgresTransaction.mutate
    observed = []

    def fail_after_write(tx, **request):
        result = mutate(tx, **request)
        if request["table"] == "projects":
            observed.append(result["record"]["authorization"])
            raise PostgresKernelError("injected_failure", "Abort after row and history write")
        return result

    with monkeypatch.context() as patch:
        patch.setattr(PostgresTransaction, "mutate", fail_after_write)
        result = change(client, "not authorized")
    assert result.status_code == 422 and result.json()["error"]["code"] == "injected_failure"
    assert observed == ["not authorized"]
    assert client.get("/v1/projects/PROJECT-1").json() == before
    assert history_count(service) == history
    assert change(client, "not authorized").status_code == 200


def test_native_authorization_rechecks_new_delivery_and_preserves_same_claim_retry(bridge):
    _, client, contexts, _ = bridge
    reserved = claim(client, "new-ordering", "pb1", 0, "NEW").json()
    assert change(client, "not authorized").status_code == 200
    body = {
        "native_context_id": "pb1",
        "fence": reserved["fence"],
        "content": authored(contexts["pb1"], "new-ordering", 1, "NEW"),
    }
    before = client.get("/v1/bridge/new-ordering/show", params={"include_content": True}).json()
    refused = client.post("/v1/bridge/new-ordering/deliver", json=body)
    assert refused.status_code == 422 and refused.json()["error"]["code"] == "project_not_authorized"
    assert client.get("/v1/bridge/new-ordering/show", params={"include_content": True}).json() == before
    assert put(client, "work-items", "WI-2", work_fields(), project_id="PROJECT-1").status_code == 200
    new_claim = claim(client, "another-new", "pb2", 0, "NEW", work_item_id="WI-2")
    assert new_claim.status_code == 422 and new_claim.json()["error"]["code"] == "project_not_authorized"
    assert change(client, "authorized").status_code == 200
    assert client.post("/v1/bridge/new-ordering/deliver", json=body).status_code == 200


@pytest.mark.parametrize("stage", ["GO", "VERIFIED"])
def test_native_authorization_change_preserves_initiated_effect_and_finalization(bridge, stage):
    _, _, contexts, _ = bridge
    client, root, body = ready_checkout(bridge)
    if stage == "GO":
        assert change(client, "not authorized").status_code == 200
    published = client.post("/v1/bridge/effect-chain/publish-work", json=body)
    assert published.status_code == 200, published.text
    assert (root / "code.py").read_text() == "result = 42\n"
    report = client.post(
        "/v1/bridge/effect-chain/deliver",
        json={
            "native_context_id": "pb2",
            "fence": body["fence"],
            "content": authored(contexts["pb2"], "effect-chain", 3, "READY"),
        },
    )
    assert report.status_code == 200, report.text
    artifacts = client.get("/v1/bridge/effect-chain/artifacts").json()
    deliver(client, contexts, "effect-chain", "lo2", 4, "VERIFIED", verified_artifacts=json.dumps(artifacts))
    if stage == "VERIFIED":
        assert change(client, "not authorized").status_code == 200
    project = client.get("/v1/projects/PROJECT-1").json()["project"]
    assert project["authorization"] == "not authorized"
    prepared = client.post(
        "/v1/projects/PROJECT-1/prepare-commit",
        json={
            "native_context_id": "lo3",
            "expected_version": project["version"],
        },
    )
    assert prepared.status_code == 200, prepared.text
    ready = prepared.json()
    assert ready["status"] == "ready_to_commit"
    assert ready["required_citations"] == ["(WI-1)"]
    checkout = Path(ready["checkout"]["path"])
    main = integration(checkout)
    assert base(main) == ready["expected_parent"]
    git(checkout, "add", "--", "code.py", "tests/test_effect.py")
    git(checkout, "commit", "-m", "Complete initiated project after ordering change (WI-1)")
    commit = base(checkout)
    confirmation = {
        "native_context_id": "lo3",
        "expected_version": project["version"],
        "commit_id": commit,
        "expected_parent": ready["expected_parent"],
    }
    result = client.post("/v1/projects/PROJECT-1/confirm-commit", json=confirmation)
    assert result.status_code == 200 and result.json()["status"] == "confirmed", result.text
    assert base(main) == commit
    assert git(main, "rev-list", "--count", ready["expected_parent"] + "..HEAD").stdout.strip() == "1"
    terminal = client.get("/v1/projects/PROJECT-1").json()["project"]
    assert terminal["status"] == "verified" and terminal["authorization"] == "not authorized"
    work = client.get("/v1/work-items/WI-1").json()
    assert work["work_item"]["completion_evidence"] == "git:" + commit
    assert work["membership"]["project_id"] == "PROJECT-1"
    state = client.get("/v1/bridge/effect-chain/show", params={"include_content": True}).json()
    assert state["attempt"]["disposition"] == "committed"
    assert state["attempt"]["terminal_commit"] == commit
    assert "messages" not in state
    retry = client.post("/v1/projects/PROJECT-1/confirm-commit", json=confirmation)
    assert retry.status_code == 200 and retry.json()["status"] == "already_confirmed", retry.text
    assert base(main) == commit


def test_real_cli_authorization_readback_stale_and_unavailable_refusals(membership_cli):
    service, client, cli, stop = membership_cli

    def amend(value, version):
        return cli(
            "projects",
            "set-authorization",
            "PROJECT-1",
            "--authorization",
            value,
            "--expected-version",
            str(version),
            "--actor",
            "qualification",
            "--change-reason",
            "Owner orders this project",
            "--json",
        )

    changed = amend("not authorized", 1)
    assert changed.returncode == 0, changed.stderr
    record = json.loads(changed.stdout)
    assert record["authorization"] == "not authorized" and record["version"] == 2
    assert client.get("/v1/projects/PROJECT-1").json()["project"] == record
    text = cli("projects", "show", "PROJECT-1")
    assert text.returncode == 0 and 'authorization: "not authorized"' in text.stdout
    before = history_count(service)
    stale = amend("authorized", 1)
    assert stale.returncode != 0 and "cas_conflict" in stale.stderr
    assert history_count(service) == before
    stop()
    unavailable = amend("authorized", 2)
    assert unavailable.returncode != 0 and "authority_unavailable" in unavailable.stderr
    assert client.get("/v1/projects/PROJECT-1").json()["project"] == record
    assert history_count(service) == before
