<#
.SYNOPSIS
    Register both Prime and Codex bridge resident workers as Windows Scheduled Tasks.
    This is the canonical runtime bootstrap for the bridge autonomy system.

.DESCRIPTION
    Creates two logon-triggered scheduled tasks that keep both workers alive
    independently of any Claude/Codex interactive session. Workers restart
    automatically on failure (up to 999 times at 1-minute intervals).

    After registration, both tasks are started immediately.

    Bridge Autonomy Phase B (S259): scheduled tasks replace SessionStart hooks
    as the primary worker lifecycle.

.EXAMPLE
    .\register_bridge_runtime_tasks.ps1
    .\register_bridge_runtime_tasks.ps1 -Verify

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
#>

param(
  [switch]$Verify,
  [switch]$Unregister
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
$registerScript = Join-Path $scriptDir "register_bridge_resident_worker_task.ps1"

if (-not (Test-Path $registerScript)) {
  throw "Missing: $registerScript"
}

$agents = @("prime", "codex")

if ($Unregister) {
  foreach ($agent in $agents) {
    $taskName = "AgentRedBridgeResidentWorker-$agent"
    Write-Output "Unregistering $taskName..."
    & schtasks.exe /Delete /TN $taskName /F 2>&1 | Out-Null
    Write-Output "  Done."
  }
  Write-Output "Both tasks unregistered."
  return
}

if ($Verify) {
  $allHealthy = $true
  foreach ($agent in $agents) {
    $taskName = "AgentRedBridgeResidentWorker-$agent"
    $taskInfo = & schtasks.exe /Query /TN $taskName /FO CSV 2>&1
    if ($LASTEXITCODE -ne 0) {
      Write-Output "[FAIL] $taskName - not registered"
      $allHealthy = $false
      continue
    }
    Write-Output "[OK]   $taskName - registered"

    # Check health file
    $healthFile = Join-Path (Split-Path $scriptDir -Parent) ".claude\hooks\.bridge-worker-$agent-health.json"
    if (Test-Path $healthFile) {
      $health = Get-Content $healthFile | ConvertFrom-Json
      $status = $health.status
      $lastError = $health.last_error
      $lastPoll = $health.updated_at
      if ($status -eq "error") {
        Write-Output "       Health: ERROR - $lastError"
        $allHealthy = $false
      } else {
        Write-Output "       Health: $status (last poll: $lastPoll)"
      }
    } else {
      Write-Output "       Health: no health file yet"
    }
  }
  if ($allHealthy) {
    Write-Output "`nBridge runtime: HEALTHY"
  } else {
    Write-Output "`nBridge runtime: UNHEALTHY - see above"
  }
  return
}

# Register both agents
foreach ($agent in $agents) {
  Write-Output "Registering $agent worker..."
  & $registerScript -Agent $agent
  Write-Output ""
}

Write-Output "========================================"
Write-Output "Bridge runtime installed."
Write-Output ""
Write-Output "Tasks:"
foreach ($agent in $agents) {
  Write-Output "  AgentRedBridgeResidentWorker-$agent"
}
Write-Output ""
Write-Output "Verify: .\register_bridge_runtime_tasks.ps1 -Verify"
Write-Output "Remove: .\register_bridge_runtime_tasks.ps1 -Unregister"
Write-Output "========================================"
