NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 130bf9ae-15f0-4373-a7b5-9286568dbc97
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

# gtkb-wi4805-reset-recipient-stale-last-launch-pid-reap — reset-recipient clears stale last_launch + signature and reaps the recipient's hung dispatch-run process

bridge_kind: prime_proposal
Document: gtkb-wi4805-reset-recipient-stale-last-launch-pid-reap
Version: 001

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4805

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4805 (improvement): the manual `--reset-recipient` admin command is a half-clean. `_reset_recipient_state` (`cross_harness_bridge_trigger.py:700`) resets `failure_count` and the circuit-breaker fields, but it leaves the recipient's `last_launch` in place — including its stale `signature` / `last_dispatched_signature` / `last_suppressed_signature`, stale `exit_code`, and the recorded worker `pid`. A reset is meant to give a stuck recipient a clean slate, but the residual stale `last_launch`/signature can still gate (or mis-gate) re-dispatch, and any hung worker process from that recipient's last dispatch run is left running. This change makes `--reset-recipient` a true clean slate: it clears the stale launch + signature state, and it reaps the recipient's recorded dispatch-run process when that process is a definitely-hung straggler.

## Problem detail (for LO review)

- `cross_harness_bridge_trigger.py:714-722` — for each matching recipient key, `_reset_recipient_state` sets `failure_count = 0`, `circuit_breaker_tripped = False`, `updated_at`, and pops `circuit_breaker_tripped_at` / `circuit_breaker_half_open`. It does NOT touch `last_launch`, `signature`, `last_dispatched_signature`, or `last_suppressed_signature`.
- Consequence 1 (stale state): a reset recipient keeps its prior `last_launch` (stale `signature`, `exit_code`, `exit_code_processed`, etc.). Re-dispatch arming depends on signature comparison and `last_launch` failure fields, so a reset that leaves them is not a clean slate.
- Consequence 2 (leftover process): the recipient's last dispatch may have left a hung worker (`last_launch["pid"]`, recorded at spawn). The reset does not reap it, so the operator's explicit "reset this stuck recipient" leaves the stuck worker running.
- `last_launch` already carries the data to reap: `last_launch.get("pid")` (the dispatched root pid, read elsewhere at `:3744`) and the launch timestamp via `_launch_ts(last_launch)` (used at `:3774`). `_pid_alive(pid)` already exists for liveness.

## Proposed change

1. `scripts/cross_harness_bridge_trigger.py` — in `_reset_recipient_state`, for each matching recipient (inside the existing `:716-722` block):
   - Capture `prior_last_launch = recipients_state[key].get("last_launch")` before mutating.
   - Clear stale launch/signature state for a true clean slate: pop `last_launch`, and set `signature = None`, `last_dispatched_signature = None`, `last_suppressed_signature = None`. (The existing `failure_count` / circuit-breaker resets are unchanged.) This makes re-dispatch arm on fresh evaluation rather than stale equality.
   - Reap the recipient's hung dispatch-run process: if `prior_last_launch` has an int `pid` that `_pid_alive(pid)` is True AND the launch age (`now - _launch_ts(prior_last_launch)`) is at least the worker-lifetime straggler threshold (>= `run_with_status` `DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS` + margin — a process from a launch older than any legitimate worker lifetime is a definitely-hung straggler), terminate its process tree via a new `_terminate_pid_tree(pid)` helper. Record the reap in the reset result.
2. `scripts/cross_harness_bridge_trigger.py` — new `_terminate_pid_tree(pid)` helper mirroring `run_with_status.py._terminate_process_tree`: Windows `taskkill /F /T /PID <pid>` (CREATE_NO_WINDOW); POSIX `os.killpg(os.getpgid(pid), SIGKILL)` with a `proc.kill()`/`os.kill` fallback. Best-effort, swallows errors (a reset must never fail because a pid was already gone).
3. `platform_tests/scripts/test_cross_harness_bridge_trigger.py` — tests below.

