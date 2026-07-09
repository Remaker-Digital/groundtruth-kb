REVISED

# gtkb-wi4855-daemon-process-lifecycle-hardening — Dispatcher daemon process-lifecycle hardening (REVISED: corrected control-surface scope per NO-GO -002)

bridge_kind: prime_proposal
Document: gtkb-wi4855-daemon-process-lifecycle-hardening
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-26 UTC

author_identity: claude
author_harness_id: B
author_session_context_id: b3b723c1-9a52-424c-94f3-70c609bd1588
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4855-DAEMON-LIFECYCLE-HARDENING
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4855

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Response to NO-GO -002

LO NO-GO -002 (Cursor harness E) correctly found that the daemon `start`/`stop` control surface lives in `groundtruth-kb/src/groundtruth_kb/cli.py` (`bridge_dispatch_daemon_start_cmd` / `bridge_dispatch_daemon_stop_cmd`, ~L873-917), NOT in `scripts/gtkb_dispatcher_daemon.py` (whose `main()` exposes only `run`/`tick`/`status`). The defect analysis was accepted; only the scope was wrong. This REVISED corrects `target_paths` to include `cli.py` and adds an explicit defect-to-file mapping (below). The implementation-precondition gate (finalize the dispatcher pile-up) is retained and now names the specific `cli.py` tangle.

## Summary

Go-live testing of the dispatcher daemon surfaced three process-lifecycle defects in the daemon control surface (`gt bridge dispatch daemon start|stop`, implemented in `cli.py`):

1. **Stop does not terminate the process.** `bridge_dispatch_daemon_stop_cmd` reads the lock-JSON PID and sends `SIGTERM`, then releases the lock — it does not use the `daemon.pid` file or process-tree termination, so the daemon (and any children) can survive, orphaned.
2. **Start has no real single-instance enforcement.** `bridge_dispatch_daemon_start_cmd` gates only on `read_daemon_status().running` (lock-based); a live-but-lockless daemon is not detected, so a second daemon launches concurrently (two ran during go-live; dedup masked the double-dispatch).
3. **Start does not truly detach.** Start uses a plain `subprocess.Popen` with no detach flags, so the daemon dies when its launching shell / scheduled task ends.

The fix hardens the lifecycle across `cli.py` (the control surface) backed by new helpers in `gtkb_dispatcher_daemon.py` (the daemon module): `stop` terminates the daemon process tree (via the `daemon.pid` file) then clears the lock; `start` checks process liveness (PID + probe) in addition to the lock and refuses a second instance; `start` spawns the daemon fully detached (platform-appropriate flags) and records its PID. Tick/shadow/health/watchdog logic is unchanged.

## Defect-to-File Mapping

| Defect | Primary fix (cli.py) | Supporting helper (gtkb_dispatcher_daemon.py) |
|---|---|---|
| (1) stop terminates process | `bridge_dispatch_daemon_stop_cmd`: read `daemon.pid`, terminate the process tree, then release the lock (replaces lock-PID `SIGTERM`-then-release) | `terminate_daemon_process_tree(pid)` (or reuse `bridge_dispatch_reset.terminate_pid_tree`); read/clear `daemon.pid` |
| (2) single-instance via liveness | `bridge_dispatch_daemon_start_cmd`: before spawn, check process liveness in addition to the lock; refuse if a live daemon is found | `daemon_process_alive()` — read `daemon.pid` + liveness probe (PID exists + heartbeat fresh) |
| (3) true detach | `bridge_dispatch_daemon_start_cmd`: spawn with detached flags (Windows new-process-group + detached-process); write `daemon.pid` | PID-file write helper invoked by the daemon on startup |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next append-only numbered bridge file (REVISED after NO-GO -002).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: cites governing specs; tests mapped to defects.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: WI-4855 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: each defect maps to a derived test below.
- `ADR-DISPATCHER-ARCHITECTURE-001` — the daemon is the GT-KB-owned dispatch service; correct process lifecycle (one live instance, clean stop, durable detach) is required for it to be the reliable live dispatch substrate.
- `GOV-STANDING-BACKLOG-001` — WI-4855 is an authorized standing-backlog item under the active project.

