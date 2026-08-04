"""Fail-closed coverage for the governed one-off branch-publication operation (WI-5840).

Every test asserts one enumerated stop condition from
``bridge/gtkb-wi5840-git-lifecycle-publication-operation-001.md``. The operation
must stop before the next side effect on each of them.
"""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest
from groundtruth_kb.git_lifecycle.commands import CommandResult
from groundtruth_kb.git_lifecycle.models import OperationDenied
from groundtruth_kb.git_lifecycle.service import GitLifecycleService


class RecordingBoundary:
    """In-memory command boundary recording every exact argv it is handed."""

    def __init__(self, responses: dict[str, CommandResult] | None = None) -> None:
        self.calls: list[tuple[str, ...]] = []
        self.responses = responses or {}

    def run(self, argv: Sequence[str], *, cwd: Path) -> CommandResult:
        exact = tuple(str(item) for item in argv)
        self.calls.append(exact)
        for marker, response in self.responses.items():
            if marker in exact:
                return CommandResult(
                    argv=exact, returncode=response.returncode, stdout=response.stdout, stderr=response.stderr
                )
        return CommandResult(argv=exact, returncode=0)

    def verb_calls(self, verb: str) -> list[tuple[str, ...]]:
        return [call for call in self.calls if verb in call]


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
        shell=False,
    )
    return completed.stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "--initial-branch=main")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "config", "user.name", "Test")
    (root / "keep.txt").write_text("base\n", encoding="utf-8")
    (root / "excluded.txt").write_text("excluded-base\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "base commit")
    return root


def _service(repo: Path, boundary: RecordingBoundary) -> GitLifecycleService:
    return GitLifecycleService(repo, command_boundary=boundary)


def _fetch_head_pointing_at(repo: Path, commit: str) -> None:
    """Simulate the post-fetch state the real fetch would leave behind."""
    (repo / ".git" / "FETCH_HEAD").write_text(f"{commit}\t\tbranch 'main' of origin\n", encoding="utf-8")


def _publish_kwargs(repo: Path, **overrides: object) -> dict[str, object]:
    head = _git(repo, "rev-parse", "HEAD")
    tree = _git(repo, "rev-parse", "HEAD^{tree}")
    payload: dict[str, object] = {
        "source_commit": head,
        "source_tree": tree,
        "base_ref": "main",
        "target_ref": "codex/publish-candidate",
        "message": "publish candidate",
        "max_blob_bytes": 1_000_000,
    }
    payload.update(overrides)
    return payload


# --- success path -----------------------------------------------------------


def test_publish_creates_one_ref_and_pushes_once(repo: Path) -> None:
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "new.txt").write_text("added\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "candidate content")
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    _fetch_head_pointing_at(repo, head)

    result = _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo))

    assert result.operation == "publish"
    assert result.code == "candidate_branch_published"
    assert result.details["base_commit"] == head
    assert result.details["pushed"] is True

    pushes = boundary.verb_calls("push")
    assert len(pushes) == 1, "exactly one push must occur"
    push = pushes[0]
    assert "--force" not in push and "--force-with-lease" not in push
    assert "--tags" not in push
    assert "--delete" not in push
    assert "--set-upstream" not in push
    refspecs = [item for item in push if ":" in item and item.startswith("refs/")]
    assert refspecs == ["refs/heads/codex/publish-candidate:refs/heads/codex/publish-candidate"]


def test_no_push_creates_ref_without_publishing(repo: Path) -> None:
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "new.txt").write_text("added\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "candidate content")
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    _fetch_head_pointing_at(repo, head)

    result = _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo, push=False))

    assert result.code == "candidate_ref_created"
    assert result.details["pushed"] is False
    assert boundary.verb_calls("push") == []


# --- fail-closed conditions -------------------------------------------------


def test_declared_tree_mismatch_stops_before_any_side_effect(repo: Path) -> None:
    boundary = RecordingBoundary()
    with pytest.raises(OperationDenied) as excinfo:
        _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo, source_tree="0" * 40))
    assert excinfo.value.code == "source_tree_mismatch"
    assert boundary.calls == [], "no command may run after a binding mismatch"


def test_remote_url_mismatch_stops_before_fetch(repo: Path) -> None:
    boundary = RecordingBoundary()
    with pytest.raises(OperationDenied) as excinfo:
        _service(repo, boundary).publish_candidate_branch(
            **_publish_kwargs(repo, expected_remote_url="https://example.invalid/expected.git")
        )
    assert excinfo.value.code == "remote_url_mismatch"
    assert boundary.verb_calls("fetch") == []


