"""Predecessor results through native readiness, effects and real Git workspaces."""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

import pytest
from groundtruth_kb.bridge import native as native_bridge
from groundtruth_kb.bridge.native import NativeBridgeService
from groundtruth_kb.native_authority import Mutation, SpecMutation, _related, _write
from groundtruth_kb.postgres_kernel import PostgresKernelError

from platform_tests.groundtruth_kb.test_native_authority_service import history_count, put, work_fields
from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge
from platform_tests.groundtruth_kb.test_native_bridge import claim, deliver
from platform_tests.groundtruth_kb.test_native_project_dependencies import project
from platform_tests.groundtruth_kb.test_native_project_finalization import (
    base,
    commit_product,
    git,
    integration,
    post,
    verify,
)

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def dependent(client, *, project_id="PROJECT-1"):
    result = put(client, "work-items", "WI-2", work_fields(depends_on_work_items=["WI-1"]), project_id=project_id)
    assert result.status_code == 200, result.text


def readiness(client):
    result = client.get("/v1/work-items/WI-2/readiness")
    assert result.status_code == 200, result.text
    return result.json()


@pytest.mark.parametrize("path", ["code.py", "second.py"])
def test_same_project_predecessors_allow_one_complete_project_commit(bridge, path):
    service, client, contexts, root = bridge
    dependent(client)
    before = history_count(service)
    refused = claim(client, "chain-2", "pb1", 0, "NEW", work_item_id="WI-2")
    assert refused.json()["error"]["code"] == "work_item_dependencies_unsatisfied"
    assert readiness(client)["predecessors"][0]["reason"] == "predecessor_not_verified"
    assert client.get("/v1/bridge/chain-2/show").status_code == 404
    assert history_count(service) == before
    verify(client, contexts, root, 1, "code.py")
    ready = readiness(client)
    assert ready["ready"] and ready["predecessors"][0]["required_result"] == "independent_review"
    assert client.get("/v1/work-items/WI-2/context").json()["work_item_readiness"] == ready
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "active"
    assert client.get("/v1/project-dependencies").json()["records"] == []
    verify(client, contexts, root, 2, path)
    prepared = post(client, "prepare-commit").json()
    if path == "code.py":
        assert prepared["status"] == "fresh_verification_required"
        assert prepared["work_item_ids"] == ["WI-1"]
        assert not readiness(client)["ready"]
        artifacts = client.get("/v1/bridge/chain-1/artifacts").json()
        deliver(client, contexts, "chain-1", "lo3", 5, "VERIFIED", verified_artifacts=json.dumps(artifacts))
        prepared = post(client, "prepare-commit").json()
    assert prepared["status"] == "ready_to_commit"
    candidate = commit_product(Path(prepared["checkout"]["path"]))
    result = post(client, "confirm-commit", commit_id=candidate, expected_parent=prepared["expected_parent"])
    assert result.status_code == 200 and result.json()["status"] == "confirmed", result.text
    assert base(integration(root)) == candidate


@pytest.mark.parametrize("status", ["verified", "retired"])
def test_labels_without_review_do_not_satisfy_predecessors_or_block_unrelated_work(bridge, status):
    service, client, _, _ = bridge
    dependent(client)
    with service.kernel.transaction() as tx:
        _write(
            tx,
            "work_items",
            "WI-1",
            {"resolution_status": status},
            Mutation(expected_version=1, actor="qualification", reason="Incomplete historical source fixture"),
        )
    report = readiness(client)
    assert not report["ready"]
    expected = "predecessor_review_missing" if status == "verified" else "predecessor_not_verified"
    assert report["predecessors"][0]["reason"] == expected
    assert put(client, "work-items", "WI-3", work_fields(), project_id="PROJECT-1").status_code == 200
    assert client.get("/v1/work-items/WI-3/readiness").json()["ready"]
    assert claim(client, "unrelated", "pb1", 0, "NEW", work_item_id="WI-3").status_code == 200


