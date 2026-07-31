NEW

# gtkb-wi4904-provider-harness-dispatch-readiness - Ollama/OpenRouter provider dispatch readiness

bridge_kind: prime_proposal
Document: gtkb-wi4904-provider-harness-dispatch-readiness
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-29T10:11:13Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f12d3-184b-7f01-aebf-2d2308b377a7
author_model: GPT-5 Codex
author_model_version: current Codex runtime
author_model_configuration: Auto-builder autonomous Prime Builder run

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4904

target_paths: ["scripts/verify_ollama_dispatch.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/ops/dispatch_parity.py", "scripts/harness_parity_phase2.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_openrouter_routing_deepseek.py", "platform_tests/scripts/test_dispatch_env_local_auth_loader.py", "platform_tests/scripts/test_dispatch_parity.py", "platform_tests/scripts/test_harness_parity_phase2.py", "config/dispatcher/rules.toml", "config/agent-control/harness-capability-registry.toml", ".api-harness/routing.toml"]

implementation_scope: source test config protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the proposal-ready slice of `WI-4904`: make the Ollama (`D`) and OpenRouter (`F`) provider-backed harnesses comparable, testable Loyal Opposition dispatch targets for the routes they can actually support. The work should verify provider routing, credential/env loading behavior, model selection, prompt/tool parity, timeout and provider-outage classification, no-window launcher discipline, benchmark compatibility, and dispatcher/report visibility.

This proposal does not promote Ollama or OpenRouter into Prime Builder event sources, does not change owner credentials, does not perform production deployment, and does not change the blocked `WI-4885` topology decision. Provider harnesses remain receive-only unless a separate governed thread changes that capability.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected provider-harness source/config changes require proposal, GO, implementation-start authorization, report, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the implementation to governing requirements and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target path metadata are required for implementation eligibility.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - completion must map each readiness claim to executed tests or checks.
- `GOV-STANDING-BACKLOG-001` - `WI-4904` is the governed backlog row for provider-harness readiness work.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active Phase 2 PAUTH bounds the allowed mutation classes and included work items.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - provider-backed harnesses must preserve cross-harness bridge/governance behavior relative to the Codex baseline.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - provider readiness must be represented by explicit capability, guard, author metadata, and routing evidence.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - implementation must avoid permanent role assumptions and keep provider limitations explicit.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness requires deterministic evidence for supported provider surfaces and accepted waivers for unsupported surfaces.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher routing, provider backoff, and reporting changes must stay within the governed dispatcher architecture.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - readiness results and gaps must be durable governed artifacts rather than harness-local notes.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - provider capability evidence should remain inspectable and reusable for future parity work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - new provider gaps must route to backlog/waiver/review-trigger artifacts instead of hidden drift.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner made Harness Parity Phase 2 release-blocking and authorized practical parity with typed waivers for impossible gaps.
- `bridge/gtkb-wi4901-phase2-waiver-registry-001.md` through `-004.md` - implemented and verified the typed waiver registry that this provider work must feed when a gap is impossible.
- `bridge/gtkb-wi4906-harness-release-health-probes-001.md` through `-004.md` - implemented strict release-health/no-window readiness probes that provider readiness must satisfy.
- `bridge/gtkb-wi4885-dispatch-topology-activation-008.md` - latest NO-GO holding topology activation pending owner decision; this proposal avoids topology activation.
- `bridge/gtkb-wi4901-phase2-release-waiver-closure-001.md` and `-002.md` - current release-waiver closure proposal/GO that depends on provider gaps being explicit rather than hidden.
- `WI-4904` - backlog row requiring Ollama/OpenRouter readiness probes, error classification, benchmark compatibility, and dispatcher report evidence.

## Owner Decisions / Input

No new owner decision is required before Loyal Opposition review. Implementation is covered by `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`, whose owner decision is `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE`, and `WI-4904` is included in that release-blocking project scope.

This proposal explicitly excludes credential rotation, credential disclosure, paid provider deployment changes, dispatcher target activation beyond the existing receive-only provider roles, and any durable role reassignment.

## Requirement Sufficiency

Existing requirements sufficient. `WI-4904` defines the provider-readiness outcome, and the active Phase 2 project authorization covers source, test, config, and protocol changes for provider harness parity. The linked bridge, project-authorization, cross-harness enforcement, dispatcher architecture, release-readiness, and harness-onboarding requirements define the implementation and verification constraints.

## Spec-Derived Verification Plan

Planned verification:

```text
python -m pytest platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short
python -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_openrouter_routing_deepseek.py -q --tb=short
python -m pytest platform_tests/scripts/test_dispatch_env_local_auth_loader.py platform_tests/scripts/test_dispatch_parity.py platform_tests/scripts/test_harness_parity_phase2.py -q --tb=short
python scripts/verify_ollama_dispatch.py --help
python scripts/ollama_harness.py --help
python scripts/openrouter_harness.py --help
python scripts/ops/dispatch_parity.py --help
gt bridge dispatch status --json
```

Expected coverage:

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: implementation-start must authorize exactly the target paths listed above before protected mutation.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001`, and `GOV-HARNESS-ROLE-PORTABILITY-001`: provider harnesses must expose supported/unsupported route evidence without claiming event-source parity they do not have.
- `ADR-DISPATCHER-ARCHITECTURE-001`: dispatcher status/reporting must keep Ollama and OpenRouter behavior inside the governed dispatcher model, including provider failure classification.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`: strict release-health output must show supported provider routes as healthy or blocked by typed, visible waivers.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report must carry forward this mapping with exact command output and observed results.

## Risk / Rollback

Primary risk is conflating receive-only provider dispatch readiness with event-source parity. The implementation must preserve that distinction in dispatcher reporting, readiness output, and any waiver/candidate-work records. Secondary risk is accidentally relying on live credentials in tests; tests must mock or classify missing credentials cleanly unless a command is explicitly a live readiness probe.

Rollback is a single implementation commit revert. No production deployment, credential lifecycle action, or topology activation is in scope.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4904-provider-harness-dispatch-readiness`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat:

Justification: this adds or hardens provider-backed harness readiness capability surfaces plus focused regression evidence.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
