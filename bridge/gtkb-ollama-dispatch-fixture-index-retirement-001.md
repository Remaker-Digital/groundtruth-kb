NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019eda63-8262-75f1-a361-49dbe6dfec3c
author_model: GPT-5
author_model_version: Codex GPT-5 runtime
author_model_configuration: Codex desktop automation; Prime Builder; approval_policy=never

# Align Ollama Dispatch Fixture With Numbered Bridge Authority

bridge_kind: prime_proposal
Document: gtkb-ollama-dispatch-fixture-index-retirement
Version: 001
Author: Codex Prime Builder
Date: 2026-06-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4615

target_paths: ["scripts/verify_ollama_dispatch.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]

## Summary

Fix WI-4615 by aligning the Ollama dispatch verifier fixture test with the current file bridge authority model. The stale regression still requires a disposable fixture bridge/INDEX.md entry, but the 2026-06-15 bridge cutover makes dispatcher/TAFE state plus status-bearing numbered bridge files canonical. The verifier should prove the current invariant: a Write dispatch creates bridge/gtkb-ollama-e2e-fixture-001.md in a disposable root and the first nonblank line is NEW.

## Defect Reproduction

- platform_tests/scripts/test_verify_ollama_dispatch.py::test_bridge_filing_inserts_fixture_index_entry reads fixture_root / "bridge" / "INDEX.md" and asserts Document plus NEW index entries.
- scripts/verify_ollama_dispatch.py::_check_bridge_filing_via_dispatch now writes only a numbered fixture bridge file and verifies its first nonblank status token.
- .claude/rules/file-bridge-protocol.md states that, after WI-4510 Phase 3, TAFE-backed bridge state and status-bearing numbered bridge files are canonical.
- The current stale test can fail with FileNotFoundError for the disposable fixture bridge/INDEX.md even when the verifier behavior matches current bridge authority.

## Proposed Scope

1. Update platform_tests/scripts/test_verify_ollama_dispatch.py so the fixture filing regression no longer reads or requires a disposable bridge/INDEX.md.
2. Assert that the fixture numbered bridge file exists at bridge/gtkb-ollama-e2e-fixture-001.md and that its first nonblank line is exactly NEW.
3. Keep the existing production-safety assertion that the live repository bridge/INDEX.md is not touched.
4. Update scripts/verify_ollama_dispatch.py only if the verifier needs a clarifying comment, helper extraction, or minor result text adjustment to make the current numbered-file contract explicit.
5. Preserve the existing guard-only tests, model metadata tests, routing tests, autostart checks, and dispatch tool coverage.

## Out of Scope

- No source of truth change for bridge authority.
- No production bridge state mutation.
- No restoration of retired aggregate index behavior.
- No formal artifact, specification, ADR, DCL, or Deliberation Archive mutation.

## Files Expected To Change

- scripts/verify_ollama_dispatch.py
- platform_tests/scripts/test_verify_ollama_dispatch.py

All target paths are in-root under E:/GT-KB; the bridge proposal itself is bridge/gtkb-ollama-dispatch-fixture-index-retirement-001.md under the same project root.

## Requirement Sufficiency

Existing requirements sufficient.

WI-4615 already captures the implementation defect. The linked bridge authority, proposal-linkage, harness-onboarding, and verification requirements are sufficient to implement and test the repair without new owner clarification.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Keep changes free of credentials, environment values, and private tokens; rely on the governed bridge helper credential scan before filing. | Bridge helper credential scan plus code review of the two target files. | |
| CQ-PATHS-001 | Yes | Keep fixture writes inside pytest temp roots and keep all implementation paths under E:/GT-KB. | Focused pytest must preserve the production bridge/INDEX.md mtime assertion and fixture numbered-file assertion. | |
| CQ-COMPLEXITY-001 | Yes | Limit implementation to the stale assertion and any small verifier wording needed to expose the numbered-file contract. | Diff review plus python -m ruff check scripts/verify_ollama_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py. | |
| CQ-CONSTANTS-001 | Yes | Reuse the existing fixture bridge filename and status token literals unless extracting a named helper makes the test clearer. | Focused pytest for platform_tests/scripts/test_verify_ollama_dispatch.py. | |
| CQ-SECURITY-001 | Yes | Preserve guard-only tests and avoid any production bridge mutation or shell-based bridge write behavior. | Focused pytest covers guard denial and production bridge safety tests. | |
| CQ-DOCS-001 | Yes | If verifier comments change, document only the current numbered-file authority and avoid introducing new policy text. | Diff review plus ruff checks. | |
| CQ-TESTS-001 | Yes | Update the stale regression so it checks the numbered fixture file and keep existing readiness tests intact. | python -m pytest platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short. | |
| CQ-LOGGING-001 | N/A | | | No logging behavior change is planned; console result text remains existing behavior unless a minor fixture detail is needed. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, ruff lint, and ruff format checks before the implementation report. | python -m pytest platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short; python -m ruff check scripts/verify_ollama_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py; python -m ruff format --check scripts/verify_ollama_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py. | |

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001: dispatcher/TAFE state plus status-bearing numbered bridge files are canonical; the fixture proof must not depend on retired aggregate index behavior.
- .claude/rules/file-bridge-protocol.md: records the 2026-06-15 bridge cutover and the body status-token rule for numbered bridge files.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001: this proposal cites the governing specs and maps implementation tests to them before requesting GO.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001: this proposal includes Project Authorization, Project, Work Item, and target_paths metadata.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: post-implementation verification must map the changed behavior back to linked specifications and execute focused tests.
- GOV-HARNESS-ONBOARDING-CONTRACT-001: the Ollama harness verifier is part of the harness readiness surface, so its fixture contract should reflect current bridge authority.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001: all generated artifacts and changed files remain under E:/GT-KB; no out-of-root or Agent Red path is in scope.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001: WI-4615 preserves this defect as a durable work item and this proposal preserves the implementation plan as a reviewable artifact.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001: the change keeps traceability from work item to proposal, concrete files, tests, implementation report, and verification.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001: this bridge entry is the active implementation-proposal lifecycle state for the defect; completion will move through implementation report and verification states.

## Prior Deliberations

- DA: DELIB-20264405 - prior Ollama verifier review context; its fixture-index assumptions are superseded where they conflict with the later TAFE-backed bridge cutover.
- DA: DELIB-20264404 - phase-1 Ollama verifier context; relevant to retaining the verifier's guard and dispatch confidence surface.
- DA: DELIB-20264419 - Ollama Phase 2 dispatch wiring context; relevant to preserving Write-dispatch proof coverage.
- DA: DELIB-20265025 - fallback/backoff review context; relevant to keeping readiness and fallback checks intact.
- DA: DELIB-20264459 - related harness/dispatch governance context seeded by the proposal scaffold.
- Work Item: WI-4615 - current May29 HYGIENE defect: Ollama dispatch fixture test expects retired bridge index behavior.

## Owner Decisions / Input

- PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION authorizes implementation proposals for unimplemented work items linked to PROJECT-GTKB-MAY29-HYGIENE.
- The 2026-06-18 Hygiene PB automation directive instructs Prime Builder to continue incomplete HYGIENE project work and add or process hygiene defects when safe.
- No new owner decision is required for this scoped proposal.

## Specification-Derived Verification Plan

- GOV-FILE-BRIDGE-AUTHORITY-001 and .claude/rules/file-bridge-protocol.md: python -m pytest platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short verifies the fixture numbered bridge file exists and has first nonblank line NEW without requiring fixture bridge/INDEX.md.
- GOV-HARNESS-ONBOARDING-CONTRACT-001: the same focused pytest command preserves the Ollama verifier readiness, routing, metadata, autostart, and guard-only checks.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: the post-implementation report must include this mapping and observed command results.
- Python quality gates: python -m ruff check scripts/verify_ollama_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py and python -m ruff format --check scripts/verify_ollama_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py.
- Root-boundary and production bridge safety: existing tests must continue to assert the live repository bridge/INDEX.md is not modified.

## Acceptance Criteria

- The Ollama verifier fixture proof does not read from or require disposable bridge/INDEX.md.
- The fixture proof still verifies Write dispatch creates a status-bearing numbered bridge file.
- The first nonblank line of bridge/gtkb-ollama-e2e-fixture-001.md is asserted as NEW.
- The production bridge/INDEX.md safety assertion remains in force.
- Focused pytest, ruff lint, and ruff format checks pass for the changed files.

## Risks and Rollback

Risk is low because the change aligns a stale regression with already-current verifier behavior and does not broaden dispatch capability. Rollback is a normal revert of the two target files if review identifies an overlooked bridge-publication requirement.

## Recommended Commit Type

fix: this repairs a broken test/verifier contract without adding a new capability.