@pytest.mark.parametrize("status", ["resolved", "verified"])
def test_closed_predecessor_with_irregular_membership_reports_a_reason_without_refusing(bridge, status):
    # Owner decision 2026-09-10: closed work migrates with its recorded membership
    # history exactly, so a closed predecessor may carry no current project. The
    # dependent's readiness names that reason; open work keeps the strict rule.
    service, client, _, _ = bridge
    dependent(client)
    with service.kernel.transaction() as tx:
        _write(
            tx,
            "work_items",
            "WI-1",
            {"resolution_status": status},
            Mutation(expected_version=1, actor="qualification", reason="Closed historical source fixture"),
        )
        membership = _related(tx, "project_work_item_memberships", work_item_id="WI-1", status="active")[0]
        _write(
            tx,
            "project_work_item_memberships",
            membership["id"],
            {"status": "removed"},
            Mutation(expected_version=membership["version"], actor="qualification", reason="Irregular closed history"),
        )
    report = readiness(client)
    assert not report["ready"]
    assert report["predecessors"] == [
        {
            "work_item_id": "WI-1",
            "project_id": None,
            "required_result": "project_commit",
            "current_status": status,
            "satisfied": False,
            "reason": "predecessor_membership_irregular",
            "changed_paths": [],
        }
    ]
    assert client.get("/v1/work-items/WI-2/context").json()["work_item_readiness"] == report
    refused = claim(client, "chain-2", "pb1", 0, "NEW", work_item_id="WI-2")
    assert refused.json()["error"]["code"] == "work_item_dependencies_unsatisfied"
    assert client.get("/v1/work-items/WI-1/context").json()["error"]["code"] == "invalid_membership"
    assert put(client, "work-items", "WI-3", work_fields(), project_id="PROJECT-1").status_code == 200
    assert client.get("/v1/work-items/WI-3/readiness").json()["ready"]
    assert claim(client, "unrelated", "pb1", 0, "NEW", work_item_id="WI-3").status_code == 200


def test_changed_prerequisite_bytes_block_effects_and_leave_corrective_review_available(bridge):
    _, client, contexts, root = bridge
    dependent(client)
    verify(client, contexts, root, 1, "code.py")
    deliver(client, contexts, "chain-2", "pb1", 1, "NEW", work_item_id="WI-2", target_paths='["second.py"]')
    original = (root / "code.py").read_bytes()
    (root / "code.py").write_text("unreviewed = True\n", encoding="utf-8")
    assert readiness(client)["predecessors"][0]["changed_paths"] == ["code.py"]
    queue = client.get("/v1/bridge/queue", params={"role": "lo"}).json()
    assert [row["id"] for row in queue["blocked"]] == ["chain-2"]
    assert queue["blocked"][0]["work_item_readiness"]["ready"] is False
    assert claim(client, "chain-2", "lo1", 1, "GO", work_item_id="WI-2").status_code == 422
    # A negative verdict remains lawful and is authored by the reviewing agent.
    deliver(client, contexts, "chain-2", "lo1", 2, "NO-GO", work_item_id="WI-2")
    (root / "code.py").write_bytes(original)
    deliver(client, contexts, "chain-2", "pb1", 3, "REVISED", work_item_id="WI-2", target_paths='["second.py"]')
    deliver(client, contexts, "chain-2", "lo1", 4, "GO", work_item_id="WI-2")
    reserved = claim(client, "chain-2", "pb3", 4, "READY", work_item_id="WI-2").json()
    fence = {"native_context_id": "pb3", "fence": reserved["fence"]}
    opened = client.post("/v1/bridge/chain-2/worktree", json=fence).json()
    (Path(opened["path"]) / "second.py").write_text("downstream = 2\n", encoding="utf-8")
    (root / "code.py").write_text("changed_after_retrieval = True\n", encoding="utf-8")
    before = (root / "second.py").read_bytes()
    for route, body in (
        ("check", fence),
        ("worktree", fence),
        ("publish-work", {**fence, "expected_artifacts": opened["artifact_preimages"]}),
    ):
        response = client.post(f"/v1/bridge/chain-2/{route}", json=body)
        assert response.json()["error"]["code"] == "work_item_dependencies_unsatisfied", response.text
    assert (root / "second.py").read_bytes() == before
    (root / "code.py").write_bytes(original)
    result = client.post(
        "/v1/bridge/chain-2/publish-work", json={**fence, "expected_artifacts": opened["artifact_preimages"]}
    )
    assert result.status_code == 200, result.text


@pytest.mark.parametrize("overlap", [False, True])
def test_cross_project_result_requires_commit_and_reaches_a_fresh_context(bridge, overlap):
    service, client, contexts, root = bridge
    project(client)
    dependent(client, project_id="PROJECT-2")
    old = NativeBridgeService(service.kernel, integration(root)).work_root("PROJECT-2")
    local = old / ("code.py" if overlap else "unrelated-project-work.txt")
    local.write_text("Preserve this project's unfinished work\n", encoding="utf-8")
    verify(client, contexts, root, 1, "code.py")
    assert readiness(client)["predecessors"][0]["reason"] == "predecessor_project_not_committed"
    prepared = post(client, "prepare-commit").json()
    checkout = Path(prepared["checkout"]["path"])
    git(checkout, "add", "--", "code.py", "tests/test_effect.py")
    git(checkout, "commit", "-m", "Complete predecessor (WI-1)")
    commit = base(checkout)
    result = post(client, "confirm-commit", commit_id=commit, expected_parent=prepared["expected_parent"])
    assert result.status_code == 200, result.text
    assert readiness(client)["ready"]
    assert base(old) == prepared["expected_parent"]
    reserved = claim(client, "chain-2", "pb3", 0, "NEW", work_item_id="WI-2").json()
    loaded = client.post("/v1/bridge/chain-2/worktree", json={"native_context_id": "pb3", "fence": reserved["fence"]})
    assert local.read_text() == "Preserve this project's unfinished work\n"
    if overlap:
        assert loaded.json()["error"]["code"] == "project_base_reconciliation_required"
        assert base(old) == prepared["expected_parent"]
    else:
        assert loaded.status_code == 200, loaded.text
        assert loaded.json()["head"] == commit
        assert (Path(loaded.json()["path"]) / "code.py").read_text() == "result = 2\n"
        assert base(old) == commit
    assert client.get("/v1/project-dependencies").json()["records"] == []


