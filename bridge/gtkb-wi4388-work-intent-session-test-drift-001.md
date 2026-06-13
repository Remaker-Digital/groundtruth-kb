NEW

# WI-4388 Work-Intent Session Test Drift Reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi4388-work-intent-session-test-drift
Version: 001
Author: Codex Prime Builder (harness A)
Date: 2026-06-12 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-wi4388-work-intent-test-drift
author_model: GPT-5 Codex
author_model_version: 2026-06-12
author_model_configuration: Codex desktop; Prime Builder; reliability fast-lane test reconciliation

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4388

target_paths: ["platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Reconcile a stale focused regression test for WI-4388 after the verified FAB10/session-id direction changed the Prime work-intent holder contract from a synthetic `trigger-dispatched-...` prefix to the actual dispatch run id. Current production code and the newer `test_fab10_work_intent_claim_contract_uses_child_dispatch_id` assertion agree that `_work_intent_session_id(dispatch_id) == dispatch_id`, and the Ollama guard payload tests already verify that `GTKB_BRIDGE_POLLER_RUN_ID` wins over parent harness session variables.

The only proposed mutation is to update `platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py` so its held/free work-intent assertion checks the launched `work_intent_session_id` / dispatch id instead of the retired prefix. No source, hook, bridge dispatcher, harness registry, or MemBase mutation is in scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal and later implementation report must flow through the file bridge; `bridge/INDEX.md` remains canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal cites concrete governing requirements before Loyal Opposition review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries parser-visible project authorization, project, work item, and inline JSON `target_paths` metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map this test-only change to executed focused tests, Ruff check, and format check before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - WI-4388 remains the live backlog authority for the Ollama dispatch session-id reliability thread.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - even this small test reconciliation must not bypass project authorization, GO, and implementation-start evidence.
- `GOV-RELIABILITY-FAST-LANE-001` - the change is a bounded reliability regression-test repair inside `PROJECT-GTKB-RELIABILITY-FIXES`.
- `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001` - the test expectation concerns the canonical bridge work-intent session-id resolution order.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing owner authorization for bounded reliability fixes under the reliability fast lane.
- `DELIB-20260897` - prior Ollama dispatch baseline before default-role promotion.
- `DELIB-20260909` - prior verified Ollama dispatch hardening baseline cited by later WI-4388 verification work.
- `bridge/gtkb-ollama-lo-dispatch-session-propagation-008.md` - VERIFIED predecessor that established the dispatch-run-first session-id contract for WI-4388.
- `bridge/gtkb-ollama-dispatch-stall-retry-cap-006.md` - VERIFIED follow-up that kept WI-4388 as the active reliability work item while hardening dispatch retry behavior.

## Owner Decisions / Input

No new owner decision is required. The change is covered by the active standing reliability authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, the existing WI-4388 reliability work item, and the current owner directive to continue Prime Builder-actionable bridge/backlog work autonomously while respecting governance gates.

## Requirement Sufficiency

Existing requirements are sufficient. The prior VERIFIED WI-4388 thread established that bridge work-intent surfaces must prefer `GTKB_BRIDGE_POLLER_RUN_ID` and use the dispatch run id for guarded Ollama work. This proposal only aligns one stale focused test with that verified contract; it does not create new product behavior or require a new/revised requirement.

## Spec-Derived Verification Plan

| Spec / governing surface | Proposed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | File proposal and implementation report through the bridge helper; run bridge applicability and clause preflights before report filing. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `scripts/implementation_authorization.py begin --bridge-id gtkb-wi4388-work-intent-session-test-drift` must accept the GO'd proposal and target path metadata before implementation. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation report must cite the issued implementation-start packet hash for this bridge id. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest command below must pass and be mapped in the implementation report. |
| `GOV-STANDING-BACKLOG-001` and `GOV-RELIABILITY-FAST-LANE-001` | Report must tie the test-only change to WI-4388 and the standing reliability PAUTH with no source or governance mutation. |
| `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001` | Focused tests must show dispatch id remains the work-intent holder id and Ollama guard payloads still prefer `GTKB_BRIDGE_POLLER_RUN_ID`. |

```text
$env:GTKB_NO_CROSS_HARNESS_TRIGGER=$null; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger_work_intent.py platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_fab10_work_intent_claim_contract_uses_child_dispatch_id platform_tests\scripts\test_verify_ollama_dispatch.py::test_ollama_session_resolver_prefers_dispatch_run_id platform_tests\scripts\test_verify_ollama_dispatch.py::test_ollama_guard_payload_uses_dispatch_run_id -q --tb=short
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check platform_tests\scripts\test_cross_harness_bridge_trigger_work_intent.py
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check platform_tests\scripts\test_cross_harness_bridge_trigger_work_intent.py
```

## Risk / Rollback

Risk is low and confined to test coverage: changing the assertion incorrectly could mask a future work-intent handoff regression. The mitigation is to assert the free-thread holder equals the launch metadata's `work_intent_session_id` and that this value equals the launch dispatch id, rather than merely checking a loose prefix. Rollback is a normal single-file test revert plus a bridge follow-up note; no runtime state migration or harness topology change is involved.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
the `gtkb-wi4388-work-intent-session-test-drift` document list in `bridge/INDEX.md`; no prior version is deleted or
rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

test: the implementation scope is a focused regression-test expectation update with no source mutation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
