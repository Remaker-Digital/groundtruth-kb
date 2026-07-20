# Transient driver: capture owner decision to prioritize wi5158 before WI-5105-class finalizations.
import sys
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB

# Import the helper by path
helper_dir = ROOT / ".claude" / "skills" / "decision-capture" / "helpers"
sys.path.insert(0, str(helper_dir))
from record_decision import record_decision  # noqa: E402

DELIB_ID = "DELIB-20260710-PRIORITIZE-WI5158-BEFORE-WI5105-FINALIZATIONS"

TITLE = "Owner Decision - Prioritize wi5158 finalization-mechanism fix before WI-5105-class finalizations"

SUMMARY = (
    "Owner directs the LO auto-process loop to hold the pending by-reference / "
    "commingled-worktree VERIFIED finalizations (wi5174, wi5171) and prioritize "
    "implementing + verifying wi5158 (unified `gt commit scoped` finalization) "
    "first; the loop keeps verifying report substance and reporting status each "
    "tick but does not force per-report finalizations until the wi5158 mechanism "
    "lands."
)

CONTENT = """# Owner Decision - Prioritize wi5158 finalization-mechanism fix

## Context

The 20-minute Loyal Opposition auto-process loop repeatedly surfaced GO'd
implementations that are complete but cannot reach terminal VERIFIED, because LO
finalization hits one of two walls:

- By-reference wall: the implementation was committed separately (WI-4841 at
  9fe6b2e7; wi5174 at edb35b78), so the finalize helper's
  `_report_has_by_reference_finalization_waiver` gate requires a By-Reference
  Finalization Waiver section the report lacks, and the include-coverage gate
  otherwise demands staging foreign-edited shared files.
- Commingled-worktree wall: the implementation is uncommitted alongside foreign
  changes (wi5171), requiring a scoped-commit finalization that cannot be safely
  hand-rolled by interactive LO.

This is the recurring WI-5105 class. The structural fix is wi5158 (governed
Git-lifecycle; unifies VERIFIED finalization onto `gt commit scoped`), which
received an LO design GO this session but is not yet implemented.

## Decision

Prioritize implementing and verifying wi5158 before forcing the accumulating
WI-5105-class finalizations. Hold the pending by-reference / commingled
finalizations (wi5174, wi5171). The LO loop keeps verifying report substance and
reporting status each tick, but does NOT force per-report VERIFIED finalizations
until the wi5158 mechanism lands and can finalize them cleanly.

## Options Considered

1. [SELECTED] Prioritize wi5158 fix first - hold pending finalizations; fix the
   mechanism once; then close the backlog cleanly in one mode.
2. Grant standing by-reference waiver - authorize by-reference/scoped
   finalization for the pending reports (multi-step per report: verify -> NO-GO
   route -> Prime REVISED with waiver section -> LO finalize).
3. Verify-only, no finalize - loop verifies + records substance but leaves all
   finalization for batch resolution.

## Linked Artifacts

- WI-5158 - structural finalization fix; LO design GO at
  bridge/gtkb-modernization-wi5158-git-binding-bootstrap-002.md.
- WI-5105 - recurring commingled-shared-finalization class.
- WI-4841 - by-reference finalization; NO-GO at
  bridge/gtkb-wi4841-hunk-scoped-finalization-waiver-004.md routing the
  owner-granted by-reference close.
- wi5174 - by-reference class; report at
  bridge/gtkb-wi5174-dispatch-workflow-report-003.md; impl committed at
  edb35b78.
- wi5171 - commingled class; report at
  bridge/gtkb-wi5171-document-authoritative-backlog-writer-007.md; impl
  uncommitted in the shared worktree.

## First Concrete Actions Authorized

1. Prime Builder (Codex) implements the GO'd wi5158 proposal and files a
   post-implementation report.
2. LO prioritizes verifying the wi5158 report when it arrives.
3. Once wi5158's unified finalization mechanism is verified, LO uses it to
   finalize the held WI-5105-class reports.
4. Until then, the LO loop verifies substance and reports status without forcing
   per-report finalizations.
"""

db = KnowledgeDB(str(ROOT / "groundtruth.db"))
row = record_decision(
    db,
    DELIB_ID,
    TITLE,
    SUMMARY,
    CONTENT,
    work_item_id="WI-5158",
    participants=["owner", "loyal-opposition/claude"],
)
print("RECORDED", row.get("id"), "version", row.get("version"))
