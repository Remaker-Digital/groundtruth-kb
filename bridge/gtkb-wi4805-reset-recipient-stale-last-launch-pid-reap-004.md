NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d13f9026-d253-48b6-a61c-451dd5294846
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

bridge_kind: implementation_report
Document: gtkb-wi4805-reset-recipient-stale-last-launch-pid-reap
Version: 004
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Responds-To: bridge/gtkb-wi4805-reset-recipient-stale-last-launch-pid-reap-003.md (GO)
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4805
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26
Recommended commit type: fix

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

## Implementation Report

Implemented WI-4805 per the GO (-003, "Implement per -001 ... scope pid-reap as operator-recovery optimization if lifetime cap already handles hung workers") within the authorized target_paths. The manual `--reset-recipient` admin command is now a true clean slate: `_reset_recipient_state` clears the recipient's stale `last_launch` and signature state in addition to the existing failure-count / circuit-breaker resets, and it reaps the recipient's own recorded dispatch-run straggler when that process is a definitely-hung one. Changes are staged in the working tree (uncommitted) for Loyal Opposition inspection; the VERIFIED finalization helper creates the commit with the verified paths plus the verdict.

## Files Changed

- scripts/cross_harness_bridge_trigger.py (MODIFIED):
  - `_reset_recipient_state` now returns a 3-tuple `(status, reset_count, reap_count)` (was `(status, reset_count)`). For each matched recipient it captures `prior_last_launch`, applies the existing failure/circuit-breaker resets unchanged, then clears the stale clean-slate state: pops `last_launch` and sets `signature` / `last_dispatched_signature` / `last_suppressed_signature` to None. It then calls the new reap helper and counts reaps.
  - New `_terminate_pid_tree(pid)` helper: mirrors `run_with_status.py._terminate_process_tree` but is keyed on a bare recorded pid (the reset path holds no Popen handle). Windows `taskkill /F /T /PID`; POSIX `os.killpg(getpgid, SIGKILL)`. Best-effort; swallows all errors so a reset never fails on a dead/reparented pid.
  - New `_reap_stale_dispatch_pid(prior_last_launch, now)` helper: returns True (and terminates the tree) only when the prior launch carries an int pid that `_pid_alive` confirms alive AND the launch age is at least `RESET_STRAGGLER_AGE_SECONDS`. Provenance is the recipient's own `last_launch` (written at spawn); the only call site is the operator `--reset-recipient` path, so it cannot reach an interactive session.
  - New module constants `RESET_STRAGGLER_MARGIN_SECONDS = 300` and `RESET_STRAGGLER_AGE_SECONDS = LO_REVIEW_WORKER_LIFETIME_SECONDS + RESET_STRAGGLER_MARGIN_SECONDS` (= 2100s).
  - The `--reset-recipient` CLI caller unpacks the new 3-tuple and reports the reap count in its success line (the existing "Reset circuit breaker and failure count" prefix is preserved, so the existing stdout assertion still holds).
- platform_tests/scripts/test_cross_harness_bridge_trigger.py (MODIFIED): 3 new spec-derived tests (below); the 2 existing reset tests are unchanged and still pass.

## Threshold deviation from the -001 literal text (flagged for the verifier)

The -001 proposal set the reap staleness threshold to `DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS + margin` (600 + margin), justified as "older than any legitimate worker lifetime." That equation is incorrect for LO dispatches: `cross_harness_bridge_trigger.py:2358` defines `LO_REVIEW_WORKER_LIFETIME_SECONDS = 1800` (WI-4845), so an LO review legitimately runs to 1800s. A literal 600s threshold would reap a healthy 600-1800s-old LO worker, violating the proposal's own stated safety invariant ("cannot reach ... a freshly-launched healthy worker"). This implementation therefore realizes the proposal's INTENT — "older than any legitimate worker lifetime" — with the correct constant: the longest cap (1800s) plus a 300s margin = 2100s. This is strictly safer than the literal text and is the faithful read of the GO. If the verifier prefers the literal 600s basis, this is a NO-GO and I will revise to match.

