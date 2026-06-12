Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Workspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$MonitorPath = Join-Path $PSScriptRoot "bridge-scan-monitor-window.ps1"
$LogDir = Join-Path $PSScriptRoot "logs"
$LogPath = Join-Path $LogDir "bridge-monitor-ensure.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-EnsureLog {
    param([string]$Message)
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    Add-Content -LiteralPath $LogPath -Value "$stamp $Message"
}

function Test-InteractiveCodexDesktopRunning {
    try {
        $processes = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
            $_.Name -ieq "Codex.exe" -and
            $_.CommandLine -match "\\app\\Codex\.exe" -and
            $_.CommandLine -notmatch "--type="
        })
        return ($processes.Count -gt 0)
    } catch {
        Write-EnsureLog "WARN: Codex desktop process check failed: $($_.Exception.Message)"
        return $false
    }
}

if (-not (Test-Path -LiteralPath $MonitorPath)) {
    throw "Bridge monitor window script not found: $MonitorPath"
}

if (-not (Test-InteractiveCodexDesktopRunning)) {
    Write-EnsureLog "paused: interactive Codex desktop process is not running; monitor will not be started"
    Write-Output "Bridge monitor paused: Codex desktop is not running."
    exit 0
}

$escapedName = [Regex]::Escape([System.IO.Path]::GetFileName($MonitorPath))
$existing = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -in @("powershell.exe", "pwsh.exe") -and
    $_.ProcessId -ne $PID -and
    $_.CommandLine -match $escapedName
})

if ($existing.Count -gt 0) {
    $pids = ($existing | ForEach-Object { $_.ProcessId }) -join ", "
    Write-EnsureLog "monitor already running; pid(s)=$pids"
    Write-Output "Bridge monitor already running; pid(s)=$pids"
    exit 0
}

Start-Process -FilePath "powershell.exe" -WorkingDirectory $Workspace -ArgumentList @(
    "-NoLogo",
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    "`"$MonitorPath`""
)

Write-EnsureLog "started visible bridge monitor"
Write-Output "Started visible bridge monitor."
