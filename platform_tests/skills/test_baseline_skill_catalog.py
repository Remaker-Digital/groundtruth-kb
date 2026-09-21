"""Every baseline skill is a valid, projected catalog entry (harness-neutral skill contract).

Carries the retained structural duties of the retired per-skill scaffolding tests (Claude-only skill paths, the
Codex adapter MANIFEST and normalized-sha adapters, the agent-control capability registry): each baseline skill
directory holds a SKILL.md whose frontmatter names the directory and describes the skill; every declared harness
profile reads the shared source or receives a pointer carrying its frontmatter; no skill is referenced by a retired
registry. Derivation and tamper detection are the projector's own contract (test_check_harness_parity.py).
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest
import yaml

from scripts.harness_projection import project_harness as projector

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_SKILLS = REPO_ROOT / ".agents" / "skills"
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


@pytest.mark.parametrize("harness", sorted(PROFILES))
def test_every_harness_discovers_shared_skills_or_receives_frontmatter_pointers(harness: str) -> None:
    plan = projector.build_plan(harness)
    assert not plan.gaps, plan.gaps
    profile = PROFILES[harness]
    for skill in NAMED_SKILLS:
        source = (BASELINE_SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
        outputs = {path: text for path, text in plan.writes.items() if path.endswith(f"/{skill}/SKILL.md")}
        if profile["skills_discovery"] == "agents_skills":
            assert outputs == {}
        else:
            path = profile["skills_stub_dir"] + f"/{skill}/SKILL.md"
            assert set(outputs) == {path}
            assert _frontmatter(outputs[path]) == _frontmatter(source)
            assert f".agents/skills/{skill}/SKILL.md" in outputs[path]
            assert source.split("---", 2)[2].strip() not in outputs[path]


def test_retired_skill_registries_are_absent() -> None:
    present = [str(p.relative_to(REPO_ROOT)) for p in RETIRED_REGISTRIES if p.exists()]
    assert not present, present


def _resource_targets(skill: Path, skills_root: Path) -> set[Path]:
    text = skill.read_text(encoding="utf-8")
    metadata = yaml.safe_load(text.split("---", 2)[1]) or {}
    declared: set[str] = set()

    def collect(value, resource_field=False):
        if isinstance(value, dict):
            for key, child in value.items():
                collect(child, resource_field or key in {"references", "resources", "scripts"})
        elif isinstance(value, list):
            for child in value:
                collect(child, resource_field)
        elif resource_field and isinstance(value, str):
            declared.add(value)

    collect(metadata)
    declared.update(re.findall(r"\[[^\]]*\]\(([^)]+)\)", text))
    declared.update(re.findall(r"`((?:\.\./[A-Za-z0-9_-]+/)?(?:references|helpers|agents)/[^`]+)`", text))
    targets = set()
    for raw in declared:
        target = raw.strip().split("#", 1)[0]
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        resolved = (skill.parent / target).resolve()
        assert resolved.is_relative_to(skills_root.resolve()), f"skill resource escapes shared source: {skill} -> {raw}"
        assert resolved.is_file(), f"missing authored skill resource: {skill} -> {raw}"
        targets.add(resolved)
    return targets


def test_every_declared_skill_resource_resolves_at_the_shared_source():
    skills = sorted(BASELINE_SKILLS.glob("*/SKILL.md"))
    assert skills
    targets = set().union(*(_resource_targets(skill, BASELINE_SKILLS) for skill in skills))
    assert targets, "a zero-resource loop is not resource-resolution evidence"


@pytest.mark.parametrize(
    "target,valid",
    [("../other/references/guide.md", True), ("references/missing.md", False), ("../../outside.md", False)],
)
def test_skill_resource_resolution_rejects_missing_or_escaping_targets(tmp_path, target, valid):
    skills = tmp_path / "skills"
    skill = skills / "example/SKILL.md"
    skill.parent.mkdir(parents=True)
    present = skills / "other/references/guide.md"
    present.parent.mkdir(parents=True)
    present.write_text("shared resource", encoding="utf-8")
    (tmp_path / "outside.md").write_text("foreign resource", encoding="utf-8")
    skill.write_text(
        "---\nname: example\nmetadata:\n  references:\n    - " + target + "\n---\nbody\n", encoding="utf-8"
    )
    if valid:
        assert _resource_targets(skill, skills) == {present.resolve()}
    else:
        with pytest.raises(AssertionError, match="missing authored|escapes shared"):
            _resource_targets(skill, skills)
