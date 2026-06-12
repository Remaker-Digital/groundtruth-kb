param(
    [int]$WarnThresholdSeconds = 600,
    [int]$AlertThresholdSeconds = 1800,
    [int]$ConfirmMissingPidSeconds = 8
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$LogDir = Join-Path $PSScriptRoot "logs"
$OutputFile = Join-Path $LogDir "poller-liveness-external.json"
$StableLogPath = Join-Path $LogDir "poller-liveness-stable.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Add-LogLine {
    param(
        [string]$Path,
        [string]$Value
    )

    for ($attempt = 1; $attempt -le 5; $attempt++) {
        try {
            [System.IO.File]::AppendAllText($Path, $Value + [Environment]::NewLine, [System.Text.Encoding]::UTF8)
            return
        } catch {
            if ($attempt -eq 5) {
                throw
            }
            Start-Sleep -Milliseconds (100 * $attempt)
        }
    }
}

$WatcherMutex = [System.Threading.Mutex]::new($false, "Local\AgentRedPollerLivenessStableWatcher")
$WatcherMutexAcquired = $false
try {
    $WatcherMutexAcquired = $WatcherMutex.WaitOne([TimeSpan]::FromSeconds(20))
} catch [System.Threading.AbandonedMutexException] {
    $WatcherMutexAcquired = $true
} catch {
    if ($_.Exception.InnerException -is [System.Threading.AbandonedMutexException]) {
        $WatcherMutexAcquired = $true
    } else {
        throw
    }
}
if (-not $WatcherMutexAcquired) {
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    Add-LogLine -Path $StableLogPath -Value "$stamp another watcher run is active; leaving previous output in place"
    $WatcherMutex.Dispose()
    exit 0
}

function Write-StableLog {
    param([string]$Message)
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    Add-LogLine -Path $StableLogPath -Value "$stamp $Message"
}

function Publish-JsonFile {
    param(
        [string]$TempPath,
        [string]$DestinationPath
    )

    for ($attempt = 1; $attempt -le 5; $attempt++) {
        try {
            if (Test-Path -LiteralPath $DestinationPath) {
                $destinationDir = Split-Path -Parent $DestinationPath
                $destinationLeaf = Split-Path -Leaf $DestinationPath
                $backupPath = Join-Path $destinationDir ("{0}.{1}.bak" -f $destinationLeaf, ([guid]::NewGuid().ToString("N")))
                [System.IO.File]::Replace($TempPath, $DestinationPath, $backupPath, $true)
                Remove-Item -LiteralPath $backupPath -Force -ErrorAction SilentlyContinue
            } else {
                Move-Item -LiteralPath $TempPath -Destination $DestinationPath -Force
            }
            return
        } catch {
            if ($attempt -eq 5) {
                throw
            }
            Start-Sleep -Milliseconds (100 * $attempt)
        }
    }
}

function Get-OptionalProperty {
    param(
        [object]$Object,
        [string]$Name
    )

    if ($null -eq $Object) {
        return $null
    }

    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }

    return $property.Value
}

function Get-ChildLiveness {
    param(
        $ChildPid,
        $ChildStartUtc,
        $ChildExe
    )

    if ($null -eq $ChildPid -or "$ChildPid" -eq "") {
        return @{
            present = $false
            reason = "no child pid recorded"
        }
    }

    $process = Get-Process -Id ([int]$ChildPid) -ErrorAction SilentlyContinue
    if (-not $process) {
        return @{
            present = $false
            reason = "pid $ChildPid not found"
        }
    }

    if ($ChildStartUtc) {
        try {
            $actualStart = $process.StartTime.ToUniversalTime()
            $recordedStart = [DateTime]::Parse($ChildStartUtc).ToUniversalTime()
            $delta = [Math]::Abs(($actualStart - $recordedStart).TotalSeconds)
            if ($delta -gt 2) {
                return @{
                    present = $false
                    reason = "pid reused (start delta ${delta}s)"
                }
            }
        } catch {
            return @{
                present = $false
                reason = "cannot read StartTime: $($_.Exception.Message)"
            }
        }
    }

    if ($ChildExe -and $process.Path) {
        try {
            $expectedPath = [System.IO.Path]::GetFullPath($ChildExe)
            $actualPath = [System.IO.Path]::GetFullPath($process.Path)
            if ($expectedPath -ne $actualPath) {
                return @{
                    present = $false
                    reason = "exe mismatch: $actualPath vs $expectedPath"
                }
            }
        } catch {
            # If path resolution itself is flaky, do not convert that into a dead verdict.
        }
    }

    $childAgeSec = [int]((Get-Date) - $process.StartTime).TotalSeconds
    return @{
        present = $true
        reason = "pid $ChildPid alive, child_age=${childAgeSec}s"
    }
}

function New-PollerResult {
    param(
        [string]$Name,
        [string]$Verdict,
        [string]$StatusState,
        [int]$StatusAgeSec,
        [string]$TaskState,
        [bool]$ChildPidPresent,
        [string]$ChildReason,
        [string]$ObservedAtUtc,
        [string]$LastChildConfirmedUtc
    )

    return [ordered]@{
        name = $Name
        verdict = $Verdict
        statusState = $StatusState
        statusAgeSec = $StatusAgeSec
        taskState = $TaskState
        childPidPresent = $ChildPidPresent
        childReason = $ChildReason
        lastChildConfirmedUtc = $LastChildConfirmedUtc
        observedAtUtc = $ObservedAtUtc
        reason = ("status=$StatusState age=${StatusAgeSec}s task=$TaskState " +
            "pid=$ChildPidPresent $ChildReason")
    }
}

