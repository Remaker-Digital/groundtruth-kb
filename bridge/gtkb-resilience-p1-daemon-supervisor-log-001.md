NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 75cea783-a1f3-4f8b-b834-cca62d92299c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal

# gtkb-resilience-p1-daemon-supervisor-log — Resilience P1 Slice 1: supervisor scheduled task + persistent daemon log so the daemon stays up unattended and its death is diagnosable

Document: gtkb-resilience-p1-daemon-supervisor-log
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4882
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Recommended commit type: feat

target_paths: ["scripts/ensure_dispatcher_daemon.py", "scripts/gtkb_dispatcher_daemon.py", "scripts/install_dispatcher_daemon_task.ps1", "scripts/uninstall_dispatcher_daemon_task.ps1", "platform_tests/scripts/test_dispatcher_daemon_supervision.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice 1 of WI-4882 (Daemon Resilience program, Phase 1) addresses the two `keep-live` gaps observed during PHASE-Y go-live: the dispatcher daemon died unsupervised (~40 min uptime, stayed dead ~7 min until a manual restart) and left ZERO diagnostic trail because it writes only `status.json` + `shadow-decisions.jsonl` and has no persistent activity/error log. This slice makes the daemon (1) stay up unattended via an OS-level supervisor and (2) leave a recoverable record of why it died.

Root-cause context: `scripts/gtkb_dispatcher_daemon.py` `run_loop` wraps `while True: run_tick(); sleep()` in a `try/finally` that releases the lock but has NO `except` that logs a fatal exception. `run_tick` is internally fail-soft, but any exception raised outside it kills the loop silently. The `gt bridge dispatch daemon start` CLI (`cli.py:943`) raises "already running" (non-zero exit) when the daemon is alive, so it is NOT safe to call repeatedly from a supervisor.

### Deliverables (precise)

1. New `scripts/ensure_dispatcher_daemon.py` — an idempotent ensure-alive entrypoint. It checks `daemon_process_alive(state_dir)` (and `read_daemon_status(...).running`); when the daemon is alive it prints a no-op message and exits 0; when dead it spawns the detached daemon loop reusing the existing `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP` spawn pattern (mirroring `cli.py` start), then exits 0. Accepts `--project-root` and `--interval`. This is the command the supervisor task invokes; it never raises on the already-running path.

2. Modify `scripts/gtkb_dispatcher_daemon.py` — add a persistent rotating daemon log at `.gtkb-state/dispatcher-daemon/daemon.log` via a `logging.handlers.RotatingFileHandler` (bounded size + backup count). Wire INFO-level per-tick summaries (tick time, spawn count, mode) and WARN/ERROR for anomalies. Wrap the `while True` loop body in a try/except that logs the full exception + traceback at ERROR before the existing `finally` cleanup runs, so the next unsupervised death is diagnosable. Logging must be fail-soft: a logging error never breaks a tick or the loop.

3. New `scripts/install_dispatcher_daemon_task.ps1` + `scripts/uninstall_dispatcher_daemon_task.ps1` — register/unregister a `GTKB-DispatcherDaemon` Windows scheduled task, modeled on `scripts/install_single_harness_dispatcher_task.ps1`: hidden, `pythonw.exe` invoking `scripts/ensure_dispatcher_daemon.py --project-root <root> --interval <n>`, repeating every `IntervalMinutes` (default 1), idempotent registration (unregister-then-register), `-DryRun` prints the rendered command line and makes no Task Scheduler call, `-TaskName` overridable for nonce-suffixed test tasks.

4. New `platform_tests/scripts/test_dispatcher_daemon_supervision.py` — spec-derived tests (mapped below).

This slice does NOT change dispatch behavior, the actionable-signature scheme, or worker spawning; it is supervision + observability only. The storm-watchdog FAILSAFE-decider repair is deferred to WI-4882 Slice 2.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal is filed as the next numbered bridge file (`bridge/gtkb-resilience-p1-daemon-supervisor-log-001.md`) in the append-only versioned bridge chain, with the implementation report and verdict to follow as later numbered versions.
- `ADR-DISPATCHER-ARCHITECTURE-001` — the dispatcher daemon architecture this slice hardens; supervision + diagnosability are within its scope.
- `GOV-17` (Automation script modification approval gate) — this adds/modifies dispatcher automation scripts (the ensure entrypoint, the daemon, and the scheduled-task installers); the change is bridge-reviewed and owner-authorized via `DELIB-20266276` (D3 supervision mechanism) and the cited PAUTH.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: cites governing specs; tests mapped below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: WI-4882 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: the supervision + logging behaviors map to derived tests below.
- `GOV-STANDING-BACKLOG-001` — WI-4882 is an authorized standing-backlog item under the active project authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the supervisor + log are durable tracked surfaces (scripts, scheduled task, test) per artifact-oriented governance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the work is tracked as durable artifacts (work item, bridge thread, scripts, test).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — new automation surfaces are created under a backlog/work-item-triggered artifact event.

## Prior Deliberations

- `DELIB-20266276` — owner scope-lock for the Daemon Resilience program. D2 (full auto-recovery, all modes — daemon death auto-restart within ~1 interval) and D3 (dedicated `GTKB-DispatcherDaemon` scheduled task, idempotent ensure-alive, kept separate from the storm-watchdog) directly authorize and shape this slice.
- `DELIB-20266272` — PHASE-Y full daemon go-live; the live exercise during which the daemon died unsupervised with no log, motivating WI-4882.
- `DELIB-20266203` — autonomous-loop plan (Q6 tight single-thread, kill-switch armed); supervision is the keep-live prerequisite for unattended operation.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION` (active; includes WI-4882 + ADR-DISPATCHER-ARCHITECTURE-001 + GOV-17; allowed mutations source, test, config; cites `DELIB-20266276`). The owner selected the supervision mechanism via AskUserQuestion (grilling 2026-06-27, archived as `DELIB-20266276` D3): "Dedicated scheduled task" — a `GTKB-DispatcherDaemon` task running the idempotent ensure-alive path, kept separate from the storm-watchdog. D2 fixed the recovery posture as full auto-recovery (daemon death auto-restart within ~1 interval). No further owner decision is required for this slice.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are `DELIB-20266276` D2 (daemon death must auto-recover within ~1 interval) and D3 (dedicated scheduled-task supervisor, idempotent ensure-alive, separate from the watchdog). This slice implements exactly those decisions plus the persistent-log diagnosability prerequisite they imply. No new or revised requirement is needed.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| D3 idempotent ensure-alive (no-op when alive) | `test_ensure_is_idempotent_noop_when_alive` (new) | with a live daemon (or a stubbed-alive `daemon_process_alive`), `ensure_dispatcher_daemon` exits 0 and spawns NO new process. |
| D2/D3 ensure restarts a dead daemon | `test_ensure_restarts_dead_daemon` (new) | with no live daemon and a stale/absent pid, `ensure_dispatcher_daemon` spawns a detached daemon and exits 0; the new daemon acquires the lock. |
| Persistent log on activity | `test_daemon_log_written_on_tick` (new) | after a tick, `.gtkb-state/dispatcher-daemon/daemon.log` exists and contains an INFO tick record. |
| Fatal-exception is logged before death | `test_fatal_exception_logged` (new) | when the loop body raises (injected), the ERROR + traceback is written to `daemon.log` before the loop exits (so the death is diagnosable). |
| Logging is fail-soft | `test_logging_failure_does_not_break_tick` (new) | a logging-handler error does not propagate out of `run_tick`/`run_loop`. |
| Supervisor install (dry-run) | `test_install_task_dry_run_renders_command` (new) | `install_dispatcher_daemon_task.ps1 -DryRun` prints `WOULD REGISTER TaskName=GTKB-DispatcherDaemon ...` invoking `ensure_dispatcher_daemon.py` and makes no Task Scheduler call. |

Commands (pre-report): targeted `pytest` over `test_dispatcher_daemon_supervision.py` via the repo venv; `ruff check` AND `ruff format --check` on the changed Python files; PowerShell `-DryRun` invocation of the installer for the render assertion. Daemon liveness is simulated deterministically via dependency-injection / monkeypatch of `daemon_process_alive` and the spawn function — no real background daemon or Task Scheduler mutation in the test path (test tasks, if registered at all, use a nonce-suffixed `-TaskName`).

## Risk / Rollback

- **Risk:** a supervisor that restarts too aggressively could mask a crash-looping daemon. Mitigated: this slice ONLY restarts a dead daemon (idempotent ensure); crash-loop detection + backoff is Phase-2 (WI-4790) self-healing scope, and the new persistent log makes a crash loop visible. The 1-minute interval bounds restart frequency.
- **Risk:** scheduled-task registration is host-mutating. Mitigated: install is idempotent (unregister-then-register), `-DryRun` is side-effect-free, tests never register the production task name, and an uninstall script is provided.
- **Isolation:** no change to dispatch decisions, the actionable-signature scheme, worker spawning, or harness identity (DELIB-20265888 isolation preserved — the supervisor only ensures the daemon process exists; it does not trigger or influence dispatch).
- **Rollback:** `uninstall_dispatcher_daemon_task.ps1` removes the task; reverting the commit removes the ensure script, the log wiring, and the installers. No KB mutation (`kb_mutation_in_scope: false`); append-only bridge history untouched.

## Recommended Commit Type

`feat` — adds new supervisor + observability capability (ensure-alive entrypoint, persistent daemon log, scheduled-task installers) plus tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
