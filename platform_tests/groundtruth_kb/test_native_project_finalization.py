"""Real Git confirmation, multi-member closure and successor-verifier recovery."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_authority_service import put, work_fields
from platform_tests.groundtruth_kb.test_native_bridge import authored, claim, deliver
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def git(root, *args, check=True):
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Qualification",
            "-c",
            "user.email=qualification@example.invalid",
            *args,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check:
        assert result.returncode == 0, result.stderr
    return result


def base(root):
    return git(root, "rev-parse", "HEAD").stdout.strip()


def integration(root):
    return Path(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()).parent


def verify(client, contexts, root, number, path):
    document = f"chain-{number}"
    work = f"WI-{number}"
    deliver(client, contexts, document, "pb1", 1, "NEW", work_item_id=work, target_paths=json.dumps([path]))
    deliver(client, contexts, document, "lo1", 2, "GO", work_item_id=work)
    reserved = claim(client, document, "pb2", 2, "READY", work_item_id=work)
    assert reserved.status_code == 200, reserved.text
    fence = {"native_context_id": "pb2", "fence": reserved.json()["fence"]}
    opened = client.post(f"/v1/bridge/{document}/worktree", json=fence)
    assert opened.status_code == 200, opened.text
    checkout = opened.json()
    (Path(checkout["path"]) / path).write_text(f"result = {number + 1}\n", encoding="utf-8")
    published = client.post(
        f"/v1/bridge/{document}/publish-work", json={**fence, "expected_artifacts": checkout["artifact_preimages"]}
    )
    assert published.status_code == 200, published.text
    assert (root / path).read_text() == f"result = {number + 1}\n"
    assert (integration(root) / path).read_text() != f"result = {number + 1}\n"
    ready = client.post(
        f"/v1/bridge/{document}/deliver",
        json={**fence, "content": authored(contexts["pb2"], document, 3, "READY", **{"Work Item": work})},
    )
    assert ready.status_code == 200, ready.text
    artifacts = client.get(f"/v1/bridge/{document}/artifacts").json()
    deliver(
        client, contexts, document, "lo2", 4, "VERIFIED", work_item_id=work, verified_artifacts=json.dumps(artifacts)
    )


def post(client, action, **body):
    return client.post(
        f"/v1/projects/PROJECT-1/{action}",
        json={
            "native_context_id": "lo3",
            "expected_version": 1,
            **body,
        },
    )


def two_members(bridge):
    _, client, contexts, root = bridge
    parent = base(root)
    assert (
        put(client, "work-items", "WI-2", work_fields(title="Second artifact"), project_id="PROJECT-1").status_code
        == 200
    )
    verify(client, contexts, root, 1, "code.py")
    assert post(client, "prepare-commit").json()["error"]["code"] == "project_not_fully_verified"
    verify(client, contexts, root, 2, "second.py")
    return client, contexts, root, parent


def commit_product(root):
    git(root, "add", "--", "code.py", "second.py", "tests/test_effect.py")
    git(root, "commit", "-m", "Complete the qualified project (WI-1) (WI-2)")
    return git(root, "rev-parse", "HEAD").stdout.strip()


def test_project_terminal_state_requires_one_complete_real_commit(bridge):
    client, _, root, parent = two_members(bridge)
    assert (
        post(client, "prepare-commit", native_context_id="pb3").json()["error"]["code"]
        == "independent_verifier_required"
    )
    ready = post(client, "prepare-commit").json()
    assert ready["status"] == "ready_to_commit" and ready["expected_parent"] == parent
    assert ready["required_citations"] == ["(WI-1)", "(WI-2)"]
    main = integration(root)
    (main / "foreign.txt").write_text("Preserve unrelated bytes\n", encoding="utf-8")
    (main / "foreign_tracked.txt").write_text("Unrelated staged bytes\n", encoding="utf-8")
    git(main, "add", "--", "foreign_tracked.txt")
    (main / "foreign_tracked.txt").write_text("Unrelated unstaged bytes\n", encoding="utf-8")
    commit = commit_product(Path(ready["checkout"]["path"]))
    assert base(main) == parent
    assert (main / "code.py").read_text() == "value = 1\n"
    response = post(client, "confirm-commit", commit_id=commit, expected_parent=parent)
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "confirmed"
    project = client.get("/v1/projects/PROJECT-1").json()["project"]
    assert project["status"] == "verified"
    memberships = client.get("/v1/projects/PROJECT-1").json()["memberships"]
    assert {(row["work_item_id"], row["status"]) for row in memberships} == {("WI-1", "active"), ("WI-2", "active")}
    for number in (1, 2):
        work = client.get(f"/v1/work-items/WI-{number}").json()["work_item"]
        assert work["completion_evidence"] == "git:" + commit
        state = client.get(f"/v1/bridge/chain-{number}/show", params={"include_content": True}).json()
        assert state["attempt"]["disposition"] == "committed"
        assert state["attempt"]["terminal_commit"] == commit
        assert state["attempt"]["verified_artifacts"] is None and "messages" not in state
    assert client.get("/v1/bridge/queue", params={"role": "lo"}).json()["eligible"] == []
    assert (
        post(client, "confirm-commit", commit_id=commit, expected_parent=parent).json()["status"] == "already_confirmed"
    )
    assert base(main) == commit
    assert (main / "foreign.txt").read_text() == "Preserve unrelated bytes\n"
    assert (main / "foreign_tracked.txt").read_text() == "Unrelated unstaged bytes\n"
    assert git(main, "show", ":foreign_tracked.txt").stdout == "Unrelated staged bytes\n"
    assert "foreign" not in git(main, "show", "--format=", "--name-only", commit).stdout


def test_changed_reviewed_bytes_requeue_only_the_affected_member(bridge):
    client, contexts, root, _ = two_members(bridge)
    (root / "code.py").write_text("corrected = 3\n", encoding="utf-8")
    result = post(client, "prepare-commit").json()
    assert result == {
        "status": "fresh_verification_required",
        "reason": "verified_bytes_changed",
        "work_item_ids": ["WI-1"],
    }
    queue = client.get("/v1/bridge/queue", params={"role": "lo"}).json()["eligible"]
    assert [row["work_item_id"] for row in queue] == ["WI-1"]
    assert client.get("/v1/work-items/WI-1").json()["work_item"]["resolution_status"] == "verified"
    artifacts = client.get("/v1/bridge/chain-1/artifacts").json()
    deliver(client, contexts, "chain-1", "lo3", 5, "VERIFIED", verified_artifacts=json.dumps(artifacts))
    assert post(client, "prepare-commit").json()["status"] == "ready_to_commit"


def test_failed_normal_git_commit_requires_fresh_verification_without_dispatcher_verdict(bridge):
    client, contexts, root, parent = two_members(bridge)
    ready = post(client, "prepare-commit").json()
    root = Path(ready["checkout"]["path"])
    hook = integration(root) / ".git/hooks/pre-commit"
    hook.write_text("#!/bin/sh\necho qualification-refusal >&2\nexit 1\n", encoding="utf-8", newline="\n")
    git(root, "add", "--", "code.py", "second.py")
    failed = git(root, "commit", "-m", "Complete project (WI-1) (WI-2)", check=False)
    assert failed.returncode != 0 and "qualification-refusal" in failed.stderr
    assert git(root, "rev-parse", "HEAD").stdout.strip() == parent
    response = post(client, "commit-failed", reason="commit_not_confirmed", evidence=failed.stderr.strip())
    assert response.status_code == 200, response.text
    assert response.json()["work_item_ids"] == ["WI-1", "WI-2"]
    for number in (1, 2):
        state = client.get(f"/v1/bridge/chain-{number}/show", params={"include_content": True}).json()
        assert [message["status"] for message in state["messages"]] == ["NEW", "GO", "READY", "VERIFIED"]
        assert json.loads(state["attempt"]["finalization_failure"])["code"] == "commit_not_confirmed"
        artifacts = client.get(f"/v1/bridge/chain-{number}/artifacts").json()
        deliver(
            client,
            contexts,
            f"chain-{number}",
            "lo3",
            5,
            "VERIFIED",
            work_item_id=f"WI-{number}",
            verified_artifacts=json.dumps(artifacts),
        )
    hook.unlink()
    assert post(client, "prepare-commit").json()["status"] == "ready_to_commit"
    commit = commit_product(root)
    assert post(client, "confirm-commit", commit_id=commit, expected_parent=parent).json()["status"] == "confirmed"


@pytest.mark.parametrize("defect", ["foreign-path", "missing-citation", "partial-product", "hook-changed-bytes"])
def test_incomplete_or_unreviewed_git_commit_cannot_mark_project_terminal(bridge, defect):
    client, _, root, parent = two_members(bridge)
    root = Path(post(client, "prepare-commit").json()["checkout"]["path"])
    paths = ["code.py", "second.py"]
    message = "Complete project (WI-1) (WI-2)"
    if defect == "foreign-path":
        (root / "unreviewed.txt").write_text("unreviewed\n", encoding="utf-8")
        paths.append("unreviewed.txt")
    elif defect == "missing-citation":
        message = "Incomplete retirement citations (WI-1)"
    elif defect == "partial-product":
        paths.remove("second.py")
    else:
        hook = integration(root) / ".git/hooks/pre-commit"
        hook.write_text(
            "#!/bin/sh\nprintf 'unreviewed = 9\\n' > code.py\ngit add -- code.py\n", encoding="utf-8", newline="\n"
        )
    git(root, "add", "--", *paths)
    git(root, "commit", "-m", message)
    commit = git(root, "rev-parse", "HEAD").stdout.strip()
    response = post(client, "confirm-commit", commit_id=commit, expected_parent=parent)
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "fresh_verification_required"
    assert base(integration(root)) == parent
    assert (integration(root) / "code.py").read_text() == "value = 1\n"
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "active"
    assert len(client.get("/v1/bridge/queue", params={"role": "lo"}).json()["eligible"]) == 2


def test_integration_overlap_is_preserved_and_recovery_reuses_the_verified_candidate(bridge):
    client, contexts, root, parent = two_members(bridge)
    ready = post(client, "prepare-commit").json()
    commit = commit_product(Path(ready["checkout"]["path"]))
    main = integration(root)
    (main / "code.py").write_text("Owner work at the same path\n", encoding="utf-8")
    failed = post(client, "confirm-commit", commit_id=commit, expected_parent=parent).json()
    assert failed["status"] == "fresh_verification_required"
    assert base(main) == parent
    assert (main / "code.py").read_text() == "Owner work at the same path\n"
    # Test owner resolves its own overlap; the service never resets those bytes.
    (main / "code.py").write_text("value = 1\n", encoding="utf-8")
    for number in (1, 2):
        artifacts = client.get(f"/v1/bridge/chain-{number}/artifacts").json()
        deliver(
            client,
            contexts,
            f"chain-{number}",
            "lo3",
            5,
            "VERIFIED",
            work_item_id=f"WI-{number}",
            verified_artifacts=json.dumps(artifacts),
        )
    assert post(client, "confirm-commit", commit_id=commit, expected_parent=parent).json()["status"] == "confirmed"
    assert base(main) == commit


def test_successor_confirms_git_fact_after_uncertain_database_acknowledgement(bridge):
    client, _, root, parent = two_members(bridge)
    ready = post(client, "prepare-commit").json()
    commit = commit_product(Path(ready["checkout"]["path"]))
    main = integration(root)
    git(main, "merge", "--ff-only", commit)
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "active"
    assert (
        client.post(
            "/v1/sessions/bind", json={"native_context_id": "fresh-confirmation", "init_command": "::init gtkb lo"}
        ).status_code
        == 200
    )
    response = post(
        client, "confirm-commit", native_context_id="fresh-confirmation", commit_id=commit, expected_parent=parent
    )
    assert response.json()["status"] == "confirmed"
    assert git(main, "rev-list", "--count", parent + "..HEAD").stdout.strip() == "1"