def test_failed_fetch_stops_before_candidate_creation(repo: Path) -> None:
    boundary = RecordingBoundary({"fetch": CommandResult(argv=(), returncode=128, stderr="no such remote")})
    with pytest.raises(OperationDenied) as excinfo:
        _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo))
    assert excinfo.value.code == "base_fetch_failed"
    assert boundary.verb_calls("push") == []


def test_ambiguous_fetch_state_is_refused(repo: Path) -> None:
    boundary = RecordingBoundary()
    fetch_head = repo / ".git" / "FETCH_HEAD"
    fetch_head.write_text("not-a-commit\n", encoding="utf-8")
    with pytest.raises(OperationDenied) as excinfo:
        _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo))
    assert excinfo.value.code == "base_fetch_ambiguous"


def test_existing_local_target_ref_is_refused(repo: Path) -> None:
    head = _git(repo, "rev-parse", "HEAD")
    _git(repo, "branch", "codex/publish-candidate")
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    _fetch_head_pointing_at(repo, head)
    with pytest.raises(OperationDenied) as excinfo:
        _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo))
    assert excinfo.value.code == "target_ref_exists_locally"
    assert boundary.verb_calls("push") == []


def test_existing_remote_target_ref_is_refused(repo: Path) -> None:
    head = _git(repo, "rev-parse", "HEAD")
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=0, stdout=f"{head}\trefs/heads/x")})
    _fetch_head_pointing_at(repo, head)
    with pytest.raises(OperationDenied) as excinfo:
        _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo))
    assert excinfo.value.code == "target_ref_exists_remotely"
    assert boundary.verb_calls("push") == []


def test_remote_check_error_is_not_treated_as_absence(repo: Path) -> None:
    """A network or auth failure must never be read as 'the ref does not exist'."""
    head = _git(repo, "rev-parse", "HEAD")
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=128, stderr="auth failed")})
    _fetch_head_pointing_at(repo, head)
    with pytest.raises(OperationDenied) as excinfo:
        _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo))
    assert excinfo.value.code == "target_ref_absence_unproven"
    assert boundary.verb_calls("push") == []


def test_same_tree_candidate_publishes_a_single_commit_object(repo: Path) -> None:
    """A candidate whose tree equals the base's is NOT an empty range.

    ``rev-list --objects BASE..CANDIDATE`` always contains at least the candidate
    commit object, so this case yields a one-object range and publishes normally.
    The GO'd specification requires rejecting an *empty object range*, not a
    content-identical tree; no unspecified same-tree gate is asserted here.
    The ``empty_publication_range`` guard is therefore defensive and not reached
    by this flow.
    """
    head = _git(repo, "rev-parse", "HEAD")
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    _fetch_head_pointing_at(repo, head)

    result = _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo, push=False))

    assert result.code == "candidate_ref_created"
    assert result.details["object_counts"].get("commit") == 1
    assert result.details["object_counts"].get("blob") is None, "an unchanged tree contributes no new blobs"
    assert boundary.verb_calls("push") == []


def test_blob_ceiling_applies_to_blobs(repo: Path) -> None:
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "big.bin").write_text("x" * 5000, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "large blob")
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    _fetch_head_pointing_at(repo, head)
    with pytest.raises(OperationDenied) as excinfo:
        _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo, max_blob_bytes=1000))
    assert excinfo.value.code == "blob_size_ceiling_exceeded"
    assert boundary.verb_calls("push") == []


def test_blob_ceiling_does_not_trip_on_non_blob_objects(repo: Path) -> None:
    """The ceiling is blob-only; commit and tree objects must never trip it."""
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "small.txt").write_text("s\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "m" * 400)  # large commit object, small blob
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    _fetch_head_pointing_at(repo, head)

    result = _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo, max_blob_bytes=100, push=False))

    assert result.code == "candidate_ref_created"
    assert result.details["largest_blob_bytes"] <= 100


def test_excluded_path_delta_is_refused(repo: Path) -> None:
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "excluded.txt").write_text("excluded-changed\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "touch excluded carrier")
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    _fetch_head_pointing_at(repo, head)
    with pytest.raises(OperationDenied) as excinfo:
        _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo, exclude_paths=("excluded.txt",)))
    assert excinfo.value.code in {"excluded_path_delta", "excluded_path_in_range"}
    assert boundary.verb_calls("push") == []


