"""Frozen black-box acceptance for the modernization Git lifecycle service."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "check_modernization_git_lifecycle.py"
EXPECTED = {f"GIT-LIFECYCLE-A{i}" for i in range(1, 27)}


@pytest.mark.timeout(180)
def test_frozen_modernization_git_lifecycle_contract() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=900,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assertions = {item["id"]: item for item in report["assertions"]}
    assert report["capability"] == "CAP-GIT-LIFECYCLE"
    assert report["status"] == "PASS"
    assert set(assertions) == EXPECTED
    assert all(item["status"] == "PASS" and item["evidence"] for item in assertions.values())
