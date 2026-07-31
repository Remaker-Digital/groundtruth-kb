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