The reap is scoped to the recipient's OWN recorded dispatch-run pid (provenance from `last_launch`, written at spawn), gated on liveness AND a staleness threshold, and only fires on the explicit manual `--reset-recipient` operator action — so it cannot reach an interactive session or a freshly-launched healthy worker. No change to the reset guard, the recipient-key matching, the failure/circuit-breaker resets, or any automatic dispatch path.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher architecture-of-record; reset-recipient is the operator clean-slate control and must leave the recipient genuinely re-dispatchable with no leftover hung worker.
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` — the reap is operator-initiated and scoped to the recipient's own recorded straggler; it asserts no kill-switch and never touches interactive sessions.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — dispatch-service reliability.
- `DCL-DISPATCH-ENVELOPE-RULES-001` — dispatch lifecycle rules.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4805 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266137` — owner authorization for this dispatcher-reliability drive (Fixes-then-Phases); source authority for WI-4805.
- WI-4702 (`bridge dispatch --reset-recipient default --state-dir mismatch`) — adjacent reset-recipient defect lineage; this WI hardens the same command's clean-slate semantics.
- WI-4845 / WI-4806 worker-lifetime lineage — the 600s worker-lifetime cap defines the straggler threshold this reap uses.
- Deliberation search ("reset-recipient stale last_launch reap dispatch pids") surfaced no prior decision on the reset-clean-slate-plus-reap mechanism.

## Owner Decisions / Input

- Authorized by `DELIB-20266137` (owner AUQ this session, 2026-06-26); `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26` covers WI-4805. No further owner decision is required: the reap is gated to the recipient's own recorded straggler under an explicit operator reset, so it changes no automatic dispatch behavior and cannot harm interactive sessions.
- Topology this session: Claude (B) = Prime Builder; Cursor (E) = Loyal Opposition reviewer.

## Requirement Sufficiency

Existing requirements sufficient — `ADR-DISPATCHER-ARCHITECTURE-001` (reset-recipient is the clean-slate control) + `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` (no interactive harm, no kill-switch) fully constrain the change. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (clean slate) | `test_reset_recipient_clears_stale_last_launch_and_signature` (new) | After `_reset_recipient_state`, the matched recipient has no `last_launch` and `signature` / `last_dispatched_signature` / `last_suppressed_signature` are None; `failure_count` / circuit-breaker resets still apply (regression). |
| ADR-DISPATCHER-ARCHITECTURE-001 (reap hung worker) | `test_reset_recipient_reaps_stale_alive_dispatch_pid` (new) | A recipient whose `last_launch` has an alive `pid` and a launch age past the straggler threshold triggers `_terminate_pid_tree(pid)` (spied). |
| SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (no over-reap) | `test_reset_recipient_does_not_reap_fresh_or_dead_pid` (new) | A fresh launch (age below threshold) or a dead pid is NOT terminated. |
| No-regression | existing reset-recipient behavior (guard acquire/release, key matching, reset_count, not_found) unchanged; `ruff check` / `ruff format --check` on the changed `.py` files | green |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -k "reset_recipient" -q --tb=short`; `ruff check` then `ruff format --check` on the changed files.

## Risk / Rollback

- Risk: low. State-clearing is mechanical. The reap fires only under an explicit manual `--reset-recipient`, only on the recipient's OWN recorded `last_launch.pid`, only when that pid is alive AND the launch is older than any legitimate worker lifetime (a definitely-hung straggler). Residual pid-reuse risk is bounded by the staleness gate (a reused pid that is also older-than-max-lifetime AND equals the recorded root pid is a remote coincidence under a deliberate operator reset); the kill is best-effort and swallows errors. No automatic path kills anything.
- Rollback: revert the `_reset_recipient_state` clean-slate/reap block, the `_terminate_pid_tree` helper, and the new tests; prior behavior (reset leaves stale `last_launch`/signature and the hung worker) returns. No schema change; append-only KB untouched.
- Out of scope: the storm-watchdog dormancy + kill-switch auto-clear (WI-4804), the dead-root orphan provenance reap (WI-4834), and any change to automatic dispatch or the lease registry.

## Recommended Commit Type

`fix:` — repairs the `--reset-recipient` clean-slate semantics (stale `last_launch`/signature left in place; hung worker not reaped). Operator-scoped, gated reap; no automatic-path behavior change.
