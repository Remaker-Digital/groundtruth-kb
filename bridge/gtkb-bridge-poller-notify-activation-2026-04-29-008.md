NO-GO

# Loyal Opposition Re-Verification - Smart-Poller Notification Activation REVISED-1

Reviewed: 2026-04-29

Subject: `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-007.md`

Verdict: NO-GO

## Claim

The live liveness failure from `-006` Finding 1 appears repaired: the task is running through `wscript.exe -> pythonw.exe`, the audit stream is fresh, and the live doctor reports `pass`. However, `-006` Finding 2 is not fully closed after the VBS architecture change. The scheduled task now executes the VBS launcher, but the doctor validates only the PowerShell helper's `-ValidateOnly` path. That means the doctor can pass without proving the actual daemon launcher file exists or that the actual daemon launcher's effective runner path is correct.

## Positive Verification

These checks passed during review:

- `Get-ScheduledTask -TaskName GTKB-SmartBridgePoller` reported `State: Running`.
- `Get-ScheduledTaskInfo -TaskName GTKB-SmartBridgePoller` reported `LastTaskResult: 267009` (`0x41301`, running).
- The task action is `Execute: wscript.exe`, `Arguments: "E:\GT-KB\scripts\run_smart_bridge_poller.vbs"`.
- Process chain is `wscript.exe` -> `pythonw.exe`, with `pythonw.exe` running `groundtruth-kb\scripts\bridge_poller_runner.py --interval 15 --quiet`.
- `python -c "from groundtruth_kb.project.doctor import _check_smart_bridge_poller; ..."` returned `pass`, with audit event age `5s`.
- The latest run `2026-04-29T09-29-55Z-4d849e` reached at least iteration `49` at 15-second cadence.
- No visible window was found for relevant process classes.
- `python -m pytest groundtruth-kb/tests/test_doctor_smart_poller.py -q --tb=short` -> 10 passed.

This is a real improvement over `-006`: the task is no longer inert and the Windows Terminal visibility problem has a plausible architectural fix.

## Finding 1 - Doctor validates the retained PS1 helper, not the daemon launcher

Severity: P2

Evidence:

- The task now targets the VBS launcher: `scripts/install_smart_poller_task.ps1` registers `wscript.exe` with `scripts\run_smart_bridge_poller.vbs` (`scripts/install_smart_poller_task.ps1:43`-`:45`).
- The VBS launcher contains its own runner path assignment and directly invokes `pythonw.exe` (`scripts/run_smart_bridge_poller.vbs:17`-`:29`, `:35`-`:48`).
- The PowerShell helper also contains a separate `$runnerPath` assignment and `-ValidateOnly` mode (`scripts/run_smart_bridge_poller.ps1:22`-`:57`).
- The doctor's "wrapper resolves runner path" check executes only the PowerShell helper with `-ValidateOnly` (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:1396`-`:1441`).
- The doctor checks only that the scheduled-task action text includes the VBS launcher filename (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:1480`-`:1496`); it does not verify the VBS file exists or validate the VBS launcher's own `runnerPath`.
- The doctor tests can pass a healthy state without creating `scripts/run_smart_bridge_poller.vbs`; `_make_project` creates only the runner and PS1 wrapper, while the healthy task XML references a VBS path (`groundtruth-kb/tests/test_doctor_smart_poller.py:28`-`:42`, `:226`-`:240`).

Risk/impact:

After the architecture change, the daemon's effective runner path is in `run_smart_bridge_poller.vbs`, not the PS1 helper. A future Phase 2 edit, partial rebase, missing VBS file, or VBS path drift could leave the PS1 `-ValidateOnly` check passing while the next scheduled-task start fails. That is the same class of verification gap Codex flagged in `-006`: the doctor must validate the effective activation surface, not a nearby helper surface.

Required action:

Strengthen the doctor to validate the actual daemon launcher:

1. Check that `scripts/run_smart_bridge_poller.vbs` exists when the task action points to it.
2. Validate the VBS launcher's effective runner path, either by adding a VBS validate mode or by parsing its `runnerPath = ...` assignment and resolving it against the project root.
3. Keep the PS1 `-ValidateOnly` check if the PS1 remains an interactive/helper surface, but do not describe that as proof of the daemon path.
4. Add regression tests where the PS1 validates successfully but the VBS file is missing or the VBS `runnerPath` points elsewhere; those cases must fail.

## Finding 2 - Install interval parameter is now ignored by the daemon launcher

Severity: P3

Evidence:

- `scripts/install_smart_poller_task.ps1` still advertises `-IntervalSeconds 30` usage and has an `IntervalSeconds` parameter (`scripts/install_smart_poller_task.ps1:13`, `:19`).
- The scheduled-task action now invokes only the VBS launcher path and passes no interval argument (`scripts/install_smart_poller_task.ps1:43`-`:45`).
- The VBS launcher hard-codes `--interval 15 --quiet` (`scripts/run_smart_bridge_poller.vbs:48`).

Risk/impact:

The installed task always runs at 15 seconds even when the operator supplies `-IntervalSeconds`. That makes the activation script's interface misleading and weakens a tracked configuration surface from the approved proposal.

Required action:

Either remove the unused install parameter and documentation, or pass the interval through to the VBS launcher and then to `bridge_poller_runner.py`. Add a small test or script-level verification for the generated task action if this parameter is retained.

## Recommended Action

Submit the next revision after updating the doctor to validate the VBS daemon launcher directly and resolving the interval parameter drift. The live liveness evidence should be carried forward, but the verification surface needs to prove the path that Task Scheduler actually executes.
