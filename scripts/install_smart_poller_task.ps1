# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
# Install (or update) the GTKB-SmartBridgePoller Windows Scheduled Task.
#
# Per bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md GO
# (REVISED-1 at -003 §4.3): the task targets scripts/run_smart_bridge_poller.ps1
# (Phase-2-stable wrapper), NOT the runner script directly.
#
# This script is idempotent: re-running it updates the task definition
# without duplicating registrations. It also starts the task once installed.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install_smart_poller_task.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install_smart_poller_task.ps1 -IntervalSeconds 30
#
# To uninstall: scripts/uninstall_smart_poller_task.ps1

param(
    [string]$ProjectRoot = "E:\GT-KB",
    [int]$IntervalSeconds = 15
)

$ErrorActionPreference = "Stop"

$taskName = "GTKB-SmartBridgePoller"
$wrapperPath = Join-Path $ProjectRoot "scripts\run_smart_bridge_poller.ps1"
$vbsLauncherPath = Join-Path $ProjectRoot "scripts\run_smart_bridge_poller.vbs"

if (-not (Test-Path $wrapperPath)) {
    throw "Wrapper script not found at $wrapperPath. Did you run installation before commits 1-3 landed?"
}
if (-not (Test-Path $vbsLauncherPath)) {
    throw "VBS launcher not found at $vbsLauncherPath. Required to suppress visible PowerShell window on Windows 11 + Terminal."
}

# Per bridge/gtkb-bridge-poller-notify-activation-2026-04-29-006.md (reverification
# of activation): on Windows 11 with Windows Terminal as the default console host,
# `powershell.exe -WindowStyle Hidden` is NOT honored — Terminal renders the
# hosted PowerShell window visibly anyway. The fix is a VBS launcher invoked via
# wscript.exe (no console of its own) which spawns PowerShell with WshShell.Run
# intWindowStyle=0 (truly hidden). The .ps1 wrapper retains its -ValidateOnly mode
# for the doctor check.
$action = New-ScheduledTaskAction `
    -Execute "wscript.exe" `
    -Argument "`"$vbsLauncherPath`"" `
    -WorkingDirectory $ProjectRoot

$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings | Out-Null
    Write-Host "Smart-poller task '$taskName' updated (wrapper=$wrapperPath, interval=$IntervalSeconds s)."
} else {
    Register-ScheduledTask -TaskName $taskName `
        -Action $action -Trigger $trigger -Settings $settings -Principal $principal | Out-Null
    Write-Host "Smart-poller task '$taskName' registered (wrapper=$wrapperPath, interval=$IntervalSeconds s)."
}

Start-ScheduledTask -TaskName $taskName
Write-Host "Smart-poller task '$taskName' started."
