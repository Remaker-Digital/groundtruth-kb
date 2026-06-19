NEW

# gtkb-lo-dispatch-pipeline-repair — Repair degraded Loyal Opposition auto-dispatch pipeline (F sticky-signature backoff + C gemini-tier fallthrough)

bridge_kind: prime_proposal
Document: gtkb-lo-dispatch-pipeline-repair
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-19 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 1a3b0a86-91ee-4d2e-8ef8-b13df7a9e370
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI (explanatory output style); Prime Builder role (harness B)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4679

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The Loyal Opposition (LO) auto-dispatch pipeline is degraded by two independent defects in the cross-harness event-driven trigger, which together leave NEW/REVISED bridge reports unreviewed and impl-start locks unable to auto-clear (the production-readiness root cause: "reports don't get reviewed").

**Defect 1 — F (OpenRouter) sticky backoff.** In `scripts/cross_harness_bridge_trigger.py`, the dispatch exit-code handler's *failure* branch increments `failure_count` and trips the circuit breaker but never clears `last_dispatched_signature` (only the *success* branch updates it). Because `_provider_failure_backoff_skip` short-circuits when `_prior_dispatched_signature(prior) != signature` is false, the same pending signature stays equal to the last-dispatched one and the recipient is permanently deduped as "already dispatched" → `provider_failure_backoff_active` forever, never retried.

**Defect 2 — C (Antigravity/gemini) tier regression.** The gemini CLI raises `IneligibleTierError` (deprecated "individuals" tier), so `loyal-opposition:C` exits 1 on every auto-dispatch and trips its circuit breaker, with no fall-through to the next eligible LO candidate — one dead harness stalls the whole pipeline. This is a regression of the previously-VERIFIED headless gemini LO dispatch (DELIB-2780).

**Fix.** (1) In the failure branch, clear the dedup signals (`last_dispatched_signature = None`; align legacy `signature`) so the circuit-breaker / retry-delay window governs backoff instead of a permanent signature-match skip. (2) Classify `IneligibleTierError` / fatal tier-deprecation as a non-retryable harness-unavailable condition that demotes the failing candidate and falls through to the next eligible LO.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the dispatch trigger is bridge infrastructure; this repair restores correct bridge-review routing.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — governs dispatch eligibility/health semantics this change corrects.
- `DCL-DISPATCH-ENVELOPE-RULES-001` — dispatch routing/eligibility rules the fallthrough must honor.
- `SPEC-TAFE-R4` — TAFE-backed dispatch state whose signature lifecycle is the Defect-1 surface.
- `REQ-HARNESS-REGISTRY-001` — harness eligibility/availability; the fix prevents an unavailable harness from blocking routing.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — cross-harness dispatch fallback discipline the C fallthrough extends.
- `GOV-RELIABILITY-FAST-LANE-001` — small reliability defect fix under the standing reliability fast-lane.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — bounded to PROJECT-GTKB-RELIABILITY-FIXES / WI-4679.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan derives tests from the specs below.
- `GOV-STANDING-BACKLOG-001` — bounded to the single work item WI-4679.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; durable-artifact governance carried forward (per sibling dispatch-repair thread).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; artifact-lifecycle triggers carried forward.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; artifact-oriented governance stance carried forward.

## Prior Deliberations

- `DELIB-2780` — gtkb-headless-gemini-lo-dispatch-verification (VERIFIED). Establishes that headless gemini LO dispatch worked; Defect 2 (`IneligibleTierError`) is a regression caused by the upstream gemini account-tier deprecation. This proposal does not re-litigate that verification; it adds graceful fallthrough so a future tier regression degrades to the next LO instead of stalling the pipeline.
- `DELIB-2460` — Post-Stop Dispatch Retry Pass. Prior reasoning on dispatch retry semantics; Defect 1 is precisely the retry path failing to re-arm after a failed dispatch because the dedup signature is never cleared.
- `DELIB-1535` — Cross-Harness Trigger Active-Session Suppression. Establishes the `last_dispatched_signature` / `last_suppressed_signature` suppression model; this fix corrects the failure-path handling of that model without changing the active-session-suppression semantics.

## Owner Decisions / Input

No owner decision is required for implementation. The standing reliability fast-lane authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers this work stream (consistent with the sibling `gtkb-dispatch-runtime-health-readiness-repair` thread's disposition). The owner separately directed prioritization of this fix via AskUserQuestion this session (LO auto-dispatch is degraded, so the owner will manually record GO/VERIFIED while the pipeline is restored), but that is task sequencing, not an implementation-approval dependency.

## Requirement Sufficiency

Existing requirements sufficient. The dispatch reliability and routing requirements above (`SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`, `SPEC-TAFE-R4`, `REQ-HARNESS-REGISTRY-001`) govern correct dispatch retry and fallthrough behavior; this is a defect fix that brings the implementation into conformance with them. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Specification | Test / verification command | Expected result |
|---|---|---|
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` / `SPEC-TAFE-R4` (Defect 1) | New regression test in `platform_tests/scripts/test_cross_harness_bridge_trigger.py` asserting that after a failed/exhausted dispatch of signature S, a subsequent run with the same pending work re-dispatches once the retry-delay window elapses (recipient state has `last_dispatched_signature` cleared; `_provider_failure_backoff_skip` no longer returns `provider_failure_backoff_active` on the unchanged-signature path). | PASS |
| `DCL-DISPATCH-ENVELOPE-RULES-001` / `REQ-HARNESS-REGISTRY-001` / `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (Defect 2) | New regression test asserting that a fatal tier / `IneligibleTier` failure for one LO candidate demotes it and the dispatcher selects/falls through to the next eligible LO rather than leaving pending work unrouted. | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `GTKB_HARNESS_NAME=claude groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q` plus `ruff check` and `ruff format --check` on the two changed files. | All pass / clean |

## Risk / Rollback

Risk is confined to dispatch eligibility/retry semantics in `cross_harness_bridge_trigger.py`. The change fails closed: clearing the dedup signature only re-enables retry after the existing circuit-breaker / retry-delay window (it does not remove backoff), and the tier-fallthrough demotes only the candidate that emitted a fatal non-retryable failure, preserving the existing "no eligible target" audit path. Both changes are localized (the failure branch of the exit-code handler and the candidate-selection/skip path); rollback is a single-commit revert restoring the prior logic. Bridge audit files remain append-only.

Note on file coordination: `cross_harness_bridge_trigger.py` is also touched by the sibling `gtkb-dispatch-runtime-health-readiness-repair` (WI-4578, VERIFIED) work currently being committed by another session; implementation will apply on top of that committed state.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-lo-dispatch-pipeline-repair`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs two reliability defects in the dispatch substrate (failure-branch signature reset + tier-error fallthrough); no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
