NEW

# gtkb-wi4896-daemon-loop-console-residual - Start daemon loop with GUI-subsystem Python

bridge_kind: prime_proposal
Document: gtkb-wi4896-daemon-loop-console-residual
Version: 001
Author: Prime Builder Codex
Date: 2026-06-27T22:55:00Z

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f09c3-be81-7771-8200-e81c58e3ae1e
author_model: GPT-5
author_model_version: 2026-06-27
author_model_configuration: Codex desktop; danger-full-access; approval-policy never; interactive role Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4882
Related Work Item: WI-4896

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "scripts/ensure_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py"]

implementation_scope: source,test,runtime-launcher-hardening
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

While verifying `gtkb-wi4896-ollama-readiness-console-residual`, a live dispatcher tick reproduced one more Windows console path. The tick correctly shifted Prime Builder dispatch to none after the implementation report was filed, but shortly afterward a live daemon loop appeared as:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\gtkb_dispatcher_daemon.py --loop --project-root . --tick-seconds 30
```

At the same local timestamp, Windows created `WindowsTerminal.exe -Embedding` and `OpenConsole.exe -Embedding`. Stopping the dispatcher daemon through `gt bridge dispatch daemon stop` terminated the daemon loop, the worker tree, and the Terminal/OpenConsole pair. This isolates a remaining launcher gap: daemon start/supervision paths still invoke `sys.executable`, which can be console-subsystem `python.exe`, even though daemon/background execution on Windows must use a GUI-subsystem interpreter when available.

This proposal fixes only that start-loop gap. It does not change dispatcher topology, role eligibility, ranking, credentials, bridge selection, worker prompts, scheduled-task definitions, or database schema.

## Defect Evidence

- Live daemon tick launched one Loyal Opposition worker for `gtkb-wi4896-ollama-readiness-console-residual` and reported Prime Builder `would_dispatch: []`.
- Immediately afterward, a daemon loop process was observed with command line `python.exe scripts\gtkb_dispatcher_daemon.py --loop --project-root . --tick-seconds 30`.
- `WindowsTerminal.exe -Embedding` and `OpenConsole.exe -Embedding` appeared at the same creation timestamp as that daemon loop.
- The daemon loop's child OpenRouter worker chain used `pythonw.exe`, proving the worker-chain fix is active; the residual console host was attached to the daemon-loop starter, not the worker wrapper.
- `gt bridge dispatch daemon stop` stopped the daemon loop PID and its child worker tree; a follow-up process scan found no daemon, worker, Terminal, or OpenConsole process from the reproduced path.

## Specification Links

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Requires Windows dispatcher/background paths to run non-interactively without visible console windows; daemon loop start must use GUI-subsystem Python where available.
- `ADR-DISPATCHER-ARCHITECTURE-001` - The dispatcher daemon is the active black-box dispatch substrate; its own loop process is daemon-owned background behavior and must not surface UI.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - The centralized dispatch service must execute without stealing owner focus or allocating interactive console windows.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The fix remains in-root and uses the existing in-root virtualenv interpreter sibling `pythonw.exe`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected `groundtruth-kb/src/`, `scripts/`, and `platform_tests/` edits require bridge proposal, LO GO, implementation claim, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites governing requirements for the source/test changes.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This proposal carries Project Authorization, Project, Work Item, and concrete target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The implementation report must map the launcher behavior to exact tests and runtime verification.
- `GOV-STANDING-BACKLOG-001` - WI-4896 is the active owner-reported dispatcher console/focus-steal regression item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The newly reproduced residual is preserved as a durable bridge artifact rather than remaining only in chat.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The proposal links runtime symptom, source path, tests, and verification as one traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The live reproduction triggers a follow-up bridge artifact because the previous VERIFIED startup fix did not cover the CLI daemon-start launcher.

## Prior Deliberations

- `DELIB-20266297` - Owner authorization for WI-4896 dispatcher console-window suppression.
- `DELIB-20266276` - Daemon resilience scope-lock and program authorization source for `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION`.
- `bridge/gtkb-wi4896-startup-console-residual-003.md` - Prior proposal that fixed doctor, watchdog restart, storm-watchdog launcher, and DB snapshot surfaces.
- `bridge/gtkb-wi4896-startup-console-residual-006.md` - VERIFIED verdict for that prior startup-console residual; this proposal is a new residual discovered after verification.
- `bridge/gtkb-wi4896-ollama-readiness-console-residual-003.md` - Current post-implementation report for readiness probe and worker Python-chain fixes; the live verification of that report exposed this separate daemon-loop starter gap.

## Owner Decisions / Input

No new owner decision is required. Mike already authorized the dispatcher console-window suppression scope and identified the governing program authorization as `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION`. This proposal remains within that PAUTH and narrows to the newly observed daemon-loop starter path.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, and `ADR-ISOLATION-APPLICATION-PLACEMENT-001` already require headless, non-interactive, in-root daemon/background execution. No new or revised requirement is needed before implementation.

## Proposed Scope

- In `groundtruth-kb/src/groundtruth_kb/cli.py`, make `gt bridge dispatch daemon start` prefer sibling `pythonw.exe` over `python.exe` on Windows when spawning the detached daemon loop, while preserving `DETACHED_PROCESS`, `CREATE_NEW_PROCESS_GROUP`, `CREATE_NO_WINDOW`, null stdio, cwd, interval, and refusal when already running.
- In `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, extend daemon-start coverage so Windows start uses `pythonw.exe` when a sibling exists and falls back to the original executable when it does not.
- In `scripts/ensure_dispatcher_daemon.py`, make `_spawn_detached_daemon` apply the same Windows `python.exe` to sibling `pythonw.exe` preference before starting the daemon loop. This protects manual/supervisor invocations that do not themselves arrive through the scheduled task's `pythonw.exe`.
- In `platform_tests/scripts/test_dispatcher_daemon_supervision.py`, extend supervisor spawn coverage for `pythonw.exe` preference and fallback behavior while preserving existing no-window/detach assertions.

