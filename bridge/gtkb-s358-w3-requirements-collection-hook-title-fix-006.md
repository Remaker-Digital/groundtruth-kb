GO

# Loyal Opposition Review - W3 GOV-REQUIREMENTS-COLLECTION-HOOK-001 Title Fix REVISED-2

Document: `gtkb-s358-w3-requirements-collection-hook-title-fix`
Reviewed proposal: `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-005.md`
Reviewer: Codex, durable harness A, Loyal Opposition
Date: 2026-05-18 UTC
Verdict: GO

## Summary

The `-005` revision closes the prior blocking defects. It keeps the corrected
authorization envelope (`groundtruth.db` plus the formal-artifact
approval-packet glob), replaces the invalid decision-evidence citation with
retrievable Deliberation Archive records, and preserves the narrow title-only
scope.

This GO authorizes only the proposal's stated implementation scope. It does
not pre-approve the required implementation-time formal-artifact approval
packet for the GOV v4 supersession.

## Applicability Preflight

- packet_hash: `sha256:df3fd4d2df7af6355056d19a151e9a3b02c2f334797d2ebae8bee93dfbfa49c6`
- missing_required_specs: []

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s358-w3-requirements-collection-hook-title-fix`

```text
## Applicability Preflight

- packet_hash: `sha256:df3fd4d2df7af6355056d19a151e9a3b02c2f334797d2ebae8bee93dfbfa49c6`
- bridge_document_name: `gtkb-s358-w3-requirements-collection-hook-title-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-005.md`
- operative_file: `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified |
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
- Operative file: `bridge\gtkb-s358-w3-requirements-collection-hook-title-fix-005.md`
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

I performed the required Deliberation Archive review using the repo-native
`gt deliberations` surface and read-only MemBase inspection.

The semantic search command below returned no direct hits:

```text
UV_CACHE_DIR=E:\GT-KB\.uv-cache uv run --project groundtruth-kb python -m groundtruth_kb deliberations search "requirements collection hook LLM classifier retrieval augmented regex gate title fix" --limit 10
```

Direct read-only inspection of `current_deliberations` and LIKE-based search
found the relevant records:

- `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` exists and records
  the owner decision authorizing W3 as a metadata-only v4 title fix for
  `GOV-REQUIREMENTS-COLLECTION-HOOK-001`.
- `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` exists
  and records the earlier LLM-classifier / retrieval-augmented design whose
  title-level remnant W3 removes.
- `DELIB-1701` exists as the Loyal Opposition GO for the earlier requirements
  collection hook revised proposal and records the no-LLM regex-gate direction.
- `DELIB-1941`, `DELIB-1702`, `DELIB-1703`, and `DELIB-1704` preserve related
  requirements-collection hook bridge history.

The invalid `DELIB-S332-NO-LLM-API-PARALLEL-USE-DIRECTIVE` token still appears
in `-005` only as a description of the prior `-004` NO-GO defect and the stale
hook-header drift. It is no longer used as operative decision evidence. No
prior deliberation I reviewed contradicts the metadata-only title correction.

## Review Checks

- Live `bridge/INDEX.md` was read before this verdict; the selected document
  was still latest `REVISED` at
  `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-005.md`.
- `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-005.md:16`
  includes both `groundtruth.db` and
  `.groundtruth/formal-artifact-approvals/*-gov-requirements-collection-hook-001.json`
  in `target_paths`, closing the prior authorization-envelope finding.
- `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-005.md:65`
  cites retrievable prior deliberations and documents the removal of the
  nonexistent DELIB citation as decision evidence.
- `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-005.md:75`
  includes a substantive `Owner Decisions / Input` section and keeps the
  implementation-time formal-artifact approval requirement explicit.
- `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-005.md:80`
  states `Existing requirements sufficient`.
- `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-005.md:106`
  provides a specification-derived verification plan based on MemBase field
  inspection and formal-artifact approval-packet evidence.
- Read-only MemBase inspection confirms current
  `GOV-REQUIREMENTS-COLLECTION-HOOK-001` is version 3, status `verified`, and
  its current title still contains the stale
  `(LLM classification + retrieval-augmented options)` parenthetical.
- Read-only MemBase inspection confirms `SPEC-AUQ-NO-LLM-CLASSIFIER-001`,
  `SPEC-AUQ-POLICY-ENGINE-001`, `GOV-ARTIFACT-APPROVAL-001`,
  `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`, and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` exist.
- The cited project authorization is active, tied to
  `PROJECT-GTKB-GOVERNANCE-CORRECTION-S358`, and includes `WI-3367`; the
  `PROJECT-GTKB-GOVERNANCE-CORRECTION-S358` -> `WI-3367` membership is active.
- Read-only inspection of `.claude/hooks/spec-classifier.py` supports the
  proposal's implementation premise: the hook imports only `json`, `re`, and
  `sys`; the only LLM/retrieval references are historical rationale/header text
  and the module docstring says the hook is a regex gate.

## Findings

No blocking findings.

## Prime Builder Implementation Constraints

Proceed only within the approved `target_paths` and the title-only IP-1 scope:
insert a version 4 of `GOV-REQUIREMENTS-COLLECTION-HOOK-001` into
`groundtruth.db` and create the matching formal-artifact approval packet under
`.groundtruth/formal-artifact-approvals/`. Do not change
`.claude/hooks/spec-classifier.py`, other source/configuration/test files, or
the W1/W2/W4 surfaces under this GO.

Before inserting the GOV v4 row, present and receive the required owner approval
for the formal-artifact approval packet. The post-implementation report must
carry forward the proposal's specification links, cite the approval-packet path,
and include exact read-only MemBase inspection proving:

- v4 exists;
- v4 title equals the specified title without the stale parenthetical;
- v4 body and non-title fields match v3;
- v3 remains preserved in the append-only history.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
