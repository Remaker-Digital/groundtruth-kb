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

$projectPythonw = Join-Path $ProjectRoot "groundtruth-kb\.venv\Scripts\pythonw.exe"
$pathPythonw = Get-Command pythonw.exe -ErrorAction SilentlyContinue
if (Test-Path $projectPythonw) {
    $pythonExe = $projectPythonw
}
elseif ($pathPythonw) {
    $pythonExe = $pathPythonw.Source
}
else {
    $pythonExe = (Get-Command python.exe -ErrorAction Stop).Source
}

$scriptBody = @"
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(r'$ProjectRoot') / 'groundtruth-kb' / 'src'))
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db_snapshot import create_snapshot
cfg = GTConfig.load(config_path=pathlib.Path(r'$ProjectRoot') / 'groundtruth.toml')
result = create_snapshot(cfg)
result_path = pathlib.Path(r'$ProjectRoot') / '.gtkb-state' / 'db-snapshot' / 'last-run.json'
result_path.write_text(json.dumps(result.to_json_dict(), indent=2) + '\n', encoding='utf-8')
"@

# WI-4512: the launcher is an active runtime dependency (the scheduled task
# executes it daily), so it must live in-root and survive Temp cleaning rather
# than under $env:TEMP. The snapshot OUTPUT path (%LOCALAPPDATA%\gtkb-snapshots)
# is governed by the separate DB-Snapshot Output Exception and is unchanged.
$launcherDir = Join-Path $ProjectRoot ".gtkb-state\db-snapshot"
$launcherScript = Join-Path $launcherDir "gtkb_db_snapshot_task.py"
New-Item -ItemType Directory -Force -Path $launcherDir | Out-Null
Set-Content -Path $launcherScript -Value $scriptBody -Encoding UTF8

$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument "`"$launcherScript`"" `
    -WorkingDirectory $ProjectRoot

$trigger = New-ScheduledTaskTrigger -Daily -At $Time

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopIfGoingOnBatteries `
    -AllowStartIfOnBatteries `
    -Hidden `
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
Write-Host "Script: $launcherScript"
Write-Host "Working directory: $ProjectRoot"
