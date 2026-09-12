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


def _status(repo: Path) -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


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


def _write_sot_registry(repo: Path) -> None:
    registry_dir = repo / "config" / "registry"
    registry_dir.mkdir(parents=True)
    (registry_dir / "sot-artifacts.toml").write_text(
        """
[[artifacts]]
id = "owner-local-env"
domain = "runtime_state"
lifecycle = "active"
storage_path = ".env.local"
coverage_mode = "exact"
authority_spec_id = "GOV-ENV-LOCAL-AUTHORITY-001"
mutation_api = "owner-managed local file; GT-KB records path authority only"
versioning_policy = "overwrite_single_writer"
backup_policy = "gitignored_runtime"
health_check_function = ""
owner_role = "owner_only"
notes = ".env.local is preserved by cleanup scans without reading or serializing credential values."
""".lstrip(),
        encoding="utf-8",
    )


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


def test_parse_stash_entries_uses_epoch_timestamp() -> None:
    report = parse_stash_entries("stash@{0}\t1782684000\tWIP on branch\n")

    assert len(report) == 1
    assert report[0].stash_ref == "stash@{0}"
    assert report[0].created_at == datetime.fromtimestamp(1782684000, UTC)
    assert report[0].subject == "WIP on branch"
