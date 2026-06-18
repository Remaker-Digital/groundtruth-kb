NEW

# ADR/DCL Clause Preflight Missing-Config Fail-Closed Fix - Implementation Report

bridge_kind: implementation_report
Document: gtkb-adr-dcl-clause-preflight-config-missing-fail-closed
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-adr-dcl-clause-preflight-config-missing-fail-closed-002.md
Approved proposal: bridge/gtkb-adr-dcl-clause-preflight-config-missing-fail-closed-001.md
Recommended commit type: fix:

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019edc89-ab96-74c2-a86f-058b955fbc1a
author_model: GPT-5 Codex
author_model_version: system-declared GPT-5 runtime on 2026-06-18
author_model_configuration: Codex Desktop automation; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4637

target_paths: ["scripts/adr_dcl_clause_preflight.py", "platform_tests/scripts/test_adr_dcl_clause_preflight.py", "bridge/gtkb-adr-dcl-clause-preflight-config-missing-fail-closed-*.md"]

## Implementation Claim

Implemented the GO-approved WI-4637 fix. A missing mandatory ADR/DCL clause registry now fails closed with exit `5` (`EXIT_CANNOT_EVALUATE`) instead of returning exit `0`.

The implementation also preserves the existing focused test suite's legacy `--index` argument by accepting it as a deprecated no-op compatibility option. This does not restore aggregate index authority; the help text states that dispatcher/TAFE state and numbered files remain authoritative. The compatibility option lets existing tests reach the gate logic instead of failing in `argparse`.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision was required. Implementation proceeded under the active May29 Hygiene project authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`, backed by `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`, and under the live GO at `bridge/gtkb-adr-dcl-clause-preflight-config-missing-fail-closed-002.md`.

## Prior Deliberations

- `bridge/gtkb-adr-dcl-clause-preflight-config-missing-fail-closed-001.md` - approved implementation proposal for WI-4637.
- `bridge/gtkb-adr-dcl-clause-preflight-config-missing-fail-closed-002.md` - Loyal Opposition GO authorizing this implementation.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-008.md` - VERIFIED terminal evidence for the mandatory ADR/DCL clause gate and exit-code semantics.
- `bridge/gtkb-adr-dcl-clause-auto-discovery-slice-5-008.md` - VERIFIED follow-on confirming the existing mandatory exit-5 clause gate remained unchanged.
- `bridge/gtkb-adr-dcl-clause-preflight-content-file-path-fix-004.md` - VERIFIED precedent for focused source/test corrections to `scripts/adr_dcl_clause_preflight.py`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Acquired work-intent claim for `gtkb-adr-dcl-clause-preflight-config-missing-fail-closed` at `2026-06-18T21:12:00Z`; created implementation-start packet `sha256:730188bc5f905fb98d186c4c97cb6a88cfd3c418f2dea883a4219a687434dcf0`; validated `scripts/adr_dcl_clause_preflight.py`, `platform_tests/scripts/test_adr_dcl_clause_preflight.py`, and this report path as authorized. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Ran `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-preflight-config-missing-fail-closed --json`; observed `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. |
| Implementation-report filing gates | Ran `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-preflight-config-missing-fail-closed --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-adr-dcl-clause-preflight-config-missing-fail-closed-003.md --json`; observed `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:f86ed4460e22acacc70c1428a6112b5271672fece4c96ffe6d05c6cffdc59f6b`. Ran `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-preflight-config-missing-fail-closed --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-adr-dcl-clause-preflight-config-missing-fail-closed-003.md`; observed `Blocking gaps (gate-failing): 0`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, mandatory clause-gate exit semantics | Ran `groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp .gtkb-tmp\pytest\wi4637-focused platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short`; observed `22 passed, 1 warning in 0.91s`. The new test asserts a missing `--clauses-config` returns `EXIT_CANNOT_EVALUATE` and preserves the stderr diagnostic. |
| Existing focused test compatibility | Baseline before the patch showed `9 failed, 12 passed` because existing tests supplied `--index` and the parser rejected it. After adding the deprecated no-op compatibility argument, the same focused module passed `22 passed`. |
| Code quality baseline | Ran `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py`; observed `All checks passed!`. Ran `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py`; observed `2 files already formatted`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` | All claimed files are under `E:\GT-KB` and match the approved target paths. No Agent Red, deployment, credential, or out-of-root path is touched. |
| `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `WI-4637` remains the durable work item for this defect, and this post-implementation report links the work item, GO evidence, implementation, tests, and verification request. No MemBase status mutation was performed. |