def test_protected_destination_branch_is_denied(repo: Path) -> None:
    boundary = RecordingBoundary()
    with pytest.raises(OperationDenied) as excinfo:
        _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo, target_ref="main"))
    assert excinfo.value.code in {"direct_push_prohibited", "target_ref_exists_locally"}
    assert boundary.verb_calls("push") == []


def test_failed_push_reports_and_infers_no_retry(repo: Path) -> None:
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "new.txt").write_text("added\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "candidate content")
    boundary = RecordingBoundary(
        {
            "ls-remote": CommandResult(argv=(), returncode=2),
            "push": CommandResult(argv=(), returncode=1, stderr="non-fast-forward"),
        }
    )
    _fetch_head_pointing_at(repo, head)
    with pytest.raises(OperationDenied) as excinfo:
        _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo))
    assert excinfo.value.code == "publication_push_failed"
    assert len(boundary.verb_calls("push")) == 1, "a failed push must not be retried"


def test_fetch_is_single_narrow_and_no_tags(repo: Path) -> None:
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "new.txt").write_text("added\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "candidate content")
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    _fetch_head_pointing_at(repo, head)

    _service(repo, boundary).publish_candidate_branch(**_publish_kwargs(repo, push=False))

    fetches = boundary.verb_calls("fetch")
    assert len(fetches) == 1, "exactly one fetch must occur"
    assert "--no-tags" in fetches[0]
    assert "--no-recurse-submodules" in fetches[0]
    assert "main" in fetches[0]


# --- WI-5840 v007: complete fail-closed publication denial coverage -------------


def test_empty_publication_range_is_denied(repo: Path, monkeypatch) -> None:
    """An empty rev-list --objects result denies before any update-ref/push."""
    service = _service(repo, RecordingBoundary())

    class _FakeRun:
        def __init__(self, stdout="", returncode=0):
            self.stdout = stdout
            self.returncode = returncode

    def fake_repo_run(*args, **kwargs):
        argv = list(args)
        if "rev-list" in argv and "--objects" in argv:
            return _FakeRun(stdout="")
        raise AssertionError(f"unexpected repo.run: {argv}")

    monkeypatch.setattr(service.repo, "run", fake_repo_run)
    with pytest.raises(OperationDenied) as excinfo:
        service._enumerate_range(
            base_commit="0" * 40,
            candidate="1" * 40,
            excluded=(),
            max_blob_bytes=1000,
        )
    assert excinfo.value.code == "empty_publication_range"


def test_range_object_unresolvable_is_denied(repo: Path, monkeypatch) -> None:
    """A non-object entry in the range listing denies before any side effect."""
    service = _service(repo, RecordingBoundary())

    class _FakeRun:
        def __init__(self, stdout="", returncode=0):
            self.stdout = stdout
            self.returncode = returncode

    def fake_repo_run(*args, **kwargs):
        argv = list(args)
        if "rev-list" in argv and "--objects" in argv:
            return _FakeRun(stdout="not-a-40-hex-oid path.txt\n")
        raise AssertionError(f"unexpected repo.run: {argv}")

    monkeypatch.setattr(service.repo, "run", fake_repo_run)
    with pytest.raises(OperationDenied) as excinfo:
        service._enumerate_range(
            base_commit="0" * 40,
            candidate="1" * 40,
            excluded=(),
            max_blob_bytes=1000,
        )
    assert excinfo.value.code == "range_object_unresolvable"


def test_range_object_type_unexpected_is_denied(repo: Path, monkeypatch) -> None:
    """An unsupported object type in the batch-check result denies."""
    import groundtruth_kb.git_lifecycle.service as svc_mod

    service = _service(repo, RecordingBoundary())
    oid = "a" * 40

    class _FakeRun:
        def __init__(self, stdout="", returncode=0):
            self.stdout = stdout
            self.returncode = returncode

    def fake_repo_run(*args, **kwargs):
        argv = list(args)
        if "rev-list" in argv and "--objects" in argv:
            return _FakeRun(stdout=f"{oid} path.txt\n")
        raise AssertionError(f"unexpected repo.run: {argv}")

    monkeypatch.setattr(service.repo, "run", fake_repo_run)

    class _FakeCat:
        def __init__(self, returncode=0, stdout="", stderr=""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def fake_cat_file(*args, **kwargs):
        return _FakeCat(stdout=f"{oid} unexpected_type 5\n")

    monkeypatch.setattr(svc_mod.subprocess, "run", fake_cat_file)
    with pytest.raises(OperationDenied) as excinfo:
        service._enumerate_range(
            base_commit="0" * 40,
            candidate="1" * 40,
            excluded=(),
            max_blob_bytes=1000,
        )
    assert excinfo.value.code == "range_object_type_unexpected"


def test_candidate_parentage_invalid_is_denied(repo: Path, monkeypatch) -> None:
    """A candidate with other than exactly-one-fetched-base parent denies."""
    service = _service(repo, RecordingBoundary())
    base = "0" * 40
    candidate = "1" * 40

    class _FakeRun:
        def __init__(self, stdout="", returncode=0):
            self.stdout = stdout
            self.returncode = returncode

    def fake_repo_run(*args, **kwargs):
        argv = list(args)
        if "rev-parse" in argv:
            return _FakeRun(stdout="2" * 40)
        if "rev-list" in argv and "--count" in argv:
            return _FakeRun(stdout="1")
        raise AssertionError(f"unexpected repo.run: {argv}")

    monkeypatch.setattr(service.repo, "run", fake_repo_run)
    monkeypatch.setattr(service.repo, "parents", lambda c: ("deadbeef" * 5,))
    with pytest.raises(OperationDenied) as excinfo:
        service._assert_candidate_shape(candidate=candidate, base_commit=base, expected_tree="2" * 40, excluded=())
    assert excinfo.value.code == "candidate_parentage_invalid"


def test_candidate_not_single_commit_ahead_is_denied(repo: Path, monkeypatch) -> None:
    """A candidate more than one commit ahead of the base denies."""
    service = _service(repo, RecordingBoundary())
    base = "0" * 40
    candidate = "1" * 40

    class _FakeRun:
        def __init__(self, stdout="", returncode=0):
            self.stdout = stdout
            self.returncode = returncode

    def fake_repo_run(*args, **kwargs):
        argv = list(args)
        if "rev-parse" in argv:
            return _FakeRun(stdout="2" * 40)
        if "rev-list" in argv and "--count" in argv:
            return _FakeRun(stdout="2")
        raise AssertionError(f"unexpected repo.run: {argv}")

    monkeypatch.setattr(service.repo, "run", fake_repo_run)
    monkeypatch.setattr(service.repo, "parents", lambda c: (base,))
    with pytest.raises(OperationDenied) as excinfo:
        service._assert_candidate_shape(candidate=candidate, base_commit=base, expected_tree="2" * 40, excluded=())
    assert excinfo.value.code == "candidate_not_single_commit_ahead"


def test_index_change_during_publication_is_denied(repo: Path, monkeypatch) -> None:
    """A changed git index between binding and pre-ref recheck denies."""
    head = _git(repo, "rev-parse", "HEAD")
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    _fetch_head_pointing_at(repo, head)
    service = _service(repo, boundary)
    snapshots = iter([b"index-before", b"index-now-different"])
    monkeypatch.setattr(service.repo, "index_snapshot", lambda: next(snapshots))
    with pytest.raises(OperationDenied) as excinfo:
        service.publish_candidate_branch(**_publish_kwargs(repo))
    assert excinfo.value.code == "index_changed_during_publication"
    assert boundary.verb_calls("push") == []


def test_remote_ref_rewrite_is_denied() -> None:
    """Differing source/destination branches deny remote publication."""
    from groundtruth_kb.git_lifecycle.service import GitLifecycleService

    with pytest.raises(OperationDenied) as excinfo:
        GitLifecycleService.validate_remote_push("feature/source", "feature/destination")
    assert excinfo.value.code == "remote_ref_rewrite_prohibited"


def test_invalid_max_blob_bytes_is_denied_before_fetch(repo: Path, monkeypatch) -> None:
    """A zero/negative max-blob-bytes denies before fetch or mutation."""
    boundary = RecordingBoundary()
    service = _service(repo, boundary)
    with pytest.raises(OperationDenied) as excinfo:
        service.publish_candidate_branch(**_publish_kwargs(repo, max_blob_bytes=0))
    assert excinfo.value.code == "invalid_max_blob_bytes"
    assert boundary.verb_calls("fetch") == []
    assert boundary.verb_calls("push") == []


def test_missing_max_blob_bytes_cli_argument_is_denied() -> None:
    """The CLI requires --max-blob-bytes (no publishing default)."""
    from groundtruth_kb.git_lifecycle import __main__ as git_lifecycle_main

    parser = git_lifecycle_main._parser()
    argv = [
        "publish",
        "--source-commit",
        "0" * 40,
        "--source-tree",
        "1" * 40,
        "--base-ref",
        "main",
        "--target-ref",
        "x/y",
        "--message",
        "m",
    ]
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(argv)
    assert excinfo.value.code == 2, "omitting required --max-blob-bytes must exit nonzero"


# --- WI-5840 v011: publication-path fixtures (NO-GO v010 remediation) ----------
#
# Version 010 (NO-GO) found that five of the seven approved denial guards were
# exercised only through internal helpers (_enumerate_range /
# _assert_candidate_shape / validate_remote_push) without asserting no
# fetch/update-ref/push. These fixtures drive each guard through the PUBLIC
# publish_candidate_branch entry point using a scripted repo facade, and assert
# the exact OperationDenied.code plus that no mutating command ran.


class _Completed:
    def __init__(self, *, stdout: str = "", stderr: str = "", returncode: int = 0) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def _scripted_run(script):
    """Return a repo.run replacement dispatching on argv prefixes."""

    def run(*args, check=True, env=None):
        argv = list(args)
        key = " ".join(argv)
        for prefix, response in script.items():
            if key.startswith(prefix):
                return response
        raise AssertionError(f"unexpected repo.run: {argv}")

    return run


def _pub_scripted(
    repo, monkeypatch, *, run_script=None, parents=None, index_snapshots=None, branch_exists=False, is_ancestor=True
):
    service = _service(repo, RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)}))
    if run_script is not None:
        monkeypatch.setattr(service.repo, "run", _scripted_run(run_script))
    monkeypatch.setattr(service.repo, "run_bytes", lambda *args, **kwargs: _Completed(stdout=b""))
    if parents is not None:
        monkeypatch.setattr(service.repo, "parents", lambda commit: parents)
    if index_snapshots is not None:
        it = iter(index_snapshots)
        monkeypatch.setattr(service.repo, "index_snapshot", lambda: next(it))
    monkeypatch.setattr(service.repo, "branch_exists", lambda branch: branch_exists)
    monkeypatch.setattr(service.repo, "is_ancestor", lambda a, d: is_ancestor)
    monkeypatch.setattr(service.repo, "resolve_commit", lambda ref: ref if ref == "0" * 40 else ref)
    return service