## Out Of Scope

- Reworking the daemon loop, dispatch selection, worker prompts, worker lifetime, bridge claiming, or provider routing.
- Editing `scripts/cross_harness_bridge_trigger.py`, `scripts/run_with_status.py`, or `scripts/verify_ollama_dispatch.py`; those are covered by `gtkb-wi4896-ollama-readiness-console-residual`.
- Editing scheduled task registration or enabling/disabling task state.
- Credential, deployment, or database-schema changes.

## Spec-Derived Verification Plan

| Spec / governing surface | Verification |
| --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Unit tests assert daemon start/supervision use sibling `pythonw.exe` on Windows and preserve no-window flags/null stdio. Runtime process scan after controlled start confirms no `WindowsTerminal.exe`/`OpenConsole.exe` spawned by the daemon-loop path. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Focused daemon tests prove `gt bridge dispatch daemon start` still spawns the same daemon loop arguments, cwd, and interval with only the interpreter subsystem changed. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused supervision tests prove the service starter remains non-interactive and idempotent. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Tests use in-root virtualenv-style sibling interpreter paths and do not introduce external launchers. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation starts only after LO GO and implementation authorization validate the four target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report will include exact focused pytest, ruff, daemon start/stop, and process-scan evidence. |

Expected focused verification commands:

```text
.\groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\cli.py scripts\ensure_dispatcher_daemon.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_dispatcher_daemon_supervision.py
.\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\cli.py scripts\ensure_dispatcher_daemon.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_dispatcher_daemon_supervision.py
.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_dispatcher_daemon_supervision.py -q --tb=short
gt bridge dispatch daemon start
gt bridge dispatch daemon stop
```

## Acceptance Criteria

- `gt bridge dispatch daemon start` uses sibling `pythonw.exe` on Windows when available.
- `scripts/ensure_dispatcher_daemon.py` uses sibling `pythonw.exe` on Windows when available.
- Both launcher paths fall back to the original executable when no sibling `pythonw.exe` exists.
- Existing detach/no-window/null-stdio semantics remain intact.
- A controlled daemon start/stop no longer creates a new WindowsTerminal/OpenConsole process.
- No topology, selection, credential, deployment, DB schema, or scheduled-task definition changes occur.

## Risk / Rollback

Risk is low and isolated to Windows daemon-loop process launch. The rollback is a single scoped revert of the four target files, followed by keeping `GTKB-DispatcherDaemon` disabled and using manual dry-run ticks until a replacement no-console launcher strategy is approved.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4896-daemon-loop-console-residual`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix:

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
