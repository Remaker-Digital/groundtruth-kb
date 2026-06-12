Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$LogDir = Join-Path $PSScriptRoot "logs"
$LogPath = Join-Path $LogDir "claude-token-handoff-repair.log"
$TokenPath = Join-Path $PSScriptRoot ".local\claude-oauth-token.txt"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-RepairLog {
    param([string]$Message)
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    Add-Content -LiteralPath $LogPath -Value "$stamp $Message"
}

function Get-ClaudeExe {
    $base = Join-Path $env:USERPROFILE "AppData\Roaming\Claude\claude-code"
    $latest = Get-ChildItem -LiteralPath $base -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^\d+\.\d+\.\d+$' } |
        Sort-Object { [version]$_.Name } -Descending |
        Select-Object -First 1

    if ($null -eq $latest) {
        throw "No claude-code version directory found under $base"
    }

    return (Join-Path $latest.FullName "claude.exe")
}

function Test-ClaudePrompt {
    param(
        [string]$ClaudeExe,
        [string]$Token
    )

    $oldToken = [Environment]::GetEnvironmentVariable("CLAUDE_CODE_OAUTH_TOKEN", "Process")
    $oldAnthropic = [Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "Process")

    try {
        if ($Token) {
            $env:CLAUDE_CODE_OAUTH_TOKEN = $Token
        } else {
            Remove-Item Env:\CLAUDE_CODE_OAUTH_TOKEN -ErrorAction SilentlyContinue
        }
        Remove-Item Env:\ANTHROPIC_API_KEY -ErrorAction SilentlyContinue

        $output = & $ClaudeExe -p --output-format json "Reply exactly: bridge-auth-ok" 2>&1 | Out-String
        return ($output -match '"is_error"\s*:\s*false' -and $output -match "bridge-auth-ok")
    } finally {
        if ($oldToken) {
            $env:CLAUDE_CODE_OAUTH_TOKEN = $oldToken
        } else {
            Remove-Item Env:\CLAUDE_CODE_OAUTH_TOKEN -ErrorAction SilentlyContinue
        }

        if ($oldAnthropic) {
            $env:ANTHROPIC_API_KEY = $oldAnthropic
        } else {
            Remove-Item Env:\ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
        }
    }
}

if (-not (Test-Path -LiteralPath $TokenPath)) {
    Write-RepairLog "handoff token absent; using Claude managed auth"
    exit 0
}

$token = (Get-Content -Raw -LiteralPath $TokenPath).Trim()
if (-not $token) {
    $stamp = Get-Date -Format "yyyyMMddTHHmmss"
    $backup = Join-Path (Split-Path -Parent $TokenPath) "claude-oauth-token.empty-$stamp.txt"
    Move-Item -LiteralPath $TokenPath -Destination $backup -Force
    Write-RepairLog "disabled empty handoff token: $backup"
    exit 0
}

$claudeExe = Get-ClaudeExe
$injectedWorks = Test-ClaudePrompt -ClaudeExe $claudeExe -Token $token
if ($injectedWorks) {
    Write-RepairLog "handoff token valid"
    exit 0
}

$managedWorks = Test-ClaudePrompt -ClaudeExe $claudeExe -Token ""
if (-not $managedWorks) {
    Write-RepairLog "handoff token invalid and managed auth also failed; leaving token file in place for operator diagnosis"
    exit 1
}

$stamp = Get-Date -Format "yyyyMMddTHHmmss"
$disabledPath = Join-Path (Split-Path -Parent $TokenPath) "claude-oauth-token.disabled-$stamp.txt"
Move-Item -LiteralPath $TokenPath -Destination $disabledPath -Force
Write-RepairLog "disabled invalid handoff token; managed auth works: $disabledPath"
