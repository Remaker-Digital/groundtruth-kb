# Implementation Proposal — Post-Stop Dispatch Retry Pass (Slice 3 of 4)

bridge_kind: prime_implementation_proposal

## Summary

Add a post-Stop dispatch retry pass to `scripts/cross_harness_bridge_trigger.py`
so that signatures suppressed during a counterpart-active session are
re-evaluated immediately when the counterpart Stop hook fires. Currently the
suppression marker (`last_suppressed_signature`) is set when dispatch is
suppressed by `check_counterpart_active`, but the next dispatch attempt
happens only on the next PostToolUse / Stop event of an unrelated tool call.
Owner sessions that end without a subsequent tool call leave the suppressed
work waiting indefinitely until the next session.

This slice does NOT introduce per-bridge-thread locks (more invasive
architectural change). It uses the coarse `active-{handle}-session.lock`
mechanism unchanged, and adds a retry pass that fires the moment the lock
ages out.

## Dependency on Slice 1

Implementation execution is gated on `gtkb-prime-worker-permission-profile-slice-1`
reaching `GO`. Slice 1 lands the permission flags that let spawned Prime
workers actually complete the suppressed work; without those flags, a
post-Stop retry that successfully dispatches a Prime worker still wouldn't
deliver value because the worker would hit permission gates.

Codex may review Slice 3 in parallel.

## Background

`scripts/cross_harness_bridge_trigger.py:1042-1053` records suppression like this:

```python
elif check_counterpart_active(target, state_dir):
    recipient_state["last_suppressed_signature"] = signature
    recipient_state["last_result"] = "counterpart_active_session_present"
    results[recipient] = {
        "launched": False,
        "reason": "counterpart_active_session_present",
    }
```

The retry condition (line 1054-1080 dispatch branch) only fires on the next
trigger invocation. Trigger invocation requires a tool call or a Stop event
in some active session. If the owner session ends without subsequent tool
calls in any other harness, the suppressed work waits until:

- Another harness has a tool-use event in some other workflow.
- The owner starts a new session and Claude's SessionStart hook eventually
  fires the trigger.
- The owner manually invokes a bridge scan.

Symptom: bridge work that should have been dispatched at owner-session-end
sits stale until the next session pickup, sometimes hours later.

## Scope (Slice 3 of 4)

In scope:

1. Detect Stop events in the trigger script: add a `--stop-event` arg or
   reuse the existing `--stop-hook` flag (which already exists per
   `cross_harness_bridge_trigger.py:1271-1281`). Decision: extend `--stop-hook`
   semantics, no new flag.
2. In Stop-event mode, after the normal trigger pass, immediately evaluate
   whether any recipient's `last_suppressed_signature` is still relevant
   (i.e., the lock is no longer fresh per `check_counterpart_active`). If
   yes, run a second dispatch pass for that recipient.
3. The retry pass uses the same signature/dispatch logic — it does not
   bypass `check_counterpart_active`; it relies on lock TTL having aged
   out between the normal pass and the retry pass.
4. Tests covering the retry semantics.

Out of scope for Slice 3:

