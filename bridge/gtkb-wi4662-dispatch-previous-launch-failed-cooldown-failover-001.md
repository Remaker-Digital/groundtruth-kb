NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 600b3b4c-edc3-4090-9217-267db92defe8
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

# Dispatch repair: cooldown-gate the previous_launch_failed re-log and exhaust LO failover instead of re-logging indefinitely (WI-4662)

bridge_kind: implementation_proposal
Document: gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover
Version: 001 (NEW)
Recommended commit type: fix:

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4662

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Problem / Diagnosis

When a Loyal Opposition (LO) headless worker launch fails, the cross-harness dispatch trigger re-emits the same `previous_launch_failed` marker on *every* subsequent reconcile cycle, with no cooldown-clear and no terminal-state handling once the ranked LO candidate list is exhausted. Live evidence (`.gtkb-state/bridge-poller/dispatch-failures.jsonl`, current checkout): 5716 rows, of which **1505 are `previous_launch_failed`** — 731 for `loyal-opposition:D`, 538 for `loyal-opposition:F`, 166 for `loyal-opposition:C`, 44 for `loyal-opposition:A` — versus only a few dozen genuine root launch failures. This matches the WI-4662 backlog evidence (795 re-logs for D from 9 genuine failures on 2026-06-18).

Root-cause, file:line (current `scripts/cross_harness_bridge_trigger.py`):

1. **Unconditional re-record in the dispatch path.** In `run_trigger`, when the selected batch signature is unchanged from the prior failed launch, the trigger calls `_detect_previous_launch_failure` and then `_record_dispatch_failure(state_dir, previous_launch_failure)` on every cycle (`scripts/cross_harness_bridge_trigger.py:3783-3791`). This record is written *before* the circuit-breaker gate at `:3805`, so it fires regardless of breaker/back-off state. `last_launch` is carried forward verbatim (`:3705-3706`) and `exit_code_processed` is never re-cleared, so the same marker is re-detected indefinitely.

2. **Unconditional re-record in the back-off path.** `_provider_failure_backoff_skip` likewise calls `_record_dispatch_failure(state_dir, previous_failure)` each cycle for a non-retryable class (`:3340-3341`) and for the same-failed-batch case (`:3352-3353`). For a fatal marker that is *not* non-retryable (e.g. `max_turn_exhaustion`), `same_failed_batch` is true, so a row is written every cycle even when no genuine new failure occurred.

3. **`_detect_previous_launch_failure` has no cooldown / no clear.** It re-inspects `prior["last_launch"]` and re-derives the same evidence every call (`:697-771`) with no timestamp gate and no mechanism to clear/quiesce `last_launch` after the failure has been recorded once.

4. **No terminal handling when failover is exhausted.** Ordered failover to the next-ranked LO already exists (VERIFIED WI-4484 `gtkb-lo-dispatch-ordered-fallback-routing`, see Prior Deliberations): `select_dispatch_candidates` ranks active LO candidates and `run_trigger` iterates them, skipping a failed higher-ranked target via `_provider_failure_backoff_skip` (`:3572-3607`). But the skip-and-fall-through is only evaluated for non-last candidates (`if target_index < len(targets) - 1:`, `:3583`). When the *only active* LO candidate fails (the live steady-state today: `bridge dispatch status` shows A active; C/D/F inactive, so `select_dispatch_candidates` filters them out and the ranked list has length 1), there is no next rank to fail over to, and the single failing primary re-logs the marker forever. The historical D/F/C spam happened the same way when each was, in turn, the only/top active candidate.

Net effect described by WI-4662: a single failing primary LO indefinitely spams the LO dispatch lane and (when it is also the sole active candidate) blocks LO verdicts from completing, so NEW/REVISED threads stay stuck awaiting LO review.

## Proposed Change

All edits are additive and confined to `scripts/cross_harness_bridge_trigger.py` plus one new focused test file. The change introduces a per-recipient **cooldown stamp** that gates the `previous_launch_failed` re-record, and makes failover-exhaustion a recorded terminal state rather than an unbounded re-log loop.

1. **Add a cooldown horizon constant and reuse the existing retry-delay knob.** Near the existing `DEFAULT_DISPATCH_RETRY_DELAY_SECONDS = 300` (`:187`), add `PREVIOUS_LAUNCH_FAILED_RELOG_COOLDOWN_SECONDS` defaulting to the same `_dispatch_retry_delay_seconds()` value (env-tunable via the existing `GTKB_DISPATCH_RETRY_DELAY_SECONDS`). No new env var is required.

2. **Cooldown-gate the re-record at the single shared chokepoint.** Add a small helper `_should_relog_previous_launch_failure(recipient_state, *, now) -> bool` that reads a new `previous_launch_failed_logged_at` field on the recipient state and returns `False` while within the cooldown window. Wrap *both* re-record sites — the dispatch-path call at `:3790` and the two `_provider_failure_backoff_skip` calls at `:3341` / `:3353` — so `_record_dispatch_failure(...)` for a `previous_launch_failed` row is emitted at most once per cooldown window per recipient, stamping `previous_launch_failed_logged_at = _now_iso()` on emit. The in-memory `recipient_state["previous_launch_failed"]` annotation (used by `bridge dispatch status`/diagnose) is still set every cycle so health visibility is unchanged; only the *append to the JSONL failure log* is throttled. This is the minimal, behavior-preserving fix for the log-spam half of WI-4662.

