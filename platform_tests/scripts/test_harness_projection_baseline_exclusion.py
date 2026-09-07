"""Baseline artifact exclusion and fail-closed render (WI-7112, TEST-12546).

Binds TEST-12546 to executable selectors. Covers the half of WI-7112 that
`is_projection_junk` did not: nested harness-config trees, projector output that
has leaked into source, and artifact classes the projector does not recognize.

Specification coverage:
  GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 2 - projection-only configuration
  GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 3 - baseline neutrality
  GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6 - gap capture
  GOV-SOT-SINGLETON-001 - source must not carry its own output
  DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 - one stray artifact must not multiply
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = REPO_ROOT / "scripts" / "harness_projection" / "project_harness.py"


def _load_engine():
    """Import the projector under a registered module name.

    The module defines dataclasses, and `@dataclass` resolves the defining
    module out of `sys.modules`; loading it unregistered raises AttributeError.
    """
    spec = importlib.util.spec_from_file_location("gtkb_project_harness", ENGINE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def engine():
    return _load_engine()


def test_harness_config_dir_names_covers_registered_harnesses(engine):
    """The nested-harness rule is derived from the registry, not one hardcoded name."""
    names = engine.harness_config_dir_names()
    assert names, "no registered harness config directories were derived"
    # The pre-WI-7112 rule recognized exactly one harness tree. Whatever the
    # registry holds, the derived set must be broader than a single entry,
    # otherwise the generalization did not happen.
    assert len(names) > 1, f"expected multiple registered config dirs, got {names}"
    assert all(n == n.lower() for n in names), "config dir names must be lowercased"


def test_planted_nested_harness_tree_is_excluded(engine, tmp_path):
    """A nested harness config tree under a surface is another harness's output."""
    src_root = tmp_path / "rules"
    names = sorted(engine.harness_config_dir_names())
    for harness_dir in names:
        planted = src_root / harness_dir / "session" / "spec-events-seen.jsonl"
        planted.parent.mkdir(parents=True, exist_ok=True)
        planted.write_text("{}", encoding="utf-8")
        assert engine.is_projection_junk(planted, src_root), (
            f"nested harness tree {harness_dir}/ was not excluded; a stray artifact "
            "there is copied into every registered projection"
        )


def test_planted_projection_manifest_is_excluded(engine, tmp_path):
    """Projector output that has leaked into source is never projectable."""
    src_root = tmp_path / "skills"
    planted = src_root / "some-skill" / ".projection-manifest.json"
    planted.parent.mkdir(parents=True, exist_ok=True)
    planted.write_text('{"harness": "somewhere"}', encoding="utf-8")
    assert engine.is_projection_junk(planted, src_root)


def test_bytecode_and_lock_exclusions_are_preserved(engine, tmp_path):
    """The pre-existing exclusions must survive the generalization."""
    src_root = tmp_path / "hooks"
    for rel in ("__pycache__/mod.cpython-314.pyc", "a.lock", "sub/b.pyo", ".DS_Store"):
        planted = src_root / rel
        planted.parent.mkdir(parents=True, exist_ok=True)
        planted.write_text("x", encoding="utf-8")
        assert engine.is_projection_junk(planted, src_root), f"{rel} stopped being excluded"


def test_legitimate_baseline_content_is_not_excluded(engine, tmp_path):
    """The exclusion set must not swallow real neutral source.

    This is the over-exclusion guard: an exclusion class broad enough to drop
    genuine configuration would silently shrink every projection.
    """
    src_root = tmp_path / "skills"
    for rel in ("gtkb-bridge/SKILL.md", "gtkb-bridge/helpers/write.py", "x/manifest.toml"):
        planted = src_root / rel
        planted.parent.mkdir(parents=True, exist_ok=True)
        planted.write_text("content", encoding="utf-8")
        assert not engine.is_projection_junk(planted, src_root), f"{rel} was wrongly excluded"


def test_unrecognized_artifact_class_is_named_in_a_gap(engine):
    """Fail-closed must identify WHAT was unrecognized, per the GO condition.

    The projector's gap list already fails the render; the requirement this
    covers is that the message names the offending material rather than only
    reporting that something was wrong.
    """
    source = ENGINE_PATH.read_text(encoding="utf-8")
    marker = "unrecognized artifact class"
    assert marker in source, "fail-closed gap for unrecognized artifact classes is absent"
    block = source[source.index(marker) - 600 : source.index(marker) + 400]
    assert "plan.gaps.append" in block, "the unrecognized-class branch does not append a gap"
    assert "offending" in block, "the gap message does not name the offending path"
    assert "artifact_class" in block, "the gap message does not name the artifact class"
    # The silent latin-1 round-trip was the defect; it must not survive anywhere.
    assert 'read_bytes().decode("latin-1")' not in source, (
        "the silent latin-1 copy still runs for unrecognized artifact classes"
    )


def test_engine_still_renders_every_implemented_profile(engine):
    """Over-exclusion guard against the live baseline, not a fixture.

    Every profile with an implemented slice must still produce a non-empty plan.
    A plan that collapsed would mean the new exclusion classes started matching
    real configuration.
    """
    profiles = engine.load_profiles()
    checked = 0
    for name, profile in (profiles.get("harnesses") or {}).items():
        if (profile or {}).get("status") == "profile_pending":
            continue
        plan = engine.build_plan(name)
        assert plan.writes, f"profile {name} produced an empty plan after exclusion changes"
        assert not plan.gaps, f"profile {name} reported gaps: {plan.gaps[:3]}"
        checked += 1
    assert checked >= 1, "no implemented profile was exercised"
