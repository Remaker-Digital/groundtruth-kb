NEW

# Post-Implementation Report: WI-4703 dispatch non-transient fast-trip

bridge_kind: implementation_report
Document: gtkb-wi4703-dispatch-non-transient-fast-trip
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4703-dispatch-non-transient-fast-trip-004.md
Approved proposal: bridge/gtkb-wi4703-dispatch-non-transient-fast-trip-003.md
Recommended commit type: fix:

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 25c46582-3e5d-41f4-be4f-e1e2462553d5
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb); takeover of stale session 6f5bd1b5 work-intent claim per owner AskUserQuestion (2026-06-20)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4703-DISPATCHER-FAST-TRIP-REPAIR
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4703

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_dispatch_non_transient_fast_trip.py"]

## Summary

Implemented the GO'd (`-004`) fast-trip circuit-breaker tier for non-transient
worker failures, exactly as approved in `-003`. The dispatcher now trips the
half-open circuit breaker after a SINGLE non-transient worker failure
(`auth_failure` / `max_turn_exhaustion` / `provider_failure` /
`provider_configuration_failure` / `guard_denied_write` / `guard_denial`)
instead of spending up to `DEFAULT_DISPATCH_MAX_RETRIES` (=3) expensive spawns
first. Retryable failures keep the normal threshold. The existing half-open
auto-recovery and success-reset paths are unchanged, so dispatch self-heals on
the next successful spawn once the underlying cause is fixed — no manual reset,
no permanent suppression.

This implementation was authored in session `25c46582` after an owner-authorized
takeover of the stale `6f5bd1b5` work-intent claim (owner AskUserQuestion
"It's done/stale — I take over WI-4703", 2026-06-20). The sibling WI-4707
credential-loader work, which `6f5bd1b5` left uncommitted in the same file, was
first committed cleanly under its own scope (commit `294fa0bd3`) to un-entangle
`scripts/cross_harness_bridge_trigger.py` before this WI-4703 change, per the
same owner directive. The WI-4707 thread (`-003` report) remains in the Loyal
Opposition verification queue and is out of scope for this report.

## Diff Summary (authorized target paths only)

- `scripts/cross_harness_bridge_trigger.py` — **+28 / -1**:
  1. Two new `FATAL_WORKER_OUTPUT_MARKERS` entries detecting the headless-Claude
     401 result text (`"Invalid authentication credentials"` and
     `"API Error: 401"`), both labelled `auth_failure`.
  2. New module-level `FAST_TRIP_FAILURE_CLASSES` frozenset
     (`auth_failure`, `max_turn_exhaustion`, `provider_failure`,
     `provider_configuration_failure`, `guard_denied_write`, `guard_denial`).
  3. In `_process_pending_exit_codes`, an `effective_trip_threshold`
     (`1` when `failure_reason in FAST_TRIP_FAILURE_CLASSES`, else `max_retries`)
     replacing the unconditional `failure_count >= max_retries` breaker-trip
     check. The success-reset (lines ~3217-3229) and `non_retryable_failure`
     path (line ~3243) are untouched.
- `platform_tests/scripts/test_dispatch_non_transient_fast_trip.py` — **+207**
  (new file): 6 unit tests driving `_process_pending_exit_codes` and
  `_matched_worker_output_markers` directly.

No other files were modified under this WI-4703 scope.

## Specification-Derived Test Mapping (GOV-AUTOMATION-VALUE-VS-COST-001)

| Specification / behavior | Test | Result |
| --- | --- | --- |
| 401 worker output classified as non-transient `auth_failure` | `test_401_output_is_classified_as_auth_failure` | PASS |
| Fast-trip: a single `auth_failure` trips the breaker at failure_count 1 | `test_auth_failure_fast_trips_breaker_at_first_failure` | PASS |
| `max_turn_exhaustion` fast-trips at failure_count 1 | `test_max_turn_exhaustion_fast_trips_breaker` | PASS |
| Retryable class unchanged: a generic `subprocess_execution_failed` does NOT trip at 1 and still trips only at the normal threshold (3) | `test_generic_failure_does_not_fast_trip_and_trips_at_normal_threshold` | PASS |
| Half-open recovery / success-reset intact: success on a fast-tripped recipient clears failure_count + breaker | `test_success_resets_failure_count_and_breaker_after_fast_trip` | PASS |
| No permanent suppression: a fast-trip uses the breaker, NOT `non_retryable_failure` | `test_fast_trip_does_not_set_non_retryable_failure` | PASS |

## Command Evidence

