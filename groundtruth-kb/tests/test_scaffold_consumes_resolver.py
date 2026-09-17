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
    """local-only scaffold returns 13 hooks + 4 rules + 3 file-class records (20 total).

    Baseline post-canonical-terminology (v0.6.1): 14 hooks + 3 rules.
    Post-Slice-1 GTKB-GOV-TERM-DISAMBIGUATION-MECHANICAL: + rule.canonical-terminology-policy.
    Post-Slice-3 GTKB-ISOLATION-017: + file.readme-quickstart, file.release-readiness-banner.
    Post-Slice-4 GTKB-ISOLATION-017: + file.upgrade-rehearsal-recipe (retired with the legacy upgrade wrapper, O-7 R18).
    Post-WI-4628: - retired scheduler hook.
    """
    ids = sorted(a.id for a in artifacts_for_scaffold("local-only"))
    expected = sorted(
        [
            "hook.destructive-gate",
            "hook.credential-scan",
            "hook.scanner-safe-writer",
            "hook.bridge-compliance-gate",
            "hook.kb-not-markdown",
            "hook.session-health",
            "rule.prime-builder",
            "rule.canonical-terminology",
            "rule.canonical-terminology-config",
            "rule.canonical-terminology-policy",
            "rule.session-start-orientation",
            "skill.baseline-audit.skill-md",
            "file.readme-quickstart",
            "file.release-readiness-banner",
        ]
    )
    assert ids == expected


def test_scaffold_dual_agent_id_set_matches_baseline() -> None:
    """The current bridge profile delivers the 37 retained registry records (the rehearsal recipe retired, O-7 R18)."""
    ids = sorted(a.id for a in artifacts_for_scaffold("dual-agent"))
    assert len(ids) == 37
    assert "hook._delib_common" not in ids
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
