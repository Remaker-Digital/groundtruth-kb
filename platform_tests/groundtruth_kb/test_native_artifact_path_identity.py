"""Concrete path identities cannot alias or expand the independently reviewed scope."""

from __future__ import annotations

import json

import pytest
from psycopg import sql
from psycopg.types.json import Jsonb

from platform_tests.groundtruth_kb.bridge_fixtures import authored, claim, deliver
from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]

UNSAFE = [
    "../outside.py",
    ".git/config",
    "scripts/*.py",
    "scripts/",
    " scripts/leading.py",
    "scripts/back\\slash.py",
    "scripts/CON.txt",
    "scripts/CON .txt",
    "scripts/trailing.py ",
    "scripts/trailing-dot.",
    "scripts/name?.py",
    "scripts/AUX.py",
    "scripts/com1.log",
    "scripts/LPT9",
    "scripts/NUL",
    "scripts/CONIN$",
    "scripts/CONOUT$.txt",
    "scripts/COM¹.txt",
    "scripts/ leading.py",
    "scripts/name:stream",
    "scripts/a|b.py",
    'scripts/a"b.py',
    "scripts/<part>.py",
]
COLLISIONS = [
    ["scripts/same.py", "scripts/same.py"],
    ["Scripts/Authority.py", "scripts/authority.py"],
    ["scripts/é.py", "scripts/e\u0301.py"],
]


@pytest.mark.parametrize("field", ["target_paths", "test_artifact_targets"])
def test_native_proposal_refuses_ambiguous_paths_without_consuming_claim(bridge, field):
    _, client, contexts, root = bridge
    document = "path-identity"
    reserved = claim(client, document, "pb1", 0, "NEW").json()
    fence = {"native_context_id": "pb1", "fence": reserved["fence"]}
    original = (root / "code.py").read_bytes()
    before = client.get(f"/v1/bridge/{document}/show", params={"include_content": True}).json()
    for paths in [[value] for value in UNSAFE] + COLLISIONS:
        response = client.post(
            f"/v1/bridge/{document}/deliver",
            json={**fence, "content": authored(contexts["pb1"], document, 1, "NEW", **{field: json.dumps(paths)})},
        )
        assert response.status_code == 422, (paths, response.text)
        assert response.json()["error"]["code"] == "invalid_bridge_header", (paths, response.text)
        assert client.get(f"/v1/bridge/{document}/show", params={"include_content": True}).json() == before
        assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 200
        assert (root / "code.py").read_bytes() == original
    content = authored(contexts["pb1"], document, 1, "NEW")
    accepted = client.post(f"/v1/bridge/{document}/deliver", json={**fence, "content": content})
    assert accepted.status_code == 200, accepted.text
    stored = client.get(f"/v1/bridge/{document}/show", params={"include_content": True}).json()
    assert stored["messages"][0]["content"] == content


def test_native_scope_collisions_across_source_and_test_lists_refuse(bridge):
    _, client, contexts, _ = bridge
    document = "combined-path-identity"
    reserved = claim(client, document, "pb1", 0, "NEW").json()
    fence = {"native_context_id": "pb1", "fence": reserved["fence"]}
    for first, second in COLLISIONS[1:]:
        response = client.post(
            f"/v1/bridge/{document}/deliver",
            json={
                **fence,
                "content": authored(
                    contexts["pb1"],
                    document,
                    1,
                    "NEW",
                    target_paths=json.dumps([first]),
                    test_artifact_targets=json.dumps([second]),
                ),
            },
        )
        assert response.status_code == 422 and response.json()["error"]["code"] == "invalid_bridge_header", (
            response.text
        )
    # The same exact artifact can intentionally be both source and test scope.
    content = authored(contexts["pb1"], document, 1, "NEW", target_paths='["code.py","tests/test_effect.py"]')
    result = client.post(f"/v1/bridge/{document}/deliver", json={**fence, "content": content})
    assert result.status_code == 200, result.text


