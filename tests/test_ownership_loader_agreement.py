# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Loader / resolver agreement tests for the artifact ownership matrix.

Proposal §3.1 (``bridge/gtkb-artifact-ownership-matrix-003.md``). Each test
enforces one invariant at the seam between
:mod:`groundtruth_kb.project.managed_registry` and
:mod:`groundtruth_kb.project.ownership`.
"""

from __future__ import annotations

import pytest

from groundtruth_kb.project.managed_registry import (
    FileArtifact,
    InvalidArtifactRecord,
    OwnershipGlobArtifact,
    _load_all_artifacts,
    _parse_record,
    artifacts_for_doctor,
    artifacts_for_scaffold,
    artifacts_for_upgrade,
)
from groundtruth_kb.project.ownership import OwnershipResolver

# ---------------------------------------------------------------------------
# Cross-file loader agreement
# ---------------------------------------------------------------------------


def test_loader_reads_both_files_and_all_record_ids_unique() -> None:
    """IDs across ``managed-artifacts.toml`` + ``scaffold-ownership.toml`` are unique."""
    records = _load_all_artifacts()
    ids = [r.id for r in records]
    # Cross-file uniqueness guaranteed by _load_all_artifacts().
    assert len(ids) == len(set(ids)), f"duplicate ids: {[x for x in ids if ids.count(x) > 1]}"
    # Sibling file contributes ownership-glob records.
    glob_rows = [r for r in records if isinstance(r, OwnershipGlobArtifact)]
    assert len(glob_rows) >= 6, "sibling file must contribute at least 6 ownership-glob rows"


def test_loader_rejects_ownership_glob_with_file_class_keys() -> None:
    """An ownership-glob record with file-class keys must raise InvalidArtifactRecord."""
    bad: dict[str, object] = {
        "class": "ownership-glob",
        "id": "test-glob-with-template-path",
        "path_glob": "foo/**",
        "priority": 10,
        "template_path": "hooks/foo.py",  # forbidden on ownership-glob
        "initial_profiles": [],
        "managed_profiles": [],
        "doctor_required_profiles": [],
        "ownership": "gt-kb-managed",
        "upgrade_policy": "preserve",
    }
    with pytest.raises(InvalidArtifactRecord, match="forbidden"):
        _parse_record(bad)


def test_loader_rejects_file_class_with_path_glob() -> None:
    """File-class records must not carry path_glob (new forbidden key)."""
    bad: dict[str, object] = {
        "class": "hook",
        "id": "hook.test-bad",
        "template_path": "hooks/foo.py",
        "target_path": ".claude/hooks/foo.py",
        "path_glob": "**/*.py",  # forbidden on hook class
        "initial_profiles": ["local-only"],
        "managed_profiles": [],
        "doctor_required_profiles": [],
    }
    with pytest.raises(InvalidArtifactRecord, match="forbidden"):
        _parse_record(bad)


def test_loader_rejects_missing_divergence_on_overwrite() -> None:
    """upgrade_policy='overwrite' without adopter_divergence_policy must raise (GO C1)."""
    bad: dict[str, object] = {
        "class": "hook",
        "id": "hook.test-missing-div",
        "template_path": "hooks/foo.py",
        "target_path": ".claude/hooks/foo.py",
        "initial_profiles": ["local-only"],
        "managed_profiles": [],
        "doctor_required_profiles": [],
        "ownership": "gt-kb-managed",
        "upgrade_policy": "overwrite",
        # adopter_divergence_policy intentionally absent
    }
    with pytest.raises(InvalidArtifactRecord, match="adopter_divergence_policy"):
        _parse_record(bad)


def test_loader_rejects_divergence_on_preserve() -> None:
    """upgrade_policy='preserve' with adopter_divergence_policy must raise."""
    bad: dict[str, object] = {
        "class": "ownership-glob",
        "id": "test-preserve-with-div",
        "path_glob": "foo.txt",
        "priority": 10,
        "initial_profiles": [],
        "managed_profiles": [],
        "doctor_required_profiles": [],
        "ownership": "adopter-owned",
        "upgrade_policy": "preserve",
        "adopter_divergence_policy": "warn",  # forbidden on preserve
    }
    with pytest.raises(InvalidArtifactRecord, match="adopter_divergence_policy"):
        _parse_record(bad)


def test_loader_rejects_divergence_on_transient() -> None:
    """upgrade_policy='transient' with adopter_divergence_policy must raise."""
    bad: dict[str, object] = {
        "class": "ownership-glob",
        "id": "test-transient-with-div",
        "path_glob": ".cache/**",
        "priority": 10,
        "initial_profiles": [],
        "managed_profiles": [],
        "doctor_required_profiles": [],
        "ownership": "gt-kb-managed",
        "upgrade_policy": "transient",
        "adopter_divergence_policy": "warn",  # forbidden on transient
    }
    with pytest.raises(InvalidArtifactRecord, match="adopter_divergence_policy"):
        _parse_record(bad)


# ---------------------------------------------------------------------------
# GO C1 — all-or-none default semantics
# ---------------------------------------------------------------------------


def test_legacy_row_with_no_ownership_keys_receives_class_default() -> None:
    """Old-style row with NO ownership keys gets the class default block (C1)."""
    legacy: dict[str, object] = {
        "class": "hook",
        "id": "hook.legacy-no-ownership",
        "template_path": "hooks/foo.py",
        "target_path": ".claude/hooks/foo.py",
        "initial_profiles": ["local-only"],
        "managed_profiles": [],
        "doctor_required_profiles": [],
        # NO ownership / upgrade_policy / adopter_divergence_policy keys at all
    }
    artifact = _parse_record(legacy)
    assert isinstance(artifact, FileArtifact)
    assert artifact.ownership is not None
    # Class defaults for hook = gt-kb-managed / overwrite / warn.
    assert artifact.ownership.ownership == "gt-kb-managed"
    assert artifact.ownership.upgrade_policy == "overwrite"
    assert artifact.ownership.adopter_divergence_policy == "warn"


def test_partial_ownership_row_with_overwrite_but_missing_divergence_raises() -> None:
    """GO C1: a row with ownership OR upgrade_policy present MUST be fully valid.

    Explicitly: ``upgrade_policy='overwrite'`` with neither divergence policy nor
    ownership present must raise rather than silently fill defaults.
    """
    bad: dict[str, object] = {
        "class": "hook",
        "id": "hook.partial-ownership",
        "template_path": "hooks/foo.py",
        "target_path": ".claude/hooks/foo.py",
        "initial_profiles": ["local-only"],
        "managed_profiles": [],
        "doctor_required_profiles": [],
        "upgrade_policy": "overwrite",
        # ownership key is absent → partial block → must raise
        # adopter_divergence_policy is absent → overwrite requires it
    }
    with pytest.raises(InvalidArtifactRecord):
        _parse_record(bad)


# ---------------------------------------------------------------------------
# Resolver agreement with loader
# ---------------------------------------------------------------------------


def test_resolver_sees_every_loader_record() -> None:
    """OwnershipResolver.all_records() count equals loader record count."""
    resolver = OwnershipResolver()
    loader_records = _load_all_artifacts()
    all_resolver = resolver.all_records()
    assert len(all_resolver) == len(loader_records)
    # IDs match 1-for-1 (set equality).
    assert {r.id for r in all_resolver} == {r.id for r in loader_records}


def test_resolver_classify_path_matches_registry_target_path() -> None:
    """For every FILE-class row, classify_path(row.target_path).id == row.id."""
    resolver = OwnershipResolver()
    for row in _load_all_artifacts():
        if isinstance(row, FileArtifact):
            result = resolver.classify_path(row.target_path)
            assert result.id == row.id, (
                f"classify_path({row.target_path!r}) returned id={result.id!r}, expected {row.id!r}"
            )


def test_resolver_registry_row_wins_over_glob_on_exact_match() -> None:
    """FILE-class target_path wins over any ownership-glob that would also match."""
    # .claude/hooks/assertion-check.py is a registry row; we verify it wins
    # even though any hypothetical glob like ".claude/**" could also match.
    resolver = OwnershipResolver()
    rec = resolver.classify_path(".claude/hooks/assertion-check.py")
    assert rec.id == "hook.assertion-check"
    assert rec.source_class == "file"


def test_resolver_path_classification_excludes_settings_and_gitignore() -> None:
    """classify_path(.claude/settings.json) never returns a settings-hook-registration row.

    Settings-hook-registration rows collide on ``target_settings_path`` (11 rows
    share ``.claude/settings.json``) so they are intentionally excluded from
    path-based classification. They remain accessible via ``classify_by_id``.
    """
    resolver = OwnershipResolver()
    rec = resolver.classify_path(".claude/settings.json")
    # Settings-hook-registration rows must NOT appear here.
    assert rec.source_class != "settings-hook-registration"
    # Either ownership-glob (if a glob matched) or __fallback__ is acceptable.
    assert rec.source_class in ("ownership-glob", "__fallback__", "file")


# ---------------------------------------------------------------------------
# Helper regression — existing code paths untouched by sibling file
# ---------------------------------------------------------------------------


def test_artifacts_for_scaffold_unchanged_by_sibling_file() -> None:
    """With scaffold-ownership.toml present, artifacts_for_scaffold still returns the original 40 IDs.

    The sibling file contains only ownership-glob records which are filtered
    out by the helper.
    """
    # Expected per proposal: local-only = 15 (14 hooks + 1 rule)
    ids = {a.id for a in artifacts_for_scaffold("local-only")}
    assert len(ids) == 15
    # dual-agent scaffold pulls all 40 registry rows.
    ids_da = {a.id for a in artifacts_for_scaffold("dual-agent")}
    assert len(ids_da) == 40
    # None are ownership-glob.
    assert all("adopter-" not in i for i in ids_da), "ownership-glob leaked into scaffold"


def test_artifacts_for_upgrade_unchanged_by_sibling_file() -> None:
    """artifacts_for_upgrade filters out ownership-glob rows."""
    for profile in ("local-only", "dual-agent", "dual-agent-webapp"):
        results = artifacts_for_upgrade(profile)
        for a in results:
            assert a.class_ != "ownership-glob", f"ownership-glob leaked into upgrade for {profile}: {a.id}"


def test_artifacts_for_doctor_unchanged_by_sibling_file() -> None:
    """artifacts_for_doctor filters out ownership-glob rows."""
    for profile in ("local-only", "dual-agent", "dual-agent-webapp"):
        results = artifacts_for_doctor(profile)
        for a in results:
            assert a.class_ != "ownership-glob", f"ownership-glob leaked into doctor for {profile}: {a.id}"
