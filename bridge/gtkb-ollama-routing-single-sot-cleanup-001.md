NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; workspace E:\GT-KB; approval-policy never
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Ollama Routing Single-SoT Cleanup Proposal

bridge_kind: prime_proposal
Document: gtkb-ollama-routing-single-sot-cleanup
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-LO-OPERATIONS-QWEN-FULL-LO
Project: PROJECT-GTKB-OLLAMA-LO-OPERATIONS
Work Item: WI-4385
target_paths: ["platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_ollama_routing_config.py", "bridge/gtkb-ollama-routing-single-sot-cleanup-*.md", "bridge/INDEX.md"]
Owner Decision: current-session directive on 2026-06-06 that model version must not be hardcoded and model selection must have a single source of truth
Prior Bridge Evidence: bridge/gtkb-ollama-qwen-full-lo-route-gate-compliant-004.md and bridge/gtkb-ollama-qwen-full-lo-dispatch-test-update-004.md
Date: 2026-06-06 UTC
Requires verification: true
Recommended commit type: test

## Summary

The Qwen Loyal Opposition route is implemented and verified, but the owner clarified before commit that the Ollama model version must not be hardcoded in multiple live surfaces. Runtime code derives `author_model_version` from the selected Ollama `model_id`, and `.ollama/routing.toml` is the operational model-selection authority. This cleanup removes duplicated selected-model expectations from focused tests so changing the active Ollama route remains a configuration choice rather than a test-code edit.

## Requirement Sufficiency

Existing requirements sufficient.

The active Ollama routing schema specification already establishes `.ollama/routing.toml` as the routing authority. The owner clarification narrows how tests should assert that contract: tests should validate configured behavior from the routing file and derived metadata, not duplicate one selected cloud tag as a second source of truth.

## Owner Decisions And Input

Mike explicitly directed in this session on 2026-06-06: "the model version should not be hardcoded anywhere - it should be selectable, with a single SoT".

No further owner choice is required. This proposal does not change the selected operational model; it only removes test-level duplication of selected model identity/version.

## Prior Deliberations

- `DELIB-20260606-OLLAMA-QWEN-FULL-LO-DIRECTIVE` - owner directive to make Ollama Qwen the active full-capability LO target.
- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` - owner directive to complete Ollama bridge integration.
- `DELIB-20260895` - owner selected Codex Prime Builder and Ollama Loyal Opposition while Claude Code and Antigravity were offline.
- `DELIB-20260898` - owner clarified suspended harnesses may still participate in GT-KB work.
- `DELIB-20260679` - owner clarified Ollama should be the target for LO work dispatched via the bridge.

## Specification Links

- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` - `.ollama/routing.toml` is the single routing authority for model rows and skill route selection.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - readiness tests must validate required tools on the selected route.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` - author metadata must use the selected route's derived model metadata.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge artifacts remain the handoff and audit authority for this change.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal links governing specifications before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must map claims to executed tests.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation must occur under active project authorization.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - adopted harness routing and tool behavior must be explicit and verifiable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changes remain within `E:\GT-KB`.

## Files Expected To Change

- `platform_tests/scripts/test_ollama_harness.py` - replace the parser's selected Qwen route literal with a neutral route fixture.
- `platform_tests/scripts/test_ollama_routing_config.py` - remove repository-test constants for active Qwen and Kimi model IDs; assert the configured bridge-review/verification route is present, selectable, full-tool, and derives model version from configured model ID.
- `bridge/gtkb-ollama-routing-single-sot-cleanup-*.md` and `bridge/INDEX.md` - record proposal, verdict, report, and verification state.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not add credentials; only test fixture strings and model route labels are touched. | Bridge helper credential scan plus focused diff review. |  |
| CQ-PATHS-001 | Yes | Keep all mutations under `E:\GT-KB`. | Bridge preflights and scoped git diff. |  |
| CQ-COMPLEXITY-001 | Yes | Keep change to two test assertions without new helpers or runtime branching. | Focused diff review. |  |
| CQ-CONSTANTS-001 | Yes | Remove duplicated selected-model constants from tests; keep `.ollama/routing.toml` as live SoT. | Focused `rg` scan and routing tests. |  |
| CQ-SECURITY-001 | Yes | Do not alter guard behavior, tool permissions, credentials, or runtime dispatch. | Diff review confirms tests only. |  |
| CQ-DOCS-001 | Yes | Record rationale in bridge proposal/report; no user-facing docs are changed. | LO review of bridge thread. |  |
| CQ-TESTS-001 | Yes | Update focused tests to validate behavior through config-derived route data. | Run the Ollama focused pytest suite. |  |
| CQ-LOGGING-001 | N/A | No logging code changes. | Diff review confirms no logging surface changed. | Test-only cleanup. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest plus ruff lint and format checks for changed Python tests. | Capture exact commands and observed results in implementation report. |  |

## Implementation Plan

1. Update `platform_tests/scripts/test_ollama_harness.py` so CLI parser coverage uses a neutral route key instead of the current selected Qwen route.
2. Update `platform_tests/scripts/test_ollama_routing_config.py` so repository routing assertions load `.ollama/routing.toml` and validate the configured active LO route without duplicating the selected `model_id` or tag in test constants.
3. Run focused pytest for the changed Ollama test files plus the already-touched readiness and dispatch tests.
4. Run ruff lint and ruff format checks on changed Python tests.
5. File a post-implementation report and dispatch Ollama/Qwen for Loyal Opposition verification.

## Spec-To-Test Mapping

- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`: `platform_tests/scripts/test_ollama_routing_config.py` will assert model selection is read from `.ollama/routing.toml` and that `selected.model_version == infer_model_version(selected.model_id)`.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`: `platform_tests/scripts/test_ollama_routing_config.py` will assert the configured bridge-review route exposes the full LO tool set.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`: `platform_tests/scripts/test_ollama_harness.py` continues to assert system prompt metadata uses selected route metadata, with neutral fixtures.

## Acceptance Criteria

- No focused test duplicates the active selected Ollama model ID or model-version tag as a second selection authority.
- `.ollama/routing.toml` remains the only live place to switch the active Ollama LO model route.
- Focused pytest passes.
- Ruff lint and format checks pass for changed Python test files.
- The bridge thread receives Loyal Opposition `VERIFIED` before commit.

## Risk And Rollback

Risk is limited to weakening tests too far. The cleanup must keep behavioral assertions: skill routes resolve to configured models, bridge-review and verification share the configured LO route, the selected route exposes the full LO tool set, and model version is derived from model ID. Rollback is to restore prior test constants if LO finds the new tests no longer catch route drift.

## Out Of Scope

- Changing the operational selected model in `.ollama/routing.toml`.
- Changing harness runtime behavior.
- Changing protected narrative or formal MemBase artifacts.
- Modifying files outside the listed target paths.

## Pre-Filing Preflight

The proposal is filed through the helper-mediated Codex bridge writer. Pre-filing bridge preflights cannot fully evaluate a brand-new bridge ID before the INDEX entry exists; after filing, Prime Builder will run:

```powershell
python scripts\\bridge_applicability_preflight.py --bridge-id gtkb-ollama-routing-single-sot-cleanup
python scripts\\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-routing-single-sot-cleanup
```

Any failing post-file preflight will be treated as a proposal defect requiring revision before implementation.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
