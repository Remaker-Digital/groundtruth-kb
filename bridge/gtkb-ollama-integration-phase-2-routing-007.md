REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder session override; workspace E:\GT-KB; approval-policy never

# Ollama Phase 2 Routing Expansion Proposal - REVISED

bridge_kind: implementation_proposal
Document: gtkb-ollama-integration-phase-2-routing
Version: 007
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Work Item: WI-4379
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION
Owner Decision: DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE
Responds to: bridge/gtkb-ollama-integration-phase-2-routing-006.md
Supersedes: bridge/gtkb-ollama-integration-phase-2-routing-005.md
Date: 2026-06-05 UTC
Requires verification: true
Recommended commit type: feat
target_paths: [".ollama/routing.toml", "scripts/ollama_harness.py", "config/agent-control/harness-capability-registry.toml", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_ollama_routing_config.py"]

## Revision Response

This revision addresses `bridge/gtkb-ollama-integration-phase-2-routing-006.md`:

- F1: adds a substantive `## Prior Deliberations` section in this operative proposal.
- F2: replaces terminal `WI-4373` with active successor `WI-4379`; the supported backlog CLI does not permit `resolved` to `backlogged` stage transitions, so a successor was created and attached to the project.
- F3: restores the artifact-governance advisory spec links from the prior GO'd proposal.

Scope remains the previously GO'd routing expansion plus the machine-readable `target_paths` required by implementation authorization.

## Owner Decisions / Input

- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` records the owner directive to complete remaining Ollama phases while preserving bridge GO/VERIFIED gates and the self-review prohibition.
- `DELIB-20260663` records the Phase 1 owner decision set and explicitly leaves multi-model routing and skill overrides as Phase 2+ work.
- `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION` v5 authorizes this child proposal and later child implementation only after Loyal Opposition GO; it includes `WI-4379`.
- `bridge/gtkb-ollama-integration-phase-2-004.md` authorizes filing this child proposal but does not authorize implementation until this child receives GO.
- This proposal does not authorize adapter generation, dispatch wiring, role promotion, credential lifecycle work, production deployment, out-of-root artifacts, or bypassing formal/narrative approval gates.

## Prior Deliberations

Deliberation and bridge context reviewed for this revision:

- `DELIB-20260663`: Phase 1 owner decisions, including that multi-model routing and skill overrides remain Phase 2+ scope.
- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE`: owner directive to complete remaining Ollama Phase 2+ work through child bridge GO/VERIFIED gates.
- `DELIB-20260680`: earlier LO concern context for Ollama mutating-tool safety and child verification requirements; no conflict with this bounded routing proposal.
- `bridge/gtkb-ollama-integration-phase-2-004.md`: parent GO authorizing child proposal filing only.
- `bridge/gtkb-ollama-integration-phase-2-010.md`: parent scaffolding VERIFIED, explicitly leaving child source/config implementation to the child bridge threads.
- Child thread context: `-003` was GO'd at `-004`; `-005` was NO-GO'd at `-006` because the amendment was not self-contained and cited terminal `WI-4373`.

## Backlog And Authorization Repair Evidence

- Original child WI `WI-4373` is terminal/resolved due parent bridge reconciler evidence, not child implementation verification.
- Supported CLI dry-run rejected `resolved` to `backlogged` stage transition, so the repair path is active successor `WI-4379`.
- `WI-4379` is `resolution_status=open`, `stage=backlogged`, depends on `WI-4373`, and is attached to `PROJECT-GTKB-OLLAMA-INTEGRATION` as membership order 15.
- PAUTH v5 rowid 142 includes `WI-4379` while retaining original child WI traceability.

## Requirement Sufficiency

Existing requirements sufficient. No new owner choice is required before Loyal Opposition review.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use synthetic fixtures and local config metadata only; no credentials or environment values. | Commit hook secret scan and diff review. | |
| CQ-PATHS-001 | Yes | Keep all target paths under E:\GT-KB and use explicit target_paths metadata. | Bridge applicability preflight and implementation-start packet. | |
| CQ-COMPLEXITY-001 | Yes | Keep the child scope narrow and avoid combining routing, adapters, dispatch, and role promotion in one implementation. | Loyal Opposition review of this child proposal. | |
| CQ-CONSTANTS-001 | Yes | Name schema keys, model IDs, command surfaces, and registry fields rather than scattering literals. | Focused tests and code review in the child implementation report. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed behavior for unavailable models, unsupported tools, destructive gates, and out-of-root paths. | Focused tests and code review in the child implementation report. | |
| CQ-DOCS-001 | Yes | Update only canonical operational surfaces needed by this child. | Diff review. | |
| CQ-TESTS-001 | Yes | Add or update focused tests that map directly to cited Ollama governance specs. | Pytest plus scoped ruff check and format check. | |
| CQ-LOGGING-001 | Yes | Keep diagnostic output structured and avoid persistent logs unless an existing surface owns them. | Test assertions or code review of changed command output. | |
| CQ-VERIFICATION-001 | Yes | File a post-implementation report with exact commands and observed results before VERIFIED review. | Bridge implementation report and LO verification. | |

## Target Paths

- `.ollama/routing.toml`
- `scripts/ollama_harness.py`
- `config/agent-control/harness-capability-registry.toml`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_ollama_routing_config.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-OLLAMA-HARNESS-ADOPTION-001`
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Proposed Scope

Implement a bounded routing expansion for the Ollama harness shim:

- Extend `.ollama/routing.toml` to support multiple model rows and per-skill routing overrides while keeping the existing Python shim and static TOML approach.
- Validate configured routes against the advertised local model inventory and fail closed on invalid route references.
- Preserve Phase 1 author metadata injection and tool-parity gate behavior while adding route selection.
- Register routing capability in the harness capability registry only to the extent needed for deterministic doctor and test surfaces.

## Out Of Scope

- `.ollama/skills/` adapter generation.
- Cross-harness dispatch wiring.
- Harness D role promotion or project closure mechanics.
- Credential handling, production deployment, or external network model provisioning.

## Specification-Derived Verification Plan

- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`: add parser and validation tests for multiple model rows, per-skill overrides, default selection, and invalid references.
- `ADR-OLLAMA-HARNESS-ADOPTION-001`: verify routing remains a local harness-shim adoption path and does not create a new external service dependency.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`: verify routed harness output continues to include required author metadata.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`: verify route selection does not bypass the existing fail-closed tool parity gate.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`: verify routing remains compatible with onboarding and doctor checks.
- `GOV-SESSION-ROLE-AUTHORITY-001`: verify route selection does not alter durable role authority or active-session override semantics.

## Implementation Report Requirements

After implementation, file the next bridge artifact on this thread as `NEW` with exact files changed, spec-to-test mapping, pytest and ruff results, implementation authorization packet hash, and any deferred issues or explicit statement that none remain.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
