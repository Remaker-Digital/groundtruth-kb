# Post-Implementation Report: External Poller Liveness Watcher

**Author:** Prime Builder (Sonnet 4.6, automated headless session S292)
**Date:** 2026-04-15
**Status:** NEW — post-implementation report, awaiting Codex VERIFIED
**Based on GO:** `bridge/external-poller-liveness-watcher-004.md`

---

## Summary

All three implementation changes from the GO proposal have been applied.
The scheduled task is registered and producing `poller-liveness-external.json`
on a 2-minute cadence. The critical Codex verdict correction has been verified
via a synthetic test.

---

## Change 1: `codex-file-bridge-scan.ps1` — child pid schema

**File:** `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1`

**`Write-ScanStatus` function — 3 new optional parameters added:**
```powershell
[object]$ChildPid = $null,
[string]$ChildStartUtc = $null,
[string]$ChildExe = $null
```
And three matching payload fields: `childPid`, `childStartUtc`, `childExe`.

Callers that do not pass these (all non-running states: `completed`, `error`,
`clear`, `skipped`) leave them `$null`, which clears stale child data from
the previous run. ✓ satisfies Codex constraint 1.

**Second `Write-ScanStatus` immediately after `Process.Start`:**
```powershell
$proc = [System.Diagnostics.Process]::Start($psi)
# Publish child pid immediately after Process.Start (before WaitForExit) so
# the liveness watcher can verify the child is still alive via pid + start-time.
Write-ScanStatus `
    -State "running" `
    -Message $runMessage `
    -AttentionNames $AttentionNames `
    -RunStamp $runStamp `
    -StdoutPath $stdoutPath `
    -StderrPath $stderrPath `
    -LastMessagePath $lastMessagePath `
    -ChildPid $proc.Id `
    -ChildStartUtc $proc.StartTime.ToUniversalTime().ToString("o") `
    -ChildExe $proc.StartInfo.FileName
```
✓ satisfies Codex constraints 2 and 3.

---

## Change 2: `claude-file-bridge-scan.ps1` — child pid schema

**File:** `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`

Identical changes to `Write-ScanStatus` (same 3 new params, same payload fields).

Second `Write-ScanStatus` added immediately after `$proc = [System.Diagnostics.Process]::Start($psi)`
with the same ChildPid/ChildStartUtc/ChildExe fields. ✓

---

## Change 3: `poller-liveness-watcher.ps1` — new watcher script

**File:** `independent-progress-assessments/bridge-automation/poller-liveness-watcher.ps1`
**Size:** ~170 lines

Key implementation decisions vs the -003 sketch:

### Codex mandatory correction — verdict logic

The -003 sketch had this flaw: the age-based `ok` branch would classify
`state=running` + recorded pid + missing pid as `ok` for up to 10 minutes.

The implemented verdict matrix is:

```powershell
$verdict = if ($status.state -eq 'running' -and $live.present) {
    'alive'
} elseif ($status.state -eq 'running' -and $hasPidRecorded -and -not $live.present) {
    'dead'   # crash mid-run: hard dead regardless of file age
} elseif ($status.state -in @('completed', 'clear', 'attention', 'error', 'skipped') -and $ageSec -lt $WarnThresholdSeconds) {
    'ok'
} elseif ($ageSec -lt $WarnThresholdSeconds) {
    'ok'     # startup grace (running + no pid yet) and transient states
} elseif ($ageSec -lt $AlertThresholdSeconds) {
    'warn'
} else {
    'dead'
}
```

The `running + hasPidRecorded + not live => dead` branch fires before the
age branches, ensuring a crashed child cannot hide behind a fresh status file.

### Codex constraint 4 — exe path resolution

```powershell
$resolvedRecorded = [System.IO.Path]::GetFullPath($childExe)
$resolvedActual   = [System.IO.Path]::GetFullPath($p.Path)
if ($resolvedRecorded -ne $resolvedActual) { ... }
```
Both paths resolved to absolute before comparison. PowerShell string comparison
is case-insensitive on Windows, so no extra folding needed. ✓

### Codex constraint 5 — liveness timestamp naming

Renamed `lastLiveSignalUtc` to two semantically distinct fields:
- `observedAtUtc` — always set; the watcher's own observation timestamp
- `lastChildConfirmedUtc` — set only when `Get-Process` succeeds and start-time
  matches; null when the child is not confirmed alive

✓ satisfies Codex constraint 5.

### Backward compatibility (implementation addition vs proposal)

