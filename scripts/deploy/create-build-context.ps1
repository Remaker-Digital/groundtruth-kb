# Per S307 hardcoded-path directive: discover repo root from this script's
# location, not from a hardcoded literal. This file is at scripts/deploy/, so
# `$PSScriptRoot/..\..` resolves to the repo root regardless of where the
# checkout lives. `Resolve-Path` normalizes the result.
$stamp = Get-Date -Format 'yyyyMMddHHmmss'
$tmp = New-Item -ItemType Directory -Path (Join-Path $env:TEMP "agentred-build-$stamp") -Force
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

Copy-Item "$root\Dockerfile" $tmp\
Copy-Item "$root\requirements.txt" $tmp\
Copy-Item -Recurse "$root\src" "$tmp\src"
Copy-Item -Recurse "$root\config" "$tmp\config"

New-Item -ItemType Directory -Path "$tmp\admin\standalone" -Force | Out-Null
Copy-Item -Recurse "$root\admin\standalone\dist" "$tmp\admin\standalone\dist"

New-Item -ItemType Directory -Path "$tmp\admin\shopify" -Force | Out-Null
Copy-Item -Recurse "$root\admin\shopify\dist" "$tmp\admin\shopify\dist"

New-Item -ItemType Directory -Path "$tmp\widget" -Force | Out-Null
Copy-Item -Recurse "$root\widget\dist" "$tmp\widget\dist"

Write-Output $tmp.FullName
