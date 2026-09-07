"""Local machine state must be ignored, not swept into the index.

On 2026-09-07 a ``git add -A`` in the main tree staged 41 embedded worktree
checkouts as gitlinks, a 1.1 GB database backup, the semantic index, the
registry control-plane lock, and a registry backup, because none of them were
ignored. The patterns added to ``.gitignore`` that day are asserted here so the
hazard cannot silently return. The root ``bridge/`` anchor has its own test
(``test_gitignore_bridge_package_anchor.py``).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

IGNORED = (
    ".worktrees/some-branch/README.md",
    "groundtruth.db.pre-wi7781-20260904-161839",
    "config/registry/sot-artifacts.toml.pre-wi7781",
    "chroma_db/chroma.sqlite3",
    "groundtruth.db.registry-control-plane.lock",
    ".pytest-tmp/session/x.txt",
)
TRACKED_MUST_STAY_VISIBLE = (
    "config/registry/sot-artifacts.toml",
    "groundtruth-kb/src/groundtruth_kb/bridge/vocabulary.py",
    "scripts/check_dev_environment_inventory_drift.py",
)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _is_ignored(rel_path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", rel_path],
        capture_output=True,
        text=True,
        cwd=_project_root(),
    )
    return result.returncode == 0


@pytest.mark.parametrize("rel_path", IGNORED)
def test_local_state_is_ignored(rel_path: str) -> None:
    assert _is_ignored(rel_path), f"{rel_path} must be ignored: it is local machine state, not repository content"


@pytest.mark.parametrize("rel_path", TRACKED_MUST_STAY_VISIBLE)
def test_repository_content_is_not_ignored(rel_path: str) -> None:
    assert not _is_ignored(rel_path), f"{rel_path} is repository content and must not match a local-state pattern"