3. **Clear the cooldown stamp on recovery.** In `_process_pending_exit_codes`, in the success branch that already resets the breaker (`:3216-3221`, where `failure_count`/`circuit_breaker_tripped` are cleared), also `recipient_state.pop("previous_launch_failed_logged_at", None)` and `recipient_state.pop("previous_launch_failed", None)` so a recovered target re-logs immediately if it fails again later (no stale suppression).

4. **Record a terminal `lo_failover_exhausted` state when the ranked list is exhausted.** In the LO branch of the candidate loop in `run_trigger` (`:3570-3607`), when every ranked candidate was skipped for a launch-failure/back-off reason (the `selected_target is None` path, currently recorded as `no_ready_target_for_role` at `:3603`) AND the role is `loyal-opposition` AND at least one candidate was skipped specifically due to a `previous_launch_failed`/`provider_failure_backoff_active` reason, set the per-recipient `last_result = "lo_failover_exhausted"` and emit a single cooldown-gated failure row with `reason = "lo_failover_exhausted"` plus the `fallback_skipped_candidates` list. This converts the "sole failing LO" case from an infinite re-log into one bounded, diagnosable record per cooldown window, and is the explicit failover-half of WI-4662. (When >=2 LO candidates are active, the existing WI-4484 skip-and-fall-through already routes to the next rank; this change only adds the bounded terminal record for the exhausted case.)

