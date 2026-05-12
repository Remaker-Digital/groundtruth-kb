# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
<#
.SYNOPSIS
    Register the GTKB-SingleHarnessBridgeDispatcher Windows scheduled task.

.DESCRIPTION
    Per IP-2 of bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md
    (Codex GO at -006): register a Windows Task Scheduler task that fires the
    single-harness bridge dispatcher on a fixed interval (default 5 minutes).

    Substrate constraint: DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 §
    Platform Bindings requires "a non-interactive Python invocation of the
    dispatcher script with CREATE_NO_WINDOW so it does not surface a console
    window". This installer satisfies that constraint via two
    mutually-reinforcing measures:

    1. ``pythonw.exe`` (Windows GUI-subsystem Python; does NOT allocate a
       console at process start) instead of ``python.exe``.
    2. ``New-ScheduledTaskSettingsSet -Hidden`` for defense-in-depth UI
       suppression at the Task Scheduler level.

    Idempotent: re-registering with the same -TaskName unregisters the prior
    instance first, then re-registers. -DryRun mode prints the rendered
    command line WITHOUT performing any Task Scheduler API call.

.PARAMETER TaskName
    The Task Scheduler task name. Default 'GTKB-SingleHarnessBridgeDispatcher'.
    Tests should pass a nonce-suffixed name (e.g.
    'GTKB-SingleHarnessBridgeDispatcher-Test-<uuid8>') to avoid mutating the
    production task.

.PARAMETER ProjectRoot
    The GT-KB project root directory. Required.

.PARAMETER IntervalMinutes
    The wake interval in minutes. Default 5.

.PARAMETER DryRun
    If set, print 'WOULD REGISTER TaskName=... Execute=... Arguments=...' to
    stdout and exit 0 WITHOUT calling Register-ScheduledTask.
#>
param(
    [string]$TaskName = "GTKB-SingleHarnessBridgeDispatcher",
    [Parameter(Mandatory=$true)]
    [string]$ProjectRoot,
    [int]$IntervalMinutes = 5,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Validate project root.
if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
    Write-Error "ProjectRoot does not exist or is not a directory: $ProjectRoot"
    exit 1
}
$scriptPath = Join-Path -Path $ProjectRoot -ChildPath "scripts\single_harness_bridge_dispatcher.py"
if (-not $DryRun -and -not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
    Write-Error "Dispatcher script not found at $scriptPath"
    exit 1
}

# F4 fix: pythonw.exe (GUI-subsystem; no console allocation).
$execName = "pythonw.exe"
$argString = "`"$scriptPath`" --project-root `"$ProjectRoot`""

if ($DryRun) {
    Write-Output "WOULD REGISTER TaskName=$TaskName Execute=$execName Arguments=$argString"
    exit 0
}

$action = New-ScheduledTaskAction -Execute $execName -Argument $argString -WorkingDirectory $ProjectRoot

# Repeating trigger: start now, repeat every $IntervalMinutes for indefinite duration.
$startTime = (Get-Date).AddSeconds(60)
$trigger = New-ScheduledTaskTrigger -Once -At $startTime `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes)
# Workaround for PowerShell's RepetitionDuration default (which can clamp to
# 1 day): force an effectively-infinite duration.
$trigger.Repetition.Duration = ""

# F4 fix: Hidden=$true at Task Scheduler level (defense-in-depth UI suppression).
$settings = New-ScheduledTaskSettingsSet -Hidden `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

# Idempotent registration: unregister then register.
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Limited `
    -Description "GroundTruth-KB single-harness bridge dispatcher (Slice 2 of gtkb-single-harness-bridge-dispatcher-slice-2; SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 + DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001)." | Out-Null

Write-Output "Registered TaskName=$TaskName IntervalMinutes=$IntervalMinutes Execute=$execName ScriptPath=$scriptPath"
