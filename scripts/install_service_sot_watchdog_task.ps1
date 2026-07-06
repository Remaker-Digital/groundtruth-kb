# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
<#
.SYNOPSIS
    Register the GTKB-ServiceSoTWatchdog Windows scheduled task.

.DESCRIPTION
    Registers the detection-only service/SoT watchdog runner as a hidden,
    repeating Windows scheduled task. The task runs through pythonw.exe so Task
    Scheduler does not allocate a visible console window.

.PARAMETER TaskName
    Task name. Default 'GTKB-ServiceSoTWatchdog'.

.PARAMETER ProjectRoot
    The GT-KB project root directory. Required.

.PARAMETER IntervalMinutes
    Watchdog wake interval in minutes. Default 5.

.PARAMETER PythonExe
    Python GUI-subsystem executable. Default: project venv pythonw.exe if
    present, else 'pythonw.exe' from PATH.

.PARAMETER DryRun
    If set, print the scheduled-task command and exit without registering.
#>
param(
    [string]$TaskName = "GTKB-ServiceSoTWatchdog",
    [Parameter(Mandatory=$true)]
    [string]$ProjectRoot,
    [int]$IntervalMinutes = 5,
    [string]$PythonExe = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
    Write-Error "ProjectRoot does not exist or is not a directory: $ProjectRoot"
    exit 1
}

$runnerPath = Join-Path -Path $ProjectRoot -ChildPath "scripts\gtkb_service_sot_watchdog.py"
if (-not $DryRun -and -not (Test-Path -LiteralPath $runnerPath -PathType Leaf)) {
    Write-Error "Service/SoT watchdog runner not found at $runnerPath"
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

$argString = "`"$runnerPath`" --project-root `"$ProjectRoot`""

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
    -Description "GroundTruth-KB detection-only service and SoT availability watchdog." | Out-Null

Enable-ScheduledTask -TaskName $TaskName | Out-Null

Write-Output "Registered TaskName=$TaskName IntervalMinutes=$IntervalMinutes Execute=$PythonExe RunnerPath=$runnerPath Enabled=True"

