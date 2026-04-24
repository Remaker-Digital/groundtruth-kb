param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$GrafanaHome = "",
    [int]$GrafanaPort = 3000,
    [int]$RefreshPort = 8766,
    [int]$RefreshIntervalMinutes = 60
)

$ErrorActionPreference = "Stop"

function Import-EnvFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }
    foreach ($line in Get-Content -LiteralPath $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#") -or -not $trimmed.Contains("=")) {
            continue
        }
        $name, $value = $trimmed.Split("=", 2)
        if ($name -match "^[A-Za-z_][A-Za-z0-9_]*$") {
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

function Resolve-GrafanaHome {
    param([string]$ProjectRoot, [string]$RequestedHome)
    if ($RequestedHome) {
        return [System.IO.Path]::GetFullPath($RequestedHome)
    }
    if ($env:GRAFANA_HOME) {
        return [System.IO.Path]::GetFullPath($env:GRAFANA_HOME)
    }
    $recordPath = Join-Path $ProjectRoot "tools\grafana\GRAFANA_HOME.txt"
    if (Test-Path -LiteralPath $recordPath) {
        return (Get-Content -LiteralPath $recordPath -Raw).Trim()
    }
    $pathCommand = Get-Command grafana-server -ErrorAction SilentlyContinue
    if ($pathCommand) {
        return Split-Path (Split-Path $pathCommand.Source -Parent) -Parent
    }
    throw "Grafana is not installed for this project. Run .\scripts\gtkb_dashboard\install_local_grafana.ps1 first, or set GRAFANA_HOME."
}

function Join-ProcessArguments {
    param([string[]]$Arguments)
    $quoted = foreach ($argument in $Arguments) {
        if ($argument -match '[\s"]') {
            '"' + ($argument -replace '"', '\"') + '"'
        } else {
            $argument
        }
    }
    return ($quoted -join " ")
}

$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
Set-Location $ProjectRoot
Import-EnvFile -Path (Join-Path $ProjectRoot ".env.local")

$RuntimeRoot = Join-Path $ProjectRoot "memory\grafana"
$DataDir = Join-Path $RuntimeRoot "data"
$LogsDir = Join-Path $RuntimeRoot "logs"
$PluginsDir = Join-Path $RuntimeRoot "plugins"
$PidDir = Join-Path $RuntimeRoot "pids"
$DashboardDb = Join-Path $ProjectRoot "memory\gtkb-dashboard.sqlite"
$ProvisioningDir = Join-Path $ProjectRoot "docs\gtkb-dashboard\grafana\provisioning"
$DashboardsDir = Join-Path $ProjectRoot "docs\gtkb-dashboard\grafana\dashboards"
$DashboardJson = Join-Path $ProjectRoot "docs\gtkb-dashboard\grafana\dashboards\gtkb-dashboard.json"

New-Item -ItemType Directory -Path $DataDir, $LogsDir, $PluginsDir, $PidDir, (Split-Path $DashboardDb -Parent) -Force | Out-Null

$env:GTKB_DASHBOARD_DB = $DashboardDb
$env:GTKB_DASHBOARD_SQLITE_PATH = $DashboardDb
$env:GTKB_DASHBOARD_DASHBOARDS_PATH = $DashboardsDir
$env:GTKB_DASHBOARD_PROJECT_ROOT = $ProjectRoot
$env:GTKB_DASHBOARD_REFRESH_PORT = [string]$RefreshPort
$env:GTKB_DASHBOARD_REFRESH_INTERVAL_MINUTES = [string]$RefreshIntervalMinutes
$env:GF_PATHS_DATA = $DataDir
$env:GF_PATHS_LOGS = $LogsDir
$env:GF_PATHS_PLUGINS = $PluginsDir
$env:GF_PATHS_PROVISIONING = $ProvisioningDir
$env:GF_AUTH_ANONYMOUS_ENABLED = "true"
$env:GF_AUTH_ANONYMOUS_ORG_ROLE = "Viewer"
$env:GF_SECURITY_ADMIN_USER = "admin"
$env:GF_SECURITY_ADMIN_PASSWORD = "admin"
$env:GF_USERS_DEFAULT_THEME = "light"
$env:GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH = $DashboardJson

$GrafanaHome = Resolve-GrafanaHome -ProjectRoot $ProjectRoot -RequestedHome $GrafanaHome
$grafanaServer = Join-Path $GrafanaHome "bin\grafana-server.exe"
$grafanaExe = Join-Path $GrafanaHome "bin\grafana.exe"
if (Test-Path -LiteralPath $grafanaServer) {
    $grafanaFile = $grafanaServer
    $grafanaArgs = @(
        "--homepath", $GrafanaHome,
        "cfg:server.http_port=$GrafanaPort",
        "cfg:default.paths.data=$DataDir",
        "cfg:default.paths.logs=$LogsDir",
        "cfg:default.paths.plugins=$PluginsDir",
        "cfg:default.paths.provisioning=$ProvisioningDir",
        "cfg:dashboards.default_home_dashboard_path=$DashboardJson"
    )
} elseif (Test-Path -LiteralPath $grafanaExe) {
    $grafanaFile = $grafanaExe
    $grafanaArgs = @(
        "server",
        "--homepath", $GrafanaHome,
        "cfg:server.http_port=$GrafanaPort",
        "cfg:default.paths.data=$DataDir",
        "cfg:default.paths.logs=$LogsDir",
        "cfg:default.paths.plugins=$PluginsDir",
        "cfg:default.paths.provisioning=$ProvisioningDir",
        "cfg:dashboards.default_home_dashboard_path=$DashboardJson"
    )
} else {
    throw "Could not find grafana-server.exe or grafana.exe under $GrafanaHome\bin."
}

python (Join-Path $ProjectRoot "scripts\gtkb_dashboard\refresh_dashboard_db.py") --db-path $DashboardDb --project-root $ProjectRoot

$refreshLog = Join-Path $LogsDir "refresh-service.log"
$refreshErr = Join-Path $LogsDir "refresh-service.err.log"
$refreshProcess = Start-Process -FilePath "python" `
    -ArgumentList (Join-ProcessArguments @((Join-Path $ProjectRoot "scripts\gtkb_dashboard\refresh_service.py"))) `
    -WorkingDirectory $ProjectRoot `
    -RedirectStandardOutput $refreshLog `
    -RedirectStandardError $refreshErr `
    -WindowStyle Hidden `
    -PassThru
Set-Content -LiteralPath (Join-Path $PidDir "refresh-service.pid") -Value $refreshProcess.Id -Encoding UTF8

$grafanaLog = Join-Path $LogsDir "grafana.log"
$grafanaErr = Join-Path $LogsDir "grafana.err.log"
$grafanaProcess = Start-Process -FilePath $grafanaFile `
    -ArgumentList (Join-ProcessArguments $grafanaArgs) `
    -WorkingDirectory $GrafanaHome `
    -RedirectStandardOutput $grafanaLog `
    -RedirectStandardError $grafanaErr `
    -WindowStyle Hidden `
    -PassThru
Set-Content -LiteralPath (Join-Path $PidDir "grafana.pid") -Value $grafanaProcess.Id -Encoding UTF8

Write-Host "Grafana dashboard: http://127.0.0.1:$GrafanaPort/"
Write-Host "Refresh control:   http://127.0.0.1:$RefreshPort/"
Write-Host "SQLite database:   $DashboardDb"
Write-Host "Grafana logs:      $grafanaLog"
