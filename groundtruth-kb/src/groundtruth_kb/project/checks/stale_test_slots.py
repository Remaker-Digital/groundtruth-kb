# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Check for stale test-sandbox slots (ADR-REGISTRY-DISCOVERY-001)."""

from __future__ import annotations

import os
import shutil
import stat
import sys
import time
from pathlib import Path
from typing import Any

from groundtruth_kb.project.checks import register_check
from groundtruth_kb.project.doctor import ToolCheck

_TEST_SLOT_STALE_SECONDS = 24 * 3600


def _force_remove_tree(path: Path) -> None:
    """Remove a directory tree, clearing read-only bits (Windows .git) then retrying."""

    def _on_rm_error(func: Any, p: Any, exc: BaseException) -> None:
        os.chmod(p, stat.S_IWRITE)
        func(p)

    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_on_rm_error)
    else:
        shutil.rmtree(
            path,
            onerror=lambda func, p, exc_info: _on_rm_error(func, p, exc_info[1]),
        )


@register_check("stale_test_slots")
def check_stale_test_slots(target: Path) -> ToolCheck:
    """Auto-prune leaked clean-adopter test sandboxes (FAB-08 / HYG-053).

    Detects ``applications/_test_*`` slots older than 24h — the clean-adopter
    fixture leak signature — and prunes them, emitting a WARN listing what was
    removed. Deletes ONLY ``_test_*`` directories directly under
    ``applications/``; never a real application subtree.
    """
    name = "Stale test-sandbox auto-prune (applications/_test_*)"
    apps_dir = target / "applications"
    if not apps_dir.is_dir():
        return ToolCheck(name=name, required=False, found=True, status="pass", message="no applications/ directory")
    now = time.time()
    pruned: list[str] = []
    failed: list[str] = []
    for child in sorted(apps_dir.glob("_test_*")):
        # Defense-in-depth: only ever touch _test_*-named dirs directly under applications/.
        if not child.is_dir() or child.parent != apps_dir or not child.name.startswith("_test_"):
            continue
        try:
            age = now - child.stat().st_mtime
        except OSError:
            continue
        if age <= _TEST_SLOT_STALE_SECONDS:
            continue
        try:
            _force_remove_tree(child)
            pruned.append(child.name)
        except OSError as exc:
            failed.append(f"{child.name} ({exc})")
    if not pruned and not failed:
        return ToolCheck(name=name, required=False, found=True, status="pass", message="no stale _test_* slots (>24h)")
    shown = ", ".join(pruned[:10]) + (" ..." if len(pruned) > 10 else "")
    message = f"pruned {len(pruned)} stale _test_* slot(s) >24h: {shown}"
    if failed:
        message += f"; {len(failed)} could not be removed: {', '.join(failed[:5])}"
    return ToolCheck(name=name, required=False, found=True, status="warning", message=message)
