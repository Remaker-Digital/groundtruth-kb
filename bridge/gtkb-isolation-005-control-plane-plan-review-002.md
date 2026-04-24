GO

# Loyal Opposition Review - GTKB-ISOLATION-005 Dashboard Control Plane Plan

bridge_kind: review
scope: protocol
work_item_ids: [GTKB-ISOLATION-005]
reviewed_file: bridge/gtkb-isolation-005-control-plane-plan-review-001.md
reviewed_status: NEW
reviewed_plan: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-005-PHASE5-DASHBOARD-CONTROL-PLANE-PLAN-2026-04-23.md

## Verdict

GO for accepting the Phase 5 dashboard control-plane plan as the completed
planning artifact for `GTKB-ISOLATION-005`.

This is a planning GO only. It does not authorize implementation, dashboard
mutation endpoints, formal artifact mutation, credential use, release,
deployment, repository moves, or destructive cleanup.

## Prior Deliberations

- `DELIB-0877` is the parent isolation planning record
  (`.groundtruth/formal-artifact-approvals/2026-04-22-gtkb-app-isolation-phased-planning.json:6`).
- `DELIB-0877` version 7 identified privileged dashboard shells, canonical
  Markdown mutation, over-projection, mixed roots, and control-plane
  reconciliation as risks to avoid
  (`.groundtruth/formal-artifact-approvals/2026-04-22-gtkb-app-isolation-industry-critique-update.json:6`).
- `DELIB-0878` and `DELIB-0879` provide the authority and root-topology basis
  for path/capability allowlists
  (`.groundtruth/formal-artifact-approvals/2026-04-22-gtkb-isolation-001-authority-matrix-plan.json:6`,
  `.groundtruth/formal-artifact-approvals/2026-04-22-gtkb-isolation-002-root-topology-plan.json:6`).

The proposal builds on these deliberations and does not ask to expose an
arbitrary browser shell or free-form filesystem editor.

## Findings

### F1 - Operation Registry Before Mutation Is Adequately Specified

Claim: The Phase 5 plan defines a safe control-plane shape before any mutating
dashboard endpoint exists.

Evidence: The claim starts at line 9. Control-plane principles start at line
86 and deny arbitrary shell execution and arbitrary filesystem paths. The
operation registry starts at line 109 and names operation metadata including
subject, role slot, path policy, approval policy, dry-run handler, apply
handler, audit schema, rollback strategy, and timing. Path and capability
allowlists start at line 155. Authentication and authorization start at line
347, and GOV/formal approval boundaries start at line 365.

Risk/impact: Without a registry-first design, a dashboard control plane could
become a privileged shell or raw artifact editor.

Recommended action: Accept the plan, and require later implementation to begin
with registry/dry-run/path resolver foundations before any apply-capable UI
endpoint is enabled.

Owner decision needed: none.

### F2 - Projection, Topology, Bridge, And Session Controls Are Covered

Claim: The plan covers the non-obvious control-plane surfaces that would
otherwise produce cross-harness or stale-policy drift.

Evidence: Markdown operations begin at line 188, projection at line 215,
durable mode/subject/role-slot flow at line 249, harness topology at line
270, bridge operations at line 293, session control at line 309, and audit/
diff/rollback at line 325. Verification requirements start at line 411 and
acceptance criteria at line 428. `memory/work_list.md:173` marks
`GTKB-ISOLATION-005` as DONE.

Risk/impact: Mode changes, generated startup files, and bridge writes are high
risk because they can alter future agent behavior. The plan keeps them typed,
source-hashed, audited, and role/topology-aware.

Recommended action: Later implementation must test wrong-role bridge writes,
stale projection handling, rollback hash mismatch behavior, and browser
refresh-token scope separation.

Owner decision needed: none.

## Verification Performed

This review performed document and repository evidence checks only. No tests
were run because the bridge request is a planning review and no implementation
change was proposed.

## Decision Needed From Owner

None for this planning GO.
