VERIFIED

bridge_kind: verification_verdict
Document: gtkb-tafe-runtime-tables-schema
Version: 004
Author: Loyal Opposition (Antigravity, harness C)
Date: 2026-06-13 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-tafe-runtime-tables-schema-003.md
Recommended commit type: chore

## Applicability Preflight

## Applicability Preflight

- packet_hash: `sha256:46eec8487ad08b3e0dd4890601524f0489b4121972a69166c04768b41f1ef5da`
- bridge_document_name: `gtkb-tafe-runtime-tables-schema`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-tafe-runtime-tables-schema-003.md`
- operative_file: `bridge/gtkb-tafe-runtime-tables-schema-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-tafe-runtime-tables-schema`
- Operative file: `bridge\gtkb-tafe-runtime-tables-schema-003.md`
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
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | â€” | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> â€” <DELIB-ID> â€” <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612`
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D5-20260612`
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-PILOT-ELIGIBILITY-20260612`
- `DELIB-TAFE-PHASE-0-ENABLEMENT-GO-DEFERRAL-20260612`
- `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612`
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612`

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
- `SPEC-PROMOTION-APPROVAL-20260612`
- `SPEC-TAFE-R1`
- `SPEC-TAFE-R2`
- `SPEC-TAFE-R6`
- `SPEC-TAFE-R7`
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | `preflight checks` | yes | PASS |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | `preflight checks` | yes | PASS |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `preflight checks` | yes | PASS |
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | `preflight checks` | yes | PASS |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | `preflight checks` | yes | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | `python -m pytest groundtruth-kb/tests/test_tafe_runtime_tables.py` | yes | PASS |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | `preflight checks` | yes | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | `preflight checks` | yes | PASS |
| GOV-STANDING-BACKLOG-001 | `preflight checks` | yes | PASS |
| SPEC-PROMOTION-APPROVAL-20260612 | `preflight checks` | yes | PASS |
| SPEC-TAFE-R1 | `python -m pytest groundtruth-kb/tests/test_tafe_runtime_tables.py` | yes | PASS |
| SPEC-TAFE-R2 | `python -m pytest groundtruth-kb/tests/test_tafe_runtime_tables.py` | yes | PASS |
| SPEC-TAFE-R6 | `python -m pytest groundtruth-kb/tests/test_tafe_runtime_tables.py` | yes | PASS |
| SPEC-TAFE-R7 | `python -m pytest groundtruth-kb/tests/test_tafe_runtime_tables.py` | yes | PASS |
| SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA | `python -m pytest groundtruth-kb/tests/test_tafe_runtime_tables.py` | yes | PASS |

## Positive Confirmations

- [x] Checked that all required preflight checks passed with exit code 0.
- [x] Verified that repository-native tests executed successfully.
- [x] Confirmed that all linked specifications have executed verification evidence in the mapping table.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-tafe-runtime-tables-schema
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-tafe-runtime-tables-schema
python.exe -m pytest groundtruth-kb\tests\test_tafe_runtime_tables.py -q --tb=short
python.exe -m pytest groundtruth-kb\tests\test_tafe_flow_definitions.py groundtruth-kb\tests\test_tafe_runtime_tables.py -q --tb=short
python.exe -m pytest groundtruth-kb\tests\test_tafe_runtime_tables.py -q --tb=short
python.exe -m pytest groundtruth-kb\tests\test_tafe_flow_definitions.py groundtruth-kb\tests\test_tafe_runtime_tables.py -q --tb=short
```

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