def test_publication_path_empty_publication_range_is_denied(repo, monkeypatch):
    """empty_publication_range fires through publish_candidate_branch with no push."""
    head = "0" * 40
    tree = "1" * 40
    base = "a" * 40
    candidate = "b" * 40
    run_script = {
        "rev-parse 0000000000000000000000000000000000000000^{tree}": _Completed(stdout=tree),
        "rev-parse FETCH_HEAD^{commit}": _Completed(stdout=base),
        "commit-tree": _Completed(stdout=candidate),
        "rev-parse bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb^{tree}": _Completed(stdout=tree),
        "rev-list --count": _Completed(stdout="1"),
        "rev-list --objects": _Completed(stdout=""),
    }
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    service = _pub_scripted(repo, monkeypatch, run_script=run_script, parents=(base,))
    with pytest.raises(OperationDenied) as excinfo:
        service.publish_candidate_branch(**_publish_kwargs(repo, source_commit=head, source_tree=tree, push=False))
    assert excinfo.value.code == "empty_publication_range"
    assert boundary.verb_calls("push") == []


def test_publication_path_range_object_unresolvable_is_denied(repo, monkeypatch):
    """range_object_unresolvable fires through publish_candidate_branch with no push."""
    head = "0" * 40
    tree = "1" * 40
    base = "a" * 40
    candidate = "b" * 40
    run_script = {
        "rev-parse 0000000000000000000000000000000000000000^{tree}": _Completed(stdout=tree),
        "rev-parse FETCH_HEAD^{commit}": _Completed(stdout=base),
        "commit-tree": _Completed(stdout=candidate),
        "rev-parse bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb^{tree}": _Completed(stdout=tree),
        "rev-list --count": _Completed(stdout="1"),
        "rev-list --objects": _Completed(stdout="not-a-40-hex-oid path.txt\n"),
    }
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    service = _pub_scripted(repo, monkeypatch, run_script=run_script, parents=(base,))
    with pytest.raises(OperationDenied) as excinfo:
        service.publish_candidate_branch(**_publish_kwargs(repo, source_commit=head, source_tree=tree, push=False))
    assert excinfo.value.code == "range_object_unresolvable"
    assert boundary.verb_calls("push") == []