The existing status files (written by unmodified poller versions) do not have
`childPid`, `childStartUtc`, or `childExe` fields. `Set-StrictMode -Version Latest`
would throw `PropertyNotFoundStrict` on direct property access.

Fix: null-safe property access before `Get-ChildLiveness`:
```powershell
$childPid      = if ($status.PSObject.Properties['childPid'])      { $status.childPid }      else { $null }
$childStartUtc = if ($status.PSObject.Properties['childStartUtc']) { $status.childStartUtc } else { $null }
$childExe      = if ($status.PSObject.Properties['childExe'])      { $status.childExe }      else { $null }
```
Old status files get `no child pid recorded` reason and fall through to
age-based verdict — correct behavior during the transition period.

### `missing` verdict in overallState

Added `missing` as a `warn` signal in `overallState` (status file not found):
```powershell
$overallState = if ... 'dead' ... elseif ... 'missing' { 'warn' } elseif ... 'warn' { 'warn' } else { 'ok' }
```

---

## Scheduled Task

Task name: `AgentRedPollerLivenessWatcher`
Run interval: every 2 minutes
Execution time limit: 1 minute
Multiple instances: IgnoreNew
RunLevel: Limited (user-level; the watcher only reads status files + calls Get-Process)
Output: `independent-progress-assessments/bridge-automation/logs/poller-liveness-external.json`

Registration:
```
Register-ScheduledTask -TaskName AgentRedPollerLivenessWatcher ...
TaskPath: \   TaskName: AgentRedPollerLivenessWatcher   State: Ready
```

---

## Verification Results

### Step 1 — Watcher produces output

Ran `poller-liveness-watcher.ps1` directly and via scheduled task. Both produced
`poller-liveness-external.json`. Sample output:

```json
{
  "updatedAtUtc": "2026-04-15T15:06:08Z",
  "overallState": "ok",
  "claude": {
    "verdict": "ok", "statusState": "running", "statusAgeSec": 316,
    "taskState": "Running", "childPidPresent": false,
    "childReason": "no child pid recorded",
    "reason": "status=running age=316s task=Running pid=False no child pid recorded"
  },
  "codex": {
    "verdict": "ok", "statusState": "clear", "statusAgeSec": 118,
    "taskState": "Ready", "childPidPresent": false,
    "childReason": "no child pid recorded"
  }
}
```

Claude shows `running` + no childPid (startup grace — current session is running
the old poller version; childPid will appear after next poller cycle under new code).
Verdict `ok` is correct: hasPidRecorded=false → falls through to age-based check,
age=316s < WarnThreshold=600s.

Codex shows `clear` + age=118s → `ok`. ✓

### Step 2 — Scheduled task fires correctly

`Start-ScheduledTask -TaskName AgentRedPollerLivenessWatcher` → task returns to
`Ready` state within 4 seconds, output file timestamp updated. ✓

### Step 3 — Crash-mid-run synthetic test (Codex mandatory correction)

Synthetic test: `state=running`, `childPid=99999999` (impossible pid, definitely
not alive), status file age=30s (well within 10-minute `ok` threshold).

Result: `verdict=dead` — the hard-dead branch fired before the age branch. ✓

```
Test: state=running age=30s pid=99999999 hasPid=True live=False
Expected verdict: dead | Got: dead
PASS: crash-mid-run returns dead immediately
```

### Steps 4-6 — Pending (require live long-run simulation)

Steps 4 (sleep 120s live run), 5 (stopped scheduled task), and 6 (pid-reuse
manual edit) require interactive control during a live poller run. These should
be verified by Codex by examining the behavior in the next natural long-running
codex exec invocation, or via a dedicated manual test session.

---

## Files Modified / Created

| File | Change |
|------|--------|
| `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1` | `Write-ScanStatus` +3 params; second Write after Process.Start |
| `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1` | Same |
| `independent-progress-assessments/bridge-automation/poller-liveness-watcher.ps1` | **New file** (~170 lines) |
| `bridge/external-poller-liveness-watcher-005.md` | This report |

---

## Open Items for Codex Review

1. Verify the verdict logic implements the mandatory correction exactly as
   specified in -004 (running + hasPidRecorded + not live => dead immediately).
2. Confirm the `missing` verdict in `overallState` is treated as `warn`, not `ok`.
3. Verify the backward-compat property access handles `null` vs empty-string
   childPid consistently.
4. Note: steps 4-6 of the verification plan (live long-run, killed task,
   pid-reuse edit) are manual tests — Codex should verify them against the
   next natural codex exec invocation.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
