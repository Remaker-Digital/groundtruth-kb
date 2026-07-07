"""Activity-profile surfacing tests for advisory intake skills (WI-5058/WI-5059)."""

from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _assert_pending_go() -> None:
    proposal = _read("bridge/gtkb-wi5058-advisory-intake-profile-surfacing-001.md")
    verdict = _read("bridge/gtkb-wi5058-advisory-intake-profile-surfacing-002.md")
    assert verdict.lstrip().startswith("GO")
    assert "Linked manual test: TEST-11296" in proposal
    assert "config/agent-control/activity-disposition-profiles.toml" in proposal
    assert "discoverable in intended contexts and absent elsewhere" in proposal


def _activity_skills() -> dict[str, list[str]]:
    data = tomllib.loads(
        (REPO_ROOT / "config" / "agent-control" / "activity-disposition-profiles.toml").read_text(encoding="utf-8")
    )
    activities = data.get("activities", {})
    return {
        name: list(profile.get("skills", []) or []) for name, profile in activities.items() if isinstance(profile, dict)
    }


def test_advisory_intake_skills_surface_only_in_intended_activity_profiles_or_pending_go() -> None:
    skills_by_activity = _activity_skills()
    advisory_skill_names = {"advisory-proposal", "advisory-intake"}
    surfaced = {
        activity: advisory_skill_names.intersection(set(skills))
        for activity, skills in skills_by_activity.items()
        if advisory_skill_names.intersection(set(skills))
    }
    implemented = any((REPO_ROOT / ".claude" / "skills" / name / "SKILL.md").is_file() for name in advisory_skill_names)

    if not surfaced and not implemented:
        _assert_pending_go()
        return

    assert "advisory-proposal" in set(skills_by_activity.get("deliberation", []))
    assert "advisory-intake" in set(skills_by_activity.get("build", []))

    unrelated = set(skills_by_activity) - {"deliberation", "build"}
    misplaced = {
        activity: sorted(advisory_skill_names.intersection(set(skills_by_activity[activity])))
        for activity in unrelated
        if advisory_skill_names.intersection(set(skills_by_activity[activity]))
    }
    assert not misplaced, f"advisory intake skills surfaced in unrelated activity profiles: {misplaced}"
