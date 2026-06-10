GO

# Loyal Opposition Supplemental Review - GTKB-ISOLATION-007 Work Subject And Root Enforcement Plan

bridge_kind: lo_verdict
scope: protocol
work_item_ids: [GTKB-ISOLATION-007]
reviewed_file: bridge/gtkb-isolation-007-work-subject-root-plan-review-001.md
reviewed_status: NEW
reviewed_plan: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md
supersedes_generated_review: bridge/gtkb-isolation-007-work-subject-root-plan-review-002.md

## Verdict

GO for accepting the Phase 7 work-subject and root-enforcement plan as the
completed planning artifact for `GTKB-ISOLATION-007`.

This is not an implementation GO. It does not authorize work-subject code
changes, formal artifact mutation, release, deployment, repository moves,
credential use, or destructive cleanup. A later concrete implementation
proposal or explicit owner supersession is still required before
implementation.

## Prior Deliberations

- `DELIB-0877` is the parent GT-KB/application isolation planning record
  (`.groundtruth/formal-artifact-approvals/2026-04-22-gtkb-app-isolation-phased-planning.json:6`).
- `DELIB-0877` version 7 required the separation problem to cover artifact
  authority, workspace/repository boundary, host/container/development
  environment boundary, service/API boundary, control-plane reconciliation,
  and subject-scoped review/release/test boundaries
  (`.groundtruth/formal-artifact-approvals/2026-04-22-gtkb-app-isolation-industry-critique-update.json:6`).
- `DELIB-0878` and `DELIB-0879` provide the authority-matrix and root-topology
  prerequisites for this phase
  (`.groundtruth/formal-artifact-approvals/2026-04-22-gtkb-isolation-001-authority-matrix-plan.json:6`,
  `.groundtruth/formal-artifact-approvals/2026-04-22-gtkb-isolation-002-root-topology-plan.json:6`).
- Prior bridge context also applies: `bridge/gtkb-session-work-subject-004.md`
  GO'd the revised Phase 7 planning basis while expressly withholding immediate
  implementation authorization.

The proposal does not revisit a rejected approach without acknowledging the
dependency and authorization boundaries.

## Findings

### F1 - Phase 7 Now Integrates Its Prerequisites

Claim: The completed Phase 7 plan adequately incorporates Phases 3 through 6
instead of treating work-subject enforcement as a standalone hook rename.

Evidence: The Phase 7 claim starts at line 9 and states at line 24 that
implementation must use the Phase 3 environment boundary, Phase 4 scoped
service boundary, Phase 5 typed control plane, and Phase 6 copy-only overlay
contracts. The evidence base starts at line 30 and cites each prerequisite
phase. `memory/work_list.md:197` marks `GTKB-ISOLATION-007` as DONE and
`memory/work_list.md:201` points to the completed plan.

Risk/impact: Work-subject text without the lower-level boundaries would leave
the owner supervising routine root and product/application separation risk.

Recommended action: Accept the Phase 7 planning artifact, but require the
later implementation proposal to map every file/test slice to the Phase 3-6
contract it enforces.

Owner decision needed: none.

### F2 - Work Subject, Root, Startup, And Test Scoping Are Concrete

Claim: The plan is specific enough to guide a later implementation proposal.

Evidence: The subject model starts at line 98, durable state contract at line
120, root-boundary enforcement at line 169, startup/dashboard scoping at line
204, release-readiness and test scoping at line 231, hook/Codex parity at line
253, control-plane integration at line 266, overlay integration at line 283,
multi-harness bridge-role awareness at line 299, and portable GT-KB delivery
at line 319. Verification matrix starts at line 356 and acceptance criteria at
line 376.

Risk/impact: The plan reduces ambiguity around whether role, subject, root,
topology, and bridge role slot are the same thing. They are not, and the later
implementation must preserve that separation.

Recommended action: Later implementation should include migration from
workstream-focus state to work-subject state, resolved-root traversal tests,
application/GT-KB verification lanes, and upstream clean-adopter scaffold,
doctor, and preflight coverage.

Owner decision needed: none.

### F3 - Implementation Remains Properly Blocked

Claim: The reviewed package preserves the governance boundary between planning
completion and implementation authority.

Evidence: The review request states that it is a planning review and does not
authorize implementation. The prior `gtkb-session-work-subject` GO in
`bridge/gtkb-session-work-subject-004.md` also said the prior planning GO was
not an immediate implementation GO and required Phases 3 through 6 first.

Risk/impact: Treating this planning GO as implementation authorization would
bypass the bridge proposal sequence and could mutate hooks/startup/control
plane behavior without an implementation slice, test plan, or rollback path.

Recommended action: Prime Builder may treat `GTKB-ISOLATION-007` planning as
accepted. Before changing behavior, Prime Builder should submit a concrete
implementation proposal or obtain explicit owner supersession.

Owner decision needed: none.

### F4 - Bridge Index Behavior Must Be Mechanized

Claim: The later implementation plan must include deterministic bridge index
handling so bridge state cannot be derived from cached or partially stale
surfaces.

Evidence: During this review session, live bridge processing exposed exactly
the failure mode the protocol is trying to prevent: bridge response files can
exist on disk while the live index has not been advanced, and manual patching
can partially apply before all intended entry updates are complete. The
authoritative bridge protocol now requires a mechanical bridge writer/validator
that fresh-reads live `bridge/INDEX.md`, parses full entries, validates role
and status transitions, computes the next version from live index plus disk,
writes the response file before inserting the status line, re-reads or locks
the index before insertion, preserves prior audit lines, and verifies the
post-write live state.

Risk/impact: If the future work-subject/control-plane implementation leaves
bridge updates as ad hoc manual edits, the bridge can drift from its audit
files, cached dashboard/status values can mislead agents, and Prime Builder or
Loyal Opposition can process the wrong queue state.

Recommended action: The later concrete implementation proposal for Phase 7,
or any earlier bridge/control-plane implementation proposal, must include a
scripted bridge writer/validator plus tests for stale index rejection,
next-number calculation, invalid transition rejection, existing-file collision,
concurrent index change, and post-write live-state verification.

Owner decision needed: none; this is now a bridge-function requirement.

## Verification Performed

This review performed document and repository evidence checks only. No tests
were run because the bridge request is a planning review and no implementation
change was proposed.

## Decision Needed From Owner

None for this planning GO.
