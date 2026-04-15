param(
    [switch]$VerifyOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Workspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$LogDir = Join-Path $PSScriptRoot "logs"
$StartupDir = [Environment]::GetFolderPath("Startup")
$StartupShortcut = Join-Path $StartupDir "Agent Red Bridge Monitor Watchdog.lnk"

$WatchdogVbs = Join-Path $PSScriptRoot "run-bridge-monitor-watchdog-hidden.vbs"
$WatchdogScript = Join-Path $PSScriptRoot "bridge-monitor-watchdog.ps1"
$MonitorScript = Join-Path $PSScriptRoot "bridge-scan-monitor-window.ps1"
$EnsureScript = Join-Path $PSScriptRoot "ensure-bridge-scan-monitor.ps1"
$AlertScript = Join-Path $PSScriptRoot "show-bridge-liveness-alert.ps1"

$RequiredFiles = @(
    (Join-Path $PSScriptRoot "run-file-bridge-scan-hidden.vbs"),
    (Join-Path $PSScriptRoot "run-claude-bridge-scan-hidden.vbs"),
    (Join-Path $PSScriptRoot "poller-liveness-watcher.ps1"),
    $WatchdogVbs,
    $WatchdogScript,
    $MonitorScript,
    $EnsureScript,
    $AlertScript
)

foreach ($path in $RequiredFiles) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing bridge automation file: $path"
    }
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Get-RepetitionInterval {
    param([string]$TaskName)

    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if (-not $task) {
        return ""
    }

    $trigger = @($task.Triggers | Where-Object { $_.Repetition -and $_.Repetition.Interval } | Select-Object -First 1)
    if ($trigger.Count -eq 0) {
        return ""
    }

    return [string]$trigger[0].Repetition.Interval
}

function Test-TaskRequirement {
    param(
        [string]$TaskName,
        [string]$ExpectedInterval,
        [string]$ExpectedExecutable
    )

    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if (-not $task) {
        return [pscustomobject]@{
            Check = $TaskName
            Ok = $false
            Detail = "missing"
        }
    }

    $info = $task | Get-ScheduledTaskInfo
    $action = @($task.Actions)[0]
    $interval = Get-RepetitionInterval -TaskName $TaskName
    $ok = $task.State -ne "Disabled" -and $interval -eq $ExpectedInterval -and $action.Execute -eq $ExpectedExecutable
    return [pscustomobject]@{
        Check = $TaskName
        Ok = $ok
        Detail = "state=$($task.State) interval=$interval exe=$($action.Execute) last=$($info.LastTaskResult) next=$($info.NextRunTime)"
    }
}

function Test-ProcessCommand {
    param(
        [string]$Name,
        [string]$CommandPattern
    )

    $escaped = [Regex]::Escape($CommandPattern)
    $processes = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -in @("powershell.exe", "pwsh.exe", "wscript.exe") -and
        $_.CommandLine -match $escaped
    })

    if ($processes.Count -eq 0) {
        return [pscustomobject]@{
            Check = $Name
            Ok = $false
            Detail = "not running"
        }
    }

    $pids = ($processes | ForEach-Object { $_.ProcessId }) -join ", "
    return [pscustomobject]@{
        Check = $Name
        Ok = $true
        Detail = "running pid(s)=$pids"
    }
}

function Install-StartupShortcut {
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($StartupShortcut)
    $shortcut.TargetPath = "wscript.exe"
    $shortcut.Arguments = ('//B //Nologo "{0}"' -f $WatchdogVbs)
    $shortcut.WorkingDirectory = $Workspace
    $shortcut.Description = "Agent Red bridge monitor watchdog"
    $shortcut.Save()
}

function Start-Watchdog {
    $existing = Test-ProcessCommand -Name "bridge-monitor-watchdog.ps1" -CommandPattern "bridge-monitor-watchdog.ps1"
    if ($existing.Ok) {
        return
    }

    Start-Process -FilePath "wscript.exe" -WorkingDirectory $Workspace -ArgumentList @(
        "//B",
        "//Nologo",
        "`"$WatchdogVbs`""
    )
}

function Test-BridgeAutomation {
    $checks = @()
    $checks += Test-TaskRequirement -TaskName "AgentRedFileBridgeIndexScan-Codex" -ExpectedInterval "PT3M" -ExpectedExecutable "wscript.exe"
    $checks += Test-TaskRequirement -TaskName "AgentRedFileBridgeIndexScan-Claude" -ExpectedInterval "PT3M" -ExpectedExecutable "wscript.exe"
    $checks += Test-TaskRequirement -TaskName "AgentRedPollerLivenessWatcher" -ExpectedInterval "PT2M" -ExpectedExecutable "powershell.exe"

    $checks += [pscustomobject]@{
        Check = "startup shortcut"
        Ok = (Test-Path -LiteralPath $StartupShortcut)
        Detail = $StartupShortcut
    }

    $checks += Test-ProcessCommand -Name "bridge-monitor-watchdog.ps1" -CommandPattern "bridge-monitor-watchdog.ps1"
    $checks += Test-ProcessCommand -Name "bridge-scan-monitor-window.ps1" -CommandPattern "bridge-scan-monitor-window.ps1"

    $livenessPath = Join-Path $LogDir "poller-liveness-external.json"
    if (Test-Path -LiteralPath $livenessPath) {
        $liveness = Get-Content -Raw -LiteralPath $livenessPath | ConvertFrom-Json
        $checks += [pscustomobject]@{
            Check = "poller-liveness-external.json"
            Ok = ([string]$liveness.overallState -eq "ok")
            Detail = "overall=$($liveness.overallState) claude=$($liveness.claude.verdict) codex=$($liveness.codex.verdict)"
        }
    } else {
        $checks += [pscustomobject]@{
            Check = "poller-liveness-external.json"
            Ok = $false
            Detail = "missing"
        }
    }

    return $checks
}

if (-not $VerifyOnly) {
    Install-StartupShortcut
    Start-Watchdog
    Start-Sleep -Seconds 5
}

$results = Test-BridgeAutomation
$results | Format-Table -AutoSize | Out-String -Width 240

if (@($results | Where-Object { -not $_.Ok }).Count -gt 0) {
    exit 1
}

exit 0
