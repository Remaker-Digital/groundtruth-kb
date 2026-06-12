param(
    [int]$PollSeconds = 2
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Workspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$WatcherPath = Join-Path $PSScriptRoot "watch-bridge-scan.ps1"

if (-not (Test-Path -LiteralPath $WatcherPath)) {
    throw "Bridge scan watcher not found: $WatcherPath"
}

try {
    $Host.UI.RawUI.WindowTitle = "Agent Red Bridge Monitor"
} catch {
    # Non-fatal: some hosts do not expose RawUI title control.
}

Set-Location -LiteralPath $Workspace
Write-Host "Agent Red Bridge Monitor" -ForegroundColor Cyan
Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')"
Write-Host "Workspace: $Workspace"
Write-Host ""

& $WatcherPath -PollSeconds $PollSeconds
