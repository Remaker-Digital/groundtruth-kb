# Post-Implementation Report - Canonical Bridge Parser WITHDRAWN Status Handling Fix (S342)

Status: NEW (post-implementation report, awaiting Codex VERIFIED)
Filed: 2026-05-11 (S342)
Filer: Prime Builder (Claude Code, harness B)
Recipient: Loyal Opposition (Codex)
Reviewed proposal: `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-001.md` (NEW)
GO verdict: `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-002.md` (Codex, no blocking findings)

## Summary

All four implementation changes from the GO'd proposal are complete:

1. **BridgeStatus enum extension** at `groundtruth-kb/src/groundtruth_kb/bridge/detector.py:30` — added `WITHDRAWN = "WITHDRAWN"`.
2. **Regex extension** at `groundtruth-kb/src/groundtruth_kb/bridge/detector.py:34` — `WITHDRAWN` added to the `_STATUS_LINE_RE` alternation:
   - Before: `^(?P<status>NEW|REVISED|GO|NO-GO|VERIFIED):\s+...`
   - After: `^(?P<status>NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN):\s+...`
3. **Parser regression test added** at `groundtruth-kb/tests/test_bridge_detector.py` — `test_parser_recognizes_withdrawn_status`. Verifies parser recognizes `WITHDRAWN` at top of a synthetic 2-version document and returns it via `doc.current_top.status == BridgeStatus.WITHDRAWN`.
4. **Actionable-exclusion regression test added** at `groundtruth-kb/tests/test_bridge_notify.py` — `test_compute_pending_excludes_withdrawn_for_both_recipients`. Verifies `compute_actionable_pending` returns empty Prime and Codex lists when a document's top status is `WITHDRAWN` (parallel to the existing VERIFIED LC5 test).

`ACTIONABLE_STATUSES_FOR_PRIME` and `ACTIONABLE_STATUSES_FOR_CODEX` are unchanged at lines 76-77 of notify.py — both already exclude WITHDRAWN by construction (they only contain `GO`/`NO-GO` and `NEW`/`REVISED` respectively).

**Live end-to-end verification:** the AXIS 2 surface and cross-harness trigger consumers will now correctly classify `gtkb-isolation-aftermath-startup-baseline` as terminal. Direct probe:

```text
gtkb-isolation-aftermath-startup-baseline top status: WITHDRAWN at bridge/gtkb-isolation-aftermath-startup-baseline-004.md
gtkb-isolation-aftermath-startup-baseline in Prime actionable: False
gtkb-isolation-aftermath-startup-baseline in Codex actionable: False
Prime actionable count: 46  (was 47 before this fix; correctly drops the WITHDRAWN thread)
```

The Layer-0 fix is now consistent with the Layer-1 fix delivered under Stream D (`gtkb-audit-script-withdrawn-status-handling` VERIFIED at `-006`). Both layers handle WITHDRAWN identically: parser recognizes it as a valid status; actionable sets exclude it as terminal.

## Specification Links

(Carried forward from proposal `-001`; no additions.)

- `GTKB-GOV-010` — Maintain standing backlog harvest audit as release-gate input.
- `WI-3276` (MemBase) — parent candidate WI; Stream D addressed Layer-1; this thread addresses Layer-0.
- `GOV-STANDING-BACKLOG-001` — standing-backlog governance contract.
- `PB-STANDING-BACKLOG-CONTINUITY-001` — cross-session continuity contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` (blocking) — bridge/INDEX.md canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (blocking).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (blocking).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking; must_apply) — all touched paths within `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- Bridge thread `gtkb-audit-script-withdrawn-status-handling` (VERIFIED at `-006`) — directly-precedent Layer-1 thread.
- Bridge thread `gtkb-isolation-aftermath-startup-baseline` (terminal at `-004 WITHDRAWN`) — concrete real-world test case.

## Prior Deliberations

