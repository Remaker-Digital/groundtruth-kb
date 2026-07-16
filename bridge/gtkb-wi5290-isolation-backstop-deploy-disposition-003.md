NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f69a3-25dd-75e1-83d6-8c4aa29fb912
author_model: GPT-5 Codex
author_model_version: 2026-07-16 runtime
author_model_configuration: Codex Desktop interactive Prime Builder A; user-directed PB bridge auto-process

# GT-KB Bridge Implementation Report - gtkb-wi5290-isolation-backstop-deploy-disposition - 003

bridge_kind: implementation_report
Document: gtkb-wi5290-isolation-backstop-deploy-disposition
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5290-isolation-backstop-deploy-disposition-002.md
Approved proposal: bridge/gtkb-wi5290-isolation-backstop-deploy-disposition-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5290
Recommended commit type: fix

## Implementation Claim

The isolation backstop now recognizes exactly the two governed reference-adopter release build-context helpers. No directory glob was added. A focused regression places identical Agent Red references in both approved helper paths and in `scripts/deploy/other.ps1`; only the two literal helpers are allowed and the sibling remains a violation.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required. `DELIB-0834`, `DELIB-0877`, and `DELIB-202666274` remain the carried authority.

## Prior Deliberations

- `DELIB-0834`
- `DELIB-0877`
- `DELIB-202666274`
- `bridge/gtkb-wi5290-isolation-backstop-deploy-disposition-001.md`
- `bridge/gtkb-wi5290-isolation-backstop-deploy-disposition-002.md`

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | The two deployment helpers and application placement remained byte-untouched; only the checker and focused test changed. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | The live backstop exits 0 with 1,641 files scanned and zero violations. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | One fixture proves both literal positive paths and the unauthorized sibling negative path. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Allowed results carry `reference-adopter release build-context helper`; the sibling has no reason and remains a violation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | 10 focused tests, Ruff lint, Ruff format, and diff check pass. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Claim row 31490 and packet `sha256:f762231070c5e59592bf484498fc830f62692cfe9b6f81657b74e7b62ccab7b5` bound the exact two targets. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe scripts\isolation_program_backstop.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_isolation_program_backstop.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\ruff.exe check scripts\isolation_program_backstop.py platform_tests\scripts\test_isolation_program_backstop.py`
- `groundtruth-kb\.venv\Scripts\ruff.exe format platform_tests\scripts\test_isolation_program_backstop.py`
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts\isolation_program_backstop.py platform_tests\scripts\test_isolation_program_backstop.py`
- `git diff --check -- scripts/isolation_program_backstop.py platform_tests/scripts/test_isolation_program_backstop.py`
- `git status --short --` on the two targets and two deployment helpers.

## Observed Results

- Live backstop: PASS, 1,641 files scanned, 210 allowed references, 0 violations.
- Focused pytest: 10 passed in 0.34 seconds; one existing unknown-`asyncio_mode` warning.
- Ruff check: all checks passed.
- Ruff format check: 2 files already formatted after the scoped test formatter run.
- Diff check: passed; only Git line-ending notices were emitted.
- Deployment helpers were clean in `git status` and unchanged by this implementation.
- Candidate hashes:
  - checker: `B40F6B64FEC46A5E1F91C0E5CCDA95FA479FF0163950F08A9014CB7599D3049D`
  - test: `91A93A75C3D089F62C0C857C53BC8AEE87C0A7F262CEE2DC520137A78376D44C`
  - build-context helper unchanged: `45AB98D85C177920239CC8FB4F47C91F8C6BF9B9D381006D442FF07F6DA3F1CC`
  - staging helper unchanged: `BA0613D7B88582B90F83C66F6E3265B1CD5505E34AA55C9B7B96FDEAA48CAB1F`

## Files Changed

- `scripts/isolation_program_backstop.py`
- `platform_tests/scripts/test_isolation_program_backstop.py`

Diff stat: 41 insertions across exactly two files.

## Recommended Commit Type

- Recommended commit type: `fix`
- Justification: corrects a deterministic release-gate false positive without changing deployment behavior.

## Acceptance Criteria Status

- PASS: live backstop exits zero.
- PASS: exactly the two named helpers receive the reference-adopter reason.
- PASS: `scripts/deploy/other.ps1` remains a violation.
- PASS: no broad deploy glob exists.
- PASS: deployment helpers and application placement remain unchanged.
- PASS: all focused tests and static gates pass.
- PASS: no stage, commit, push, deployment, release, credential, dispatcher, cleanup, or external mutation occurred.

## Risk And Rollback

Residual risk is the existing path-level allowlist design: future references in either exact helper inherit the same disposition. This GO explicitly accepted that as non-blocking. Rollback removes only the two literal tuples and the focused test; deployment files remain untouched.

## Loyal Opposition Asks

1. Re-run the live backstop and require zero violations.
2. Re-run the focused tests and both Ruff gates.
3. Inspect the diff for exactly two literal helper entries and the sibling negative test.
4. Return VERIFIED only if all evidence and scope constraints hold; otherwise return NO-GO with concrete findings.
