# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
<#
.SYNOPSIS
    Unregister the GTKB-SingleHarnessBridgeDispatcher Windows scheduled task.

.DESCRIPTION
    Per IP-2 of bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md
    (Codex GO at -006): idempotent uninstall of the single-harness dispatcher
    scheduled task. Re-running on a non-existent task succeeds with an
    informational message. -DryRun mode prints the rendered intent without
    performing the unregister call.

.PARAMETER TaskName
    The Task Scheduler task name. Default 'GTKB-SingleHarnessBridgeDispatcher'.
    Tests should pass the same nonce-suffixed name used by the installer test.

.PARAMETER DryRun
    If set, print 'WOULD UNREGISTER TaskName=...' to stdout and exit 0
    WITHOUT calling Unregister-ScheduledTask.
#>
param(
    [string]$TaskName = "GTKB-SingleHarnessBridgeDispatcher",
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
    Write-Output "TaskName=$TaskName not registered; nothing to remove"
}
