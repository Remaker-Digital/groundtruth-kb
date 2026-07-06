NEW

# WI-4962 - Ollama-D Dispatch Reliability

bridge_kind: prime_proposal
Document: gtkb-wi4962-ollama-d-dispatch-reliability
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-06T00:56:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-WI4962-BATCH-B-20260705
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4962

target_paths: ["scripts/ollama_harness.py", "scripts/dispatcher_runtime.py", "scripts/verify_ollama_dispatch.py", ".api-harness/routing.toml", "config/dispatcher/rules.toml", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_ollama_routing_config.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime_worker_delivery.py", "platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py", "platform_tests/scripts/test_dispatch_non_transient_fast_trip.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4962 captures an Ollama-D dispatch reliability defect after D was realigned to Loyal Opposition: the dispatcher can rank D for LO work, but prior dispatch state showed launch failures and session-budget timeouts before an Ollama chat turn. That leaves low-cost/pre-paid cloud capacity idle and makes D look available while it cannot reliably complete a bounded bridge review.

Current evidence shows the D projection launches `scripts/ollama_harness.py` through the in-root Python, selects `--skill bridge-review --model deepseek-v4-pro-cloud`, and `.api-harness/routing.toml` already sets `routing.ollama.timeout_seconds = 3600`. The implementation should therefore diagnose and fix the concrete launch/timeout path rather than blindly increasing a constant. Likely work includes preserving Windows-safe subprocess launch normalization, verifying runtime timeout derivation from routing config, ensuring session-timeout and worker-lifetime budgets are aligned for D, improving failure classification around launch failures versus chat-turn timeouts, and resetting/validating D's circuit breaker only after the actual fault is fixed.

This proposal does not authorize credential lifecycle changes, production deployment, broad dispatcher rewrites, or ad hoc direct harness invocation. Any live exercise must go through dispatcher/control-plane surfaces or approved manual owner operation; automated verification should use focused tests and disposable fixture workspaces.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation work requires this proposal, Loyal Opposition review, latest `GO`, implementation-start authorization, implementation report, and verification before WI-4962 can be treated as terminal.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH bounds the owner-approved WI-4962 Batch B scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization satisfies owner approval only; it does not bypass bridge `GO`, target paths, report, or verification.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - D must remain a portable LO-capable harness rather than a one-off local workaround.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` - harness role/config changes must preserve the multi-harness role registry and dispatch configuration contract.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - dispatcher-controlled bridge work remains the supported automation path; implementation must not recreate retired poller or direct-launch behavior.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - dispatcher/harness reliability work must honor the GT-KB root and application boundary and must not treat adopter application files as directly integrated GT-KB artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every governing bridge, harness, and dispatcher requirement before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header binds this proposal to the active project authorization, project, and work item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map launch reliability, timeout behavior, and circuit-breaker recovery to concrete tests.
- `GOV-STANDING-BACKLOG-001` - WI-4962 remains the MemBase backlog authority and must be resolved only with bridge/report/verification evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the dispatch reliability defect must remain traceable through WI, PAUTH, bridge proposal, tests, implementation report, and terminal disposition.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation must preserve traceability across the artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4962 moves from backlog candidate to proposal, implementation, verification, and terminal resolution through explicit lifecycle states.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch B continuation and the active PAUTH covering WI-4962.
- WI-4962 backlog row - records the 2026-07-02 owner directive that pre-paid Ollama cloud credits were underutilized after D role realignment and that launch/timeout reliability faults remain.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - direct harness-to-harness launch is prohibited; live exercising must use bridge/dispatcher control-plane surfaces or owner/manual harness operation.
- Existing dispatch reliability bridge threads for WI-4933, WI-4986, WI-5001, and WI-5008 are relevant background, but this proposal is bounded to the WI-4962 D launch/timeout reliability defect.

## Owner Decisions / Input

Owner approval is already recorded by `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` and active authorization `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-WI4962-BATCH-B-20260705`. No fresh owner decision is required for this proposal.

## Requirement Sufficiency

Existing requirements are sufficient. The backlog item defines the failure modes, acceptance condition, and forbidden credential/reset ordering: fix launch and timeout faults first, then reset/validate the circuit breaker only after reliability is corrected. The PAUTH constrains the allowed mutation classes and explicitly keeps credential lifecycle out of scope.

## Spec-Derived Verification Plan

| Requirement | Verification |
|---|---|
| D launch path is reliable and Windows-safe | Add or update dispatcher runtime tests around D's projected headless argv, `_normalize_argv_head`, and `_spawn_harness` so relative in-root Python paths and subprocess failures are classified deterministically. |
| D session budget aligns with cloud latency | Extend `platform_tests/scripts/test_ollama_harness.py` or routing tests so `routing.ollama.timeout_seconds` derives both operation and session timeout correctly, and explicit CLI overrides preserve expected behavior. |
| Launch failure and chat-turn timeout are classified separately | Add tests in dispatcher failure/circuit-breaker coverage so `subprocess_execution_failed`, worker timeout, and previous-launch-failed cooldown produce the intended state and do not permanently suppress D after recovery. |
| D readiness can be checked without direct invocation | Update `scripts/verify_ollama_dispatch.py` and its tests so readiness/smoke evidence uses disposable fixtures and dispatcher/control-plane-compatible checks; any live dispatch proof must avoid ad hoc direct harness invocation. |
| Circuit breaker reset is post-fix only | Implementation report must show launch/timeout fixes and tests before any D circuit-breaker reset or validation evidence is claimed. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` bridge lifecycle | Implementation must run only after latest `GO` and `implementation_authorization.py begin --bridge-id gtkb-wi4962-ollama-d-dispatch-reliability`; report must cite target-path authorization evidence. |

Minimum expected verification commands after implementation:

```text
python -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_ollama_routing_config.py platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short
python -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_worker_delivery.py platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py platform_tests/scripts/test_dispatch_non_transient_fast_trip.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4962-ollama-d-dispatch-reliability --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4962-ollama-d-dispatch-reliability
```

## Risk / Rollback

Risk is concentrated in making D appear healthy while it still cannot complete work, or in bypassing dispatcher safety by directly spawning harnesses. Keep tests fixture-based, use dispatcher/control-plane status surfaces for live evidence, avoid credential lifecycle changes, and roll back as one commit if dispatch state or circuit-breaker behavior regresses.

## Bridge Filing

This proposal is filed as the next status-bearing numbered bridge file for `gtkb-wi4962-ollama-d-dispatch-reliability`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix - the expected implementation corrects dispatch launch/timeout reliability for the Ollama-D LO harness.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
