NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: eb4f5b12-588a-43b5-bf6b-5439c7a97cf0
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report

# Implementation Report: WI-4855 dispatcher daemon process-lifecycle hardening

Document: gtkb-wi4855-daemon-process-lifecycle-hardening
Version: 005
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Responds to: bridge/gtkb-wi4855-daemon-process-lifecycle-hardening-004.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4855
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4855-DAEMON-LIFECYCLE-HARDENING
Recommended commit type: fix

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

## Summary

Implemented per the GO'd `-003` proposal (Cursor LO GO at `-004`). The three go-live process-lifecycle defects in the daemon control surface (`gt bridge dispatch daemon start|stop`, in `cli.py`) are fixed, backed by helpers in the daemon module:

1. **Stop terminates the process tree** (defect 1): `bridge_dispatch_daemon_stop_cmd` reads the authoritative `daemon.pid`, terminates the process tree via `bridge_dispatch_reset.terminate_pid_tree`, clears the pid file, then releases the lock.
2. **Single-instance via process-liveness** (defect 2): `bridge_dispatch_daemon_start_cmd` refuses to spawn when the lock is held OR a live-but-lockless daemon is detected via the new `daemon_process_alive()` helper (reads `daemon.pid` + tasklist / `os.kill(0)` liveness probe).
3. **True detach** (defect 3): `start` spawns the daemon with platform detach flags (`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP` on Windows; `start_new_session=True` on POSIX) so it survives its launching shell / scheduled task. The daemon's `run_loop` writes/cleans `daemon.pid`.

Tick / shadow / health / watchdog logic is unchanged.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — report filed as the next append-only numbered bridge file (NEW post-implementation report) for verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: specs carried forward from `-003`; tests mapped to defects.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: WI-4855 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: each defect maps to an executed derived test (mapping below).
- `ADR-DISPATCHER-ARCHITECTURE-001` — daemon process-lifecycle correctness (one live instance, clean stop, durable detach) is required for the daemon to be the reliable live dispatch substrate.
- `GOV-STANDING-BACKLOG-001` — WI-4855 is an authorized standing-backlog item under the active project.

## Spec-to-Test Mapping

| Spec / clause | Test (new) | Result |
|---|---|---|
| `ADR-DISPATCHER-ARCHITECTURE-001` clean-stop + defect (1) | `test_daemon_stop_terminates_process_tree` | PASS: real throwaway child recorded in `daemon.pid` is terminated by `stop`; pid file cleared; lock released. |
| defect (2) single-instance | `test_daemon_start_refuses_when_live_instance_present` | PASS: with the live test-process pid in `daemon.pid` and no lock file, the real liveness probe detects it and `start` refuses (no Started output, non-zero exit). |
| defect (3) true detach | `test_daemon_start_spawns_detached` | PASS: `start` invokes Popen with platform detach flags; on Windows asserts `DETACHED_PROCESS` + `CREATE_NEW_PROCESS_GROUP`. |
| Non-regression | existing `test_gtkb_dispatcher_daemon.py` suite (16 tests) | PASS: run/tick/status/shadow/health/watchdog unchanged. |

The three tests exercise the production CLI commands (`gt bridge dispatch daemon start|stop`) via `CliRunner` (the exposed control surface in `cli.py`) per GOV-10/GOV-19 outside-in testing, rather than internal helpers.

## Executed Commands

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
# 19 passed in 3.31s  (16 non-regression + 3 new WI-4855 tests)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check (cli.py, gtkb_dispatcher_daemon.py, test_gtkb_dispatcher_daemon.py)
# daemon + test file: clean. cli.py: 2 E501 reported at L6165 + L6601 (ChromaDB semantic-only message and sibling): PRE-EXISTING in HEAD (confirmed via git show HEAD ... cli.py piped to ruff check stdin), NOT within the WI-4855 hunks (L877-938). The WI-4855 hunks introduce zero ruff errors.

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check (same 3 files)
# 3 files already formatted

## Commit Scope / Finalization Guidance

`cli.py` carries two unrelated uncommitted clusters co-mingled with the WI-4855 start/stop lifecycle hunks: WI-4727 `--description-file` (separate GO) and the `dispatcher_daemon` `--substrate` Choice addition (X1 / PHASE-Y enablement). To keep this commit scoped to WI-4855, the implementation is committed hunk-scoped: only the WI-4855 `cli.py` start/stop hunks plus `scripts/gtkb_dispatcher_daemon.py` (clean: daemon helpers only), the test file, and this report are staged; the WI-4727 and substrate hunks are left unstaged.

Verifier finalization note: because `cli.py` still carries the unrelated dirty clusters, the VERIFIED finalize must NOT include `groundtruth-kb/src/groundtruth_kb/cli.py` in its include set (the verdict helper stages whole files and would fold the unrelated clusters into the VERIFIED commit). The WI-4855 `cli.py` hunks are already committed with this report. Finalize with the include set scripts/gtkb_dispatcher_daemon.py plus platform_tests/scripts/test_gtkb_dispatcher_daemon.py (both clean after this commit, so they stage as no-ops); the VERIFIED commit then contains only the verdict file.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is daemon process-lifecycle correctness (one live instance; stop terminates; start detaches durably) per `ADR-DISPATCHER-ARCHITECTURE-001` and the WI-4787 daemon-foundation contract. No new requirement; this corrects the implementation to meet existing requirements go-live showed were unmet.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4855-DAEMON-LIFECYCLE-HARDENING` (includes WI-4855 + `ADR-DISPATCHER-ARCHITECTURE-001`, cites `DELIB-20266201`). The owner scoped WI-4855 as X2 of the full daemon fix-chain in the S20260626 grill (`DELIB-20266203`). Source-only defect fix; no formal-artifact / narrative mutation, so no separate artifact-approval packet is required.

## Prior Deliberations

- `DELIB-20266203` — Owner clarification (S20260626): autonomous dispatcher-daemon PB/LO loop plan; WI-4855 is X2 (full daemon fix-chain).
- `DELIB-20266201` — Owner authorization for WI-4855 (the minted PAUTH's owner-decision evidence).
- `DELIB-20266084` — WI-4787 daemon foundation; this hardens the process lifecycle that foundation introduced.
- bridge/gtkb-wi4855-daemon-process-lifecycle-hardening-002.md (NO-GO, control-surface scope correction), -003 (REVISED), and -004 (GO).

## Recommended Commit Type

`fix` — repairs broken daemon process-lifecycle behavior (orphan-on-stop, concurrent double-instance, premature death with the launcher). No new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
