# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Phase 9 §5 line 244: ``workstream-focus retired hook stays absent``.

Spec: the deprecated ``.claude/hooks/workstream-focus.py`` hook does NOT
appear in a clean scaffold and is NOT re-introduced by ``gt project upgrade``.

Outside-in surface: scaffold output + ``run_isolation_checks`` (check #6) +
``execute_upgrade``.

Authority: ``bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md`` GO.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from groundtruth_kb.project.doctor_isolation import run_isolation_checks
from groundtruth_kb.project.upgrade import execute_upgrade, plan_upgrade

from .conftest import _setup_git


def _commit_all(adopter: Path, message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=adopter, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=adopter, check=True, capture_output=True)


def test_workstream_focus_hook_absent_from_clean_scaffold(
    clean_adopter: tuple[Path, Path],
) -> None:
    """Clean scaffold has no legacy hook + check #6 passes."""
    adopter, doctor_root = clean_adopter
    legacy = adopter / ".claude" / "hooks" / "workstream-focus.py"
    assert not legacy.exists(), f"clean scaffold should not contain {legacy}"

    checks = run_isolation_checks(adopter, "dual-agent", product_root=doctor_root)
    by_name = {c.name: c for c in checks}
    assert by_name["isolation:workstream-focus-hook-absent"].status == "pass"


def test_upgrade_does_not_re_introduce_legacy_hook(clean_adopter: tuple[Path, Path], tmp_path: Path) -> None:
    """Run ``execute_upgrade`` from a clean state → legacy hook still absent.

    Trigger an upgrade action by deleting a managed file (so ``execute_upgrade``
    actually runs the file-action executor + receipt-write flow); afterwards
    confirm ``workstream-focus.py`` was not added by the upgrade.
    """
    adopter, _ = clean_adopter
    legacy = adopter / ".claude" / "hooks" / "workstream-focus.py"

    _setup_git(adopter)
    managed = adopter / ".claude" / "hooks" / "assertion-check.py"
    managed.unlink()
    _commit_all(adopter, "delete managed hook")

    actions = plan_upgrade(adopter)
    # See test_upgrade_applies_registry_diff_under_receipts.py for the
    # ``enforce_isolation=False`` rationale.
    execute_upgrade(adopter, actions, product_root=tmp_path, enforce_isolation=False)

    assert not legacy.exists(), f"{legacy} reappeared after upgrade; the deprecated hook must stay absent"
