GO

# Proposal Review Verdict - WI-5041 dispatcher per-thread re-offer backoff (GO)

bridge_kind: lo_verdict
Document: gtkb-wi5041-dispatcher-thread-reoffer-backoff
Version: 002
Author: Loyal Opposition (Claude Code, harness B)
Date: 2026-07-09 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5041-dispatcher-thread-reoffer-backoff-001.md

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 85e78bc0-61f1-4383-84cd-fb4128f29b95
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

## Verdict: GO

Loyal Opposition grants GO for WI-5041 (dispatcher per-thread, slug-keyed re-offer backoff). Every architectural claim the proposal makes about `scripts/dispatcher_runtime.py` was independently verified against the live code, including the one load-bearing claim (additive top-level state, no schema migration) that could have inverted the verdict. Spec linkage is complete, both preflights pass, all target paths are in-root, and the owner authorized the treadmill-drain program. The proposal correctly identifies a real gap that neither existing suppression axis covers. No blocking findings; the conditions below are implementation-phase guidance.

## Applicability Preflight

- packet_hash: `sha256:5c9256dfbc4662e8a5537361197a119f835b63595e34b381c0f271807e4b1f8e`
- bridge_document_name: `gtkb-wi5041-dispatcher-thread-reoffer-backoff`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5041-dispatcher-thread-reoffer-backoff-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0; Blocking gaps (gate-failing): 0
- Clause preflight exit code: 0 (no blocking gap)
- CLAUSE-IN-ROOT (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`): satisfied - all three target paths are in-root.

## Prior Deliberations

- `DELIB-20266278` - owner authorization of the dispatch-treadmill-drain program (cited by the proposal; confirmed as the governing authorization for WI-5041 as a later slice).
- `DELIB-20266272` - PHASE-Y dispatcher-daemon go-live whose dispatch asymmetry creates the treadmill this backoff suppresses.
- `.claude/rules/auto-finalization-sweep.md` (WI-4889) - Slice 1 of the same program (drains the symptom); WI-5041 attacks the re-offer cause. Distinct scope, no overlap.
- Deliberation search this session (`work subject config platform classification ...` and dispatch-treadmill context) surfaced no prior design of a per-thread re-offer backoff; consistent with the proposal's novel-gate framing.

## Premise Verification (independent, against live `scripts/dispatcher_runtime.py`)

| Proposal claim | Verification | Result |
| --- | --- | --- |
| `run_dispatch_cycle` computes a per-recipient `_signature` over actionable items | `_signature` at L501; `run_dispatch_cycle` at L5538 | CONFIRMED |
| Suppression is only "unchanged-signature" (per-recipient) + provider failure-count backoff | `_provider_failure_backoff_skip` at L5437 keyed on `failure_count` (L5486); `circuit_breaker_active`/`retry_delay_enforced` at L1276-79 | CONFIRMED |
| `failure_count` increments only after a launch, so a looping-but-successful thread never trips provider backoff | in-code comment L6113-14 states exactly this; increment at L5299-5300 | CONFIRMED - this is the real gap |
| `subject_suppression` / `circuit_breaker` gates exist to place the new gate parallel to | `subject_suppression` at L6035; circuit-breaker/retry branches at L6075/L6120 | CONFIRMED |
| `_reset_recipient_state` (WI-4805 clean-slate) exists to drop the new counter in | L946; resets `failure_count` (L970), clears signatures (L980-81) | CONFIRMED |
| `_load_dispatch_state`/`_write_dispatch_state` preserve unknown top-level keys (additive, no migration) | `_load_dispatch_state` returns `raw` wholesale (L530), migrating only the `recipients` submap; `_write_dispatch_state` writes full `payload` via `json.dumps(payload, ...)` (L746) with no key allowlist | CONFIRMED - the additive `thread_reoffers` top-level key round-trips cleanly |
| `thread_reoffers` / `_thread_reoffer_backoff_skip` not already implemented | grep of `dispatcher_runtime.py` finds neither symbol | CONFIRMED - net-new work, no sibling collision |

## Review Analysis

- **Correct gap identification.** The two existing suppression axes are (a) per-recipient signature ("unchanged") and (b) provider failure-count backoff. On an owner-gated NO-GO <-> REVISED treadmill the signature legitimately changes every cycle (new `top_file`/`top_status`) and no launch fails (so `failure_count` stays 0). Neither axis engages. A third, slug-keyed, cycle-count axis is genuinely required. The proposal's diagnosis is accurate and evidence-backed (WI-4978 13-version treadmill).
- **Correct keying.** Keying by document slug (spanning LO -> Prime -> LO) rather than by recipient is the right choice for a role-alternating treadmill; a recipient-keyed counter could not see the cross-role loop.
- **Orthogonality preserved.** The proposal explicitly forbids reusing `failure_count`/provider backoff and requires a distinct audit token (`thread_reoffer_backoff_active`), so `diagnose`/status surfaces can tell cycle-count suppression from provider suppression. This is the right separation and prevents cross-contamination of the two axes.
- **Re-arm semantics.** Re-arm on terminal/non-actionable status (VERIFIED/WITHDRAWN/DEFERRED) and on `_reset_recipient_state` (operator clean-slate). Both are appropriate; the operator override matters so a clean-slate genuinely re-arms.
- **Scope of suppression is correct.** The backoff suppresses only headless *dispatch* (worker spawn), NOT the thread's actionability. An interactive LO/Prime session still sees and can process a throttled thread manually. This is the right blast radius: it stops the token storm without hiding legitimate work.

## Conditions / Required Actions (implementation-phase; non-blocking)

1. **Test the cooldown-window re-offer resumption.** Add a test asserting that after `THREAD_REOFFER_BACKOFF_WINDOW_SECONDS` elapses (or the recent-offer count ages out of the window), a still-non-terminal thread is re-offered again. This guards the starvation edge: a legitimately-resolved-but-non-terminal REVISED (owner un-gates the blocker) must not be suppressed indefinitely by headless dispatch. State the maximum starvation delay (bounded by the cooldown window) in the implementation report.
2. **Assert the additive round-trip in a test.** Although LO verified `_load_dispatch_state`/`_write_dispatch_state` preserve the new top-level key, add an explicit test that `thread_reoffers` survives a load -> mutate -> write -> reload cycle, so a future strict-schema change to the state loader cannot silently break persistence.
3. **Surface the suppression in operator visibility.** Confirm the distinct `thread_reoffer_backoff_active` token appears in `gt bridge dispatch status`/`diagnose` so an operator can see a thread is being throttled (not silently dropped).
4. **Keep the durable-keyed regression green** (`test_dispatcher_runtime_durable_keyed_regression.py`) and run BOTH ruff gates (`ruff check` AND `ruff format --check`) on all three changed files before filing the implementation report.

## Owner Action Required

None. GO is unconditional; the conditions above are implementation guidance for the report, not owner decisions.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
