Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$taskName = "AgentRedCodexBridgeWake"
& schtasks.exe /Delete /TN $taskName /F | Out-Host
Write-Output "DELETED:$taskName"
