NO-GO

# Loyal Opposition Review - Governed Spec Retirement Proposal REVISED-1

Document: gtkb-governed-spec-retirement
Reviewed file: `bridge/gtkb-governed-spec-retirement-003.md`
Prior chain reviewed:

- `bridge/gtkb-governed-spec-retirement-001.md`
- `bridge/gtkb-governed-spec-retirement-002.md`
- `bridge/gtkb-governed-spec-retirement-003.md`

Reviewer: Codex Loyal Opposition
Date: 2026-05-14 UTC
Verdict: NO-GO

## Summary

REVISED-1 materially improves the original filing: it replaces the non-existent
`update_specification()` call with the live `KnowledgeDB.update_spec(...)` API,
adds `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, removes the placeholder posture,
and passes both mandatory mechanical preflights.

It still cannot receive GO because the formal-artifact approval packet is not
bound tightly enough to the exact spec retirement being performed. As written,
a valid formal packet for a different spec of the same artifact type could pass
the proposed checks. The proposal also keeps a `work_items` mutation in scope
without specifying required `insert_work_item()` fields or verifying the
resulting row. Both issues are within the revised proposal's core safety claim.

## Prior Deliberations

Read-only Deliberation Archive searches were run:

```powershell
python -m groundtruth_kb deliberations search "governed spec retirement assertion retirement workflow SPEC-1662" --limit 8
python -m groundtruth_kb deliberations search "S349 retire deferral governed retirement follow-on bridge" --limit 8
```

Relevant results:

- `DELIB-1580` - Loyal Opposition verification of the backlog work-list retirement directive; relevant to retirement discipline and avoiding misleading lifecycle closure.
- The searches did not surface direct archived deliberation evidence for the S349 retire-deferral AskUserQuestion. The direct durable evidence for this review remains the live bridge chain, especially `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-014.md`, `-015.md`, and `bridge/gtkb-governed-spec-retirement-001.md` through `-003.md`.

## Blocking Findings

### F1 - Formal packet validation is not bound to the exact spec retirement

Severity: P1 governance authorization defect

Observation: The proposal says the formal packet check is fixed by deriving
`artifact_type` from the spec being retired (`bridge/gtkb-governed-spec-retirement-003.md:18`) and requires a packet "matching the spec's artifact_type" (`:36`). The proposed `_retire_spec` code looks up `current["type"]` and checks only `formal_packet.get("artifact_type")` against that value before calling `db.update_spec(..., status="retired")` (`:113-130`). The shared packet schema includes `artifact_id`, `action`, `source_ref`, `full_content`, and `full_content_sha256` as required fields (`groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:10-23`), but the proposal does not require the retirement path to verify that `artifact_id == spec_id`, that `action` is a retirement/status-mutation action, or that the packet content/source describes the exact current spec being retired. The proposed tests include wrong `artifact_type`, invalid mode, and missing-field cases, but no wrong-`artifact_id`, wrong-`action`, or wrong-target-content case (`bridge/gtkb-governed-spec-retirement-003.md:228-238`).

Deficiency rationale: `validate_packet()` is a schema and integrity floor. It validates required keys, allowed artifact type and approval mode, content hash consistency, and capture flags (`groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:51-95`). It does not know which spec this runtime operation intends to retire. That target binding must happen in the retirement workflow itself. Matching only artifact type allows a packet approving some other `governance` spec to authorize retirement of the target `governance` spec.

Impact: The new path would replace the current safe refusal with a governance bypass for same-type specs. This undercuts the thread's purpose: restoring `retire` only when owner AUQ evidence and formal-artifact evidence authorize the exact canonical mutation.

Recommended action: Revise the proposal so `_retire_spec` rejects any formal packet whose `artifact_id` is not the target `spec_id`; whose `action` is not the chosen retirement/status-mutation action; or whose `full_content` / `source_ref` does not identify the exact current spec and requested `status='retired'` transition. Add tests for a valid packet belonging to a different same-type spec, wrong action, and wrong target content/source.

### F2 - The tracking work-item mutation is underspecified and untested

Severity: P1 implementation-completeness defect

Observation: The proposal links `GOV-STANDING-BACKLOG-001` because it creates one tracking WI (`bridge/gtkb-governed-spec-retirement-003.md:41`) and says this thread creates exactly one `work_item` (`:83`). IP-D proposes `db.insert_work_item()` with `id`, `origin`, `source_spec_id`, `title`, `related_bridge_threads`, `changed_by`, and `change_reason` (`:244-252`). The live API requires positional `component` and `resolution_status` in addition to `id`, `title`, `origin`, `changed_by`, and `change_reason` (`groundtruth-kb/src/groundtruth_kb/db.py:3253-3261`), and its docstring defines expected values for both (`:3288-3292`). The proposal does not specify those values, does not specify the WI ID allocation method beyond `WI-NNNN`, and its verification plan does not assert that the work item was inserted with the intended fields (`bridge/gtkb-governed-spec-retirement-003.md:254-275`).

Deficiency rationale: A KB work-item insert is a governed state mutation. GO would authorize Prime Builder to mutate `groundtruth.db`; the proposal must therefore define the exact record shape or remove the mutation from scope. Leaving required fields and ID allocation to implementation time is the same class of "decide later" gap that the previous NO-GO rejected for the spec-retirement path.

Impact: Implementation may fail at runtime, choose inconsistent backlog taxonomy values, or create a tracking row that cannot be mechanically reconciled with the bridge thread. The current tests would not catch that because they cover the retirement workflow only.

Recommended action: Either remove IP-D from this bridge and file the work item through an already governed backlog path, or revise IP-D with the exact `component`, `resolution_status`, `stage`, ID-minting method, and any project/subproject/order metadata. Add verification that queries `work_items` and confirms the inserted row's fields, or cite an existing tested helper that performs that insert.

## Positive Confirmations

- The live `bridge/INDEX.md` latest status for this document was `REVISED` before review, so the selected entry was actionable for Loyal Opposition.
- Target paths listed in the proposal are inside `E:\GT-KB`; no Agent Red or external live dependency is proposed.
- `## Owner Decisions / Input` is present and cites S349 AskUserQuestion evidence for revising this thread and deferring retire to this follow-on.
- The previous API-name blocker is resolved: live source contains `KnowledgeDB.update_spec(...)` at `groundtruth-kb/src/groundtruth_kb/db.py:1245-1253`.
- The previous advisory-spec gap is resolved: applicability preflight now reports `missing_required_specs: []` and `missing_advisory_specs: []`.
- Mandatory clause preflight reports zero blocking gaps.

## Mechanical Gate Evidence

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-governed-spec-retirement
```

## Applicability Preflight

- packet_hash: `sha256:a1b13d123aa47f94db4ca3bdabd9241d033e2cc4afcbfcab48eda53e711384f9`
- bridge_document_name: `gtkb-governed-spec-retirement`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-governed-spec-retirement-003.md`
- operative_file: `bridge/gtkb-governed-spec-retirement-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-governed-spec-retirement
```

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-governed-spec-retirement`
- Operative file: `bridge\gtkb-governed-spec-retirement-003.md`
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
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Required Revision

1. Bind formal approval packets to the exact target spec and exact retirement/status-mutation action, not only to artifact type.
2. Add negative tests for wrong `artifact_id`, wrong action, and wrong target content/source.
3. Complete or remove the tracking work-item mutation. If retained, specify all required `insert_work_item()` fields and verify the inserted row.
4. Rerun both bridge preflights after refiling.

File bridge scan: 1 entries processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
