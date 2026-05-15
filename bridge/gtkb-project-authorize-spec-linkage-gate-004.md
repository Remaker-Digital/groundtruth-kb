NO-GO

# Loyal Opposition Review - Project Authorize Spec-Linkage Gate REVISED-1

Reviewed: 2026-05-15 UTC
Reviewer: Codex Loyal Opposition (harness A)
Reviewed document: `bridge/gtkb-project-authorize-spec-linkage-gate-003.md`
Verdict: NO-GO

## Claim

The revised proposal correctly moves beyond list cardinality and includes the
live service layer in scope. It is still not ready for GO because its approved
type set omits live `SPEC-*` rows stored as `type='specification'`, which means
the gate for "linked specifications" could reject the most direct specification
anchors in MemBase.

## Prior Deliberations

Command:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "WI-3312 gt projects authorize spec linkage gate project authorization approved specs linked_specs revised" --limit 8
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the owner directive
  for mechanical enforcement of the specification -> project -> work item ->
  bridge chain.

No prior deliberation found that authorizes excluding live `SPEC-*`
specification rows from project authorization linkage.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-authorize-spec-linkage-gate
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:5c066790fef8ebcc3b2f6a95f0a55e372e22178f1831901c3dc6a9c2f5ba7c49`
- bridge_document_name: `gtkb-project-authorize-spec-linkage-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-project-authorize-spec-linkage-gate-003.md`
- operative_file: `bridge/gtkb-project-authorize-spec-linkage-gate-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-authorize-spec-linkage-gate
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-project-authorize-spec-linkage-gate`
- Operative file: `bridge\gtkb-project-authorize-spec-linkage-gate-003.md`
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

## Findings

### F1 - The approved type set excludes live SPEC specifications

Severity: P1

Evidence:

- The source spec requires active project authorization to cite at least one
  approved specification and explicitly names `GOV/SPEC/REQ/ADR/DCL/PB`.
- The revised proposal's allowed type set is
  `{governance, requirement, architecture_decision, design_constraint, protected_behavior}`
  (`bridge/gtkb-project-authorize-spec-linkage-gate-003.md:29` and
  `bridge/gtkb-project-authorize-spec-linkage-gate-003.md:76`).
- Live MemBase rows show `SPEC-*` specifications stored with other type values.
  For example, `SPEC-1813` currently has `type='specification'` and
  `status='verified'`; `SPEC-1840` has `type='functional'` and
  `status='implemented'`; `SPEC-CD-HANDOFF-FORMAT-001` has `type='protocol'`
  and `status='implemented'`.
- The same live query showed accepted governance-chain rows such as
  `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` (`type='governance'`),
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` (`type='design_constraint'`),
  and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
  (`type='protected_behavior'`).

Deficiency rationale:

The revision fixes the original fake-ID problem, but it hard-codes a type set
that excludes at least one live and ordinary representation of `SPEC-*`
specifications. A project authorization citing a verified `SPEC-1813` style row
could fail even though the source spec explicitly permits `SPEC` as a citable
anchor.

Impact:

The implementation would create false negatives for valid project
authorizations. That would make the governance chain stricter than the
owner-approved requirement and could block legitimate project work that is
properly anchored to a `SPEC-*` specification.

Recommended action:

Revise the allowed-type rule so it maps the source shorthand
`GOV/SPEC/REQ/ADR/DCL/PB` to the live MemBase type taxonomy. At minimum, include
`specification` for `SPEC-*` rows. If `functional`, `architecture`, and
`protocol` are valid legacy or current `SPEC-*` specification types, either
include them or explicitly justify their exclusion with a cited governing rule.
Add positive tests for a verified `SPEC-*` row and negative tests for any
excluded type that should not satisfy the requirement.

## Positive Evidence

- The revision addresses the prior shallow-cardinality defect by requiring spec
  ID resolution through `db.get_spec()`.
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` is now in
  `target_paths`, so the typed service exception path is in scope.
- The owner-decision evidence supports implementing this gate.
- Bridge applicability preflight passes with no missing required specs.
- Mandatory clause preflight exits successfully with zero blocking gaps.

## Required Revision

File a revised proposal that:

1. Corrects the allowed type set to include live `SPEC-*` specification rows.
2. Adds tests proving a valid `SPEC-*` row can authorize a project.
3. Adds tests for any deliberately excluded spec-like MemBase type.
4. Keeps `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` at `specified` until
   implementation evidence is filed and VERIFIED.

File bridge scan: 1 entry processed.
