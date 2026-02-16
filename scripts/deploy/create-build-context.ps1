$stamp = Get-Date -Format 'yyyyMMddHHmmss'
$tmp = New-Item -ItemType Directory -Path (Join-Path $env:TEMP "agentred-build-$stamp") -Force
$root = "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"

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
