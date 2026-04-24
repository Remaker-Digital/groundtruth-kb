GO

# Loyal Opposition Review - GTKB-ISOLATION-004 Scoped Service Boundary Plan

bridge_kind: review
scope: protocol
work_item_ids: [GTKB-ISOLATION-004]
reviewed_file: bridge/gtkb-isolation-004-service-boundary-plan-review-001.md
reviewed_status: NEW
reviewed_plan: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-004-PHASE4-SCOPED-SERVICE-BOUNDARY-PLAN-2026-04-23.md

## Verdict

GO for accepting the Phase 4 scoped service boundary plan as the completed
planning artifact for `GTKB-ISOLATION-004`.

This is a planning GO only. It does not authorize implementation,
formal artifact mutation, service deployment, credential use, release,
repository moves, or destructive cleanup.

## Prior Deliberations

- `DELIB-0877` is the parent GT-KB/application isolation planning record
  (`.groundtruth/formal-artifact-approvals/2026-04-22-gtkb-app-isolation-phased-planning.json:6`).
- `DELIB-0877` version 7 warned against raw database credentials, privileged
  dashboard shells, and treating project roots as security boundaries
  (`.groundtruth/formal-artifact-approvals/2026-04-22-gtkb-app-isolation-industry-critique-update.json:6`).
- `DELIB-0878` and `DELIB-0879` provide authority-matrix and root-topology
  context for scoped service design
  (`.groundtruth/formal-artifact-approvals/2026-04-22-gtkb-isolation-001-authority-matrix-plan.json:6`,
  `.groundtruth/formal-artifact-approvals/2026-04-22-gtkb-isolation-002-root-topology-plan.json:6`).

The proposal is aligned with those deliberations and does not reintroduce raw
all-powerful product authority as the ordinary app-session path.

## Findings

### F1 - Raw Product Authority Is Correctly Rejected

Claim: The Phase 4 plan establishes the service/API boundary needed to keep
ordinary application sessions from receiving raw parent-root or database
authority.

Evidence: The claim begins at line 14. The boundary principles start at line
96 and frame scoped, subject-labeled operations as the control surface. The
scoped operation catalog begins at line 119 and covers dashboard reads/refresh,
Deliberation Archive, MemBase, bridge, release/deployment, credential,
upgrade/scaffold, and offline/degraded workflows. The data and authority model
begins at line 136.

Risk/impact: If later implementation bypasses this service boundary and hands
ordinary sessions raw DB/root access, the Phase 7 work-subject model would not
protect product artifacts.

Recommended action: Accept the plan, but require later implementation to expose
typed operations rather than direct database handles or unbounded filesystem
access.

Owner decision needed: none.

### F2 - GOV And Subject Enforcement Are Covered At The Right Layer

Claim: The plan correctly places mutation enforcement in service/library code,
not only in AI prompts or local hooks.

Evidence: Service-side GOV enforcement starts at line 182. The plan separately
covers dashboard read boundaries at line 200, DA boundaries at line 219,
MemBase boundaries at line 237, release/deployment request boundaries at line
254, credential scope at line 281, and offline/degraded mode at line 302. The
verification matrix starts at line 316 and acceptance criteria start at line
380. `memory/work_list.md:161` marks `GTKB-ISOLATION-004` as DONE.

Risk/impact: Hook-only enforcement would fail for CLI/package callers, future
hosted services, or dashboard/control-plane paths.

Recommended action: Later implementation should reuse one approval-packet
validation path across CLI, package, service, and dashboard operations, and
must test app-subject attempts to mutate product records.

Owner decision needed: none.

## Verification Performed

This review performed document and repository evidence checks only. No tests
were run because the bridge request is a planning review and no implementation
change was proposed.

## Decision Needed From Owner

None for this planning GO.
