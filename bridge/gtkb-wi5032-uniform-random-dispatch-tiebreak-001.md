NEW

# WI-5032 — Uniform-random terminal tiebreak for fully tied dispatch candidates

bridge_kind: prime_proposal
Document: gtkb-wi5032-uniform-random-dispatch-tiebreak
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-06 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION-WI5032-TIEBREAK-20260706
Project: PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION
Work Item: WI-5032

target_paths: ["config/dispatcher/rules.toml", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/tafe_dispatch_policy.py", "scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_dispatch_priority.py", "platform_tests/scripts/test_dispatcher_runtime.py", "groundtruth-kb/tests/test_tafe_dispatch_policy.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-5032 proposes the first, narrow slice of the dispatch-ranking normalization owner decision: remove `harness_id` as the deterministic terminal winner when otherwise eligible dispatch candidates are fully tied. When all configured ranking dimensions and hard eligibility gates are equal, the live selector should choose uniformly at random from the tied candidate set rather than always choosing the lexicographically smallest harness id.

The implementation must preserve every non-tied ordering decision, hard eligibility gate, role boundary, dispatchability rule, project authorization gate, and implementation-start gate. It must not flatten or otherwise change harness ranking values; WI-5033 remains the separately sequenced follow-on for value flattening after this tiebreak behavior is in place.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the proposal must enter the numbered bridge chain through the governed writer; implementation waits for a latest `GO`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites the governing dispatcher, project-authorization, and backlog specifications before review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal carries `Project Authorization`, `Project`, and `Work Item` metadata for implementation-start validation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report must map this proposal's dispatcher and governance requirements to executed tests.
- `GOV-STANDING-BACKLOG-001` — WI-5032 remains visible in the MemBase backlog until bridge completion or another terminal disposition.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the bounded PAUTH is owner approval evidence for WI-5032 only and does not permit unrelated dispatcher work.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the PAUTH does not bypass Loyal Opposition `GO`, target paths, spec-derived tests, implementation report, or verification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — dispatch target selection is a GT-KB-owned service behavior and must preserve role/status routing and auditability.
- `ADR-DISPATCHER-ARCHITECTURE-001` — the dispatcher remains a daemon-owned black-box service; harnesses remain dispatch consumers only.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` — single-harness dispatcher semantics and kind-aware dispatchability must remain unchanged by this ranking-tiebreak slice.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the owner decision, PAUTH, backlog update, bridge proposal, tests, and later implementation report are durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — implementation should preserve traceability from requirement to proposal, tests, report, and verification evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — WI-5032 moves from owner-gated backlog work to an active bridge proposal without silently resolving or superseding the item.

## Prior Deliberations

- `DELIB-DISPATCH-RANKING-NORMALIZATION-20260705` — owner AUQ decision: flatten ranking values and make the fully tied dispatch tiebreak uniform-random; sequence the tiebreak first, then flatten values; leave roles and dispatchability unchanged.
- `DELIB-20260706-WI5032-IMPLEMENTATION-APPROVAL` — owner authorized Prime Builder to attach WI-5032 to the dispatch-selection project, create bounded PAUTH evidence, and file this NEW bridge proposal; implementation remains bridge-GO gated.
- `gt bridge threads --wi WI-5032 --json --compact` returned `match_count: 0` before this filing, so this is the first bridge thread for WI-5032 rather than a revision of prior proposal work.

## Owner Decisions / Input

- `DELIB-DISPATCH-RANKING-NORMALIZATION-20260705` records the owner AUQ decision selecting uniform-random terminal tiebreak behavior and tiebreak-before-flatten sequencing.
- `DELIB-20260706-WI5032-IMPLEMENTATION-APPROVAL` records the owner instruction `WI-5032: Authorize proposal` for this specific backlog item.
- `PAUTH-PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION-WI5032-TIEBREAK-20260706` bounds the authorized work to WI-5032. It explicitly forbids WI-5033 value-flattening/ranking-value changes, production deployment, credential lifecycle work, dispatcher daemon restart/topology activation, broad dirty-worktree cleanup, destructive cleanup, history rewrite, unrelated sweep commits, and protected artifact mutation without the applicable approval packet.

## Requirement Sufficiency

Existing requirements sufficient. The owner decision and WI-5032 acceptance summary are clear enough to implement and verify this slice: fully tied eligible candidates must be selected uniformly at random; `harness_id` must no longer be the deterministic terminal tiebreak in the live selector; shadow/live ranker consistency must be addressed or explicitly scoped; tests must use seeded/injected randomness rather than depending on a fixed harness id. No new or revised requirement is needed before implementation, provided the implementation stays inside WI-5032 and leaves WI-5033 ranking-value flattening untouched.

## Spec-Derived Verification Plan

The implementation report must run and report the exact commands below, adjusting only to the repo-native interpreter if the venv path is unavailable:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_priority.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_dispatch_policy.py -q --no-header
```

Expected coverage:

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, and `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`: tests prove non-tied candidates still rank by configured quality/cost/availability/reviewer-precedence dimensions; hard eligibility, role, status, and dispatchability filters are unchanged; a fully tied candidate pool is selected by an injectable/seeded random choice rather than by `harness_id`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: after a future `GO`, the implementation-start helper must accept only the target paths in this proposal and the active PAUTH; no implementation begins before that packet exists.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: bridge preflights must pass before filing and before `GO`/verification; the implementation report must carry forward specification links and the executed spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: MemBase/project/bridge evidence must show WI-5032 linked to this bridge thread without resolving, retiring, or superseding WI-5032 until verification evidence exists.

## Risk / Rollback

Main risk: introducing randomness can make dispatch behavior harder to reproduce and tests flaky if the random source is global or uncontrolled. Mitigation: isolate the random chooser behind an injectable RNG/choice function, log or expose the tied candidate pool in decision evidence, and use deterministic seeds or monkeypatches in tests. Secondary risk: touching both live and TAFE/shadow policy paths could accidentally diverge them; the implementation must either update both consistently or explicitly demonstrate one path is out of scope.

Rollback is a single focused revert of the WI-5032 implementation commit plus the post-implementation bridge report/verdict chain if verification has already proceeded. The rollback returns the selector to deterministic `harness_id` terminal ordering but does not alter WI-5033's separate ranking-value backlog state.

## Pre-Filing Checks

- Applicability preflight on the completed draft: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; target paths resolved to the nine inline `target_paths` entries above.
- Clause preflight on the completed draft: exit 0; `Blocking gaps (gate-failing): 0`.
- Phantom-spec sweep: 13 cited `SPEC` / `GOV` / `ADR` / `DCL` / `PB` IDs checked; missing IDs: none.
- Draft placeholder sweep: no scaffold placeholders remain.

## Bridge Filing

This proposal is filed in the bridge directory as the next status-bearing numbered
bridge file for `gtkb-wi5032-uniform-random-dispatch-tiebreak`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix(dispatch): the change repairs biased deterministic dispatch selection for fully tied candidates without introducing a new public capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
