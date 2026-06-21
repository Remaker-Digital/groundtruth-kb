NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f6ca6785-12f7-4d08-808f-74566b1f10c0
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

# Post-implementation report: WI-4662 cooldown-gated previous_launch_failed re-log + lo_failover_exhausted terminal

bridge_kind: implementation_report
Document: gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover
Version: 003 (NEW)
Recommended commit type: fix:

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4662

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implements the GO'd proposal (`-001` NEW, `-002` GO). All edits are additive and confined to the two `target_paths`. The original implementer session (`600b3b4c`) let its go_implementation claim lapse without a report; this report is filed by a fresh interactive Prime Builder session (`f6ca6785`) that re-acquired the claim and implemented the approved design. Implementation-start authorization packet: `sha256:359665224a00abd0351c5880e17c17b0ec7b4085afb04e0a191a88dc23fdfdd0` (derived from `-002` GO).

The base already contained WI-4703 (`9af7607a1`) and WI-4707 (`294fa0bd3`); per the proposal's composition note, the WI-4703 `effective_trip_threshold` line and `FAST_TRIP_FAILURE_CLASSES` were left untouched — this change adds only the success-branch pops and new fields.

## Implemented changes (`scripts/cross_harness_bridge_trigger.py`, +99/-3)

1. **`_should_relog_previous_launch_failure(recipient_state, *, now=None)`** (new helper) — returns True when no cooldown stamp exists or the cooldown window (`_dispatch_retry_delay_seconds()`, env `GTKB_DISPATCH_RETRY_DELAY_SECONDS`) has elapsed; False inside the window. Fail-open (True) on a missing/unparseable stamp.
2. **`_LO_FAILOVER_EXHAUSTION_SKIP_REASONS`** (new constant) = `{provider_failure_backoff_active, previous_launch_failed}`.
3. **`_is_lo_failover_exhausted(failure_reason, recipient, fallback_skipped_candidates)`** (new helper) — extracts the terminal-vs-relog decision so it is unit-testable: True only for `no_ready_target_for_role` + `loyal-opposition` + ≥1 skipped candidate with a failure/back-off reason.
4. **Cooldown carry-forward** in the per-cycle `recipient_state` init: `previous_launch_failed_logged_at` is inherited from `prior` (recipient_state is rebuilt fresh each cycle and otherwise drops it), so the throttle persists across reconcile cycles.
5. **Dispatch-path re-record gate**: the `_record_dispatch_failure(...)` for a detected `previous_launch_failed` is gated by `_should_relog_...` and stamps `previous_launch_failed_logged_at` on emit; the in-memory `previous_launch_failed` annotation is still set every cycle (status/diagnose visibility unchanged).
6. **`_provider_failure_backoff_skip` re-record gates** (both sites): gated by `_should_relog_...(prior)`, stamping `prior["previous_launch_failed_logged_at"]` in place. `_prior_state_for_target` returns the live `recipients_state` dict (and the record sites are only reached when `prior` is non-empty), so the stamp persists and flows through `_seed_provider_failure_skip_state` (`dict(prior)`).
7. **Recovery clear** in `_process_pending_exit_codes` success branch: `previous_launch_failed_logged_at` and `previous_launch_failed` are popped alongside the existing `failure_count` / circuit-breaker reset, so a recovered target re-logs immediately on a later failure.
8. **`lo_failover_exhausted` terminal record**: when the ranked LO list is exhausted by launch-failure/back-off skips, `last_result = "lo_failover_exhausted"` and one cooldown-gated failure row (reason `lo_failover_exhausted`, with `fallback_skipped_candidates`) is emitted instead of an unbounded `no_ready_target_for_role` re-log. The WI-4484 multi-active failover (a candidate is selected) is unaffected.

New test file `platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py` (7 tests).

## Specification Links (carried forward from -001)