function Test-PollerHealth {
    param(
        [string]$Name,
        [string]$StatusPath,
        [string]$TaskName,
        [switch]$ConfirmedMissingPid
    )

    $observedAt = (Get-Date).ToUniversalTime().ToString("o")

    if (-not (Test-Path -LiteralPath $StatusPath)) {
        return New-PollerResult `
            -Name $Name `
            -Verdict "missing" `
            -StatusState "missing" `
            -StatusAgeSec 0 `
            -TaskState "Unknown" `
            -ChildPidPresent $false `
            -ChildReason "status file missing" `
            -ObservedAtUtc $observedAt `
            -LastChildConfirmedUtc $null
    }

    try {
        $status = Get-Content -Raw -LiteralPath $StatusPath | ConvertFrom-Json -ErrorAction Stop
    } catch {
        return New-PollerResult `
            -Name $Name `
            -Verdict "dead" `
            -StatusState "parse-error" `
            -StatusAgeSec 0 `
            -TaskState "Unknown" `
            -ChildPidPresent $false `
            -ChildReason "status file parse failed: $($_.Exception.Message)" `
            -ObservedAtUtc $observedAt `
            -LastChildConfirmedUtc $null
    }

    $statusState = [string](Get-OptionalProperty -Object $status -Name "state")
    $updatedAtUtc = [string](Get-OptionalProperty -Object $status -Name "updatedAtUtc")
    $ageSec = 0
    if ($updatedAtUtc) {
        try {
            $updatedAt = [DateTime]::Parse($updatedAtUtc).ToUniversalTime()
            $ageSec = [int](((Get-Date).ToUniversalTime() - $updatedAt).TotalSeconds)
        } catch {
            $ageSec = $AlertThresholdSeconds
        }
    } else {
        $ageSec = $AlertThresholdSeconds
    }

    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    $taskState = if ($task) { [string]$task.State } else { "Missing" }

    $childPid = Get-OptionalProperty -Object $status -Name "childPid"
    $childStartUtc = Get-OptionalProperty -Object $status -Name "childStartUtc"
    $childExe = Get-OptionalProperty -Object $status -Name "childExe"
    $hasPidRecorded = $null -ne $childPid -and "$childPid" -ne ""
    $live = Get-ChildLiveness -ChildPid $childPid -ChildStartUtc $childStartUtc -ChildExe $childExe
    $lastChildConfirmedUtc = if ($live.present) { $observedAt } else { $null }

    if ($taskState -eq "Missing") {
        $verdict = "missing"
    } elseif ($taskState -eq "Disabled") {
        $verdict = "dead"
    } elseif ($statusState -eq "error") {
        $verdict = "dead"
    } elseif ($statusState -eq "running" -and $live.present) {
        $verdict = "alive"
    } elseif ($statusState -eq "running" -and $hasPidRecorded -and -not $live.present) {
        if (-not $ConfirmedMissingPid -and $ConfirmMissingPidSeconds -gt 0) {
            Write-StableLog "$Name suspect missing pid; waiting ${ConfirmMissingPidSeconds}s to confirm ($($live.reason))"
            Start-Sleep -Seconds $ConfirmMissingPidSeconds
            $confirmed = Test-PollerHealth `
                -Name $Name `
                -StatusPath $StatusPath `
                -TaskName $TaskName `
                -ConfirmedMissingPid
            if ([string]$confirmed.verdict -eq "dead") {
                Write-StableLog "$Name confirmed dead after debounce"
            } else {
                Write-StableLog "$Name debounced transient missing pid; now $($confirmed.verdict)"
            }
            return $confirmed
        }
        $verdict = "dead"
    } elseif ($statusState -in @("completed", "clear", "attention", "skipped") -and $ageSec -lt $WarnThresholdSeconds) {
        $verdict = "ok"
    } elseif ($ageSec -lt $WarnThresholdSeconds) {
        $verdict = "ok"
    } elseif ($ageSec -lt $AlertThresholdSeconds) {
        $verdict = "warn"
    } else {
        $verdict = "dead"
    }

    return New-PollerResult `
        -Name $Name `
        -Verdict $verdict `
        -StatusState $statusState `
        -StatusAgeSec $ageSec `
        -TaskState $taskState `
        -ChildPidPresent ([bool]$live.present) `
        -ChildReason ([string]$live.reason) `
        -ObservedAtUtc $observedAt `
        -LastChildConfirmedUtc $lastChildConfirmedUtc
}

$claude = Test-PollerHealth `
    -Name "claude" `
    -StatusPath (Join-Path $LogDir "claude-scan-status.json") `
    -TaskName "AgentRedFileBridgeIndexScan-Claude"

$codex = Test-PollerHealth `
    -Name "codex" `
    -StatusPath (Join-Path $LogDir "codex-scan-status.json") `
    -TaskName "AgentRedFileBridgeIndexScan-Codex"

$verdicts = @([string]$claude.verdict, [string]$codex.verdict)
$overallState = if ($verdicts -contains "dead") {
    "dead"
} elseif ($verdicts -contains "missing") {
    "warn"
} elseif ($verdicts -contains "warn") {
    "warn"
} else {
    "ok"
}

$summary = [ordered]@{
    updatedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
    overallState = $overallState
    claude = $claude
    codex = $codex
}

$tmpName = "poller-liveness-external.{0}.tmp" -f ([guid]::NewGuid().ToString("N"))
$tmpPath = Join-Path $LogDir $tmpName
$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $tmpPath -Encoding UTF8

Publish-JsonFile -TempPath $tmpPath -DestinationPath $OutputFile

try {
    $WatcherMutex.ReleaseMutex()
} catch {
    Write-StableLog "mutex release failed after liveness publish: $($_.Exception.Message)"
}
$WatcherMutex.Dispose()
