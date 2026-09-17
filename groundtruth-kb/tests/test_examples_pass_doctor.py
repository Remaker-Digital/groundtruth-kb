# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Verify the clean example trees against the public doctor surface.

Verification includes the public doctor surface (`run_doctor` or `gt project doctor`), not only
`run_isolation_checks`. The former `existing-adopter-migration` example documented the retired
receipt/rollback upgrade (O-7 R18) and is retired with it; a legacy adopter joins a host by registering the
application and initializing it with `gt project init`.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from groundtruth_kb.project.doctor import run_doctor

_EXAMPLES_ROOT = Path(__file__).resolve().parents[1] / "examples"
_CLEAN_EXAMPLES: tuple[tuple[str, str], ...] = (
    ("clean-adopter-minimal", "local-only"),
    ("adopter-with-transport-tests", "dual-agent"),
    ("adopter-with-release-gate", "dual-agent"),
)


def _isolation_checks(target: Path, profile: str) -> dict[str, str]:
    """Return ``{check_name: status}`` for `isolation:*` checks via the public doctor surface."""
    report = run_doctor(target, profile)
    return {c.name: c.status for c in report.checks if c.name.startswith("isolation:")}


def _setup_git(target: Path) -> None:
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=target, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=target, check=True)
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "pre-test snapshot", "--allow-empty"],
        cwd=target,
        check=True,
        capture_output=True,
    )


@pytest.mark.parametrize(("example_name", "profile"), _CLEAN_EXAMPLES)
def test_clean_example_doctor_isolation_checks_have_no_failures(
    tmp_path: Path, example_name: str, profile: str
) -> None:
    """Each clean example: every `isolation:*` check returns pass / info / warning, never fail.

    The example tree is copied into ``tmp_path`` so the doctor's product_root
    (which is `_PRODUCT_ROOT = groundtruth-kb/`) does not contain the adopter,
    avoiding spurious `isolation:adopter-root-placement` failures.
    """
    src = _EXAMPLES_ROOT / example_name
    adopter = tmp_path / example_name
    shutil.copytree(src, adopter)

    statuses = _isolation_checks(adopter, profile)
    failed = [name for name, status in statuses.items() if status == "fail"]
    assert not failed, (
        f"{example_name}: clean example must not produce isolation:* failures; "
        f"got fails={failed}; full statuses={statuses}"
    )
    # And the orchestrator must have actually emitted isolation checks.
    assert statuses, f"{example_name}: run_doctor returned no isolation:* checks"
