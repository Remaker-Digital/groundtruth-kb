NEW

# WI-5221 - Establish Prime worker role provenance before work-intent acquisition

bridge_kind: prime_proposal
Document: gtkb-wi5221-prime-preclaim-worker-provenance
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-13 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5221-PRIME-WORKER-PROVENANCE-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5221

target_paths: ["scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Canonical role authority requires document-backed worker provenance before a
Prime `go_implementation` claim. The runtime and daemon currently mint a
dispatch/session ID and acquire the claim before worker startup, while the
worker envelope is created only after launch. Production Prime dispatch
therefore fails closed as `work_intent_acquire_failed`; six deterministic
fanout/quarantine tests reproduce it.

Add one shared runtime helper that establishes the exact dispatcher-composed
worker session envelope before any Prime claim, and invoke it from both runtime
and daemon paths. Envelope creation failure remains a non-launch. LO document
leases, review independence, registry authority, and all generous allowances
remain unchanged.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` - headless role authority must be dispatcher-composed and document-backed.
- `DCL-SESSION-ROLE-RESOLUTION-001` - the worker session must resolve the exact harness, role, and dispatch provenance.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - headless authority remains distinct from interactive transcript overrides.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - valid selected Prime work must reach the chosen harness after claim acquisition.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - GO implementation claims and bridge lifecycle remain canonical.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - session envelopes and 29,400-second worker lifetimes remain consistent.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Prime-capable harnesses require equivalent prelaunch authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - role and dispatch requirements are linked before mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact project, WI, PAUTH, and targets are declared.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification executes runtime and daemon claim/fanout tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the production regression is separate from stale fixtures.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - WI, TEST, PAUTH, bridge, source, and verification remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - deterministic production non-launch triggers governed correction.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all envelopes and targets remain under the GT-KB root.

## Prior Deliberations

- `DELIB-202666173` - require genuine PB/LO dispatch proof and correct every discovered defect.
- `INTAKE-7073854a` - infrastructure owns deterministic worker identity and claim ordering.
- `bridge/gtkb-wi5208-concurrent-dispatch-launch-ledger-004.md` - VERIFIED concurrent launches retain per-dispatch identity and exact-once reconciliation.

## Owner Decisions / Input

- `DELIB-202666173` supplies owner authority for genuine dispatcher proof defects.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5221-PRIME-WORKER-PROVENANCE-20260712` bounds the four paths and forbids gate weakening.

## Requirement Sufficiency

Existing requirements sufficient - session-role authority already requires the
worker envelope and work-intent acquisition already requires Prime eligibility;
only their execution order is defective.

## Proposed Scope

- Add a shared fail-closed helper accepting project root, dispatch target, and exact dispatch/session ID.
- Delegate to canonical `groundtruth_kb.session.envelope.ensure_worker_session` with harness ID/name, `prime-builder`, dispatcher-composition source, canonical init keyword, and dispatch run ID.
- Call it immediately before `_acquire_prime_work_intent_batch` in daemon and runtime Prime paths.
- On envelope failure, record a classified non-launch and acquire no claim.
- Reuse the same envelope when the worker starts; do not create alternate role authority.
- Preserve LO paths, selected-document leases, claim TTLs, finalization, and runtime allowances.

## Spec-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| Session role authority | Unit-test helper arguments and written envelope | Exact dispatch ID, target harness, Prime role, canonical keyword, and dispatcher provenance. |
| Claim ordering | Runtime and daemon tests instrument envelope and acquire calls | Envelope succeeds before first claim acquisition. |
| Failure closure | Inject envelope write/validation failure | No claim and no process launch; classified diagnostic retained. |
| Prime fanout | Existing WI-4992/WI-4994 tests | Independent docs launch or stand down according to claims. |
| LO isolation | Existing lease/review tests | No LO envelope or lease behavior changes. |
| Generous allowances | Existing lifetime/lease tests | 29,400-second workers and 29,700-second leases unchanged. |
| Full regression | Run both dispatcher modules alone and together after WI-5220 | Green. |

## Acceptance Criteria

- Every Prime claim session has accepted worker role provenance before acquisition.
- Runtime and daemon paths use one shared helper and identical authority fields.
- Envelope failure acquires no claim and launches no worker.
- Same-session independence, role registry, bridge gates, leases, and finalization remain unchanged.
- Existing Prime fanout/quarantine behavior is restored.
- WI-5217 and WI-5220 hunks in overlapping paths remain separately governed and finalized.

## Risk / Rollback

The risk is creating role authority for a dispatch that never launches. The
envelope is keyed to the exact dispatch ID, records dispatcher composition, and
failed-launch reconciliation remains authoritative; no interactive role state
is changed. Rollback reverts the four-path focused patch.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5221-prime-preclaim-worker-provenance`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - restores production Prime dispatch ordering without weakening authority.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
