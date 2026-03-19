# build-context.ps1 — Create ACR build context and trigger build with --no-logs
# Temporary helper for Windows ACR builds (avoids charmap crash)
param(
    [Parameter(Mandatory=$true)]
    [string]$Version
)

$PROJECT_ROOT = (Resolve-Path "$PSScriptRoot\..\..").Path
$ts = Get-Date -Format 'yyyyMMddHHmmss'
$ctx = "$env:TEMP\agentred-build-$ts"

Write-Host "Creating build context at $ctx..."
New-Item -ItemType Directory -Path $ctx -Force | Out-Null

# Copy required files
Copy-Item "$PROJECT_ROOT\Dockerfile" "$ctx\"
Copy-Item "$PROJECT_ROOT\requirements.txt" "$ctx\"
Copy-Item -Recurse "$PROJECT_ROOT\src" "$ctx\src"
Copy-Item -Recurse "$PROJECT_ROOT\config" "$ctx\config"

# Admin SPAs
foreach ($spa in @("standalone", "shopify", "provider")) {
    $distPath = "$PROJECT_ROOT\admin\$spa\dist"
    if (Test-Path $distPath) {
        New-Item -ItemType Directory -Path "$ctx\admin\$spa" -Force | Out-Null
        Copy-Item -Recurse $distPath "$ctx\admin\$spa\dist"
        Write-Host "  Copied admin/$spa/dist"
    } else {
        Write-Host "  WARNING: admin/$spa/dist missing"
    }
}

# Widget
if (Test-Path "$PROJECT_ROOT\widget\dist") {
    New-Item -ItemType Directory -Path "$ctx\widget" -Force | Out-Null
    Copy-Item -Recurse "$PROJECT_ROOT\widget\dist" "$ctx\widget\dist"
    Write-Host "  Copied widget/dist"
}

# Docs site (Dockerfile COPY docs-site/docs/)
if (Test-Path "$PROJECT_ROOT\docs-site\docs") {
    New-Item -ItemType Directory -Path "$ctx\docs-site" -Force | Out-Null
    Copy-Item -Recurse "$PROJECT_ROOT\docs-site\docs" "$ctx\docs-site\docs"
    Write-Host "  Copied docs-site/docs"
} else {
    Write-Warning "docs-site/docs missing — build will fail"
}

# Verify critical files
$critical = @("src\main.py", "src\multi_tenant\cosmos_schema.py", "src\multi_tenant\auth.py", "Dockerfile", "requirements.txt")
foreach ($f in $critical) {
    if (-not (Test-Path "$ctx\$f")) {
        Write-Error "MISSING critical file: $f"
        exit 1
    }
}
Write-Host "Critical files verified ($($critical.Count) files)"

$size = [math]::Round((Get-ChildItem -Recurse $ctx | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
Write-Host "Build context: $size MB"

# Build on ACR with --no-logs to avoid Windows charmap crash
Write-Host ""
Write-Host "Building image: api-gateway:$Version on ACR..."
az acr build --registry acragentredeastus --image "api-gateway:$Version" --build-arg "BUILD_VERSION=$Version" --file "$ctx\Dockerfile" --no-logs $ctx

if ($LASTEXITCODE -ne 0) {
    Write-Error "az acr build command failed (exit code: $LASTEXITCODE)"
    exit 1
}

# Verify the image exists
Write-Host "Verifying image tag in ACR..."
$verifyTag = az acr repository show-tags --name acragentredeastus --repository api-gateway --query "[?@=='$Version']" -o tsv
if ($verifyTag -ne $Version) {
    Write-Error "Image tag $Version not found in ACR after build"
    exit 1
}

Write-Host ""
Write-Host "SUCCESS: api-gateway:$Version built and verified in ACR"
Write-Host "Run upgrade.ps1 -Version $Version -SkipBuild to deploy"

# Cleanup
Remove-Item -Recurse -Force $ctx
Write-Host "Build context cleaned up"
