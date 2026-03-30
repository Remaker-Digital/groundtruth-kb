param(
  [ValidateSet("codex", "prime")]
  [string]$Agent = "codex"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$taskName = "AgentRedBridgeResidentWorker-$Agent"
& schtasks.exe /Delete /TN $taskName /F | Out-Host
Write-Output "DELETED:$taskName"
