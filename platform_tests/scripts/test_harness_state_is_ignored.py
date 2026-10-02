"""c123 (batch design WP5, G44(a)): git ignores the retired harness-state tree whole.

Nothing under harness-state/ is tracked, the native bridge refuses its paths as targets, and the commit checker refuses
them in pathspecs, so the tree is retired runtime residue. .gitignore ignores it whole instead of keeping some of its
files visible as durable controls. This replaces test_session_envelope_git_disposition.py, which pinned that
visibility.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _check_ignore(path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "check-ignore", "--no-index", "-v", path], cwd=ROOT, text=True, capture_output=True, check=False
    )


@pytest.mark.parametrize(
    "path",
    [
        "harness-state/harness-registry.json",
        "harness-state/codex/operating-role.md",
        "harness-state/claude/session-envelopes/x.json",
    ],
)
def test_harness_state_paths_are_ignored(path: str) -> None:
    result = _check_ignore(path)

    assert result.returncode == 0, (path, result.stdout, result.stderr)
    assert ".gitignore" in result.stdout


def test_a_tracked_root_file_stays_visible() -> None:
    result = _check_ignore("README.md")

    assert result.returncode == 1, (result.stdout, result.stderr)
