REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder session override; workspace E:\GT-KB; approval-policy never

# Ollama Phase 2 Skill Adapter Generation Proposal - REVISED

bridge_kind: prime_proposal
Document: gtkb-ollama-integration-phase-2-adapters
Version: 003
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Work Item: WI-4374
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION
Owner Decision: DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE
Responds to: bridge/gtkb-ollama-integration-phase-2-adapters-002.md
Supersedes: bridge/gtkb-ollama-integration-phase-2-adapters-001.md
Date: 2026-06-05 UTC
Requires verification: true
Recommended commit type: feat

## Revision Response

This revision addresses NO-GO F1 in `bridge/gtkb-ollama-integration-phase-2-adapters-002.md` by adding a substantive `## Owner Decisions / Input` section. Scope, target paths, and verification mapping remain bounded to adapter generation and drift checks.

## Owner Decisions / Input

- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` records the owner directive to complete remaining Ollama phases while preserving bridge GO/VERIFIED gates and the self-review prohibition.
- `DELIB-20260663` records the Phase 1 owner decision set and explicitly leaves `.ollama/skills/` adapter generation as Phase 2+ work.
- `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION` authorizes this child proposal and later child implementation only after Loyal Opposition GO.
- `bridge/gtkb-ollama-integration-phase-2-004.md` authorizes filing this child proposal but does not authorize implementation until this child receives GO.
- This proposal does not authorize route selection changes, dispatch wiring, role promotion, credential lifecycle work, production deployment, out-of-root artifacts, or bypassing formal/narrative approval gates.

## Requirement Sufficiency

Existing requirements sufficient.

The owner directive, Phase 1 owner-decision anchor, Phase 1 terminal verification at `bridge/gtkb-ollama-integration-phase-1-008.md`, and Phase 2 umbrella GO provide enough direction for this child. No new owner choice is required before Loyal Opposition review.

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

- `scripts/generate_ollama_skill_adapters.py`
- `.ollama/skills/**`
- `.ollama/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`
- `platform_tests/scripts/test_generate_ollama_skill_adapters.py`
- `platform_tests/scripts/test_ollama_skill_adapters.py`

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
- `DCL-CONCEPT-ON-CONTACT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Proposed Scope

Implement a deterministic adapter generator for Ollama-visible skill surfaces:

- Add a generator that reads canonical GT-KB skill metadata and emits `.ollama/skills/` adapter files plus `.ollama/skills/MANIFEST.json`.
- Preserve canonical skill files as the source of truth; generated adapter text must identify its source path and generation metadata.
- Add a check mode that detects stale, missing, or manually edited generated adapters.
- Register adapter generation status in the harness capability registry only to the extent needed for deterministic doctor and test surfaces.
- Preserve concept-on-contact constraints by keeping canonical knowledge in source skill files and minimizing duplicated narrative content in adapters.

## Out Of Scope

- Multi-model route selection.
- Cross-harness dispatch wiring.
- Harness D role promotion or project closure mechanics.
- Rewriting canonical skill bodies beyond minimal adapter metadata required for deterministic generation.
- Credential handling, production deployment, or external network model provisioning.

## Specification-Derived Verification Plan

- `DCL-OLLAMA-TOOL-PARITY-GATE-001`: verify generated adapters do not advertise unavailable tools or bypass parity failure behavior.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`: verify generated adapter metadata preserves the required author metadata contract for downstream Ollama output.
- `ADR-OLLAMA-HARNESS-ADOPTION-001`: verify adapters remain local harness support artifacts and do not create an external service dependency.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`: verify the adapter manifest can feed onboarding and doctor checks.
- `DCL-CONCEPT-ON-CONTACT-001`: verify adapter output avoids broad duplication of canonical knowledge surfaces.

## Implementation Report Requirements

After implementation, file the next bridge artifact on this thread as `NEW` with exact files changed, generated manifest summary and stale-check evidence, spec-to-test mapping, pytest and ruff results, implementation authorization packet hash, and any deferred issues or explicit statement that none remain.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
