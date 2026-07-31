"""Obsolete bridge aggregate classification contract tests.

Maps to DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001 STRIP completeness,
KEEP guard machinery, and QUARANTINE audit preservation per
the docs strip bridge thread and the WI-4800 in-root memory tranche.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOCS_STRIP_TARGETS = [
    "groundtruth-kb/docs/architecture/product-split.md",
    "groundtruth-kb/docs/architecture/isolation.md",
    "groundtruth-kb/docs/start-here.md",
    "groundtruth-kb/docs/day-in-the-life.md",
    "groundtruth-kb/docs/tutorials/dual-agent-setup.md",
    "groundtruth-kb/docs/tutorials/bridge-smart-poller.md",
    "groundtruth-kb/docs/tutorials/bridge-os-scheduler.md",
    "groundtruth-kb/docs/method/12-file-bridge-automation.md",
    "groundtruth-kb/docs/reference/cli.md",
    "groundtruth-kb/docs/reference/canonical-terminology-detail.md",
]

GUARD_FILES = [
    "scripts/protected_mutation_guard.py",
    ".claude/hooks/bridge-compliance-gate.py",
    ".claude/hooks/lo-file-safety-gate.py",
    "scripts/check_skill_health.py",
]

QUARANTINE_REPORTS = [
    "groundtruth-kb/docs/reports/non-disruptive-upgrade-audit.md",
    "groundtruth-kb/docs/reports/agent-red-classification.md",
]

MEMORY_STRIP_TARGETS = [
    "memory/antigravity-integration-status.md",
    "memory/fable-campaign-monitor-envelope.md",
    "memory/fable-investigation-campaign.md",
    "memory/project_role_status_orthogonality_dispatch.md",
    "memory/feedback/feedback_interactive_poller_monitor.md",
    "memory/feedback/feedback_read_index_comments_before_executing_go.md",
    "memory/feedback/feedback_session_start_orient_block.md",
    "memory/feedback/feedback_worktree_drift_pattern.md",
]

MEMORY_QUARANTINE_TARGETS = [
    "memory/CLAUDE_ARCHIVE.md",
    "memory/pending-owner-decisions.md",
    "memory/archive/pending-owner-decisions-202605.md",
]

WI5067_TEST_STRIP_TARGETS = [
    "platform_tests/scripts/test_dispatcher_runtime.py",
    "platform_tests/scripts/test_gtkb_dispatcher_daemon.py",
    "platform_tests/scripts/test_bridge_dispatch_config.py",
    "platform_tests/scripts/test_scan_bridge.py",
    "platform_tests/scripts/test_show_thread_bridge.py",
    "groundtruth-kb/tests/adopter/test_registry_entry_present_for_every_scaffolded_file.py",
]

OBSOLETE_FILENAME = "".join(chr(code) for code in (73, 78, 68, 69, 88)) + ".md"
OBSOLETE_TOKEN = "bridge/" + OBSOLETE_FILENAME


def _guard_references_retired_aggregate(text: str) -> bool:
    """K2 guard machinery may cite the retired path or name constant."""
    if OBSOLETE_TOKEN in text:
        return True
    return "_RETIRED_BRIDGE_AGGREGATE_NAME" in text and OBSOLETE_FILENAME in text


def test_docs_strip_completeness() -> None:
    """STRIP set: zero obsolete aggregate tokens in S1 docs targets."""
    for relative in DOCS_STRIP_TARGETS:
        text = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert OBSOLETE_TOKEN not in text, f"{relative} still contains {OBSOLETE_TOKEN!r}"


def test_keep_guard_machinery_intact() -> None:
    """KEEP set: guard machinery still detects the retired aggregate."""
    for relative in GUARD_FILES:
        path = PROJECT_ROOT / relative
        assert path.is_file(), f"missing guard file: {relative}"
        text = path.read_text(encoding="utf-8")
        assert _guard_references_retired_aggregate(text), f"{relative} no longer detects the retired bridge aggregate"


def test_quarantine_reports_untouched() -> None:
    """QUARANTINE Q1: dated audit reports retain their historical references."""
    for relative in QUARANTINE_REPORTS:
        path = PROJECT_ROOT / relative
        assert path.is_file(), f"missing quarantine report: {relative}"
        text = path.read_text(encoding="utf-8")
        assert OBSOLETE_TOKEN in text, f"{relative} lost quarantined {OBSOLETE_TOKEN!r}"


def test_s4_memory_strip_completeness() -> None:
    """WI-4800 S4 STRIP: editable in-root memory no longer teaches the retired aggregate."""
    for relative in MEMORY_STRIP_TARGETS:
        path = PROJECT_ROOT / relative
        assert path.is_file(), f"missing S4 memory target: {relative}"
        text = path.read_text(encoding="utf-8")
        assert OBSOLETE_TOKEN not in text, f"{relative} still contains {OBSOLETE_TOKEN!r}"
        assert OBSOLETE_FILENAME not in text, f"{relative} still contains {OBSOLETE_FILENAME!r}"


def test_s4_memory_quarantine_scope_is_explicit() -> None:
    """WI-4800 S4 QUARANTINE: historical memory records are outside STRIP targets."""
    overlap = set(MEMORY_STRIP_TARGETS).intersection(MEMORY_QUARANTINE_TARGETS)
    assert overlap == set()
    for relative in MEMORY_QUARANTINE_TARGETS:
        path = PROJECT_ROOT / relative
        assert path.is_file(), f"missing quarantined memory record: {relative}"


def test_wi5067_active_test_strip_completeness() -> None:
    """WI-5067 STRIP: active dispatcher/bridge/registry tests no longer materialize
    or read the retired bridge aggregate as live state (numbered-file discovery only)."""
    for relative in WI5067_TEST_STRIP_TARGETS:
        path = PROJECT_ROOT / relative
        assert path.is_file(), f"missing WI-5067 STRIP target: {relative}"
        text = path.read_text(encoding="utf-8")
        assert OBSOLETE_FILENAME not in text, f"{relative} still contains {OBSOLETE_FILENAME!r}"
