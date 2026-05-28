"""Drift-prevention regression guard for rehearsal package lint state.

Per ``bridge/gtkb-rehearsal-package-ruff-clean-001.md`` (REVISED-1 GO at
``-002``): the rehearsal package + driver + common-validation test must
remain ruff-check clean and ruff-format clean. This test fails fast if
debt accumulates again, preventing the silent-drift pattern that LO
flagged in S313.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RUFF_TARGETS: tuple[str, ...] = (
    "scripts/rehearse",
    "scripts/rehearse_isolation.py",
    "tests/scripts/test_rehearse_common_validation.py",
)


def test_rehearse_package_passes_ruff_check() -> None:
    """Run ``ruff check`` against the rehearsal package surface.

    If this fails, run ``python -m ruff check <targets> --fix`` and
    inspect the diff before re-running tests.
    """
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *_RUFF_TARGETS],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"ruff check found issues:\n{result.stdout}\n{result.stderr}"
    )


def test_rehearse_package_passes_ruff_format_check() -> None:
    """Run ``ruff format --check`` against the rehearsal package surface."""
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", *_RUFF_TARGETS],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"ruff format --check found unformatted files:\n"
        f"{result.stdout}\n{result.stderr}"
    )
