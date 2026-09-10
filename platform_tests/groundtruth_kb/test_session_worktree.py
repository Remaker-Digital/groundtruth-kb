"""One git worktree per session context.

These tests drive real git repositories rather than mocks, because the whole
value of the module is what git actually does with a second checkout: which
commits survive a removal, what ``status`` reports, and whether a branch keeps a
commit reachable. A mocked ``subprocess`` would assert only that this module
composes strings.

The failure being prevented is concrete. Commit ``2f688c4ca`` folded 1,756 paths
of other sessions' uncommitted work into one unreviewed commit and silently
dropped a mandatory deny from the compliance gate. So the assertions that matter
most here are the refusals: that a checkout holding work is never closed, and
that nothing in this module ever commits on another session's behalf.
"""

from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path

import pytest
from groundtruth_kb.session.worktree import (
    SESSION_BRANCH_PREFIX,
    SessionWorktreeError,
    classify_worktrees,
    close_worktree,
    is_session_context_id,
    live_session_context_ids,
    open_worktree,
    project_worktree,
    session_branch,
    show_worktree,
    worktree_path,
)

SENV_A = "SENV-" + "a" * 32
SENV_B = "SENV-" + "b" * 32


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A repository with a develop branch and one commit."""
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "develop")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "Test")
    (root / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git(root, "add", "seed.txt")
    _git(root, "commit", "-qm", "seed")
    return root


@pytest.fixture
def db(tmp_path: Path) -> Path:
    """A MemBase stub carrying the one table this module reads."""
    path = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE session_init_bindings (native_context_id TEXT, session_context_id TEXT)")
    conn.commit()
    conn.close()
    return path


def _bind(db_path: Path, session_context_id: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO session_init_bindings VALUES (?, ?)",
        (f"native-{session_context_id}", session_context_id),
    )
    conn.commit()
    conn.close()


def _retire(db_path: Path, session_context_id: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM session_init_bindings WHERE session_context_id = ?", (session_context_id,))
    conn.commit()
    conn.close()


def _find(states, path: Path):
    return next((state for state in states if state.path == path.resolve()), None)


# --- derivation -------------------------------------------------------------


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


def test_missing_database_yields_no_live_bindings(tmp_path: Path) -> None:
    """Fail closed: with no readable database every checkout classifies as
    unowned, which is the class that is never removed."""
    assert live_session_context_ids(tmp_path / "absent.db") == frozenset()


def test_live_bindings_are_read_from_the_shared_source_of_truth(db: Path) -> None:
    _bind(db, SENV_A)
    assert live_session_context_ids(db) == frozenset({SENV_A})


# --- open -------------------------------------------------------------------


def test_open_creates_a_checkout_on_a_named_branch(repo: Path, db: Path) -> None:
    """Never detached: a commit made in the checkout must survive its removal."""
    _bind(db, SENV_A)
    state = open_worktree(repo, SENV_A, db_path=db, base="develop")
    assert state.path == worktree_path(repo, SENV_A)
    assert state.path.is_dir()
    assert state.branch == session_branch(SENV_A)
    assert state.classification == "live"
    assert state.candidate_action == "skip"


def test_open_is_idempotent(repo: Path, db: Path) -> None:
    """An init line that arrives twice must not produce a second checkout."""
    _bind(db, SENV_A)
    first = open_worktree(repo, SENV_A, db_path=db, base="develop")
    second = open_worktree(repo, SENV_A, db_path=db, base="develop")
    assert first.path == second.path
    assert len(list((repo / ".worktrees").iterdir())) == 1


def test_open_refuses_an_unresolvable_base(repo: Path, db: Path) -> None:
    _bind(db, SENV_A)
    with pytest.raises(SessionWorktreeError) as excinfo:
        open_worktree(repo, SENV_A, db_path=db, base="no-such-ref")
    assert excinfo.value.code == "unknown_base"


def test_two_sessions_get_independent_checkouts(repo: Path, db: Path) -> None:
    """The point of the change: one session's edit cannot reach the other."""
    _bind(db, SENV_A)
    _bind(db, SENV_B)
    a = open_worktree(repo, SENV_A, db_path=db, base="develop")
    b = open_worktree(repo, SENV_B, db_path=db, base="develop")
    assert a.path != b.path

    (a.path / "seed.txt").write_text("edited by A\n", encoding="utf-8")
    states = classify_worktrees(repo, db)
    assert _find(states, a.path).tracked_dirty == 1
    assert _find(states, b.path).tracked_dirty == 0


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


# --- classification ---------------------------------------------------------


def test_a_retired_binding_with_no_work_is_closeable(repo: Path, db: Path) -> None:
    _bind(db, SENV_A)
    state = open_worktree(repo, SENV_A, db_path=db, base="develop")
    _retire(db, SENV_A)
    after = _find(classify_worktrees(repo, db), state.path)
    assert after.classification == "abandoned_clean"
    assert after.candidate_action == "close_session_worktree"


