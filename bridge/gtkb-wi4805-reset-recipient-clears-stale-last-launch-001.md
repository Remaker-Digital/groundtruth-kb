NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: e6490e91-a7fd-489d-be63-363714e9ba47
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

bridge_kind: prime_proposal
Document: gtkb-wi4805-reset-recipient-clears-stale-last-launch
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4805
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

## Summary

WI-4805 slice 1: make `--reset-recipient` clear the stale last_launch failure markers so dispatch health stops reading FAIL for a recipient after a reset. This is the first item of the dispatcher-reliability lane takeover (owner AUQ 2026-06-26) under the existing Fixes-then-Phases authorization.

## Scope (slice 1 of WI-4805)

WI-4805 has two gaps. This slice fixes part 1 (reset clears stale last_launch failure state). Part 2 (reap live-but-stale dispatch-run PIDs before exit) is now reduced-necessity: WI-4845's worker-lifetime cap kills hung workers (exit 124) and WI-4803 releases their work-intent claims on that failure, so the hung-worker leak part 2 targeted is already handled -- at the lifetime cap rather than at N-min-stale. Part 2 is deferred as a reconcile/follow-on, re-evaluated against the landed WI-4845/WI-4803 behavior (a faster stale-reap is an optimization, no longer a correctness gap).

## Problem / Root Cause

`_reset_recipient_state` (scripts/cross_harness_bridge_trigger.py:700) clears `failure_count`, `circuit_breaker_tripped`, `circuit_breaker_tripped_at`, and `circuit_breaker_half_open` for a matched recipient -- but it never touches that recipient's `last_launch` failure markers. The "previous launch failed" health detector returns a FAIL record when `last_launch` carries a failure `exit_code` (the exit_code branch) OR an `exit_failure_reason` (cross_harness_bridge_trigger.py:1037-1050). So after `--reset-recipient`, the recipient still reads FAIL until a successful launch overwrites `last_launch` -- the stale-FAIL class (WI-4789 / WI-4725 lineage), exactly what an explicit reset is supposed to clear.

## Specification Links

- ADR-DISPATCHER-ARCHITECTURE-001 (architecture_decision) -- dispatcher architecture-of-record; the reset command is part of the dispatch operational contract and must produce a clean recipient state.
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001 (requirement) -- dispatch health must reflect real dispatchability; a stale-FAIL after an explicit reset is a health-accuracy defect.
- DCL-DISPATCH-ENVELOPE-RULES-001 (design_constraint) -- the recipient-state envelope; the reset clears the recipient's failure envelope consistently.
- GOV-FILE-BRIDGE-AUTHORITY-001 (governance) -- bridge protocol authority; filed as the next append-only numbered bridge file in the versioned chain.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (design_constraint) -- this proposal cites all governing specs.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (design_constraint) -- spec-to-test mapping below.
- GOV-STANDING-BACKLOG-001 (governance) -- WI-4805 is the governing backlog item.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (architecture_decision) -- the change is captured as durable artifacts (this thread, the PAUTH, spec-derived tests).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (design_constraint) -- the work-item-to-test trigger is honored.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (governance) -- governed proposal/review/implement/verify cycle.

## Prior Deliberations

- DELIB-20266137 -- owner authorization of the dispatcher-reliability Fixes-then-Phases drive (covers WI-4805); the source authority under PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26.
- WI-4789 / WI-4725 -- the dispatch-health stale-FAIL lineage this slice reduces.
- WI-4845 / WI-4803 (VERIFIED this session) -- the landed worker-lifetime cap + claim-release-on-failure that make WI-4805 part 2 reduced-necessity.
- No prior deliberation decided the reset-clears-last_launch mechanism; deliberation search ("reset-recipient clears stale last_launch dispatch health") surfaced no on-point precedent.

## Requirement Sufficiency

Existing requirements sufficient -- ADR-DISPATCHER-ARCHITECTURE-001 + SPEC-CENTRALIZED-DISPATCH-SERVICE-001 establish that an explicit recipient reset must yield a clean, accurate health state. No new or revised requirement is needed before implementation.

## Proposed Implementation

1. scripts/cross_harness_bridge_trigger.py: in `_reset_recipient_state`, when a recipient is matched (the existing loop that zeroes failure_count and clears the circuit breaker), also clear its stale last_launch failure markers -- pop `exit_code` and `exit_failure_reason` from `last_launch` when present, and clear the recipient-level `last_failure_reason` -- so the "previous launch failed" detector returns None for that recipient after the reset. Additive and idempotent; the existing failure_count / circuit-breaker reset and the reset-guard / write path are unchanged.
2. platform_tests/scripts/test_cross_harness_bridge_trigger.py: add a focused unit test exercising `_reset_recipient_state` directly (NOT the run_trigger integration path, which carries the pre-existing WI-4712 failures): build a dispatch state with a recipient whose last_launch has exit_code=124 + exit_failure_reason and a tripped circuit breaker; call `_reset_recipient_state`; assert the failure markers are cleared, an unrelated recipient is untouched, and the previous-launch-failed detector returns None for the reset recipient.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| SPEC-CENTRALIZED-DISPATCH-SERVICE-001 (reset yields clean health) | test_reset_recipient_clears_stale_last_launch_failure (new) | after reset, last_launch.exit_code + exit_failure_reason are cleared and the previous-launch-failed detector returns None for the recipient |
| ADR-DISPATCHER-ARCHITECTURE-001 (reset is scoped to the target) | same test | only the targeted recipient is reset; an unrelated recipient's last_launch is untouched |
| No-regression | existing failure_count / circuit-breaker reset behavior unchanged; targeted unit test avoids the WI-4712 run_trigger path; ruff check + ruff format --check on the changed files | green |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -k reset_recipient -q --tb=short`; `python -m ruff check` then `python -m ruff format --check` on the changed files.

## Risk / Rollback

- Risk: low. Additive clearing inside the existing matched-recipient reset branch; fires only for recipients the operator explicitly resets; touches no dispatch-target selection, signature/dedupe, or success-path behavior. It cannot clear another recipient's state (the match condition is unchanged).
- Rollback: revert the marker-clearing lines and the new test; prior behavior (stale FAIL until a successful launch) returns. No schema change; append-only KB untouched.
- Out of scope: WI-4805 part 2 (live-but-stale dispatch-run PID reap; deferred as reduced-necessity per the Scope section), the other reset/quiesce commands, and the health computation itself.

## Owner Decisions / Input

- DELIB-20266137 (AskUserQuestion, 2026-06-26): owner authorized the dispatcher-reliability Fixes-then-Phases drive (WI-4803/4804/4805/4834/4788/4790/4793) under PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26 (source + test).
- Owner AUQ (2026-06-26): "Take over the lane -- it's done" -- directing this session to drive the remaining reliability WIs to completion after the concurrent session finished its committed work.

## Recommended Commit Type

fix -- repairs the stale-FAIL that persists after `--reset-recipient` (a dispatch-health-accuracy defect); no new capability surface.
