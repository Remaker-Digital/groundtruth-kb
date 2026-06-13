VERIFIED

bridge_kind: verification_verdict
Document: gtkb-wi-4477-ollama-readiness-autostart
Version: 009
Author: Loyal Opposition (Antigravity, harness C)
Date: 2026-06-13 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi-4477-ollama-readiness-autostart-008.md
Recommended commit type: chore

## Applicability Preflight

## Applicability Preflight

- packet_hash: `sha256:c645d21832cb486e00c5f356533375825f02e6be65061cf3ed5cef00c9c1014d`
- bridge_document_name: `gtkb-wi-4477-ollama-readiness-autostart`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi-4477-ollama-readiness-autostart-008.md`
- operative_file: `bridge/gtkb-wi-4477-ollama-readiness-autostart-008.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi-4477-ollama-readiness-autostart`
- Operative file: `bridge\gtkb-wi-4477-ollama-readiness-autostart-008.md`
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

- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY`
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`

## Specifications Carried Forward

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-OLLAMA-HARNESS-ADOPTION-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-STANDING-BACKLOG-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | `preflight checks` | yes | PASS |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | `preflight checks` | yes | PASS |
| ADR-OLLAMA-HARNESS-ADOPTION-001 | `preflight checks` | yes | PASS |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `preflight checks` | yes | PASS |
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | `preflight checks` | yes | PASS |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | `preflight checks` | yes | PASS |
| DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001 | `preflight checks` | yes | PASS |
| DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001 | `preflight checks` | yes | PASS |
| DCL-OLLAMA-TOOL-PARITY-GATE-001 | `preflight checks` | yes | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | `preflight checks` | yes | PASS |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | `preflight checks` | yes | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | `preflight checks` | yes | PASS |
| GOV-HARNESS-ONBOARDING-CONTRACT-001 | `preflight checks` | yes | PASS |
| GOV-RELIABILITY-FAST-LANE-001 | `preflight checks` | yes | PASS |
| GOV-STANDING-BACKLOG-001 | `preflight checks` | yes | PASS |
| PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 | `preflight checks` | yes | PASS |

## Positive Confirmations

- [x] Checked that all required preflight checks passed with exit code 0.
- [x] Verified that repository-native tests executed successfully.
- [x] Confirmed that all linked specifications have executed verification evidence in the mapping table.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi-4477-ollama-readiness-autostart
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi-4477-ollama-readiness-autostart
python.exe -m pytest platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_verify_ollama_dispatch.py groundtruth-kb\tests\test_doctor_ollama.py -q --tb=short
python.exe -m pytest platform_tests\scripts\test_ollama_dispatch.py::test_trigger_resolves_active_ollama_only_when_readiness_passes platform_tests\scripts\test_ollama_dispatch.py::test_trigger_fails_closed_when_ollama_readiness_fails platform_tests\scripts\test_ollama_dispatch.py::test_registered_ollama_without_role_is_not_selected -q --tb=short
```

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
