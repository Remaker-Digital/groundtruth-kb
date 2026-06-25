# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Skill catalog-contract regression test (WI-4813).

Converts doctor-reported skill-catalog coverage into a tested contract by
importing the production parity logic from ``scripts/check_harness_parity.py``
(per GOV-10 — exercise exposed production interfaces rather than reimplement),
and folds the residual of retired WI-4811: every skill name referenced in
``config/agent-control/skill-scenarios.toml`` must resolve via the production
``_registry_skill_dirs()`` set (which unions SKILL.md directory names AND
registry ``canonical_name`` values).

Reusing the production resolution surface guarantees the test's notion of
"registered / resolves / adapter-loadable" cannot drift from the parity/doctor
surface it formalizes.

Specifications:
- SPEC-1853 (Stable Skill/Tool Identity Contract) — frontmatter validity.
- ADR-REGISTRY-DISCOVERY-001 / GOV-HARNESS-ONBOARDING-CONTRACT-001 — registry
  registration, no orphans, Codex adapter loadability.
- SPEC-SKILL-USAGE-ROUTER-001 (R2/R3) — scenario->skills table must reference
  resolvable skills (folded WI-4811 consistency check).
- GOV-10 — production-interface reuse.

Work item: WI-4813. Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import check_harness_parity as chp  # noqa: E402  (path injected above)

_SCENARIOS = _REPO_ROOT / "config" / "agent-control" / "skill-scenarios.toml"


def _skill_capabilities() -> list[dict]:
    """Return the ``kind == 'skill'`` capability records from the registry."""
    registry, _ = chp.load_registry(_REPO_ROOT)
    capabilities = registry.get("capabilities") or []
    return [c for c in capabilities if c.get("kind") == "skill"]


def test_every_skill_has_valid_frontmatter() -> None:
    """SPEC-1853: every ``.claude/skills/*/SKILL.md`` has loadable frontmatter.

    Uses the production ``inventory_project_skills`` + ``_skill_frontmatter_error``
    so the contract matches the parity checker's definition of a skill (a dir
    with a ``SKILL.md``); reference-stub dirs without ``SKILL.md`` are excluded.
    """
    inventory = chp.inventory_project_skills(_REPO_ROOT)
    assert inventory, "no project skills discovered under .claude/skills/*/SKILL.md"
    errors: dict[str, str] = {}
    for rel_path in sorted(set(inventory.values())):
        text = (_REPO_ROOT / rel_path).read_text(encoding="utf-8")
        err = chp._skill_frontmatter_error(text, rel_path)
        if err is not None:
            errors[rel_path] = err
    assert not errors, f"skills with invalid frontmatter: {errors}"


def test_skill_dirs_match_registry_no_orphans() -> None:
    """ADR-REGISTRY-DISCOVERY-001 / GOV-HARNESS-ONBOARDING-CONTRACT-001.

    Every SKILL.md-bearing skill dir is declared in the registry (no
    unregistered orphans), and every registered skill name resolves to a
    backing project skill (no dangling registry rows).
    """
    capabilities = _skill_capabilities()
    assert capabilities, "registry declares no kind='skill' capabilities"

    # Direction 1: no unregistered project skills (orphans / extras).
    extras = chp._extra_project_skills(_REPO_ROOT, capabilities)
    assert not extras, f"project skills present on disk but absent from the registry: {[e.skill_name for e in extras]}"

    # Direction 2: every registered skill name (dir name or canonical_name)
    # has a backing project skill inventory entry.
    registry_names = chp._registry_skill_dirs(capabilities)
    inventory_names = set(chp.inventory_project_skills(_REPO_ROOT))
    dangling = sorted(name for name in registry_names if name not in inventory_names)
    assert not dangling, f"registered skill names without a backing SKILL.md dir: {dangling}"


def test_every_skill_has_loadable_codex_adapter() -> None:
    """GOV-HARNESS-ONBOARDING-CONTRACT-001: every registered skill's Codex
    adapter surface exists and is loadable.

    The production ``_status_for_surface`` evaluation must yield ``PASS`` (no
    MISSING adapter, no STALE hash mismatch, no unloadable frontmatter) for the
    ``codex`` surface of every skill capability.
    """
    capabilities = _skill_capabilities()
    non_pass: dict[str, tuple[str, str]] = {}
    for capability in capabilities:
        result = chp._status_for_surface(_REPO_ROOT, capability, "codex")
        if result.state != "PASS":
            non_pass[str(capability.get("id"))] = (result.state, result.note)
    assert not non_pass, f"skills with a non-PASS Codex adapter: {non_pass}"


def test_scenario_skill_names_resolve() -> None:
    """SPEC-SKILL-USAGE-ROUTER-001 R2/R3 + folded WI-4811.

    Every ``required`` and ``recommended`` skill name across every scenario in
    ``skill-scenarios.toml`` must be a member of the production
    ``_registry_skill_dirs()`` resolution set. Because that set unions directory
    names with registry ``canonical_name`` values, a canonical alias such as
    ``gtkb-bridge`` (canonical_name of ``skill.bridge``) resolves correctly; a
    typo'd, renamed, or non-skill reference (e.g. a slash command) does not.
    """
    capabilities = _skill_capabilities()
    registry_names = chp._registry_skill_dirs(capabilities)
    data = tomllib.loads(_SCENARIOS.read_text(encoding="utf-8"))
    scenarios = data.get("scenarios", {})
    assert scenarios, "skill-scenarios.toml defines no [scenarios.*] tables"

    unresolved: dict[str, list[str]] = {}
    for key, scenario in scenarios.items():
        for field in ("required", "recommended"):
            for name in scenario.get(field, []) or []:
                if name not in registry_names:
                    unresolved.setdefault(f"{key}.{field}", []).append(name)
    assert not unresolved, (
        "skill-scenarios.toml references skill names that do not resolve to a "
        f"registered skill (dead advisory suggestions): {unresolved}"
    )
