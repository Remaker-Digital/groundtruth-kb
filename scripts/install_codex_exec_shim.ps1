param(
  [string]$TargetDir = "$env:LOCALAPPDATA\OpenAI\Codex\bin",
  [switch]$UpdateUserPath = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-LatestCodexPackage {
  $packages = Get-AppxPackage OpenAI.Codex | Sort-Object Version -Descending
  if (-not $packages) {
    throw "OpenAI.Codex package is not installed."
  }
  return $packages | Select-Object -First 1
}

function Set-UserPathPrepend([string]$PathEntry) {
  $current = [Environment]::GetEnvironmentVariable("Path", "User")
  $parts = @()
  if ($current) {
    $parts = $current.Split(";", [System.StringSplitOptions]::RemoveEmptyEntries)
  }

  $normalizedEntry = $PathEntry.TrimEnd("\")
  $filtered = @(
    $parts | Where-Object {
      $_.TrimEnd("\") -and $_.TrimEnd("\") -ne $normalizedEntry
    }
  )
  $updated = @($normalizedEntry) + $filtered
  [Environment]::SetEnvironmentVariable("Path", ($updated -join ";"), "User")
}

$package = Get-LatestCodexPackage
$resourceDir = Join-Path $package.InstallLocation "app\resources"
$files = @(
  "codex.exe",
  "codex-command-runner.exe",
  "rg.exe"
)

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

foreach ($name in $files) {
  $source = Join-Path $resourceDir $name
  if (-not (Test-Path $source)) {
    throw "Missing packaged resource: $source"
  }
  Copy-Item -LiteralPath $source -Destination (Join-Path $TargetDir $name) -Force
}

$manifest = [ordered]@{
  package_full_name = $package.PackageFullName
  install_location = $package.InstallLocation
  resource_dir = $resourceDir
  target_dir = $TargetDir
  copied_at = (Get-Date).ToString("o")
  files = $files
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $TargetDir "shim-manifest.json") -Encoding UTF8

if ($UpdateUserPath) {
  Set-UserPathPrepend -PathEntry $TargetDir
}

Write-Output "INSTALLED:$TargetDir PACKAGE=$($package.PackageFullName)"
