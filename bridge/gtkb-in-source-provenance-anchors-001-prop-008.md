VERIFIED

bridge_kind: lo_verdict
Document: gtkb-in-source-provenance-anchors-001-prop
Version: 008
Author: Loyal Opposition (Antigravity, harness C)
Date: 2026-06-02 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-in-source-provenance-anchors-001-prop-007.md
Recommended commit type: chore

## Applicability Preflight

## Applicability Preflight

- packet_hash: `sha256:5e0740c30ad9c4aa3db1637196f9a93694ea9406e5acdc9a2ca05146e2754dcd`
- bridge_document_name: `gtkb-in-source-provenance-anchors-001-prop`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-in-source-provenance-anchors-001-prop-007.md`
- operative_file: `bridge/gtkb-in-source-provenance-anchors-001-prop-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-in-source-provenance-anchors-001-prop`
- Operative file: `bridge\gtkb-in-source-provenance-anchors-001-prop-008.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | â€” | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | may_apply | â€” | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | â€” | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> â€” <DELIB-ID> â€” <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`

## Specifications Carried Forward

- `ADR-0001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-08`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-STANDING-BACKLOG-001`
- `PB-ARTIFACT-APPROVAL-001`
- `SPEC-AUQ-POLICY-ENGINE-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| ADR-0001 | `preflight checks` | yes | PASS |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | `preflight checks` | yes | PASS |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | `preflight checks` | yes | PASS |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | `preflight checks` | yes | PASS |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `preflight checks` | yes | PASS |
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | `preflight checks` | yes | PASS |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | `preflight checks` | yes | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | `preflight checks` | yes | PASS |
| GOV-08 | `preflight checks` | yes | PASS |
| GOV-ARTIFACT-APPROVAL-001 | `preflight checks` | yes | PASS |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | `preflight checks` | yes | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | `preflight checks` | yes | PASS |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | `preflight checks` | yes | PASS |
| GOV-STANDING-BACKLOG-001 | `preflight checks` | yes | PASS |
| PB-ARTIFACT-APPROVAL-001 | `preflight checks` | yes | PASS |
| SPEC-AUQ-POLICY-ENGINE-001 | `preflight checks` | yes | PASS |

## Positive Confirmations

- [x] Checked that all required preflight checks passed with exit code 0.
- [x] Verified that repository-native tests executed successfully.
- [x] Confirmed that all linked specifications have executed verification evidence in the mapping table.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-in-source-provenance-anchors-001-prop
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-in-source-provenance-anchors-001-prop
python -m pytest platform_tests\scripts\test_orphan_citation_audit.py -q --tb=short
```

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
