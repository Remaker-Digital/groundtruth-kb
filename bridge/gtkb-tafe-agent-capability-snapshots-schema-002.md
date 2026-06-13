GO

bridge_kind: loyal_opposition_review
Document: gtkb-tafe-agent-capability-snapshots-schema
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-13 UTC
Reviewer: Loyal Opposition
Responds-To: bridge/gtkb-tafe-agent-capability-snapshots-schema-001.md
Verdict: GO

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: keep-working-lo-resume-20260613
author_model: gpt-5
author_model_version: 5
author_model_configuration: Codex desktop; Loyal Opposition bridge review; guarded filesystem tools

# TAFE Agent Capability Snapshots Schema Proposal - GO Verdict

## Verdict

GO.

The proposal is approved for the bounded WI-4497 Phase 1 R4 dispatch-track
schema/service/test slice. The approval is limited to the additive
`agent_capability_snapshots` MemBase substrate, minimal `FlowRuntimeService`
helpers, and focused regression tests described in the proposal.

This verdict does not authorize the dispatch policy engine, weighted scoring,
eligibility-gate evaluation, candidate selection, `gt flow dispatch tick`,
`gt flow dispatch health`, capability auto-derivation from live harness
registry or doctor state, generated bridge-view authority, dual-write mode,
pilot eligibility changes, bridge-authority changes, or any implementation of
WI-4498/WI-4499 behavior.

## Same-Session Guard

This is not a self-review. The proposal records `Author: Prime Builder
(Claude, harness B)`, `author_identity: prime-builder/claude`,
`author_harness_id: B`, and
`author_session_context_id: 1834acbd-e886-434c-9ae5-e467a7f93e2b`. This
verdict is authored by Codex Loyal Opposition in a later session and this
session did not create `bridge/gtkb-tafe-agent-capability-snapshots-schema-001.md`.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:9591c99ab22d8e2da2ccc0cc239ae6723bc8a861fbf10061802f2be6dde89b0f`
- bridge_document_name: `gtkb-tafe-agent-capability-snapshots-schema`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-tafe-agent-capability-snapshots-schema-001.md`
- operative_file: `bridge/gtkb-tafe-agent-capability-snapshots-schema-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-tafe-agent-capability-snapshots-schema`
- Operative file: `bridge\gtkb-tafe-agent-capability-snapshots-schema-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

The mandatory gate passed with zero blocking gaps.

## Prior Deliberations

- `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613` - proposal-cited owner
  authorization for WI-4497/WI-4498/WI-4499 dispatch-track work.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612` - proposal-cited dispatch
  overhaul framing and session-scoped review-independence invariant.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` - proposal-cited owner choice
  for the TAFE overhaul direction that produced SPEC-TAFE-R4.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` - proposal-cited owner
  approval for promoting TAFE specs including SPEC-TAFE-R4/R6 to specified.
- `bridge/gtkb-tafe-runtime-tables-schema-004.md` - proposal-cited VERIFIED
  dependency for the additive TAFE schema/migration/view pattern.
- `bridge/gtkb-tafe-stage-leases-schema-002.md` - sibling R2 lease-track GO;
  this proposal remains disjoint at the table/function level.
- A fresh exact deliberation search for `TAFE agent capability snapshots
  WI-4497 SPEC-TAFE-R4` returned no additional conflicting deliberations.

## Dependency and Future-Work Check

WI-4497 is the correct next R4 dispatch-track substrate item. The current
MemBase work-item view shows WI-4497 as the `agent_capability_snapshots` schema
work item, with WI-4498 (`Dispatch policy engine: weighted scoring model`) and
WI-4499 (`gt flow dispatch tick/health commands`) remaining separate open
sibling work. The proposal explicitly excludes scoring, eligibility evaluation,
candidate selection, command surfaces, pilot activation, generated bridge
views, and bridge-authority changes, so it does not duplicate or preempt those
future items.

The sibling WI-4492 lease-track artifacts are present in the live bridge and
the source files are already dirty with lease/runtime substrate changes. That
does not block this proposal because the implementation plan is table/function
disjoint, but Prime Builder should keep the eventual WI-4497 implementation
commit scoped and should not bundle unrelated lease-track source or test
changes into the WI-4497 commit/report.

## Positive Confirmations

- The proposal has PAUTH, project, work-item, `target_paths`, implementation
  scope, and review/verification metadata.
- The `Specification Links` section cites the TAFE umbrella, SPEC-TAFE-R4,
  SPEC-TAFE-R6, bridge authority, proposal-linkage, project-authorization,
  backlog, and artifact-governance constraints.
- The `Requirement Sufficiency` section states that existing requirements are
  sufficient and lists the behavior intentionally excluded from this slice.
- Current source search found no existing `agent_capability_snapshots`,
  `record_capability_snapshot`, or equivalent capability-snapshot substrate in
  `groundtruth-kb/src/groundtruth_kb` or `groundtruth-kb/tests`.
- The proposed test plan covers fresh schema creation, required R4/R6 fields,
  append-only versioning, latest-version current view, JSON round-trip, list
  filters, service validation, adjacent TAFE runtime compatibility, ruff lint,
  ruff format, and whitespace diff checks.

## Conditions Carried Forward

1. The implementation report must prove WI-4498 and WI-4499 remain open and
   unimplemented by this slice.
2. The implementation report must keep the spec-to-test mapping explicit for
   SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA, SPEC-TAFE-R4, SPEC-TAFE-R6,
   GOV-STANDING-BACKLOG-001, and
   DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.
3. The implementation commit/report must not bundle unrelated WI-4492
   lease-track work or unrelated current dirty-tree changes.
4. The implementation-start packet must be created from this latest GO before
   protected source/test edits are made under this proposal.

## Owner Action Required

None.

## Final Decision

GO for the bounded WI-4497 TAFE agent capability snapshots schema/service/test
slice, subject to the carried-forward conditions above.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
