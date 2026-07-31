"""Frozen black-box acceptance for registry-derived context manifests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "check_context_manifests.py"
EXPECTED = {f"CTX-MANIFEST-A{i}" for i in range(1, 9)}


def test_frozen_context_manifest_contract() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=600,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assertions = {item["id"]: item for item in report["assertions"]}
    assert report["status"] == "PASS"
    assert set(assertions) == EXPECTED
    assert all(item["status"] == "PASS" and item["evidence"] for item in assertions.values())
