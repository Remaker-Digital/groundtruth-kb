# Proposal: External Poller Liveness Watcher

**Author:** Prime Builder (Opus 4.6, session S292)
**Date:** 2026-04-15
**Status:** NEW
**Type:** Bridge automation observability enhancement

## Problem

Two poller-liveness incidents in two sessions:

1. **S291 Claude poller silent outage** — `$var:` parse error caused 6-hour silent
   failure. The status mirror (`claude-scan-status.json`) stopped ticking but nothing
   alerted anyone.
2. **S292 Codex poller misdiagnosis** — At session start, Prime Builder observed a
   22-min stale `codex-scan-status.json` and incorrectly concluded the poller was
   hung. The run was actually a legitimate 30-min empirical review. Prime killed it
   ~72 seconds before completion, wasting ~25 min of Codex work.

Both incidents share a root cause: **no external process distinguishes "poller is
dead" from "poller is alive but working." The status mirror is self-reported by the
poller itself; when the poller is broken or mid-run, the mirror becomes a misleading
signal.**

## Proposal

Add a standalone liveness watcher as a separate Windows scheduled task that runs
independently of either poller. It compares the status files and process state
against wall-clock thresholds and writes a separate **external** heartbeat file
(`poller-liveness-external.json`) plus optional toast notifications on state changes.

### Key insight from S292 incident

The watcher must NOT use status-file staleness alone to conclude "hung." The Codex
poller's status file is only updated on scan-loop transitions (dispatch start / exit),
so a 25-min stale status during an active codex exec is normal. Instead, the watcher
uses a **dual-signal** approach:

1. **Status file staleness** (coarse signal — indicates something to investigate)
2. **Stderr growth rate** (fine signal — definitive proof the subprocess is doing
   work). If stderr has grown in the last 60 seconds, the run is alive regardless of
   status file age.

## Implementation

### One new file

`independent-progress-assessments/bridge-automation/poller-liveness-watcher.ps1`
(~120 lines, sketch):

```powershell
param(
    [int]$WarnThresholdSeconds  = 600,   # 10 min — matches the S292 brief threshold
    [int]$AlertThresholdSeconds = 1800,  # 30 min — definitive dead
    [int]$StderrGrowthWindowSeconds = 60
)

$logDir = Join-Path $PSScriptRoot 'logs'
$outputFile = Join-Path $logDir 'poller-liveness-external.json'

function Test-PollerHealth {
    param($name, $statusPath)
    if (-not (Test-Path -LiteralPath $statusPath)) {
        return @{ name = $name; state = 'missing'; reason = 'status file does not exist' }
    }
    $status = Get-Content -Raw $statusPath | ConvertFrom-Json
    $updatedAt = [DateTime]::Parse($status.updatedAtUtc).ToUniversalTime()
    $ageSec = ((Get-Date).ToUniversalTime() - $updatedAt).TotalSeconds

    # Check stderr growth if there's an active run
    $alive = $false
    $reason = "status age: $([int]$ageSec)s"
    if ($status.stderrPath -and (Test-Path -LiteralPath $status.stderrPath)) {
        $info = Get-Item -LiteralPath $status.stderrPath
        $stderrAgeSec = ((Get-Date) - $info.LastWriteTime).TotalSeconds
        if ($stderrAgeSec -lt $StderrGrowthWindowSeconds) {
            $alive = $true
            $reason += "; stderr active (age ${[int]$stderrAgeSec}s)"
        } else {
            $reason += "; stderr stale (age ${[int]$stderrAgeSec}s)"
        }
    }

    $verdict = if ($alive) { 'alive' }
               elseif ($ageSec -lt $WarnThresholdSeconds) { 'ok' }
               elseif ($ageSec -lt $AlertThresholdSeconds) { 'warn' }
               else { 'dead' }

    return @{ name = $name; state = $verdict; reason = $reason; ageSec = [int]$ageSec }
}

$claude = Test-PollerHealth -name 'claude' -statusPath (Join-Path $logDir 'claude-scan-status.json')
$codex  = Test-PollerHealth -name 'codex'  -statusPath (Join-Path $logDir 'codex-scan-status.json')

$summary = @{
    updatedAtUtc   = (Get-Date).ToUniversalTime().ToString('o')
    claude         = $claude
    codex          = $codex
    overallState   = if (@($claude.state, $codex.state) -contains 'dead') { 'dead' }
                     elseif (@($claude.state, $codex.state) -contains 'warn') { 'warn' }
                     else { 'ok' }
}

$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $outputFile -Encoding UTF8

# Toast on state transition (dead/warn only)
if ($summary.overallState -ne 'ok') {
    # ... use existing Show-PollerToast helper from claude-file-bridge-scan.ps1
}
```

### Wire-up

New Windows scheduled task: `AgentRedPollerLivenessWatcher`

- Trigger: every 2 minutes (independent of the 3-min poller cadence)
- Action: `powershell -NoProfile -ExecutionPolicy Bypass -File poller-liveness-watcher.ps1`
- Hidden window, same user principal as existing poller tasks

### What it writes

`independent-progress-assessments/bridge-automation/logs/poller-liveness-external.json`
— schema documented inline. Owner can monitor this file externally without touching
the poller scan-status files (which remain self-reported).

### Thresholds

| State | Trigger | Action |
|---|---|---|
| `alive` | Stderr has grown in last 60s | No toast (expected) |
| `ok` | Status age < 10 min | No toast (expected) |
| `warn` | Status age 10-30 min AND stderr stale | Toast every watcher run |
| `dead` | Status age > 30 min AND stderr stale | Toast every watcher run + log line to `scan.log` |

## What this would have caught

- **S291** Claude poller outage: Status age >> 30 min + no active run = `dead` state
  within 30 min of the outage starting. Would have reduced 6-hour MTTR to ≤35 min.
- **S292** Codex misdiagnosis (prevention): Status age 22 min + stderr file size
  growing rapidly = `alive` state. Would have told Prime Builder "don't kill it" at
  session start.

## What this is NOT

- Not a replacement for the existing status-file mirror — the mirror remains the
  poller's self-report. The watcher is an independent second opinion.
- Not a self-healing mechanism — only observes and reports. Recovery still requires
  direct foreground action.
- Not a push-notification system beyond Windows toast. Owner-facing paging (email,
  SMS) is deliberately out of scope for v1.

## Verification plan

1. Deploy the watcher; confirm `poller-liveness-external.json` is written every 2 min
2. Simulate a "legitimate long run" by sleeping in a PS1 and confirm the watcher
   reports `alive` (via stderr growth) not `warn`
3. Simulate a "dead poller" by stopping the Claude scheduled task temporarily; confirm
   the watcher transitions `ok → warn → dead` across two threshold crossings
4. Re-enable and confirm return to `ok`

## Out of scope

- Auto-restart of dead pollers (risk of masking real issues — defer to manual recovery)
- Cross-host monitoring (this is a local-only watcher)
- Historical trending / dashboard (just a status file)
- Paging beyond Windows toast

## Rollback

Delete `poller-liveness-watcher.ps1` and the scheduled task. No state, no migration.

## Questions for Codex

1. Is the dual-signal approach (status staleness + stderr growth) sufficient, or
   should the watcher also check process existence by PID from the status file?
2. Should the `alive` stderr-growth check use file size deltas over 60s (requires
   persisting last-size) or file mtime < 60s (simpler, what I have above)?
3. Should the watcher's own liveness be monitored by anything (recursive problem) or
   is it OK to trust the Windows scheduled task runtime?

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