def test_readiness_does_not_recreate_a_missing_project_checkout(bridge):
    _, client, contexts, root = bridge
    dependent(client)
    verify(client, contexts, root, 1, "code.py")
    destination = root.with_name(root.name + "-preserved")
    git(integration(root), "worktree", "move", str(root), str(destination))
    report = readiness(client)
    assert not report["ready"] and report["predecessors"][0]["reason"] == "predecessor_artifacts_unavailable"
    assert not root.exists()
    assert destination.is_dir()


def test_predecessor_formal_change_cannot_cross_a_publication_effect(bridge, monkeypatch):
    service, client, contexts, root = bridge
    assert (
        put(
            client,
            "specifications",
            "SPEC-PREDECESSOR",
            {
                "title": "Prerequisite behavior",
                "status": "active",
                "type": "requirement",
                "description": "Required predecessor result",
            },
        ).status_code
        == 200
    )
    dependent(client)
    verify(client, contexts, root, 1, "code.py", spec_versions='{"SPEC-1": 1, "SPEC-PREDECESSOR": 1}')
    deliver(client, contexts, "chain-2", "pb1", 1, "NEW", work_item_id="WI-2", target_paths='["second.py"]')
    deliver(client, contexts, "chain-2", "lo1", 2, "GO", work_item_id="WI-2")
    reservation = claim(client, "chain-2", "pb3", 2, "READY", work_item_id="WI-2").json()
    fence = {"native_context_id": "pb3", "fence": reservation["fence"]}
    opened = client.post("/v1/bridge/chain-2/worktree", json=fence).json()
    (Path(opened["path"]) / "second.py").write_text("dependent_result = 3\n", encoding="utf-8")
    body = {**fence, "expected_artifacts": opened["artifact_preimages"]}
    entered, release, writer_started = Event(), Event(), Event()
    original = native_bridge.publish_context_work

    def pause(*args, **kwargs):
        entered.set()
        # Held until the concurrent amendment has been refused by the kernel's bounded lock wait (5 s) - the
        # bound covers that wait plus client round trips on a slow host; it is not a kernel timeout.
        assert release.wait(timeout=30)
        return original(*args, **kwargs)

    def amend_predecessor():
        return service.amend_specification(
            "SPEC-PREDECESSOR",
            SpecMutation(
                expected_version=1,
                actor="qualification",
                reason="Changed prerequisite intent",
                fields={"description": "A different predecessor result is required"},
            ),
        )

    def writer():
        writer_started.set()
        return amend_predecessor()

    with monkeypatch.context() as patch:
        patch.setattr(native_bridge, "publish_context_work", pause)
        with ThreadPoolExecutor(max_workers=2) as pool:
            effect = pool.submit(client.post, "/v1/bridge/chain-2/publish-work", json=body)
            assert entered.wait(timeout=10)
            change = pool.submit(writer)
            try:
                assert writer_started.wait(timeout=10)
                # The change cannot cross the effect: while the effect holds the predecessor row the kernel's
                # bounded lock wait refuses the amendment with its typed error and writes nothing.
                with pytest.raises(PostgresKernelError) as refused_change:
                    change.result(timeout=25)
                assert refused_change.value.code == "retryable_conflict", refused_change.value.message
                assert client.get("/v1/specifications/SPEC-PREDECESSOR").json()["version"] == 1
            finally:
                release.set()
            result = effect.result(timeout=15)
            assert result.status_code == 200, result.text
    # Synchronized on the effect's completion: the same amendment now acquires the row and completes.
    assert amend_predecessor()["version"] == 2
    assert (root / "second.py").read_text() == "dependent_result = 3\n"
    assert readiness(client)["predecessors"][0]["reason"] == "predecessor_scope_changed"
    refused = client.post("/v1/bridge/chain-2/publish-work", json=body)
    assert refused.json()["error"]["code"] == "work_item_dependencies_unsatisfied"
