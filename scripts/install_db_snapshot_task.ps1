<#
.SYNOPSIS
    Idempotent installer for the GTKB-DbSnapshot daily scheduled task.

.DESCRIPTION
    Creates or updates a Windows scheduled task that runs gt db snapshot
    daily at 03:00. The task invokes the Python API directly to avoid the
    CLI output-silence issue observed with `python -m groundtruth_kb.cli`.

    Re-running is safe: the task is unregistered first if it already exists.

.PARAMETER TaskName
    Name of the scheduled task (default: GTKB-DbSnapshot).

.PARAMETER Time
    Daily trigger time in HH:mm format (default: 03:00).

.PARAMETER ProjectRoot
    Path to the GT-KB project root (default: E:\GT-KB).

.EXAMPLE
    .\install_db_snapshot_task.ps1
    .\install_db_snapshot_task.ps1 -Time "04:30"
#>
[CmdletBinding()]
param(
    [string]$TaskName = "GTKB-DbSnapshot",
    [string]$Time = "03:00",
    [string]$ProjectRoot = "E:\GT-KB"
)

$ErrorActionPreference = "Stop"

$pythonExe = (Get-Command python -ErrorAction Stop).Source
$scriptBody = @"
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(r'$ProjectRoot') / 'groundtruth-kb' / 'src'))
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db_snapshot import create_snapshot
cfg = GTConfig.load(config_path=pathlib.Path(r'$ProjectRoot') / 'groundtruth.toml')
result = create_snapshot(cfg)
print(json.dumps(result.to_json_dict(), indent=2))
"@

$tempScript = Join-Path $env:TEMP "gtkb_db_snapshot_task.py"
Set-Content -Path $tempScript -Value $scriptBody -Encoding UTF8

$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument "`"$tempScript`"" `
    -WorkingDirectory $ProjectRoot

$trigger = New-ScheduledTaskTrigger -Daily -At $Time

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopIfGoingOnBatteries `
    -AllowStartIfOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task '$TaskName'."
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Daily GroundTruth-KB database snapshot (VACUUM INTO + integrity check + retention)." `
    | Out-Null

Write-Host "Scheduled task '$TaskName' registered: daily at $Time."
Write-Host "Python: $pythonExe"
Write-Host "Script: $tempScript"
Write-Host "Working directory: $ProjectRoot"
