NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-automation-keep-working-2026-06-18T20-52Z
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop automation session; Prime Builder

# GT-KB Bridge Implementation Report - Dot-Prefixed Protected Path Normalization

bridge_kind: implementation_report
Document: gtkb-dot-prefixed-protected-path-normalization
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-dot-prefixed-protected-path-normalization-002.md
Approved proposal: bridge/gtkb-dot-prefixed-protected-path-normalization-001.md
Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4642
Recommended commit type: fix:

## Implementation Claim

Implemented the WI-4642 protected-path normalization fix. Both governance classifiers now preserve real dot-prefixed path names and only strip explicit leading `./` segments after separator normalization.

Behavior changed:

- `.claude/hooks/`, `.claude/rules/`, `.codex/gtkb-hooks/`, `.github/`, `.claude/settings.json`, `.codex/hooks.json`, `.env`, `.env.*`, `env.local`, and `env.staging` classify as protected.
- Existing allowed-write exceptions for `bridge/`, `independent-progress-assessments/`, `.groundtruth/session/snapshots/`, and `.gtkb-state/` remain unprotected.
- `scripts/` and other existing protected prefixes still classify as protected.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority and lifecycle rules govern this report and the LO verification handoff.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation stayed inside the approved proposal's linked surfaces.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - report carries the project authorization, project, work item, and target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification below maps tests to the approved specification surfaces.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active May29 Hygiene authorization covered `WI-4642`.
- `GOV-STANDING-BACKLOG-001` - implementation traces to durable backlog item `WI-4642`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected mutation classifiers now fail closed for dot-prefixed protected surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves governance artifact traceability by preventing protected artifacts from bypassing bridge authorization.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserves proposal -> GO -> report -> verification lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - defect remains linked to durable work-item and bridge artifacts.

## Owner Decisions / Input

No new owner decision was required. Implementation used the existing May29 Hygiene authorization and the Loyal Opposition GO verdict.

## Prior Deliberations

- `WI-4642` - captured the dot-prefixed protected-path escape.
- `bridge/gtkb-dot-prefixed-protected-path-normalization-001.md` - approved implementation proposal.
- `bridge/gtkb-dot-prefixed-protected-path-normalization-002.md` - Loyal Opposition GO verdict.
- `INTAKE-5a61f299` - claim-gated implementation-start intake; this repair fixes a classifier used by that gate.
- `gtkb-governance-hook-worktree-root-resolution` - related prior path-normalization repair, distinct from this dot-prefix issue.
- `gtkb-protected-commit-authorization-gate-001` - adjacent commit-time gate work that left this source-gate classifier repair to `WI-4642`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Added `test_is_protected_path_preserves_dot_prefixed_protected_paths` and `test_protected_path_classification_preserves_dot_prefixed_prefixes` for `scripts/implementation_start_gate.py`; focused pytest passed. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Added `test_guard_classifies_dot_prefixed_protected_paths` for `scripts/protected_mutation_guard.py`; focused pytest passed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verified bridge/diagnostic allowed-write exceptions remain unprotected with `test_guard_keeps_bridge_and_diagnostic_writes_unprotected` and direct implementation-start classifier assertions. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Ran focused pytest, Ruff check, Ruff format check, and target authorization validation before filing this report. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `scripts/implementation_authorization.py validate --target ...` returned `authorized: true` for all four changed target paths. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target scripts/implementation_start_gate.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target scripts/protected_mutation_guard.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target platform_tests/scripts/test_implementation_start_gate.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target platform_tests/scripts/test_protected_mutation_guard.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= platform_tests\scripts\test_implementation_start_gate.py::test_is_protected_path_preserves_dot_prefixed_protected_paths platform_tests\scripts\test_implementation_start_gate.py::test_protected_path_classification_preserves_dot_prefixed_prefixes platform_tests\scripts\test_protected_mutation_guard.py::test_guard_classifies_dot_prefixed_protected_paths platform_tests\scripts\test_protected_mutation_guard.py::test_guard_keeps_bridge_and_diagnostic_writes_unprotected -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\implementation_start_gate.py scripts\protected_mutation_guard.py platform_tests\scripts\test_implementation_start_gate.py platform_tests\scripts\test_protected_mutation_guard.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\implementation_start_gate.py scripts\protected_mutation_guard.py platform_tests\scripts\test_implementation_start_gate.py platform_tests\scripts\test_protected_mutation_guard.py`
- `git diff --check -- scripts/implementation_start_gate.py scripts/protected_mutation_guard.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protected_mutation_guard.py`

## Observed Results

- Implementation authorization validation returned `authorized: true` for all four changed targets.
- Focused pytest result: `24 passed, 1 warning`.
- Ruff check result: `All checks passed!`
- Ruff format check result: `4 files already formatted`.
- Git whitespace check result: no whitespace errors for the changed target paths.

The pytest warning is the pre-existing repository warning for unknown pytest config option `asyncio_mode`.

## Files Changed

- `scripts/implementation_start_gate.py`
- `scripts/protected_mutation_guard.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_protected_mutation_guard.py`
- `bridge/gtkb-dot-prefixed-protected-path-normalization-003.md`

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: source gate behavior changed with focused regression coverage.

## Acceptance Criteria Status

- Dot-prefixed protected exact paths and prefixes classify as protected: satisfied.
- Environment credential paths classify as protected in the implementation-start gate: satisfied.
- Bridge and diagnostic write exceptions remain allowed: satisfied.
- Source/test target scope stayed inside the GO packet: satisfied.
- Focused pytest and ruff verification passed: satisfied.

## Risk And Rollback

Residual risk is limited to path normalization behavior in two governance classifiers. Rollback is a single source/test commit revert plus an append-only bridge follow-up if Loyal Opposition finds an over-broad or under-broad classification. The implementation intentionally does not alter bridge dispatch, work-intent, or authorization packet semantics.

## Loyal Opposition Asks

1. Verify that dot-prefixed protected surfaces can no longer bypass the implementation-start or protected-mutation guards.
2. Verify that allowed bridge/diagnostic writes remain unblocked.
3. Return VERIFIED if the implementation and evidence satisfy the approved proposal, otherwise return NO-GO with findings.
