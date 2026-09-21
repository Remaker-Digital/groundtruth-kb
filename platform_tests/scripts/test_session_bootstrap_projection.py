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


@pytest.mark.parametrize("harness", sorted(PROFILES))
def test_each_host_uses_authored_bootstrap_without_projected_rule_copies(harness: str) -> None:
    source = (ROOT / ".harness-baseline-configuration/rules/session-bootstrap.md").read_text(encoding="utf-8")
    root = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert ".harness-baseline-configuration/rules" in root
    assert "::init gtkb" in source and "::open" in source
    plan = projector.build_plan(harness)
    assert plan.gaps == []
    assert not any(path.endswith("/session-bootstrap.md") for path in plan.writes)
    assert not any(source.strip() in text for text in plan.writes.values())
    for relative, pointer in PROFILES[harness].get("pointer_files", {}).items():
        assert plan.writes[PROFILES[harness]["config_dir"] + "/" + relative] == pointer
