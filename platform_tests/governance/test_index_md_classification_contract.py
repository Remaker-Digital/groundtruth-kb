"""S1 docs-surface contract tests for gtkb-index-md-strip-docs (WI-4797).

Maps to DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001 STRIP completeness,
KEEP guard machinery, and QUARANTINE audit preservation per
bridge/gtkb-index-md-strip-docs-001.md.
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

OBSOLETE_TOKEN = "bridge/INDEX.md"


def _guard_references_retired_aggregate(text: str) -> bool:
    """K2 guard machinery may cite the literal path or the retired-name constant."""
    if OBSOLETE_TOKEN in text:
        return True
    return "_RETIRED_BRIDGE_AGGREGATE_NAME" in text and "INDEX.md" in text


def test_docs_strip_completeness() -> None:
    """STRIP set: zero obsolete bridge/INDEX.md tokens in S1 docs targets."""
    for relative in DOCS_STRIP_TARGETS:
        text = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert OBSOLETE_TOKEN not in text, f"{relative} still contains {OBSOLETE_TOKEN!r}"


def test_keep_guard_machinery_intact() -> None:
    """KEEP set: guard machinery still references bridge/INDEX.md for detection."""
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
