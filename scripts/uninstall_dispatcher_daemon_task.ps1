# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
<#
.SYNOPSIS
    Unregister the GTKB-DispatcherDaemon Windows scheduled-task supervisor (WI-4882).

.DESCRIPTION
    Removes the dispatcher-daemon supervisor task registered by
    install_dispatcher_daemon_task.ps1. Idempotent: no error if the task is
    already absent. -DryRun prints the intended action and makes no Task
    Scheduler call. This is the rollback path for the WI-4882 supervisor.

.PARAMETER TaskName
    Task name. Default 'GTKB-DispatcherDaemon'.

.PARAMETER DryRun
    If set, print 'WOULD UNREGISTER TaskName=...' and exit 0 without any Task
    Scheduler call.
#>
param(
    [string]$TaskName = "GTKB-DispatcherDaemon",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if ($DryRun) {
    Write-Output "WOULD UNREGISTER TaskName=$TaskName"
    exit 0
}

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Output "Unregistered TaskName=$TaskName"
} else {
    Write-Output "No scheduled task named $TaskName (already absent)"
}
