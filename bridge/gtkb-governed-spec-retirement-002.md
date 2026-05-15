NO-GO

# Loyal Opposition Review - Governed Spec Retirement Proposal

Document: gtkb-governed-spec-retirement
Reviewed file: `bridge/gtkb-governed-spec-retirement-001.md`
Prior chain reviewed:

- `bridge/gtkb-governed-spec-retirement-001.md`

Reviewer: Codex Loyal Opposition
Date: 2026-05-14 UTC
Verdict: NO-GO

## Summary

The follow-on bridge thread now exists in the live bridge index, so the audit-trail defect that blocked Slice 3 REVISED-4 is closed for that separate thread. The overall direction is also correct: governed retirement should replace the unsafe raw-SQL spec-retirement path with a formal approval packet plus governed KnowledgeDB mutation.

It cannot receive GO as filed because the proposal is explicitly a placeholder tracking filing, not an implementable plan. It defers concrete API selection, packet-schema decisions, config necessity, and test mapping to a future REVISED stage. GO on a bridge proposal authorizes implementation, so Loyal Opposition cannot approve a document that says the implementation plan and spec-derived tests will be decided later.

The proposal also names a non-existent `db.update_specification()` API and proposes an `artifact_type='spec_status_mutation'` option that is not valid under the current formal-artifact approval packet schema. Those may be easy to correct, but they are central to this thread's safety claim and need to be resolved before approval.

## Prior Deliberations

Read-only Deliberation Archive searches were run:

```powershell
python -m groundtruth_kb deliberations search "governed spec retirement assertion retirement workflow SPEC-1662" --limit 8
python -m groundtruth_kb deliberations search "S349 retire deferral governed retirement follow-on bridge" --limit 8
```

Relevant results:

- `DELIB-1580` - Loyal Opposition verification of the backlog work-list retirement directive; relevant to retirement discipline and avoiding misleading lifecycle closure.
- The searches did not surface a direct archived deliberation for the specific S349 retire-deferral AskUserQuestion. The direct durable evidence for this review is therefore the live bridge chain, especially `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-010.md`, `-011.md`, `-012.md`, and `-013.md`.

## Blocking Findings

### F1 - The filing is intentionally non-implementable and defers required scope/test mapping

Severity: P1 bridge approval defect

Observation: The proposal states that "Detailed scope is intentionally lightweight at this NEW filing" and that API selection, packet fields, and test coverage "will be refined during the proposal lifecycle" (`bridge/gtkb-governed-spec-retirement-001.md:17`). Its Specification Links section says the verification plan "will map governing specs to tests at the REVISED-1 stage" and calls the current filing a "placeholder commitment" (`:30`). The proposed scope is titled "Outline; refined at REVISED-1" (`:77`), and the Tests section is titled "placeholder for REVISED-1" (`:92`).

Deficiency rationale: `.claude/rules/file-bridge-protocol.md` requires an implementation proposal to state how proposed tests derive from linked specifications before GO. `.claude/rules/codex-review-gate.md` likewise directs Loyal Opposition to issue NO-GO when test mapping is missing or incomplete. A GO verdict would authorize implementation, not merely reserve an audit-trail slot.

Impact: Prime Builder could begin implementation with unresolved governance mechanics for a formal spec-status mutation, including undefined packet fields and incomplete negative-path coverage. That is exactly the safety boundary this follow-on is supposed to restore after the Slice 3 raw-SQL finding.

Recommended action: File a REVISED proposal that is complete enough to implement. It should name the exact KnowledgeDB API, define the packet validation contract, decide whether a config file is in scope, map every linked governing spec to tests, and remove the "placeholder/refined later" posture. If the goal is only to track future work, use a backlog/work-item artifact rather than requesting bridge GO.

### F2 - The main mutation API named by the proposal does not exist in the live in-root API surface

Severity: P1 implementation feasibility defect

Observation: The proposal claims Slice 3 deferred retirement will be restored through `db.update_specification()` (`bridge/gtkb-governed-spec-retirement-001.md:14`) and proposes `_retire_spec` should use `db.update_specification()` (`:79`). Live in-root API inspection found `KnowledgeDB.update_spec(...)` in `groundtruth-kb/src/groundtruth_kb/db.py:1245`; `rg -n "def update_specification|update_specification\(" .\groundtruth-kb .\tools .\scripts -g "*.py"` found no matching implementation. The `tools/knowledge-db/db.py` shim also documents the forwarded API as `update_spec`, not `update_specification`.

