"""The bootstrap rule is actually delivered by each implemented projector."""

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "bootstrap_projector", ROOT / "scripts/harness_projection/project_harness.py"
)
projector = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = projector
spec.loader.exec_module(projector)
PROFILES = projector.load_profiles()["harnesses"]


@pytest.mark.parametrize(
    "harness", [name for name, profile in PROFILES.items() if profile.get("status") != "profile_pending"]
)
def test_each_projection_delivers_the_canonical_bootstrap_body(harness: str) -> None:
    source = (ROOT / ".harness-baseline-configuration/rules/session-bootstrap.md").read_text(encoding="utf-8")
    plan = projector.build_plan(harness)
    assert plan.gaps == []
    assert source in plan.writes[PROFILES[harness]["rules_dir"] + "/session-bootstrap.md"]
