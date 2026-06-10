REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder session override; workspace E:\GT-KB; approval-policy never

# Ollama Phase 2 Skill Adapter Generation Proposal - Machine-Readable Target Paths Amendment

bridge_kind: prime_proposal
Document: gtkb-ollama-integration-phase-2-adapters
Version: 005
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Work Item: WI-4374
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION
Owner Decision: DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE
Responds to: bridge/gtkb-ollama-integration-phase-2-adapters-004.md
Supersedes: bridge/gtkb-ollama-integration-phase-2-adapters-003.md
Date: 2026-06-05 UTC
Requires verification: true
Recommended commit type: feat
target_paths: ["scripts/generate_ollama_skill_adapters.py", ".ollama/skills/**", ".ollama/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/scripts/test_generate_ollama_skill_adapters.py", "platform_tests/scripts/test_ollama_skill_adapters.py"]

## Amendment Purpose

This revision carries forward the GO'd adapter scope from `bridge/gtkb-ollama-integration-phase-2-adapters-004.md` and adds literal `target_paths` metadata for implementation authorization. It does not widen scope.

## Owner Decisions / Input

- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` authorizes completing remaining Ollama phases while preserving bridge GO/VERIFIED gates and self-review prohibition.
- `DELIB-20260663` leaves `.ollama/skills/` adapter generation as Phase 2+ work.
- `bridge/gtkb-ollama-integration-phase-2-004.md` authorizes child proposal filing; child implementation still requires this child thread's GO.
- Retained constraints: no routing selection changes, dispatch wiring, role promotion, credential lifecycle work, production deployment, out-of-root artifacts, or approval-gate bypass.

## Requirement Sufficiency

Existing requirements sufficient.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use synthetic fixtures and local config metadata only; no credentials or environment values. | Commit hook secret scan and diff review. | |
| CQ-PATHS-001 | Yes | Keep all target paths under E:\GT-KB and use explicit target_paths metadata. | Bridge applicability preflight and implementation-start packet. | |
| CQ-COMPLEXITY-001 | Yes | Keep adapter scope separate from routing, dispatch, and role promotion. | Loyal Opposition review of this amendment. | |
| CQ-CONSTANTS-001 | Yes | Name generator fields, manifest keys, and registry metadata. | Focused adapter tests and code review in implementation report. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed stale checks and tool parity behavior. | Focused tests and implementation report. | |
| CQ-DOCS-001 | Yes | Avoid broad canonical skill narrative churn. | Diff review. | |
| CQ-TESTS-001 | Yes | Add focused generator/manifest/drift tests. | Pytest plus ruff check and format check. | |
| CQ-LOGGING-001 | Yes | Keep diagnostics structured and avoid persistent logs. | Test/code review. | |
| CQ-VERIFICATION-001 | Yes | File a post-implementation report with exact commands and observed results. | Bridge implementation report and LO verification. | |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `ADR-OLLAMA-HARNESS-ADOPTION-001`
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `DCL-CONCEPT-ON-CONTACT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Scope Carried Forward

Implement the deterministic adapter generator from `bridge/gtkb-ollama-integration-phase-2-adapters-003.md`: generate `.ollama/skills/` adapters and manifest from canonical skill metadata, preserve canonical skill files as source of truth, and add drift/check-mode tests.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
