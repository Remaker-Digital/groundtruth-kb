REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder session override; workspace E:\GT-KB; approval-policy never

# Ollama Phase 2 Role Promotion And Closure Proposal - REVISED

bridge_kind: prime_proposal
Document: gtkb-ollama-integration-phase-2-role-promotion
Version: 007
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Work Item: WI-4382
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION
Owner Decision: DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE
Responds to: bridge/gtkb-ollama-integration-phase-2-role-promotion-006.md
Supersedes: bridge/gtkb-ollama-integration-phase-2-role-promotion-005.md
Date: 2026-06-05 UTC
Requires verification: true
Recommended commit type: feat
target_paths: ["harness-state/harness-registry.json", "scripts/harness_roles.py", "groundtruth-kb/src/groundtruth_kb/harness_projection.py", "groundtruth.db", "memory/MEMORY.md", "platform_tests/scripts/test_ollama_role_promotion.py", "groundtruth-kb/tests/test_doctor_ollama.py"]

## Revision Response

This revision addresses `bridge/gtkb-ollama-integration-phase-2-role-promotion-006.md`:

- F1: restores the explicit `## Specification-Derived Verification Plan` and `## Implementation Report Requirements` sections.
- F2: adds a substantive `## Prior Deliberations` section in this operative proposal.
- F3: replaces terminal `WI-4376` with active successor `WI-4382`; the supported backlog CLI does not permit `resolved` to `backlogged` stage transitions.
- F4: restores the artifact-governance advisory spec links from the prior GO'd proposal.

Scope remains the previously GO'd role promotion and closure mechanics plus the machine-readable `target_paths` required by implementation authorization.

## Owner Decisions / Input

- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` records the owner directive to complete remaining Ollama phases while preserving bridge GO/VERIFIED gates and the self-review prohibition.
- `DELIB-20260663` records the Phase 1 owner decision set and explicitly keeps harness D registered with no active role during Phase 1.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` and `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` remain relevant because this child changes durable role/status behavior only after prerequisite evidence.
- `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION` v5 authorizes this child proposal and later child implementation only after Loyal Opposition GO; it includes `WI-4382`.
- `bridge/gtkb-ollama-integration-phase-2-004.md` authorizes filing this child proposal but does not authorize implementation until this child receives GO.
- Role promotion remains gated on VERIFIED routing, adapter, and dispatch children; canonical role writers remain mandatory; rollback/reversibility evidence must be reported before VERIFIED.
- This proposal does not authorize route implementation, adapter generation, dispatch implementation, credential lifecycle work, production deployment, out-of-root artifacts, or bypassing formal/narrative approval gates.

## Prior Deliberations

Deliberation and bridge context reviewed for this revision:

- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE`: owner directive to complete remaining Ollama Phase 2+ work through child bridge GO/VERIFIED gates.
- `DELIB-20260663`: Phase 1 owner decisions, including harness D registered with no active role and Phase 2+ role promotion as future scope.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`: lifecycle independence context for project/work-item closure mechanics.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`: role/status orthogonality context for any durable role/status promotion.
- `bridge/gtkb-ollama-integration-phase-2-004.md`: parent GO authorizing child proposal filing only.
- `bridge/gtkb-ollama-integration-phase-2-010.md`: parent scaffolding VERIFIED, explicitly leaving child source/config implementation to the child bridge threads.
- Child thread context: `-003` was GO'd at `-004`; `-005` was NO-GO'd at `-006` because the amendment was not self-contained and cited terminal `WI-4376`.

## Backlog And Authorization Repair Evidence

- Original child WI `WI-4376` is terminal/resolved due parent bridge reconciler evidence, not child implementation verification.
- Supported CLI dry-run rejected `resolved` to `backlogged` stage transition, so the repair path is active successor `WI-4382`.
- `WI-4382` is `resolution_status=open`, `stage=backlogged`, depends on `WI-4376`, `WI-4379`, `WI-4380`, and `WI-4381`, and is attached to `PROJECT-GTKB-OLLAMA-INTEGRATION` as membership order 18.
- PAUTH v5 rowid 142 includes `WI-4382` while retaining original child WI traceability.

## Requirement Sufficiency

Existing requirements sufficient. No new owner choice is required before Loyal Opposition review.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use synthetic fixtures and local config metadata only; no credentials or environment values. | Commit hook secret scan and diff review. | |
| CQ-PATHS-001 | Yes | Keep all target paths under E:\GT-KB and use explicit target_paths metadata. | Bridge applicability preflight and implementation-start packet. | |
| CQ-COMPLEXITY-001 | Yes | Keep the child scope narrow and avoid combining routing, adapters, dispatch, and role promotion in one implementation. | Loyal Opposition review of this child proposal. | |
| CQ-CONSTANTS-001 | Yes | Name role/status fields, closure gates, command surfaces, and registry fields rather than scattering literals. | Focused tests and code review in the child implementation report. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed behavior for missing prerequisite evidence, unsupported tools, destructive gates, and out-of-root paths. | Focused tests and code review in the child implementation report. | |
| CQ-DOCS-001 | Yes | Update only project closure and MEMORY surfaces after prerequisite evidence exists. | Diff review and bridge evidence. | |
| CQ-TESTS-001 | Yes | Add focused tests for promotion refusal and success with verified prerequisites. | Pytest plus scoped ruff check and format check. | |
| CQ-LOGGING-001 | Yes | Keep diagnostics structured and avoid persistent logs unless an existing surface owns them. | Test assertions or code review of changed command output. | |
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

After implementation, file the next bridge artifact on this thread as `NEW` with exact files changed, prerequisite bridge VERIFIED evidence, role promotion and rollback evidence, spec-to-test mapping, pytest and ruff results, implementation authorization packet hash, and any deferred issues or explicit statement that none remain.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
