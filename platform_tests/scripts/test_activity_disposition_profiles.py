"""Tests for activity disposition profiles — DCL-ACTIVITY-DISPOSITION-PROFILE-001.

Spec-to-test mapping:
  A1 (six activity profiles present):
      test_all_six_activities_present, test_default_path_loads_shipped_config
  A2 (four classes per profile):
      test_each_profile_defines_four_classes
  A3 (headless_eligibility valid and D4-consistent):
      test_headless_eligibility_valid_and_d4_consistent
  Loader fail-closed:
      test_loader_rejects_missing_activity,
      test_loader_rejects_missing_class,
      test_loader_rejects_invalid_eligibility
"""

from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb.activity.profiles import (
    _D4_ELIGIBILITY,
    _REQUIRED_CLASSES,
    CANONICAL_ACTIVITIES,
    ActivityProfile,
    ActivityProfileError,
    load_activity_profiles,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SHIPPED_CONFIG = (
    Path(__file__).resolve().parents[2] / "config" / "agent-control" / "activity-disposition-profiles.toml"
)


def _write_toml(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "profiles.toml"
    p.write_text(content, encoding="utf-8")
    return p


def _minimal_toml(overrides: dict[str, str] | None = None) -> str:
    """Return a minimal valid TOML with all six activities."""
    activity_defaults = {
        "ops": "interactive_primary",
        "deliberation": "interactive_only",
        "build": "headless_eligible",
        "test": "headless_eligible",
        "spec": "headless_eligible",
        "project": "interactive_only",
    }
    lines = ["schema_version = 1\n"]
    for act, eligibility in activity_defaults.items():
        elig = (overrides or {}).get(act, eligibility)
        lines.append(f"[activities.{act}]")
        lines.append("version = 1")
        lines.append(f'headless_eligibility = "{elig}"')
        lines.append("skills = []")
        lines.append("terminology = []")
        lines.append(f"[activities.{act}.history_state]")
        lines.append("sources = []")
        lines.append(f"[activities.{act}.direction]")
        lines.append('stance = ""')
        lines.append("guardrails = []")
        lines.append("manipulates = []")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# A1: All six canonical activities present
# ---------------------------------------------------------------------------


def test_all_six_activities_present() -> None:
    profiles = load_activity_profiles(_SHIPPED_CONFIG)
    assert set(profiles.keys()) == CANONICAL_ACTIVITIES


def test_default_path_loads_shipped_config() -> None:
    # Passing None should resolve to the shipped config and succeed.
    profiles = load_activity_profiles(None)
    assert isinstance(profiles, dict)
    assert len(profiles) == len(CANONICAL_ACTIVITIES)
    for name, profile in profiles.items():
        assert isinstance(profile, ActivityProfile)
        assert profile.name == name


# ---------------------------------------------------------------------------
# A2: Each profile defines all four payload classes
# ---------------------------------------------------------------------------


def test_each_profile_defines_four_classes() -> None:
    profiles = load_activity_profiles(_SHIPPED_CONFIG)
    for name, profile in profiles.items():
        for cls in _REQUIRED_CLASSES:
            value = getattr(profile, cls)
            assert value is not None, f"Activity '{name}' missing class '{cls}'"


def test_skills_and_terminology_are_lists() -> None:
    profiles = load_activity_profiles(_SHIPPED_CONFIG)
    for name, profile in profiles.items():
        assert isinstance(profile.skills, list), f"'{name}'.skills must be a list"
        assert isinstance(profile.terminology, list), f"'{name}'.terminology must be a list"


def test_history_state_and_direction_are_dicts() -> None:
    profiles = load_activity_profiles(_SHIPPED_CONFIG)
    for name, profile in profiles.items():
        assert isinstance(profile.history_state, dict), f"'{name}'.history_state must be a dict"
        assert isinstance(profile.direction, dict), f"'{name}'.direction must be a dict"


# ---------------------------------------------------------------------------
# A3: headless_eligibility valid and D4-consistent
# ---------------------------------------------------------------------------


def test_headless_eligibility_valid_and_d4_consistent() -> None:
    profiles = load_activity_profiles(_SHIPPED_CONFIG)
    for name, profile in profiles.items():
        expected = _D4_ELIGIBILITY[name]
        assert profile.headless_eligibility == expected, (
            f"Activity '{name}' headless_eligibility {profile.headless_eligibility!r} "
            f"does not match DELIB-20265287 D4 expected {expected!r}"
        )


# ---------------------------------------------------------------------------
# Loader fail-closed — A1 violation
# ---------------------------------------------------------------------------


def test_loader_rejects_missing_activity(tmp_path: Path) -> None:
    # Build a TOML without 'ops'.
    content = _minimal_toml()
    # Remove the ops block lines.
    lines = [ln for ln in content.splitlines() if "activities.ops" not in ln]
    p = _write_toml(tmp_path, "\n".join(lines))
    with pytest.raises(ActivityProfileError, match="A1"):
        load_activity_profiles(p)


# ---------------------------------------------------------------------------
# Loader fail-closed — A2 violation
# ---------------------------------------------------------------------------


def test_loader_rejects_missing_class(tmp_path: Path) -> None:
    # Remove the skills key from 'build'.
    content = _minimal_toml()
    filtered = []
    in_build = False
    for line in content.splitlines():
        if line.strip() == "[activities.build]":
            in_build = True
        elif line.strip().startswith("[activities.") and "build" not in line:
            in_build = False
        # Skip the skills line inside build only.
        if in_build and line.strip().startswith("skills"):
            continue
        filtered.append(line)
    p = _write_toml(tmp_path, "\n".join(filtered))
    with pytest.raises(ActivityProfileError, match="A2"):
        load_activity_profiles(p)


# ---------------------------------------------------------------------------
# Loader fail-closed — A3 violation
# ---------------------------------------------------------------------------


def test_loader_rejects_invalid_eligibility(tmp_path: Path) -> None:
    p = _write_toml(tmp_path, _minimal_toml({"ops": "not_a_real_value"}))
    with pytest.raises(ActivityProfileError, match="A3"):
        load_activity_profiles(p)


def test_loader_rejects_d4_inconsistent_eligibility(tmp_path: Path) -> None:
    # deliberation should be interactive_only, not headless_eligible.
    p = _write_toml(tmp_path, _minimal_toml({"deliberation": "headless_eligible"}))
    with pytest.raises(ActivityProfileError, match="A3"):
        load_activity_profiles(p)


# ---------------------------------------------------------------------------
# Loader fail-closed — missing config file
# ---------------------------------------------------------------------------


def test_loader_raises_on_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ActivityProfileError, match="not found"):
        load_activity_profiles(tmp_path / "does_not_exist.toml")


def test_loader_raises_on_invalid_toml(tmp_path: Path) -> None:
    p = tmp_path / "bad.toml"
    p.write_text("this is not [ valid toml !!!!", encoding="utf-8")
    with pytest.raises(ActivityProfileError, match="Invalid TOML"):
        load_activity_profiles(p)
