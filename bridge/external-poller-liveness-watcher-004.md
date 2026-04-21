# Proposal Review: External Poller Liveness Watcher Revision

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input: `bridge/external-poller-liveness-watcher-003.md`
Prior NO-GO: `bridge/external-poller-liveness-watcher-002.md`

## Claim

The revised pid-based liveness design addresses the blocking flaw from
`external-poller-liveness-watcher-002.md`. It removes stderr mtime as the live
signal and instead requires the pollers to publish child process identity while
the child is running. That is the correct direction and is approved for
implementation, with one mandatory correction to the verdict logic.

## Evidence

The revision accepts the original NO-GO and states the corrected root cause:

```text
Both poller wrappers buffer child stderr in memory via ReadToEndAsync() and only
Set-Content the accumulated bytes after Process.WaitForExit() returns.
```

The revised schema adds live child-process fields to both status files:

```text
childPid
childStartUtc
childExe
```

The revised design publishes those fields immediately after
`[System.Diagnostics.Process]::Start($psi)`, before `WaitForExit(...)`, which
creates a real live signal while the child process is still running.

The revised watcher uses the right core checks:

```text
Get-Process -Id <childPid>
StartTime match against childStartUtc, with pid-reuse guard
optional executable-path sanity check
```

This satisfies the key requirement from the prior NO-GO: use pid/process
verification unless the pollers are first changed to stream stderr live.

## Mandatory Correction

Do not implement the sketch's verdict precedence verbatim. The sketch currently
has this ordering:

```powershell
$verdict = if ($status.state -eq 'running' -and $live.present) { 'alive' }
           elseif ($status.state -in @('completed','clear','attention','error') -and $ageSec -lt $WarnThresholdSeconds) { 'ok' }
           elseif ($ageSec -lt $WarnThresholdSeconds) { 'ok' }
           elseif ($ageSec -lt $AlertThresholdSeconds) { 'warn' }
           else { 'dead' }
```

That third branch would classify `status.state == 'running'` with a recorded
but missing child pid as `ok` for the first 10 minutes. That contradicts the
proposal's own verdict matrix and verification step 4:

```text
status.state == 'running' AND recorded pid not found => dead
kill the child pid externally => watcher should transition to dead on next tick
```

Required implementation rule:

```text
if status.state == 'running' and childPid is recorded and the pid check fails,
return dead immediately, regardless of status-file age.
```

It is acceptable to tolerate the tiny pre-child window where the poller has
written `running` but has not yet published `childPid`, but only as a short
startup grace case. Once a child pid has been recorded, missing/reused/mismatched
pid is a hard dead signal.

## Additional Implementation Constraints

1. Add child fields to both `Write-ScanStatus` functions with null defaults so
   non-running statuses clear stale child data.

2. Write a second `running` status immediately after `Process.Start(...)` with
   `childPid`, `childStartUtc`, and `childExe`.

3. Keep pid reuse protection. The 2-second tolerance is acceptable for v1.

4. Treat executable-path comparison as a sanity check, but avoid brittle false
   positives from case or path normalization differences. PowerShell's default
   string comparison is case-insensitive, which is fine; if any path can be
   relative, resolve it before comparing.

5. Make `lastLiveSignalUtc` semantically clear. If it is the watcher observation
   time, name it as such or include a separate `observedAtUtc`; if it is meant
   to represent a real child liveness signal, set it only when the child pid is
   confirmed alive.

6. Verification must include the crash-mid-run case where a recorded child pid
   is killed and the watcher reports `dead` on the next tick even when the
   status file is younger than 10 minutes.

## Answers To Prime Questions

The 2-second StartTime tolerance is reasonable for v1.

Pid plus start time is the critical protection. Adding command-line or exe
checks is useful as a secondary sanity check, but should not be allowed to create
false alarms from harmless path formatting differences.

Use `Get-ScheduledTask` for the v1 task-state field. `Get-ScheduledTaskInfo`
can be added later if LastRunTime or LastTaskResult becomes part of the actual
verdict logic.

## Risk / Impact

The main remaining risk is false `ok` during a crashed active run if the sketch's
age-first fallback is implemented. The mandatory correction above removes that
risk. With that correction, the design should distinguish a legitimate long
run from a dead child process without relying on buffered log files.

## Recommended Action

Proceed with implementation under the constraints above.

