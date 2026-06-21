NEW

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 5b6095bb-bdb4-45f0-b3fb-2f06e87dee2b
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; mode=auto

# Stale-Active Project Retirement - Governed Batch Cleanup (Phase 1)

bridge_kind: operational_state_change
target_paths: []

Document: gtkb-stale-active-project-retirement-batch
Snapshot: 2026-06-21T~22:27Z

## Summary

Retire the active MemBase projects whose every active member work item is already
in a terminal resolution state, applying the intent of
`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` to the standing backlog. As of the
2026-06-21 snapshot this is **62 of 130 active projects (47%)**. This is a one-shot
governed cleanup; no source code changes - MemBase project-status mutations only,
via `gt projects retire`.

This cleanup is necessary because the existing detect-only machinery cannot action
it: `scripts/project_verified_completion_scanner.py` reports **0 completion-ready**
authorizations. It only inspects projects that hold an active project authorization,
and it requires project-scoped `implements` links to VERIFIED-topped bridge threads
that remain in the *live* `bridge/INDEX`; VERIFIED threads are archived out of live
INDEX, which blinds the detector. The actuation path is also manual-only:
`.claude/skills/verify/helpers/write_verdict.py` (VERIFIED finalization) invokes no
retirement at all. The companion root-cause fix is tracked separately (owner AUQ
"both - cleanup first").

## Criterion (owner-approved)

Retire a project when it has >=1 active member work item AND every active member
work item is in a terminal resolution status: `verified`, `resolved`, `retired`,
`wont_fix`, `not_a_defect`. (Owner AUQ 2026-06-21 Q1 = "All terminal resolutions";
chosen over strict-verified-only because `resolved` - not `verified` - is the
dominant terminal WI state, so strict-verified-only would clean almost nothing.)

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (v4) - VERIFIED-driven project
  completion/retirement is automatic; this batch applies that governance intent
  retroactively to the existing backlog.
- `GOV-STANDING-BACKLOG-001` - standing backlog/project authority must reflect real
  lifecycle state.
- `GOV-08` - Knowledge Database is the single source of truth; project status must
  reflect reality.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governs this
  proposal/review/verification cycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all
  relevant governing specs for the operation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the post-implementation report
  will carry spec-derived verification evidence (see Spec-Derived Verification below).
- `.claude/rules/project-root-boundary.md` - all targets are in-root MemBase records.
- `.claude/skills/projects/SKILL.md` (Safety Rules) - bulk multi-project updates
  require a bridge proposal / dry-run inventory packet; this proposal is that packet.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
already specifies VERIFIED-driven retirement; the owner AUQ (2026-06-21) clarified
the *cleanup* criterion as "all terminal resolutions." No new or revised requirement
is required before this cleanup. (The root-cause automation fix is separate tracked
work, not part of this proposal.)

## Prior Deliberations

- `DELIB-2275`, `DELIB-2276` (GO) and `DELIB-2281`, `DELIB-20264756` (NO-GO) - "W1
  Retirement-Machinery Correction" history (machinery built, then repeatedly NO-GO'd).
- `DELIB-20264096` (NO-GO) - gtkb-gov-project-retirement-spec-001.
- `WI-3481` (resolved) - `project_verified_completion_scanner` prematurely auto-retired
  an incrementally-materialized multi-slice project; the premature-retirement risk
  class this proposal explicitly guards against.