- `GOV-AUTOMATION-VALUE-VS-COST-001` — gate the expensive, noisy unconditional re-record behind a cheap deterministic cooldown/terminal-state check.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this bridge filing and the numbered-file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` — WI-4662 governed backlog candidate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both changed files under `E:\GT-KB`.

## Specification-Derived Verification (spec-to-test mapping + results)

Commands (run from `E:\GT-KB`, `GTKB_NO_CROSS_HARNESS_TRIGGER` cleared):

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py -q` → **7 passed**.
- Regression: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_concurrency_cap.py platform_tests/scripts/test_dispatch_non_transient_fast_trip.py -q` → **112 passed** (no regression; WI-4703/WI-4484 behavior intact).
- `ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py` → **All checks passed!**
- `ruff format --check ...` → **clean** (both files formatted).

| Specification / behavior (proposal acceptance criterion) | Test | Result |
| --- | --- | --- |
| Re-record cooldown-gated: ≤1 `previous_launch_failed` row per window | `test_backoff_skip_throttles_relog_and_keeps_annotation` (cycle 1 → 1 row; cycle 2 within window → still 1) | PASS |
| Re-record resumes after the window elapses | same test (advance stamp past cooldown → 2 rows) + `test_should_relog_respects_cooldown_window` | PASS |
| In-memory `previous_launch_failed` annotation set every cycle | `test_backoff_skip_throttles_relog_and_keeps_annotation` (both skips carry `previous_launch_failed`) | PASS |
| Cooldown window boundary honors `GTKB_DISPATCH_RETRY_DELAY_SECONDS` | `test_should_relog_respects_cooldown_window` (299s→False, 300s→True) | PASS |
| First failure (no stamp) logs; malformed stamp fail-opens | `test_should_relog_true_when_no_stamp`, `test_should_relog_true_when_stamp_unparseable` | PASS |
| Recovery clears the cooldown stamp + annotation (failure_count/breaker reset preserved) | `test_recovery_clears_previous_launch_failed_stamp` | PASS |
| Exhausted ranked-LO failover → bounded terminal decision | `test_lo_failover_exhausted_true_for_lo_with_failure_skip` | PASS |
| Multi-active / non-failure exhaustion stays non-terminal (WI-4484 unchanged) | `test_lo_failover_exhausted_false_for_non_failure_or_non_lo` (selected→False, prime-builder→False, not-ready-only→False, empty/None→False) | PASS |

**Coverage boundary (transparency):** the cooldown throttle is verified at a *real* `_record_dispatch_failure` site (`_provider_failure_backoff_skip`), the recovery clear is verified through `_process_pending_exit_codes`, and the `lo_failover_exhausted` *decision* is verified through the extracted `_is_lo_failover_exhausted` predicate. The `lo_failover_exhausted` *record emission + last_result assignment* live inline in `run_trigger`; they are a thin wrapper over two unit-tested functions (the predicate above + the `_should_relog_...` once-per-window throttle), and are not separately driven through a full multi-LO `run_trigger` integration (the existing `run_trigger` fixture is heavyweight). Flagged for reviewer judgment; an end-to-end multi-LO integration test can be added on request.

## Owner Decisions / Input

- This is project-authorized bridge-protocol reliability work under `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, covered by `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002` (owner-decision `DELIB-20265459`, AUQ 2026-06-21). Per the `-001` proposal's Owner Decisions section, no additional owner decision was required to implement once the proposal received GO.
- The interactive owner directed this take-over via AskUserQuestion this session (2026-06-21): asked how to proceed after the original implementer's claim lapsed, the owner selected **"Take over now"**.

## Prior Deliberations

- `DELIB-20265484` — Loyal Opposition GO verdict for this thread (the `-002` GO being implemented).
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-001.md` .. `-008.md` (VERIFIED, WI-4484) — the ordered LO failover this change extends with the bounded exhausted-terminal record.
- `bridge/gtkb-wi4703-dispatch-non-transient-fast-trip-*` (landed) — the same-file fast-trip breaker this composes with; its `effective_trip_threshold` / `FAST_TRIP_FAILURE_CLASSES` lines were left untouched.

## Files Changed

- `scripts/cross_harness_bridge_trigger.py` (modified, +99/-3) — new helpers/constant, cooldown carry-forward + gates at three record sites, recovery clear, lo_failover_exhausted terminal.
- `platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py` (new, 7 tests).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