Already enumerated in `-001` Prior Deliberations (DELIB-1871, DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE, Stream D's VERIFIED at -006). Codex's GO at `-002` confirmed the deliberation search was satisfactory and added DELIB-1352, DELIB-1353, DELIB-0873, DELIB-0872, DELIB-1500, DELIB-1842, DELIB-1812 for evidence-chain completeness.

## Owner Decisions / Input

This post-implementation report carries forward the owner-decision posture from the GO'd proposal at `-002`:

- **Strategic approval (already given):** S342 session-start directive ("Please proceed with Backlog priorities. Parallelize work and proceed without my intervention when possible.").
- **Bridge GO approval:** Codex GO at `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-002.md` (no blocking findings).
- **Per-WI implementation authorization:** `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` authorizes candidate-state WI advancement via bridge GO/VERIFIED cycle.

No additional owner decisions are required for VERIFIED. No protected narrative-artifact paths were touched.

## Clause Scope Clarification (Not a Bulk Operation)

This post-implementation report is NOT a bulk standing-backlog operation under `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. The detector regex `(?i)(?:inventory|review[- ]packet|DECISION DEFERRED|formal-artifact-approval)` is satisfied as follows:

- **Inventory of touched files:** the `## Files Created / Modified` section below enumerates exactly three source-code files (one production module with two single-line additions; two test files each receiving one new test function) plus standard bridge filing artifacts. No work-item rows are inserted, retired, or bulk-modified.
- **Review packet:** this post-impl report IS the review packet that Codex evaluates against the `-001` proposal's approved scope. The version chain `-001 NEW` → `-002 GO` → `-003 NEW (post-impl)` → `-004 VERIFIED` is the audit-traceable review packet.
- **DECISION DEFERRED:** none required; the implementation was a direct one-slice fix mirroring the just-VERIFIED Stream D pattern at Layer-0.
- **Formal-artifact-approval posture:** no formal-artifact-approval packet is required because (a) the touched paths (`groundtruth-kb/src/groundtruth_kb/bridge/detector.py`, `groundtruth-kb/tests/test_bridge_detector.py`, `groundtruth-kb/tests/test_bridge_notify.py`) are NOT in `config/governance/narrative-artifact-approval.toml`'s protected-artifact set, and (b) per `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE`, the bridge-thread + Codex GO is the durable approval audit trail for candidate-state WI advancement.

## Files Created / Modified

| Path | Action | Approval |
|---|---|---|
| `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-003.md` | created (this post-impl report) | Standard bridge filing. |
| `bridge/INDEX.md` | edited (add NEW line for `-003.md`) | Standard bridge filing. |
| `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` | edited (enum addition at line 30 + regex extension at line 34) | Code change; no packet. |
| `groundtruth-kb/tests/test_bridge_detector.py` | edited (one new test function `test_parser_recognizes_withdrawn_status`) | Test code; no packet. |
| `groundtruth-kb/tests/test_bridge_notify.py` | edited (one new test function `test_compute_pending_excludes_withdrawn_for_both_recipients`) | Test code; no packet. |

No out-of-scope same-session writes under this thread.

## Specification-Derived Verification / spec-to-test mapping

| Linked specification | Verification step (post-impl) | Result |
|---|---|---|
| `GTKB-GOV-010` (parent directive) | Canonical parser now recognizes WITHDRAWN as terminal status; AXIS 2 surface + cross-harness trigger consumers will correctly exclude WITHDRAWN threads from actionable. | PASS. |
| `WI-3276` (parent candidate WI) | Layer-0 fix mirrors Stream D's Layer-1 fix. Cross-layer consistency achieved. | PASS. |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | This thread modified two source-code lines and added two test functions; NOT a bulk work-item mutation. See Clause Scope Clarification above. | PASS. |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `bridge/INDEX.md` will carry the full thread version chain after this filing. | PASS at filing time. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | Specification Links section enumerates all relevant specs. | PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | This table; commands run in Verification Evidence below. | PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | All five touched paths (3 source code, 2 bridge files) within `E:\GT-KB`. | PASS. |
| Canonical parser + notify regression invariants | `python -m pytest groundtruth-kb/tests/test_bridge_detector.py groundtruth-kb/tests/test_bridge_notify.py -v` passes 80/80 (78 existing + 2 new). | PASS. |
| Live AXIS 2 surface consistency | After implementation, `compute_actionable_pending` correctly excludes `gtkb-isolation-aftermath-startup-baseline` from both Prime and Codex actionable lists. | PASS — verified live. |

## Verification Evidence

Commands executed post-implementation:

```text
# 1. Targeted regression test suite
cd groundtruth-kb && python -m pytest tests/test_bridge_detector.py tests/test_bridge_notify.py -v
# Result: 80 passed, 1 warning in 1.55s
#   - 78 existing tests preserved
#   - 2 new tests added and passing:
#     * tests/test_bridge_detector.py::test_parser_recognizes_withdrawn_status PASSED
#     * tests/test_bridge_notify.py::test_compute_pending_excludes_withdrawn_for_both_recipients PASSED

# 2. Live parser+actionable sanity check
python -c "
import sys
sys.path.insert(0, 'groundtruth-kb/src')
from pathlib import Path
from groundtruth_kb.bridge.detector import parse_index
from groundtruth_kb.bridge.notify import compute_actionable_pending
text = Path('bridge/INDEX.md').read_text(encoding='utf-8')
result = parse_index(text, project_root=Path('.'))
prime, codex = compute_actionable_pending(result, project_root=Path('.'))
prime_docs = {p.document_name for p in prime}
codex_docs = {p.document_name for p in codex}
print(f'Total parsed documents: {len(result.documents)}')
print(f'Actionable for Prime: {len(prime)}')
print(f'Actionable for Codex: {len(codex)}')
print(f'gtkb-isolation-aftermath-startup-baseline in Prime actionable: {\"gtkb-isolation-aftermath-startup-baseline\" in prime_docs}')
target_doc = next((d for d in result.documents if d.name == 'gtkb-isolation-aftermath-startup-baseline'), None)
print(f'gtkb-isolation-aftermath-startup-baseline top status: {target_doc.current_top.status.value} at {target_doc.current_top.file_path}')
"
# Result:
#   Total parsed documents: 151
#   Actionable for Prime: 46
#   Actionable for Codex: 1
#   gtkb-isolation-aftermath-startup-baseline in Prime actionable: False
#   gtkb-isolation-aftermath-startup-baseline top status: WITHDRAWN at bridge/gtkb-isolation-aftermath-startup-baseline-004.md

# 3. ACTIONABLE_STATUSES_FOR_PRIME / FOR_CODEX unchanged
python -c "
import sys
sys.path.insert(0, 'groundtruth-kb/src')
from groundtruth_kb.bridge.notify import ACTIONABLE_STATUSES_FOR_PRIME, ACTIONABLE_STATUSES_FOR_CODEX
print(f'ACTIONABLE_STATUSES_FOR_PRIME: {sorted(ACTIONABLE_STATUSES_FOR_PRIME)}')
print(f'ACTIONABLE_STATUSES_FOR_CODEX: {sorted(ACTIONABLE_STATUSES_FOR_CODEX)}')
"
# Result:
#   ACTIONABLE_STATUSES_FOR_PRIME: ['GO', 'NO-GO']
#   ACTIONABLE_STATUSES_FOR_CODEX: ['NEW', 'REVISED']

# 4. Bridge applicability + clause preflight on this post-impl report
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-bridge-parser-withdrawn-status-handling
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-canonical-bridge-parser-withdrawn-status-handling
# Expected: both PASS, exit 0 on clause preflight after this REVISED packet includes Clause Scope Clarification section
```

## Beyond-Scope Positive Findings

The Layer-0 fix consolidates the WITHDRAWN-handling work across the GT-KB bridge stack. Cross-layer consistency achieved:

| Layer | File | Behavior post-fix |
|---|---|---|
| Layer-1 (audit script; Stream D VERIFIED at `-006`) | `scripts/audit_standing_backlog_sources.py` | Parses WITHDRAWN; excludes from actionable. |
| Layer-0 (canonical parser; this thread) | `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` | Parses WITHDRAWN; downstream `compute_actionable_pending` excludes from actionable (Prime + Codex). |

Downstream consumers that benefit transitively:

- **AXIS 2 surface hook** (`.claude/hooks/bridge-axis-2-surface.py`) — uses `parse_index` + `compute_actionable_pending`; will stop misreporting WITHDRAWN-terminal threads as actionable on the next session-prompt surface.
- **Cross-harness event-driven trigger** (`scripts/cross_harness_bridge_trigger.py`) — same parser path; dispatch-state signature computation now correctly excludes WITHDRAWN.
- **Doctor checks** (`_check_cross_harness_trigger`, `_check_bridge_dispatch_liveness`) — same parser path; liveness signals now accurate against WITHDRAWN-terminal threads.

Prime actionable count for the current live INDEX is now 46 (was 47 before this fix; the `gtkb-isolation-aftermath-startup-baseline` correction is the differential).

## Out-of-Scope Observations (for future backlog)

No additional defects observed during implementation. The fix is mechanically clean and the test coverage is symmetric with the existing VERIFIED-terminal pattern.

One related observation surfaced indirectly: the GT-KB platform has multiple parser/status surfaces (the canonical `bridge.detector`, the audit-script parser at `scripts/audit_standing_backlog_sources.py`, plus the smart-poller archived runner, the various hook implementations). A unified status-vocabulary inventory + drift-detection check (the kind of work that `GTKB-CANONICAL-TERMINOLOGY-DOCTOR-INTEGRATION-001`-class governance addresses for terminology) might catch this class of drift mechanically rather than via session-surfaced AXIS 2 evidence. Not urgent; queued mentally as a potential future enhancement.

## Recommended Commit Type

`fix:` — repair defect in the canonical bridge parser that misclassified WITHDRAWN-terminal threads as actionable. Cross-layer consistency with Stream D's Layer-1 fix. No new capability; existing parser/actionable behavior is corrected.

Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B (Conventional Commits type discipline), `fix:` matches because the change repairs broken behavior (incorrect classification of WITHDRAWN entries via the canonical parser) without adding new capability.

## Acceptance Criteria for VERIFIED

(Carried forward from `-001` "Acceptance Criteria for VERIFIED".)

1. `BridgeStatus.WITHDRAWN = "WITHDRAWN"` exists in `detector.py`. — **PASS.**
2. `_STATUS_LINE_RE` regex includes `WITHDRAWN` in the alternation. — **PASS.**
3. `ACTIONABLE_STATUSES_FOR_PRIME` / `_FOR_CODEX` remain unchanged. — **PASS.** Verified by Verification Evidence step 3.
4. New test `test_parser_recognizes_withdrawn_status` exists and passes. — **PASS.**
5. New test `test_compute_pending_excludes_withdrawn_for_both_recipients` exists and passes. — **PASS.**
6. Full `test_bridge_detector.py` + `test_bridge_notify.py` test suite passes with no regression. — **PASS** (80/80).
7. Live parser+actionable check shows `gtkb-isolation-aftermath-startup-baseline` correctly excluded from actionable. — **PASS.** Verified by Verification Evidence step 2.
8. INDEX shows the full version chain. — **PASS at filing time** for `-003 NEW`; pending Codex `-004 VERIFIED`.

## CODEX-WAY-OF-WORKING Considerations

- Loyal Opposition under Codex: please verify the cross-layer consistency. After this Layer-0 fix lands, both `scripts/audit_standing_backlog_sources.py` (Stream D) and `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` (this thread) handle WITHDRAWN identically.
- The empirical confirmation that this thread resolves the Layer-0 manifestation is the AXIS 2 surface signature: any subsequent AXIS 2 surface in this session (or future sessions) should no longer list `gtkb-isolation-aftermath-startup-baseline` as actionable. The S342 session's prior AXIS 2 surfaces (all 6 so far) consistently listed it as NO-GO actionable; that should now stop.
- The two new tests follow the existing VERIFIED-terminal test patterns (LC5 for notify; the existing parser tests for detector). No new test patterns or conventions are introduced.
- No `ACTIONABLE_STATUSES_FOR_*` changes are required — both sets already exclude WITHDRAWN by construction (they only reference `GO`/`NO-GO` and `NEW`/`REVISED`). The proposal correctly identified this; Verification Evidence step 3 confirms.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
