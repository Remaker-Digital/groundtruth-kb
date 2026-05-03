# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GTKB-ISOLATION-017 Slice 7 — verify the 4 example trees against the public doctor surface.

Per bridge `gtkb-isolation-017-slice7-examples-2026-05-03-002.md` GO
condition 1: verification must include the public doctor surface
(`run_doctor` or `gt project doctor`), not only `run_isolation_checks`.

Per condition 2: `existing-adopter-migration` is verified in two phases:
first as the intended pre-isolation shape with named expected failures,
then via test evidence showing the documented upgrade path ends in a clean
post-migration state.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from groundtruth_kb.project.doctor import run_doctor
from groundtruth_kb.project.upgrade import execute_upgrade

_EXAMPLES_ROOT = Path(__file__).resolve().parents[1] / "examples"
_CLEAN_EXAMPLES: tuple[tuple[str, str], ...] = (
    ("clean-adopter-minimal", "local-only"),
    ("adopter-with-transport-tests", "dual-agent"),
    ("adopter-with-release-gate", "dual-agent"),
)

# Pre-isolation example fails these specific checks per its design.
_MIGRATION_EXPECTED_PRE_FAILURES: frozenset[str] = frozenset(
    {
        "isolation:service-endpoint",
        "isolation:work-subject",
        "isolation:workstream-focus-hook-absent",
        "isolation:release-readiness-app-subject-header",
    }
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


def test_migration_example_phase1_has_expected_pre_isolation_failures(tmp_path: Path) -> None:
    """Phase 1: the migration example's tree fails the documented isolation checks.

    This asserts the example is correctly shaped as a pre-isolation adopter.
    The set of expected failures comes from the WALKTHROUGH.md walkthrough +
    the Slice 4 partition.
    """
    src = _EXAMPLES_ROOT / "existing-adopter-migration"
    adopter = tmp_path / "existing-adopter-migration"
    shutil.copytree(src, adopter)

    statuses = _isolation_checks(adopter, "dual-agent")
    actual_non_pass = {name for name, status in statuses.items() if status in ("fail", "warning")}
    missing_expected = _MIGRATION_EXPECTED_PRE_FAILURES - actual_non_pass
    assert not missing_expected, (
        f"migration example missing expected pre-isolation failures: {missing_expected}; full statuses={statuses}"
    )


def test_migration_example_phase2_walkthrough_ends_in_clean_post_migration_state(
    tmp_path: Path,
) -> None:
    """Phase 2: applying the WALKTHROUGH.md upgrade ends in a clean post-migration state.

    Reproduces the WALKTHROUGH.md sequence end-to-end:
    copy example → init git → execute_upgrade(accept_migration=True) → re-run doctor.
    The post-state must clear the auto-fixable subset of pre-failures.
    """
    src = _EXAMPLES_ROOT / "existing-adopter-migration"
    adopter = tmp_path / "existing-adopter-migration"
    shutil.copytree(src, adopter)

    # Use a synthetic sibling product_root so check #1
    # (`isolation:adopter-root-placement`) does not hard-refuse: the adopter
    # at tmp_path/existing-adopter-migration/ is NOT a child of
    # tmp_path/_synthetic_product_root/. Mirrors Slice 5's
    # `_load_existing_adopter_into_tmp_path` pattern.
    product_root = tmp_path / "_synthetic_product_root"
    product_root.mkdir(parents=True, exist_ok=True)

    _setup_git(adopter)
    execute_upgrade(
        adopter,
        actions=[],
        accept_migration=True,
        product_root=product_root,
    )

    statuses = _isolation_checks(adopter, "dual-agent")
    auto_fixable_fails = [
        name for name, status in statuses.items() if name in _MIGRATION_EXPECTED_PRE_FAILURES and status == "fail"
    ]
    assert not auto_fixable_fails, (
        f"migration walkthrough did not clear auto-fixable failures; "
        f"residual fails={auto_fixable_fails}; full statuses={statuses}"
    )
    # The legacy hook file must be gone after the auto-fixer.
    assert not (adopter / ".claude" / "hooks" / "workstream-focus.py").exists(), (
        "auto-fixer should have deleted .claude/hooks/workstream-focus.py"
    )
