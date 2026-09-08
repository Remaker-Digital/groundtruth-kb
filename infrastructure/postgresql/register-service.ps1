#Requires -RunAsAdministrator
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Root
)

$ErrorActionPreference = 'Stop'
$resolvedRoot = (Resolve-Path -LiteralPath $Root).Path.TrimEnd('\')
$installation = Join-Path $resolvedRoot 'infrastructure\postgresql'
$release = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'release.json') -Raw | ConvertFrom-Json
$runtime = Join-Path $installation ('runtime\' + $release.build)
$dataDirectory = Join-Path $installation 'data'
$control = Join-Path $runtime 'bin\pg_ctl.exe'
$serviceName = 'gtkb-postgresql'

foreach ($target in @($runtime, $dataDirectory, (Join-Path $installation 'logs'), (Join-Path $installation 'wal'))) {
    $resolvedTarget = (Resolve-Path -LiteralPath $target).Path
    if (-not $resolvedTarget.StartsWith($resolvedRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'An installation path resolves outside the selected GT-KB root.'
    }
    if ((Get-Item -LiteralPath $target).Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw 'Service installation does not accept redirected target directories.'
    }
}
if (-not (Test-Path -LiteralPath $control -PathType Leaf)) { throw 'PostgreSQL runtime is not installed.' }
if (-not (Test-Path -LiteralPath (Join-Path $dataDirectory 'PG_VERSION') -PathType Leaf)) {
    throw 'PostgreSQL cluster is not initialized.'
}

$existing = Get-CimInstance Win32_Service -Filter "Name = '$serviceName'"
if ($existing) {
    if (-not $existing.PathName.Contains($control) -or -not $existing.PathName.Contains($dataDirectory)) {
        throw 'The existing service belongs to a different installation; refusing to change it.'
    }
    Set-Service -Name $serviceName -StartupType Automatic
    Start-Service -Name $serviceName
    Get-Service -Name $serviceName | Select-Object Name, Status, StartType
    return
}

# LocalService can run the server and archiver, but cannot read client/admin
# credential files. PostgreSQL itself authenticates from the protected cluster.
& icacls $runtime /grant '*S-1-5-19:(OI)(CI)RX' | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Could not grant runtime read access.' }
foreach ($directory in @($dataDirectory, (Join-Path $installation 'logs'), (Join-Path $installation 'wal'))) {
    & icacls $directory /grant '*S-1-5-19:(OI)(CI)M' | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Could not grant service data access.' }
}
& $control status -D $dataDirectory | Out-Null
if ($LASTEXITCODE -eq 0) {
    & $control stop -D $dataDirectory -m fast -w
    if ($LASTEXITCODE -ne 0) { throw 'Could not stop the operator-started instance.' }
} elseif ($LASTEXITCODE -ne 3) {
    throw 'Could not establish cluster process state.'
}
& $control register -N $serviceName -D $dataDirectory -U 'NT AUTHORITY\LocalService' -S auto
if ($LASTEXITCODE -ne 0) { throw 'Service registration failed; use the documented pg_ctl start command to restore operation.' }
Start-Service -Name $serviceName
Get-Service -Name $serviceName | Select-Object Name, Status, StartType
