# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for :mod:`groundtruth_kb.project.managed_registry`.

Covers:

- parse / roundtrip / schema-validation of ``templates/managed-artifacts.toml``
- lifecycle-axis invariants (``managed ⊆ initial``, ``doctor_required ⊆ initial``)
- lifecycle-matrix tests (scaffold × profile, upgrade × profile)
- doctor-axis parity per profile
- settings-registration parity (exact 11-row event-to-hook matrix)
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
    load_managed_artifacts,
)


def _registry_records() -> list[ManagedArtifact]:
    """Return only the original 40 managed-registry records (excludes ownership-glob).

    ``_load_all_artifacts()`` merges records from ``managed-artifacts.toml``
    and ``templates/scaffold-ownership.toml`` (``ownership-glob`` class). These
    tests were written before the sibling file was introduced and assert on
    registry-only counts.
    """
    return [r for r in _load_all_artifacts() if not isinstance(r, OwnershipGlobArtifact)]


# ---------------------------------------------------------------------------
# Parse / totals
# ---------------------------------------------------------------------------


def test_registry_total_is_forty_two_records() -> None:
    """42 total = 14 hooks + 10 rules + 6 skills + 11 settings + 1 gitignore.

    Post-canonical-terminology-surface: rule count rose from 8 to 10 with the
    addition of ``rule.canonical-terminology`` and
    ``rule.canonical-terminology-config`` (see
    ``bridge/gtkb-canonical-terminology-surface-implementation-007.md`` Option B).

    ``ownership-glob`` rows from ``templates/scaffold-ownership.toml`` are
    excluded via ``_registry_records()`` helper — this test scope is
    registry-only.
    """
    records = _registry_records()
    assert len(records) == 42, f"expected 42 total registry records; got {len(records)}"


def test_registry_class_counts_match_proposal() -> None:
    """Class counts match the approved proposal (post-canonical-terminology)."""
    records = _registry_records()
    counts: dict[str, int] = {}
    for r in records:
        counts[r.class_] = counts.get(r.class_, 0) + 1
    assert counts == {
        "hook": 14,
        "rule": 10,
        "skill": 6,
        "settings-hook-registration": 11,
        "gitignore-pattern": 1,
    }


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


def test_scaffold_local_only_copies_all_hooks_and_initial_rules() -> None:
    """local-only scaffold copies all 14 hooks plus the 3 initial local-only rules.

    Post-canonical-terminology-surface: local-only initial rules grew from 1
    (prime-builder) to 3 with the addition of ``canonical-terminology.md`` and
    ``canonical-terminology.toml``.
    """
    scaffolded = artifacts_for_scaffold("local-only")
    # 14 hooks
    hooks = [r for r in scaffolded if r.class_ == "hook"]
    assert len(hooks) == 14
    # 3 rules (prime-builder + canonical-terminology surface)
    rules = [r for r in scaffolded if r.class_ == "rule"]
    rule_paths = {r.target_path for r in rules if isinstance(r, FileArtifact)}
    assert rule_paths == {
        ".claude/rules/prime-builder.md",
        ".claude/rules/canonical-terminology.md",
        ".claude/rules/canonical-terminology.toml",
    }
    # 0 skills, 0 settings, 0 gitignore-patterns
    assert [r for r in scaffolded if r.class_ == "skill"] == []
    assert [r for r in scaffolded if r.class_ == "settings-hook-registration"] == []
    assert [r for r in scaffolded if r.class_ == "gitignore-pattern"] == []


def test_scaffold_dual_agent_copies_everything() -> None:
    """dual-agent scaffold copies 14 hooks + 10 rules + 6 skills + 11 settings + 1 gitignore.

    Rule count rose from 8 to 10 post-canonical-terminology-surface.
    """
    scaffolded = artifacts_for_scaffold("dual-agent")
    by_class: dict[str, int] = {}
    for r in scaffolded:
        by_class[r.class_] = by_class.get(r.class_, 0) + 1
    assert by_class == {
        "hook": 14,
        "rule": 10,
        "skill": 6,
        "settings-hook-registration": 11,
        "gitignore-pattern": 1,
    }


def test_scaffold_dual_agent_webapp_matches_dual_agent() -> None:
    """dual-agent-webapp scaffold set matches dual-agent for C1 scope."""
    a = _file_target_paths(artifacts_for_scaffold("dual-agent"))
    b = _file_target_paths(artifacts_for_scaffold("dual-agent-webapp"))
    assert a == b


def test_upgrade_local_only_manages_two_hooks() -> None:
    """local-only upgrade manages 2 hooks plus 3 rules (prime-builder + canonical-terminology.{md,toml}).

    Post-canonical-terminology-surface: local-only upgrade-managed rules grew
    from 1 to 3 because both new canonical-terminology records have
    ``managed_profiles`` covering all three profiles.
    """
    managed = artifacts_for_upgrade("local-only")
    hooks = {r.target_path for r in managed if isinstance(r, FileArtifact) and r.class_ == "hook"}
    assert hooks == {
        ".claude/hooks/assertion-check.py",
        ".claude/hooks/spec-classifier.py",
    }
    rules = {r.target_path for r in managed if isinstance(r, FileArtifact) and r.class_ == "rule"}
    assert rules == {
        ".claude/rules/prime-builder.md",
        ".claude/rules/canonical-terminology.md",
        ".claude/rules/canonical-terminology.toml",
    }
    # No skills or settings or gitignore for local-only
    assert [r for r in managed if r.class_ == "skill"] == []
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
    assert len(managed_rule_paths) == 10


