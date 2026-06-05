# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Regression gate: scaffold behavior unchanged by ownership-matrix sub-bridge.

Proposal §3.3 — scaffold copy planning must be bit-identical before and after
this sub-bridge introduced ``ownership-glob`` rows. We assert on the stable
``artifacts_for_scaffold(profile)`` output.
"""

from __future__ import annotations

from groundtruth_kb.project.managed_registry import (
    FileArtifact,
    GitignorePattern,
    SettingsHookRegistration,
    artifacts_for_scaffold,
)


def test_scaffold_local_only_id_set_matches_baseline() -> None:
    """local-only scaffold returns 14 hooks + 4 rules + 3 file-class records (21 total).

    Baseline post-canonical-terminology (v0.6.1): 14 hooks + 3 rules.
    Post-Slice-1 GTKB-GOV-TERM-DISAMBIGUATION-MECHANICAL: + rule.canonical-terminology-policy.
    Post-Slice-3 GTKB-ISOLATION-017: + file.readme-quickstart, file.release-readiness-banner.
    Post-Slice-4 GTKB-ISOLATION-017: + file.upgrade-rehearsal-recipe.
    """
    ids = sorted(a.id for a in artifacts_for_scaffold("local-only"))
    expected = sorted(
        [
            "hook.assertion-check",
            "hook.spec-classifier",
            "hook.intake-classifier",
            "hook.destructive-gate",
            "hook.credential-scan",
            "hook.scheduler",
            "hook.scanner-safe-writer",
            "hook.bridge-compliance-gate",
            "hook.delib-search-gate",
            "hook.delib-search-tracker",
            "hook.kb-not-markdown",
            "hook.session-health",
            "hook.session-start-governance",
            "hook.spec-before-code",
            "rule.prime-builder",
            "rule.canonical-terminology",
            "rule.canonical-terminology-config",
            "rule.canonical-terminology-policy",
            "file.readme-quickstart",
            "file.release-readiness-banner",
            "file.upgrade-rehearsal-recipe",
        ]
    )
    assert ids == expected


def test_scaffold_dual_agent_id_set_matches_baseline() -> None:
    """dual-agent scaffold returns the full 60-record registry set.

    Post-C4 (gtkb-settings-merge): 51 → 54 via 3 new adopter-critical
    gitignore-pattern rows (groundtruth.db, .groundtruth/,
    .claude/settings.local.json).
    Post-spec-event-surfacer (Slice A): 54 → 56 (+ hook + settings).
    Post-Slice-3 GTKB-ISOLATION-017: 56 → 58 (+2 file).
    Post-Slice-1 GTKB-GOV-TERM-DISAMBIGUATION-MECHANICAL: 58 → 59 (+1 rule).
    Post-Slice-4 GTKB-ISOLATION-017: 59 → 60 (+1 file upgrade-rehearsal-recipe).

    Post-governance-completeness: 42 v0.6.1 rows + 9 new governance records
    (5 hook-class + 4 settings-hook-registration) = 51. See
    gtkb-da-governance-completeness-implementation-016.
    """
    ids = sorted(a.id for a in artifacts_for_scaffold("dual-agent"))
    assert len(ids) == 66
    # None are ownership-glob.
    for a in artifacts_for_scaffold("dual-agent"):
        assert isinstance(a, (FileArtifact, SettingsHookRegistration, GitignorePattern))


def test_scaffold_dual_agent_webapp_matches_dual_agent() -> None:
    """dual-agent-webapp scaffold set equals dual-agent set (per C1 scope)."""
    a = sorted(x.id for x in artifacts_for_scaffold("dual-agent"))
    b = sorted(x.id for x in artifacts_for_scaffold("dual-agent-webapp"))
    assert a == b


def test_scaffold_no_ownership_glob_records_leak() -> None:
    """Sibling ownership-glob rows must never appear in scaffold results."""
    for profile in ("local-only", "dual-agent", "dual-agent-webapp"):
        for a in artifacts_for_scaffold(profile):
            assert a.class_ != "ownership-glob", f"ownership-glob leaked into scaffold for {profile}: {a.id}"