## Prior Deliberations

- `DELIB-20266203` — Owner clarification (S20260626): the autonomous dispatcher-daemon PB/LO loop plan; WI-4855 is X2 of that plan (full daemon fix-chain).
- `DELIB-20266201` — Owner authorization for WI-4855 (the minted PAUTH's owner-decision evidence).
- `DELIB-20266084` — WI-4787 daemon foundation; this hardens the process lifecycle that foundation introduced.
- `DELIB-20265888` — harness/dispatch isolation directive; true detach keeps the daemon a standalone process, serving isolation.
- NO-GO `bridge/gtkb-wi4855-daemon-process-lifecycle-hardening-002.md` — the control-surface scope correction this REVISED addresses.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4855-DAEMON-LIFECYCLE-HARDENING` (includes WI-4855 + ADR-DISPATCHER-ARCHITECTURE-001, cites `DELIB-20266201`). The owner directed the §B daemon-activation resume and, in the S20260626 grill (`DELIB-20266203`), scoped WI-4855 as X2 of the full daemon fix-chain. Source-only defect fix; no formal-artifact/narrative mutation, so no separate artifact-approval packet is required.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is daemon process-lifecycle correctness (one live instance; stop terminates; start detaches durably) per `ADR-DISPATCHER-ARCHITECTURE-001` and the WI-4787 daemon-foundation contract. No new requirement; this corrects the implementation to meet existing requirements that go-live showed are unmet.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| `ADR-DISPATCHER-ARCHITECTURE-001` clean-stop + defect (1) | `test_daemon_stop_terminates_process_tree` (new) | after `daemon stop`, the recorded `daemon.pid` process (and tree) is not alive AND the lock is released. |
| defect (2) single-instance | `test_daemon_start_refuses_when_live_instance_present` (new) | with a live (lock-cleared) daemon process present, a second `daemon start` is refused via liveness detection; no second process spawns. |
| defect (3) true detach | `test_daemon_start_spawns_detached` (new) | `daemon start` spawns with detached flags and writes `daemon.pid`; the child survives parent termination (Windows-deterministic). |
| Non-regression | existing `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` suite | PASS — run/tick/status/shadow/health/watchdog unchanged. |

Commands (pre-report): targeted `pytest` over the daemon suite + the new lifecycle tests via the repo venv; `ruff check` AND `ruff format --check` on changed Python files. Windows detach/terminate semantics exercised deterministically; no POSIX-only signal dependence.

## Risk / Rollback

- **Implementation precondition (dispatcher pile-up — now names cli.py):** `cli.py` currently carries an uncommitted, unrelated `--description-file` backlog-tooling change co-mingled with the dispatcher-daemon substrate-choice change (the X1 finding). Because this REVISED scopes WI-4855 into `cli.py`, that tangle MUST be resolved (the unrelated change committed by its owner or set aside) so the WI-4855 implementation commit touches only the daemon start/stop lifecycle. `scripts/gtkb_dispatcher_daemon.py` is now committed clean (X1, commit 4e2f36119), so it is a clean base. Implementation is gated on a clean `cli.py` base.
- **Risk:** platform-sensitive process semantics (Windows detach/terminate) in a CLI command path. Mitigation: surgical scope (start/stop command bodies + daemon-module lifecycle helpers only); Windows-deterministic tests; no change to dispatch decision logic.
- **Rollback:** single-commit revert restores prior lifecycle behavior. No KB mutation (`kb_mutation_in_scope: false`); append-only bridge history untouched.

## Bridge Filing

Filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4855-daemon-process-lifecycle-hardening` (REVISED -003); no prior version rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs broken daemon process-lifecycle behavior (orphan-on-stop, concurrent double-instance, premature death with the launcher). No new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
