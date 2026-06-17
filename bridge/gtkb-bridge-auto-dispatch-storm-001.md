NEW

# gtkb-bridge-auto-dispatch-storm — Implement auto-dispatch rate guard and robust process-liveness check

bridge_kind: implementation_proposal
Document: gtkb-bridge-auto-dispatch-storm
Version: 001
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-17 UTC

author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: 68a85c45-4776-4341-b646-3664fc66f02d
author_model: Gemini 3.5 Flash
author_model_version: Gemini 3.5 Flash (High)
author_model_configuration: Antigravity CLI interface, Prime Builder mode

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4569

target_paths: ["scripts/cross_harness_bridge_trigger.py"]

implementation_scope: bridge-dispatch
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal resolves a defect (WI-4569) where the cross-harness bridge trigger can spawn multiple duplicate workers, leading to process storms (up to 30+ concurrent processes) and hook execution hangs. This happens due to three primary gaps:
1. **Bypassed Concurrency Cap:** The Windows process-liveness check (`_pid_alive`) in `scripts/cross_harness_bridge_trigger.py` fails closed (returning `False`) when execution occurs inside a restricted/sandboxed harness python runner (due to ctypes `OpenProcess` failure). This results in `live_count` always reporting `0`, completely bypassing the global concurrency cap of `8`.
2. **Missing Rate Guard:** The trigger hook fires on every tool call. If a worker is spawned but is still cold/bootstrapping (taking 10-25 seconds), subsequent tool calls see the bridge thread as still unclaimed and immediately spawn another duplicate worker.
3. **Hook Execution Hangs on Stdin:** In the Antigravity harness environment, the `PostToolUse` trigger hook executes `cross_harness_bridge_trigger.py` with standard input redirected but kept open without sending EOF. Because `_read_hook_context_from_stdin` only checks `sys.stdin.isatty()` (which is `False` in redirected environments), it calls `sys.stdin.read()`, which blocks indefinitely. This causes hook execution to time out (10s), leading to spontaneous harness cancellations of the active agent session.

We will resolve these issues by:
* Adding `os.kill(pid, 0)` fallback liveness checking on Windows when `OpenProcess` fails, correctly recognizing alive sandboxed processes.
* Introducing a global 10-second rate guard on child process spawning by scanning the modification times (`mtime`) of `.pid` files in the runs directory.
* Implementing a non-blocking `_has_stdin_data()` check using Windows `PeekNamedPipe` and POSIX `select.select` in `_read_hook_context_from_stdin()` to prevent blocking on empty, redirected stdin.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — TAFE-backed bridge state and status-bearing numbered files are canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Linked specifications are required for bridge approval.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project and WI linkage metadata must be specified.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Proposal must specify a spec-derived verification plan.
- `GOV-STANDING-BACKLOG-001` — Backlog items are the cross-session work authority.

## Prior Deliberations

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` — Owner authorized all unimplemented WIs in the May29 Hygiene project.

## Owner Decisions / Input

- Authorized by owner in deliberation `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` during S445.

## Requirement Sufficiency

- Existing requirements sufficient — Resolving a bug/defect in the implementation of work-intent trigger dispatching.

## Spec-Derived Verification Plan

We will add unit test cases to verify the concurrency cap and rate guard:
* Execute:
  ```text
  groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --no-header -p no:cacheprovider
  ```
* Expected: All tests pass, including new assertions verifying that (1) `_pid_alive` correctly identifies sandboxed processes as alive, and (2) spawning is suppressed if another worker was launched globally within 10 seconds.

## Risk / Rollback

- **Risk:** Low. The change is isolated to trigger-filtering and liveness check logic.
- **Rollback:** Single-commit revert of `scripts/cross_harness_bridge_trigger.py`.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-bridge-auto-dispatch-storm`; no prior version is deleted or rewritten (append-only).

## Recommended Commit Type

Recommended commit type: `fix: implement global launch rate guard and robust sandboxed process liveness checking for bridge trigger`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
