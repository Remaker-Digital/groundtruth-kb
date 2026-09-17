# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for :mod:`groundtruth_kb.project.managed_registry`.

Covers:

- parse / roundtrip / schema-validation of ``templates/managed-artifacts.toml``
- lifecycle-axis invariants (``managed ⊆ initial``, ``doctor_required ⊆ initial``)
- lifecycle-matrix tests (scaffold × profile, upgrade × profile)
- doctor-axis parity per profile
- settings-registration parity (exact retained event-to-hook matrix)
- Condition 2 composite-ID trio (Codex GO at
  ``bridge/gtkb-managed-artifact-registry-008.md``).

The registry is the single source of truth for scaffold, upgrade, and
doctor lifecycle behavior. These tests treat the TOML file as the spec
and the loader as the executable contract.
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
    assert len(records) == 37


def test_bridge_skill_records_are_managed_for_dual_agent_profiles() -> None:
    """The bridge skill template is scaffolded and upgrade-managed as Tier A."""
    expected_targets = {
        ".claude/skills/gtkb-bridge/SKILL.md",
        ".claude/skills/gtkb-bridge/helpers/scan_bridge.py",
        ".claude/skills/gtkb-bridge/helpers/show_thread_bridge.py",
    }

    scaffold_targets = {
        r.target_path for r in artifacts_for_scaffold("dual-agent", class_="skill") if isinstance(r, FileArtifact)
    }
    upgrade_targets = {
        r.target_path for r in artifacts_for_upgrade("dual-agent", class_="skill") if isinstance(r, FileArtifact)
    }

    assert expected_targets <= scaffold_targets
    assert expected_targets <= upgrade_targets


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


def test_upgrade_local_only_manages_retained_hook() -> None:
    """local-only upgrade manages 1 hook plus 5 rules and 1 skill.

    Post-canonical-terminology-surface: local-only upgrade-managed rules grew
    from 1 to 3 because both new canonical-terminology records have
    ``managed_profiles`` covering all three profiles.
    Post gtkb-session-start-orientation-gate: +1 rule, +1 skill.
    """
    managed = artifacts_for_upgrade("local-only")
    hooks = {r.target_path for r in managed if isinstance(r, FileArtifact) and r.class_ == "hook"}
    assert hooks == set()
    rules = {r.target_path for r in managed if isinstance(r, FileArtifact) and r.class_ == "rule"}
    assert rules == {
        ".claude/rules/prime-builder.md",
        ".claude/rules/canonical-terminology.md",
        ".claude/rules/canonical-terminology.toml",
        ".claude/rules/canonical-terminology-policy.toml",
        ".claude/rules/session-start-orientation.md",
    }
    # 1 skill (baseline-audit); no settings or gitignore for local-only
    skills = [r for r in managed if r.class_ == "skill"]
    assert len(skills) == 1
    assert skills[0].id == "skill.baseline-audit.skill-md"
    assert [r for r in managed if r.class_ == "settings-hook-registration"] == []
    assert [r for r in managed if r.class_ == "gitignore-pattern"] == []


def test_upgrade_dual_agent_manages_full_set_including_gap_28_rules() -> None:
    """dual-agent upgrade includes the 3 Gap 2.8 bridge rules + canonical-terminology pair.

    Post-canonical-terminology-surface: dual-agent upgrade-managed rules grew
    from 8 to 10 with the addition of ``canonical-terminology.{md,toml}``.
    """
    managed_rule_paths = {
        r.target_path for r in artifacts_for_upgrade("dual-agent", class_="rule") if isinstance(r, FileArtifact)
    }
    # The 5 pre-C1 managed rules
    assert ".claude/rules/prime-builder.md" in managed_rule_paths
    assert ".claude/rules/loyal-opposition.md" in managed_rule_paths
    assert ".claude/rules/bridge-poller-canonical.md" in managed_rule_paths
    assert ".claude/rules/prime-bridge-collaboration-protocol.md" in managed_rule_paths
    assert ".claude/rules/report-depth.md" in managed_rule_paths
    # The 3 Gap 2.8 rules added by C1
    assert ".claude/rules/file-bridge-protocol.md" in managed_rule_paths
    assert ".claude/rules/bridge-essential.md" in managed_rule_paths
    assert ".claude/rules/deliberation-protocol.md" in managed_rule_paths
    # The 2 canonical-terminology rules added post-C1
    assert ".claude/rules/canonical-terminology.md" in managed_rule_paths
    assert ".claude/rules/canonical-terminology.toml" in managed_rule_paths
    # +1: canonical-terminology-policy added by Slice 1 of GTKB-GOV-TERM-DISAMBIGUATION-MECHANICAL
    assert ".claude/rules/canonical-terminology-policy.toml" in managed_rule_paths
    # +1: session-start-orientation (gtkb-session-start-orientation-gate)
    assert ".claude/rules/session-start-orientation.md" in managed_rule_paths
    assert len(managed_rule_paths) == 12


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


def test_doctor_rules_bridge_profiles_are_three() -> None:
    """For bridge profiles, doctor requires the 3 Gap 2.8 bridge rules."""
    for profile in ("dual-agent", "dual-agent-webapp"):
        rule_names = {
            r.target_path.split("/")[-1]
            for r in artifacts_for_doctor(profile, class_="rule")
            if isinstance(r, FileArtifact)
        }
        assert rule_names == {
            "file-bridge-protocol.md",
            "bridge-essential.md",
            "deliberation-protocol.md",
        }


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


def test_condition2_composite_ids_exist_and_resolve() -> None:
    """Three canonical scanner-safe-writer IDs exist, are unique, and resolve via loader."""
    hook = find_artifact_by_id("hook.scanner-safe-writer")
    settings = find_artifact_by_id("settings.hook.scanner-safe-writer.pretooluse")
    gitignore = find_artifact_by_id("gitignore.hook-logs")

    assert isinstance(hook, FileArtifact)
    assert hook.class_ == "hook"
    assert hook.target_path == ".claude/hooks/scanner-safe-writer.py"

    assert isinstance(settings, SettingsHookRegistration)
    assert settings.event == "PreToolUse"
    assert settings.hook_filename == "scanner-safe-writer.py"

    assert isinstance(gitignore, GitignorePattern)
    assert gitignore.pattern == ".claude/hooks/*.log"

    # Uniqueness — all three IDs are distinct.
    assert len({hook.id, settings.id, gitignore.id}) == 3


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
        "gitignore.hook-logs": replace(find_artifact_by_id("gitignore.hook-logs"), pattern="custom/*.log"),
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
    (tmp_path / ".gitignore").write_text("custom/*.log\n", encoding="utf-8")
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
