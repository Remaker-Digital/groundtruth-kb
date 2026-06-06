NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; workspace E:\GT-KB; approval-policy never
author_metadata_source: explicit Prime Builder metadata supplied to bridge-propose helper

# Ollama Routing Model-Version Fixture Cleanup Proposal

bridge_kind: implementation_proposal
Document: gtkb-ollama-routing-model-version-fixture-cleanup
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-LO-FOLLOWUP-WI-4386-MODEL-SOT-FIXTURE-CLEANUP
Project: PROJECT-GTKB-OLLAMA-LO-FOLLOWUP
Work Item: WI-4386
target_paths: ["platform_tests/scripts/test_verify_ollama_dispatch.py", "bridge/gtkb-ollama-routing-model-version-fixture-cleanup-*.md", "bridge/INDEX.md"]
Owner Decision: DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE
Prior Bridge Evidence: bridge/gtkb-ollama-routing-single-sot-cleanup-004.md
Date: 2026-06-06 UTC
Requires verification: true
Recommended commit type: test

## Summary

The earlier single-SoT cleanup removed duplicated selected-model expectations from the main Ollama routing tests, but a follow-up sweep found fixture-only `model_version="v1"` values in `platform_tests/scripts/test_verify_ollama_dispatch.py`. Those fixture strings are not live route selection, but they are still model-version literals. This proposal removes them so test fixtures derive route metadata the same way runtime routing does.

## Requirement Sufficiency

Existing requirements sufficient.

The owner clarification and existing Ollama routing specifications are sufficient for this narrow fixture cleanup. No new formal requirement is required before implementation because the change does not alter the selected operational model, routing schema, dispatch behavior, or tool permissions.

## Owner Decisions And Input

Mike explicitly directed in this session on 2026-06-06 that "the model version should not be hardcoded anywhere" and that model selection should be selectable with a single source of truth. This is captured as `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE`.

No further owner choice is required. This proposal only removes residual fixture-level hardcoding from tests.

## Prior Deliberations

- `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE` - owner clarification that Ollama model version must not be hardcoded and selection must have one SoT.
- `DELIB-20260606-OLLAMA-QWEN-FULL-LO-DIRECTIVE` - owner directive to make Ollama Qwen the active full-capability LO target.
- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` - owner directive to complete Ollama bridge integration.
- `DELIB-20260895` - owner selected Codex Prime Builder and Ollama Loyal Opposition while Claude Code and Antigravity were offline.
- `DELIB-20260898` - owner clarified suspended harnesses may still participate in GT-KB work.
- `DELIB-20260679` - owner clarified Ollama should be the target for LO work dispatched via the bridge.

## Specification Links

- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` - `.ollama/routing.toml` is the single routing authority for model rows and skill route selection.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` - author metadata must use the selected route's derived model metadata.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - readiness and dispatch tests must validate required tools on the selected route.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge artifacts remain the handoff and audit authority for this change.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal links governing specifications before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must map claims to executed tests.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation must occur under active project authorization.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - adopted harness routing and tool behavior must be explicit and verifiable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changes remain within `E:\GT-KB`.

## Files Expected To Change

- `platform_tests/scripts/test_verify_ollama_dispatch.py` - replace hardcoded fixture `model_version` values with model IDs whose versions are derived through `ollama_harness.infer_model_version(...)`.
- `bridge/gtkb-ollama-routing-model-version-fixture-cleanup-*.md` and `bridge/INDEX.md` - record proposal, verdict, report, and verification state.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not add credentials; only fixture model names are touched. | Bridge helper credential scan and focused diff review. |  |
| CQ-PATHS-001 | Yes | Keep all mutations under `E:\GT-KB`. | Bridge preflights and scoped git diff. |  |
| CQ-COMPLEXITY-001 | Yes | Keep change to test fixture construction. | Focused diff review. |  |
| CQ-CONSTANTS-001 | Yes | Remove duplicated model-version literals from dispatch verification fixtures. | Focused `rg` scan for remaining `model_version="..."` literals. |  |
| CQ-SECURITY-001 | Yes | Do not alter guard behavior, tool permissions, credentials, or runtime dispatch. | Diff review confirms test-only change. |  |
| CQ-DOCS-001 | Yes | Record rationale in bridge proposal/report; no user-facing docs are changed. | LO review of bridge thread. |  |
| CQ-TESTS-001 | Yes | Update focused tests while preserving behavior assertions. | Run focused pytest for Ollama script tests. |  |
| CQ-LOGGING-001 | N/A | No logging code changes. | Diff review confirms no logging surface changed. | Test-only cleanup. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest plus ruff lint and format checks. | Capture exact commands and observed results in implementation report. |  |

## Implementation Plan

1. Add neutral fixture model IDs in `platform_tests/scripts/test_verify_ollama_dispatch.py` where needed.
2. Replace every direct `model_version="v1"` fixture value with `ollama_harness_module.infer_model_version(<fixture_model_id>)`.
3. Run a focused `rg` scan proving no `model_version="..."` literals remain in that test file.
4. Run focused pytest for the Ollama script tests.
5. Run ruff lint and format checks for the changed test file.
6. File a post-implementation report and dispatch Ollama/Qwen for Loyal Opposition verification.

## Spec-To-Test Mapping

- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`: focused `rg` scan and tests verify fixture metadata is derived rather than hardcoded as a duplicate route-selection authority.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`: `test_author_metadata_check_passes_when_model_id_matches` continues to check route metadata behavior with derived fixture version metadata.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`: existing dispatch verification tests continue to exercise tool-specific route fixtures.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: implementation report will include executed command evidence for each mapped claim.

## Acceptance Criteria

- `platform_tests/scripts/test_verify_ollama_dispatch.py` contains no `model_version="..."` literals.
- All fixture route metadata in that file derives model version from the fixture model ID.
- Focused Ollama pytest passes.
- Ruff lint and format checks pass for the changed test file.
- The bridge thread receives Loyal Opposition `VERIFIED` before commit.

## Risk And Rollback

Risk is limited to making fixtures slightly more verbose. Rollback is to restore the previous fixture literals if Loyal Opposition finds the derived fixture version obscures the behavior under test.

## Out Of Scope

- Changing the selected operational model in `.ollama/routing.toml`.
- Changing harness runtime behavior.
- Changing protected narrative or formal MemBase artifacts.
- Modifying files outside the listed target paths.

## Pre-Filing Preflight

A brand-new bridge ID cannot be fully evaluated by the preflight scripts before it has an INDEX entry. After filing, Prime Builder and Loyal Opposition will run:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-routing-model-version-fixture-cleanup
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-routing-model-version-fixture-cleanup
```

Any failing post-file preflight will be treated as a proposal defect requiring revision before implementation.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
