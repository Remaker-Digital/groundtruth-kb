param(
    [int]$PollSeconds = 2
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Workspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$LogDir = Join-Path $Workspace "independent-progress-assessments\bridge-automation\logs"
$Sources = @(
    [pscustomobject]@{
        Agent = "claude"
        Path  = Join-Path $LogDir "claude-scan-status.json"
    },
    [pscustomobject]@{
        Agent = "codex"
        Path  = Join-Path $LogDir "codex-scan-status.json"
    }
)
$LivenessPath = Join-Path $LogDir "poller-liveness-external.json"

function Get-StateColor {
    param([string]$State)

    switch ($State) {
        "error"     { return "Red" }
        "dead"      { return "Red" }
        "attention" { return "Yellow" }
        "running"   { return "Cyan" }
        "alive"     { return "Cyan" }
        "completed" { return "Green" }
        "ok"        { return "Green" }
        "skipped"   { return "DarkYellow" }
        "clear"     { return "DarkGray" }
        default     { return "Gray" }
    }
}

function Write-AgentStatus {
    param(
        [string]$Agent,
        [object]$Status
    )

    $state = [string]$Status.state
    $message = [string]$Status.message
    Write-Host ("{0}: {1} | {2}" -f $Agent, $state, $message) -ForegroundColor (Get-StateColor -State $state)
}

function Write-LivenessStatus {
    param([object]$Status)

    $state = [string]$Status.overallState
    $claudeVerdict = [string]$Status.claude.verdict
    $codexVerdict = [string]$Status.codex.verdict
    $message = "claude=$claudeVerdict codex=$codexVerdict"
    Write-Host ("liveness: {0} | {1}" -f $state, $message) -ForegroundColor (Get-StateColor -State $state)
}

Clear-Host
Write-Host "Agent Red bridge scan monitor" -ForegroundColor Cyan
Write-Host "Watching status files in: $LogDir"
Write-Host "Press Ctrl+C to stop."
Write-Host ""

$lastSeen = @{}

while ($true) {
    foreach ($source in $Sources) {
        if (-not (Test-Path -LiteralPath $source.Path)) {
            continue
        }

        try {
            $status = Get-Content -Raw -LiteralPath $source.Path | ConvertFrom-Json
            $stamp = [string]$status.updatedAtUtc
            $state = [string]$status.state
            $message = [string]$status.message
            $key = "$stamp|$state|$message"
            $agent = [string]$source.Agent
            if (-not $lastSeen.ContainsKey($agent) -or $lastSeen[$agent] -ne $key) {
                Write-AgentStatus -Agent $agent -Status $status
                $lastSeen[$agent] = $key
            }
        } catch {
            $agent = [string]$source.Agent
            $key = "parse-error|$($_.Exception.Message)"
            if (-not $lastSeen.ContainsKey($agent) -or $lastSeen[$agent] -ne $key) {
                Write-Host ("{0}: error | status file could not be parsed: {1}" -f $agent, $_.Exception.Message) -ForegroundColor Red
                $lastSeen[$agent] = $key
            }
        }
    }

    if (Test-Path -LiteralPath $LivenessPath) {
        try {
            $liveness = Get-Content -Raw -LiteralPath $LivenessPath | ConvertFrom-Json
            $stamp = [string]$liveness.updatedAtUtc
            $state = [string]$liveness.overallState
            $claudeVerdict = [string]$liveness.claude.verdict
            $codexVerdict = [string]$liveness.codex.verdict
            $key = "$stamp|$state|$claudeVerdict|$codexVerdict"
            if (-not $lastSeen.ContainsKey("liveness") -or $lastSeen["liveness"] -ne $key) {
                Write-LivenessStatus -Status $liveness
                $lastSeen["liveness"] = $key
            }
        } catch {
            $key = "parse-error|$($_.Exception.Message)"
            if (-not $lastSeen.ContainsKey("liveness") -or $lastSeen["liveness"] -ne $key) {
                Write-Host ("liveness: error | status file could not be parsed: {0}" -f $_.Exception.Message) -ForegroundColor Red
                $lastSeen["liveness"] = $key
            }
        }
    }

    Start-Sleep -Seconds $PollSeconds
}
