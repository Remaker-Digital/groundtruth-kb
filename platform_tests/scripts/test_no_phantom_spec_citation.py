# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Regression lock for WI-3506 phantom-spec-citation re-point.

PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS / WI-3506. Three live rule files cited the
phantom spec `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` (not present in MemBase). The
re-point replaced it with the live governing surface
`GOV-SPEC-CAPTURE-TRANSPARENCY-001`. This test pins the corrected state so the
phantom cannot silently re-appear in these rule files (a live instance of the
rule-vs-MemBase drift `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` governs).

Owner decision (2026-06-03 AUQ): fold into WI-3506; re-point all 3 rule files.
Authority: `bridge/gtkb-wi-3506-phantom-spec-citation-repoint-002.md` (GO).
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_RULE_FILES = (
    _ROOT / ".claude" / "rules" / "canonical-terminology.md",
    _ROOT / ".claude" / "rules" / "prime-builder-role.md",
    _ROOT / ".claude" / "rules" / "operating-model.md",
)
_PHANTOM = "GOV-CHAT-DERIVED-SPEC-APPROVAL-001"
_REPLACEMENT = "GOV-SPEC-CAPTURE-TRANSPARENCY-001"


def _read(path: Path) -> str:
    assert path.is_file(), f"required rule file missing: {path}"
    return path.read_text(encoding="utf-8")


def test_phantom_absent_from_rule_files() -> None:
    offenders = [str(p) for p in _RULE_FILES if _PHANTOM in _read(p)]
    assert not offenders, f"phantom {_PHANTOM} still cited in: {offenders}"


def test_replacement_present_in_rule_files() -> None:
    missing = [str(p) for p in _RULE_FILES if _REPLACEMENT not in _read(p)]
    assert not missing, f"replacement {_REPLACEMENT} not found in: {missing}"
