"""Drift-prevention regression guard for the GT-KB platform tree.

Per ``bridge/gtkb-ruff-format-check-pre-commit-drift-clear-001.md`` and
the Loyal Opposition GO at ``-002``, the ``groundtruth-kb/`` tree must remain
ruff-check clean and ruff-format clean.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RUFF_TARGET = "groundtruth-kb/"


def test_groundtruth_kb_passes_ruff_check() -> None:
    """Run ``ruff check`` against the GT-KB platform tree."""
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", _RUFF_TARGET],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"ruff check found issues:\n{result.stdout}\n{result.stderr}"


def test_groundtruth_kb_passes_ruff_format_check() -> None:
    """Run ``ruff format --check`` against the GT-KB platform tree."""
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", _RUFF_TARGET],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"ruff format --check found unformatted files:\n{result.stdout}\n{result.stderr}"
