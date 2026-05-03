# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Phase 9 §5 line 238: ``upgrade applies registry diff under receipts``.

Spec: ``gt project upgrade`` restores missing managed files declared in the
registry AND records a rollback receipt under
``.claude/upgrade-receipts/active/`` after the merge.

Outside-in surface: ``plan_upgrade`` (public) + ``execute_upgrade`` (public)
+ filesystem inspection of the receipt directory.

Authority: ``bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md`` GO.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from groundtruth_kb.project.upgrade import execute_upgrade, plan_upgrade

from .conftest import _setup_git


def _commit_all(adopter: Path, message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=adopter, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=adopter, check=True, capture_output=True)


def test_upgrade_restores_missing_managed_file_and_writes_receipt(
    clean_adopter: tuple[Path, Path], tmp_path: Path
) -> None:
    """Delete a managed hook → upgrade restores it + writes a v1 receipt."""
    adopter, _ = clean_adopter
    managed_file = adopter / ".claude" / "hooks" / "assertion-check.py"
    assert managed_file.exists(), "scaffold should have produced the managed hook"

    _setup_git(adopter)
    managed_file.unlink()
    _commit_all(adopter, "delete managed hook")

    actions = plan_upgrade(adopter)
    restoring = [a for a in actions if a.file == ".claude/hooks/assertion-check.py"]
    assert restoring, (
        f"plan_upgrade must surface a restoring action for the deleted managed "
        f"hook; got files={sorted({a.file for a in actions})}"
    )

    # ``enforce_isolation=False`` scopes this test to the file-action +
    # receipt mechanics. The in-root sandbox triggers
    # ``isolation:no-writable-product-paths`` (NEEDS-ADOPTER-INPUT, no
    # auto-fixer) which would otherwise hard-refuse the upgrade. Slice 4's
    # tests cover the isolation-pre-flight and auto-fixer paths;
    # ``test_doctor_detects_isolation_violations.py`` covers detection.
    execute_upgrade(adopter, actions, product_root=tmp_path, enforce_isolation=False)

    assert managed_file.exists(), "upgrade did not restore the deleted managed hook"

    receipts_dir = adopter / ".claude" / "upgrade-receipts" / "active"
    assert receipts_dir.exists(), "upgrade did not create the receipts directory"
    receipt_files = list(receipts_dir.glob("*.json"))
    assert len(receipt_files) == 1, f"expected exactly one receipt; got {len(receipt_files)}: {receipt_files}"

    receipt = json.loads(receipt_files[0].read_text(encoding="utf-8"))
    assert receipt["schema_version"] == "v1"
    assert isinstance(receipt["merge_commit"], str) and len(receipt["merge_commit"]) == 40
    assert receipt["mode"] in ("tracked", "filesystem")
    assert isinstance(receipt["artifact_classes_touched"], list)
