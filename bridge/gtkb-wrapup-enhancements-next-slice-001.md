NEW

# Implementation Proposal - Wrap-Up Enhancements Next Slice (GTKB-WRAPUP-ENHANCEMENTS)

bridge_kind: implementation_proposal
Document: gtkb-wrapup-enhancements-next-slice
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH
Project: PROJECT-GTKB-SESSION-LIFECYCLE-UX
Work Item: GTKB-WRAPUP-ENHANCEMENTS

target_paths: ["scripts/wrap_up_consistency_scanner.py", "groundtruth-kb/src/groundtruth_kb/wrapup/consistency_check.py", "tests/scripts/test_wrapup_consistency_scanner.py"]

This NEW proposal advances `GTKB-WRAPUP-ENHANCEMENTS` to the next slice. Slice 1 Stage 1 VERIFIED at S310 lands the synthesis scanner; this proposal lands S2 (consistency scanner): identifies cross-artifact contradictions while session context is fresh.

## Claim

Build a consistency scanner that compares this-session's bridge proposals + DELIB inserts + work_item mutations + memory file changes against the canonical MemBase state, flagging contradictions: e.g., DELIB content disagreeing with cited spec text; bridge proposal target_paths mismatching actual files modified; memory/*.md state recording WI status differently from MemBase.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` - lifecycle engagement spec.
- `GOV-SESSION-SELF-INITIALIZATION-001` - companion startup spec.
- `GOV-08` - KB is truth; consistency checks enforce.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-SESSION-LIFECYCLE-UX authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient. WI description specifies the 5-scanner suite (S1 synthesis = Stage 1 VERIFIED; S2 consistency = this proposal).

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI, single sub-slice (S2 only); member of PROJECT-GTKB-SESSION-LIFECYCLE-UX per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (scanner) + IP-2 (output) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Consistency scanner module

`groundtruth-kb/src/groundtruth_kb/wrapup/consistency_check.py`:

Four check lenses:
1. **Spec-DELIB consistency**: For DELIB inserted this session, check that referenced spec IDs match the DELIB's claimed status.
2. **Bridge target_paths vs actual changes**: For bridge proposals filed this session, check that `target_paths` covers the files actually edited (via git status / diff).
3. **WI status MemBase vs memory**: For WIs touched this session, check that memory/*.md references match MemBase status.
4. **Cross-DELIB references**: For DELIBs that cite other DELIBs, check referenced DELIBs exist + are not retired.

### IP-2: CLI surface

`scripts/wrap_up_consistency_scanner.py`: CLI wrapper. Reads session-id from env or arg; emits markdown report + JSON.

### IP-3: Tests

Tests verify each lens with fixture data.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Spec-DELIB consistency: aligned passes | `test_spec_delib_aligned` |
| Spec-DELIB consistency: drift flagged | `test_spec_delib_drift_flagged` |
| Bridge target_paths gap detected | `test_target_paths_vs_actual_diff` |
| WI status mismatch flagged | `test_wi_status_mismatch_flagged` |
| Cross-DELIB broken ref detected | `test_broken_delib_reference_flagged` |
| Output schema stable | `test_output_schema` |

Run: `python -m pytest tests/scripts/test_wrapup_consistency_scanner.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 6 tests PASS.
- Both preflights PASS.
- Subsequent scanners (S3 close-in-flight, S4 next-session-anticipation, S5 hygiene-candidate) tracked for follow-on slices.

## Risks / Rollback

- Risk: heuristics for memory/*.md vs MemBase comparison may over-flag intentional divergence. Mitigation: severity is informational; report-only.
- Rollback: remove module + CLI.

## Recommended Commit Type

`feat` - new wrap-up scanner. ~120 LOC + tests.
