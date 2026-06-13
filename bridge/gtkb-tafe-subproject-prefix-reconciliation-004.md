VERIFIED

bridge_kind: verification_verdict
Document: gtkb-tafe-subproject-prefix-reconciliation
Version: 004
Author: Loyal Opposition (Antigravity, harness C)
Date: 2026-06-13 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-tafe-subproject-prefix-reconciliation-003.md
Recommended commit type: fix:

## Applicability Preflight

- packet_hash: `sha256:4b063e479b639d2928dfc8121a4641fb51d7a02940612f39694a8a0f9e751471`
- bridge_document_name: `gtkb-tafe-subproject-prefix-reconciliation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-tafe-subproject-prefix-reconciliation-003.md`
- operative_file: `bridge/gtkb-tafe-subproject-prefix-reconciliation-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-tafe-subproject-prefix-reconciliation`
- Operative file: `bridge\gtkb-tafe-subproject-prefix-reconciliation-003.md`
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

- `DELIB-2532` - Bridge thread: gtkb-phantom-project-prefix-reconciliation
- `DELIB-2508` - Owner AUQ Answer: Accept 8th Reconciliation Link
- `DELIB-2506` - Owner AUQ Answer: Re-link to Retired Canonical
- `DELIB-2505` - Owner Directive: NOT DEFERRED Phantom PROJECT-PROJECT-* Reconciliation

## Specifications Carried Forward

- `GOV-STANDING-BACKLOG-001` - WI-4511 backlog authority.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge index/file authority remains canonical.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project implementation authorization.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic services.
- `SPEC-TAFE-R7` - MemBase project/backlog state authority.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test verification.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `SPEC-TAFE-R7` | `test_canonical_id_derivation_strips_exactly_one_prefix` | yes | PASS |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | `test_project_scoped_plan_detects_tafe_subproject_phantom_only`, `test_project_scoped_apply_reconciles_tafe_without_touching_global_phantoms` | yes | PASS |
| `GOV-STANDING-BACKLOG-001` | `DB read-back verification: tafe_phantom_count=8, tafe_phantom_active_memberships=0, tafe_canonical_active_memberships=24` | yes | PASS |

## Positive Confirmations

- Subproject prefix reconciliation service generalised structural doubled prefix segments and scoped project filters cleanly.
- `gt projects reconcile-doubled-prefix --project PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE` was executed successfully on `groundtruth.db`, retiring 8 phantom sub-projects and re-linking 24 memberships.
- Idempotence is verified: a second run does not write anything.
- Unit tests pass cleanly.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-tafe-subproject-prefix-reconciliation`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-tafe-subproject-prefix-reconciliation`
- `python -m pytest platform_tests/scripts/test_cli_projects_reconcile.py -q --tb=short`

## Owner Action Required

No owner action is required.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
