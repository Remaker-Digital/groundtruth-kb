"""Canonical wrap guidance and actual registered projector output.

These checks qualify authored instructions and their derivation. Actual lifecycle
invocation, canonical harvest and host fresh/successor behavior remain separate.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.harness_projection import project_harness as projector

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = PROJECT_ROOT / ".agents/skills/gtkb-session-wrap"
SKILL = SKILL_ROOT / "SKILL.md"
PROFILES = projector.load_profiles()["harnesses"]


def _normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_canonical_wrap_skill_requires_knowledge_collection() -> None:
    text = _normalized(SKILL)
    for pattern in (
        r"explicit.*::close.*activity-scoped",
        r"explicit.*::wrap.*context-wide",
        r"read-only guidance.*does not perform harvest",
        r"supported native.*current version.*read back every result",
        r"owner decisions directly.*authoritative source",
        r"logs retain the conversation",
        r"successor obtains its own claim",
        r"never implicitly stage, commit, push, publish",
        r"without that text, prior-agent memory or contact with another harness",
    ):
        assert re.search(pattern, text, re.I), pattern
    for retired in ("session_prompts", "KnowledgeDB(", "git push origin", "TAFE", ".gtkb-state"):
        assert retired not in text


@pytest.mark.parametrize("harness", sorted(PROFILES))
def test_projector_points_to_authored_wrap_and_companion_resources(harness: str) -> None:
    companion_source = SKILL_ROOT.parent / "gtkb-session-wrap-scan/SKILL.md"
    companion = companion_source.read_text(encoding="utf-8")
    assert "../gtkb-session-wrap/references/audit-checklist.md" in companion
    assert "wrap_capture_transcript.py" not in companion and "S000" not in companion
    source = SKILL.read_text(encoding="utf-8")
    for name in ("audit-checklist.md", "handoff-template.md"):
        assert "references/" + name in source
        assert (SKILL_ROOT / "references" / name).is_file()
    plan = projector.build_plan(harness)
    assert plan.writes and not plan.gaps, plan.gaps
    for skill in ("gtkb-session-wrap", "gtkb-session-wrap-scan"):
        outputs = {path: text for path, text in plan.writes.items() if f"/{skill}/" in path}
        if PROFILES[harness]["skills_discovery"] == "agents_skills":
            assert outputs == {}
        else:
            path = PROFILES[harness]["skills_stub_dir"] + f"/{skill}/SKILL.md"
            assert set(outputs) == {path}
            assert f".agents/skills/{skill}/SKILL.md" in outputs[path]
            authored = (SKILL_ROOT.parent / skill / "SKILL.md").read_text(encoding="utf-8")
            assert authored.split("---", 2)[2].strip() not in outputs[path]


def test_handoff_template_is_gtkb_specific_and_self_contained() -> None:
    text = _normalized(SKILL_ROOT / "references/handoff-template.md")
    for phrase in (
        "only when the owner or dispatch has supplied those exact lines",
        "Do not default a role",
        "own native identity and immutable binding",
        "Re-query all current facts",
        "Obtain a fresh next-artifact claim",
        "grants no claim, ownership or authority",
    ):
        assert phrase in text
    assert "::init gtkb pb" not in text and "session_prompts" not in text


def test_audit_checklist_checks_freshness_and_ignored_evidence() -> None:
    text = _normalized(SKILL_ROOT / "references/audit-checklist.md")
    for phrase in (
        "Re-query current work",
        "complete project commit boundary",
        "failed cases, unexecuted obligations",
        "do not qualify actual-host behavior",
        "preserve the immutable binding",
    ):
        # Wording may use an active imperative for the final identity condition.
        if phrase == "preserve the immutable binding":
            assert "leave the immutable binding intact" in text
        else:
            assert phrase.lower() in text.lower()
    assert "session_prompts" not in text and "Every 5th" not in text
