NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder session override; workspace E:\GT-KB; approval-policy never

# Ollama Phase 2 Role Promotion And Closure Proposal

bridge_kind: prime_proposal
Document: gtkb-ollama-integration-phase-2-role-promotion
Version: 001
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Work Item: WI-4376
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION
Owner Decision: DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE
Date: 2026-06-05 UTC
Requires verification: true
Recommended commit type: feat

## Requirement Sufficiency

Existing requirements sufficient.

The owner directive in `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE`, the Phase 1 owner-decision anchor `DELIB-20260663`, the Phase 1 terminal verification at `bridge/gtkb-ollama-integration-phase-1-008.md`, and the Phase 2 umbrella GO at `bridge/gtkb-ollama-integration-phase-2-004.md` provide enough direction for this child. No new owner choice is required before Loyal Opposition review.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use synthetic fixtures and local config metadata only; no credentials or environment values. | Commit hook secret scan and diff review. | |
| CQ-PATHS-001 | Yes | Keep all target paths under E:\GT-KB and use explicit target_paths metadata. | Bridge applicability preflight and implementation-start packet. | |
| CQ-COMPLEXITY-001 | Yes | Keep the child scope narrow and avoid combining routing, adapters, dispatch, and role promotion in one implementation. | Loyal Opposition review of this child proposal. | |
| CQ-CONSTANTS-001 | Yes | Name schema keys, model IDs, command surfaces, and registry fields rather than scattering literals. | Focused tests and code review in the child implementation report. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed behavior for unavailable models, unsupported tools, destructive gates, and out-of-root paths. | Focused tests and code review in the child implementation report. | |
| CQ-DOCS-001 | Yes | Update only the canonical operational surfaces needed by this child; avoid broad narrative churn. | Diff review and targeted docs/protected-artifact evidence when applicable. | |
| CQ-TESTS-001 | Yes | Add or update focused tests that map directly to the cited Ollama governance specs. | Pytest plus scoped ruff check and format check. | |
| CQ-LOGGING-001 | Yes | Keep diagnostic output structured and avoid persistent logs unless an existing surface owns them. | Test assertions or code review of changed command output. | |
| CQ-VERIFICATION-001 | Yes | File a post-implementation report with exact commands and observed results before VERIFIED review. | Bridge implementation report and LO verification. | |

## Target Paths

- `harness-state/harness-registry.json`
- `scripts/harness_roles.py`
- `groundtruth-kb/src/groundtruth_kb/harness_projection.py`
- `groundtruth.db`
- `memory/MEMORY.md`
- `platform_tests/scripts/test_ollama_role_promotion.py`
- `groundtruth-kb/tests/test_doctor_ollama.py`

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
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations And Bridge Evidence

- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` authorizes completing the remaining Ollama phases while preserving bridge GO and VERIFIED gates.
- `DELIB-20260663` preserves the Phase 1 owner decisions and leaves role promotion as Phase 2+ scope.
- `DELIB-20260679` confirms Phase 1 kept harness D registered without an active role.
- `bridge/gtkb-ollama-integration-phase-1-008.md` verifies the Phase 1 terminal state and its exclusions.
- `bridge/gtkb-ollama-integration-phase-2-004.md` GO authorizes this child proposal filing but not its implementation.

## Proposed Scope

Implement governed role-promotion and closure mechanics for harness D after prerequisite Ollama children are independently verified:

- Add a reversible role/status transition path that uses canonical role writers and preserves durable role authority.
- Gate any role promotion on verified evidence from routing, adapter, and dispatch children.
- Add closure mechanics that can resolve Phase 2+ work items and update `memory/MEMORY.md` only after child VERIFIED evidence exists.
- Add tests for promotion refusal when prerequisite evidence is missing and success when all prerequisite bridge threads are VERIFIED.

## Out Of Scope

- Multi-model route implementation.
- `.ollama/skills/` adapter generation.
- Cross-harness dispatch implementation.
- Credential handling, production deployment, or external network model provisioning.
- Assigning a production workload to Ollama beyond governed GT-KB harness participation.

## Specification-Derived Verification Plan

- `GOV-HARNESS-ROLE-PORTABILITY-001`: verify promotion mechanics use portable role authority rather than vendor-specific assumptions.
- `GOV-SESSION-ROLE-AUTHORITY-001`: verify durable registry writes and active-session override behavior stay canonical.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`: verify role promotion is gated by onboarding evidence and doctor-visible readiness.
- `ADR-OLLAMA-HARNESS-ADOPTION-001`: verify closure mechanics preserve Ollama as a governed local harness adoption path.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`: verify promotion refuses any state where tool parity evidence is missing.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`: verify promotion evidence includes required author metadata behavior for Ollama-authored artifacts.

## Implementation Report Requirements

After implementation, file the next bridge artifact on this thread as `NEW` with:

- exact files changed;
- prerequisite bridge VERIFIED evidence;
- role promotion and rollback evidence;
- spec-to-test mapping;
- pytest, ruff check, and ruff format results;
- implementation authorization packet hash;
- any deferred issues or explicit statement that none remain.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
