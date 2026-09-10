"""Current interview guidance is independently derived for every harness.

Text parity is configuration evidence, not proof of model interview behavior.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/harness_projection"))
import project_harness  # noqa: E402

PROFILES = project_harness.load_profiles()["harnesses"]


@pytest.mark.parametrize(
    "harness", [name for name, profile in PROFILES.items() if profile.get("status") != "profile_pending"]
)
def test_current_interview_skill_is_derived_independently(harness):
    source = (ROOT / ".harness-baseline-configuration/skills/gtkb-grill-me-for-clarification/SKILL.md").read_text(
        encoding="utf-8"
    )
    body = source.split("---", 2)[2].strip()
    plan = project_harness.build_plan(harness)
    # Missing native startup events are separately covered by full parity tests.
    # This test exercises the generated skill output, even for an incomplete profile.
    targets = {
        path: text for path, text in plan.writes.items() if path.endswith("/gtkb-grill-me-for-clarification/SKILL.md")
    }
    assert len(targets) == 1
    path, text = next(iter(targets.items()))
    assert path.startswith(PROFILES[harness]["config_dir"] + "/")
    assert body in text
    assert not any("decision-capture/" in path for path in plan.writes)
