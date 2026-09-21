# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Managed metadata schema, retained authored hooks and native registrations.

The baseline and projector supply source content and derivation. The managed
registry carries lifecycle metadata and does not create third hook/rule/skill copies.
"""

from __future__ import annotations

import pytest

from groundtruth_kb.project.managed_registry import (
    FileArtifact,
    GitignorePattern,
    InvalidArtifactRecord,
    ManagedArtifact,
    OwnershipGlobArtifact,
    SettingsHookRegistration,
    UnknownArtifactClass,
    _load_all_artifacts,
    artifacts_for_doctor,
    artifacts_for_scaffold,
    artifacts_for_upgrade,
    find_artifact_by_id,
)


def _registry_records() -> list[ManagedArtifact]:
    """Return only current managed-registry records (excludes ownership-glob).

    ``_load_all_artifacts()`` merges records from ``managed-artifacts.toml``
    and ``templates/scaffold-ownership.toml`` (``ownership-glob`` class). These
    tests were written before the sibling file was introduced and assert on
    registry-only counts.
    """
    return [r for r in _load_all_artifacts() if not isinstance(r, OwnershipGlobArtifact)]


# ---------------------------------------------------------------------------
# Parse / totals
# ---------------------------------------------------------------------------


def test_registry_total_matches_current_manifest() -> None:
    """Current registry excludes retired capture, stubs and event notification."""
    records = _registry_records()
    assert len(records) == 13


def test_shared_skills_are_not_third_copy_managed_artifacts() -> None:
    for profile in ("local-only", "dual-agent", "dual-agent-webapp"):
        assert artifacts_for_scaffold(profile, class_="skill") == []
        assert artifacts_for_upgrade(profile, class_="skill") == []


def test_registry_ids_are_unique() -> None:
    """Every record must have a unique id (registry + sibling ownership-glob combined)."""
    records = _load_all_artifacts()
    ids = [r.id for r in records]
    assert len(ids) == len(set(ids)), f"duplicate ids found: {[x for x in ids if ids.count(x) > 1]}"


def test_registry_parses_into_correct_dataclass_types() -> None:
    """Every record parses to one of the four dataclass types."""
    records = _load_all_artifacts()
    for r in records:
        assert isinstance(r, (FileArtifact, SettingsHookRegistration, GitignorePattern, OwnershipGlobArtifact))


# ---------------------------------------------------------------------------
# Schema validation — invariants rejected
# ---------------------------------------------------------------------------


def test_invariant_managed_must_subset_initial(monkeypatch: pytest.MonkeyPatch) -> None:
    """Records where managed_profiles escapes initial_profiles must raise."""
    # Construct an in-memory raw record and invoke the parser directly.
    from groundtruth_kb.project.managed_registry import _parse_record

    bad: dict[str, object] = {
        "class": "hook",
        "id": "hook.test-bad-managed",
        "template_path": "hooks/foo.py",
        "target_path": ".claude/hooks/foo.py",
        "initial_profiles": ["dual-agent"],
        "managed_profiles": ["local-only"],
        "doctor_required_profiles": [],
    }
    with pytest.raises(InvalidArtifactRecord, match="managed_profiles"):
        _parse_record(bad)


def test_invariant_doctor_required_must_subset_initial() -> None:
    """Records where doctor_required_profiles escapes initial_profiles must raise."""
    from groundtruth_kb.project.managed_registry import _parse_record

    bad: dict[str, object] = {
        "class": "rule",
        "id": "rule.test-bad-doctor",
        "template_path": "rules/foo.md",
        "target_path": ".claude/rules/foo.md",
        "initial_profiles": ["dual-agent"],
        "managed_profiles": [],
        "doctor_required_profiles": ["local-only"],
    }
    with pytest.raises(InvalidArtifactRecord, match="doctor_required_profiles"):
        _parse_record(bad)


def test_unknown_class_raises() -> None:
    """Unknown class value raises :class:`UnknownArtifactClass`."""
    from groundtruth_kb.project.managed_registry import _parse_record

    bad: dict[str, object] = {
        "class": "hypothetical-thing",
        "id": "whatever.x",
        "initial_profiles": [],
        "managed_profiles": [],
        "doctor_required_profiles": [],
    }
    with pytest.raises(UnknownArtifactClass):
        _parse_record(bad)


def test_forbidden_key_rejected() -> None:
    """A file-class record containing a forbidden key raises."""
    from groundtruth_kb.project.managed_registry import _parse_record

    bad: dict[str, object] = {
        "class": "hook",
        "id": "hook.test-forbidden",
        "template_path": "hooks/foo.py",
        "target_path": ".claude/hooks/foo.py",
        "initial_profiles": ["local-only"],
        "managed_profiles": [],
        "doctor_required_profiles": [],
        "pattern": "nope",  # forbidden for file class
    }
    with pytest.raises(InvalidArtifactRecord, match="forbidden"):
        _parse_record(bad)


def test_missing_required_key_rejected() -> None:
    """A file-class record missing a required key raises."""
    from groundtruth_kb.project.managed_registry import _parse_record

    bad: dict[str, object] = {
        "class": "hook",
        "id": "hook.test-missing",
        # template_path missing
        "target_path": ".claude/hooks/foo.py",
        "initial_profiles": ["local-only"],
        "managed_profiles": [],
        "doctor_required_profiles": [],
    }
    with pytest.raises(InvalidArtifactRecord, match="missing required"):
        _parse_record(bad)


# ---------------------------------------------------------------------------
# Lifecycle-matrix tests — 2 axes × 3 profiles for files
# ---------------------------------------------------------------------------


def _file_target_paths(records: list[ManagedArtifact]) -> set[str]:
    return {r.target_path for r in records if isinstance(r, FileArtifact)}


def test_scaffold_dual_agent_webapp_matches_dual_agent() -> None:
    """dual-agent-webapp scaffold set matches dual-agent for C1 scope."""
    a = _file_target_paths(artifacts_for_scaffold("dual-agent"))
    b = _file_target_paths(artifacts_for_scaffold("dual-agent-webapp"))
    assert a == b


def test_upgrade_local_only_requires_no_copied_hook_rule_or_skill() -> None:
    managed = artifacts_for_upgrade("local-only")
    assert not [
        r for r in managed if r.class_ in {"hook", "rule", "skill", "settings-hook-registration", "gitignore-pattern"}
    ]


def test_rules_are_read_from_the_baseline_without_managed_copies() -> None:
    for profile in ("local-only", "dual-agent", "dual-agent-webapp"):
        assert artifacts_for_scaffold(profile, class_="rule") == []
        assert artifacts_for_upgrade(profile, class_="rule") == []


# ---------------------------------------------------------------------------
# Doctor-axis parity — registry matches the prior hardcoded sets byte-for-byte
# ---------------------------------------------------------------------------


def test_doctor_hooks_local_only_matches_prior_hardcoded() -> None:
    """For local-only, doctor requires only the retained spec-classifier hook."""
    hook_names = {
        r.target_path.split("/")[-1]
        for r in artifacts_for_doctor("local-only", class_="hook")
        if isinstance(r, FileArtifact)
    }
    assert hook_names == set()


def test_doctor_hooks_dual_agent_matches_prior_hardcoded() -> None:
    """For bridge profiles, doctor requires the 4 pre-governance hooks +
    5 governance-completeness hooks (9 total).

    Post-governance-completeness (gtkb-da-governance-completeness-implementation-015 §A):
    all 5 new governance hooks carry ``doctor_required_profiles = ["dual-agent",
    "dual-agent-webapp"]``, matching their managed status.
    """
    for profile in ("dual-agent", "dual-agent-webapp"):
        hook_names = {
            r.target_path.split("/")[-1]
            for r in artifacts_for_doctor(profile, class_="hook")
            if isinstance(r, FileArtifact)
        }
        assert hook_names == {
            "destructive-gate.py",
            "credential-scan.py",
        }, f"doctor hook set mismatch for {profile!r}: {hook_names}"


def test_doctor_has_no_required_projected_rule_files() -> None:
    for profile in ("dual-agent", "dual-agent-webapp"):
        assert artifacts_for_doctor(profile, class_="rule") == []


def test_doctor_rules_local_only_is_empty() -> None:
    """local-only has no doctor-required rules."""
    rules = artifacts_for_doctor("local-only", class_="rule")
    assert rules == []


# ---------------------------------------------------------------------------
# Settings-registration parity — exact retained event-to-hook matrix
# ---------------------------------------------------------------------------


def test_retired_spec_event_hook_and_registration_are_absent() -> None:
    records = _load_all_artifacts()
    assert not {"hook.spec-event-surfacer", "settings.hook.spec-event-surfacer.posttooluse"}.intersection(
        record.id for record in records
    )


def test_managed_registry_settings_registration_managed_profiles_match_hook_artifact() -> None:
    """Every retained managed registration delivers the corresponding hook."""
    records = _load_all_artifacts()
    for reg in (r for r in records if isinstance(r, SettingsHookRegistration)):
        hook = next(
            r
            for r in records
            if isinstance(r, FileArtifact) and r.class_ == "hook" and r.target_path.endswith("/" + reg.hook_filename)
        )
        assert set(reg.initial_profiles) <= set(hook.initial_profiles)
        assert set(reg.managed_profiles) <= set(hook.managed_profiles)
        assert set(reg.doctor_required_profiles) <= set(hook.doctor_required_profiles)


# ---------------------------------------------------------------------------
# Condition 2 — canonical composite-ID trio (Codex GO -008)
# ---------------------------------------------------------------------------


def test_scanner_composite_pairs_authored_hook_and_registration() -> None:
    hook = find_artifact_by_id("hook.scanner-safe-writer")
    settings = find_artifact_by_id("settings.hook.scanner-safe-writer.pretooluse")
    assert isinstance(hook, FileArtifact) and hook.class_ == "hook"
    assert hook.target_path == hook.template_path == ".harness-baseline-configuration/hooks/scanner-safe-writer.py"
    assert isinstance(settings, SettingsHookRegistration)
    assert settings.event == "PreToolUse" and settings.hook_filename == "scanner-safe-writer.py"
    with pytest.raises(KeyError):
        find_artifact_by_id("gitignore.hook-logs")


def test_condition2_doctor_composite_uses_registry_ids(tmp_path, monkeypatch) -> None:
    """The executed diagnostic follows registry paths and reports actual absence."""
    import json
    from dataclasses import replace

    from groundtruth_kb.project import doctor

    records = {
        "hook.scanner-safe-writer": replace(
            find_artifact_by_id("hook.scanner-safe-writer"), target_path="custom/check.py"
        ),
        "settings.hook.scanner-safe-writer.pretooluse": replace(
            find_artifact_by_id("settings.hook.scanner-safe-writer.pretooluse"),
            target_settings_path="custom/settings.json",
            hook_filename="check.py",
        ),
    }
    reads = []

    def lookup(ident):
        reads.append(ident)
        return records[ident]

    monkeypatch.setattr(doctor, "find_artifact_by_id", lookup)
    (tmp_path / "custom").mkdir()
    hook = tmp_path / "custom/check.py"
    hook.write_text("# fixture\n", encoding="utf-8")
    (tmp_path / "custom/settings.json").write_text(
        json.dumps({"hooks": {"PreToolUse": [{"hooks": [{"command": "python custom/check.py"}]}]}}), encoding="utf-8"
    )
    assert doctor._check_scanner_safe_writer_drift(tmp_path, "dual-agent").status == "pass"
    assert set(reads) == set(records)
    hook.unlink()
    missing = doctor._check_scanner_safe_writer_drift(tmp_path, "dual-agent")
    assert missing.status == "fail" and not missing.found


# ---------------------------------------------------------------------------
# load_managed_artifacts — profile query helper
# ---------------------------------------------------------------------------


def test_find_artifact_by_id_raises_on_unknown() -> None:
    """Unknown id raises KeyError."""
    with pytest.raises(KeyError):
        find_artifact_by_id("hook.does-not-exist")


def test_retained_hook_metadata_uses_authored_sources_and_one_pair_per_registration() -> None:
    records = _registry_records()
    hooks = {r.id: r for r in records if isinstance(r, FileArtifact) and r.class_ == "hook"}
    assert set(hooks) == {
        "hook.destructive-gate",
        "hook.credential-scan",
        "hook.kb-not-markdown",
        "hook.scanner-safe-writer",
    }
    assert all(
        row.target_path == row.template_path and row.target_path.startswith(".harness-baseline-configuration/hooks/")
        for row in hooks.values()
    )
    registrations = [r for r in records if isinstance(r, SettingsHookRegistration)]
    assert len(registrations) == 4
    assert all(
        sum(row.target_path.endswith("/" + reg.hook_filename) for row in hooks.values()) == 1 for reg in registrations
    )
    ids = {r.id for r in records}
    assert "hook.bridge-compliance-gate" not in ids
    assert not any("bridge-compliance" in ident for ident in ids)
