NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019eec7a-1812-7560-843e-18734055771e
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive; owner requested ::init gtkb pb; approval_policy=never; sandbox=danger-full-access

# Closure authorization repair: resolve WI GTKB-DASHBOARD-002-SLICE-2-2-METRICS and retire PROJECT-GTKB-DASHBOARD-002-SLICE-2-2-METRICS

bridge_kind: operational_state_change
Document: gtkb-dashboard-002-slice-2-2-metrics-descope-closure-auth-repair
Version: 001
Author: Prime Builder (Codex, harness A, interactive PB override)
Date: 2026-06-22 UTC

Subject Work Item: GTKB-DASHBOARD-002-SLICE-2-2-METRICS
Subject Project: PROJECT-GTKB-DASHBOARD-002-SLICE-2-2-METRICS
target_paths: ["groundtruth.db"]
implementation_scope: project_lifecycle_membase_state_change
requires_review: true
kb_mutation_in_scope: true

---

## Purpose

This proposal repairs the implementation-start authorization shape for the already
owner-approved Slice 2.2 metrics closure. The prior closure thread
`gtkb-dashboard-002-slice-2-2-metrics-descope-closure` received `GO` at
`bridge/gtkb-dashboard-002-slice-2-2-metrics-descope-closure-002.md`, but
`python scripts/implementation_authorization.py begin --bridge-id gtkb-dashboard-002-slice-2-2-metrics-descope-closure`
correctly failed because the approved proposal carried `target_paths: []` and no
specification-derived verification plan.

This fresh operational-state-change proposal preserves the same owner-approved
closure intent while making the protected MemBase mutation target and
verification plan explicit. No source, test, hook, workflow, schema, dashboard,
deployment, or Agent Red repository change is in scope.

## Proposed State Changes

After Loyal Opposition records `GO`, Prime Builder will perform exactly two
MemBase state mutations in `groundtruth.db`:

1. Resolve work item `GTKB-DASHBOARD-002-SLICE-2-2-METRICS`
   (`resolution_status` open -> resolved), with completion evidence citing:
   `DELIB-DASHBOARD-002-SLICE-2-2-METRICS-DESCOPE-CLOSE`,
   `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-026.md`, and this
   authorization-repair bridge thread.
2. Retire project `PROJECT-GTKB-DASHBOARD-002-SLICE-2-2-METRICS`
   (`status` active -> retired), with change reason citing the same evidence.

The live `pip-audit-results -> dashboard` CI-evidence concern remains descoped
from this project and preserved separately as Agent Red backlog item `WI-4736`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority for this proposal,
  the required LO review, and the implementation-start authorization packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete
  governing specification links in bridge proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification to
  derive from cited requirements. For this no-code operational state change,
  verification maps to exact MemBase lifecycle-state assertions rather than
  source-level tests.
- `GOV-STANDING-BACKLOG-001` - MemBase `work_items` is the canonical backlog
  authority; this proposal resolves one work item there.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - VERIFIED-driven project
  completion/retirement; the underlying Slice 2.2 implementation thread is
  already VERIFIED at `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-026.md`.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - the principle
  that a VERIFIED bridge thread retires its parent backlog item, applied here
  under explicit owner descope authority because the original slice thread did
  not auto-resolve this sub-project work item.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - reclassifies the live CI-evidence
  flow to Agent Red scope without making this GT-KB project depend on an
  out-of-root application repository state.
- `.claude/rules/project-root-boundary.md` - this action mutates only the in-root
  MemBase database and does not create any live out-of-root dependency.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the descoped concern as
  durable backlog item `WI-4736`.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the work item and project transition
  into explicit terminal lifecycle states with recorded evidence and rollback
  path.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links the owner decision, verified
  implementation thread, descoped backlog item, and lifecycle state changes as
  durable artifacts.
- `GOV-16` - deployment approval gate is not triggered because this proposal
  performs no deploy, no workflow dispatch, no Agent Red repository operation,
  and no `develop -> main` merge.

## Requirement Sufficiency

