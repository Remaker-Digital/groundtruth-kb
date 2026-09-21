"""Publication must refuse redirected inputs and targets before any effect."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from platform_tests.groundtruth_kb.bridge_fixtures import authored, claim, deliver
from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.native_fixtures import native as native
from platform_tests.groundtruth_kb.native_fixtures import put, work_fields

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def _publication(bridge):
    _, client, contexts, root = bridge
    document = "publication-redirect"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    deliver(client, contexts, document, "lo1", 2, "GO")
    reserved = claim(client, document, "pb2", 2, "READY").json()
    fence = {"native_context_id": "pb2", "fence": reserved["fence"]}
    opened = client.post(f"/v1/bridge/{document}/worktree", json=fence)
    assert opened.status_code == 200, opened.text
    checkout = Path(opened.json()["path"])
    (checkout / "code.py").write_bytes(b"value = 2\n")
    (checkout / "tests/test_effect.py").write_bytes(b"assert 2 == 2\n")
    return client, document, root, checkout, {**fence, "expected_artifacts": opened.json()["artifact_preimages"]}


def _assert_refused_without_effect(client, document, root, checkout, request):
    paths = [
        base / name for base in [root, checkout] for name in ["code.py", "tests/test_effect.py", "foreign_tracked.txt"]
    ]
    before = {str(path): path.read_bytes() for path in paths}
    indexes = {
        str(base): subprocess.check_output(["git", "-C", str(base), "ls-files", "--stage", "-z"])
        for base in [root, checkout]
    }
    state = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    response = client.post(f"/v1/bridge/{document}/publish-work", json=request)
    assert response.status_code == 422, response.text
    assert response.json()["error"]["code"] == "artifact_path_redirected"
    assert {str(path): path.read_bytes() for path in paths} == before
    assert {
        str(base): subprocess.check_output(["git", "-C", str(base), "ls-files", "--stage", "-z"])
        for base in [root, checkout]
    } == indexes
    assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == state
    assert (
        client.post(
            f"/v1/bridge/{document}/check", json={key: request[key] for key in ["native_context_id", "fence"]}
        ).status_code
        == 200
    )


@pytest.mark.parametrize("side", ["source", "destination"])
def test_publication_refuses_real_in_root_directory_redirect_before_any_write(bridge, side):
    client, document, root, checkout, request = _publication(bridge)
    target_root = checkout if side == "source" else root
    linked = target_root / "tests"
    preserved = target_root / "foreign-tests"
    assert linked.resolve().is_relative_to(target_root.resolve())
    assert preserved.resolve().is_relative_to(target_root.resolve())
    linked.rename(preserved)
    if os.name == "nt":
        command = (
            "New-Item -ItemType Junction -Path '"
            + str(linked).replace("'", "''")
            + "' -Target '"
            + str(preserved).replace("'", "''")
            + "' | Out-Null"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command], check=True, capture_output=True
        )
        assert linked.is_junction()
    else:
        linked.symlink_to(preserved, target_is_directory=True)
        assert linked.is_symlink()
    original = (preserved / "test_effect.py").read_bytes()
    _assert_refused_without_effect(client, document, root, checkout, request)
    assert (preserved / "test_effect.py").read_bytes() == original


@pytest.mark.parametrize("side", ["source", "destination"])
@pytest.mark.parametrize("kind", ["file_symlink", "parent_symlink", "parent_junction"])
def test_publication_refuses_redirected_path_components_without_link_privileges(bridge, monkeypatch, side, kind):
    client, document, root, checkout, request = _publication(bridge)
    target_root = checkout if side == "source" else root
    redirected = target_root / ("tests/test_effect.py" if kind == "file_symlink" else "tests")
    method = "is_junction" if kind == "parent_junction" else "is_symlink"
    original = getattr(Path, method)
    monkeypatch.setattr(Path, method, lambda path: path == redirected or original(path))
    _assert_refused_without_effect(client, document, root, checkout, request)


def test_verdict_cannot_reuse_another_attempt_claim_or_predecessor(bridge):
    _, client, contexts, _ = bridge
    assert put(client, "work-items", "WI-2", work_fields(), project_id="PROJECT-1").status_code == 200
    held = {}
    for document, work in [("first-verdict", "WI-1"), ("second-verdict", "WI-2")]:
        deliver(client, contexts, document, "pb1", 1, "NEW", work_item_id=work)
        reservation = claim(client, document, "lo1", 1, "GO", work_item_id=work)
        assert reservation.status_code == 200, reservation.text
        held[document] = {
            "native_context_id": "lo1",
            "fence": reservation.json()["fence"],
            "content": authored(contexts["lo1"], document, 2, "GO", **{"Work Item": work}),
        }
    first, second = held["first-verdict"], held["second-verdict"]
    before = {document: client.get(f"/v1/bridge/{document}/show?include_content=true").json() for document in held}
    for request, code in [
        ({**first, "fence": second["fence"]}, "stale_artifact_fence"),
        ({**first, "content": second["content"]}, "invalid_bridge_header"),
        ({**first, "content": first["content"].replace("Version: 2", "Version: 3")}, "claim_does_not_match_artifact"),
    ]:
        refused = client.post("/v1/bridge/first-verdict/deliver", json=request)
        assert refused.status_code == 422, refused.text
        assert refused.json()["error"]["code"] == code
        assert {
            document: client.get(f"/v1/bridge/{document}/show?include_content=true").json() for document in held
        } == before
    for document, request in held.items():
        assert client.post(f"/v1/bridge/{document}/deliver", json=request).status_code == 200
        assert (
            client.get(f"/v1/bridge/{document}/show?include_content=true").json()["messages"][-1]["content"]
            == request["content"]
        )
