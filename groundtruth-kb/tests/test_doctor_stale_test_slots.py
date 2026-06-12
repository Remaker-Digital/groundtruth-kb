# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.project.checks.stale_test_slots."""

from __future__ import annotations

import os
import time
from pathlib import Path

from groundtruth_kb.project.checks.stale_test_slots import check_stale_test_slots
from groundtruth_kb.project.doctor import ToolCheck


def test_check_stale_test_slots_empty_no_apps(tmp_path: Path) -> None:
    """If there is no applications/ directory, the check passes with no staleness message."""
    res = check_stale_test_slots(tmp_path)
    assert isinstance(res, ToolCheck)
    assert res.status == "pass"
    assert "no applications/ directory" in res.message


def test_check_stale_test_slots_pruning(tmp_path: Path) -> None:
    """Leaked test slots (>24h) are pruned, fresh ones (<24h) and real apps are ignored."""
    apps_dir = tmp_path / "applications"
    apps_dir.mkdir()

    # Create stale test slot
    stale_slot = apps_dir / "_test_stale_slot"
    stale_slot.mkdir()
    stale_file = stale_slot / "some_git_file"
    stale_file.write_text("dummy", encoding="utf-8")

    # Create fresh test slot
    fresh_slot = apps_dir / "_test_fresh_slot"
    fresh_slot.mkdir()

    # Create real app directory (should not be touched regardless of age)
    real_app = apps_dir / "my_production_app"
    real_app.mkdir()

    # Set mtime back 25 hours for stale_slot and real_app
    stale_mtime = time.time() - (25 * 3600)
    os.utime(stale_slot, (stale_mtime, stale_mtime))
    os.utime(real_app, (stale_mtime, stale_mtime))

    # Run check
    res = check_stale_test_slots(tmp_path)

    # Assert stale is gone, others remain
    assert not stale_slot.exists()
    assert fresh_slot.exists()
    assert real_app.exists()

    assert res.status == "warning"
    assert "pruned 1 stale _test_* slot(s)" in res.message
