# Verification Review: External Poller Liveness Watcher

Verdict: VERIFIED

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input: `bridge/external-poller-liveness-watcher-005.md`
Prior GO: `bridge/external-poller-liveness-watcher-004.md`

## Claim

The post-implementation report is materially verified. The implementation adds
child process identity fields to both poller status writers, publishes the child
pid immediately after process start, implements the mandatory hard-dead verdict
for `running + recorded pid + failed pid check`, registers the watcher scheduled
task, and is producing an external liveness file.

## Evidence

### Poller schema and live pid publication

`independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1`
adds optional child-process parameters and payload fields at lines 24-58:

```text
ChildPid, ChildStartUtc, ChildExe
childPid, childStartUtc, childExe
```

The Codex poller writes an initial `running` status before spawn at line 134,
then writes a second `running` status immediately after
`[System.Diagnostics.Process]::Start($psi)` at lines 191-206 with:

```text
ChildPid = $proc.Id
ChildStartUtc = $proc.StartTime.ToUniversalTime().ToString("o")
ChildExe = $proc.StartInfo.FileName
```

Non-running Codex statuses call `Write-ScanStatus` without those child fields at
lines 228, 244, 251, and 260, so the default null values clear stale child data.

`independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`
has the same schema additions at lines 57-90. It publishes child identity
immediately after process start at lines 342-355, and non-running completed/error
statuses at lines 432-441 clear child data by omitting the child arguments.

### Watcher verdict logic

`independent-progress-assessments/bridge-automation/poller-liveness-watcher.ps1`
implements null-safe child-field access at lines 111-123.

The mandatory correction from the GO file is implemented at lines 139-142:

```text
running + live pid present => alive
running + pid recorded + pid check fails => dead
```

That dead branch precedes the age-based `ok` branch at lines 143-150, so a
crashed active child cannot be hidden by a fresh status file.

The timestamp semantics requested in the GO file are implemented at lines
153-167: `observedAtUtc` is always present, while `lastChildConfirmedUtc` is set
only when the child process is confirmed alive.

The `missing` verdict contributes `warn`, not `ok`, in the overall state logic at
lines 183-185.

### Runtime evidence

Current Codex status file:

```text
Command: Get-Content -Raw independent-progress-assessments/bridge-automation/logs/codex-scan-status.json
Result: state=running, updatedAtUtc=2026-04-15T15:10:10Z,
childPid=34156, childStartUtc=2026-04-15T15:10:10.6953010Z,
childExe=C:\Users\micha\AppData\Local\OpenAI\Codex\bin\codex.exe
```

The matching process exists:

```text
Command: Get-Process -Id 34156
Result: ProcessName=codex, StartTime=2026-04-15 08:10:10 -07:00,
Path=C:\Users\micha\AppData\Local\OpenAI\Codex\bin\codex.exe
```

Current external watcher output:

```text
Command: Get-Content -Raw independent-progress-assessments/bridge-automation/logs/poller-liveness-external.json
Result: updatedAtUtc=2026-04-15T15:12:03.9061389Z, overallState=ok,
codex.verdict=alive, codex.statusState=running, codex.childPidPresent=true,
codex.childReason="pid 34156 alive, child_age=113s"
```

This directly verifies the S292 prevention case: a legitimate active Codex run is
classified as `alive`, not stale or dead.

### Scheduled task evidence

```text
Command: Get-ScheduledTask -TaskName AgentRedPollerLivenessWatcher
Result: TaskPath=\, State=Ready
```

```text
Command: inspect task action/settings/trigger
Result: Execute=powershell.exe
Arguments=-NoLogo -NonInteractive -ExecutionPolicy Bypass -File "...poller-liveness-watcher.ps1"
Repetition.Interval=PT2M
ExecutionTimeLimit=PT1M
MultipleInstances=IgnoreNew
RunLevel=Limited
LogonType=Interactive
```

### Syntax verification

```text
Command: PowerShell parser ParseFile on all three scripts
Result:
PARSE OK: independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1
PARSE OK: independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1
PARSE OK: independent-progress-assessments/bridge-automation/poller-liveness-watcher.ps1
```

## Findings

No blocking findings.

The crash-mid-run behavior was verified by code inspection rather than by
killing the currently active Codex child process. The decisive branch is present
and ordered correctly in `poller-liveness-watcher.ps1` lines 139-142. Killing the
live child would have interrupted the bridge scan itself, so that destructive
manual test was not repeated.

Non-blocking hardening note: `Get-ChildLiveness` only performs the start-time
pid-reuse guard when `childStartUtc` is present. The current poller writers
publish `childPid` and `childStartUtc` together, so normal operation preserves
the guard. If future code or manual edits can produce `childPid` without
`childStartUtc`, treat that malformed state as not-live rather than accepting pid
existence alone.

## Required Action Items

None for this verification.

## Recommended Follow-Up

During a maintenance window, run the two destructive/manual cases that were not
safe to repeat during this live bridge scan:

1. Kill a dedicated test child process after the poller records its pid and
   confirm the watcher reports `dead` on the next tick.
2. Manually alter `childStartUtc` for a dedicated test status file and confirm
   the pid-reuse guard reports `dead`.

