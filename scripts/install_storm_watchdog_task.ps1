# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
<#
.SYNOPSIS
    Register the GTKB-HarnessStormWatchdog Windows scheduled task.

.DESCRIPTION
    Registers the existing storm-watchdog launcher as a hidden, repeating
    Windows scheduled task. The task runs through pythonw.exe so Task Scheduler
    does not allocate a visible console window.

    Kept deliberately separate from the GTKB-DispatcherDaemon supervisor task
    so watchdog lifecycle control cannot mutate daemon supervision.

.PARAMETER TaskName
    Task name. Default 'GTKB-HarnessStormWatchdog'. Tests pass a nonce-suffixed
    name.

.PARAMETER ProjectRoot
    The GT-KB project root directory. Required.

.PARAMETER IntervalMinutes
    Watchdog wake interval in minutes. Default 1.

.PARAMETER PythonExe
    Python (GUI-subsystem) executable. Default: the project venv pythonw.exe if
    present, else 'pythonw.exe' from PATH.

.PARAMETER DryRun
    If set, print 'WOULD REGISTER TaskName=... Execute=... Arguments=...' and
    exit 0 WITHOUT calling Register-ScheduledTask.
#>
param(
    [string]$TaskName = "GTKB-HarnessStormWatchdog",
    [Parameter(Mandatory=$true)]
    [string]$ProjectRoot,
    [int]$IntervalMinutes = 1,
    [string]$PythonExe = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
    Write-Error "ProjectRoot does not exist or is not a directory: $ProjectRoot"
    exit 1
}

$launcherPath = Join-Path -Path $ProjectRoot -ChildPath "scripts\ops\harness_storm_watchdog_launcher.py"
if (-not $DryRun -and -not (Test-Path -LiteralPath $launcherPath -PathType Leaf)) {
    Write-Error "Storm-watchdog launcher not found at $launcherPath"
    exit 1
}

if ([string]::IsNullOrEmpty($PythonExe)) {
    $venvPythonw = Join-Path -Path $ProjectRoot -ChildPath "groundtruth-kb\.venv\Scripts\pythonw.exe"
    if (Test-Path -LiteralPath $venvPythonw -PathType Leaf) {
        $PythonExe = $venvPythonw
    } else {
        $PythonExe = "pythonw.exe"
    }
}

$argString = "`"$launcherPath`""

if ($DryRun) {
    Write-Output "WOULD REGISTER TaskName=$TaskName Execute=$PythonExe Arguments=$argString"
    exit 0
}

$action = New-ScheduledTaskAction -Execute $PythonExe -Argument $argString -WorkingDirectory $ProjectRoot

$startTime = (Get-Date).AddSeconds(60)
$trigger = New-ScheduledTaskTrigger -Once -At $startTime `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes)
$trigger.Repetition.Duration = ""

$settings = New-ScheduledTaskSettingsSet -Hidden `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Limited `
    -Description "GroundTruth-KB harness storm watchdog. Hidden pythonw.exe launcher for liveness-aware dispatch-process reaping." | Out-Null

Enable-ScheduledTask -TaskName $TaskName | Out-Null

Write-Output "Registered TaskName=$TaskName IntervalMinutes=$IntervalMinutes Execute=$PythonExe LauncherPath=$launcherPath Enabled=True"
