NEW

# gtkb-wi4855-daemon-process-lifecycle-hardening — Dispatcher daemon process-lifecycle hardening: terminate-on-stop, single-instance via process-liveness, true detach

bridge_kind: prime_proposal
Document: gtkb-wi4855-daemon-process-lifecycle-hardening
Version: 001
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

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Go-live testing of the dispatcher daemon (WI-4787 foundation / WI-4790 monitoring / WI-4848 cutover) surfaced three process-lifecycle defects in `scripts/gtkb_dispatcher_daemon.py`:

1. **Stop does not terminate the process.** `daemon stop` releases the single-instance lock but leaves the daemon process running, orphaning it.
2. **Start has no real single-instance enforcement.** `daemon start` gates only on the lock file, so a live-but-lockless daemon is not detected and a second daemon launches concurrently. During go-live two daemons ran at once; signature dedup masked the resulting double-dispatch.
3. **Start does not truly detach.** The spawned daemon dies when its launching shell / scheduled task ends, so it cannot survive as a background service.

This proposal hardens the daemon's process lifecycle: `stop` terminates the daemon process tree and then clears the lock; `start` enforces single-instance by checking process liveness (recorded PID + a liveness probe) in addition to the lock, refusing to spawn a second daemon when one is already alive; and `start` spawns the daemon as a fully-detached process (platform-appropriate detach) that survives its launcher. Scope is confined to the daemon's lifecycle surface (start / stop / detach / single-instance / PID handling); tick, shadow-decision, health, and dispatch logic are unchanged. This is WI-4790/WI-4848 daemon follow-on and a prerequisite for the §B go-live resume.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal is filed as the next status-bearing numbered bridge file in the append-only chain and is reviewed before any implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: this proposal cites every governing spec and maps proposed tests to them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: WI-4855 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH linkage present in metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: each defect clause (terminate-on-stop, single-instance-via-liveness, true-detach) maps to a derived test in the verification plan.
- `ADR-DISPATCHER-ARCHITECTURE-001` — the daemon is the GT-KB-owned dispatch service; a correct process lifecycle (exactly one live instance, clean termination on stop, durable detach independent of any launching session) is required for the daemon to be the reliable live dispatch substrate. WI-4855 aligns the implementation to that decision.
- `GOV-STANDING-BACKLOG-001` — WI-4855 is an authorized standing-backlog work item under the active project.

## Prior Deliberations

- `DELIB-20266201` — Owner authorization (this session, S20260626): owner AUQ decisions authorizing WI-4855 under PROJECT-GTKB-DISPATCHER-RELIABILITY (the owner-decision evidence for the minted authorization envelope cited above).
- `DELIB-20266084` — Owner authorization for the WI-4787 dispatcher daemon foundation (Phase 2): persistent process + control CLI + independence. This proposal hardens the process lifecycle that foundation introduced (the go-live test exposed the gaps).
- `DELIB-20265888` — Owner directive: harness/dispatch isolation — dispatch is triggered by artifact deposit + ownership-release, not by harness/session state. True detach (defect 3) keeps the daemon a standalone process rather than a shell/session-bound one, directly serving this isolation directive.
- `DELIB-20266166` — Owner decision: the WI-4804 scope split, routing dormancy auto-restart into the daemon program (now the sibling watchdog work). This proposal is the parallel daemon-process-reliability follow-on; both ensure the daemon program stays alive and singular.
- `DELIB-20266176`, `DELIB-20266096` — WI-4790 verification deliberations for the health-response / monitoring framework the daemon hosts; this proposal ensures the process hosting that framework is single and durable.

## Owner Decisions / Input

This work is implementation-authorized under the active project authorization `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4855-DAEMON-LIFECYCLE-HARDENING` (minted this session under PROJECT-GTKB-DISPATCHER-RELIABILITY, including WI-4855 + spec ADR-DISPATCHER-ARCHITECTURE-001, citing owner-decision `DELIB-20266201`). The owner directed the §B daemon-activation resume (2026-06-26) and made three AskUserQuestion decisions this session — "Proceed to §B (WI-4855)", "Proceed WI-4855 proposal now", and "Mint authorization + file" — captured as `DELIB-20266201`. This is a source-only defect fix; it makes no formal-artifact or narrative-artifact mutation, so no separate artifact-approval packet is required. The project authorization plus DELIB-20266201 are the governing owner-decision evidence.

## Requirement Sufficiency

Existing requirements sufficient. The governing work item is a defined defect; the governing requirement is daemon process-lifecycle correctness — exactly one live instance, stop terminates the process, start detaches durably — per `ADR-DISPATCHER-ARCHITECTURE-001` and the WI-4787 daemon-foundation contract (`DELIB-20266084`). No new or revised requirement is needed; this proposal corrects the implementation to meet the existing daemon-foundation requirements that go-live showed are unmet.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| `ADR-DISPATCHER-ARCHITECTURE-001` clean-stop + defect (1) | `test_daemon_stop_terminates_process` (new) | after `daemon stop`, the recorded daemon PID is no longer alive AND the single-instance lock is released. |
| defect (2) single-instance | `test_daemon_start_refuses_when_live_instance_present` (new) | with a live (but lock-cleared) daemon process present, a second `daemon start` is refused via process-liveness detection; no second process is spawned. |
| defect (3) true detach | `test_daemon_start_detaches_from_launcher` (new) | the spawned daemon survives termination of its launching parent process (platform-appropriate detached spawn). |
| Non-regression | existing `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` suite | PASS — tick, shadow-decision, health, and watchdog behavior unchanged by the lifecycle hardening. |

Commands (pre-report):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --no-header
```

plus `ruff check` AND `ruff format --check` on changed Python files. Windows detach/terminate semantics (e.g. `CREATE_NEW_PROCESS_GROUP` / detached spawn for start; process-tree termination for stop) must be exercised deterministically on the host platform; tests must not depend on POSIX-only signals.

## Risk / Rollback

- **Implementation precondition (dispatcher finalization pile-up):** `scripts/gtkb_dispatcher_daemon.py` currently carries uncommitted VERIFIED watchdog-dormancy work (plus shadow-parity changes) — the dispatcher finalization pile-up. This proposal edits the same file. That pile-up MUST be finalized (committed to a clean daemon base) BEFORE implementation; otherwise the implementation commit would entangle the uncommitted changes. This proposal is filed for review now; implementation is explicitly gated on that finalization. Owner sequenced this 2026-06-26 ("proceed with the proposal now; drain the pile-up before implementation") via AskUserQuestion.
- **Risk:** process-lifecycle changes are platform-sensitive (Windows detach/terminate semantics) and touch a hot multi-work-item file. Mitigation: surgical scope (lifecycle functions only — start/stop/detach/single-instance/PID); Windows-deterministic tests; no change to tick/shadow/dispatch decision logic.
- **Rollback:** single-commit revert restores the prior lifecycle behavior (orphan-on-stop, lock-only single-instance, shell-bound process). No KB mutation (`kb_mutation_in_scope: false`); append-only bridge history is untouched.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4855-daemon-process-lifecycle-hardening`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs broken daemon process-lifecycle behavior (orphan-on-stop, concurrent double-instance, premature death with the launcher). No new capability surface; the daemon's dispatch behavior is unchanged.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
