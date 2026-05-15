NEW

# Implementation Proposal - Isolation Program Closeout + Backstop (GTKB-ISOLATION-019)

bridge_kind: implementation_proposal
Document: gtkb-isolation-019-program-closeout
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH
Project: PROJECT-GTKB-ISOLATION-CLOSEOUT
Work Item: GTKB-ISOLATION-019

target_paths: ["docs/gtkb-isolation-program-closeout-report.md", "scripts/isolation_program_backstop.py", "tests/scripts/test_isolation_program_backstop.py"]

This NEW proposal closes the GT-KB isolation program with a final verification report + a backstop check that prevents inadvertent isolation regressions. Final phase of a long-running multi-slice program.

## Claim

Two parts: (1) a closeout report enumerating each isolation Phase / Slice outcome, with VERIFIED bridge thread citations; (2) a backstop script that runs as part of release-candidate gate to verify no path under `applications/` accidentally appears in canonical GT-KB platform files.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - isolation contract.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - lifecycle independence motivation.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release-readiness contract (backstop integration).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - foundational decision.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-ISOLATION-CLOSEOUT including this WI.

## Requirement Sufficiency

Existing requirements sufficient.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-ISOLATION-CLOSEOUT per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. Review-packet inventory: IP-1 (closeout report) + IP-2 (backstop script) + IP-3 (release-gate integration) + IP-4 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Program closeout report

`docs/gtkb-isolation-program-closeout-report.md`:
- Phase-by-phase enumeration (Phase 0..7).
- For each Phase: outcome, VERIFIED bridge thread, retrospective notes.
- Net outcome: lifecycle independence achieved; adopter packaging tested (per WI-3017); root enforcement live (per WI-3015).

Depends on WI-3015 + WI-3017 reaching VERIFIED. This proposal can be filed in parallel but the report's content gets finalized after siblings VERIFY.

### IP-2: Backstop script

`scripts/isolation_program_backstop.py`:
1. Scan canonical GT-KB platform files for paths matching `applications/<name>/` outside of explicitly-authorized cross-scope references.
2. Report violations as JSON.
3. Exit non-zero if any unauthorized references exist.

### IP-3: Release-gate integration

In `scripts/release_candidate_gate.py`, add a check that runs the backstop. Adds isolation backstop as a release-readiness criterion.

### IP-4: Tests

Tests verify: backstop finds intentional references in test fixtures; backstop exits 0 on a clean tree; release-gate integration calls the backstop.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Backstop detects unauthorized applications/ ref | `test_backstop_detects_unauthorized_ref` |
| Backstop allows authorized cross-scope ref | `test_backstop_allows_authorized_ref` |
| Backstop exit code on clean tree | `test_backstop_clean_tree_exit_zero` |
| Release-gate calls backstop | `test_release_gate_invokes_backstop` |
| Closeout report references each phase | manual: inspect report structure |
| Sibling WI dependency documented | manual: report references WI-3015 + WI-3017 VERIFIED state |

Run: `python -m pytest tests/scripts/test_isolation_program_backstop.py -v`.

## Acceptance Criteria

- IP-1 report drafted (final content after sibling WIs VERIFY).
- IP-2, IP-3 landed; 4 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: closeout report citations may have stale VERIFIED bridge IDs if sibling work changes. Mitigation: cite by bridge slug + version, not by absolute version-number; report regenerated at sibling-VERIFIED time.
- Rollback: remove backstop registration from release-gate; report stays as historical doc.

## Recommended Commit Type

`feat` - new backstop + program closeout report. ~80 LOC + report markdown.
