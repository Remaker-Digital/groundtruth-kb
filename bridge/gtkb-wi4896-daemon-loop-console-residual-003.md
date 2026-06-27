NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c3-be81-7771-8200-e81c58e3ae1e
author_model: GPT-5
author_model_version: 2026-06-27
author_model_configuration: Codex desktop interactive Prime Builder

# GT-KB Bridge Implementation Report - gtkb-wi4896-daemon-loop-console-residual - 003

bridge_kind: implementation_report
Document: gtkb-wi4896-daemon-loop-console-residual
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4896-daemon-loop-console-residual-002.md
Approved proposal: bridge/gtkb-wi4896-daemon-loop-console-residual-001.md
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Work Item: WI-4896
Recommended commit type: fix:

## Implementation Claim

Implemented the approved daemon-loop console residual fix. Windows daemon-loop launch paths now prefer the sibling GUI-subsystem interpreter `pythonw.exe` whenever the launching interpreter is `python.exe` and the sibling exists, while preserving the existing fallback to `python.exe` when `pythonw.exe` is unavailable.

The change covers both daemon-loop start surfaces approved by the GO:

- `gt bridge dispatch daemon start` in `groundtruth-kb/src/groundtruth_kb/cli.py`
- scheduled-task supervisor respawn in `scripts/ensure_dispatcher_daemon.py`

The existing null-stdio, detached-process, new-process-group, and no-window process flags remain intact. The dispatcher substrate is intentionally left at `none` as a safety brake pending Loyal Opposition verification; no scheduled tasks were re-enabled by this implementation.

## Specification Links

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Requires Windows dispatcher/background paths to run non-interactively without visible console windows.
- `ADR-DISPATCHER-ARCHITECTURE-001` - The daemon loop is dispatcher-owned background behavior and must not surface interactive UI.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - Centralized dispatch must execute without stealing owner focus or allocating interactive console windows.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The fix remains in-root and uses the existing in-root virtualenv interpreter sibling `pythonw.exe`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected source, script, and test edits require bridge GO, implementation claim, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This report maps the approved proposal to concrete implementation and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This work remains under the cited project authorization and WI-4896 residual thread.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification evidence below maps tests and runtime checks to the linked requirements.
- `GOV-STANDING-BACKLOG-001` - WI-4896 remains the active owner-reported dispatcher console/focus-steal regression item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The reproduced residual is preserved as a durable bridge artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The runtime symptom, source paths, tests, and report remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The live residual triggered this follow-up bridge artifact after the previous startup/readiness fixes.

## Owner Decisions / Input

No new owner decision is required. This implementation is within the active daemon resilience project authorization and the LO `GO` verdict in `bridge/gtkb-wi4896-daemon-loop-console-residual-002.md`.

## Prior Deliberations

- `DELIB-20266297` - Owner authorization for WI-4896 dispatcher console-window suppression.
- `DELIB-20266276` - Daemon resilience scope-lock and scheduled-supervisor context.
- `bridge/gtkb-wi4896-startup-console-residual-006.md` - Previous startup residual verification.
- `bridge/gtkb-wi4896-ollama-readiness-console-residual-004.md` - Previous readiness/worker-chain residual verification.
- `bridge/gtkb-wi4896-daemon-loop-console-residual-001.md` - Approved implementation proposal.
- `bridge/gtkb-wi4896-daemon-loop-console-residual-002.md` - Loyal Opposition GO verdict authorizing this implementation.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli.py`
  - Added `_prefer_windows_gui_python`.
  - `bridge_dispatch_daemon_start_cmd` now launches `gtkb_dispatcher_daemon.py --loop` through `pythonw.exe` on Windows when available.
- `scripts/ensure_dispatcher_daemon.py`
  - Added the same Windows GUI-Python preference helper.
  - `_spawn_detached_daemon` now uses the helper before spawning the detached daemon loop.
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
  - Updated daemon-start coverage to expect `pythonw.exe` on Windows-capable installs.
  - Added explicit tests for pythonw preference and python.exe fallback.
  - Preserved pre-existing local watchdog-headless coverage already present in this file before this daemon-loop patch.
- `platform_tests/scripts/test_dispatcher_daemon_supervision.py`
  - Extended scheduled-supervisor spawn coverage to assert pythonw preference and python.exe fallback.
  - Preserved pre-existing local watchdog-launcher headless coverage already present in this file before this daemon-loop patch.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Unit tests assert both Windows daemon-loop launch paths choose sibling `pythonw.exe` when present and keep no-window/detach/null-stdio flags. Runtime start verified daemon command lines under `pythonw.exe` with no `WindowsTerminal.exe` or `OpenConsole.exe`. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Controlled `gt bridge dispatch daemon start --interval 120` ran the daemon in shadow mode under the dispatcher control surface; `gt bridge dispatch daemon stop` stopped it and released the lock. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Runtime process scan showed daemon loop running as `pythonw.exe scripts\gtkb_dispatcher_daemon.py --loop ...` and no visible terminal companion. One-minute observation after stop showed no respawn. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implementation targets are in-root under `E:/GT-KB` and use the existing virtualenv sibling `E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verified latest status was `GO`; acquired Prime Builder implementation claim for session `019f09c3-be81-7771-8200-e81c58e3ae1e`; `implementation_authorization.py begin` returned authorized target globs for the four changed files. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused ruff and pytest commands executed and passed; runtime process evidence recorded below. |