```
$ groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatch_non_transient_fast_trip.py -q --tb=short
6 passed, 1 warning in 6.27s

$ groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q
39 failed, 52 passed, 1 warning in 32.97s   # see "Pre-existing regression baseline" below

$ groundtruth-kb/.venv/Scripts/ruff.exe check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_non_transient_fast_trip.py
All checks passed!

$ groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_non_transient_fast_trip.py
2 files already formatted
```

## Pre-existing Regression Baseline (39 failures are NOT introduced by WI-4703)

`test_cross_harness_bridge_trigger.py` reports `39 failed, 52 passed` — but this
is a **pre-existing, orthogonal baseline, not a WI-4703 regression**. Evidence:

- The same `39 failed, 52 passed` count was observed on `HEAD` with the WI-4703
  trigger change stashed (`git stash push -- scripts/cross_harness_bridge_trigger.py`
  → run → `39 failed, 52 passed` → `git stash pop`).
- The same count was observed with the sibling WI-4707 change present and absent.
- The count is **identical (39) before and after** the WI-4703 changes — the
  WI-4703 edits introduce **zero new failures**.
- The 39 failures are in the `run_trigger(...)` integration path
  (dispatch-decision / diagnostic-classification tests, e.g.
  `test_diagnostic_classifies_dispatched` asserting an LO diagnostic record is
  produced). WI-4703 changes only the breaker-sensitivity branch of
  `_process_pending_exit_codes`; it does not touch target selection, dispatch
  decisioning, or diagnostics. The new WI-4703 tests are deliberately unit-level
  (driving `_process_pending_exit_codes` / `_matched_worker_output_markers`
  directly) to isolate the behavior under test from the failing integration
  harness.
- The pre-existing 39-failure breakage is captured as a separate backlog item
  for independent investigation; it is out of scope for this WI-4703 fast-trip
  slice.

## Confirmations (GO `-004` Required Implementation Evidence)

- **`non_retryable_failure` semantics unchanged.** The fast-trip uses the
  half-open `circuit_breaker_tripped` path only. The
  `if failure_reason in NON_RETRYABLE_WORKER_FAILURE_CLASSES:` line is untouched,
  and `NON_RETRYABLE_WORKER_FAILURE_CLASSES` still equals
  `frozenset({"harness_unavailable_tier"})`. Proven by
  `test_fast_trip_does_not_set_non_retryable_failure` (an `auth_failure` trips
  the breaker but does NOT set `non_retryable_failure`).
- **No permanent suppression introduced.** A fast-tripped breaker half-opens
  after `DEFAULT_DISPATCH_RETRY_DELAY_SECONDS` (=300s) for one probe and resets
  on the next success (`test_success_resets_failure_count_and_breaker_after_fast_trip`).
- **Headless-Claude credential repair remains out of scope.** The 401 itself is
  environmental (owner credential domain); WI-4703 only makes the dispatcher
  fail FAST and recover cleanly regardless of the underlying cause. The
  credential-loading remediation is the separate WI-4707 thread.

## Specification Links

- `GOV-AUTOMATION-VALUE-VS-COST-001` — the governing principle implemented:
  gate the expensive re-spawn behind a cheap deterministic failure-class check.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this bridge filing / numbered-file chain.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — links carried forward from `-003`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Work Item / Project Authorization metadata present above.
- `GOV-STANDING-BACKLOG-001` — WI-4703 is the governed backlog item.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both changed files are under `E:\GT-KB`.

## Owner Decisions / Input

- Owner AskUserQuestion (2026-06-20, this session): "Authorize full in-session
  repair" — authorized WI-4703 implementation and the emergency-bridge-infra
  takeover path.
- Owner AskUserQuestion (2026-06-20): "It's done/stale — I take over WI-4703" —
  authorized taking over the stale `6f5bd1b5` work-intent claim and committing
  the sibling WI-4707 work first to un-entangle the shared file.
- These are captured as the durable owner-evidence for the bounded PAUTH cited
  above; no further owner decision is required before Loyal Opposition
  verification.

## Prior Deliberations

- `DELIB-S20260620-WI4703-DISPATCH-REPAIR-AUTH` — owner authorization for the
  bounded WI-4703 source/test repair and PAUTH (carried forward from `-003`).
- `DELIB-20265287` — owner-decision anchor for `GOV-AUTOMATION-VALUE-VS-COST-001`.
- `bridge/gtkb-wi4703-dispatch-non-transient-fast-trip-004.md` — the GO this
  report responds to.
- `bridge/gtkb-wi4682-automation-value-cost-principle-014.md` — the dispatch
  churn this fix's diagnosis drew on.

## Risk And Rollback

- Rollback: revert this single source commit; the new test file is additive. No
  state migration — the change reuses the existing
  `circuit_breaker_tripped` / `failure_count` `dispatch-state.json` fields.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
