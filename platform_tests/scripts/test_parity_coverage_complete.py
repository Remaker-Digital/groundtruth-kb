"""Every declared target must satisfy baseline/projector conformance.

This is a real repository acceptance check. Missing sources, unimplemented
registrations, or stale installed outputs remain failures, without waivers.
"""

import tomllib
from pathlib import Path

import pytest

from scripts.check_harness_parity import check_harness_parity

ROOT = Path(__file__).resolve().parents[2]
PROFILES = tomllib.loads((ROOT / "scripts/harness_projection/profiles.toml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("harness", sorted(PROFILES["harnesses"]))
def test_declared_target_derivation_is_complete(harness):
    report = check_harness_parity(ROOT, harness=harness, installed=False)
    assert report["status"] == "pass", report
