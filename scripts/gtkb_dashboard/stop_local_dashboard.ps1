param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

$PidDir = Join-Path $ProjectRoot "memory\grafana\pids"
foreach ($name in @("grafana", "refresh-service")) {
    $pidPath = Join-Path $PidDir "$name.pid"
    if (-not (Test-Path -LiteralPath $pidPath)) {
        continue
    }
    $processId = [int](Get-Content -LiteralPath $pidPath -Raw)
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $processId -Force
        Write-Host "Stopped $name process $processId"
    }
    Remove-Item -LiteralPath $pidPath -Force
}

Get-Process -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Path -and (
            $_.Path.StartsWith((Join-Path $ProjectRoot "tools\grafana"), [System.StringComparison]::OrdinalIgnoreCase) -or
            $_.Path.StartsWith((Join-Path $ProjectRoot "memory\grafana"), [System.StringComparison]::OrdinalIgnoreCase)
        )
    } |
    ForEach-Object {
        Stop-Process -Id $_.Id -Force
        Write-Host "Stopped Grafana child process $($_.Id) ($($_.ProcessName))"
    }