## Commands Run

- `.\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi4896-daemon-loop-console-residual --session-id 019f09c3-be81-7771-8200-e81c58e3ae1e --project-root E:\GT-KB`
- `.\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py --project-root E:\GT-KB begin --bridge-id gtkb-wi4896-daemon-loop-console-residual --session-id 019f09c3-be81-7771-8200-e81c58e3ae1e`
- `.\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py --project-root E:\GT-KB validate --target <each changed target>`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\cli.py scripts\ensure_dispatcher_daemon.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_dispatcher_daemon_supervision.py`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\cli.py scripts\ensure_dispatcher_daemon.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_dispatcher_daemon_supervision.py`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_dispatcher_daemon_supervision.py -q --tb=short --basetemp .gtkb-state\tmp\pytest-wi4896-daemon-loop-final`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch daemon start --interval 120`
- `Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'gtkb_dispatcher_daemon.py' -or $_.Name -match '^(WindowsTerminal|OpenConsole)\.exe$' } ...`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch daemon status --json`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch daemon stop`
- Two observation scans covering more than one 60-second recurrence interval with substrate `none`.

## Observed Results

- Bridge claim acquired as Prime Builder:
  - `claim_kind: go_implementation`
  - `implementation_deadline: 2026-06-27T23:47:50Z`
  - `ttl_expires_at: 2026-06-27T23:57:50Z`
- Implementation authorization passed:
  - latest status `GO`
  - GO file `bridge/gtkb-wi4896-daemon-loop-console-residual-002.md`
  - authorized target globs exactly matched the four changed files.
- Ruff:
  - `All checks passed!`
  - `4 files already formatted`
- Pytest:
  - `42 passed in 6.00s`
- Live daemon check:
  - start output: `Started shadow dispatcher daemon pid=4736`
  - process scan showed:
    - `ProcessId 4736`, `Name pythonw.exe`, command `E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe scripts\gtkb_dispatcher_daemon.py --loop --project-root . --tick-seconds 120`
    - `ProcessId 38780`, `Name pythonw.exe`, command `E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe scripts\gtkb_dispatcher_daemon.py --loop --project-root . --tick-seconds 120`
  - no `WindowsTerminal.exe` or `OpenConsole.exe` process appeared in the filtered scan.
  - daemon status while running: `active_substrate: none`, `mode: shadow`, `running: true`, last decision `spawned: false`.
  - stop output: `Stopped dispatcher daemon (pid=38780 tree terminated, lock released).`
  - daemon status after stop: `active_substrate: none`, `mode: shadow`, `running: false`.
- Quiet observation:
  - first 35-second watch found no daemon/supervisor/Terminal/OpenConsole process other than the scan process itself; substrate stayed `none`.
  - second 35-second watch found no daemon/supervisor/Terminal/OpenConsole process; substrate stayed `none`.
- Scheduled task state after implementation:
  - `GTKB-DispatcherDaemon`: Disabled, Hidden, Execute `E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe`
  - `GTKB-HarnessStormWatchdog`: Disabled, Hidden, Execute `E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe`
  - `GTKB-DbSnapshot`: Ready, Hidden, Execute `E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe`

## Acceptance Criteria Status

- `gt bridge dispatch daemon start` uses sibling `pythonw.exe` on Windows when available: met.
- `scripts/ensure_dispatcher_daemon.py` uses sibling `pythonw.exe` on Windows when available: met.
- Both launcher paths fall back to the original executable when no sibling `pythonw.exe` exists: met.
- Existing detach/no-window/null-stdio semantics remain intact: met.
- Controlled daemon start/stop no longer creates a WindowsTerminal/OpenConsole process: met.
- No topology, selection, credential, deployment, DB schema, or scheduled-task definition changes occur: met.
- Safety brake remains active pending LO verification: met (`harness-state/bridge-substrate.json` is `substrate: none`).

## Residual Notes

During investigation, an automated mode transaction briefly restored `harness-state/bridge-substrate.json` from `none` to `dispatcher_daemon` with reason `release-governance unblock: restore owner-declared live dispatcher daemon substrate after canonical state drift`. That caused the known-bad pre-fix daemon start to reappear. Prime Builder restored the safety brake to `none` and stopped the daemon before implementation. The current code fix removes the console-allocating launch behavior when the daemon substrate is deliberately restored after verification.

`git diff --check` reports CRLF-tracked added lines in `groundtruth-kb/src/groundtruth_kb/cli.py` and `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` as trailing whitespace in this Windows worktree, even though Ruff formatting passes and byte inspection found normal CRLF with no doubled carriage returns. This is noted for LO review transparency; no actual trailing spaces were introduced in the LF-tracked files.

## Risk And Rollback

Residual risk is low. The helper only rewrites an executable named `python.exe` to a same-directory `pythonw.exe` when the sibling exists and only on Windows. Non-Windows behavior and missing-pythonw Windows installs continue using the original executable.

Rollback is limited to reverting the four changed target files:

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `scripts/ensure_dispatcher_daemon.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_daemon_supervision.py`

Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return `VERIFIED` if the report and implementation satisfy the approved proposal; otherwise return `NO-GO` with findings.
