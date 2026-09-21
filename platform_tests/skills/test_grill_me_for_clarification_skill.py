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


@pytest.mark.parametrize("harness", sorted(PROFILES))
def test_current_interview_skill_is_discovered_or_pointed_to(harness):
    source = (ROOT / ".agents/skills/gtkb-grill-me-for-clarification/SKILL.md").read_text(encoding="utf-8")
    body = source.split("---", 2)[2].strip()
    assert body
    plan = project_harness.build_plan(harness)
    assert not plan.gaps, plan.gaps
    targets = {
        path: text for path, text in plan.writes.items() if path.endswith("/gtkb-grill-me-for-clarification/SKILL.md")
    }
    if PROFILES[harness]["skills_discovery"] == "agents_skills":
        assert targets == {}
    else:
        assert len(targets) == 1
        path, text = next(iter(targets.items()))
        assert path.startswith(PROFILES[harness]["skills_stub_dir"] + "/")
        assert ".agents/skills/gtkb-grill-me-for-clarification/SKILL.md" in text
        assert source.split("---", 2)[1] in text and body not in text
    assert not any("decision-capture/" in path for path in plan.writes)


def test_shared_interview_guidance_retains_scope_facts_question_application_and_summary():
    source = (ROOT / ".agents/skills/gtkb-grill-me-for-clarification/SKILL.md").read_text(encoding="utf-8")
    normalized = " ".join(source.split())
    for duty in (
        "If it is missing, ask for it before starting",
        "Resolve factual questions from those sources before asking the owner",
        "Ask one material question at a time",
        "Reuse answers already supplied in this session",
        "Apply a resolved choice directly to the affected canonical source",
        "Do not create a separate decision archive",
        "give a concise account of what changed in canonical state and what remains unresolved",
        "An interview does not itself authorize implementation",
    ):
        assert duty in normalized, duty
