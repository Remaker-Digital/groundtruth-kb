"""Every harness declaring a skills surface receives every baseline skill (WI-7682).

Specs: `GOV-HARNESS-NEUTRAL-BASELINE-001` obligations 2 and 6;
`REQ-GTKB-HARNESS-BASELINE-PROJECTION-CONTRACT-001`;
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`.

The defect this pins: `[harnesses.cursor]` declared `skill_body = "adapter_script"`
and an `adapter_generator`, and `project_harness.py` excluded adapter-script
harnesses from the full-body skill projection without ever writing the branch
that was supposed to replace it. `adapter_generator` was declared once in
profiles.toml and referenced zero times in the projector. Cursor received 5 of
45 skills.

The shortfall was invisible to `--check`, and that is the part worth pinning.
Drift detection compares the projection against the plan, so a file the plan
never contained cannot drift. Cursor reported `0 drifted of 67 managed` while
missing 40 skills, because the missing skills were never managed. A test that
asserts "no drift" would have passed throughout. These assertions compare the
plan against the BASELINE instead, which is the only place the shortfall is
visible.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "harness_projection"))

import project_harness  # noqa: E402


def _profiles() -> dict:
    return project_harness.load_profiles()


def _baseline_skill_names() -> set[str]:
    profiles = _profiles()
    base = PROJECT_ROOT / profiles["baseline"]["root"] / "skills"
    return {p.parent.name for p in base.rglob("SKILL.md")}


def _projected_skill_names(harness: str, skills_dir: str) -> set[str]:
    plan = project_harness.build_plan(harness)
    prefix = f"{skills_dir}/"
    return {
        rel[len(prefix) :].split("/", 1)[0]
        for rel in plan.writes
        if rel.startswith(prefix) and rel.endswith("/SKILL.md")
    }


def _harnesses_with_skills() -> list[tuple[str, str]]:
    out = []
    for name, profile in _profiles()["harnesses"].items():
        if profile.get("status") == "profile_pending":
            continue
        if profile.get("skills_dir"):
            out.append((name, profile["skills_dir"]))
    return sorted(out)


@pytest.mark.parametrize(("harness", "skills_dir"), _harnesses_with_skills())
def test_every_harness_projects_every_baseline_skill(harness: str, skills_dir: str) -> None:
    """Exact baseline coverage also proves parity without repeating every pair of renders."""
    baseline = _baseline_skill_names()
    assert baseline, "baseline declares no skills; the fixture is wrong, not the projector"
    projected = _projected_skill_names(harness, skills_dir)
    assert projected == baseline, (
        f"{harness}: missing skills {sorted(baseline - projected)}; extra skills {sorted(projected - baseline)}"
    )


def test_every_declared_profile_key_is_read_by_the_projector() -> None:
    """The regression floor for the WI-7682 defect class itself.

    `adapter_generator` was declared in profiles.toml and referenced nowhere in
    the projector for as long as the defect existed. A profile key with no
    reader is a capability the configuration claims and the code does not have,
    and it fails silently by construction because nothing consults it.
    """
    source = (PROJECT_ROOT / "scripts" / "harness_projection" / "project_harness.py").read_text(encoding="utf-8")
    declared: set[str] = set()
    for profile in _profiles()["harnesses"].values():
        declared.update(k for k, v in profile.items() if not isinstance(v, dict))

    unread = sorted(key for key in declared if not re.search(rf"""["']{re.escape(key)}["']""", source))
    assert not unread, (
        f"profile keys declared but never read by the projector: {unread}. "
        "Implement the declared behavior or remove the obsolete declaration."
    )
