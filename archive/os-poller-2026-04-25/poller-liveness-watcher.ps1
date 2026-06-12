# poller-liveness-watcher.ps1
# External liveness monitor for both file-bridge poller workers.
#
# Reads the status files written by codex-file-bridge-scan.ps1 and
# claude-file-bridge-scan.ps1 and verifies child process identity via
# pid + start-time lookup. Writes a single verdict file
# (logs/poller-liveness-external.json) on every invocation.
#
# Design: external-poller-liveness-watcher-003.md (approved -004 GO)
# Verdict logic corrected per Codex mandatory constraint in -004:
#   running + pid recorded + pid check fails => dead immediately (ignore age)
#
# Run via scheduled task AgentRedPollerLivenessWatcher every 2 minutes.
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

param(
    [int]$WarnThresholdSeconds  = 600,   # 10 min — status age before 'warn'
    [int]$AlertThresholdSeconds = 1800   # 30 min — status age before 'dead'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$logDir     = Join-Path $PSScriptRoot 'logs'
$outputFile = Join-Path $logDir 'poller-liveness-external.json'

# Returns a hashtable: { present: bool, reason: string }
# Checks pid existence, pid-reuse guard (start-time within 2s), and exe path sanity.
function Get-ChildLiveness {
    param(
        $childPid,
        $childStartUtc,
        $childExe
    )

    if ($null -eq $childPid -or "$childPid" -eq '') {
        return @{ present = $false; reason = 'no child pid recorded' }
    }

    $p = Get-Process -Id ([int]$childPid) -ErrorAction SilentlyContinue
    if (-not $p) {
        return @{ present = $false; reason = "pid $childPid not found" }
    }

    # Pid reuse guard: recorded start time must match actual start time within 2 seconds.
    # 2s tolerance absorbs clock-read jitter between Process.Start return and the
    # timestamp capture in the poller. Once a mismatch > 2s is detected, the pid
    # has been reused by a different process and we must treat it as dead.
    if ($childStartUtc) {
        try {
            $actualStart = $p.StartTime.ToUniversalTime()
            $recorded    = [DateTime]::Parse($childStartUtc).ToUniversalTime()
            $delta       = [Math]::Abs(($actualStart - $recorded).TotalSeconds)
            if ($delta -gt 2) {
                return @{ present = $false; reason = "pid reused (start delta ${delta}s)" }
            }
        } catch {
            return @{ present = $false; reason = "cannot read StartTime: $_" }
        }
    }

    # Exe path sanity check: resolve both paths to absolute before comparing so
    # relative-path or case-normalization differences do not produce false alarms.
    # This is a belt-and-suspenders check; skip it if path resolution fails rather
    # than raising a false dead verdict.
    if ($childExe -and $p.Path) {
        try {
            $resolvedRecorded = [System.IO.Path]::GetFullPath($childExe)
            $resolvedActual   = [System.IO.Path]::GetFullPath($p.Path)
            # PowerShell string comparison is case-insensitive by default on Windows.
            if ($resolvedRecorded -ne $resolvedActual) {
                return @{ present = $false; reason = "exe mismatch: $resolvedActual vs $resolvedRecorded" }
            }
        } catch {
            # Non-fatal: path resolution failed; skip the exe check.
        }
    }

    $childAgeSec = [int]((Get-Date) - $p.StartTime).TotalSeconds
    return @{ present = $true; reason = "pid $childPid alive, child_age=${childAgeSec}s" }
}

# Returns an ordered hashtable describing the health of one poller.
function Test-PollerHealth {
    param(
        [string]$Name,
        [string]$StatusPath,
        [string]$TaskName
    )

    $observedAt = (Get-Date).ToUniversalTime().ToString('o')

    if (-not (Test-Path -LiteralPath $StatusPath)) {
        return [ordered]@{
            name          = $Name
            verdict       = 'missing'
            reason        = 'status file missing'
            observedAtUtc = $observedAt
        }
    }

    $status    = Get-Content -Raw $StatusPath | ConvertFrom-Json
    $updatedAt = [DateTime]::Parse($status.updatedAtUtc).ToUniversalTime()
    $ageSec    = ((Get-Date).ToUniversalTime() - $updatedAt).TotalSeconds

    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    $taskState = if ($task) { "$($task.State)" } else { 'Missing' }

    # Read child fields with null-safe property access so the watcher tolerates
    # status files written by older poller versions that lack these fields.
    $childPid      = if ($status.PSObject.Properties['childPid'])      { $status.childPid }      else { $null }
    $childStartUtc = if ($status.PSObject.Properties['childStartUtc']) { $status.childStartUtc } else { $null }
    $childExe      = if ($status.PSObject.Properties['childExe'])      { $status.childExe }      else { $null }

    $live = Get-ChildLiveness `
        -childPid      $childPid `
        -childStartUtc $childStartUtc `
        -childExe      $childExe

    # $hasPidRecorded: true once the poller has written childPid after Process.Start.
    # False during the brief startup-grace window where state=running but childPid
    # has not yet been published (between first and second Write-ScanStatus calls).
    $hasPidRecorded = $null -ne $childPid -and "$childPid" -ne ''

    # Verdict matrix (corrected per Codex -004 mandatory constraint):
    #
    #   task missing                              => missing (operator/action required)
    #   task disabled                             => dead    (3-minute cycle cannot run)
    #   running + pid found + start-time matches  => alive   (long run OK; do not alarm)
    #   running + pid recorded + pid check fails  => dead    (crash mid-run; bypass age)
    #   running + no pid recorded                 => ok      (startup grace; fallthrough)
    #   non-running + age < WarnThreshold         => ok
    #   age < WarnThreshold                       => ok      (catches startup grace)
    #   age < AlertThreshold                      => warn
    #   else                                      => dead
    #
    # The critical fix vs. the sketch in -003: the third branch from the sketch
    # ("elseif ageSec < WarnThreshold => ok") would classify running+pid-recorded
    # +pid-missing as ok for the first 10 minutes. That is now blocked by the
    # explicit "running + hasPidRecorded + not live" => dead branch above it.
    $verdict = if ($taskState -eq 'Missing') {
        'missing'
    } elseif ($taskState -eq 'Disabled') {
        'dead'
    } elseif ($status.state -eq 'running' -and $live.present) {
        'alive'
    } elseif ($status.state -eq 'running' -and $hasPidRecorded -and -not $live.present) {
        'dead'   # crash mid-run: recorded pid gone — hard dead regardless of file age
    } elseif ($status.state -in @('completed', 'clear', 'attention', 'error', 'skipped') -and $ageSec -lt $WarnThresholdSeconds) {
        'ok'
    } elseif ($ageSec -lt $WarnThresholdSeconds) {
        'ok'     # startup grace (running + no pid yet) and any other transient state
    } elseif ($ageSec -lt $AlertThresholdSeconds) {
        'warn'
    } else {
        'dead'
    }

    # lastChildConfirmedUtc is set only when Get-Process succeeds and start-time
    # matches — it records "we confirmed this child was alive at this moment."
    # Distinct from observedAtUtc (watcher's own timestamp, always present).
    $lastChildConfirmedUtc = if ($live.present) { $observedAt } else { $null }

    return [ordered]@{
        name                  = $Name
        verdict               = $verdict
        statusState           = $status.state
        statusAgeSec          = [int]$ageSec
        taskState             = "$taskState"
        childPidPresent       = $live.present
        childReason           = $live.reason
        lastChildConfirmedUtc = $lastChildConfirmedUtc
        observedAtUtc         = $observedAt
        reason                = ("status=$($status.state) age=$([int]$ageSec)s " +
                                 "task=$taskState pid=$($live.present) $($live.reason)")
    }
}

$claude = Test-PollerHealth `
    -Name       'claude' `
    -StatusPath (Join-Path $logDir 'claude-scan-status.json') `
    -TaskName   'AgentRedFileBridgeIndexScan-Claude'

$codex = Test-PollerHealth `
    -Name       'codex' `
    -StatusPath (Join-Path $logDir 'codex-scan-status.json') `
    -TaskName   'AgentRedFileBridgeIndexScan-Codex'

$overallState = if (@($claude.verdict, $codex.verdict) -contains 'dead') { 'dead' }
                elseif (@($claude.verdict, $codex.verdict) -contains 'missing') { 'warn' }
                elseif (@($claude.verdict, $codex.verdict) -contains 'warn') { 'warn' }
                else { 'ok' }

$summary = [ordered]@{
    updatedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
    overallState = $overallState
    claude       = $claude
    codex        = $codex
}

# Atomic write: temp file + rename so readers never see a partial file.
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$tmpName = "poller-liveness-external.{0}.tmp" -f ([guid]::NewGuid().ToString("N"))
$tmpPath = Join-Path $logDir $tmpName
$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $tmpPath -Encoding UTF8
if (Test-Path -LiteralPath $outputFile) {
    Remove-Item -LiteralPath $outputFile -Force
}
Move-Item -LiteralPath $tmpPath -Destination $outputFile -Force
