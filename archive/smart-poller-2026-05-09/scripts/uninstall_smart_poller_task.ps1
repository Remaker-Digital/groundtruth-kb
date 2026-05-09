# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
# Uninstall the GTKB-SmartBridgePoller Windows Scheduled Task.
#
# Companion to install_smart_poller_task.ps1. Removes the OS task registration
# but does NOT delete .gtkb-state/bridge-poller/ contents (those are the
# audit/notification artifacts; preserve for diagnostic review).
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/uninstall_smart_poller_task.ps1

$ErrorActionPreference = "Stop"

$taskName = "GTKB-SmartBridgePoller"

if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Smart-poller task '$taskName' unregistered."
} else {
    Write-Host "Smart-poller task '$taskName' not found; nothing to uninstall."
}
