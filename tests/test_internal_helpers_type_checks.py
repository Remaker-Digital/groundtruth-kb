"""Phase 4B.5b: regression guard for internal-helper mypy strict cleanliness.

Pins mypy --strict to green on the five internal-helper source files so future
changes cannot silently regress the type surface. Skipped if mypy is not
installed (opt-in regression guard, not hard dependency).

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

INTERNAL_HELPER_FILES = [
    "src/groundtruth_kb/seed.py",
    "src/groundtruth_kb/web/app.py",
    "src/groundtruth_kb/reconciliation.py",
    "src/groundtruth_kb/spec_scaffold.py",
    "src/groundtruth_kb/project/scaffold.py",
]


def test_internal_helpers_mypy_strict_is_clean() -> None:
    """mypy --strict must report zero errors on the internal-helper surface.

    Phase 4B.5b closed 40 baseline errors across the five named files. This
    test pins the guarantee so future changes cannot silently regress the type
    surface. Uses --follow-imports=silent to avoid pulling in the full
    transitive dependency graph (matching the empirical baseline established
    in bridge/gtkb-phase4b5b-internal-helpers-mypy-002.md).
    """
    if shutil.which("mypy") is None:
        try:
            import importlib.util

            if importlib.util.find_spec("mypy") is None:
                pytest.skip("mypy not installed; install via pip install '.[dev]'")
        except Exception:
            pytest.skip("mypy not installed; install via pip install '.[dev]'")

    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--strict",
            "--follow-imports=silent",
            "--no-incremental",
        ]
        + INTERNAL_HELPER_FILES,
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"mypy --strict found issues on internal helpers:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
