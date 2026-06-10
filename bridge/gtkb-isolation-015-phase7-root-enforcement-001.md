NEW

# Implementation Proposal - Isolation Phase 7 Work-Subject/Root Enforcement (GTKB-ISOLATION-015)

bridge_kind: prime_proposal
Document: gtkb-isolation-015-phase7-root-enforcement
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH
Project: PROJECT-GTKB-ISOLATION-CLOSEOUT
Work Item: GTKB-ISOLATION-015

target_paths: [".claude/hooks/work-subject-write-gate.py", ".claude/session/work-subject.json", "scripts/work_subject_enforce.py", "tests/scripts/test_work_subject_enforce.py"]

This NEW proposal completes Phase 7 of the GT-KB isolation program: full work-subject/root enforcement via PreToolUse Write hook. Currently `work-subject.json` is advisory; this WI promotes it to mechanically enforced.

## Claim

Add a PreToolUse Write/Edit hook that consults `.claude/session/work-subject.json`, identifies the declared work subject (`gtkb_infrastructure` or `application`), and blocks Writes to paths that violate the declared scope. For `gtkb_infrastructure`: in-root paths only (per `.claude/rules/project-root-boundary.md`). For `application`: paths under `applications/<name>/` only.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - source isolation contract.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - lifecycle independence motivation.
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` - three-mode declaration as runtime invariant.
- `DELIB-0876` - durable session work subject (adjacent).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization.
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` - three-mode scope contract.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-ISOLATION-CLOSEOUT authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient. WI description + cited DELIBs specify the enforcement scope.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-ISOLATION-CLOSEOUT per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. Review-packet inventory: IP-1 (hook) + IP-2 (registration) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: work-subject-write-gate hook

In `.claude/hooks/work-subject-write-gate.py`:
1. Read `.claude/session/work-subject.json`; resolve declared subject + scope mode.
2. For Write/Edit/MultiEdit target paths:
   - `gtkb_infrastructure` scope: require path is in-root under `E:\GT-KB` AND not under `applications/<name>/` (unless that's an authorized cross-scope mutation).
   - `application` scope: require path under `applications/<app-name>/`.
   - `gtkb+application` exceptional scope: allow both; surface advisory comment.
3. Block with rule-cited reason when violated.

### IP-2: Hook registration + Codex parity

Register in `.claude/settings.json` PreToolUse for Write/Edit/MultiEdit. Mirror at `.codex/gtkb-hooks/work-subject-write-gate.py` + `.codex/hooks.json`.

### IP-3: Tests

Test fixtures cover each scope mode + path classification.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| gtkb_infrastructure: in-root write allowed | `test_gtkb_in_root_write_allowed` |
| gtkb_infrastructure: applications/* write blocked | `test_gtkb_apps_write_blocked` |
| application: applications/<name>/ write allowed | `test_application_in_app_write_allowed` |
| application: gtkb-only path blocked | `test_application_gtkb_path_blocked` |
| gtkb+application: both allowed with advisory | `test_dual_scope_both_allowed` |
| Block reason cites ADR | `test_block_reason_cites_isolation_adr` |
| Codex mirror exists | `test_codex_mirror_exists` |

Run: `python -m pytest tests/scripts/test_work_subject_enforce.py -v`.

## Acceptance Criteria

- IP-1, IP-2 landed; 7 tests PASS.
- Both preflights PASS.
- Existing work-subject.json advisory references remain compatible.

## Risks / Rollback

- Risk: legitimate cross-scope writes (e.g., copying templates from gt-kb to applications) get blocked. Mitigation: `gtkb+application` mode covers this; explicit AUQ for permanent cases.
- Rollback: remove hook registration.

## Recommended Commit Type

`feat` - new isolation enforcement gate. ~120 LOC + tests.