@pytest.mark.parametrize("field", ["proposal_paths", "test_targets"])
def test_native_effect_boundary_rechecks_stored_noncanonical_scope(bridge, field):
    service, client, contexts, root = bridge
    document = "stored-path-identity"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    deliver(client, contexts, document, "lo1", 2, "GO")
    reserved = claim(client, document, "pb2", 2, "READY").json()
    fence = {"native_context_id": "pb2", "fence": reserved["fence"]}
    original = (root / "code.py").read_bytes()
    for paths in [[value] for value in UNSAFE] + COLLISIONS:
        with service.kernel.transaction() as tx:
            tx.cursor.execute(
                sql.SQL("UPDATE {}.bridge_attempts SET {}=%s WHERE id=%s").format(
                    sql.Identifier(tx.schema), sql.Identifier(field)
                ),
                (Jsonb(paths), document),
            )
        refused = client.post(f"/v1/bridge/{document}/check", json=fence)
        assert refused.status_code == 422 and refused.json()["error"]["code"] == "scope_changed", (paths, refused.text)
        assert (root / "code.py").read_bytes() == original
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("UPDATE {}.bridge_attempts SET {}=%s WHERE id=%s").format(
                sql.Identifier(tx.schema), sql.Identifier(field)
            ),
            (Jsonb(["code.py"] if field == "proposal_paths" else ["tests/test_effect.py"]), document),
        )
    assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 200


def test_literal_bracket_filename_mode_transfer_preserves_both_blob_identities(tmp_path):
    import subprocess

    from groundtruth_kb.session.worktree import _apply_artifact_modes, _artifact_modes

    def git(*args):
        return subprocess.check_output(
            ["git", "--literal-pathspecs", "-C", str(tmp_path), *args], stderr=subprocess.PIPE, text=True
        ).strip()

    git("init")
    git("config", "user.name", "Qualification")
    git("config", "user.email", "qualification@example.invalid")
    git("config", "core.filemode", "false")
    target = "a[1].py"
    foreign = "a1.py"
    (tmp_path / target).write_text("reviewed_literal = 1\n", encoding="utf-8")
    (tmp_path / foreign).write_text("unrelated = 2\n", encoding="utf-8")
    git("add", "--", target, foreign)
    git("commit", "-m", "Disposable bracket filename preimage")
    target_blob = git("rev-parse", "HEAD:" + target)
    foreign_before = git("ls-files", "--stage", "--", foreign)
    head = git("rev-parse", "HEAD")
    _apply_artifact_modes(tmp_path, {target: {"mode": "100755", "object_id": target_blob}})
    assert git("ls-files", "--stage", "--", target) == f"100755 {target_blob} 0\t{target}"
    assert git("ls-files", "--stage", "--", foreign) == foreign_before
    assert _artifact_modes(tmp_path, [target, foreign]) == {target: "100755", foreign: "100644"}
    assert (tmp_path / target).read_text() == "reviewed_literal = 1\n"
    assert (tmp_path / foreign).read_text() == "unrelated = 2\n"
    assert git("rev-parse", "HEAD") == head


def test_large_mode_scope_ignores_foreign_conflict_and_preserves_the_index(tmp_path):
    import subprocess

    from groundtruth_kb.session.worktree import SessionWorktreeError, _artifact_modes

    def git(*args, input=None):
        return (
            subprocess.run(
                ["git", "--literal-pathspecs", "-C", str(tmp_path), *args],
                input=input.encode("utf-8") if input is not None else None,
                capture_output=True,
                check=True,
            )
            .stdout.decode("utf-8")
            .strip()
        )

    git("init")
    git("config", "core.filemode", "false")
    paths = [f"artifact scope/{i:04d}-{'reviewed' * 8}.py" for i in range(600)]
    assert len(subprocess.list2cmdline(["git", "ls-files", "--stage", "-z", "--", *paths])) > 32767
    (tmp_path / "artifact scope").mkdir()
    for path in paths:
        (tmp_path / path).write_bytes(b"reviewed = True\n")
    foreign = "foreign.py"
    (tmp_path / foreign).write_bytes(b"foreign bytes\n")
    git("add", "--all")
    git("update-index", "--chmod=+x", "--", paths[0])
    blob = git("hash-object", "--", foreign)
    git("update-index", "--force-remove", "--", foreign)
    git("update-index", "--index-info", input=f"100644 {blob} 2\t{foreign}\n100755 {blob} 3\t{foreign}\n")
    assert git("ls-files", "--stage", "--", foreign).splitlines() == [
        f"100644 {blob} 2\t{foreign}",
        f"100755 {blob} 3\t{foreign}",
    ]
    before = (tmp_path / ".git/index").read_bytes()

    modes = _artifact_modes(tmp_path, paths)
    assert modes == {path: "100755" if path == paths[0] else "100644" for path in paths}
    with pytest.raises(SessionWorktreeError, match="unmerged"):
        _artifact_modes(tmp_path, [foreign])
    assert (tmp_path / ".git/index").read_bytes() == before
    assert (tmp_path / foreign).read_bytes() == b"foreign bytes\n"
