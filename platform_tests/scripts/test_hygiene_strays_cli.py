"""Tests for the WI-4356 ``gt hygiene strays`` dry-run CLI."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.hygiene.strays import parse_stash_entries

NOW = datetime(2026, 6, 5, 12, 0, 0, tzinfo=UTC)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _init_repo(repo: Path) -> Path:
    _git(repo, "init")
    _git(repo, "config", "user.email", "gtkb-tests@example.invalid")
    _git(repo, "config", "user.name", "GTKB Tests")
    (repo / "tracked.txt").write_text("initial\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-m", "initial")
    return repo


def _old_mtime(path: Path, *, hours: int = 13) -> None:
    old = (NOW - timedelta(hours=hours)).timestamp()
    os.utime(path, (old, old))


def _run_strays(repo: Path, *extra: str) -> dict[str, object]:
    result = CliRunner().invoke(
        main,
        [
            "hygiene",
            "strays",
            "--root",
            str(repo),
            "--format",
            "json",
            "--now",
            NOW.isoformat(),
            *extra,
        ],
    )
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def test_hygiene_strays_clean_repo_has_zero_findings(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    report = _run_strays(repo)

    assert report["candidate_actions_only"] is True
    assert report["source"]["read_only"] is True
    assert report["counts"]["workspace_total"] == 0
    assert report["counts"]["stash_total"] == 0
    assert report["counts"]["worktree_total"] == 0


def test_hygiene_strays_reports_stale_tracked_and_untracked_paths(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    tracked = repo / "tracked.txt"
    tracked.write_text("changed\n", encoding="utf-8")
    untracked = repo / "stray.txt"
    untracked.write_text("left behind\n", encoding="utf-8")
    _old_mtime(tracked)
    _old_mtime(untracked)

    report = _run_strays(repo)

    by_path = {finding["path"]: finding for finding in report["workspace_findings"]}
    assert report["counts"]["workspace_stale"] == 2
    assert by_path["tracked.txt"]["classification"] == "stale"
    assert by_path["tracked.txt"]["tracked"] is True
    assert by_path["stray.txt"]["classification"] == "stale"
    assert by_path["stray.txt"]["tracked"] is False


def test_hygiene_strays_active_workspace_path_is_not_stale(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    held = repo / "held.txt"
    held.write_text("still in use\n", encoding="utf-8")
    _old_mtime(held)

    report = _run_strays(repo, "--active-workspace-path", "held.txt")

    finding = report["workspace_findings"][0]
    assert report["counts"]["workspace_stale"] == 0
    assert report["counts"]["workspace_active_session"] == 1
    assert finding["classification"] == "active_session"
    assert finding["candidate_action"] == "skip"


def test_hygiene_strays_reports_orphaned_worktree_directory(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    orphan = repo / ".claude" / "worktrees" / "stale-checkout"
    orphan.mkdir(parents=True)
    _old_mtime(orphan)

    report = _run_strays(repo)

    assert report["counts"]["worktree_stale"] == 1
    finding = report["worktree_findings"][0]
    assert finding["path"] == ".claude/worktrees/stale-checkout"
    assert finding["classification"] == "stale"
    assert finding["candidate_action"] == "prune_and_delete_orphaned_worktree"


def test_parse_stash_entries_uses_epoch_timestamp() -> None:
    report = parse_stash_entries("stash@{0}\t1782684000\tWIP on branch\n")

    assert len(report) == 1
    assert report[0].stash_ref == "stash@{0}"
    assert report[0].created_at == datetime.fromtimestamp(1782684000, UTC)
    assert report[0].subject == "WIP on branch"
