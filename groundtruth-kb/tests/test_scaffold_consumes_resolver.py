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
    """local-only scaffold returns the four authored hook identities + 2 file-class records (6 total).

    M15 (D15/D34, edit-m15-34): rule and skill copy rows, the bridge-compliance pair and session-health are
    retired; hooks run in place from the baseline and are identified, not copied.
    """
    ids = sorted(a.id for a in artifacts_for_scaffold("local-only"))
    expected = sorted(
        [
            "hook.destructive-gate",
            "hook.credential-scan",
            "hook.scanner-safe-writer",
            "hook.kb-not-markdown",
            "file.readme-quickstart",
            "file.release-readiness-banner",
        ]
    )
    assert ids == expected


def test_scaffold_dual_agent_id_set_matches_baseline() -> None:
    """The current bridge profile delivers the 13 retained registry records (M15: no rule/skill copies)."""
    ids = sorted(a.id for a in artifacts_for_scaffold("dual-agent"))
    assert len(ids) == 13
    assert not [identifier for identifier in ids if identifier.startswith(("rule.", "skill."))]
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
