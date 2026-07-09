NEW

# Implementation Proposal - WI-5041 dispatcher per-thread re-offer backoff

bridge_kind: prime_proposal
Document: gtkb-wi5041-dispatcher-thread-reoffer-backoff
Version: 001
Date: 2026-07-09 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5041

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d97ced75-3b71-45cb-ae8d-88a0dd70e33c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

## Summary

Add a bounded per-thread (per-document-slug) re-offer backoff to the bridge
dispatcher so it stops re-waking counterpart harness workers on owner-gated
verification-blocker treadmills. On an owner-gated NO-GO <-> REVISED thread, each
cycle writes a new bridge version, so the per-recipient actionable signature
legitimately changes every round and the existing "unchanged"-signature
suppression never engages; the dispatcher therefore re-offers the same
non-terminal thread indefinitely, each offer launching a full (token-costly)
worker. This proposal adds a new dispatch-decision gate keyed on the document
slug's recent re-offer count/timestamp that suppresses further re-offers once a
thread has been re-offered N times within a window without reaching a terminal
status, until the thread materially changes or a cooldown elapses.

## Requirement Sufficiency

Existing requirements sufficient. Bounded dispatch-reliability defect fix under
the reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`) and the owner-
authorized dispatch-treadmill-drain program (`DELIB-20266278`, under
PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY). No new requirement capture needed; the
fix repairs a resource-waste defect in existing dispatch behavior.

## Problem / Context

In `scripts/dispatcher_runtime.py`, `run_dispatch_cycle` computes a per-recipient
actionable `_signature` over `[{document_name, top_status, top_file}]` and, in the
per-recipient dispatch branch, suppresses re-dispatch only when
`prior_dispatched == dispatched_signature` (the "unchanged" test). On an owner-
gated treadmill:

- Loyal Opposition writes a NO-GO (new `bridge/<slug>-NNN.md`), Prime writes a
  REVISED (new `bridge/<slug>-NNN+1.md`), and so on. Both `top_file` and
  `top_status` change every cycle, so `_signature` differs every cycle and the
  "unchanged" branch never fires.
- There is **no per-thread cycle counter** anywhere in the decision. Every cycle
  LAUNCHES a full worker (Prime blocker report + LO review), which is token-costly
  (distinct from cheap `launched=false` log-churn).

This is distinct from the existing PROVIDER/launch-FAILURE backoff
(`_provider_failure_backoff_skip`, `circuit_breaker_active`,
`retry_delay_enforced`), which keys on `failure_count`/a prior *failed* launch: a
looping-but-successful thread never increments those, so provider backoff cannot
suppress it. It is also distinct from the per-recipient signature state (keyed
`role:harness`), which cannot see a treadmill that spans LO -> Prime -> LO.

Diagnosis source: WI-4978 (13-version NO-GO/REVISED treadmill; LO re-offered
again ~58 min after a record-and-stop). This is the highest-leverage churn-stopper
in the treadmill-drain program.

## Proposed Scope

1. **New durable per-document state.** Add a top-level `state["thread_reoffers"]`
   map in `.gtkb-state/bridge-poller/dispatch-state.json`, keyed by the dispatched
   thread's document slug: `{count, first_offered_at, last_offered_at,
   last_status}`. `_load_dispatch_state` already preserves unknown top-level keys
   and `_write_dispatch_state` round-trips them, so no schema migration is needed
   beyond a preserve/merge step.

2. **New dispatch-decision gate.** Add `_thread_reoffer_backoff_skip(...)` invoked
   in the per-recipient dispatch branch AFTER the "unchanged"-signature test and
   BEFORE `_spawn_harness`, parallel to the existing `subject_suppression` and
   `circuit_breaker`/`retry_delay` gates. It looks up the dispatched slug's
   `thread_reoffers` record and SKIPS the dispatch (with a durable audit
   `last_result = "thread_reoffer_backoff_active"` and a distinct skipped-reason
   token, NOT the provider `provider_failure_backoff_active` token) when the slug
   has been re-offered `>= THREAD_REOFFER_BACKOFF_THRESHOLD` times (default `3`)
   within `THREAD_REOFFER_BACKOFF_WINDOW_SECONDS` (default `3600`) without reaching
   a terminal/non-actionable status (VERIFIED / WITHDRAWN / DEFERRED), and the last
   offer is within the cooldown. Keyed by document slug, NOT recipient.

3. **Counter maintenance.** On each real dispatch of a slug, set/increment `count`,
   set `last_offered_at` (and `first_offered_at` on first offer), and record the
   observed `last_status`. Clear/exempt the slug's counter when its thread reaches
   a terminal/non-actionable status, and also drop it in `_reset_recipient_state`
   (WI-4805 operator clean-slate) so an owner clean-slate genuinely re-arms.

4. **Orthogonality guard.** The new axis is cycle-count, orthogonal to the
   failure-count axis; the fix must NOT reuse `failure_count` or the provider
   backoff machinery, and its audit token must be distinguishable in
   `diagnose`/status surfaces.

5. **Tests.** Add a `test_dispatcher_runtime.py` case asserting a slug re-offered
   `THRESHOLD`+ times within the window is skipped with the
   `thread_reoffer_backoff_active` audit token, and re-armed after terminal status
   or `_reset_recipient_state`; extend `test_gtkb_dispatcher_daemon.py` re-offer
   coverage. Keep the new state additive so
   `test_dispatcher_runtime_durable_keyed_regression.py` (signature/dedup keyed
   regression) stays green.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge dispatch/audit authority; the treadmill wastes dispatch resource against the audit-trail workflow.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete spec links required.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived test evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization / project / work item / target-path metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - bounded PAUTH-backed implementation.
- `GOV-RELIABILITY-FAST-LANE-001` - reliability fast-lane for bounded defect fixes.
- `GOV-STANDING-BACKLOG-001` - WI-5041 backlog linkage.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root under E:/GT-KB.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact-oriented governance linkage.

## Prior Deliberations

- `DELIB-20266278` - owner authorization of the dispatch-treadmill-drain program under PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY ("build the sweep first"); WI-5041 is a later slice of that program.
- `DELIB-20266272` - the PHASE-Y dispatcher-daemon go-live whose dispatch asymmetry creates the treadmill this backoff suppresses.
- `.claude/rules/auto-finalization-sweep.md` (WI-4889) - Slice 1 of the same treadmill-drain program (drains the symptom); this backoff attacks the re-offer cause.
- _No prior deliberation designs a per-thread re-offer backoff; this is a novel dispatch-decision gate distinct from the existing provider-failure backoff and signature suppression._

## Owner Decisions / Input

- Owner directive (2026-07-09 program prompt): "land WI-5041 backoff + WI-5040 finalization routing early ... WI-5041 [is] the highest-leverage churn-stopper"; owner "Continue" authorization for this draft.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: standing reliability fast-lane authorization covering bounded source + test defect fixes.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run pytest over platform_tests/scripts/test_dispatcher_runtime.py + platform_tests/scripts/test_gtkb_dispatcher_daemon.py (incl. the new re-offer-backoff cases) via the project venv python -> all pass. |
| Regression safety | Run platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py -> pass (new state additive; signature/dedup unchanged). |
| Defect closure | Simulate N+1 re-offers of one owner-gated slug within the window -> dispatch suppressed with thread_reoffer_backoff_active on offer N+1; re-armed after terminal status or _reset_recipient_state. |
| Code quality | ruff check + ruff format --check on scripts/dispatcher_runtime.py + the two changed test files (both gates). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability + clause preflights pass. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths in-root under E:/GT-KB. |

## Acceptance Criteria

- The dispatcher suppresses re-offer of an owner-gated non-terminal thread once it has been re-offered `THRESHOLD`+ times within the window, recording a distinct `thread_reoffer_backoff_active` audit result.
- The suppression is keyed by document slug (spans LO <-> Prime), not by recipient, and does not reuse `failure_count`/provider backoff.
- The counter re-arms on terminal/non-actionable status and on `_reset_recipient_state`.
- Signature/dedup regression tests remain green; the new dispatch-state map is additive.
- ruff check + ruff format --check pass on all changed files.

## Bridge Protocol Compliance

Filed as the next numbered bridge file
(`bridge/gtkb-wi5041-dispatcher-thread-reoffer-backoff-001.md`); the numbered
bridge file chain is the append-only canonical audit trail and no prior version is
deleted or rewritten (`GOV-FILE-BRIDGE-AUTHORITY-001`).