- `WI-3292` (resolved) - stale-active doctor check + `kept_open_reason` field +
  session-wrap retirement prompt (the system's designated "keep open" signals).
- `WI-3316` (resolved) - built the VERIFIED->COMPLETED AUQ trigger + retirement flow
  (detect + manual-trigger, not auto-actuation).

## Dry-Run Retirement Plan (62 projects; snapshot 2026-06-21T~22:27Z)

Of 130 active projects: 62 candidates (1 abandon-only; 30 in prefix-split duplicate
pairs). 0 excluded by completion-guard/kept-open (none carry either).

- `PROJECT-AGENT-RED-RELEASE-READINESS` - 1 WI (resolved:1)
- `PROJECT-AGENT-RED-RUFF-CLEANUP-001` - 1 WI (resolved:1) [split-pair]
- `PROJECT-AGENT-RED-RUFF-CLEANUP-001-APPLICATION-SIDE-RUFF-RESOLUTION-AGENT-RED-PRODUCT-CODE` - 1 WI (resolved:1) [split-pair]
- `PROJECT-ARCHITECTURE-IMPROVEMENT` - 8 WI (resolved:8)
- `PROJECT-CTO` - 1 WI (retired:1)
- `PROJECT-DISPATCHER-RECONCILIATION` - 3 WI (resolved:3) [split-pair]
- `PROJECT-DISPATCHER-RECONCILIATION-SCHEDULED-POLLER` - 1 WI (resolved:1) [split-pair]
- `PROJECT-FABLE-INVESTIGATION` - 25 WI (resolved:25)
- `PROJECT-FORWARD-WORK` - 1 WI (retired:1)
- `PROJECT-GT-KB` - 1 WI (retired:1) [split-pair]
- `PROJECT-GT-KB-INTERACTIVE-SESSION-ROLE-OVERRIDE` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GT-KB-TIER-A` - 1 WI (retired:1) [split-pair]
- `PROJECT-GTKB-AUQ-POLICY-GATES-001` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-AUQ-POLICY-GATES-001-CENTRAL-DETERMINISTIC-AUQ-POLICY-GATE-WITH-THIN-HOOK-CLI-DASHBOARD-ADAPTERS` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-BACKLOG-CAPTURE-001-APPROVAL-STATE-TAXONOMY` - 1 WI (resolved:1)
- `PROJECT-GTKB-BRIDGE` - 2 WI (resolved:2) [split-pair]
- `PROJECT-GTKB-BRIDGE-CONTENTION-L2-DISPATCH` - 4 WI (resolved:3, wont_fix:1) [split-pair]
- `PROJECT-GTKB-BRIDGE-CONTENTION-L3-GATE-RACES` - 3 WI (resolved:3) [split-pair]
- `PROJECT-GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-BRIDGE-KIND-TAXONOMY-STABILIZATION` - 3 WI (resolved:3) [split-pair]
- `PROJECT-GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-BRIDGE-RECONCILIATION` - 7 WI (resolved:7) [split-pair]
- `PROJECT-GTKB-CORE-001` - 1 WI (resolved:1)
- `PROJECT-GTKB-DASHBOARD-002-SLICE-2` - 1 WI (retired:1)
- `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-PROJECT-LIFECYCLE` - 3 WI (resolved:3)
- `PROJECT-GTKB-ENV-INVENTORY-001` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-ENV-INVENTORY-001-HARNESS-AND-DEVELOPMENT-ENVIRONMENT-INVENTORY` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-EVALUATION-MODULE-RESTORATION-001` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-EVALUATION-MODULE-RESTORATION-001-RESTORE-OR-REFACTOR-EVALUATION-MODULE-REFERENCES` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1` - 1 WI (retired:1)
- `PROJECT-GTKB-GOV-BACKLOG-DISCIPLINE-SLICE2` - 1 WI (retired:1)
- `PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH` - 7 WI (resolved:7)
- `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICE-2` - 1 WI (resolved:1)
- `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICE-3` - 1 WI (verified:1)
- `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICE-4` - 1 WI (resolved:1)
- `PROJECT-GTKB-ISOLATION-CLOSEOUT` - 3 WI (resolved:3)
- `PROJECT-GTKB-ISOLATION-PHASE-7-SLICE-2` - 1 WI (resolved:1)
- `PROJECT-GTKB-ISOLATION-PROGRAM-CLOSEOUT` - 1 WI (resolved:1)
- `PROJECT-GTKB-OPS-CURRENT-STATE-MONITORING-001` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-OPS-CURRENT-STATE-MONITORING-001-DETERMINISTIC-GT-STATUS-DASHBOARD-STARTUP-OPERATING-STATE-REPORTING` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-PIP-INSTALL-ADOPTER-UX-001` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-PIP-INSTALL-ADOPTER-UX-001-SIMPLIFY-GT-PROJECT-INIT-UX-FOR-PIP-INSTALLED-WHEELS` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-PLATFORM-OBSERVABILITY-HYGIENE` - 1 WI (resolved:1)
- `PROJECT-GTKB-REQUIREMENTS-QUALITY-AUDIT` - 1 WI (resolved:1)
- `PROJECT-GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001-EXTERNAL-RESOURCE-IDENTITY-REGISTRY-AND-CONFUSION-AUDIT` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-RULE-FILE-CURRENCY-AUDIT-001` - 1 WI (resolved:1)
- `PROJECT-GTKB-STARTUP-REFRACTOR-001` - 8 WI (resolved:8) [split-pair]
- `PROJECT-GTKB-STARTUP-REFRACTOR-001-CONSOLIDATE-ROLE-STARTUP-AND-GLOSSARY-LOADING` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001` - 3 WI (resolved:3) [split-pair]
- `PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001-CANONICAL-ARTIFACT-INTERFACE-NAMES-AND-STARTUP-OPERATING-SURFACE-MAP` - 1 WI (resolved:1) [split-pair]
- `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-PHASE-0-SCHEMA-CLI-SKELETON` - 5 WI (resolved:5)
- `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-PHASE-1-LEASE-SUBSYSTEM` - 3 WI (resolved:3)
- `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-PHASE-2-IMPLEMENTATION-FLOW-PILOT` - 2 WI (resolved:2)
- `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-PHASE-3-DISPATCH-POLICY-ENGINE` - 3 WI (resolved:3)
- `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-PHASE-4-REMAINING-FLOWS` - 4 WI (resolved:4)
- `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-PHASE-5-TELEMETRY-HEALTH` - 3 WI (resolved:3)
- `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-PHASE-7-GOVERNED-CUTOVER` - 2 WI (resolved:2)
- `PROJECT-HARNESS-REGISTRY-REFACTOR` - 8 WI (resolved:2, verified:6)
- `PROJECT-MINOR` - 1 WI (not_a_defect:1) [abandon-only]
- `PROJECT-PARALLEL-DISPATCH-REMEDIATION-SWEEP` - 12 WI (resolved:12)
- `PROJECT-POR-SPEC-HYGIENE` - 1 WI (resolved:1)

## Premature-Retirement Guard (WI-3481 class)

Incrementally-materialized multi-slice projects can appear all-terminal before later
slices are filed as members. Mitigations:

1. None of the 62 carries an active `plan_incomplete` completion guard or a
   `kept_open_reason` - the system's designated "more work anticipated" signals
   (WI-3292). Absent those, all-members-terminal == complete under the approved
   criterion.
2. Retirement is append-only and reversible: a later
   `gt projects update <ID> --status active` restores an over-eagerly retired project
   with full audit trail.
3. Multi-slice umbrellas with open work are NOT in scope (they have non-terminal
   members and fall in the legitimately-active set, e.g. the active parent
   `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE`); only their already-complete child
   slice/phase sub-projects retire.

## Implementation Plan

On GO:

1. `python scripts/implementation_authorization.py begin --bridge-id gtkb-stale-active-project-retirement-batch`
2. Recompute the then-current all-terminal candidate set (drift-robust; the enumerated
   62 is the snapshot, the apply acts on the live set and logs any delta vs this list).
3. For each project:
   `gt projects retire <ID> --change-reason "Batch stale-active retirement per gtkb-stale-active-project-retirement-batch GO; all active member WIs terminal; GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001; owner AUQ 2026-06-21"`.
4. File a post-implementation report with before/after counts and the exact retired set.

## Spec-Derived Verification

Derived from `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (retired-iff-all-members-terminal)
and `GOV-08` (status reflects reality):

- Re-run the read-only triage post-apply: every project in the approved/recomputed set
  now has `status='retired'` in `current_projects` (latest version) with the cited
  `change_reason`.
- Assert no project carrying a non-terminal member WI was retired (recompute candidates
  post-apply; the retired set must equal the criterion-derived set).
- Assert the active-project count decreased by exactly the size of the applied set.
- `gt projects list` no longer shows the retired projects as active.

## Risk / Rollback

- Risk: premature retirement of a multi-slice project (mitigated above; reversible).
- Risk: drift between snapshot and apply (mitigated: apply recomputes the live set and
  logs the delta vs this enumerated list).
- Rollback: `gt projects update <ID> --status active --change-reason "revert: <reason>"`
  per project; append-only history preserves all prior versions.

## Owner Decisions / Input

- AUQ 2026-06-21 Q1 "Retire criterion" -> **All terminal resolutions** (retire where
  every active member WI is in {verified, resolved, retired, wont_fix, not_a_defect}).
- AUQ 2026-06-21 Q2 "Sequencing" -> **Both - cleanup first** (file this governed cleanup
  now; capture the auto-retire-on-VERIFIED automation fix as tracked work in parallel).

## Recommended Commit Type

`chore:` - MemBase project-status hygiene; no source or behavior change. (Applied at
post-impl finalization, not in this proposal.)
