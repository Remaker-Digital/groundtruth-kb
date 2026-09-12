"""WI-5638: Committed terminal archive dispatch reconciliation tests.

Proves that committed terminal archive verdicts are excluded from live
queue surfaces while unrelated live work remains actionable.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GTKB_SRC = REPO_ROOT / "groundtruth-kb" / "src"
SCRIPTS = REPO_ROOT / "scripts"
if str(GTKB_SRC) not in sys.path:
    sys.path.insert(0, str(GTKB_SRC))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _init_git_repo(project_root: Path) -> None:
    """Initialize a minimal Git repository for synthetic archive tests."""
    subprocess.run(
        ["git", "-C", str(project_root), "init", "-b", "main"],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project_root), "config", "user.email", "test@example.com"],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project_root), "config", "user.name", "Test"],
        capture_output=True,
        check=True,
    )


def _git_commit_all(project_root: Path, message: str = "commit") -> None:
    subprocess.run(
        ["git", "-C", str(project_root), "add", "-A"],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project_root), "commit", "-m", message],
        capture_output=True,
        check=True,
    )


# ---------------------------------------------------------------------------
# Import the helpers once at module level for the direct tests.
# Tests that need a *clean* module state should use a subprocess approach
# instead of re-importing.
# ---------------------------------------------------------------------------
from groundtruth_kb.bridge.versioned_files import (  # noqa: E402
    classify_committed_archive_verdicts,
)


def test_dirty_archive_file_not_trusted(tmp_path: Path) -> None:
    """A modified (dirty) archive file is not trusted."""
    project_root = tmp_path / "repo"
    project_root.mkdir()
    _init_git_repo(project_root)

    archive_dir = project_root / "archive" / "bridge-terminal-verdicts"
    archive_dir.mkdir(parents=True)
    archive_path = archive_dir / "dirty-slug-009.md"
    archive_path.write_text(
        "VERIFIED\n\nDocument: dirty-slug\nVersion: 009\nVerdict.\n",
        encoding="utf-8",
    )

    _git_commit_all(project_root)

    # Dirty the file
    archive_path.write_text("MODIFIED CONTENT\n", encoding="utf-8")

    verdicts = classify_committed_archive_verdicts(project_root)
    assert "dirty-slug" not in verdicts


def test_nonterminal_archive_file_not_trusted(tmp_path: Path) -> None:
    """Non-terminal first status is not trusted."""
    project_root = tmp_path / "repo"
    project_root.mkdir()
    _init_git_repo(project_root)

    archive_dir = project_root / "archive" / "bridge-terminal-verdicts"
    archive_dir.mkdir(parents=True)
    (archive_dir / "nt-slug-004.md").write_text(
        "GO\n\nDocument: nt-slug\nVersion: 004\nNot terminal.\n",
        encoding="utf-8",
    )

    _git_commit_all(project_root)

    verdicts = classify_committed_archive_verdicts(project_root)
    assert "nt-slug" not in verdicts


def test_mismatched_document_field_not_trusted(tmp_path: Path) -> None:
    """Document: field must match filename slug."""
    project_root = tmp_path / "repo"
    project_root.mkdir()
    _init_git_repo(project_root)

    archive_dir = project_root / "archive" / "bridge-terminal-verdicts"
    archive_dir.mkdir(parents=True)
    (archive_dir / "real-slug-007.md").write_text(
        "VERIFIED\n\nDocument: other-slug\nVersion: 007\nMismatch.\n",
        encoding="utf-8",
    )

    _git_commit_all(project_root)

    verdicts = classify_committed_archive_verdicts(project_root)
    assert "real-slug" not in verdicts


def test_uncommitted_archive_file_not_trusted(tmp_path: Path) -> None:
    """An untracked archive file is not trusted."""
    project_root = tmp_path / "repo"
    project_root.mkdir()
    _init_git_repo(project_root)

    # Need at least one tracked file for the commit to succeed
    (project_root / "README.md").write_text("repo\n", encoding="utf-8")
    _git_commit_all(project_root)

    archive_dir = project_root / "archive" / "bridge-terminal-verdicts"
    archive_dir.mkdir(parents=True)
    (archive_dir / "untracked-slug-002.md").write_text(
        "VERIFIED\n\nDocument: untracked-slug\nVersion: 002\nVerdict.\n",
        encoding="utf-8",
    )
    # Not committed

    verdicts = classify_committed_archive_verdicts(project_root)
    assert "untracked-slug" not in verdicts
