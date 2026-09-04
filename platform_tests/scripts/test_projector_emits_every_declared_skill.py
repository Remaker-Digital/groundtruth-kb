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

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "harness_projection"))

import project_harness  # noqa: E402

# Declarations known to have no implementation behind them, each with the
# carrier that will remove it. This is a registry, not a suppression list: an
# entry documents an open instance of the WI-7682 defect class rather than
# excusing it, and is deleted when its carrier lands.
#
# A profile key absent from both this registry and the projector source is a
# NEW instance -- a capability the configuration claims and the code does not
# have, failing silently because nothing consults it.
KNOWN_UNIMPLEMENTED_DECLARATIONS: dict[str, str] = {
    "manifest_generator": (
        "WI-7162 - generate_goose_manifest.py exists and is not wired into the projector, "
        "the same shape as adapter_generator before WI-7682"
    ),
}


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


def test_every_harness_projects_every_baseline_skill() -> None:
    """Roster-driven, so a future adapter-script harness is covered unedited."""
    baseline = _baseline_skill_names()
    assert baseline, "baseline declares no skills; the fixture is wrong, not the projector"

    shortfalls = {}
    for harness, skills_dir in _harnesses_with_skills():
        missing = baseline - _projected_skill_names(harness, skills_dir)
        if missing:
            shortfalls[harness] = sorted(missing)

    assert not shortfalls, f"harnesses missing baseline skills: {shortfalls}"


def test_no_harness_receives_a_strict_subset_of_another() -> None:
    """Parity: two harnesses may differ in body form, never in skill coverage."""
    projected = {h: _projected_skill_names(h, d) for h, d in _harnesses_with_skills()}
    for a, a_skills in projected.items():
        for b, b_skills in projected.items():
            if a == b:
                continue
            assert not (a_skills < b_skills), (
                f"{a} receives a strict subset of {b}: missing {sorted(b_skills - a_skills)}"
            )


def test_adapter_script_harnesses_receive_skills() -> None:
    """The branch that WI-7682 added must actually produce output.

    Without it an adapter-script harness silently projects zero skills, which
    the shortfall assertion above would catch but only as an absence. This
    asserts the presence directly, so a regression names the right cause.
    """
    adapter_harnesses = [
        (name, profile)
        for name, profile in _profiles()["harnesses"].items()
        if profile.get("skill_body") == "adapter_script" and profile.get("skills_dir")
    ]
    if not adapter_harnesses:
        return  # no adapter-script harness in the roster; nothing to assert

    for name, profile in adapter_harnesses:
        produced = _projected_skill_names(name, profile["skills_dir"])
        assert produced, (
            f"adapter-script harness {name} projected no skills; its adapter_generator branch is not running"
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

    unread = sorted(
        key
        for key in declared
        if key not in KNOWN_UNIMPLEMENTED_DECLARATIONS and not re.search(rf"""["']{re.escape(key)}["']""", source)
    )
    assert not unread, (
        f"profile keys declared but never read by the projector: {unread}. "
        "Either wire them up, or add each to KNOWN_UNIMPLEMENTED_DECLARATIONS with the carrier "
        "work item that will."
    )


def test_known_unimplemented_declarations_are_still_unimplemented() -> None:
    """The registry must not outlive the gaps it records.

    Once a carrier lands, its key becomes readable and the entry is stale. A
    stale entry would silently re-suppress the key if it later regressed, which
    is how a suppression list rots into a blind spot.
    """
    source = (PROJECT_ROOT / "scripts" / "harness_projection" / "project_harness.py").read_text(encoding="utf-8")
    stale = sorted(
        key for key in KNOWN_UNIMPLEMENTED_DECLARATIONS if re.search(rf"""["']{re.escape(key)}["']""", source)
    )
    assert not stale, f"these keys are now read by the projector; remove them from the registry: {stale}"
