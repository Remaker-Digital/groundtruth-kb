REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder session override; workspace E:\GT-KB; approval-policy never

# Ollama Phase 2 Dispatch Wiring Proposal - Machine-Readable Target Paths Amendment

bridge_kind: implementation_proposal
Document: gtkb-ollama-integration-phase-2-dispatch
Version: 005
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Work Item: WI-4375
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION
Owner Decision: DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE
Responds to: bridge/gtkb-ollama-integration-phase-2-dispatch-004.md
Supersedes: bridge/gtkb-ollama-integration-phase-2-dispatch-003.md
Date: 2026-06-05 UTC
Requires verification: true
Recommended commit type: feat
target_paths: ["harness-state/harness-registry.json", "scripts/cross_harness_bridge_trigger.py", "scripts/verify_ollama_dispatch.py", "groundtruth-kb/src/groundtruth_kb/bridge/notify.py", "groundtruth-kb/tests/test_doctor_ollama.py", "platform_tests/scripts/test_ollama_dispatch.py"]

## Amendment Purpose

This revision carries forward the GO'd dispatch scope from `bridge/gtkb-ollama-integration-phase-2-dispatch-004.md` and adds literal `target_paths` metadata for implementation authorization. It does not widen scope.

## Owner Decisions / Input

- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` authorizes completing remaining Ollama phases while preserving bridge GO/VERIFIED gates and self-review prohibition.
- `DELIB-20260663` leaves dispatch-substrate wiring as Phase 2+ work while preserving Phase 1 registered/no-active-role state.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` remains relevant because role and status are separate dispatch axes.
- `bridge/gtkb-ollama-integration-phase-2-004.md` authorizes child proposal filing; child implementation still requires this child thread's GO.
- Retained constraints: no harness D role promotion, project closure, `memory/MEMORY.md` update, credential lifecycle work, production deployment, out-of-root artifacts, or approval-gate bypass.

## Requirement Sufficiency

Existing requirements sufficient.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use synthetic fixtures and local config metadata only; no credentials or environment values. | Commit hook secret scan and diff review. | |
| CQ-PATHS-001 | Yes | Keep all target paths under E:\GT-KB and use explicit target_paths metadata. | Bridge applicability preflight and implementation-start packet. | |
| CQ-COMPLEXITY-001 | Yes | Keep dispatch scope separate from routing, adapters, and role promotion. | Loyal Opposition review of this amendment. | |
| CQ-CONSTANTS-001 | Yes | Name dispatch eligibility keys and status values. | Focused dispatch tests and code review in implementation report. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed unavailable-Ollama and unsupported-tool behavior. | Focused tests and implementation report. | |
| CQ-DOCS-001 | Yes | Update only dispatch readiness surfaces. | Diff review. | |
| CQ-TESTS-001 | Yes | Add focused dispatch readiness tests. | Pytest plus ruff check and format check. | |
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
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Scope Carried Forward

Implement the bounded dispatch readiness work from `bridge/gtkb-ollama-integration-phase-2-dispatch-003.md`: deterministic Ollama dispatch eligibility, fail-closed recipient logic, doctor/trigger readiness, and no active-role promotion.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
