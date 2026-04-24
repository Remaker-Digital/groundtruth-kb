param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$InstallRoot = "",
    [string]$Version = "",
    [switch]$SkipDownload,
    [switch]$SkipPluginInstall
)

$ErrorActionPreference = "Stop"

if (-not $InstallRoot) {
    $InstallRoot = Join-Path $ProjectRoot "tools\grafana"
}

$InstallRoot = [System.IO.Path]::GetFullPath($InstallRoot)
$RuntimeRoot = Join-Path $ProjectRoot "memory\grafana"
$PluginsDir = Join-Path $RuntimeRoot "plugins"
New-Item -ItemType Directory -Path $InstallRoot, $RuntimeRoot, $PluginsDir -Force | Out-Null

if (-not $Version) {
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/grafana/grafana/releases/latest" -Headers @{ "User-Agent" = "gtkb-dashboard-installer" }
    $Version = [string]$release.tag_name
    $Version = $Version.TrimStart("v")
}

$ArchivePath = Join-Path $InstallRoot "grafana-$Version.windows-amd64.zip"

function Find-GrafanaHome {
    param([string]$Root, [string]$Version)
    $preferred = Join-Path $Root "grafana-v$Version"
    $candidates = @()
    if (Test-Path -LiteralPath $preferred) {
        $candidates += Get-Item -LiteralPath $preferred
    }
    $candidates += Get-ChildItem -LiteralPath $Root -Directory | Where-Object { $_.Name -like "grafana*$Version*" }
    foreach ($candidate in $candidates) {
        $grafanaExe = Join-Path $candidate.FullName "bin\grafana.exe"
        $grafanaServer = Join-Path $candidate.FullName "bin\grafana-server.exe"
        $defaults = Join-Path $candidate.FullName "conf\defaults.ini"
        if ((Test-Path -LiteralPath $defaults) -and ((Test-Path -LiteralPath $grafanaExe) -or (Test-Path -LiteralPath $grafanaServer))) {
            return $candidate.FullName
        }
    }
    return ""
}

$GrafanaHome = Find-GrafanaHome -Root $InstallRoot -Version $Version

if (-not $GrafanaHome) {
    if ($SkipDownload) {
        throw "Grafana $Version is not installed under $InstallRoot and -SkipDownload was provided."
    }
    $downloadUrl = "https://dl.grafana.com/oss/release/grafana-$Version.windows-amd64.zip"
    Write-Host "Downloading Grafana OSS $Version from $downloadUrl"
    if (-not (Test-Path -LiteralPath $ArchivePath)) {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $ArchivePath
    }
    Expand-Archive -LiteralPath $ArchivePath -DestinationPath $InstallRoot -Force
    $GrafanaHome = Find-GrafanaHome -Root $InstallRoot -Version $Version
    if (-not $GrafanaHome) {
        throw "Could not find extracted Grafana directory for version $Version under $InstallRoot."
    }
}

Set-Content -LiteralPath (Join-Path $InstallRoot "GRAFANA_HOME.txt") -Value $GrafanaHome -Encoding UTF8

if (-not $SkipPluginInstall) {
    $grafanaExe = Join-Path $GrafanaHome "bin\grafana.exe"
    $grafanaCliExe = Join-Path $GrafanaHome "bin\grafana-cli.exe"
    $env:GF_PATHS_PLUGINS = $PluginsDir
    if (Test-Path -LiteralPath $grafanaExe) {
        & $grafanaExe "cli" "--homepath" $GrafanaHome "--pluginsDir" $PluginsDir "plugins" "install" "frser-sqlite-datasource"
    } elseif (Test-Path -LiteralPath $grafanaCliExe) {
        & $grafanaCliExe "--homepath" $GrafanaHome "--pluginsDir" $PluginsDir "plugins" "install" "frser-sqlite-datasource"
    } else {
        throw "Could not find grafana.exe or grafana-cli.exe under $GrafanaHome\bin."
    }
}

Write-Host "Grafana home: $GrafanaHome"
Write-Host "Grafana plugins: $PluginsDir"
Write-Host "Next: .\scripts\gtkb_dashboard\start_local_dashboard.ps1"
