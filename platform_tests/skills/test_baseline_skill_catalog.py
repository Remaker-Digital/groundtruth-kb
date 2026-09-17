"""Every baseline skill is a valid, projected catalog entry (harness-neutral skill contract).

Carries the retained structural duties of the retired per-skill scaffolding tests (Claude-only skill paths, the
Codex adapter MANIFEST and normalized-sha adapters, the agent-control capability registry): each baseline skill
directory holds a SKILL.md whose frontmatter names the directory and describes the skill; every declared harness
profile receives a projected copy carrying the baseline description; no skill is referenced by a retired
registry. Derivation and tamper detection are the projector's own contract (test_check_harness_parity.py).
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_SKILLS = REPO_ROOT / ".harness-baseline-configuration" / "skills"
PROFILES = tomllib.loads((REPO_ROOT / "scripts/harness_projection/profiles.toml").read_text(encoding="utf-8"))[
    "harnesses"
]
RETIRED_REGISTRIES = (
    REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml",
    REPO_ROOT / "config" / "agent-control" / "skill-scenarios.toml",
    REPO_ROOT / ".codex" / "skills" / "MANIFEST.json",
    REPO_ROOT / ".agent" / "skills" / "MANIFEST.json",
)
# Skills whose retired per-skill tests this module replaces; they must remain in the catalog.
NAMED_SKILLS = (
    "gtkb-verify",
    "gtkb-managed-skill-adoption-review",
    "gtkb-advisory-disposition",
    "gtkb-advisory-proposal",
    "gtkb-advisory-intake",
    "gtkb-lo-opportunity-radar",
    "gtkb-grill-me-for-clarification",
)


def _frontmatter(text: str) -> dict[str, str]:
    assert text.startswith("---\n"), "SKILL.md must open with a YAML frontmatter block"
    head, sep, _ = text[4:].partition("\n---\n")
    assert sep, "SKILL.md frontmatter block must be closed with ---"
    fields = {}
    for line in head.splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def _skill_dirs() -> list[Path]:
    return sorted(p for p in BASELINE_SKILLS.iterdir() if p.is_dir())


def test_baseline_skill_catalog_is_nonempty_and_named_skills_are_present() -> None:
    names = {p.name for p in _skill_dirs()}
    assert len(names) >= 20
    assert set(NAMED_SKILLS) <= names, sorted(set(NAMED_SKILLS) - names)


@pytest.mark.parametrize("skill", [p.name for p in _skill_dirs()])
def test_every_baseline_skill_has_frontmatter_naming_its_directory(skill: str) -> None:
    text = (BASELINE_SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
    fields = _frontmatter(text)
    assert fields.get("name") == skill
    assert fields.get("description", "").strip()
    assert text.partition("\n---\n")[2].strip(), "skill body must not be empty"


@pytest.mark.parametrize("harness", sorted(h for h, row in PROFILES.items() if row.get("status") != "profile_pending"))
def test_every_harness_receives_the_projected_catalog(harness: str) -> None:
    skills_dir = REPO_ROOT / PROFILES[harness]["skills_dir"]
    for skill in NAMED_SKILLS:
        projected = skills_dir / skill / "SKILL.md"
        assert projected.is_file(), projected
        baseline = _frontmatter((BASELINE_SKILLS / skill / "SKILL.md").read_text(encoding="utf-8"))
        assert _frontmatter(projected.read_text(encoding="utf-8")).get("description") == baseline["description"]


def test_retired_skill_registries_are_absent() -> None:
    present = [str(p.relative_to(REPO_ROOT)) for p in RETIRED_REGISTRIES if p.exists()]
    assert not present, present
