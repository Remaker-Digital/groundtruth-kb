REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder session override; workspace E:\GT-KB; approval-policy never

# Ollama Phase 2 Routing Expansion Proposal - Machine-Readable Target Paths Amendment

bridge_kind: prime_proposal
Document: gtkb-ollama-integration-phase-2-routing
Version: 005
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Work Item: WI-4373
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION
Owner Decision: DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE
Responds to: bridge/gtkb-ollama-integration-phase-2-routing-004.md
Supersedes: bridge/gtkb-ollama-integration-phase-2-routing-003.md
Date: 2026-06-05 UTC
Requires verification: true
Recommended commit type: feat
target_paths: [".ollama/routing.toml", "scripts/ollama_harness.py", "config/agent-control/harness-capability-registry.toml", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_ollama_routing_config.py"]

## Amendment Purpose

This revision carries forward the GO'd routing scope from `bridge/gtkb-ollama-integration-phase-2-routing-004.md` and adds literal `target_paths` metadata so `scripts/implementation_authorization.py begin --bridge-id gtkb-ollama-integration-phase-2-routing` can issue the implementation packet. It does not widen scope.

## Owner Decisions / Input

- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` authorizes completing remaining Ollama phases while preserving bridge GO/VERIFIED gates and self-review prohibition.
- `DELIB-20260663` leaves multi-model routing and skill overrides as Phase 2+ work.
- `bridge/gtkb-ollama-integration-phase-2-004.md` authorizes child proposal filing; child implementation still requires this child thread's GO.
- Retained constraints: no adapter generation, dispatch wiring, role promotion, credential lifecycle work, production deployment, out-of-root artifacts, or approval-gate bypass.

## Requirement Sufficiency

Existing requirements sufficient.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use synthetic fixtures and local config metadata only; no credentials or environment values. | Commit hook secret scan and diff review. | |
| CQ-PATHS-001 | Yes | Keep all target paths under E:\GT-KB and use explicit target_paths metadata. | Bridge applicability preflight and implementation-start packet. | |
| CQ-COMPLEXITY-001 | Yes | Keep routing scope separate from adapters, dispatch, and role promotion. | Loyal Opposition review of this amendment. | |
| CQ-CONSTANTS-001 | Yes | Name schema keys, route fields, and model identifiers rather than scattering literals. | Focused routing tests and code review in implementation report. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed invalid route and unsupported tool behavior. | Focused tests and implementation report. | |
| CQ-DOCS-001 | Yes | Update only routing-related operational surfaces. | Diff review. | |
| CQ-TESTS-001 | Yes | Add focused routing parser/selection tests. | Pytest plus ruff check and format check. | |
| CQ-LOGGING-001 | Yes | Keep diagnostics structured and avoid persistent logs. | Test/code review. | |
| CQ-VERIFICATION-001 | Yes | File a post-implementation report with exact commands and observed results. | Bridge implementation report and LO verification. | |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `ADR-OLLAMA-HARNESS-ADOPTION-001`
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Scope Carried Forward

Implement the bounded routing expansion from `bridge/gtkb-ollama-integration-phase-2-routing-003.md`: multiple model rows, per-skill routing overrides, advertised-model validation, and fail-closed route selection while preserving Phase 1 author metadata and tool-parity behavior.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
