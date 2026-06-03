VERIFIED

bridge_kind: verification_verdict
Document: gtkb-governance-adoption-doctor-check
Version: 008
Author: Loyal Opposition (Antigravity, harness C)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-governance-adoption-doctor-check-007.md
Recommended commit type: feat:

## Verdict

VERIFIED.

The implementation report and changes satisfy the approved implementation proposal and successfully resolve all requirements. The managed-artifact drift check is integrated into `gt project doctor`. It aggregates drift in hook templates, settings hook registrations, and gitignore patterns, surfacing warning or error states depending on the adopter's divergence policies. Testing is comprehensive and there are no regressions.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:0a00417197f6320be2dcd09cda94a77a701c40fe421469fbb6c78e8dcc66ae25`
- bridge_document_name: `gtkb-governance-adoption-doctor-check`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-governance-adoption-doctor-check-007.md`
- operative_file: `bridge/gtkb-governance-adoption-doctor-check-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-governance-adoption-doctor-check`
- Operative file: `bridge\gtkb-governance-adoption-doctor-check-007.md`
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
```

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner/project authorization for GTKB-GOV-003.

## Specifications Carried Forward

- `GOV-GTKB-ADOPTION-ENFORCEMENT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001` | `pytest groundtruth-kb/tests/test_doctor_adoption_drift.py` | yes | PASS; 8 tests covered all scenarios of drift |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `pytest groundtruth-kb/tests/test_doctor.py` | yes | PASS; 37 tests verifying that all doctor tools check correctly |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-governance-adoption-doctor-check` | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m ruff check groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\tests\test_doctor_adoption_drift.py` | yes | PASS; clean format and checks |

## Positive Confirmations

- Verified that `_check_managed_artifact_drift` checks for all drift types (file changes, settings mismatch, gitignore missing) and integrates cleanly with other doctor tools.
- Verified that all unit tests run and pass without regressions.
- Checked that ruff check and format check are clean.

## Commands Executed

- `$env:TMP='...'; $env:TEMP='...'; groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_doctor_adoption_drift.py -q --tb=short`
- `$env:TMP='...'; $env:TEMP='...'; groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_doctor.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\tests\test_doctor_adoption_drift.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\tests\test_doctor_adoption_drift.py`

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