## Commands Run

```powershell
python scripts\bridge_claim_cli.py claim gtkb-adr-dcl-clause-preflight-config-missing-fail-closed
python scripts\implementation_authorization.py begin --bridge-id gtkb-adr-dcl-clause-preflight-config-missing-fail-closed
python scripts\implementation_authorization.py validate --target scripts/adr_dcl_clause_preflight.py
python scripts\implementation_authorization.py validate --target platform_tests/scripts/test_adr_dcl_clause_preflight.py
python scripts\implementation_authorization.py validate --target bridge/gtkb-adr-dcl-clause-preflight-config-missing-fail-closed-003.md
python scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-adr-dcl-clause-preflight-config-missing-fail-closed --candidate-paths scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py bridge/gtkb-adr-dcl-clause-preflight-config-missing-fail-closed-003.md --json
$tmp=(Resolve-Path .gtkb-tmp).Path; $env:TEMP=$tmp; $env:TMP=$tmp; groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp .gtkb-tmp\pytest\wi4637-baseline platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short
$tmp=(Resolve-Path .gtkb-tmp).Path; $env:TEMP=$tmp; $env:TMP=$tmp; groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp .gtkb-tmp\pytest\wi4637-focused platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-preflight-config-missing-fail-closed --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-preflight-config-missing-fail-closed
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-preflight-config-missing-fail-closed --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-adr-dcl-clause-preflight-config-missing-fail-closed-003.md --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-preflight-config-missing-fail-closed --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-adr-dcl-clause-preflight-config-missing-fail-closed-003.md
```

## Observed Results

- Baseline focused test before implementation: `9 failed, 12 passed`; failures were `argparse` rejection of existing `--index` test arguments.
- Focused test after implementation: `22 passed, 1 warning`.
- Ruff lint: `All checks passed!`.
- Ruff format: initially one file needed formatting; after applying `ruff format`, `2 files already formatted`.
- Proposal applicability preflight: `preflight_passed: true`, no missing required/advisory specs.
- Clause preflight on current GO thread: exit `0`, `Blocking gaps (gate-failing): 0`.
- Implementation-report content applicability preflight: `preflight_passed: true`, no missing required/advisory specs, packet hash `sha256:f86ed4460e22acacc70c1428a6112b5271672fece4c96ffe6d05c6cffdc59f6b`.
- Implementation-report content clause preflight: exit `0`, `Blocking gaps (gate-failing): 0`.
- Implementation authorization: all claimed target paths authorized.

## Files Changed

- `scripts/adr_dcl_clause_preflight.py`
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py`

The broader worktree already contains unrelated dirty and untracked files from other sessions/runs. They are not claimed by this report and were left untouched.

## Acceptance Criteria Status

- [x] Missing `--clauses-config` returns exit `5`, not exit `0`.
- [x] The stderr diagnostic remains explicit that the clauses config was not found.
- [x] A targeted regression test covers the missing-config path.
- [x] Existing ADR/DCL clause preflight tests pass.
- [x] No production deployment, credential action, formal artifact mutation, or unrelated cleanup is included.

## Risk And Rollback

Risk is low. The gate becomes stricter only when the mandatory clause registry is missing. The `--index` compatibility option is deliberately non-authoritative and ignored; it prevents existing tests and callers from failing before the gate evaluates.

Rollback is a normal revert of the two changed files. Reverting would restore the fail-open missing-config path and should require a separate bridge review.

## Loyal Opposition Asks

1. Verify that missing clause-registry configuration now fails closed.
2. Verify that the deprecated `--index` compatibility option does not restore aggregate index authority.
3. Return VERIFIED if the implementation and evidence satisfy the approved proposal, otherwise return NO-GO with findings.
