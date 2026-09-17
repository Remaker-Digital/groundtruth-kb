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

WI-4279 (adopter-facing follow-on) extends this lock to the scaffold source
`groundtruth-kb/templates/rules/canonical-terminology.md` and both committed
golden fixtures, so the phantom cannot re-enter scaffolded adopter projects.
Owner decision (2026-06-03 AUQ): mirror the live fix in the scaffold template.
Authority: `bridge/gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-002.md` (GO).
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
# The authored carriers: every neutral baseline rule (the harness projections are generated from them) and every
# scaffold rule template an initialized application inherits. The phantom must be absent from all of them.
_BASELINE_RULES = tuple(sorted((_ROOT / ".harness-baseline-configuration" / "rules").glob("*.md")))
_SCAFFOLD_FILES = tuple(sorted((_ROOT / "groundtruth-kb" / "templates" / "rules").glob("*.md")))
_PHANTOM = "GOV-CHAT-DERIVED-SPEC-APPROVAL-001"
_REPLACEMENT = "GOV-SPEC-CAPTURE-TRANSPARENCY-001"
# The live record's duty (record owner-stated requirements directly, make the canonical change reviewable, no
# per-artifact permission round) is stated in the operating model's authority section and the deliberation protocol;
# those carriers cite it. The scaffold copy of the deliberation protocol carries the citation into applications.
_RULE_FILES = (
    _ROOT / ".harness-baseline-configuration" / "rules" / "operating-model.md",
    _ROOT / ".harness-baseline-configuration" / "rules" / "deliberation-protocol.md",
)
_CITING_SCAFFOLD_FILES = (_ROOT / "groundtruth-kb" / "templates" / "rules" / "deliberation-protocol.md",)


def _read(path: Path) -> str:
    assert path.is_file(), f"required rule file missing: {path}"
    return path.read_text(encoding="utf-8")


def test_phantom_absent_from_rule_files() -> None:
    assert _BASELINE_RULES, "no baseline rules found"
    offenders = [str(p) for p in _BASELINE_RULES if _PHANTOM in _read(p)]
    assert not offenders, f"phantom {_PHANTOM} still cited in: {offenders}"


def test_replacement_present_in_rule_files() -> None:
    missing = [str(p) for p in _RULE_FILES if _REPLACEMENT not in _read(p)]
    assert not missing, f"replacement {_REPLACEMENT} not found in: {missing}"


def test_phantom_absent_from_scaffold_files() -> None:
    assert _SCAFFOLD_FILES, "no scaffold rule templates found"
    offenders = [str(p) for p in _SCAFFOLD_FILES if _PHANTOM in _read(p)]
    assert not offenders, f"phantom {_PHANTOM} still cited in scaffold: {offenders}"


def test_replacement_present_in_scaffold_files() -> None:
    missing = [str(p) for p in _CITING_SCAFFOLD_FILES if _REPLACEMENT not in _read(p)]
    assert not missing, f"replacement {_REPLACEMENT} not found in scaffold: {missing}"
