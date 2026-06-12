Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Workspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$WatcherPath = Join-Path $PSScriptRoot "watch-bridge-scan.ps1"

if (-not (Test-Path -LiteralPath $WatcherPath)) {
    throw "Bridge scan watcher not found: $WatcherPath"
}

Start-Process -FilePath "powershell.exe" -WorkingDirectory $Workspace -ArgumentList @(
    "-NoLogo",
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    "`"$WatcherPath`""
)