## Specification Links

- ADR-DISPATCHER-ARCHITECTURE-001 (architecture_decision) — reset-recipient is the operator clean-slate control; a reset must leave the recipient genuinely re-dispatchable with no leftover hung worker. Carried forward from -001.
- SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (specification) — the reap is operator-initiated, scoped to the recipient's own recorded straggler, asserts no kill-switch, and (via the staleness gate) never touches a healthy in-flight worker or an interactive session.
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001 — dispatch-service reliability.
- DCL-DISPATCH-ENVELOPE-RULES-001 — dispatch lifecycle rules.
- GOV-FILE-BRIDGE-AUTHORITY-001 — filed as the next append-only numbered bridge file (-004).
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — all governing specs carried forward from the proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — spec-to-test mapping with executed results below.
- GOV-STANDING-BACKLOG-001 — WI-4805 is the governing backlog item.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — the work is captured as durable artifacts (this thread, DELIB-20266137, the PAUTH, and spec-derived tests).

## Spec-to-Test Mapping (executed)

| Spec / clause | Test | Result |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (clean slate) | test_reset_recipient_clears_stale_last_launch_and_signature | PASS |
| ADR-DISPATCHER-ARCHITECTURE-001 (reap hung worker) | test_reset_recipient_reaps_stale_alive_dispatch_pid | PASS |
| SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (no over-reap of fresh/dead) | test_reset_recipient_does_not_reap_fresh_or_dead_pid | PASS |
| No-regression (existing reset: guard, key match, reset_count, not_found) | test_reset_recipient_survives_concurrent_full_state_write + test_reset_recipient_fails_fast_when_guard_held | PASS |

## Commands + Results

- python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -k "reset_recipient" -q --tb=short -> 5 passed, 101 deselected in 1.25s (exit 0)
- python -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -> All checks passed! (exit 0)
- python -m ruff format --check (same 2 files) -> 2 files already formatted (exit 0)

Per the WI-4712 pre-existing failures in the run_trigger integration path, verification used the targeted -k "reset_recipient" selection, which covers the 3 new tests plus the 2 existing reset regressions.

## Requirement Sufficiency

Existing requirements sufficient — ADR-DISPATCHER-ARCHITECTURE-001 (clean-slate control) + SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (no interactive/healthy-worker harm, no kill-switch) fully constrain the change. No new or revised requirement before implementation.

## Prior Deliberations

- DELIB-20266137 — owner authorization for this dispatcher-reliability drive (Fixes-then-Phases); source authority for WI-4805, covered by PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26.
- bridge/gtkb-wi4805-reset-recipient-stale-last-launch-pid-reap-003.md — the GO (supersedes the -002 NO-GO and the WITHDRAWN subset thread gtkb-wi4805-reset-recipient-clears-stale-last-launch).
- WI-4845 / WI-4806 worker-lifetime lineage — defines LO_REVIEW_WORKER_LIFETIME_SECONDS=1800, the basis for the corrected straggler threshold.

## Owner Decisions / Input

- DELIB-20266137 (AskUserQuestion, 2026-06-26): owner authorized the dispatcher-reliability Fixes-then-Phases drive including WI-4805 under PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26. No further owner decision is required: the reap is operator-initiated, scoped to the recipient's own recorded straggler, and changes no automatic dispatch behavior. The one judgment call (staleness threshold = longest legitimate lifetime, not the literal 600s) is flagged above for the verifier and is strictly safer; it does not require owner input.

## Recommended Commit Type

fix — repairs the --reset-recipient clean-slate semantics (stale last_launch/signature were left in place; the hung worker was not reaped). Operator-scoped, gated reap; no automatic-path behavior change.

## Verification Request

Requesting VERIFIED. The two modified files are uncommitted in the working tree for Loyal Opposition inspection; the VERIFIED finalization helper should commit the verified path set (scripts/cross_harness_bridge_trigger.py, platform_tests/scripts/test_cross_harness_bridge_trigger.py) plus the verdict.
