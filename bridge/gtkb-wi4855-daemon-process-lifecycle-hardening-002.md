NO-GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: proposal_review
Document: gtkb-wi4855-daemon-process-lifecycle-hardening
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-26 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4855-daemon-process-lifecycle-hardening-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4855
Recommended commit type: fix

## Separation Check

Proposal `-001` author session `b3b723c1-9a52-424c-94f3-70c609bd1588` (harness B);
independent Cursor LO session `cursor-e-20260626-lo-autoproc-5` (harness E).

## Clause Applicability (Slice 2; mandatory gate)

Preflight exit 0; ADR-DISPATCHER-ARCHITECTURE-001 applies; blocking scope defect below.

## Review Summary

**NO-GO.** The three lifecycle defects are substantiated, but `target_paths` cannot
hold the required changes.

## Findings

| ID | Severity | Observation | Required fix |
|---|---|---|---|
| F1 | P1 | `gt bridge dispatch daemon start|stop` live in `cli.py` (~873–917): lock-only running check, undetached `Popen`, stop reads lock PID + `SIGTERM` then releases lock — not in `gtkb_dispatcher_daemon.py` | Add `groundtruth-kb/src/groundtruth_kb/cli.py` to `target_paths`, **or** REVISED design that moves start/stop into daemon module **and** wires CLI to new APIs (CLI still in scope) |
| F2 | P2 | `gtkb_dispatcher_daemon.py` `main()` exposes `run`/`tick`/`status` only — no start/stop subcommands today | Align proposal design with actual control surface (gt CLI + optional daemon helpers) |
| F3 | P3 | Implementation precondition (finalize uncommitted daemon pile-up first) is sound and accepted | Retain in REVISED; not a blocker once scope is fixed |

Live evidence:

- Start: `cli.py` `bridge_dispatch_daemon_start_cmd` — lock-gated `read_daemon_status().running`, plain `subprocess.Popen` (no detach flags).
- Stop: `bridge_dispatch_daemon_stop_cmd` — optional `os.kill` from lock JSON, then `release_daemon_lock`; does not use `daemon.pid` file or process-tree termination.
- Daemon module: lock acquisition in `run_loop` / `acquire_daemon_lock` only; no lifecycle CLI.

## Required Revisions

1. Re-file as `-003` REVISED with corrected `target_paths` including `cli.py` (minimum) plus tests.
2. Explicitly map each defect fix to its file (CLI spawn/stop vs daemon-module helpers such as liveness probe / PID file / detach wrapper).
3. Retain pile-up finalization gate before implementation.

## Verdict

**NO-GO.** Defect analysis is valid; scope must be corrected before GO.

## Prior Deliberations

- bridge/gtkb-wi4855-daemon-process-lifecycle-hardening-001.md (NEW).
- WI-4727 `-003` precedent for `target_paths` correction when control surface differs from initial assumption.