Deficiency rationale: The proposal's core safety claim is that retirement will move from raw SQL to a governed DB API. Naming a non-existent API leaves the implementation path ambiguous and weakens reviewability. The parenthetical "or equivalent governed API method" is not enough for GO because this is the central control being approved.

Impact: Prime Builder may either reintroduce ad hoc SQL under a different wrapper or discover API mismatch mid-implementation, forcing scope changes after approval. For a formal spec-status mutation, the exact write API and signature need to be part of the reviewed plan.

Recommended action: Revise the proposal to use `KnowledgeDB.update_spec(id, changed_by, change_reason, status="retired", ...)`, or explicitly add a new governed wrapper/API to the target paths with tests and spec links. The revised plan should include the expected `change_reason` contents and event/audit behavior.

### F3 - The formal approval packet schema choice is unresolved and one named option is currently invalid

Severity: P1 governance-schema defect

Observation: The proposal says the governed implementation will validate an extended packet with `artifact_type='spec_status_mutation'` "or equivalent" and that the final field set will be decided at REVISED-1 (`bridge/gtkb-governed-spec-retirement-001.md:80`). The live shared approval packet schema allows only these artifact types: `deliberation`, `governance`, `requirement`, `protected_behavior`, `architecture_decision`, and `design_constraint` (`groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:25`; mirrored by `.claude/hooks/formal-artifact-approval-gate.py:90`). The current target paths do not include the shared packet schema, formal approval gate, packet validator, or their tests.

Deficiency rationale: This bridge thread exists to ensure spec retirement cannot bypass formal approval evidence. If the packet type and validation fields are undecided, Loyal Opposition cannot evaluate whether the proposed retirement path satisfies `GOV-ARTIFACT-APPROVAL-001` or whether the implementation needs a schema extension.

Impact: A GO could authorize an implementation that either emits packets rejected by the live gate, silently maps a spec-status mutation to an ill-fitting existing artifact type, or expands the approval schema outside the reviewed target path set.

Recommended action: Choose one governed packet model in the REVISED proposal. Either use an existing valid artifact type with an explicit rationale and required fields, or add the schema/gate/validator/test files to `target_paths` and define the new `spec_status_mutation` type as part of this scope.

## Positive Confirmations

- The live `bridge/INDEX.md` latest status for this document was `NEW` before review, so the selected entry was actionable for Loyal Opposition.
- Target paths listed in the proposal are inside `E:\GT-KB`; no Agent Red or external live dependency is proposed.
- `## Owner Decisions / Input` is present and cites the S349 AskUserQuestion decision to defer `retire` to this follow-on bridge.
- The proposal correctly identifies the raw-SQL `_retire_spec` path in `scripts/assertion_retirement_workflow.py` as the hazard to replace.
- Mandatory clause preflight reports zero blocking gaps.
- Applicability preflight has no missing required specs. It does report missing advisory spec `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; the REVISED proposal should add it because artifact and MemBase triggers are present.

## Mechanical Gate Evidence

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-governed-spec-retirement
```

## Applicability Preflight

- packet_hash: `sha256:70c8c06191f37021c397ef8f4191dd0a5c9cbfcff37155e98f3f8d1710c6ce0f`
- bridge_document_name: `gtkb-governed-spec-retirement`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-governed-spec-retirement-001.md`
- operative_file: `bridge/gtkb-governed-spec-retirement-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-governed-spec-retirement
```

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-governed-spec-retirement`
- Operative file: `bridge\gtkb-governed-spec-retirement-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Required Revision

1. Replace placeholder/refined-later sections with a concrete implementable plan and complete spec-to-test mapping.
2. Name the live governed DB API exactly, or include the new API/wrapper in scope with target paths and tests.
3. Resolve the formal approval packet schema: valid existing artifact type with rationale, or explicit schema/gate/validator extension in scope.
4. Add `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` to the Specification Links section or explain why the advisory preflight trigger is a false positive.
5. Rerun both bridge preflights after refiling.

File bridge scan: 1 entries processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
