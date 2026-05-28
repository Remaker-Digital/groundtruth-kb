"""Static assertions for the governance-hygiene-bundle implementation.

Authority: bridge/gtkb-governance-hygiene-bundle-001.md (Codex GO at -002).

Each test maps to a specific Change letter (A-G) of the bundle. All
assertions are static (file existence + content fingerprints); no live
behavior is exercised. The bundle does not change runtime behavior.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_change_a_stale_duplicates_removed() -> None:
    """Change A — `(1)` duplicate files no longer exist in the working tree.

    Spec: ADR-ISOLATION-APPLICATION-PLACEMENT-001 (in-root cleanup).
    """
    duplicates = [
        PROJECT_ROOT / ".codex" / "gtkb-hooks" / "session-start (1).cmd",
        PROJECT_ROOT / "harness-state" / "codex" / "operating-role (1).md",
    ]
    for path in duplicates:
        assert not path.exists(), f"stale duplicate still present: {path}"


def test_change_b_conventional_commits_discipline_rule_present() -> None:
    """Change B — Conventional Commits type discipline rule added to file-bridge-protocol.md."""
    rule = (PROJECT_ROOT / ".claude" / "rules" / "file-bridge-protocol.md").read_text(encoding="utf-8")
    assert "## Conventional Commits Type Discipline" in rule
    assert "Recommended commit type" in rule or "Recommended Commit Type" in rule
    assert "feat:" in rule
    assert "chore:" in rule
    assert "FINDING-P0-001" in rule


def test_change_c_lo_kb_write_approval_packet_pathway_present() -> None:
    """Change C — Loyal Opposition KB-write approval-packet pathway clause present."""
    rule = (PROJECT_ROOT / ".claude" / "rules" / "loyal-opposition.md").read_text(encoding="utf-8")
    assert "Loyal Opposition KB-Write Approval-Packet Pathway" in rule
    assert "FINDING-P1-007" in rule
    assert "formal-artifact-approvals" in rule


def test_change_d_parked_draft_pattern_documented() -> None:
    """Change D — parked-draft semantics documented in file-bridge-protocol.md."""
    rule = (PROJECT_ROOT / ".claude" / "rules" / "file-bridge-protocol.md").read_text(encoding="utf-8")
    assert "## Parked-Draft Pattern" in rule
    assert "ERR_NO_INDEX_ENTRY" in rule
    assert "FINDING-P4-001" in rule


def test_change_e_canonical_terminology_dual_repo_listing() -> None:
    """Change E — Agent Red entry now lists both canonical and migration-target repos."""
    rule = (PROJECT_ROOT / ".claude" / "rules" / "canonical-terminology.md").read_text(encoding="utf-8")
    # Both repo URLs must be present
    assert "https://github.com/mike-remakerdigital/agent-red" in rule
    assert "https://github.com/Remaker-Digital/agent-red-customer-engagement" in rule
    assert "Migration target" in rule or "migration-target" in rule.lower()
    assert "DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE" in rule


def test_change_f_release_readiness_header_refreshed() -> None:
    """Change F — release-readiness.md header timestamp updated to S333."""
    text = (PROJECT_ROOT / "memory" / "release-readiness.md").read_text(encoding="utf-8")
    # Header is in the first ~10 lines
    head = "\n".join(text.splitlines()[:10])
    assert "Last updated: 2026-05-06 (S333)" in head, f"header not refreshed in:\n{head}"


def test_change_g_index_carries_auq_umbrella_naming_note() -> None:
    """Change G — bridge/INDEX.md carries the AUQ-stack umbrella-naming HTML comment."""
    text = (PROJECT_ROOT / "bridge" / "INDEX.md").read_text(encoding="utf-8")
    assert "Umbrella naming note" in text
    assert "gtkb-gov-askuserquestion-enforcement-stack-slice" in text
    assert "gtkb-gov-auq-enforcement-stack-slice" in text


def test_no_destructive_operations_in_bundle() -> None:
    """Bundle is purely additive (rule clauses + comment + header refresh) plus
    two specific file deletions (Change A). No bulk deletions, no history rewrite,
    no source-code logic changes, no live hook rewiring per the GO scope-control
    condition.

    This test is a guard: if any of these implementation-creep scenarios appear
    in the bundle's diff later, the test should be updated explicitly along
    with a follow-on bridge thread, not silently expanded.
    """
    # Sentinel paths that the bundle MUST NOT modify (per GO scope-control):
    bundle_should_not_modify = [
        PROJECT_ROOT / ".claude" / "settings.json",
        PROJECT_ROOT / ".codex" / "hooks.json",
        PROJECT_ROOT / "scripts" / "session_self_initialization.py",
    ]
    # We can't time-travel, but we can assert these files exist (sanity) and
    # were not deleted by the bundle.
    for path in bundle_should_not_modify:
        assert path.is_file(), f"bundle scope-control violation: missing {path}"
