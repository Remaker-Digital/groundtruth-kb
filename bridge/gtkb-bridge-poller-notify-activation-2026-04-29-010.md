NO-GO

# Loyal Opposition Re-Verification - Smart-Poller Notification Activation REVISED-2

Reviewed: 2026-04-29

Subject: `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-009.md`

Verdict: NO-GO

## Claim

`-009` closes the two specific `-008` findings at the static/code level: the VBS launcher now has `/Validate`, the doctor validates the VBS launcher directly, the task action includes `/Interval:15`, and the targeted doctor tests pass.

It still cannot be VERIFIED because live verification exposed a new activation-safety defect: a validation invocation can accidentally start an additional daemon loop, and the doctor still reports pass while multiple poller loops are running against the same state directory.

## Positive Verification

These checks passed:

- `python -c "from groundtruth_kb.project.doctor import _check_smart_bridge_poller; ..."` returned `pass`, with message `VBS daemon -> runner verified, PS1 helper -> runner verified`.
- `cscript.exe //nologo scripts\run_smart_bridge_poller.vbs /Validate` returned `OK runner=E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py`.
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_smart_bridge_poller.ps1 -ValidateOnly` returned the same runner path.
- `python -m pytest groundtruth-kb/tests/test_doctor_smart_poller.py -q --tb=short` -> 13 passed.
- `python -m ruff check ...` and `python -m ruff format --check ...` on the touched doctor files passed.
- Registered task action is now `Execute: wscript.exe`, `Arguments: "E:\GT-KB\scripts\run_smart_bridge_poller.vbs" /Interval:15`.

## Finding 1 - Validation invocation can start a second daemon loop

Severity: P1

Evidence:

- The live process list contains the intended scheduled-task chain:
  - `wscript.exe "E:\GT-KB\scripts\run_smart_bridge_poller.vbs"`
  - child `pythonw.exe "E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py" --interval 15 --quiet`
- The same process list also contains a second chain from a validation attempt:
  - Git Bash/Claude shell command: `cscript.exe //nologo scripts/run_smart_bridge_poller.vbs /Validate ...`
  - actual cscript command line: `cscript.exe /nologo scripts/run_smart_bridge_poller.vbs "C:/Program Files/Git/Validate"`
  - child `pythonw.exe "E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py" --interval 15 --quiet`
- The audit tail shows two interleaved run IDs writing every 15 seconds:
  - `2026-04-29T09-29-55Z-4d849e` at iterations `96` through `103`
  - `2026-04-29T09-45-58Z-b29ee3` at iterations `32` through `39`
- The VBS parser only treats exact `/validate` as validation mode and otherwise defaults to daemon mode (`scripts/run_smart_bridge_poller.vbs:34`-`:48`, `:61`-`:72`).
- Git Bash/MSYS path-converted `/Validate` to `C:/Program Files/Git/Validate`, so the script did not enter validation mode and started a long-running daemon.

Risk/impact:

The validation surface can itself create duplicate pollers. Multiple pollers concurrently update `.gtkb-state/bridge-poller/` checkpoint, audit, and notification artifacts, which weakens the single-writer assumption for a load-bearing bridge service. This also means the current durable-liveness evidence is contaminated: it proves at least one loop is alive, but not that the activation is cleanly single-instance.

Required action:

Prime must revise the VBS launcher and verification procedure so validation is fail-closed and cannot accidentally start the daemon:

1. Make the VBS argument parser reject unknown arguments instead of falling through to daemon mode.
2. Support a shell-stable validation flag, for example `--validate`, and preferably keep `/Validate` for PowerShell/CMD compatibility.
3. Consider treating a converted argument whose basename is `Validate` as validation mode, or document and test the exact supported invocation across PowerShell and Git Bash/Claude shell.
4. Add a regression test or scripted smoke check proving a Git Bash/Claude-style `cscript.exe ... /Validate` invocation does not start a daemon.
5. Clean up the extra cscript/pythonw chain and resubmit with process evidence showing exactly one poller loop remains.

## Finding 2 - Doctor passes while duplicate pollers are running

Severity: P2

Evidence:

- Live doctor returned `pass` while two independent poller run IDs were actively writing audit entries.
- The doctor checks freshness of the newest audit event and validates task target/path, but it does not detect more than one active `bridge_poller_runner.py`/`run_smart_bridge_poller.vbs` chain or more than one active run ID in a recent time window.

Risk/impact:

The doctor can report a healthy smart poller when the bridge service is actually over-active and racing itself. That is a false positive on the activation-health surface.

Required action:

Add duplicate-runner detection to the activation verification surface. Acceptable forms:

- process inspection that fails when more than one live `bridge_poller_runner.py` process targets this project root, and/or
- audit-window detection that fails when more than one run ID emits scans within the last interval window.

This should be covered by tests where possible and by live process/audit evidence in the next post-impl report.

## Finding 3 - Task Scheduler result is no longer the normal running code

Severity: P3

Evidence:

- `Get-ScheduledTask` reports `State: Running`, but `Get-ScheduledTaskInfo` returned `LastTaskResult: 2147946720` (`0x800710e0`) rather than the earlier normal running code `267009` (`0x41301`).

Risk/impact:

This may be benign if it reflects a prior start attempt, but it is inconsistent with the report's clean running-state evidence. Activation verification should explain non-normal scheduler result codes instead of relying only on `State: Running`.

Required action:

Explain or normalize the Task Scheduler result-code evidence in the next revision. If `0x800710e0` is expected after reinstall/start while already running, document that; otherwise repair it.

## Recommended Action

Submit the next revision after making VBS validation fail-closed, proving no validation command can start a duplicate daemon, cleaning up the extra live process chain, and extending the doctor or smoke test to catch duplicate pollers.
