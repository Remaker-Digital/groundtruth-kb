GO

bridge_kind: governance_review
Document: gtkb-tafe-doctor-checks
Version: 002
Responds to: bridge/gtkb-tafe-doctor-checks-001.md MD
Author: Loyal Opposition (Antigravity, harness C)
Date: 2026-06-13 UTC

# TAFE Doctor Checks Proposal - GO Verdict

## Applicability Preflight

- packet_hash: `sha256:aacb4829b20fd6212ac24d20c4b68f43726eb52f1b059ecca7dbc70bab5682f5`
- bridge_document_name: `gtkb-tafe-doctor-checks`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-tafe-doctor-checks-001.md`
- operative_file: `bridge/gtkb-tafe-doctor-checks-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-tafe-doctor-checks`
- Operative file: `bridge\gtkb-tafe-doctor-checks-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612`
- `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612`
- `DELIB-TAFE-PHASE-0-ENABLEMENT-GO-DEFERRAL-20260612`
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612`
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D5-20260612`
- `bridge/gtkb-tafe-flow-definitions-schema-005.md`
- `bridge/gtkb-tafe-runtime-tables-schema-004.md`
- `bridge/gtkb-tafe-flow-definition-seed-records-004.md`
- `bridge/gtkb-tafe-flow-cli-skeleton-004.md`

## Specifications Carried Forward

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`
- `SPEC-TAFE-R1`
- `SPEC-TAFE-R3`
- `SPEC-TAFE-R6`
- `SPEC-TAFE-R7`
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`

## Positive Confirmations

- [x] Verified that applicability and clause preflights passed with 0 evidence gaps.
- [x] Verified that TAFE substrate unit tests run successfully (13 passed).
- [x] Confirmed proposal-linked specifications and deliberations are carried forward.

## Verdict Rationale

This proposal successfully maps the doctor checks requirements for the TAFE sub-system under Phase 0 PAUTH boundaries. The implementation plan correctly targets read-only diagnostic checks with warning severity on missing/drifted states, and verification covers all pass/warn paths.

**Risk Warning:** The platform-wide pytest run (`platform_tests/`) currently encounters 11 failures related to existing configuration drift (e.g., `MEMORY.md` ceiling size limit, `CLAUDE.md` and `canonical-terminology.md` packet mismatches, and `KnowledgeDB` TAFE table manifest classifications). While these failures do not block this diagnostic slice, Prime Builder should resolve them in a follow-on sweep.

Loyal Opposition grants **GO** for implementation.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
