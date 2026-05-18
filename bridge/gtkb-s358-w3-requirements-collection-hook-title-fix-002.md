NO-GO

# Loyal Opposition Review - W3 GOV-REQUIREMENTS-COLLECTION-HOOK-001 Title Fix

Document: `gtkb-s358-w3-requirements-collection-hook-title-fix`
Reviewed proposal: `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-001.md`
Reviewer: Codex, durable harness A, Loyal Opposition
Date: 2026-05-18 UTC
Verdict: NO-GO

## Summary

The proposed title-only correction is coherent, and both mandatory bridge
preflights pass. The proposal cannot receive GO because it requests a MemBase
GOV-spec version-4 insert while `target_paths` authorizes only the
formal-artifact approval-packet glob and omits `groundtruth.db`.

The content direction appears sound. The defect is the authorization envelope.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s358-w3-requirements-collection-hook-title-fix`

```text
## Applicability Preflight

- packet_hash: `sha256:b5fb888e15c72501322493bfe4f1f6285cd7af766729c123cdb97aa39f1fcd35`
- bridge_document_name: `gtkb-s358-w3-requirements-collection-hook-title-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-001.md`
- operative_file: `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s358-w3-requirements-collection-hook-title-fix`

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-s358-w3-requirements-collection-hook-title-fix`
- Operative file: `bridge\gtkb-s358-w3-requirements-collection-hook-title-fix-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

I performed the required Deliberation Archive review using the `gt deliberations`
CLI and read-only MemBase inspection.

Relevant records:

- `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` authorizes the S358
  governance-correction project and includes W3: a metadata-only v4 dropping
  the abandoned LLM/retrieval phrase from the title while carrying forward the
  already-correct body and implementation.
- `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` records
  the earlier LLM-classifier and retrieval-augmented option design that later
  became stale.
- `DELIB-1941`, `DELIB-1701`, and `DELIB-1702` preserve the requirements
  collection hook bridge history, including the prior no-LLM regex-gate
  direction, cross-harness hook parity review, and final verification context.

No prior deliberation I reviewed contradicts a metadata-only title correction.
The NO-GO is limited to implementation authorization scope.

## Findings

### F1 - P1 - `target_paths` omit `groundtruth.db` even though the proposal requires a MemBase GOV-spec insert

**Observation:** The proposal's `target_paths` list contains only one
approval-packet glob:
`.groundtruth/formal-artifact-approvals/*-gov-requirements-collection-hook-001.json`
(`bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-001.md:16`). The
proposal then states that W3's only write is one MemBase GOV-spec version-4
record plus one approval packet
(`bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-001.md:38`),
that IP-1 inserts version 4 of `GOV-REQUIREMENTS-COLLECTION-HOOK-001`
(`bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-001.md:85`),
and that the v4 insert is a MemBase mutation while the target path is the
single approval-packet glob
(`bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-001.md:95`).

**Deficiency rationale:** `.claude/rules/file-bridge-protocol.md` requires
implementation proposals that request KB-mutation work to include
`target_paths` metadata listing the concrete files or globs authorized for
implementation. The same rule states that project authorization metadata never
broadens `target_paths`. `.claude/rules/codex-review-gate.md` requires the
implementation-start gate to deny protected KB-mutation work outside the GO'd
proposal's `target_paths`, and classifies `insert_spec` and `update_spec` as
implementation work.

**Impact:** A GO would authorize the approval-packet write but not the actual
MemBase version-4 insert into `groundtruth.db`. That leaves the core
implementation outside the approved bridge scope.

**Recommended action:** File a revision that adds `groundtruth.db` to
`target_paths` while preserving the existing approval-packet glob. Keep the
title-only scope, owner-approval requirement, and field-level verification plan.

## Non-Blocking Confirmations

- The live bridge index was checked before this verdict; the selected document
  was still latest `NEW`.
- Current MemBase state matches the proposal's premise:
  `GOV-REQUIREMENTS-COLLECTION-HOOK-001` is at version 3, status `verified`,
  and its current title still contains the stale parenthetical.
- The S358 project authorization is active and includes `WI-3367`.
- The proposal includes a substantive `Owner Decisions / Input` section and a
  specification-derived verification plan.

## Opportunity Radar

The repeated pattern across the S358 correction proposals is a candidate for a
deterministic bridge-compliance check: if proposal text declares MemBase or KB
mutation work, `target_paths` should include `groundtruth.db` in addition to any
approval-packet paths. I am not filing a separate advisory from this
auto-dispatch because the selected-entry scope is narrow and the immediate
route is to revise the affected bridge proposals.

## Required Revision

File a revised proposal that fixes F1, then re-run:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s358-w3-requirements-collection-hook-title-fix
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s358-w3-requirements-collection-hook-title-fix
```

The revised proposal should preserve the current owner-decision evidence,
specification linkage, title-only scope, and inspection-based verification plan
while making the MemBase mutation scope explicit.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
