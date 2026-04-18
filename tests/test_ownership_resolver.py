# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Enum + policy dispatch tests for :class:`OwnershipResolver`.

Proposal §3.2 (``bridge/gtkb-artifact-ownership-matrix-003.md``). Each test
verifies the resolver classifies a specific path into the expected ownership
/ upgrade / divergence triple.
"""

from __future__ import annotations

import pytest

from groundtruth_kb.project.managed_registry import (
    InvalidArtifactRecord,
    _parse_record,
)
from groundtruth_kb.project.ownership import OwnershipResolver

# ---------------------------------------------------------------------------
# Classify by path — registry rows
# ---------------------------------------------------------------------------


def test_classify_tracked_managed_hook_file() -> None:
    """A managed hook file → gt-kb-managed / overwrite / warn."""
    resolver = OwnershipResolver()
    rec = resolver.classify_path(".claude/hooks/assertion-check.py")
    assert rec.ownership == "gt-kb-managed"
    assert rec.upgrade_policy == "overwrite"
    assert rec.adopter_divergence_policy == "warn"


def test_classify_tracked_managed_rule_file() -> None:
    """A managed rule file → gt-kb-managed / overwrite / warn."""
    resolver = OwnershipResolver()
    rec = resolver.classify_path(".claude/rules/prime-builder.md")
    assert rec.ownership == "gt-kb-managed"
    assert rec.upgrade_policy == "overwrite"
    assert rec.adopter_divergence_policy == "warn"


# ---------------------------------------------------------------------------
# Classify by path — ownership-glob rows
# ---------------------------------------------------------------------------


def test_classify_scaffolded_groundtruth_toml() -> None:
    """groundtruth.toml → gt-kb-scaffolded / preserve / None."""
    resolver = OwnershipResolver()
    rec = resolver.classify_path("groundtruth.toml")
    assert rec.ownership == "gt-kb-scaffolded"
    assert rec.upgrade_policy == "preserve"
    assert rec.adopter_divergence_policy is None


def test_classify_legacy_exception_groundtruth_db() -> None:
    """groundtruth.db → legacy-exception / preserve / None."""
    resolver = OwnershipResolver()
    rec = resolver.classify_path("groundtruth.db")
    assert rec.ownership == "legacy-exception"
    assert rec.upgrade_policy == "preserve"
    assert rec.adopter_divergence_policy is None


def test_classify_shared_structured_bridge_file() -> None:
    """bridge/x.md → shared-structured / preserve / None."""
    resolver = OwnershipResolver()
    rec = resolver.classify_path("bridge/foo-001.md")
    assert rec.ownership == "shared-structured"
    assert rec.upgrade_policy == "preserve"
    assert rec.adopter_divergence_policy is None


def test_classify_adopter_owned_memory() -> None:
    """memory/sample.md → adopter-owned / preserve / None."""
    resolver = OwnershipResolver()
    rec = resolver.classify_path("memory/sample.md")
    assert rec.ownership == "adopter-owned"
    assert rec.upgrade_policy == "preserve"
    assert rec.adopter_divergence_policy is None


def test_classify_adopter_owned_webapp() -> None:
    """webapp/index.html → adopter-owned / preserve / None."""
    resolver = OwnershipResolver()
    rec = resolver.classify_path("webapp/index.html")
    assert rec.ownership == "adopter-owned"
    assert rec.upgrade_policy == "preserve"


def test_classify_transient_staging() -> None:
    """.gt-upgrade-staging/foo.tmp → gt-kb-managed / transient / None."""
    resolver = OwnershipResolver()
    rec = resolver.classify_path(".gt-upgrade-staging/foo.tmp")
    assert rec.ownership == "gt-kb-managed"
    assert rec.upgrade_policy == "transient"
    assert rec.adopter_divergence_policy is None


def test_classify_unknown_path_falls_back_to_adopter_owned() -> None:
    """Unclassified path → fallback record with __fallback__: prefix."""
    resolver = OwnershipResolver()
    rec = resolver.classify_path("some/totally/unknown.xyz")
    assert rec.id.startswith("__fallback__:")
    assert rec.ownership == "adopter-owned"
    assert rec.upgrade_policy == "preserve"
    assert rec.adopter_divergence_policy is None
    assert rec.source_class == "__fallback__"


# ---------------------------------------------------------------------------
# Glob precedence
# ---------------------------------------------------------------------------


def test_glob_priority_higher_wins(tmp_path, monkeypatch) -> None:
    """When two globs cover the same path, higher priority wins."""
    # We build a resolver with synthetic glob rows to test precedence
    # deterministically without relying on the shipped templates.
    from groundtruth_kb.project import ownership as ownership_mod

    high = _parse_record(
        {
            "class": "ownership-glob",
            "id": "test-high-priority",
            "path_glob": "target/**",
            "priority": 100,
            "initial_profiles": [],
            "managed_profiles": [],
            "doctor_required_profiles": [],
            "ownership": "gt-kb-managed",
            "upgrade_policy": "transient",
        }
    )
    low = _parse_record(
        {
            "class": "ownership-glob",
            "id": "test-low-priority",
            "path_glob": "target/**",
            "priority": 10,
            "initial_profiles": [],
            "managed_profiles": [],
            "doctor_required_profiles": [],
            "ownership": "adopter-owned",
            "upgrade_policy": "preserve",
        }
    )

    # Monkeypatch the loader so OwnershipResolver picks up our synthetic rows.
    monkeypatch.setattr(ownership_mod, "_load_all_artifacts", lambda: [high, low])
    resolver = ownership_mod.OwnershipResolver()
    rec = resolver.classify_path("target/file.txt")
    assert rec.id == "test-high-priority"
    assert rec.ownership == "gt-kb-managed"


def test_glob_same_priority_longest_prefix_wins(monkeypatch) -> None:
    """Same priority; longest literal prefix wins."""
    from groundtruth_kb.project import ownership as ownership_mod

    short = _parse_record(
        {
            "class": "ownership-glob",
            "id": "test-short-prefix",
            "path_glob": "src/**",
            "priority": 50,
            "initial_profiles": [],
            "managed_profiles": [],
            "doctor_required_profiles": [],
            "ownership": "adopter-owned",
            "upgrade_policy": "preserve",
        }
    )
    longer = _parse_record(
        {
            "class": "ownership-glob",
            "id": "test-long-prefix",
            "path_glob": "src/test/**",
            "priority": 50,
            "initial_profiles": [],
            "managed_profiles": [],
            "doctor_required_profiles": [],
            "ownership": "gt-kb-managed",
            "upgrade_policy": "transient",
        }
    )

    monkeypatch.setattr(ownership_mod, "_load_all_artifacts", lambda: [short, longer])
    resolver = ownership_mod.OwnershipResolver()
    rec = resolver.classify_path("src/test/foo.py")
    # "src/test/**" has longer literal prefix than "src/**".
    assert rec.id == "test-long-prefix"
    assert rec.ownership == "gt-kb-managed"


# ---------------------------------------------------------------------------
# Invariant enforcement at OwnershipMeta-construction boundary
# ---------------------------------------------------------------------------


def test_divergence_policy_required_invariant() -> None:
    """Constructing a record with overwrite + no divergence must raise (via loader)."""
    bad: dict[str, object] = {
        "class": "hook",
        "id": "hook.test-no-div",
        "template_path": "hooks/x.py",
        "target_path": ".claude/hooks/x.py",
        "initial_profiles": ["local-only"],
        "managed_profiles": [],
        "doctor_required_profiles": [],
        "ownership": "gt-kb-managed",
        "upgrade_policy": "overwrite",
        # adopter_divergence_policy missing
    }
    with pytest.raises(InvalidArtifactRecord, match="adopter_divergence_policy"):
        _parse_record(bad)


def test_divergence_policy_forbidden_on_preserve() -> None:
    """Constructing a record with preserve + non-None divergence must raise."""
    bad: dict[str, object] = {
        "class": "ownership-glob",
        "id": "test-bad-preserve",
        "path_glob": "foo.txt",
        "priority": 10,
        "initial_profiles": [],
        "managed_profiles": [],
        "doctor_required_profiles": [],
        "ownership": "adopter-owned",
        "upgrade_policy": "preserve",
        "adopter_divergence_policy": "error",  # illegal
    }
    with pytest.raises(InvalidArtifactRecord, match="adopter_divergence_policy"):
        _parse_record(bad)


# ---------------------------------------------------------------------------
# Classify-by-id
# ---------------------------------------------------------------------------


def test_classify_by_id_returns_settings_hook_record() -> None:
    """classify_by_id returns a settings-hook-registration record."""
    resolver = OwnershipResolver()
    rec = resolver.classify_by_id("settings.hook.assertion-check.sessionstart")
    assert rec.source_class == "settings-hook-registration"
    assert rec.ownership == "gt-kb-managed"
    assert rec.upgrade_policy == "structured-merge"


def test_classify_by_id_returns_gitignore_record() -> None:
    """classify_by_id returns the gitignore-pattern row."""
    resolver = OwnershipResolver()
    rec = resolver.classify_by_id("gitignore.hook-logs")
    assert rec.source_class == "gitignore-pattern"
    assert rec.ownership == "gt-kb-managed"
    assert rec.upgrade_policy == "structured-merge"


def test_classify_by_id_unknown_raises() -> None:
    """classify_by_id on an unknown id raises KeyError."""
    resolver = OwnershipResolver()
    with pytest.raises(KeyError):
        resolver.classify_by_id("totally.nonexistent.id")


# ---------------------------------------------------------------------------
# all_records deterministic ordering
# ---------------------------------------------------------------------------


def test_all_records_sorted_by_ownership_then_id() -> None:
    """all_records() returns deterministic order: ownership enum, then id."""
    resolver = OwnershipResolver()
    records = resolver.all_records()
    order = ["gt-kb-managed", "gt-kb-scaffolded", "shared-structured", "adopter-owned", "legacy-exception"]
    seen_owner_idx = -1
    for r in records:
        idx = order.index(r.ownership)
        assert idx >= seen_owner_idx, f"ownership order violated at {r.id}: {r.ownership}"
        seen_owner_idx = idx
