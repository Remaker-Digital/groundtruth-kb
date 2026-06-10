NEW

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; workspace E:\GT-KB; approval-policy never

# Ollama Qwen Full LO Dispatch Test Update

bridge_kind: prime_proposal
Document: gtkb-ollama-qwen-full-lo-dispatch-test-update
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-LO-OPERATIONS-QWEN-FULL-LO
Project: PROJECT-GTKB-OLLAMA-LO-OPERATIONS
Work Item: WI-4385
target_paths: ["platform_tests/scripts/test_ollama_dispatch.py", "bridge/gtkb-ollama-qwen-full-lo-dispatch-test-update-*.md", "bridge/INDEX.md"]
Owner Decision: DELIB-20260606-OLLAMA-QWEN-FULL-LO-DIRECTIVE
Date: 2026-06-06 UTC
Requires verification: true
Recommended commit type: test

## Summary

This amendment authorizes the adjacent dispatch-readiness test update discovered during implementation of `gtkb-ollama-qwen-full-lo-route-gate-compliant`. The runtime verifier now correctly requires full Loyal Opposition tools for Ollama bridge dispatch. `platform_tests/scripts/test_ollama_dispatch.py` still models the bridge-review route as read/search-only and hardcodes an old model tag in its fixture. Updating that test is necessary to preserve the owner requirement that model selection live in the routing SoT and that LO dispatch readiness require full guarded tools.

## Requirement Sufficiency

Existing requirements sufficient.

The owner directive for Qwen full Loyal Opposition operation, `WI-4385`, and the approved gate-compliant proposal define the underlying behavior. This amendment only authorizes the adjacent test fixture update needed to verify that behavior.

## Owner Decisions And Input

Mike clarified during implementation that the model version must not be hardcoded anywhere and must be selectable from a single SoT. This proposal applies that clarification to the affected dispatch-readiness test fixture.

## Prior Deliberations

- `DELIB-20260606-OLLAMA-QWEN-FULL-LO-DIRECTIVE` - owner directive to use Ollama Qwen as full LO target.
- `bridge/gtkb-ollama-qwen-full-lo-route-gate-compliant-001.md` - approved primary proposal for route and harness changes.
- `bridge/gtkb-ollama-qwen-full-lo-route-gate-compliant-002.md` - Qwen LO GO verdict approving the primary proposal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge files remain the authority for implementation approval.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal links governing specs before work begins.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - tests must map to linked specifications.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation happens under active PAUTH.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - scoped target paths must match implementation authorization.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner clarification and test-surface amendment are artifact-oriented governance events.
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` - `.ollama/routing.toml` is the model route SoT.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - dispatch readiness must require tools needed for assigned LO work.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` - model metadata should derive from the selected route.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - changes stay under `E:\GT-KB`.

## Files Expected To Change

- `platform_tests/scripts/test_ollama_dispatch.py` - update fixture model ID to a neutral selectable route, remove duplicated fixture model_version field, and expect full LO tools in readiness tests.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Test fixture values remain neutral and credential-free. | Bridge helper credential scan and test diff review. |  |
| CQ-PATHS-001 | Yes | Mutate only the authorized platform test file and bridge artifacts under `E:\GT-KB`. | Implementation authorization packet and git diff inspection. |  |
| CQ-COMPLEXITY-001 | Yes | Keep the change to fixture constants and assertions only. | Focused review of the test diff. |  |
| CQ-CONSTANTS-001 | Yes | Remove the old hardcoded model/version fixture and derive expected behavior from route selection semantics. | `platform_tests/scripts/test_ollama_dispatch.py` passes. |  |
| CQ-SECURITY-001 | Yes | No production code or guard behavior changes in this amendment. | Diff review confirms test-only mutation. |  |
| CQ-DOCS-001 | N/A | No documentation artifact changes are part of this amendment. | Diff review confirms no docs touched. | Test-only update. |
| CQ-TESTS-001 | Yes | Update and run the affected dispatch-readiness test. | `python -m pytest platform_tests/scripts/test_ollama_dispatch.py -q --tb=short`. |  |
| CQ-LOGGING-001 | N/A | No logging behavior changes. | Diff review confirms no logging surface touched. | Test-only update. |
| CQ-VERIFICATION-001 | Yes | Run the affected dispatch test and the primary focused Ollama tests. | Capture commands and results in the implementation report. |  |

## Implementation Plan

1. Update `platform_tests/scripts/test_ollama_dispatch.py` so the default fixture route exposes `Read`, `Write`, `Edit`, `Grep`, `Glob`, and `Bash`.
2. Replace old real model fixture literals with a neutral `fixture-review:current` model ID and remove duplicated fixture `model_version` TOML.
3. Update assertions to expect the neutral route key and the full missing-tool set when the fixture intentionally omits tools.

## Spec-To-Test Mapping

- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`: the fixture uses `model_id` as the selectable model SoT and no duplicated `model_version` TOML field.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`: the readiness-pass fixture includes the full LO tool set, and the missing-tool fixture verifies readiness fails closed when required tools are absent.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the affected test file is executed after the amendment.

## Acceptance Criteria

- `platform_tests/scripts/test_ollama_dispatch.py` no longer contains the old Qwen 2.5 model/version fixture.
- Its default readiness fixture exposes the full guarded LO tool set.
- The affected dispatch test passes.

## Risk And Rollback

Risk is low because this is a test-only update that aligns an older fixture with the newly approved runtime readiness semantics. Rollback is to restore the old test fixture if the runtime readiness requirement is reverted.

## Out Of Scope

- Runtime code changes.
- Additional routing changes.
- Credential lifecycle or production behavior.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
