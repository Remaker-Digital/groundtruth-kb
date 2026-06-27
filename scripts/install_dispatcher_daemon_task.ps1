# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
<#
.SYNOPSIS
    Register the GTKB-DispatcherDaemon Windows scheduled-task supervisor.

.DESCRIPTION
    Per DELIB-20266276 D3 (Daemon Resilience scope-lock): register a Windows
    Task Scheduler task that runs the idempotent ensure-alive entrypoint
    (scripts/ensure_dispatcher_daemon.py) on a fixed interval (default 1 minute).
    The ensure entrypoint no-ops when the daemon is alive and spawns a detached
    daemon when it is dead, so this supervisor keeps the daemon up unattended.

    Kept deliberately separate from the GTKB-HarnessStormWatchdog task so a
    watchdog defect cannot take down daemon supervision.

    Runs hidden via pythonw.exe (GUI-subsystem; no console window). Idempotent:
    re-registering with the same -TaskName unregisters the prior instance first.
    -DryRun prints the rendered command line WITHOUT any Task Scheduler call.

.PARAMETER TaskName
    Task name. Default 'GTKB-DispatcherDaemon'. Tests pass a nonce-suffixed name.

.PARAMETER ProjectRoot
    The GT-KB project root directory. Required.

.PARAMETER IntervalMinutes
    Supervisor wake interval in minutes. Default 1.

.PARAMETER DaemonTickSeconds
    Tick interval passed to a freshly-spawned daemon. Default 30.

.PARAMETER PythonExe
    Python (GUI-subsystem) executable. Default: the project venv pythonw.exe if
    present, else 'pythonw.exe' from PATH.

.PARAMETER DryRun
    If set, print 'WOULD REGISTER TaskName=... Execute=... Arguments=...' and exit
    0 WITHOUT calling Register-ScheduledTask.
#>
param(
    [string]$TaskName = "GTKB-DispatcherDaemon",
    [Parameter(Mandatory=$true)]
    [string]$ProjectRoot,
    [int]$IntervalMinutes = 1,
    [int]$DaemonTickSeconds = 30,
    [string]$PythonExe = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
    Write-Error "ProjectRoot does not exist or is not a directory: $ProjectRoot"
    exit 1
}

$scriptPath = Join-Path -Path $ProjectRoot -ChildPath "scripts\ensure_dispatcher_daemon.py"
if (-not $DryRun -and -not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
    Write-Error "Ensure-daemon script not found at $scriptPath"
    exit 1
}

# Resolve the interpreter: prefer the project venv pythonw.exe (has the deps);
# fall back to PATH pythonw.exe.
if ([string]::IsNullOrEmpty($PythonExe)) {
    $venvPythonw = Join-Path -Path $ProjectRoot -ChildPath "groundtruth-kb\.venv\Scripts\pythonw.exe"
    if (Test-Path -LiteralPath $venvPythonw -PathType Leaf) {
        $PythonExe = $venvPythonw
    } else {
        $PythonExe = "pythonw.exe"
    }
}

$argString = "`"$scriptPath`" --project-root `"$ProjectRoot`" --interval $DaemonTickSeconds"

if ($DryRun) {
    Write-Output "WOULD REGISTER TaskName=$TaskName Execute=$PythonExe Arguments=$argString"
    exit 0
}

$action = New-ScheduledTaskAction -Execute $PythonExe -Argument $argString -WorkingDirectory $ProjectRoot

$startTime = (Get-Date).AddSeconds(60)
$trigger = New-ScheduledTaskTrigger -Once -At $startTime `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes)
# Force an effectively-infinite repetition duration (PowerShell otherwise clamps).
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
    -Description "GroundTruth-KB dispatcher daemon supervisor (WI-4882; DELIB-20266276 D3). Idempotent ensure-alive keep-live." | Out-Null

Write-Output "Registered TaskName=$TaskName IntervalMinutes=$IntervalMinutes Execute=$PythonExe ScriptPath=$scriptPath"