def test_a_retired_binding_holding_work_is_never_a_removal_candidate(repo: Path, db: Path) -> None:
    """This is the checkpoint case: work left behind by a session that ended
    without wrapping is preserved, never swept into someone else's commit."""
    _bind(db, SENV_A)
    state = open_worktree(repo, SENV_A, db_path=db, base="develop")
    (state.path / "seed.txt").write_text("unfinished work\n", encoding="utf-8")
    _retire(db, SENV_A)

    after = _find(classify_worktrees(repo, db), state.path)
    assert after.classification == "abandoned_with_work"
    assert after.candidate_action == "preserve_then_close"
    assert after.tracked_dirty == 1


def test_an_unmerged_commit_holds_the_checkout_open(repo: Path, db: Path) -> None:
    """A clean tree is not enough: a commit not yet in the integration head is
    work too, and removing the checkout would strand it."""
    _bind(db, SENV_A)
    state = open_worktree(repo, SENV_A, db_path=db, base="develop")
    (state.path / "new.txt").write_text("committed in the session\n", encoding="utf-8")
    _git(state.path, "add", "new.txt")
    _git(state.path, "commit", "-qm", "session work")
    _retire(db, SENV_A)

    after = _find(classify_worktrees(repo, db), state.path)
    assert after.tracked_dirty == 0
    assert after.head_is_ancestor is False
    assert after.classification == "abandoned_with_work"


def test_a_work_item_named_checkout_is_unowned_and_only_reported(repo: Path, db: Path) -> None:
    """All 46 checkouts predating this module are in this class."""
    legacy = repo / ".worktrees" / "wi7805-ownership-bias-census"
    # Detached, exactly as 28 of the 46 real ones are.
    _git(repo, "worktree", "add", "-q", "--detach", str(legacy), "develop")
    after = _find(classify_worktrees(repo, db), legacy)
    assert after.classification == "unowned"
    assert after.candidate_action == "report_only"
    assert after.session_context_id is None


def test_a_directory_git_does_not_know_about_is_an_orphan(repo: Path, db: Path) -> None:
    orphan = repo / ".worktrees" / "tmp-red-7680"
    orphan.mkdir(parents=True)
    (orphan / "stray.txt").write_text("x\n", encoding="utf-8")
    after = _find(classify_worktrees(repo, db), orphan)
    assert after.classification == "orphaned_checkout"
    assert after.candidate_action == "report_only"


def test_the_main_tree_is_not_classified_as_a_session_checkout(repo: Path, db: Path) -> None:
    assert _find(classify_worktrees(repo, db), repo) is None


# --- close ------------------------------------------------------------------


def test_close_removes_a_clean_checkout_and_its_branch(repo: Path, db: Path) -> None:
    _bind(db, SENV_A)
    state = open_worktree(repo, SENV_A, db_path=db, base="develop")
    _retire(db, SENV_A)
    close_worktree(repo, SENV_A, db_path=db)

    assert not state.path.exists()
    branches = subprocess.run(
        ["git", "branch", "--list", session_branch(SENV_A)],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert branches == ""


def test_close_refuses_a_checkout_holding_work_and_destroys_nothing(repo: Path, db: Path) -> None:
    """The single most important assertion in this module."""
    _bind(db, SENV_A)
    state = open_worktree(repo, SENV_A, db_path=db, base="develop")
    (state.path / "seed.txt").write_text("unfinished work\n", encoding="utf-8")

    with pytest.raises(SessionWorktreeError) as excinfo:
        close_worktree(repo, SENV_A, db_path=db)

    assert excinfo.value.code == "holds_work"
    assert state.path.is_dir()
    assert (state.path / "seed.txt").read_text(encoding="utf-8") == "unfinished work\n"


def test_close_refuses_when_a_commit_is_not_yet_integrated(repo: Path, db: Path) -> None:
    _bind(db, SENV_A)
    state = open_worktree(repo, SENV_A, db_path=db, base="develop")
    (state.path / "new.txt").write_text("committed\n", encoding="utf-8")
    _git(state.path, "add", "new.txt")
    _git(state.path, "commit", "-qm", "session work")

    with pytest.raises(SessionWorktreeError) as excinfo:
        close_worktree(repo, SENV_A, db_path=db)
    assert excinfo.value.code == "holds_work"
    assert state.path.is_dir()


def test_close_on_a_session_with_no_checkout_is_a_typed_refusal(repo: Path, db: Path) -> None:
    with pytest.raises(SessionWorktreeError) as excinfo:
        close_worktree(repo, SENV_A, db_path=db)
    assert excinfo.value.code == "no_worktree"


def test_show_returns_none_before_a_checkout_exists(repo: Path, db: Path) -> None:
    assert show_worktree(repo, SENV_A, db_path=db) is None
