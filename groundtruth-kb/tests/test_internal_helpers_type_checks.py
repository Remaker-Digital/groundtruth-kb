"""Phase 4B.5b: regression guard for internal-helper mypy strict cleanliness.

Pins mypy --strict to green on the five internal-helper source files so future
changes cannot silently regress the type surface. Skipped if mypy is not
installed (opt-in regression guard, not hard dependency).

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
    vars from the subprocess env resolves the crash and preserves everything
    else (PATH, PYTHONPATH, user site, etc.).
    """
    return {k: v for k, v in os.environ.items() if not (k.startswith("COV_") or k.startswith("COVERAGE_"))}


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
        # 300s accommodates the full coverage-instrumented suite (4B.8): under load,
        # a bare mypy subprocess takes ~24s but contends with other tests for CPU.
        # 4B.5b's original 120s was tight even before the full bridge test suite existed.
        timeout=300,
        # Strip COV_CORE_* / COVERAGE_* env vars to prevent the mypy-crash-under-
        # coverage-instrumentation failure mode on Windows (STATUS_ACCESS_VIOLATION
        # exit 3221225477). See _clean_subprocess_env docstring.
        env=_clean_subprocess_env(),
    )
    assert result.returncode == 0, (
        f"mypy --strict found issues on internal helpers:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
