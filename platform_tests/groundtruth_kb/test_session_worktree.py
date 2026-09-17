"""Real Git observations preserve work without inferring disposal or liveness."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.session import worktree as module
from groundtruth_kb.session.worktree import (
    SESSION_BRANCH_PREFIX,
    SessionWorktreeError,
    classify_worktrees,
    is_session_context_id,
    project_worktree,
    session_branch,
    worktree_path,
)

SENV_A = "SENV-" + "a" * 32
SENV_B = "SENV-" + "b" * 32


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "--no-optional-locks", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=15,
        env={k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")},
    )


@pytest.fixture
def repo(tmp_path: Path, monkeypatch) -> Path:
    for name in tuple(os.environ):
        if name.upper().startswith("GIT_"):
            monkeypatch.delenv(name)
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "develop")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "config", "user.name", "Report qualification")
    _git(root, "config", "commit.gpgsign", "false")
    _git(root, "config", "core.autocrlf", "false")
    (root / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git(root, "add", "seed.txt")
    _git(root, "commit", "-qm", "seed")
    return root


def _checkout(repo, name=SENV_A, *, detached=False):
    path = repo / ".worktrees" / name
    _git(
        repo, "worktree", "add", "-q", *(["--detach"] if detached else ["-b", "session/" + name]), str(path), "develop"
    )
    return path


def _snapshot(root):
    result = {}
    for folder, dirs, files in os.walk(root, followlinks=False):
        parent = Path(folder)
        dirs[:] = sorted(d for d in dirs if not (parent / d).is_junction() and not (parent / d).is_symlink())
        for name in files:
            path = parent / name
            if not path.is_symlink():
                result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _report(repo, **kwargs):
    before = _snapshot(repo)
    states = classify_worktrees(repo, **kwargs)
    assert _snapshot(repo) == before
    assert all(s.candidate_action == "report_only" and "binding_live" not in s.as_dict() for s in states)
    return states


def _find(states, path):
    return next(s for s in states if s.path == path.absolute())


def _application_repo(host, name):
    root = host / "applications" / name
    root.mkdir(parents=True)
    _git(root, "init", "-q", "-b", "develop")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "config", "user.name", "Application qualification")
    _git(root, "config", "commit.gpgsign", "false")
    _git(root, "config", "core.autocrlf", "false")
    (root / "seed.txt").write_text(name + "\n", encoding="utf-8")
    _git(root, "add", "seed.txt")
    _git(root, "commit", "-qm", "application seed")
    return root


def _artifact_snapshot(paths, *, root):
    modes = module._artifact_modes(root, paths)
    return {
        path: {
            "mode": modes[path],
            "object_id": _git(root, "hash-object", f"--path={path}", "--", str(root / path)).stdout.strip(),
        }
        if (root / path).is_file()
        else None
        for path in paths
    }


@pytest.mark.parametrize("name", ["Alpha", "Beta"])
def test_application_work_and_successor_contexts_stay_in_platform_workspace(repo, name):
    application = _application_repo(repo, name)
    platform_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    app_head = _git(application, "rev-parse", "HEAD").stdout.strip()
    source = project_worktree(repo, "PROJECT-" + name, repository_root=application)
    assert source.is_relative_to(repo / ".worktrees/projects")
    assert not source.is_relative_to(application)
    assert _git(source, "rev-parse", "HEAD").stdout.strip() == app_head != platform_head
    artifacts = _artifact_snapshot(["seed.txt"], root=source)
    prepared = module.materialize_context_worktree(
        repo,
        SENV_A,
        expected_head=app_head,
        artifacts=artifacts,
        snapshot=_artifact_snapshot,
        artifact_source=source,
        repository_root=application,
    )
    first = Path(prepared["path"])
    assert first == worktree_path(repo, SENV_A)
    (first / "seed.txt").write_text(name + " authored work\n", encoding="utf-8")
    published = module.publish_context_work(
        repo,
        SENV_A,
        artifact_paths=["seed.txt"],
        expected_artifacts=artifacts,
        snapshot=_artifact_snapshot,
        artifact_destination=source,
        repository_root=application,
    )
    successor = module.materialize_context_worktree(
        repo,
        SENV_B,
        expected_head=app_head,
        artifacts=published,
        snapshot=_artifact_snapshot,
        artifact_source=source,
        repository_root=application,
    )
    assert (Path(successor["path"]) / "seed.txt").read_bytes() == (first / "seed.txt").read_bytes()
    assert _git(repo, "rev-parse", "HEAD").stdout.strip() == platform_head
    assert _git(application, "rev-parse", "HEAD").stdout.strip() == app_head
    assert not (application / ".worktrees").exists()
    assert str(first).replace("\\", "/") not in _git(repo, "worktree", "list", "--porcelain").stdout
    assert str(first).replace("\\", "/") in _git(application, "worktree", "list", "--porcelain").stdout


def test_project_checkout_cannot_be_repointed_to_a_different_repository(repo):
    alpha = _application_repo(repo, "Alpha")
    beta = _application_repo(repo, "Beta")
    checkout = project_worktree(repo, "PROJECT-SAME", repository_root=alpha)
    (checkout / "seed.txt").write_bytes(b"preserved application work")
    before = _snapshot(checkout)
    with pytest.raises(SessionWorktreeError) as error:
        project_worktree(repo, "PROJECT-SAME", repository_root=beta)
    assert error.value.code == "project_checkout_unregistered"
    assert _snapshot(checkout) == before


def test_context_checkout_cannot_publish_into_a_different_repository(repo):
    alpha = _application_repo(repo, "Alpha")
    beta = _application_repo(repo, "Beta")
    artifacts = _artifact_snapshot(["seed.txt"], root=alpha)
    module.materialize_context_worktree(
        repo,
        SENV_A,
        expected_head=_git(alpha, "rev-parse", "HEAD").stdout.strip(),
        artifacts=artifacts,
        snapshot=_artifact_snapshot,
        repository_root=alpha,
    )
    before = _snapshot(beta)
    with pytest.raises(SessionWorktreeError) as error:
        module.publish_context_work(
            repo,
            SENV_A,
            artifact_paths=["seed.txt"],
            expected_artifacts=artifacts,
            snapshot=_artifact_snapshot,
            repository_root=beta,
        )
    assert error.value.code == "checkout_not_registered"
    assert _snapshot(beta) == before


def test_application_workspace_inside_its_repository_is_refused_before_git_effect(repo):
    application = _application_repo(repo, "Alpha")
    workspace = application / "internal-workspace"
    before = _snapshot(application)
    with pytest.raises(SessionWorktreeError) as error:
        project_worktree(workspace, "PROJECT-TEST", repository_root=application)
    assert error.value.code == "workspace_inside_repository"
    assert _snapshot(application) == before


def test_application_project_refresh_uses_its_repository_and_preserves_local_work(repo):
    application = _application_repo(repo, "Alpha")
    checkout = project_worktree(repo, "PROJECT-APP", repository_root=application)
    (checkout / "seed.txt").write_bytes(b"local application work")
    (application / "next.txt").write_bytes(b"next application base")
    _git(application, "add", "next.txt")
    _git(application, "commit", "-qm", "next base")
    project_worktree(repo, "PROJECT-APP", repository_root=application, refresh_base=True)
    assert (checkout / "seed.txt").read_bytes() == b"local application work"
    assert (checkout / "next.txt").read_bytes() == b"next application base"
    assert not (repo / "next.txt").exists()


def test_inherited_git_routing_cannot_redirect_project_worktree_creation(repo, monkeypatch):
    application = _application_repo(repo, "Alpha")
    before = _snapshot(application)
    monkeypatch.setenv("GIT_DIR", str(application / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(application))
    monkeypatch.setenv("GIT_INDEX_FILE", str(application / "unwanted-index"))
    checkout = project_worktree(repo, "PROJECT-PLATFORM")
    assert (
        _git(checkout, "hash-object", "--path=seed.txt", "--", "seed.txt").stdout.strip()
        == _git(repo, "rev-parse", "HEAD:seed.txt").stdout.strip()
    )
    assert _snapshot(application) == before


@pytest.mark.parametrize("binding", ["absent", "present", "unreadable"])
def test_binding_storage_does_not_establish_liveness_or_disposal(repo, binding):
    checkout = _checkout(repo)
    db = repo / "groundtruth.db"
    if binding == "present":
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE session_init_bindings (session_context_id TEXT)")
            conn.execute("INSERT INTO session_init_bindings VALUES (?)", (SENV_A,))
    elif binding == "unreadable":
        db.write_bytes(b"not a database")
    state = _find(_report(repo), checkout)
    assert state.classification == "no_reported_work"
    assert state.tracked_dirty == state.untracked == 0
    assert state.head_is_ancestor is True
    assert not db.exists() if binding == "absent" else db.is_file()


@pytest.mark.parametrize("tracked,untracked", [(False, True), (True, False), (True, True)])
def test_observed_changes_are_work_even_when_only_untracked(repo, tracked, untracked):
    checkout = _checkout(repo)
    if tracked:
        (checkout / "seed.txt").write_bytes(b"unfinished\n")
    if untracked:
        (checkout / "nested").mkdir()
        (checkout / "nested/one.txt").write_bytes(b"one")
        (checkout / "nested/two.txt").write_bytes(b"two")
    state = _find(_report(repo), checkout)
    assert state.classification == "holds_work"
    assert state.tracked_dirty == int(tracked)
    assert state.untracked == 2 * int(untracked)


def test_ignored_content_survives_a_no_reported_work_result(repo):
    (repo / ".gitignore").write_text("local.txt\n", encoding="utf-8")
    _git(repo, "add", ".gitignore")
    _git(repo, "commit", "-qm", "ignore local")
    checkout = _checkout(repo)
    (checkout / "local.txt").write_bytes(b"not disposable")
    assert _find(_report(repo), checkout).classification == "no_reported_work"
    assert (checkout / "local.txt").read_bytes() == b"not disposable"


def test_independent_checkouts_keep_their_own_changes(repo):
    first, second = _checkout(repo), _checkout(repo, SENV_B)
    (first / "seed.txt").write_bytes(b"first only")
    states = _report(repo)
    assert _find(states, first).tracked_dirty == 1
    assert _find(states, second).tracked_dirty == 0


def test_unmerged_commit_is_observed_work(repo):
    checkout = _checkout(repo)
    (checkout / "new.txt").write_bytes(b"committed work")
    _git(checkout, "add", "new.txt")
    _git(checkout, "commit", "-qm", "local work")
    state = _find(_report(repo), checkout)
    assert state.tracked_dirty == 0 and state.head_is_ancestor is False
    assert state.classification == "holds_work"


@pytest.mark.parametrize("dirty", [False, True])
def test_unavailable_integration_ref_is_unknown_without_erasing_observed_work(repo, dirty):
    checkout = _checkout(repo)
    if dirty:
        (checkout / "seed.txt").write_bytes(b"unfinished")
    state = _find(_report(repo, integration_ref="missing-ref"), checkout)
    assert state.head_is_ancestor is None
    assert state.classification == ("holds_work" if dirty else "unknown")


def test_broken_git_pointer_is_unknown_without_reading_ancestor_content(repo):
    checkout = _checkout(repo)
    # Attribute-preserving edit of the hidden Windows gitfile.
    with (checkout / ".git").open("r+b") as stream:
        stream.write(b"gitdir: missing-administration\n")
        stream.truncate()
    state = _find(_report(repo), checkout)
    assert state.classification == "unknown"
    assert state.tracked_dirty is state.untracked is state.head_is_ancestor is None


def test_orphan_payload_is_not_read_or_classified_clean(repo, monkeypatch):
    orphan = repo / ".worktrees/orphan"
    orphan.mkdir(parents=True)
    payload = orphan / "private.txt"
    payload.write_bytes(b"unrelated content")
    original = Path.read_bytes

    def read_bytes(path):
        assert path != payload, "The report must not read orphan payload"
        return original(path)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_bytes", read_bytes)
        state = _find(classify_worktrees(repo), orphan)
    assert state.classification == "orphaned_checkout"
    assert state.tracked_dirty is state.untracked is state.head_is_ancestor is None
    assert state.candidate_action == "report_only"
    assert payload.read_bytes() == b"unrelated content"


def test_detached_and_locked_checkouts_remain_report_only(repo):
    checkout = _checkout(repo, "old-work", detached=True)
    _git(repo, "worktree", "lock", "--reason", "foreign work", str(checkout))
    state = _find(_report(repo), checkout)
    assert state.session_context_id is None and state.branch is None
    assert any("detached" in note for note in state.notes)
    assert any("locked" in note for note in state.notes)


def test_missing_registered_checkout_is_unknown_and_not_pruned(repo):
    checkout = _checkout(repo)
    moved = checkout.with_name("kept-elsewhere")
    checkout.rename(moved)
    state = _find(_report(repo), checkout)
    assert state.classification == "unknown"
    assert any("prunable" in note for note in state.notes)
    assert moved.is_dir() and not checkout.exists()


@pytest.mark.parametrize("name", ["checkout café", "checkout [brackets]"])
def test_literal_unicode_and_bracket_paths_round_trip(repo, name):
    checkout = repo / ".worktrees" / name
    _git(repo, "worktree", "add", "-q", "--detach", str(checkout), "develop")
    state = _find(_report(repo), checkout)
    assert state.path.name == name


@pytest.mark.parametrize("which", ["nested", "missing"])
def test_non_checkout_root_is_refused_before_inspection(repo, which):
    root = repo / which
    if which == "nested":
        root.mkdir()
    before = _snapshot(repo)
    with pytest.raises(SessionWorktreeError) as error:
        classify_worktrees(root)
    assert error.value.code in {"not_checkout_root", "git_observation_unavailable"}
    assert _snapshot(repo) == before


@pytest.mark.parametrize("failure", ["timeout", "missing-executable"])
def test_git_read_failure_is_bounded_and_useful(repo, monkeypatch, failure):
    def unavailable(argv, **kwargs):
        assert kwargs["timeout"] == 15
        if failure == "timeout":
            raise subprocess.TimeoutExpired(argv, 15)
        raise FileNotFoundError("Git unavailable")

    monkeypatch.setattr(module.subprocess, "run", unavailable)
    with pytest.raises(SessionWorktreeError, match="15-second") as error:
        classify_worktrees(repo)
    assert error.value.code == "git_observation_unavailable"


def test_git_status_failure_is_unknown_not_zero(repo, monkeypatch):
    checkout = _checkout(repo)
    original = module._git

    def git(root, *args, **kwargs):
        if args[0] == "status":
            return subprocess.CompletedProcess(args, 128, "", "fixture failure")
        return original(root, *args, **kwargs)

    monkeypatch.setattr(module, "_git", git)
    state = _find(_report(repo), checkout)
    assert state.classification == "unknown"
    assert state.tracked_dirty is state.untracked is None


def test_inherited_git_routing_does_not_redirect_the_report(repo, tmp_path, monkeypatch):
    checkout = _checkout(repo)
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    _git(foreign, "init", "-q")
    (foreign / "private.txt").write_bytes(b"foreign")
    before = _snapshot(foreign)
    monkeypatch.setenv("GIT_DIR", str(foreign / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(foreign))
    monkeypatch.setenv("GIT_INDEX_FILE", str(foreign / "new-index"))
    assert _find(_report(repo), checkout).classification == "no_reported_work"
    assert _snapshot(foreign) == before


def _junction(link, target):
    if os.name == "nt":
        command = (
            "New-Item -ItemType Junction -Path "
            + "'"
            + str(link).replace("'", "''")
            + "' -Target '"
            + str(target).replace("'", "''")
            + "' | Out-Null"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", command], check=True, capture_output=True, timeout=15)
    else:
        link.symlink_to(target, target_is_directory=True)


@pytest.mark.parametrize("location", ["root", "worktrees-root", "orphan", "registered"])
def test_junctions_never_cause_target_content_inspection(repo, tmp_path, location):
    foreign = tmp_path / "outside"
    foreign.mkdir()
    (foreign / "private.txt").write_bytes(b"preserve target")
    before = _snapshot(foreign)
    if location == "root":
        link = tmp_path / "redirected-root"
        _junction(link, repo)
        with pytest.raises(SessionWorktreeError, match="redirected"):
            classify_worktrees(link)
    elif location == "worktrees-root":
        _junction(repo / ".worktrees", foreign)
        with pytest.raises(SessionWorktreeError, match="redirected"):
            classify_worktrees(repo)
    else:
        if location == "registered":
            link = _checkout(repo)
            link.rename(link.with_name("preserved-checkout"))
        else:
            link = repo / ".worktrees/orphan-link"
            link.parent.mkdir()
        _junction(link, foreign)
        state = _find(classify_worktrees(repo), link)
        assert state.classification == ("unknown" if location == "registered" else "orphaned_checkout")
        assert state.tracked_dirty is state.untracked is None
        assert state.candidate_action == "report_only"
    assert _snapshot(foreign) == before


def test_cli_json_and_text_report_unknown_without_database_or_mutation(repo):
    checkout = _checkout(repo)
    before = _snapshot(repo)
    runner = CliRunner()
    arguments = ["hygiene", "worktrees", "--root", str(repo), "--integration-ref", "missing-ref"]
    result = runner.invoke(main, [*arguments, "--json"])
    assert result.exit_code == 0, result.output
    item = next(row for row in json.loads(result.output) if row["path"] == checkout.as_posix())
    assert item["classification"] == "unknown" and item["candidate_action"] == "report_only"
    result = runner.invoke(main, arguments)
    assert result.exit_code == 0, result.output
    assert "disposal eligibility" in result.output and "unknown" in result.output
    assert _snapshot(repo) == before


def test_cli_preserves_lexical_root_refusal(repo):
    nested = repo / "nested"
    nested.mkdir()
    result = CliRunner().invoke(main, ["hygiene", "worktrees", "--root", str(nested), "--json"])
    assert result.exit_code == 1
    assert "not_checkout_root" in result.output


def test_report_excludes_the_main_checkout(repo):
    assert _report(repo) == []


def test_path_and_branch_are_derived_from_the_identity_alone(tmp_path: Path) -> None:
    """No registry, no pointer column, no marker file, so nothing can drift."""
    assert worktree_path(tmp_path, SENV_A) == (tmp_path.resolve() / ".worktrees" / SENV_A)
    assert session_branch(SENV_A) == f"{SESSION_BRANCH_PREFIX}{SENV_A}"


@pytest.mark.parametrize("name", ["wi7805-ownership-bias-census", "SENV-short", "", "senv-" + "a" * 32])
def test_names_that_are_not_session_identities_are_refused(tmp_path: Path, name: str) -> None:
    """The 46 pre-lifecycle checkouts are work-item-named; none may be mistaken
    for a session checkout, because that is what licenses removal."""
    assert is_session_context_id(name) is False
    with pytest.raises(SessionWorktreeError) as excinfo:
        worktree_path(tmp_path, name)
    assert excinfo.value.code == "invalid_session_context_id"


def test_project_refresh_preserves_ignored_local_files(repo: Path) -> None:
    (repo / ".gitignore").write_text("local.txt\n", encoding="utf-8")
    _git(repo, "add", ".gitignore")
    _git(repo, "commit", "-qm", "ignore local output")
    checkout = project_worktree(repo, "PROJECT-TEST")
    old_head = _git(checkout, "rev-parse", "HEAD").stdout.strip()
    local = checkout / "local.txt"
    local.write_bytes(b"unfinished local work\n")
    (repo / "local.txt").write_bytes(b"new canonical artifact\n")
    _git(repo, "add", "-f", "local.txt")
    _git(repo, "commit", "-qm", "introduce formerly ignored artifact")

    with pytest.raises(SessionWorktreeError) as excinfo:
        project_worktree(repo, "PROJECT-TEST", refresh_base=True)

    assert excinfo.value.code == "project_base_reconciliation_required"
    assert local.read_bytes() == b"unfinished local work\n"
    assert _git(checkout, "rev-parse", "HEAD").stdout.strip() == old_head


def test_project_refresh_fast_forwards_without_disturbing_local_work(repo: Path) -> None:
    (repo / ".gitignore").write_text("local.txt\n", encoding="utf-8")
    _git(repo, "add", ".gitignore")
    _git(repo, "commit", "-qm", "ignore local output")
    checkout = project_worktree(repo, "PROJECT-TEST")
    (checkout / "local.txt").write_bytes(b"unfinished local work\n")
    (repo / "new.txt").write_bytes(b"new canonical artifact\n")
    _git(repo, "add", "new.txt")
    _git(repo, "commit", "-qm", "add unrelated artifact")

    assert project_worktree(repo, "PROJECT-TEST", refresh_base=True) == checkout

    assert (checkout / "local.txt").read_bytes() == b"unfinished local work\n"
    assert (checkout / "new.txt").read_bytes() == b"new canonical artifact\n"
    assert _git(checkout, "rev-parse", "HEAD").stdout == _git(repo, "rev-parse", "HEAD").stdout
