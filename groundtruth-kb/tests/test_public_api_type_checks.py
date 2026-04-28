"""Phase 4B.4: regression guard for public API mypy strict cleanliness.

Pins mypy --strict to green on the 4 public API source files so future
changes cannot silently regress the type surface. Skipped if mypy is
not installed (opt-in regression guard, not hard dependency).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def _clean_subprocess_env() -> dict[str, str]:
    """Return an env dict with coverage.py instrumentation vars stripped.

    Phase 4B.8 discovery: when this test runs inside a pytest-cov-instrumented
    suite, pytest-cov sets COV_CORE_* / COVERAGE_* env vars that are inherited
    by subprocess calls. mypy on Windows crashes with STATUS_ACCESS_VIOLATION
    (exit 3221225477) when it sees those vars, even though a direct shell
    invocation of the same mypy command succeeds. Stripping coverage-related
    vars from the subprocess env resolves the crash.
    """
    return {k: v for k, v in os.environ.items() if not (k.startswith("COV_") or k.startswith("COVERAGE_"))}


PUBLIC_API_FILES = [
    "src/groundtruth_kb/db.py",
    "src/groundtruth_kb/config.py",
    "src/groundtruth_kb/cli.py",
    "src/groundtruth_kb/gates.py",
]


def test_public_api_mypy_strict_is_clean() -> None:
    """mypy --strict must report zero errors on the public API surface.

    Phase 4B.4 closed 48 baseline errors (46 at Phase 4A baseline, 48
    at implementation-start head after Phase 4B.1–4B.3 edits). This test
    pins the guarantee so future changes to db.py / config.py / cli.py /
    gates.py cannot silently regress the type surface.
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
        [sys.executable, "-m", "mypy", "--strict", "--no-incremental"] + PUBLIC_API_FILES,
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        # Strip COV_CORE_* / COVERAGE_* env vars to prevent the mypy-crash-under-
        # coverage-instrumentation failure mode on Windows (STATUS_ACCESS_VIOLATION
        # exit 3221225477). See _clean_subprocess_env docstring.
        env=_clean_subprocess_env(),
    )
    assert result.returncode == 0, (
        f"mypy --strict found issues on the public API surface:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
