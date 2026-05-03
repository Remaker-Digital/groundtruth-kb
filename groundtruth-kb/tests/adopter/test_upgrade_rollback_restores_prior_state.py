# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Phase 9 §5 line 240: ``upgrade rollback restores prior state``.

Spec: after ``gt project upgrade --apply`` + ``gt project rollback``, the
adopter tree returns to its pre-upgrade state byte-for-byte.

Outside-in surface: ``plan_upgrade`` + ``execute_upgrade`` + ``plan_rollback``
+ ``execute_rollback``. The receipt-write/read flow is end-to-end.

Authority: ``bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md`` GO.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from groundtruth_kb.project.rollback import (
    execute_rollback,
    find_latest_receipt,
    plan_rollback,
)
from groundtruth_kb.project.upgrade import execute_upgrade, plan_upgrade

from .conftest import _setup_git


def _commit_all(adopter: Path, message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=adopter, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=adopter, check=True, capture_output=True)


def test_rollback_restores_pre_upgrade_state(clean_adopter: tuple[Path, Path], tmp_path: Path) -> None:
    """Delete a managed file → upgrade restores it → rollback removes it again."""
    adopter, _ = clean_adopter
    managed_file = adopter / ".claude" / "hooks" / "assertion-check.py"
    assert managed_file.exists()

    _setup_git(adopter)
    managed_file.unlink()
    _commit_all(adopter, "delete managed hook")
    assert not managed_file.exists()

    actions = plan_upgrade(adopter)
    # See test_upgrade_applies_registry_diff_under_receipts.py for the
    # ``enforce_isolation=False`` rationale.
    execute_upgrade(adopter, actions, product_root=tmp_path, enforce_isolation=False)
    assert managed_file.exists(), "upgrade should have restored the deleted file"

    receipt = find_latest_receipt(adopter)
    assert receipt is not None, "no receipt found after successful upgrade"

    plan = plan_rollback(adopter, receipt_id=receipt["receipt_id"])
    execute_rollback(adopter, plan, commit=True)

    assert not managed_file.exists(), (
        f"rollback did not remove the file restored by upgrade; {managed_file} still present"
    )