# ---------------------------------------------------------------------------
# Doctor-axis parity — registry matches the prior hardcoded sets byte-for-byte
# ---------------------------------------------------------------------------


def test_doctor_hooks_local_only_matches_prior_hardcoded() -> None:
    """For local-only, doctor requires exactly {assertion-check, spec-classifier}."""
    hook_names = {
        r.target_path.split("/")[-1]
        for r in artifacts_for_doctor("local-only", class_="hook")
        if isinstance(r, FileArtifact)
    }
    assert hook_names == {"assertion-check.py", "spec-classifier.py"}


def test_doctor_hooks_dual_agent_matches_prior_hardcoded() -> None:
    """For bridge profiles, doctor requires the 4-hook set (includes destructive-gate, credential-scan)."""
    for profile in ("dual-agent", "dual-agent-webapp"):
        hook_names = {
            r.target_path.split("/")[-1]
            for r in artifacts_for_doctor(profile, class_="hook")
            if isinstance(r, FileArtifact)
        }
        assert hook_names == {
            "assertion-check.py",
            "spec-classifier.py",
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
# Settings-registration parity — exact 11-row event-to-hook matrix
# ---------------------------------------------------------------------------


def test_settings_parity_exact_eleven_row_matrix() -> None:
    """Registry produces the exact 11-row event-to-hook matrix enforced by scaffold."""
    registrations = artifacts_for_scaffold("dual-agent", class_="settings-hook-registration")
    assert len(registrations) == 11, (
        f"expected 11 settings-hook-registration records for dual-agent; got {len(registrations)}"
    )
    # Collect per-event sorted hook filenames
    by_event: dict[str, list[str]] = {}
    for reg in registrations:
        assert isinstance(reg, SettingsHookRegistration)
        by_event.setdefault(reg.event, []).append(reg.hook_filename)
    for event in by_event:
        by_event[event].sort()

    expected = {
        "SessionStart": sorted(["session-start-governance.py", "assertion-check.py"]),
        "UserPromptSubmit": sorted(["delib-search-gate.py", "intake-classifier.py"]),
        "PostToolUse": sorted(["delib-search-tracker.py"]),
        "PreToolUse": sorted(
            [
                "spec-before-code.py",
                "bridge-compliance-gate.py",
                "kb-not-markdown.py",
                "destructive-gate.py",
                "credential-scan.py",
                "scanner-safe-writer.py",
            ]
        ),
    }
    assert by_event == expected


def test_settings_scanner_safe_writer_is_only_managed_pretooluse() -> None:
    """Only scanner-safe-writer PreToolUse registration is upgrade-managed at C1."""
    managed = artifacts_for_upgrade("dual-agent", class_="settings-hook-registration")
    assert len(managed) == 1
    only = managed[0]
    assert isinstance(only, SettingsHookRegistration)
    assert only.hook_filename == "scanner-safe-writer.py"
    assert only.event == "PreToolUse"


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


def test_condition2_doctor_composite_uses_registry_ids() -> None:
    """``_check_scanner_safe_writer_drift`` resolves its inputs via registry IDs.

    Source-level check that the composite check references the three
    canonical IDs (rather than hardcoded strings) — protects against a
    regression where someone re-hardcodes the file paths.
    """
    import inspect

    from groundtruth_kb.project import doctor

    src = inspect.getsource(doctor._check_scanner_safe_writer_drift)
    assert '"hook.scanner-safe-writer"' in src
    assert '"settings.hook.scanner-safe-writer.pretooluse"' in src
    assert '"gitignore.hook-logs"' in src


# ---------------------------------------------------------------------------
# load_managed_artifacts — profile query helper
# ---------------------------------------------------------------------------


def test_load_managed_artifacts_unions_three_axes() -> None:
    """Loader returns records touching the profile in any lifecycle axis."""
    dual_agent = load_managed_artifacts("dual-agent")
    # dual-agent should see all 42 records (ALL hooks in initial, 10 rules, 6 skills,
    # 11 settings, 1 gitignore — all touch dual-agent in at least one axis).
    assert len(dual_agent) == 42

    local_only = load_managed_artifacts("local-only")
    # local-only sees all 14 hooks (initial=ALL) + rule.prime-builder +
    # the 2 canonical-terminology rules = 17 records.
    assert len(local_only) == 17


def test_find_artifact_by_id_raises_on_unknown() -> None:
    """Unknown id raises KeyError."""
    with pytest.raises(KeyError):
        find_artifact_by_id("hook.does-not-exist")
