"""Guard that platform_tests/scripts collects without ERROR (WI-6583 / GOV-10)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_scripts_dir_collection_has_zero_errors() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "platform_tests/scripts/",
            "--collect-only",
            "-q",
            "--tb=no",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    combined = f"{result.stdout}\n{result.stderr}"
    assert result.returncode == 0, combined
    lowered = combined.lower()
    assert "error during collection" not in lowered
    assert "error collecting" not in lowered
