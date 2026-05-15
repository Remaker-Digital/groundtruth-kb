NEW

# Implementation Proposal - Zero-Knowledge Architecture Phase 4 Scoping (WORKLIST-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-LONGER-TERM)

bridge_kind: implementation_proposal
Document: gtkb-zero-knowledge-architecture-phase-4-scoping
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-SECURITY-PRIVACY-SECURITY-PRIVACY-BATCH-SPECS-LIGHT-INITIAL
Project: PROJECT-GTKB-SECURITY-PRIVACY
Work Item: WORKLIST-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-LONGER-TERM

target_paths: ["docs/zero-knowledge-architecture-phase-4-scoping.md", "groundtruth-kb/src/groundtruth_kb/security/zk_phase_4_planner.py"]

This NEW scoping proposal initializes Phase 4 of the Zero-Knowledge Architecture program. Per WI description: 4 specs (SPEC-1843/1844/1644/1840), 5 implementation phases, ~6-8 sessions. Prerequisite: POR Step 16 substantially complete. This proposal is scoping-only — implementation phases are follow-on slices.

## Claim

Two scoping deliverables: (1) a Phase 4 scoping document enumerating the 5 implementation phases + their dependencies on the 4 specs; (2) a planner module that can be invoked to verify prerequisites + sequence the implementation phases. Implementation work itself is deferred to follow-on bridges, each gated on prior-phase VERIFIED.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `SPEC-1843` - one of the 4 ZK specs (per WI description).
- `SPEC-1844` - one of the 4 ZK specs.
- `SPEC-1644` - one of the 4 ZK specs.
- `SPEC-1840` - one of the 4 ZK specs.
- `GOV-ARTIFACT-APPROVAL-001` - credential safety governs.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness requires security coverage.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.

## Owner Decisions / Input

- 2026-05-15 UTC, S350+: owner approved GTKB-SECURITY-PRIVACY authorization (specs-light initial) including this WI.

## Requirement Sufficiency

Existing requirements sufficient. The 4 cited specs (SPEC-1843/1844/1644/1840) plus the WI description's 5-phase outline form the operative scope.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI, scoping-only; member of PROJECT-GTKB-SECURITY-PRIVACY per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (scoping doc) + IP-2 (planner module) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Phase 4 scoping document

`docs/zero-knowledge-architecture-phase-4-scoping.md`:
- Cite each of the 4 specs with current MemBase status snapshot.
- Enumerate the 5 implementation phases (P4.1..P4.5) with: scope summary, dependent specs, dependent prior-phase, expected session count.
- POR Step 16 prerequisite explicitly noted; readiness check defers actual implementation start.

### IP-2: Phase planner module

`groundtruth-kb/src/groundtruth_kb/security/zk_phase_4_planner.py`:
- `check_prerequisites()` returns POR-Step-16 status + ready flag.
- `next_phase()` returns the next phase to file as a bridge proposal, or None if blocked.
- Read-only; emits diagnostic JSON. No mutation.

## Specification-Derived Verification Plan

| Behavior | Verification |
|---|---|
| Scoping doc enumerates 5 phases | grep `## Phase 4.{1,5}` returns 5 matches |
| Doc cites all 4 ZK specs | grep returns each of SPEC-1843/1844/1644/1840 |
| Planner module imports cleanly | `python -c "from groundtruth_kb.security.zk_phase_4_planner import check_prerequisites"` |
| check_prerequisites returns ready=False when POR-16 incomplete | manual: snapshot current POR-16 state |

(Manual verifications; scoping deliverables are documents + read-only planner.)

## Acceptance Criteria

- IP-1, IP-2 landed.
- Both preflights PASS.
- Phase planner returns ready=False given current POR-16 incompletion (per WI description).

## Risks / Rollback

- Risk: POR Step 16 prerequisite may shift; scoping doc could go stale. Mitigation: planner reads live state; doc references planner output, not hardcoded status.
- Rollback: remove the doc + module.

## Recommended Commit Type

`feat` - scoping infrastructure. ~80 LOC + docs.