Composition with WI-4703 (`bridge/gtkb-wi4703-dispatch-non-transient-fast-trip`, same file): **complementary, non-conflicting.** WI-4703 (currently at report `-011`, GO'd proposal `-003`/`-004`) edits three regions: two added entries in `FATAL_WORKER_OUTPUT_MARKERS` (~`:202`), the new `FAST_TRIP_FAILURE_CLASSES` frozenset (~`:214-226`), and one changed statement in `_process_pending_exit_codes` that computes `effective_trip_threshold` (~`:3234-3238`). WI-4703 makes the *breaker trip faster* on a non-transient failure; WI-4662 makes the *post-failure re-logging bounded* and the *failover-exhausted state terminal*. They touch different statements. The only adjacency is inside `_process_pending_exit_codes`: WI-4703 modifies the trip-threshold line in the failure branch (`:3237-3240`); WI-4662 adds a `pop(...)` in the *success* branch (`:3216-3221`) and reads/writes `previous_launch_failed_logged_at` — different statements, no overlap. WI-4703's fast-trip actually *helps* WI-4662: once the breaker trips at failure_count 1, the dispatch path short-circuits at the breaker gate (`:3805`), so the cooldown-gated re-record from step 2 is the only `previous_launch_failed` row that can be written while broken. Recommended sequencing: WI-4703 should land first (it is already in post-implementation verification); WI-4662 then rebases cleanly on top. If WI-4703 is still unmerged at WI-4662 implementation time, the implementer must take the current `_process_pending_exit_codes` body as the base and add only the success-branch `pop`s, leaving WI-4703's `effective_trip_threshold` line untouched.

## Specification Links

- `GOV-AUTOMATION-VALUE-VS-COST-001` - the governing value/cost principle: gate the expensive, noisy unconditional re-record + the wedged sole-LO lane behind a cheap deterministic cooldown/terminal-state check.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs this bridge filing and the numbered-file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item metadata present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping in the verification plan below.
- `GOV-STANDING-BACKLOG-001` - WI-4662 is the governed backlog candidate for this work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files are under `E:\GT-KB`.

## Owner Decisions / Input

- This is project-authorized bridge-protocol reliability work under PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY; the project-authorization (PAUTH) citation above is finalized by the interactive Prime Builder session per the owner's AskUserQuestion authorization of the unauthorized bridge-tooling defect batch (WI-4565 / WI-4662 / WI-4701).
- No additional owner decision is required to proceed once this proposal receives Loyal Opposition GO: the fix is source-only, additive, behind the existing half-open recovery, and changes no dispatch-state schema field semantics (it only adds `previous_launch_failed_logged_at` and the `lo_failover_exhausted` last_result token).

## Prior Deliberations

- `DELIB-20265287` - owner-decision anchor for `GOV-AUTOMATION-VALUE-VS-COST-001`; the principle this fix operationalizes in dispatcher code.
- `DELIB-20263487` - "Cost-Optimized Autodispatch Priority Handoff" (returned by `gt deliberations search "dispatch failover LO target ranking previous_launch_failed cooldown"`); the autodispatch prioritization context behind LO candidate ranking.
- `DELIB-20261075` - "SP-1 Investigation: Dispatch Reliability Foundation" (same search); dispatch-reliability foundation for this project.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-001.md` .. `-008.md` (VERIFIED, WI-4484) - the ordered LO failover this proposal extends; WI-4662 adds the cooldown + exhausted-terminal record on top of that mechanism rather than reimplementing failover.
- `bridge/gtkb-wi4703-dispatch-non-transient-fast-trip-003.md` (GO'd proposal) / `-004.md` (GO verdict) / `-011.md` (current report) - the same-file fast-trip breaker thread this change composes with (see Proposed Change).
- `bridge/gtkb-wi4396-dispatch-suppression-routing-001.md` .. `-006.md` (VERIFIED, WI-4396) - prior art that routes expected lease/contention suppressions out of the actionable failure log via the shared `_record_dispatch_failure` chokepoint; WI-4662 reuses that same chokepoint to throttle the `previous_launch_failed` reason.

## Requirement Sufficiency

Existing requirements are sufficient: `GOV-AUTOMATION-VALUE-VS-COST-001` is the governing requirement and WI-4662 derives a concrete, bounded dispatcher behavior from it; no new specification is required before implementation.

## Specification-Derived Verification Plan

New focused unit tests in `platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py` (spec-to-test mapping):

| Specification / behavior | Test | Expected |
| --- | --- | --- |
| `GOV-AUTOMATION-VALUE-VS-COST-001` - re-record is cooldown-gated | drive two consecutive cycles with the same failed LO `last_launch` (fatal marker) inside the cooldown window | exactly one `previous_launch_failed` row appended across both cycles; `previous_launch_failed_logged_at` set after the first |
| Re-record resumes after the cooldown elapses | advance the stamp past `GTKB_DISPATCH_RETRY_DELAY_SECONDS` and run again | a second `previous_launch_failed` row is appended |
| In-memory health annotation unthrottled | both cycles above | `recipient_state["previous_launch_failed"]` present on every cycle (status/diagnose visibility unchanged) |
| Recovery clears the cooldown stamp | success exit-code processing after a fatal failure | `previous_launch_failed_logged_at` and `previous_launch_failed` cleared from recipient state |
| Sole active LO failover exhausted -> terminal record | single active LO candidate whose batch previously failed (fatal marker), run cycle | `last_result == "lo_failover_exhausted"`; exactly one `lo_failover_exhausted` failure row per cooldown window |
| Multi-active LO failover unchanged (WI-4484 regression) | two active LO candidates, top one failed | next-ranked candidate is selected/dispatched; no `lo_failover_exhausted` emitted |

Commands (run from `E:\GT-KB`):
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py -q --tb=short`
- Regression: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short`
- WI-4703 co-residence regression (if landed): `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatch_non_transient_fast_trip.py -q --tb=short`
- Lint/format: `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py`

Note: the cross-harness trigger regression must be run with `GTKB_NO_CROSS_HARNESS_TRIGGER` cleared in the child process (the parent hook env sets it to `1`, which makes trigger invocations return `loop_prevention_env_var`).

## Risk And Rollback

- Risk: cooldown throttling could hide a *genuinely new* failure that happens to share the same selected-batch signature within the window. Mitigation: the throttle applies only to the `previous_launch_failed` reason (re-detection of an already-recorded failure); a *new* distinct failure produced by `_process_pending_exit_codes` (different `dispatch_id`/exit code) is written through the normal, un-throttled path, and the in-memory health annotation remains every-cycle. Cooldown defaults to the existing 300s retry delay, so suppression never exceeds one half-open probe window.
- Risk: the new `lo_failover_exhausted` terminal record changes a `last_result` value that a downstream reader might branch on. Mitigation: it is added to the existing free-form `last_result` field (already carries many reason strings); `bridge dispatch status`/diagnose treat unknown last_result values generically.
- Risk: collision with WI-4703 in `_process_pending_exit_codes`. Mitigation: WI-4662 edits the success branch and adds new fields only; WI-4703 edits the failure-branch trip-threshold line. Sequencing guidance is in Proposed Change.
- Rollback: revert the single source commit; the new test file is additive. No dispatch-state schema migration — `previous_launch_failed_logged_at` is an optional additive field that absent-readers ignore, and stale values are cleared on the next success.

## Acceptance Criteria

- [ ] A `previous_launch_failed` row is appended at most once per cooldown window per recipient (verified by the two-cycle test); re-record resumes after the window elapses.
- [ ] The in-memory `previous_launch_failed` health annotation is still set every cycle (status/diagnose visibility unchanged).
- [ ] A successful dispatch clears `previous_launch_failed_logged_at` and `previous_launch_failed` from recipient state.
- [ ] When the ranked active LO list is exhausted by launch failures, the recipient records a single bounded `lo_failover_exhausted` terminal result per cooldown window instead of re-logging indefinitely.
- [ ] Existing WI-4484 ordered-fallback / multi-active behavior is unchanged (regression `test_cross_harness_bridge_trigger.py` passes, including the `ordered_fallback` and `prime_builder_multi_active` tests).
- [ ] WI-4703 fast-trip behavior is unaffected (its focused tests pass if that thread has landed); no edit to its `FATAL_WORKER_OUTPUT_MARKERS` / `FAST_TRIP_FAILURE_CLASSES` / `effective_trip_threshold` lines.
- [ ] New unit tests pass; ruff check + format clean on changed files.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
