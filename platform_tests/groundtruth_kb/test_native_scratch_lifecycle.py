"""Scratch lifecycle teardown on the immutable binding (SPEC-0452 v2, TEST-12212 v2).

The verb removes exactly the bound context's ``scratchpad/<session-context-id>``
directory under the service's project root. Unbound contexts, redirected roots
and non-directory paths are refused without deletion; links inside the
directory are unlinked without being followed; entries the host refuses to
delete are reported as surviving with a ``partial`` outcome. The binding and
formal history never change. These cases run the in-process authority; the
close/wrap contract module runs the verb through a separate CLI process.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.native_fixtures import history_count
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def _link(link: Path, target: Path) -> None:
    """Create a directory link the way a host would: a junction on Windows, a symlink elsewhere."""
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], check=True, capture_output=True)
    else:
        link.symlink_to(target, target_is_directory=True)


def _remove_link(link: Path) -> None:
    """Remove a directory link entry the way a host would, never its target."""
    if os.name == "nt":
        link.rmdir()
    else:
        link.unlink()


def _snapshot(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def _teardown(client, context):
    return client.post("/v1/sessions/scratch-teardown", json={"native_context_id": context})


def _populate(own: Path) -> list[dict[str, str]]:
    (own / "nested" / "deeper").mkdir(parents=True)
    (own / "draft.md").write_text("draft", encoding="utf-8")
    (own / "nested" / "notes.txt").write_text("notes", encoding="utf-8")
    (own / "nested" / "deeper" / "empty.bin").write_bytes(b"")
    return [
        {"path": "draft.md", "kind": "file"},
        {"path": "nested/deeper/empty.bin", "kind": "file"},
        {"path": "nested/deeper", "kind": "directory"},
        {"path": "nested/notes.txt", "kind": "file"},
        {"path": "nested", "kind": "directory"},
        {"path": ".", "kind": "directory"},
    ]


def test_teardown_removes_exactly_the_bound_context_directory_and_is_idempotent(bridge):
    service, client, contexts, work_root = bridge
    root = work_root.parents[2]
    own = root / "scratchpad" / contexts["pb1"]["session_context_id"]
    sibling = root / "scratchpad" / contexts["lo1"]["session_context_id"]
    expected = _populate(own)
    (sibling / "kept").mkdir(parents=True)
    (sibling / "kept" / "other.md").write_text("another context's work", encoding="utf-8")
    (root / "scratchpad" / "unrelated.txt").write_text("not a context directory", encoding="utf-8")
    before_tree = {k: v for k, v in _snapshot(root).items() if not k.startswith(own.relative_to(root).as_posix())}
    binding = client.get("/v1/sessions/binding", params={"native_context_id": "pb1"}).json()
    history = history_count(service)

    result = _teardown(client, "pb1")
    assert result.status_code == 200, result.text
    report = result.json()
    assert report["status"] == "removed"
    assert report["session_context_id"] == contexts["pb1"]["session_context_id"]
    assert Path(report["scratch_directory"]) == own
    assert report["removed"] == expected
    assert report["surviving"] == []
    assert "recovery_route" not in report
    assert not own.exists() and not own.is_symlink()
    assert _snapshot(root) == before_tree
    assert (sibling / "kept" / "other.md").read_text(encoding="utf-8") == "another context's work"

    # The binding is attribution, not a lifetime: it survives teardown unchanged and
    # the context can still be checked against its (now absent) scratch scope.
    assert client.get("/v1/sessions/binding", params={"native_context_id": "pb1"}).json() == binding
    assert history_count(service) == history
    effect = client.post(
        "/v1/bridge/check-effects",
        json={"native_context_id": "pb1", "cwd": str(root), "paths": [str(own / "later.md")]},
    )
    assert effect.status_code == 200 and effect.json()["scope"] == "scratch"

    # A repeated teardown is a typed no-op that creates nothing.
    again = _teardown(client, "pb1")
    assert again.status_code == 200, again.text
    assert again.json() == {
        "status": "absent",
        "session_context_id": contexts["pb1"]["session_context_id"],
        "scratch_directory": str(own),
        "removed": [],
        "surviving": [],
    }
    assert not own.exists()
    # A context that never created scratch is the same no-op, before and after the scratch root exists.
    assert _teardown(client, "pb2").json()["status"] == "absent"
    assert not (root / "scratchpad" / contexts["pb2"]["session_context_id"]).exists()
    assert _snapshot(root) == before_tree
    assert history_count(service) == history


def test_teardown_refuses_unbound_redirected_and_non_directory_scratch_without_deleting(bridge):
    _service, client, contexts, work_root = bridge
    root = work_root.parents[2]
    scratch = root / "scratchpad"
    own = scratch / contexts["pb1"]["session_context_id"]
    sibling = scratch / contexts["lo1"]["session_context_id"]
    (sibling / "kept").mkdir(parents=True)
    (sibling / "kept" / "other.md").write_text("another context's work", encoding="utf-8")
    before = _snapshot(root)

    unbound = _teardown(client, "never-bound")
    assert unbound.status_code == 422, unbound.text
    assert unbound.json()["error"]["code"] == "no_session_binding"
    for payload in ({}, {"native_context_id": ""}, {"native_context_id": "pb1", "path": str(sibling)}):
        assert client.post("/v1/sessions/scratch-teardown", json=payload).status_code == 422

    # The own path is a link to another context: refused, target untouched.
    _link(own, sibling)
    try:
        redirected = _teardown(client, "pb1")
        assert redirected.status_code == 422, redirected.text
        assert redirected.json()["error"]["code"] == "effect_path_redirected"
        assert redirected.json()["error"]["details"]["scratch_directory"] == str(own)
        assert own.is_dir() and (own / "kept" / "other.md").is_file()
    finally:
        _remove_link(own)
    assert not own.exists()
    assert _snapshot(root) == before

    # The scratch root itself is a link (to the project root): refused before any walk.
    elsewhere = root.parent / (root.name + "-scratch-target")
    elsewhere.mkdir()
    (elsewhere / contexts["pb1"]["session_context_id"]).mkdir()
    (elsewhere / contexts["pb1"]["session_context_id"] / "outside.md").write_text("outside", encoding="utf-8")
    moved = root / "scratchpad-moved"
    scratch.rename(moved)
    _link(scratch, elsewhere)
    try:
        redirected_root = _teardown(client, "pb1")
        assert redirected_root.status_code == 422, redirected_root.text
        assert redirected_root.json()["error"]["code"] == "effect_path_redirected"
        assert (elsewhere / contexts["pb1"]["session_context_id"] / "outside.md").read_text(
            encoding="utf-8"
        ) == "outside"
    finally:
        _remove_link(scratch)
        moved.rename(scratch)
    assert _snapshot(root) == before

    # A regular file at the own path is not a scratch directory: refused, preserved.
    own.write_text("not a directory", encoding="utf-8")
    not_directory = _teardown(client, "pb1")
    assert not_directory.status_code == 422, not_directory.text
    assert not_directory.json()["error"]["code"] == "invalid_scratch_directory"
    assert own.read_text(encoding="utf-8") == "not a directory"
    own.unlink()
    assert _snapshot(root) == before


def test_teardown_unlinks_links_inside_the_directory_without_following_them(bridge):
    _service, client, contexts, work_root = bridge
    root = work_root.parents[2]
    scratch = root / "scratchpad"
    own = scratch / contexts["pb1"]["session_context_id"]
    sibling = scratch / contexts["lo1"]["session_context_id"]
    (sibling / "kept").mkdir(parents=True)
    (sibling / "kept" / "other.md").write_text("another context's work", encoding="utf-8")
    (own / "nested").mkdir(parents=True)
    (own / "nested" / "mine.md").write_text("mine", encoding="utf-8")
    _link(own / "nested" / "to-sibling", sibling / "kept")
    _link(own / "to-root", root)
    if os.name != "nt":
        (own / "file-link").symlink_to(root / "code.py")
    sibling_before = _snapshot(sibling)
    code_before = (root / "code.py").read_bytes()

    result = _teardown(client, "pb1")
    assert result.status_code == 200, result.text
    report = result.json()
    assert report["status"] == "removed" and report["surviving"] == []
    kinds = {entry["path"]: entry["kind"] for entry in report["removed"]}
    assert kinds["nested/to-sibling"] == "link" and kinds["to-root"] == "link"
    assert kinds["nested/mine.md"] == "file" and kinds["nested"] == "directory" and kinds["."] == "directory"
    if os.name != "nt":
        assert kinds["file-link"] == "link"
    assert not own.exists() and not own.is_symlink()
    assert _snapshot(sibling) == sibling_before
    assert (root / "code.py").read_bytes() == code_before
    assert (root / "second.py").is_file() and (root / "tests" / "test_effect.py").is_file()


def test_teardown_reports_surviving_entries_as_partial_and_completes_on_rerun(bridge, monkeypatch):
    service, client, contexts, work_root = bridge
    root = work_root.parents[2]
    own = root / "scratchpad" / contexts["pb1"]["session_context_id"]
    (own / "held").mkdir(parents=True)
    (own / "held" / "open.log").write_text("held by a process", encoding="utf-8")
    (own / "free.md").write_text("free", encoding="utf-8")
    (own / "unreadable").mkdir()
    (own / "unreadable" / "hidden.md").write_text("hidden", encoding="utf-8")
    history = history_count(service)
    real_scandir = os.scandir

    def interrupted_scandir(path=".", *args, **kwargs):
        # One directory listing fails mid-walk, as an interrupted or denied read would.
        if Path(path) == own / "unreadable":
            raise OSError(5, "Listing interrupted")
        return real_scandir(path, *args, **kwargs)

    monkeypatch.setattr(os, "scandir", interrupted_scandir)
    if os.name == "nt":
        handle = (own / "held" / "open.log").open("rb")
    else:
        (own / "held").chmod(0o500)
    try:
        result = _teardown(client, "pb1")
        assert result.status_code == 200, result.text
        report = result.json()
        assert report["status"] == "partial"
        assert "rerun gt session scratch-teardown" in report["recovery_route"]
        surviving = {entry["path"]: entry for entry in report["surviving"]}
        assert surviving["held/open.log"]["reason"] == "PermissionError"
        assert surviving["held/open.log"]["kind"] == "file"
        assert surviving["unreadable"]["reason"] == "OSError" and surviving["unreadable"]["errno"] == 5
        assert set(surviving) == {"held/open.log", "unreadable"}
        removed = {entry["path"] for entry in report["removed"]}
        assert removed == {"free.md"}
        assert own.is_dir() and (own / "held" / "open.log").is_file()
        assert (own / "unreadable" / "hidden.md").read_text(encoding="utf-8") == "hidden"
        assert not (own / "free.md").exists()
    finally:
        if os.name == "nt":
            handle.close()
        else:
            (own / "held").chmod(0o700)
    monkeypatch.setattr(os, "scandir", real_scandir)
    assert history_count(service) == history

    # The held handle is closed and the listing is readable again: the rerun removes only what remained.
    rerun = _teardown(client, "pb1")
    assert rerun.status_code == 200, rerun.text
    assert rerun.json()["status"] == "removed"
    assert {entry["path"] for entry in rerun.json()["removed"]} == {
        "held/open.log",
        "held",
        "unreadable/hidden.md",
        "unreadable",
        ".",
    }
    assert not own.exists()
    assert history_count(service) == history
