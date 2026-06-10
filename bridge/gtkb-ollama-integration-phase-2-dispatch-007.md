REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder session override; workspace E:\GT-KB; approval-policy never

# Ollama Phase 2 Dispatch Wiring Proposal - REVISED

bridge_kind: prime_proposal
Document: gtkb-ollama-integration-phase-2-dispatch
Version: 007
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Work Item: WI-4381
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION
Owner Decision: DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE
Responds to: bridge/gtkb-ollama-integration-phase-2-dispatch-006.md
Supersedes: bridge/gtkb-ollama-integration-phase-2-dispatch-005.md
Date: 2026-06-05 UTC
Requires verification: true
Recommended commit type: feat
target_paths: ["harness-state/harness-registry.json", "scripts/cross_harness_bridge_trigger.py", "scripts/verify_ollama_dispatch.py", "groundtruth-kb/src/groundtruth_kb/bridge/notify.py", "groundtruth-kb/tests/test_doctor_ollama.py", "platform_tests/scripts/test_ollama_dispatch.py"]

## Revision Response

This revision addresses `bridge/gtkb-ollama-integration-phase-2-dispatch-006.md`:

- F1: adds a substantive `## Prior Deliberations` section in this operative proposal.
- F2: replaces terminal `WI-4375` with active successor `WI-4381`; the supported backlog CLI does not permit `resolved` to `backlogged` stage transitions.
- F3: restores the explicit `## Specification-Derived Verification Plan` section.
- F4: restores the artifact-governance advisory spec links from the prior GO'd proposal.

Scope remains the previously GO'd dispatch readiness and fail-closed recipient logic plus the machine-readable `target_paths` required by implementation authorization.

## Owner Decisions / Input

- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` records the owner directive to complete remaining Ollama phases while preserving bridge GO/VERIFIED gates and the self-review prohibition.
- `DELIB-20260663` records the Phase 1 owner decision set and explicitly leaves dispatch-substrate wiring as Phase 2+ work while keeping harness D registered with no active role in Phase 1.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` remains relevant to dispatch eligibility because role and status are separate axes.
- `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION` v5 authorizes this child proposal and later child implementation only after Loyal Opposition GO; it includes `WI-4381`.
- `bridge/gtkb-ollama-integration-phase-2-004.md` authorizes filing this child proposal but does not authorize implementation until this child receives GO.
- This proposal does not authorize promoting harness D to an active role, closing project work items, changing `memory/MEMORY.md`, credential lifecycle work, production deployment, out-of-root artifacts, or bypassing formal/narrative approval gates.

## Prior Deliberations

Deliberation and bridge context reviewed for this revision:

- `DELIB-20260663`: Phase 1 owner decisions, including that dispatch wiring remains Phase 2+ scope and harness D remained registered with no active role in Phase 1.
- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE`: owner directive to complete remaining Ollama Phase 2+ work through child bridge GO/VERIFIED gates.
- `DELIB-20260679`: confirms Phase 1 did not promote harness D or wire it into cross-harness dispatch.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`: role/status orthogonality context for dispatch eligibility.
- `bridge/gtkb-ollama-integration-phase-2-004.md`: parent GO authorizing child proposal filing only.
- `bridge/gtkb-ollama-integration-phase-2-010.md`: parent scaffolding VERIFIED, explicitly leaving child source/config implementation to the child bridge threads.
- Child thread context: `-003` was GO'd at `-004`; `-005` was NO-GO'd at `-006` because the amendment was not self-contained and cited terminal `WI-4375`.

## Backlog And Authorization Repair Evidence

- Original child WI `WI-4375` is terminal/resolved due parent bridge reconciler evidence, not child implementation verification.
- Supported CLI dry-run rejected `resolved` to `backlogged` stage transition, so the repair path is active successor `WI-4381`.
- `WI-4381` is `resolution_status=open`, `stage=backlogged`, depends on `WI-4375`, and is attached to `PROJECT-GTKB-OLLAMA-INTEGRATION` as membership order 17.
- PAUTH v5 rowid 142 includes `WI-4381` while retaining original child WI traceability.

## Requirement Sufficiency

Existing requirements sufficient. No new owner choice is required before Loyal Opposition review.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use synthetic fixtures and local config metadata only; no credentials or environment values. | Commit hook secret scan and diff review. | |
| CQ-PATHS-001 | Yes | Keep all target paths under E:\GT-KB and use explicit target_paths metadata. | Bridge applicability preflight and implementation-start packet. | |
| CQ-COMPLEXITY-001 | Yes | Keep the child scope narrow and avoid combining routing, adapters, dispatch, and role promotion in one implementation. | Loyal Opposition review of this child proposal. | |
| CQ-CONSTANTS-001 | Yes | Name dispatch eligibility fields, command surfaces, and registry fields rather than scattering literals. | Focused tests and code review in the child implementation report. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed behavior for unavailable daemon, unsupported tools, destructive gates, and out-of-root paths. | Focused tests and code review in the child implementation report. | |
| CQ-DOCS-001 | Yes | Update only operational surfaces needed by dispatch readiness. | Diff review. | |
| CQ-TESTS-001 | Yes | Add focused tests for dispatch command generation, eligibility, and fail-closed behavior. | Pytest plus scoped ruff check and format check. | |
| CQ-LOGGING-001 | Yes | Keep diagnostics structured and avoid persistent logs unless an existing surface owns them. | Test assertions or code review of changed command output. | |
| CQ-VERIFICATION-001 | Yes | File a post-implementation report with exact commands and observed results before VERIFIED review. | Bridge implementation report and LO verification. | |

## Target Paths

- `harness-state/harness-registry.json`
- `scripts/cross_harness_bridge_trigger.py`
- `scripts/verify_ollama_dispatch.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`
- `groundtruth-kb/tests/test_doctor_ollama.py`
- `platform_tests/scripts/test_ollama_dispatch.py`

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
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Proposed Scope

Implement bounded cross-harness dispatch readiness for harness D:

- Add a deterministic verification surface for Ollama dispatch eligibility and fail-closed behavior.
- Wire the cross-harness bridge trigger and notification code so harness D can be detected as a dispatch-capable target only when local prerequisites and role eligibility are satisfied.
- Preserve durable role authority by avoiding any active-role promotion in this child.
- Add tests for unavailable Ollama, missing shim prerequisites, unsupported tools, and eligible-dispatch metadata.

## Out Of Scope

- Multi-model route selection.
- `.ollama/skills/` adapter generation.
- Promoting harness D to active Prime Builder or Loyal Opposition role.
- Closing project work items or updating `memory/MEMORY.md`.
- Credential handling, production deployment, or external network model provisioning.

## Specification-Derived Verification Plan

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`: verify dispatch readiness depends on onboarding contract and doctor-visible prerequisites.
- `GOV-HARNESS-ROLE-PORTABILITY-001`: verify dispatch metadata is portable across harness roles without assigning a role inside this child.
- `GOV-SESSION-ROLE-AUTHORITY-001`: verify durable role registry and active-session override semantics remain authoritative.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`: verify dispatch fails closed when Ollama cannot provide required bridge-review tools.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`: verify dispatched bridge outputs remain required to carry author metadata.

## Implementation Report Requirements

After implementation, file the next bridge artifact on this thread as `NEW` with exact files changed, dispatch readiness matrix, spec-to-test mapping, pytest and ruff results, implementation authorization packet hash, and any deferred issues or explicit statement that none remain.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
