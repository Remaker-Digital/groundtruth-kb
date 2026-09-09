"""Project prerequisites through native planning, bridge effects and real Git completion."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, Event

import pytest
from groundtruth_kb import native_authority
from groundtruth_kb.bridge import native as native_bridge
from groundtruth_kb.native_authority import DependencyMutation
from groundtruth_kb.postgres_kernel import PostgresKernelError
from psycopg import sql

from platform_tests.groundtruth_kb.test_native_authority_service import history_count, put, seed, work_fields
from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_bridge import authored, claim, deliver
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge
from platform_tests.groundtruth_kb.test_native_project_finalization import base, git, integration, post, verify

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def dependency_fields(dependent="PROJECT-1", prerequisite="PROJECT-2", **extra):
    return {
        "dependent_project_id": dependent,
        "prerequisite_project_id": prerequisite,
        "required_prerequisite_state": "verified",
        "affected_gate": "readiness",
        "rationale": "The downstream artifacts require the completed predecessor result",
        **extra,
    }


def add(client, record_id="DEP-1", **fields):
    response = put(client, "project-dependencies", record_id, dependency_fields(**fields))
    assert response.status_code == 200, response.text
    return response.json()


def amend(client, record_id="DEP-1", **fields):
    current = client.get(f"/v1/project-dependencies/{record_id}").json()
    response = put(client, "project-dependencies", record_id, fields, expected_version=current["version"])
    assert response.status_code == 200, response.text
    return response.json()


def project(client, record_id="PROJECT-2"):
    response = put(client, "projects", record_id, {"name": record_id, "target_outcome": "A complete test outcome"})
    assert response.status_code == 200, response.text


def set_project_status(service, record_id, status):
    # Deliberately construct historical/incomplete source states to test refusal.
    with service.kernel.transaction() as tx:
        current = tx.get("projects", {"id": record_id})
        tx.mutate(
            table="projects",
            identity={"id": record_id},
            expected_version=current["version"],
            new_state={**current, "status": status},
            actor="qualification",
            reason="Historical-state fixture",
        )


def test_dependency_amendments_preserve_authorization_and_explain_readiness(native):
    service, client, _, _ = native
    seed(client)
    project(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    original = client.get("/v1/projects/PROJECT-1").json()["project"]
    row = add(client)
    assert row["version"] == 1
    report = client.get("/v1/projects/PROJECT-1/readiness").json()
    assert report["ready"] is False
    assert report["dependencies"] == [
        {
            "dependency_id": "DEP-1",
            "prerequisite_project_id": "PROJECT-2",
            "required_state": "verified",
            "current_state": "active",
            "satisfied": False,
            "reason": "prerequisite_state_not_reached",
        }
    ]
    assert client.get("/v1/work-items/WI-1/context").json()["readiness"] == report
    assert client.get("/v1/projects/PROJECT-1/readiness", params={"gate": "closure"}).json()["ready"]
    listing = client.get(
        "/v1/project-dependencies", params={"dependent_project_id": "PROJECT-1", "affected_gate": "readiness"}
    )
    assert listing.json()["records"] == [row]
    before = history_count(service)
    stale = put(client, "project-dependencies", "DEP-1", {"status": "retired"}, expected_version=0)
    assert stale.status_code == 409 and stale.json()["error"]["code"] == "cas_conflict"
    assert history_count(service) == before
    amend(client, status="retired")
    assert client.get("/v1/projects/PROJECT-1/readiness").json()["ready"]
    amend(client, status="active")
    assert not client.get("/v1/projects/PROJECT-1/readiness").json()["ready"]
    assert client.get("/v1/projects/PROJECT-1").json()["project"] == original


@pytest.mark.parametrize(
    "fields,code",
    [
        ({"prerequisite_project_id": "MISSING"}, "not_found"),
        ({"prerequisite_project_id": "PROGRAM-1"}, "invalid_dependency_endpoint"),
        ({"prerequisite_project_id": "PROJECT-1"}, "dependency_cycle"),
        ({"required_prerequisite_state": "completed"}, "invalid_request"),
        ({"affected_gate": "authorization"}, "invalid_request"),
        ({"affected_gate": "promotion"}, "invalid_request"),
        ({"rationale": "   "}, "invalid_dependency_contract"),
    ],
)
def test_invalid_dependency_has_no_partial_row_or_history(native, fields, code):
    service, client, _, _ = native
    seed(client)
    project(client)
    before = history_count(service)
    result = put(client, "project-dependencies", "DEP-INVALID", {**dependency_fields(), **fields})
    assert result.json().get("error", result.json())["code"] == code, result.text
    assert history_count(service) == before
    assert client.get("/v1/project-dependencies/DEP-INVALID").status_code == 404


def test_exact_states_do_not_alias_retirement_or_unbacked_verification(native):
    service, client, _, _ = native
    seed(client)
    project(client)
    add(client)
    set_project_status(service, "PROJECT-2", "retired")
    report = client.get("/v1/projects/PROJECT-1/readiness").json()
    assert not report["ready"] and report["dependencies"][0]["current_state"] == "retired"
    amend(client, required_prerequisite_state="retired")
    assert client.get("/v1/projects/PROJECT-1/readiness").json()["ready"]
    # Reconcile fixture state without pretending that a status label is a commit.
    set_project_status(service, "PROJECT-2", "verified")
    amend(client, required_prerequisite_state="verified")
    report = client.get("/v1/projects/PROJECT-1/readiness").json()
    assert not report["ready"] and report["dependencies"][0]["reason"] == "prerequisite_commit_missing"
    with service.kernel.transaction() as tx:
        native_authority._write(
            tx,
            "project_artifact_links",
            "PCL-INVALID",
            {
                "project_id": "PROJECT-2",
                "artifact_type": "git_commit",
                "relationship": "activation",
                "status": "active",
                "artifact_ref": "a label is not a Git commit identity",
            },
            native_authority.Mutation(expected_version=0, actor="qualification", reason="Malformed source fixture"),
        )
    report = client.get("/v1/projects/PROJECT-1/readiness").json()
    assert not report["ready"] and report["dependencies"][0]["reason"] == "prerequisite_commit_missing"
    project(client, "PROJECT-3")
    add(client, "DEP-OTHER", dependent="PROJECT-3", prerequisite="PROJECT-1")
    # Completing the dependent of one existing edge must not poison unrelated graph edits.
    set_project_status(service, "PROJECT-1", "verified")
    project(client, "PROJECT-4")
    add(client, "DEP-4", dependent="PROJECT-4", prerequisite="PROJECT-3")
    bad = put(client, "project-dependencies", "DEP-CLOSED", dependency_fields(prerequisite="PROJECT-3"))
    assert bad.json()["error"]["code"] == "closed_dependent_project"


def test_cycle_and_duplicate_amendments_are_atomic(native, monkeypatch):
    service, client, _, _ = native
    seed(client)
    project(client)
    barrier = Barrier(2)
    original = native_authority.validate_project_dependencies

    def simultaneous(records, projects):
        original(records, projects)
        barrier.wait(timeout=10)

    def write(pair):
        record_id, dependent, prerequisite = pair
        try:
            service.amend_dependency(
                record_id,
                DependencyMutation(
                    expected_version=0,
                    actor="qualification",
                    reason="Concurrent graph change",
                    fields=dependency_fields(dependent, prerequisite),
                ),
            )
            return "ok"
        except PostgresKernelError as error:
            return error.code

    with monkeypatch.context() as patch:
        patch.setattr(native_authority, "validate_project_dependencies", simultaneous)
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(write, [("DEP-A", "PROJECT-1", "PROJECT-2"), ("DEP-B", "PROJECT-2", "PROJECT-1")]))
    assert sorted(outcomes) == ["ok", "retryable_conflict"]
    rows = client.get("/v1/project-dependencies").json()["records"]
    assert len(rows) == 1
    existing = rows[0]
    reverse = dependency_fields(existing["prerequisite_project_id"], existing["dependent_project_id"])
    before = history_count(service)
    assert put(client, "project-dependencies", "DEP-CYCLE", reverse).json()["error"]["code"] == "dependency_cycle"
    assert (
        put(
            client,
            "project-dependencies",
            "DEP-DUP",
            dependency_fields(existing["dependent_project_id"], existing["prerequisite_project_id"]),
        ).json()["error"]["code"]
        == "duplicate_dependency"
    )
    assert history_count(service) == before


def test_dependency_added_after_new_claim_blocks_delivery_without_consuming_it(bridge):
    service, client, contexts, _ = bridge
    project(client)
    reserved = claim(client, "new-chain", "pb1", 0, "NEW").json()
    add(client)
    assert put(client, "work-items", "WI-2", work_fields(), project_id="PROJECT-1").status_code == 200
    refused = claim(client, "other-chain", "pb2", 0, "NEW", work_item_id="WI-2")
    assert refused.json()["error"]["code"] == "project_dependencies_unsatisfied"
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(
            sql.SQL("SELECT 1 FROM {}.bridge_attempts WHERE id='other-chain'").format(sql.Identifier(tx.schema))
        )
        assert tx.cursor.fetchone() is None
    body = {
        "native_context_id": "pb1",
        "fence": reserved["fence"],
        "content": authored(contexts["pb1"], "new-chain", 1, "NEW"),
    }
    refused = client.post("/v1/bridge/new-chain/deliver", json=body)
    assert refused.json()["error"]["details"]["dependencies"][0]["prerequisite_project_id"] == "PROJECT-2"
    amend(client, status="retired")
    assert client.post("/v1/bridge/new-chain/deliver", json=body).status_code == 200
    amend(client, status="active")
    queue = client.get("/v1/bridge/queue", params={"role": "lo"}).json()
    assert queue["eligible"] == [] and queue["blocked"][0]["id"] == "new-chain"
    assert claim(client, "new-chain", "lo1", 1, "GO").json()["error"]["code"] == "project_dependencies_unsatisfied"
    # A corrective rejection remains lawful when forward work is waiting.
    deliver(client, contexts, "new-chain", "lo1", 2, "NO-GO")


def ready_checkout(bridge):
    _, client, contexts, root = bridge
    deliver(client, contexts, "effect-chain", "pb1", 1, "NEW")
    deliver(client, contexts, "effect-chain", "lo1", 2, "GO")
    reserved = claim(client, "effect-chain", "pb2", 2, "READY").json()
    fence = {"native_context_id": "pb2", "fence": reserved["fence"]}
    opened = client.post("/v1/bridge/effect-chain/worktree", json=fence).json()
    (Path(opened["path"]) / "code.py").write_text("result = 42\n", encoding="utf-8")
    return client, root, {**fence, "expected_artifacts": opened["artifact_preimages"]}


def test_changed_prerequisite_blocks_publication_and_fence_check(bridge):
    client, root, body = ready_checkout(bridge)
    project(client)
    add(client)
    preimage = (root / "code.py").read_bytes()
    fence = {key: body[key] for key in ("native_context_id", "fence")}
    for route in ("check", "worktree"):
        result = client.post(f"/v1/bridge/effect-chain/{route}", json=fence)
        assert result.json()["error"]["code"] == "project_dependencies_unsatisfied"
    result = client.post("/v1/bridge/effect-chain/publish-work", json=body)
    assert result.json()["error"]["code"] == "project_dependencies_unsatisfied"
    assert (root / "code.py").read_bytes() == preimage
    amend(client, status="retired")
    result = client.post("/v1/bridge/effect-chain/publish-work", json=body)
    assert result.status_code == 200, result.text
    assert (root / "code.py").read_text() == "result = 42\n"


def test_dependency_writer_cannot_cross_a_publication_effect(bridge, monkeypatch):
    service, _, _, _ = bridge
    client, root, body = ready_checkout(bridge)
    project(client)
    entered, release, writer_started = Event(), Event(), Event()
    original = native_bridge.publish_context_work

    def paused(*args, **kwargs):
        entered.set()
        assert release.wait(timeout=10)
        return original(*args, **kwargs)

    def writer():
        writer_started.set()
        return service.amend_dependency(
            "DEP-LATE",
            DependencyMutation(
                expected_version=0,
                actor="qualification",
                reason="Resequence after publication",
                fields=dependency_fields(),
            ),
        )

    with monkeypatch.context() as patch:
        patch.setattr(native_bridge, "publish_context_work", paused)
        with ThreadPoolExecutor(max_workers=2) as pool:
            published = pool.submit(client.post, "/v1/bridge/effect-chain/publish-work", json=body)
            assert entered.wait(timeout=10)
            updated = pool.submit(writer)
            try:
                assert writer_started.wait(timeout=10)
                with pytest.raises(TimeoutError):
                    updated.result(timeout=0.2)
            finally:
                release.set()
            result = published.result(timeout=15)
            assert result.status_code == 200, result.text
            assert updated.result(timeout=15)["id"] == "DEP-LATE"
    assert (root / "code.py").read_text() == "result = 42\n"
    assert (
        client.post("/v1/bridge/effect-chain/publish-work", json=body).json()["error"]["code"]
        == "project_dependencies_unsatisfied"
    )


def test_closure_is_rechecked_before_integration_and_real_commit_unblocks_successor(bridge):
    _, client, contexts, root = bridge
    project(client)
    project(client, "PROJECT-3")
    add(client, "DEP-SUCCESSOR", dependent="PROJECT-2", prerequisite="PROJECT-1")
    add(client, "DEP-CLOSE", prerequisite="PROJECT-3", required_prerequisite_state="active", affected_gate="closure")
    verify(client, contexts, root, 1, "code.py")
    assert not client.get("/v1/projects/PROJECT-2/readiness").json()["ready"]
    prepared = post(client, "prepare-commit")
    assert prepared.status_code == 200, prepared.text
    checkout = Path(prepared.json()["checkout"]["path"])
    git(checkout, "add", "--", "code.py", "tests/test_effect.py")
    git(checkout, "commit", "-m", "Complete prerequisite result (WI-1)")
    commit, parent = base(checkout), prepared.json()["expected_parent"]
    amend(client, "DEP-CLOSE", required_prerequisite_state="verified")
    refusal = post(client, "confirm-commit", commit_id=commit, expected_parent=parent)
    assert refusal.json()["error"]["code"] == "project_dependencies_unsatisfied"
    assert refusal.json()["error"]["details"]["gate"] == "closure"
    assert base(integration(root)) == parent
    assert post(client, "prepare-commit").json()["error"]["code"] == "project_dependencies_unsatisfied"
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "active"
    amend(client, "DEP-CLOSE", status="retired")
    result = post(client, "confirm-commit", commit_id=commit, expected_parent=parent)
    assert result.status_code == 200 and result.json()["status"] == "confirmed", result.text
    assert base(integration(root)) == commit
    assert client.get("/v1/projects/PROJECT-2/readiness").json()["ready"]
