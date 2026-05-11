"""W1 performance bound: <30s on the live repository.

This test runs the scanner against the actual project root. Excluded
from the release-candidate gate because (a) it depends on live repo
size and (b) the fixture-based skip-dirs test inside the gate provides
the real correctness assurance.

Run via ``pytest -m perf`` or a separate CI workflow target.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest


PERF_BOUND_SECONDS = 30
HARD_TIMEOUT_SECONDS = 60


@pytest.mark.perf
def test_wrap_scan_hygiene_completes_within_bound() -> None:
    project_root = Path(__file__).resolve().parents[2]
    start = time.monotonic()
    result = subprocess.run(
        [sys.executable, "scripts/wrap_scan_hygiene.py", "--report-format", "json"],
        capture_output=True,
        text=True,
        timeout=HARD_TIMEOUT_SECONDS,
        cwd=project_root,
    )
    elapsed = time.monotonic() - start
    assert elapsed < PERF_BOUND_SECONDS, (
        f"W1 took {elapsed:.1f}s; bound is {PERF_BOUND_SECONDS}s. "
        "Investigate SKIP_DIRS / SCAN_ROOTS scope or scan-glob breadth."
    )
    assert result.returncode in (0, 2), (
        f"Unexpected exit {result.returncode}: stderr={result.stderr[:200]}"
    )
