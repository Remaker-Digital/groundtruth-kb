# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
<#
.SYNOPSIS
    Unregister the GTKB-ServiceSoTWatchdog Windows scheduled task.
#>
param(
    [string]$TaskName = "GTKB-ServiceSoTWatchdog",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if ($DryRun) {
    Write-Output "WOULD UNREGISTER TaskName=$TaskName"
    exit 0
}

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false | Out-Null
    Write-Output "Unregistered TaskName=$TaskName"
} else {
    Write-Output "TaskName=$TaskName not registered"
}

