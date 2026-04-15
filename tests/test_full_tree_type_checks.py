"""Phase 4B.7: regression guard — mypy --strict on the full src tree.

Replaces test_public_api_type_checks.py (public API surface only) with a
broader guard that keeps all 31 source files strictly clean. Skipped if
mypy is not installed (opt-in regression guard, not hard dependency).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

FULL_TREE_TARGET = "src/groundtruth_kb/"


def test_full_tree_mypy_strict_is_clean() -> None:
    """mypy --strict must report zero errors on the full src/groundtruth_kb/ tree.

    Phase 4B.7 closed 39 residual strict-mypy errors across 5 files
    (bridge/poller.py, bridge/worker.py, intake.py, bridge/runtime.py,
    bridge/context.py). This test pins the guarantee so future changes
    to any module cannot silently regress the full-tree type surface.

    Previously test_public_api_type_checks.py covered only the 4 public
    API files (db.py, config.py, cli.py, gates.py). That narrower guard
    remains active; this test extends coverage to the full tree.
    """
    # Check for mypy availability: prefer PATH executable, fall back to module.
    if shutil.which("mypy") is None:
        try:
            import importlib.util

            if importlib.util.find_spec("mypy") is None:
                pytest.skip("mypy not installed; install via pip install '.[dev]'")
        except Exception:
            pytest.skip("mypy not installed; install via pip install '.[dev]'")

    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", "--no-incremental", FULL_TREE_TARGET],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, (
        f"mypy --strict found issues on the full src/groundtruth_kb/ tree:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
