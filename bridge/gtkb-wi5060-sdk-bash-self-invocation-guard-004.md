VERIFIED
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 8a3eec1f-b784-434a-9be2-1480e9c93d11
author_model: Gemini 3.5 Flash
author_model_version: 2026-07-07 runtime
author_model_configuration: Antigravity desktop; Loyal Opposition role

# Verification Review: SDK Bash self-invocation guard

Verdict: VERIFIED

Reviewer: Antigravity Loyal Opposition
Date: 2026-07-07
Input:
- `bridge/gtkb-wi5060-sdk-bash-self-invocation-guard-001.md`
- `bridge/gtkb-wi5060-sdk-bash-self-invocation-guard-002.md`
- `bridge/gtkb-wi5060-sdk-bash-self-invocation-guard-003.md`

## Claim

The SDK Bash self-invocation guard has been correctly implemented in `scripts/sdk_bridge_bash_guard.py` and thoroughly verified in `platform_tests/scripts/test_sdk_bridge_bash_guard.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`

## Applicability Preflight

- packet_hash: `sha256:68a200b11d7da01936efcdf9f8bfba5524ce5e094a2ee7fb0af2076b292e58d5`
- bridge_document_name: `gtkb-wi5060-sdk-bash-self-invocation-guard`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5060-sdk-bash-self-invocation-guard-003.md`
- operative_file: `bridge/gtkb-wi5060-sdk-bash-self-invocation-guard-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi5060-sdk-bash-self-invocation-guard`
- Operative file: `bridge\gtkb-wi5060-sdk-bash-self-invocation-guard-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Spec-to-Test Mapping

| Spec / Requirement | Test / Evidence file | Executed | Expected / Observed Result |
|---|---|---|---|
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` / SDK harness self-invocation denial | `platform_tests/scripts/test_sdk_bridge_bash_guard.py` (`test_sdk_harness_self_invocation_is_denied`) | yes | `python scripts/ollama_harness.py ...` is denied before execution with explicit reason. |
| False-positive control / Benign harness references | `platform_tests/scripts/test_sdk_bridge_bash_guard.py` (`test_sdk_harness_benign_references_are_allowed`) | yes | `Get-Content` and searches containing harness script paths remain allowed. |
| Existing bridge mutation guard behavior | `platform_tests/scripts/test_sdk_bridge_bash_guard.py` (`test_bridge_mutation_shapes_are_denied`, `test_read_only_bridge_references_are_allowed`) | yes | Existing bridge mutation and read-only tests pass unchanged. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / Bridge applicability | `scripts/bridge_applicability_preflight.py` | yes | Bridge applicability check succeeds with no warnings or missing specs. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / Clause applicability | `scripts/adr_dcl_clause_preflight.py` | yes | Clause preflight check succeeds with no blocking gaps. |
| Code Quality / Linting | `ruff check` | yes | Python linter returns no violations for the changed files. |
| Code Quality / Formatting | `ruff format` | yes | Python formatter confirms modified files are properly formatted. |

## Commands Executed

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5060-sdk-bash-self-invocation-guard
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5060-sdk-bash-self-invocation-guard
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_sdk_bridge_bash_guard.py -q --tb=short --basetemp .test-tmp\pytest-sdk-bash-self-invocation-c-verify
groundtruth-kb\.venv\Scripts\python.exe -m ruff check --no-cache scripts/sdk_bridge_bash_guard.py platform_tests/scripts/test_sdk_bridge_bash_guard.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check --no-cache scripts/sdk_bridge_bash_guard.py platform_tests/scripts/test_sdk_bridge_bash_guard.py
```

## Prior Deliberations

The relevant context includes `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` for harness readiness, `bridge/gtkb-wi5037-invoke-ban-false-positive-advisory-001.md` warning against false positives, and the preceding `001.md` (proposal) and `002.md` (GO verdict) files.

## Review Findings

The implementation successfully addresses the recursion issue during bridge dispatch:
- `scripts/sdk_bridge_bash_guard.py` includes a precise regex pattern detecting direct or python-invoked scripts like `scripts/ollama_harness.py` or `scripts/openrouter_harness.py`.
- Any attempt to run these in a Bash shell returns the denial reason `Bash SDK harness self-invocation denied...`
- Benign references like reading, searching, or printing these filenames are permitted.
- The preflight validation scripts and pytest execution all run and pass cleanly.

Recommended commit type: fix(harness)

## Decision Needed From Owner

None.

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `fix(harness): guard SDK self-invocation from Bash`
- Same-transaction path set:
- `scripts/sdk_bridge_bash_guard.py`
- `platform_tests/scripts/test_sdk_bridge_bash_guard.py`
- `bridge/gtkb-wi5060-sdk-bash-self-invocation-guard-003.md`
- `bridge/gtkb-wi5060-sdk-bash-self-invocation-guard-004.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.