Existing requirements sufficient. The Slice 2.2 metric implementation was
already shipped and VERIFIED, and the owner decision
`DELIB-DASHBOARD-002-SLICE-2-2-METRICS-DESCOPE-CLOSE` authorizes resolving the
work item and retiring the project without the runtime CI-evidence gate. This
proposal requests only the two MemBase lifecycle state changes named above.

## Specification-Derived Verification Plan

The verification surface derives directly from the linked lifecycle and bridge
requirements:

- `GOV-FILE-BRIDGE-AUTHORITY-001`: before any mutation, run
  `python scripts/implementation_authorization.py begin --bridge-id gtkb-dashboard-002-slice-2-2-metrics-descope-closure-auth-repair`
  and require `authorized: true`.
- `GOV-STANDING-BACKLOG-001` and `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`:
  after mutation, query `groundtruth.db` and require work item
  `GTKB-DASHBOARD-002-SLICE-2-2-METRICS` to have `resolution_status='resolved'`
  and terminal/resolved stage detail.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`: after mutation, query
  `groundtruth.db` and require project
  `PROJECT-GTKB-DASHBOARD-002-SLICE-2-2-METRICS` to have `status='retired'`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `.claude/rules/project-root-boundary.md`,
  and `GOV-16`: verify no source, workflow, deployment, or Agent Red repository
  files were changed by comparing `git status --short` before and after the
  mutation; expected implementation delta is `groundtruth.db` plus bridge/report
  artifacts only.

Planned post-mutation verification commands:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-dashboard-002-slice-2-2-metrics-descope-closure-auth-repair
gt backlog show GTKB-DASHBOARD-002-SLICE-2-2-METRICS --json
gt projects show PROJECT-GTKB-DASHBOARD-002-SLICE-2-2-METRICS --json
git status --short
```

If `gt` output is slow or blocked by unrelated local state, Prime Builder may
use an equivalent exact SQLite read-only query against `groundtruth.db` to
verify the same two lifecycle fields.

## Owner Decisions / Input

This proposal depends on and is authorized by:

- `DELIB-DASHBOARD-002-SLICE-2-2-METRICS-DESCOPE-CLOSE`
  (`source_type=owner_conversation`, `outcome=owner_decision`) - owner AUQ answer
  "Descope gate, close now" on 2026-06-21. The selected option authorizes
  resolving WI `GTKB-DASHBOARD-002-SLICE-2-2-METRICS`, retiring project
  `PROJECT-GTKB-DASHBOARD-002-SLICE-2-2-METRICS`, and reclassifying the live
  CI-evidence flow as separate Agent Red concern `WI-4736`.

## Scope Boundaries

- No code, test, hook, workflow, schema, dashboard, deploy, or Agent Red
  repository change.
- No credential read, credential write, credential rotation, or production
  deployment.
- No change to the descoped Agent Red backlog item `WI-4736`.
- No edit to the prior approved bridge thread; this fresh thread exists only
  because the implementation-start authorization packet rejected the prior
  proposal's missing target and verification metadata.

## Risk and Rollback

Risk is low because the underlying implementation thread is already VERIFIED and
the owner explicitly authorized the descope closure. Functional application risk
is none because the shipped dashboard metric and graceful-degradation contract
are untouched.

Rollback is append-only: reopen the work item and reactivate the project with a
new bridge-authorized MemBase state change. The separate Agent Red concern
`WI-4736` remains tracked either way.

## Prior Deliberations

- `DELIB-DASHBOARD-002-SLICE-2-2-METRICS-DESCOPE-CLOSE` - owner descope decision
  authorizing closure.
- `DELIB-0983` - "Codex Verification: Slice 2.2 Metrics Parking Baseline", the
  terminal VERIFIED record for the Slice 2.2 metrics implementation thread.
- `DELIB-1127` - compressed Slice 2.2 metrics bridge thread context.
- `DELIB-2016` - compressed Slice 2.2 metrics bridge thread context from a
  parallel-checkout history.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - the bridge
  VERIFIED retires parent backlog principle applied here under owner descope
  authority.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
