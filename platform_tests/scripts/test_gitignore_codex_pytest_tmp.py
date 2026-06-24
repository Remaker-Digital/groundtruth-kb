"""Regression guard for Codex pytest/runtime temp roots.

WI-4757 covers root-level Codex temp directories that can be ACL-locked after
test or dispatch runs. Git must ignore those roots so status scans do not
descend into unreadable runtime byproducts.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

CODEX_TEMP_PATHS = (
    ".codex-pytest-tmp/auth-review-focused-20260622T0529/sentinel.txt",
    ".codex-pytest-tmp-wi4768-dispatch/sentinel.txt",
    ".codex-test-tmp-runtime/sentinel.txt",
    ".codex-test-tmp-self-init/sentinel.txt",
    ".codex_pytest_tmp/sentinel.txt",
)

CODEX_TEMP_PREFIXES = (
    ".codex-pytest-tmp",
    ".codex-test-tmp",
    ".codex_pytest_tmp/",
)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        check=False,
        cwd=_project_root(),
        text=True,
    )


def test_codex_temp_roots_are_gitignored() -> None:
    for test_path in CODEX_TEMP_PATHS:
        result = _git("check-ignore", "-v", test_path)

        assert result.returncode == 0, (
            f"Expected {test_path!r} to be gitignored. stdout: {result.stdout!r} stderr: {result.stderr!r}"
        )


def test_no_codex_temp_roots_are_tracked() -> None:
    result = _git("ls-files")
    assert result.returncode == 0, f"git ls-files failed: {result.stderr}"

    tracked_temp_paths = [path for path in result.stdout.splitlines() if path.startswith(CODEX_TEMP_PREFIXES)]

    assert tracked_temp_paths == [], (
        "Codex pytest/runtime temp roots must not be tracked. "
        "Remove these paths from the index:\n  " + "\n  ".join(tracked_temp_paths)
    )