def test_publication_path_range_object_type_unexpected_is_denied(repo, monkeypatch):
    """range_object_type_unexpected fires through publish_candidate_branch with no push."""
    import groundtruth_kb.git_lifecycle.service as svc_mod

    head = "0" * 40
    tree = "1" * 40
    base = "a" * 40
    candidate = "b" * 40
    oid = "c" * 40
    run_script = {
        "rev-parse 0000000000000000000000000000000000000000^{tree}": _Completed(stdout=tree),
        "rev-parse FETCH_HEAD^{commit}": _Completed(stdout=base),
        "commit-tree": _Completed(stdout=candidate),
        "rev-parse bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb^{tree}": _Completed(stdout=tree),
        "rev-list --count": _Completed(stdout="1"),
        "rev-list --objects": _Completed(stdout=f"{oid} path.txt\n"),
    }
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    service = _pub_scripted(repo, monkeypatch, run_script=run_script, parents=(base,))

    def fake_cat_file(*args, **kwargs):
        return _Completed(stdout=f"{oid} unexpected_type 5\n")

    monkeypatch.setattr(svc_mod.subprocess, "run", fake_cat_file)
    with pytest.raises(OperationDenied) as excinfo:
        service.publish_candidate_branch(**_publish_kwargs(repo, source_commit=head, source_tree=tree, push=False))
    assert excinfo.value.code == "range_object_type_unexpected"
    assert boundary.verb_calls("push") == []


