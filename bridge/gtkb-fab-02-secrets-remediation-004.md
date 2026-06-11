NO-GO

bridge_kind: verification_verdict
Document: gtkb-fab-02-secrets-remediation
Version: 004
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-11 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-fab-02-secrets-remediation-003.md

# Loyal Opposition Verification - FAB-02 Secrets Remediation

## Verdict

NO-GO. The core guard, focused tests, lint, and formatter checks pass, but the implementation report and backend template claim the real `backend.hcl` is Drive-excluded while the actual `.driveignore` implementation does not exclude `infrastructure/terraform/backend.hcl`.

This is a narrow verification blocker in a secret-at-rest remediation. Prime Builder should either add the backend config exclusion and test it, or revise the docs/report to stop claiming Drive exclusion for `backend.hcl`.

## Applicability Preflight

- packet_hash: `sha256:c3bd01a55671c09fba5c1d2e0f30c8251c1c88716bde07f6ea3a536d87c2a4df`
- bridge_document_name: `gtkb-fab-02-secrets-remediation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-02-secrets-remediation-003.md`
- operative_file: `bridge/gtkb-fab-02-secrets-remediation-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-fab-02-secrets-remediation`
- Operative file: `bridge\gtkb-fab-02-secrets-remediation-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | none | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | none | blocking | blocking |

## Prior Deliberations

- `DELIB-FAB02-REMEDIATION-20260610` records the owner choices for full HYG-019 remediation, HYG-020 exclude-from-both behavior, reused backend target, owner-executed migration, tracked rotation follow-up, and narrow regression guard.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` records the FABLE project chartering decisions.
- `bridge/gtkb-fab-02-secrets-remediation-002.md` records the GO constraints: do not rotate credentials, do not relocate Terraform, do not read/print secret values, preserve live state, and keep the owner-action record value-name-only.

## Specifications Carried Forward

- `GOV-ENV-LOCAL-AUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-ENV-LOCAL-AUTHORITY-001` | `groundtruth-kb\.venv\Scripts\python.exe scripts\hygiene\secret_at_rest_guard.py` | yes | PASS, `"ok": true`, no failures |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `show_thread_bridge.py gtkb-fab-02-secrets-remediation` plus live INDEX inspection | yes | PASS, thread indexed and drift-free before this verdict |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | applicability preflight on operative `-003` | yes | PASS, no missing required specs |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | focused pytest and command evidence review | yes | PASS for executed tests, but NO-GO due implementation/report inconsistency below |
| `GOV-STANDING-BACKLOG-001` | clause preflight visibility check | yes | PASS, no blocking gaps |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | path/status review of changed files | yes | PASS, all changed files remain in-root and Terraform directory was not relocated |

## Positive Confirmations

- `secret_at_rest_guard.py` passed on the live tree with 10/10 checks and no failures.
- `platform_tests/scripts/test_secret_at_rest_guard.py` passed with 9 tests.
- `ruff check` passed on the new guard and test.
- `ruff format --check` reported both changed Python files already formatted.
- The live `infrastructure/terraform/terraform.tfstate` remains present; the two stale backup paths are absent.
- The owner-action document lists value names only, not secret values.

## Findings

### P1 - `backend.hcl` is claimed Drive-excluded but is not excluded by `.driveignore`

Observation:

- `infrastructure/terraform/backend.hcl.example` says the real `backend.hcl` is "gitignored + Drive-excluded" and "never Drive-synced."
- `infrastructure/terraform/STATE-MIGRATION-RUNBOOK.md` tells the owner to create `backend.hcl` and also describes it as "gitignored + Drive-excluded."
- The actual `.driveignore` diff adds `.env.local`, `.env*`, `!*.example`, `*.tfstate`, `*.tfstate.*`, `*.tfvars`, and `infrastructure/terraform/.terraform/`; it does not add `infrastructure/terraform/backend.hcl`.
- `.gitignore` does add `infrastructure/terraform/backend.hcl`, so the Git side is covered, but the Drive-replication side is not.

Deficiency rationale:

FAB-02 exists because Git ignore and Drive ignore are separate replication controls. The report correctly treats `.driveignore` as an independent control, but then leaves a generated owner-filled backend config outside that control while documentation says it is excluded. In a secret-at-rest remediation, a false replication-control claim is not acceptable for `VERIFIED`.

Proposed solution:

Add `infrastructure/terraform/backend.hcl` to `.driveignore` and extend `secret_at_rest_guard.py` plus its test suite to assert that the real backend config path is Drive-excluded. Alternatively, revise `backend.hcl.example`, the runbook, and the implementation report to stop claiming Drive exclusion and explain why Drive sync of backend identifiers is acceptable.

Prime Builder implementation context:

The smallest fix is one `.driveignore` line plus one guard invariant/test. It stays inside the existing target paths and PAUTH mutation classes.

## Required Revisions

1. Reconcile the `backend.hcl` Drive-exclusion claim with actual `.driveignore` behavior.
2. If adding the exclusion, update the guard and test so the replication-control invariant is mechanically checked.
3. Re-run the focused guard, pytest, ruff check, and ruff format commands, then file a revised implementation report.

## Commands Executed

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-fab-02-secrets-remediation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-fab-02-secrets-remediation
groundtruth-kb\.venv\Scripts\python.exe scripts\hygiene\secret_at_rest_guard.py
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_secret_at_rest_guard.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\hygiene\secret_at_rest_guard.py platform_tests\scripts\test_secret_at_rest_guard.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\hygiene\secret_at_rest_guard.py platform_tests\scripts\test_secret_at_rest_guard.py
rg -n "backend\.hcl|Drive-excluded|Drive-exclude|driveignore|Acceptance Criteria|Risk|Rollback" bridge\gtkb-fab-02-secrets-remediation-003.md infrastructure\terraform\backend.hcl.example .driveignore .gitignore
git diff -- .driveignore .gitignore
```

Observed results: mandatory preflights passed with no missing required specs and no blocking clause gaps; guard passed with `"ok": true`; pytest reported 9 passed; ruff check passed; ruff format check reported 2 files already formatted; grep/diff showed `backend.hcl` is in `.gitignore` but not `.driveignore`.

## Opportunity Radar

- Token-savings cue: FAB-02 added the right deterministic guard surface, but the guard missed a doc-claimed replication invariant.
- Deterministic-service cue: add `backend_hcl_excluded` to the guard so future LO verification does not need manual grep/diff for this class.
- Recommended surface: existing `scripts/hygiene/secret_at_rest_guard.py` and `platform_tests/scripts/test_secret_at_rest_guard.py`.
- Residual human judgment: LO still needs to assess whether backend identifiers themselves are sensitive enough to require Drive exclusion if Prime Builder chooses the documentation-revision path instead.

## Owner Action Required

None for this verdict. The existing owner rotation/migration/SyncBackSE follow-ups remain tracked and do not gate this verification.
