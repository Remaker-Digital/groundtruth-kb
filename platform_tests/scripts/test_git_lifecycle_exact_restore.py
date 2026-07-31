"""Integration coverage for exact-path tracked-file restoration."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from groundtruth_kb.git_lifecycle.models import OperationDenied
from groundtruth_kb.git_lifecycle.service import GitLifecycleService

ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "groundtruth-kb" / "src"
TEMP_ROOT = ROOT / ".gtkb-state" / "tests" / "git-lifecycle-exact-restore"


def _git(
    repo: Path,
    *args: str,
    input_text: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        input=input_text.encode("ascii") if input_text is not None else None,
        capture_output=True,
    )
    if check and completed.returncode != 0:
        raise AssertionError((completed.stdout + completed.stderr).decode("utf-8", errors="replace"))
    return completed


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _commit_all(repo: Path, message: str) -> str:
    _git(repo, "add", "--all")
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD").stdout.decode("ascii").strip()


def _seed(repo: Path) -> str:
    _write(repo / "bridge" / "target.md", "target-v1\n")
    _write(repo / "staged.txt", "staged-v1\n")
    _write(repo / "modified.txt", "modified-v1\n")
    _write(repo / "deleted.txt", "deleted-v1\n")
    return _commit_all(repo, "seed")


def _cli(
    repo: Path,
    *args: str,
    as_json: bool = True,
) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SOURCE_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    command = [sys.executable, "-m", "groundtruth_kb.git_lifecycle"]
    if as_json:
        command.append("--json")
    command.extend(args)
    return subprocess.run(
        command,
        cwd=repo,
        capture_output=True,
        text=True,
        env=env,
    )


def _json_result(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    stream = result.stdout if result.returncode == 0 else result.stderr
    return json.loads(stream)


def _target_status(repo: Path) -> bytes:
    return _git(
        repo,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
        "--",
        ":(top,literal)bridge/target.md",
    ).stdout


def _unrelated_status(repo: Path) -> bytes:
    return _git(
        repo,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
        "--",
        ".",
        ":(top,exclude,literal)bridge/target.md",
    ).stdout


def _index(repo: Path) -> bytes:
    return _git(repo, "ls-files", "--stage", "-z").stdout


@pytest.fixture
def repo() -> Iterator[Path]:
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="wi5474-", dir=TEMP_ROOT) as temporary:
        path = Path(temporary)
        _git(path, "init")
        _git(path, "config", "user.name", "GT-KB Test")
        _git(path, "config", "user.email", "gtkb-test@example.invalid")
        _git(path, "config", "core.autocrlf", "false")
        yield path


def test_cli_restores_exact_blob_and_preserves_unrelated_state(repo: Path) -> None:
    head = _seed(repo)
    _write(repo / "staged.txt", "staged-v2\n")
    _git(repo, "add", "staged.txt")
    _write(repo / "modified.txt", "modified-v2\n")
    (repo / "deleted.txt").unlink()
    _write(repo / "untracked.txt", "untracked\n")
    (repo / "bridge" / "target.md").unlink()
    unrelated_before = _unrelated_status(repo)
    index_before = _index(repo)

    result = _cli(
        repo,
        "restore-deleted-path",
        "--path",
        "bridge/target.md",
        "--source-ref",
        "HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = _json_result(result)
    assert payload["status"] == "PASS"
    assert payload["code"] == "tracked_path_restored"
    assert payload["source_commit"] == head
    assert payload["source_blob"] == payload["restored_blob"]
    assert payload["target_status_before"] == [" D bridge/target.md"]
    assert payload["target_status_after"] == []
    assert payload["unrelated_status_hash_before"] == payload["unrelated_status_hash_after"]
    assert payload["index_hash_before"] == payload["index_hash_after"]
    assert (repo / "bridge" / "target.md").read_bytes() == b"target-v1\n"
    assert _unrelated_status(repo) == unrelated_before
    assert _index(repo) == index_before
    assert _git(repo, "rev-parse", "HEAD").stdout.decode("ascii").strip() == head


def test_cli_restores_from_different_explicit_commit(repo: Path) -> None:
    first = _seed(repo)
    _write(repo / "bridge" / "target.md", "target-v2\n")
    _commit_all(repo, "target v2")
    (repo / "bridge" / "target.md").unlink()

    result = _cli(
        repo,
        "restore-deleted-path",
        "--path",
        "bridge/target.md",
        "--source-ref",
        first,
    )

    assert result.returncode == 0, result.stderr
    payload = _json_result(result)
    assert payload["source_commit"] == first
    assert payload["target_status_after"] == [" M bridge/target.md"]
    assert (repo / "bridge" / "target.md").read_bytes() == b"target-v1\n"


@pytest.mark.parametrize(
    "unsafe_path",
    [
        "",
        ".",
        "./.",
        "././.",
        ".\\.",
        "../target.md",
        ".git/config",
        "C:/target.md",
        "/target.md",
        "*.md",
        "bridge/{target,other}.md",
        "bridge/target.md,bridge/other.md",
        "bridge/target md",
    ],
)
def test_cli_denies_unsafe_or_multipath_input(repo: Path, unsafe_path: str) -> None:
    _seed(repo)
    (repo / "bridge" / "target.md").unlink()
    target_before = _target_status(repo)
    unrelated_before = _unrelated_status(repo)
    index_before = _index(repo)

    result = _cli(
        repo,
        "restore-deleted-path",
        "--path",
        unsafe_path,
        "--source-ref",
        "HEAD",
    )

    assert result.returncode == 2
    assert _json_result(result)["code"] == "unsafe_scope_path"
    assert "Traceback" not in result.stderr
    assert not (repo / "bridge" / "target.md").exists()
    assert _target_status(repo) == target_before
    assert _unrelated_status(repo) == unrelated_before
    assert _index(repo) == index_before


def test_cli_denies_repeated_path_or_source_ref(repo: Path) -> None:
    _seed(repo)
    (repo / "bridge" / "target.md").unlink()

    repeated_path = _cli(
        repo,
        "restore-deleted-path",
        "--path",
        "bridge/target.md",
        "--path",
        "other.md",
        "--source-ref",
        "HEAD",
    )
    repeated_ref = _cli(
        repo,
        "restore-deleted-path",
        "--path",
        "bridge/target.md",
        "--source-ref",
        "HEAD",
        "--source-ref",
        "HEAD~0",
    )
    repeated_dry_run = _cli(
        repo,
        "--dry-run",
        "restore-deleted-path",
        "--path",
        "bridge/target.md",
        "--path",
        "other.md",
        "--source-ref",
        "HEAD",
    )

    assert repeated_path.returncode == 2
    assert repeated_ref.returncode == 2
    assert repeated_dry_run.returncode == 2
    assert _json_result(repeated_path)["code"] == "cli_argument_count_invalid"
    assert _json_result(repeated_ref)["code"] == "cli_argument_count_invalid"
    assert _json_result(repeated_dry_run)["code"] == "cli_argument_count_invalid"
    assert not (repo / "bridge" / "target.md").exists()


@pytest.mark.parametrize(
    "state",
    ["clean", "modified", "staged-modified", "staged-deleted", "renamed", "untracked", "conflict"],
)
def test_cli_denies_any_target_state_except_unstaged_deletion(repo: Path, state: str) -> None:
    _seed(repo)
    source_ref = "HEAD"
    target = repo / "bridge" / "target.md"
    if state == "modified":
        _write(target, "modified\n")
    elif state == "staged-modified":
        _write(target, "modified\n")
        _git(repo, "add", "bridge/target.md")
    elif state == "staged-deleted":
        _git(repo, "rm", "bridge/target.md")
    elif state == "renamed":
        _git(repo, "mv", "bridge/target.md", "bridge/renamed.md")
    elif state == "untracked":
        _git(repo, "rm", "--cached", "bridge/target.md")
        _git(repo, "commit", "-m", "untrack target")
        source_ref = "HEAD~1"
    elif state == "conflict":
        target.unlink()
        _git(repo, "rm", "--cached", "bridge/target.md")
        blobs = []
        for content in ("base\n", "ours\n", "theirs\n"):
            blobs.append(_git(repo, "hash-object", "-w", "--stdin", input_text=content).stdout.decode("ascii").strip())
        index_info = "".join(f"100644 {blob} {stage}\tbridge/target.md\n" for stage, blob in enumerate(blobs, start=1))
        _git(repo, "update-index", "--index-info", input_text=index_info)

    result = _cli(
        repo,
        "restore-deleted-path",
        "--path",
        "bridge/target.md",
        "--source-ref",
        source_ref,
    )

    assert result.returncode == 2
    assert _json_result(result)["code"] == "restore_target_not_unstaged_deletion"


@pytest.mark.parametrize("source_kind", ["unknown", "noncommit", "ambiguous"])
def test_cli_denies_unknown_noncommit_or_ambiguous_source_ref(repo: Path, source_kind: str) -> None:
    first = _seed(repo)
    if source_kind == "unknown":
        source_ref = "refs/heads/does-not-exist"
    elif source_kind == "noncommit":
        source_ref = _git(repo, "hash-object", "-w", "--stdin", input_text="blob\n").stdout.decode("ascii").strip()
    else:
        _git(repo, "tag", "duplicate", first)
        _write(repo / "later.txt", "later\n")
        _commit_all(repo, "later")
        _git(repo, "branch", "duplicate", "HEAD")
        source_ref = "duplicate"
    (repo / "bridge" / "target.md").unlink()

    result = _cli(
        repo,
        "restore-deleted-path",
        "--path",
        "bridge/target.md",
        "--source-ref",
        source_ref,
    )

    assert result.returncode == 2
    assert _json_result(result)["code"] == "source_ref_not_commit"
    assert not (repo / "bridge" / "target.md").exists()


def test_cli_denies_source_commit_without_target_path(repo: Path) -> None:
    _write(repo / "before.txt", "before\n")
    before = _commit_all(repo, "before target")
    _write(repo / "bridge" / "target.md", "target\n")
    _commit_all(repo, "add target")
    (repo / "bridge" / "target.md").unlink()

    result = _cli(
        repo,
        "restore-deleted-path",
        "--path",
        "bridge/target.md",
        "--source-ref",
        before,
    )

    assert result.returncode == 2
    assert _json_result(result)["code"] == "source_path_missing"
    assert not (repo / "bridge" / "target.md").exists()


def test_service_removes_target_when_restored_bytes_mismatch(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(repo)
    target = repo / "bridge" / "target.md"
    target.unlink()
    service = GitLifecycleService.for_testing(repo)
    original = service.repo.restore_worktree_blob

    def corrupt(path: str, payload: bytes) -> None:
        original(path, payload + b"corrupt")

    monkeypatch.setattr(service.repo, "restore_worktree_blob", corrupt)
    with pytest.raises(OperationDenied) as denied:
        service.restore_deleted_path(path="bridge/target.md", source_ref="HEAD")

    assert denied.value.code == "restored_blob_mismatch"
    assert not target.exists()


def test_service_removes_target_when_index_changes(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(repo)
    target = repo / "bridge" / "target.md"
    target.unlink()
    service = GitLifecycleService.for_testing(repo)
    original = service.repo.restore_worktree_blob

    def mutate_index(path: str, payload: bytes) -> None:
        original(path, payload)
        _write(repo / "staged.txt", "index-drift\n")
        _git(repo, "add", "staged.txt")

    monkeypatch.setattr(service.repo, "restore_worktree_blob", mutate_index)
    with pytest.raises(OperationDenied) as denied:
        service.restore_deleted_path(path="bridge/target.md", source_ref="HEAD")

    assert denied.value.code == "restore_index_changed"
    assert not target.exists()


def test_service_removes_target_when_unrelated_status_changes(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(repo)
    target = repo / "bridge" / "target.md"
    target.unlink()
    service = GitLifecycleService.for_testing(repo)
    original = service.repo.restore_worktree_blob

    def mutate_unrelated(path: str, payload: bytes) -> None:
        original(path, payload)
        _write(repo / "new-unrelated.txt", "drift\n")

    monkeypatch.setattr(service.repo, "restore_worktree_blob", mutate_unrelated)
    with pytest.raises(OperationDenied) as denied:
        service.restore_deleted_path(path="bridge/target.md", source_ref="HEAD")

    assert denied.value.code == "restore_unrelated_status_changed"
    assert not target.exists()


def test_cli_human_result_and_denial_are_actionable(repo: Path) -> None:
    _seed(repo)
    clean_denial = _cli(
        repo,
        "restore-deleted-path",
        "--path",
        "bridge/target.md",
        "--source-ref",
        "HEAD",
        as_json=False,
    )
    (repo / "bridge" / "target.md").unlink()
    success = _cli(
        repo,
        "restore-deleted-path",
        "--path",
        "bridge/target.md",
        "--source-ref",
        "HEAD",
        as_json=False,
    )

    assert clean_denial.returncode == 2
    assert "DENIED: restore_target_not_unstaged_deletion" in clean_denial.stderr
    assert "code: restore_target_not_unstaged_deletion" in clean_denial.stderr
    assert success.returncode == 0
    assert "PASS: restore-deleted-path" in success.stdout
    assert "path: bridge/target.md" in success.stdout
    assert "source blob:" in success.stdout
    assert "restored blob:" in success.stdout