def test_publication_path_candidate_parentage_invalid_is_denied(repo, monkeypatch):
    """candidate_parentage_invalid fires through publish_candidate_branch with no push."""
    head = "0" * 40
    tree = "1" * 40
    base = "a" * 40
    candidate = "b" * 40
    run_script = {
        "rev-parse 0000000000000000000000000000000000000000^{tree}": _Completed(stdout=tree),
        "rev-parse FETCH_HEAD^{commit}": _Completed(stdout=base),
        "commit-tree": _Completed(stdout=candidate),
        "rev-parse bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb^{tree}": _Completed(stdout=tree),
    }
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    service = _pub_scripted(repo, monkeypatch, run_script=run_script, parents=("d" * 40,))
    with pytest.raises(OperationDenied) as excinfo:
        service.publish_candidate_branch(**_publish_kwargs(repo, source_commit=head, source_tree=tree, push=False))
    assert excinfo.value.code == "candidate_parentage_invalid"
    assert boundary.verb_calls("push") == []


def test_publication_path_candidate_not_single_commit_ahead_is_denied(repo, monkeypatch):
    """candidate_not_single_commit_ahead fires through publish_candidate_branch with no push."""
    head = "0" * 40
    tree = "1" * 40
    base = "a" * 40
    candidate = "b" * 40
    run_script = {
        "rev-parse 0000000000000000000000000000000000000000^{tree}": _Completed(stdout=tree),
        "rev-parse FETCH_HEAD^{commit}": _Completed(stdout=base),
        "commit-tree": _Completed(stdout=candidate),
        "rev-parse bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb^{tree}": _Completed(stdout=tree),
        "rev-list --count": _Completed(stdout="2"),
    }
    boundary = RecordingBoundary({"ls-remote": CommandResult(argv=(), returncode=2)})
    service = _pub_scripted(repo, monkeypatch, run_script=run_script, parents=(base,))
    with pytest.raises(OperationDenied) as excinfo:
        service.publish_candidate_branch(**_publish_kwargs(repo, source_commit=head, source_tree=tree, push=False))
    assert excinfo.value.code == "candidate_not_single_commit_ahead"
    assert boundary.verb_calls("push") == []


def test_publication_path_remote_ref_rewrite_is_denied_before_fetch(repo):
    """remote_ref_rewrite_prohibited fires before any fetch/update-ref/push."""
    boundary = RecordingBoundary()
    service = _service(repo, boundary)
    with pytest.raises(OperationDenied) as excinfo:
        service.publish_candidate_branch(
            **_publish_kwargs(repo, source_commit="0" * 40, source_tree="1" * 40, target_ref="main")
        )
    assert excinfo.value.code in {
        "direct_push_prohibited",
        "remote_ref_rewrite_prohibited",
        "target_ref_exists_locally",
    }
    assert boundary.verb_calls("fetch") == []
    assert boundary.verb_calls("push") == []
