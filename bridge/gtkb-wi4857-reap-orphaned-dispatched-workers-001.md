NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d5a77c21-caee-404a-8fb3-6629ba276960
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal

# gtkb-wi4857-reap-orphaned-dispatched-workers — Reap in-flight/orphaned dispatched workers at daemon startup and shutdown

Document: gtkb-wi4857-reap-orphaned-dispatched-workers
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4857
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4857-REAP-ORPHANED-WORKERS
Recommended commit type: fix

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Go-live surfaced a dispatched headless worker that outlived its daemon and never produced an exit-code sidecar (dangling toward the `run_with_status.py` exit-124 lifetime cap; the monitor flagged the result as `corrupt_output`). The daemon's `run_loop` finally block (`scripts/gtkb_dispatcher_daemon.py` ~593-600) only unlinks `daemon.pid` and releases the lock — it does **not** reap the workers it spawned. Workers are launched detached (`subprocess.Popen` with `CREATE_NEW_PROCESS_GROUP`, `cross_harness_bridge_trigger.py` ~3509), so an abruptly-dying daemon orphans them with no one to reap or record their outcome.

This proposal adds a reap helper and invokes it at two daemon lifecycle points:

1. **Startup reclaim (load-bearing for daemon-death-orphaned workers):** `run_loop` acquires the single-instance lock before doing anything; holding the lock proves no prior daemon is alive, so any live dispatched worker is an orphan from a dead daemon. Immediately after acquiring the lock, the daemon reaps live dispatched workers. This is the only daemon-side handler for the abrupt-death case (a crashed daemon runs neither its finally block nor the `stop` command).
2. **Graceful-shutdown reap:** `run_loop`'s finally block reaps in-flight workers before releasing the lock, so an in-process termination (loop raises / SystemExit) does not orphan them.

The clean `stop` path already terminates the daemon process tree (`cli.py` `bridge_dispatch_daemon_stop_cmd` → `terminate_pid_tree(daemon_pid)`); a belt-and-suspenders `stop`-command reap is a noted follow-on (it would also catch detached workers the tree-walk misses) and is intentionally out of this slice to keep the change to the daemon + trigger.

### Behavior change (precise)

New `cross_harness_bridge_trigger.reap_inflight_dispatched_workers(runs_dir) -> int`:
- Enumerates `runs_dir/*.pid` sidecars (same enumeration as `_count_live_dispatched_processes`).
- A worker is reaped iff its `<dispatch_id>.pid` exists, `<dispatch_id>.exit_code` is absent/empty, and the PID is alive (`_pid_alive`).
- For each: `_terminate_pid_tree(pid)`, then write `<dispatch_id>.exit_code = 124` (a code already in `dispatch_monitor.WORKER_KILL_EXIT_CODES`, so the monitor classifies the worker as killed rather than dangling/`corrupt_output`).
- Workers that have already exited (exit_code present) or whose PID is dead are skipped untouched. Returns the count reaped. Best-effort: file errors never raise.

New daemon helper `_reap_dispatched_workers(project_root) -> int` resolves `runs_dir = _bridge_poller_state_dir(project_root) / trigger.DISPATCH_RUNS_SUBDIR` and delegates to the trigger helper; wrapped to never raise (so reap failure cannot break daemon startup/shutdown). Called once after lock acquisition and once in the finally block.

No change to dispatch selection, worker spawning, the concurrency cap, or `_count_live_dispatched_processes`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next append-only numbered bridge file.
- `GOV-17` — Automation script modification approval gate; modifies dispatcher automation scripts; owner-authorized (DELIB-20266203, PAUTH cited).
- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher persistent-daemon architecture; worker-lifecycle ownership (no orphaned workers) is part of the daemon's operability contract.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — cites governing specs; tests mapped below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — WI-4857 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — reap behavior maps to derived tests.
- `GOV-STANDING-BACKLOG-001` — WI-4857 is an authorized standing-backlog item under the active project.

## Prior Deliberations

- `DELIB-20266203` — owner grilled plan; Q2 authorizes the full daemon fix-chain including WI-4857 (reap orphaned/timed-out workers) as Phase X step X5; this deliberation is the cited owner-decision evidence for the Phase X work items.
- WI-4855 — daemon process-lifecycle hardening (`stop` tree-kill, single-instance lock) on which the startup-reclaim invariant (lock ⇒ no prior daemon) depends.
- WI-4805 / WI-4834 — existing reset-time and storm-watchdog reap of stale dispatch PIDs; this proposal adds the daemon-lifecycle reap and reuses the same `dispatch-runs` sidecar contract. WI-4790 — `corrupt_output` detection that flagged the dangling orphan.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4857-REAP-ORPHANED-WORKERS` (active; includes WI-4857 + GOV-17 + ADR-DISPATCHER-ARCHITECTURE-001; cites `DELIB-20266203`). The owner approved the full Phase X daemon fix-chain (DELIB-20266203 Q2), of which WI-4857 is step X5. No additional owner decision is required for this proposal.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement (WI-4857 acceptance) is that the daemon track dispatched-worker liveness and reap orphaned/timed-out workers, and that daemon shutdown handle in-flight workers. DELIB-20266203 Q2 authorizes the fix. No new requirement.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| WI-4857: live worker without exit-code is terminated + recorded | `test_reap_inflight_terminates_live_worker` (new) | spawn a real sleeper subprocess, write its `<id>.pid`, no exit_code → `reap_inflight_dispatched_workers` returns 1, the process is terminated, `<id>.exit_code == "124"`. |
| WI-4857: completed worker (exit_code present) is not touched | `test_reap_inflight_skips_completed_worker` (new) | live sleeper + non-empty `<id>.exit_code` → reap returns 0, process still alive (cleaned up after). |
| WI-4857: dead PID is skipped safely | `test_reap_inflight_skips_dead_pid` (new) | `<id>.pid` = a non-live PID, no exit_code → reap returns 0, no exit_code written, no error. |
| WI-4857: daemon startup reaps an orphan worker | `test_daemon_reap_helper_reaps_orphan` (new) | `daemon._reap_dispatched_workers(root)` terminates a live worker sidecar under the bridge-poller `dispatch-runs` dir. |
| Non-regression | existing daemon suite | PASS — startup/finally reap is additive; no spawn/selection change. |

Commands (pre-report): targeted `pytest` over `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` via the repo venv; `ruff check` AND `ruff format --check` on the changed files. Reap is exercised against real short-lived sleeper subprocesses (spawned + cleaned up in the test), not the live dispatch substrate.

## Risk / Rollback

- **Risk:** startup-reclaim could terminate a worker that is still doing useful work. Mitigated by the single-instance invariant: `run_loop` only proceeds past `acquire_daemon_lock` when no other daemon holds the lock, so a live worker at that point has no live owning daemon and is a genuine orphan (its outcome would never be processed). Reaping it frees the slot for re-dispatch. A double-reap (with the storm watchdog) is idempotent — `_terminate_pid_tree` no-ops on a dead PID.
- **Risk:** reap failure during finally could mask shutdown. Mitigated: `_reap_dispatched_workers` is wrapped to never raise; PID-file removal and lock release still run.
- **Rollback:** single-commit revert removes the reap helper and its two call sites. No KB mutation (`kb_mutation_in_scope: false`); append-only bridge history untouched.

## Recommended Commit Type

`fix` — repairs daemon-death-orphaned / in-flight dispatched-worker leakage. The reap helper is additive but corrects a lifecycle defect, not a new capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