- Per-bridge-thread locks (architectural change; tracked as separate
  follow-on if Slice 3's coarse-lock retry proves insufficient).
- Slice 4 regression coverage of the full worker delivery pipeline.

## In-Root Placement Evidence

All target paths and runtime artifacts in-root under `E:\GT-KB`:

- `E:\GT-KB\scripts\cross_harness_bridge_trigger.py` — `main` retry-pass logic.
- `E:\GT-KB\platform_tests\scripts\test_cross_harness_bridge_trigger.py` — retry-pass regression tests.
- `E:\GT-KB\.gtkb-state\bridge-poller\dispatch-state.json` — read for `last_suppressed_signature`; written on retry result.
- `E:\GT-KB\.gtkb-state\bridge-poller\dispatch-failures.jsonl` — retry failures appended in-root.

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, all target paths and runtime artifacts are within the GT-KB platform root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — file bridge authority; this slice preserves canonical workflow state behavior and adds only a retry pass.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived from linked specs.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — dispatched prompts retain canonical init-keyword first line; retry pass does not alter prompt content.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — emitter authority preserved across normal and retry dispatches.
- `.claude/rules/bridge-essential.md` § Active-Session Suppression — current suppression contract; retry pass does not change WHO is suppressed, only WHEN the suppression aging is re-evaluated.
- `.claude/rules/bridge-essential.md` § Bridge Dispatch Enablement Contract — opt-out, not opt-in; retry pass inherits this.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol invariants.
- `.claude/rules/codex-review-gate.md` — review gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application/root placement boundary; this proposal does not touch `applications/` paths or modify root-boundary behavior. Cited per path-match acknowledgement (the proposal references `.claude/rules/file-bridge-protocol.md`); no modification proposed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance discipline (advisory). The change preserves the `dispatch-failures.jsonl` audit artifact and the `dispatch-state.json` recipient state artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development (advisory). Traceability preserved across dispatch state, failures log, and bridge thread audit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle states (advisory). The proposal lifecycle is NEW → (GO/NO-GO) → VERIFIED per the file-bridge-protocol contract.

## Prior Deliberations

- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` VERIFIED — established the suppression state machine (`last_dispatched_signature` vs `last_suppressed_signature` distinction); this slice extends, does not modify, the state machine.
- `bridge/gtkb-bridge-poller-event-driven-replacement-003.md` GO at `-004` — established the event-driven trigger; Stop-event hook registration is already in place per `.claude/settings.json` and `.codex/hooks.json`.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*` — Slice 4 retired interval-driven dispatch; this proposal is a refinement of event-driven dispatch, not a re-introduction of intervals.
- `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09` — owner directive establishing the 120-second TTL.
- Sibling Slice 1 + Slice 2 threads (filed; NEW status).

## Owner Decisions / Input

Owner AskUserQuestion answer in S350 (2026-05-14): "Which slicing strategy for the Prime-worker-delivery fix?" → **4-slice sequence (recommended)**. Slice 3 = lock granularity (per-thread or post-Stop retry pass).

Owner directive in S350 (2026-05-14): "Please draft Slices 2-4 in parallel."

This proposal interprets the lock-granularity slot of the 4-slice plan as the lighter option (post-Stop retry pass), citing risk minimization vs full per-thread lock surgery. If Codex review judges per-thread locks are required for correctness rather than the retry-pass approximation, NO-GO with rationale and Prime files a REVISED scoping per-thread locks instead.

## Requirement Sufficiency

Existing requirements sufficient. The suppression contract at `.claude/rules/bridge-essential.md` § Active-Session Suppression is unchanged. The trigger's behavior contract is preserved; this slice adds a retry pass within the existing contract.

## target_paths

- `scripts/cross_harness_bridge_trigger.py` (post-Stop retry pass logic in `main`)
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` (retry pass behavior tests)

## Implementation Plan

1. **Extract retry logic** in `scripts/cross_harness_bridge_trigger.py`. After `run_trigger` returns its normal-pass `summary`, in Stop-event mode (`args.stop_hook == True`):
   - For each recipient in `summary["dispatch_state"]["recipients"]`:
     - If `recipient_state["last_result"] == "counterpart_active_session_present"` AND `recipient_state["last_suppressed_signature"]` is set:
       - Sleep briefly (configurable; default 1000 ms) to let the counterpart's lock-clearing operations finalize.
       - Re-run `check_counterpart_active(target, state_dir)`. If False (lock now stale or removed), re-run `run_trigger` once with the same project_root + state_dir + max_items. Capture the retry summary.
   - The retry pass is best-effort: failures are recorded in `dispatch-failures.jsonl` per the fire-and-forget contract; main return is unchanged.
2. **Sleep duration** is parameterized via `--retry-delay-ms` (default 1000) for test affordance.
3. **Unit tests**:
   - `test_stop_event_retry_dispatches_when_lock_cleared`: stage `last_suppressed_signature` in dispatch-state, no fresh lock; Stop-event mode invocation triggers a retry dispatch.
   - `test_stop_event_retry_skips_when_lock_still_fresh`: stage `last_suppressed_signature` AND a fresh lock; Stop-event mode invocation does NOT retry.
   - `test_normal_pass_unaffected_by_retry_logic`: non-Stop-event invocation behaves identically to current implementation (regression check).
   - `test_retry_pass_failures_recorded_to_dispatch_failures_jsonl`: stage retry failure; assert JSONL append.

## Spec-to-Test Mapping

- `GOV-FILE-BRIDGE-AUTHORITY-001` → `test_normal_pass_unaffected_by_retry_logic` (file-bridge authority preserved when retry inactive).
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` + `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` → `test_stop_event_retry_dispatches_when_lock_cleared` asserts the retry dispatch prompt still emits the canonical init-keyword first line.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → spec-to-test mapping is one test per assertion class.

## Risks

- **Retry causes duplicate dispatch under race**: if the counterpart's lock clears, then the counterpart immediately spawns a new session (lock re-set), the retry could dispatch into the new active window. *Mitigation:* the retry pass uses `check_counterpart_active` against the live lock state, not the dispatch-state snapshot. Race window is narrow but non-zero; documented and accepted (worst case: one duplicate dispatch suppressed on the next trigger by the dedup signature check).
- **Sleep duration too short/long**: 1000 ms is a heuristic. Too short → lock not yet cleared; too long → owner perceives lag. *Mitigation:* tunable via flag; default chosen as a reasonable midpoint. Slice 4 regression coverage observes empirically.
- **Stop-event mode signature already includes Codex Stop contract `{}` emission**: the existing Stop-hook output is exactly `{}` per the OpenAI Codex contract (`cross_harness_bridge_trigger.py:1325-1330`). The retry pass must run BEFORE the `{}` emission OR async / fire-and-forget. *Mitigation:* the retry runs synchronously before `print("{}")` because the retry latency is bounded (~1 second); Codex's Stop hook contract is just "exactly one parseable JSON object on stdout," not a latency budget.

## Rollback

Remove the post-Stop retry block from `main`. Trigger reverts to current behavior; suppressed dispatches wait for the next tool-use or session-start event.

## Verification Procedure

1. Run `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short`.
2. Manual smoke: stage `last_suppressed_signature` via a fixture, run `python scripts/cross_harness_bridge_trigger.py --stop-hook --state-dir <fixture-dir>`; observe dispatch attempt in stdout/log.
3. Liveness smoke: `python scripts/cross_harness_bridge_trigger.py --diagnose`; per-recipient state shows post-retry signatures.

## Acceptance Criteria

- Stop-event mode triggers a retry pass when `last_suppressed_signature` is set and the lock is stale.
- Normal pass behavior unchanged.
- Retry pass respects fire-and-forget contract.
- All preflights pass for this proposal.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
