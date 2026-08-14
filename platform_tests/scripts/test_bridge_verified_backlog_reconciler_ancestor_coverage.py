"""VERIFIED closure coverage accepts ancestor commits (WI-6280).

Landed by bridge/gtkb-wi6280-verified-closure-ancestor-coverage (GO at -002).

The change loosens a gate, so the load-bearing assertions here are the negative
ones: work committed AFTER verification, or absent from the verdict commit's
history, must still fail closure. Without those, the widening would admit work
the verdict never verified.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _extra in (PROJECT_ROOT, PROJECT_ROOT / "groundtruth-kb" / "src"):
    if str(_extra) not in sys.path:
        sys.path.insert(0, str(_extra))

from scripts.bridge_verified_backlog_reconciler import (  # noqa: E402
    _terminal_verdict_commit_coverage,
)

VERDICT = "bridge/gtkb-fixture-thread-002.md"
IMPL = "scripts/fixture_implementation.py"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    )


def _write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _commit(repo: Path, rel: str, text: str, message: str) -> str:
    _write(repo, rel, text)
    _git(repo, "add", "--", rel)
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A git repo with one root commit, so later commits always have a parent."""
    root = tmp_path / "fixture-repo"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "fixture@example.invalid")
    _git(root, "config", "user.name", "Fixture")
    _commit(root, "README.md", "fixture\n", "chore: root commit")
    return root


def _coverage(repo: Path, targets: tuple[str, ...] = (IMPL,)) -> dict:
    return _terminal_verdict_commit_coverage(repo, VERDICT, targets)


def test_target_committed_in_ancestor_is_covered(repo: Path):
    """The defect case: implementation first, verdict later, separate commits."""
    _commit(repo, IMPL, "print('impl')\n", "feat: implementation")
    _commit(repo, VERDICT, "VERIFIED\n", "chore(bridge): finalize VERIFIED chain")

    result = _coverage(repo)
    assert result["covered"] is True, result
    assert result["missing_paths"] == []


def test_target_in_verdict_commit_remains_covered(repo: Path):
    """The pre-existing same-commit shape must keep working unchanged."""
    _write(repo, IMPL, "print('impl')\n")
    _write(repo, VERDICT, "VERIFIED\n")
    _git(repo, "add", "--", IMPL, VERDICT)
    _git(repo, "commit", "-m", "feat: implementation and verdict together")

    result = _coverage(repo)
    assert result["covered"] is True, result


def test_target_committed_after_verdict_is_not_covered(repo: Path):
    """Ancestry is the bound: work the verdict could not have verified fails.

    This is the assertion that keeps the widening honest.
    """
    _commit(repo, VERDICT, "VERIFIED\n", "chore(bridge): finalize VERIFIED chain")
    _commit(repo, IMPL, "print('later')\n", "feat: implementation AFTER the verdict")

    result = _coverage(repo)
    assert result["covered"] is False, result
    assert IMPL in result["missing_paths"]


def test_target_on_unrelated_branch_is_not_covered(repo: Path):
    """Work off the verdict commit's history does not count.

    Mechanically this fails because the path never enters HEAD's log, rather
    than via merge-base; the assertion is on the outcome, which is what the
    closure rule depends on.
    """
    _git(repo, "checkout", "-b", "sidebranch")
    _commit(repo, IMPL, "print('side')\n", "feat: implementation on a side branch")
    _git(repo, "checkout", "main")
    _commit(repo, VERDICT, "VERIFIED\n", "chore(bridge): finalize VERIFIED chain")

    result = _coverage(repo)
    assert result["covered"] is False, result
    assert IMPL in result["missing_paths"]


def test_never_committed_target_is_not_covered(repo: Path):
    """A declared target absent from history fails, ancestor rule notwithstanding."""
    _commit(repo, VERDICT, "VERIFIED\n", "chore(bridge): finalize VERIFIED chain")

    result = _coverage(repo)
    assert result["covered"] is False, result
    assert IMPL in result["missing_paths"]


def test_untracked_verdict_still_uncovered(repo: Path):
    """The verdict's own early returns are untouched by the widening."""
    _commit(repo, IMPL, "print('impl')\n", "feat: implementation")
    _write(repo, VERDICT, "VERIFIED\n")  # written, never committed

    result = _coverage(repo)
    assert result["covered"] is False, result
    assert result["verdict_state"] == "uncommitted_or_untracked"


def test_verdict_must_still_appear_in_its_own_commit(repo: Path):
    """The verdict may NOT be satisfied by an ancestor; only targets may.

    Regression guard for the narrowest part of the change: had the ancestor
    branch been applied to verdict_rel_path too, a thread whose verdict was
    committed in some earlier unrelated commit would close spuriously.
    """
    _commit(repo, VERDICT, "VERIFIED\n", "chore(bridge): verdict lands here")
    verdict_commit = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _commit(repo, IMPL, "print('impl')\n", "feat: later commit touches only impl")

    result = _terminal_verdict_commit_coverage(repo, VERDICT, (IMPL,))
    # The verdict's latest commit is still its own; coverage keys off that
    # commit, and IMPL is a descendant -> uncovered.
    assert result["commit"] == verdict_commit
    assert result["covered"] is False, result


def test_glob_target_matches_via_ancestor(repo: Path):
    """Glob targets keep ANY-match semantics across the ancestor path."""
    _commit(repo, IMPL, "print('impl')\n", "feat: implementation")
    _commit(repo, VERDICT, "VERIFIED\n", "chore(bridge): finalize VERIFIED chain")

    result = _coverage(repo, targets=("scripts/*.py",))
    assert result["covered"] is True, result
