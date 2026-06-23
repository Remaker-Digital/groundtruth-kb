# build-and-deploy-staging.ps1 — Build ACR images and deploy to staging
#
# Builds one or both container images (api-gateway, test-host) and optionally
# deploys them to the staging Azure Container App environment.
#
# Usage:
#   # Build and deploy API gateway only:
#   .\build-and-deploy-staging.ps1 -Version v1.95.2 -Target api
#
#   # Build and deploy test host only:
#   .\build-and-deploy-staging.ps1 -Version v1.3.0 -Target testhost
#
#   # Build and deploy both:
#   .\build-and-deploy-staging.ps1 -ApiVersion v1.95.2 -TestHostVersion v1.3.0 -Target both
#
#   # Build only (no deploy):
#   .\build-and-deploy-staging.ps1 -Version v1.95.2 -Target api -SkipDeploy
#
#   # Deploy only (image already in ACR):
#   .\build-and-deploy-staging.ps1 -Version v1.95.2 -Target api -SkipBuild
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

param(
    [string]$Version,           # Shorthand: used for both api and testhost if individual versions not set
    [string]$ApiVersion,        # API gateway version (e.g., v1.95.2)
    [string]$TestHostVersion,   # Test host version (e.g., v1.3.0)

    [Parameter(Mandatory=$true)]
    [ValidateSet("api", "testhost", "both")]
    [string]$Target,

    [switch]$SkipBuild,
    [switch]$SkipDeploy,
    [switch]$DryRun
)

# ─── Resolve versions ────────────────────────────────────────────────────────
if ($Version -and -not $ApiVersion) { $ApiVersion = $Version }
if ($Version -and -not $TestHostVersion) { $TestHostVersion = $Version }

if ($Target -in @("api", "both") -and -not $ApiVersion -and -not $SkipBuild) {
    Write-Error "API gateway version required. Use -Version or -ApiVersion."
    exit 1
}
if ($Target -in @("testhost", "both") -and -not $TestHostVersion -and -not $SkipBuild) {
    Write-Error "Test host version required. Use -Version or -TestHostVersion."
    exit 1
}

# ─── Configuration ────────────────────────────────────────────────────────────
$ACR = "acragentredeastus"
$ACR_LOGIN_SERVER = "acragentredeastus.azurecr.io"
$RESOURCE_GROUP = "Agent-Red"

$API_CONTAINER_APP = "agent-red-staging"
$API_IMAGE_NAME = "api-gateway"

$TESTHOST_CONTAINER_APP = "agent-red-test-host"
$TESTHOST_IMAGE_NAME = "test-host"

$PROJECT_ROOT = (Resolve-Path "$PSScriptRoot\..\..").Path

$STAGING_URL = "https://agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io"

# ─── Logging ──────────────────────────────────────────────────────────────────
function Log {
    param([string]$Level, [string]$Message)
    $ts = Get-Date -Format "HH:mm:ss"
    $color = switch($Level) {
        "OK"    { "Green" }
        "WARN"  { "Yellow" }
        "ERR"   { "Red" }
        "PHASE" { "Magenta" }
        default { "Cyan" }
    }
    Write-Host "[$ts] [$Level] $Message" -ForegroundColor $color
}

# ─── Build context helper ─────────────────────────────────────────────────────
function New-BuildContext {
    param(
        [string]$ContextDir,
        [string]$DockerfileName,  # "Dockerfile" or "Dockerfile.test"
        [switch]$IncludeTests     # Include tests/, scripts/, test_host/, pyproject.toml
    )

    New-Item -ItemType Directory -Path $ContextDir -Force | Out-Null

    # Dockerfile (always renamed to "Dockerfile" in context for ACR)
    Copy-Item "$PROJECT_ROOT\$DockerfileName" "$ContextDir\Dockerfile"

    # Core dependencies
    Copy-Item "$PROJECT_ROOT\requirements.txt" "$ContextDir\"
    Copy-Item -Recurse "$PROJECT_ROOT\src" "$ContextDir\src"
    Copy-Item -Recurse "$PROJECT_ROOT\config" "$ContextDir\config"

    if ($IncludeTests) {
        Copy-Item "$PROJECT_ROOT\requirements-test.txt" "$ContextDir\"
        Copy-Item "$PROJECT_ROOT\pyproject.toml" "$ContextDir\"
        Copy-Item -Recurse "$PROJECT_ROOT\tests" "$ContextDir\tests"
        Copy-Item -Recurse "$PROJECT_ROOT\scripts" "$ContextDir\scripts"
        Copy-Item -Recurse "$PROJECT_ROOT\test_host" "$ContextDir\test_host"
    }

    # Admin SPAs (pre-built dist only)
    foreach ($spa in @("standalone", "shopify", "provider")) {
        $distPath = "$PROJECT_ROOT\admin\$spa\dist"
        if (Test-Path $distPath) {
            New-Item -ItemType Directory -Path "$ContextDir\admin\$spa" -Force | Out-Null
            Copy-Item -Recurse $distPath "$ContextDir\admin\$spa\dist"
            Log "INFO" "  + admin/$spa/dist"
        } else {
            Log "WARN" "  - admin/$spa/dist MISSING"
        }
    }

    # Widget bundle
    if (Test-Path "$PROJECT_ROOT\widget\dist") {
        New-Item -ItemType Directory -Path "$ContextDir\widget" -Force | Out-Null
        Copy-Item -Recurse "$PROJECT_ROOT\widget\dist" "$ContextDir\widget\dist"
        Log "INFO" "  + widget/dist"
    }

    # Docs site (API gateway Dockerfile serves /docs from built Docusaurus output)
    if (Test-Path "$PROJECT_ROOT\docs-site\docs") {
        New-Item -ItemType Directory -Path "$ContextDir\docs-site" -Force | Out-Null
        Copy-Item -Recurse "$PROJECT_ROOT\docs-site\docs" "$ContextDir\docs-site\docs"
        Log "INFO" "  + docs-site/docs"
    } else {
        Log "WARN" "  - docs-site/docs MISSING (will break API gateway build)"
    }

    $size = [math]::Round(
        (Get-ChildItem -Recurse $ContextDir | Measure-Object -Property Length -Sum).Sum / 1MB, 1
    )
    Log "INFO" "Build context: $size MB"
}

function Remove-BuildContext {
    param([string]$ContextDir)
    if (Test-Path $ContextDir) {
        # Use cmd /c rd for cleanup (avoids PowerShell Remove-Item -Recurse issues)
        cmd /c "rd /s /q `"$ContextDir`"" 2>$null
    }
}

# ─── ACR build + verify ───────────────────────────────────────────────────────
function Invoke-AcrBuild {
    param(
        [string]$ImageName,
        [string]$ImageVersion,
        [string]$ContextDir
    )

    Log "INFO" "Building $ImageName`:$ImageVersion on ACR..."

    if ($DryRun) {
        Log "INFO" "[DRY RUN] az acr build --registry $ACR --image ${ImageName}:${ImageVersion} ..."
        return $true
    }

    # --no-logs avoids Windows charmap crash (© in Dockerfile LABEL)
    az acr build `
        --registry $ACR `
        --image "${ImageName}:${ImageVersion}" `
        --build-arg "BUILD_VERSION=$ImageVersion" `
        --file "$ContextDir\Dockerfile" `
        --no-logs `
        $ContextDir

    if ($LASTEXITCODE -ne 0) {
        Log "ERR" "az acr build command failed (exit $LASTEXITCODE)"
        return $false
    }

    # Verify image tag exists (--no-logs means we can't see build output)
    Log "INFO" "Verifying image tag in ACR..."
    # Wait a few seconds for tag propagation
    Start-Sleep -Seconds 5

    $maxAttempts = 3
    for ($i = 1; $i -le $maxAttempts; $i++) {
        $tag = az acr repository show-tags `
            --name $ACR `
            --repository $ImageName `
            --query "[?@=='$ImageVersion']" -o tsv 2>&1

        if ($tag -eq $ImageVersion) {
            Log "OK" "$ImageName`:$ImageVersion verified in ACR"
            return $true
        }
        if ($i -lt $maxAttempts) {
            Log "WARN" "Tag not found yet, retrying ($i/$maxAttempts)..."
            Start-Sleep -Seconds 5
        }
    }

    Log "ERR" "Image tag $ImageVersion not found in ACR after $maxAttempts attempts"
    return $false
}

# ─── Deploy to staging ────────────────────────────────────────────────────────
function Deploy-ToStaging {
    param(
        [string]$ContainerApp,
        [string]$ImageName,
        [string]$ImageVersion,
        [hashtable]$EnvVars = @{}
    )

    $image = "${ACR_LOGIN_SERVER}/${ImageName}:${ImageVersion}"
    Log "INFO" "Deploying $image to $ContainerApp..."

    if ($DryRun) {
        Log "INFO" "[DRY RUN] az containerapp update --name $ContainerApp --image $image"
        return $true
    }

    # Build env var args if any
    $envArgs = @()
    if ($EnvVars.Count -gt 0) {
        $envPairs = ($EnvVars.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join " "
        $envArgs = @("--set-env-vars", $envPairs)
    }

    $updateArgs = @(
        "containerapp", "update",
        "--name", $ContainerApp,
        "--resource-group", $RESOURCE_GROUP,
        "--image", $image
    ) + $envArgs

    az @updateArgs 2>&1 | Out-Null

    if ($LASTEXITCODE -ne 0) {
        Log "ERR" "Deploy failed for $ContainerApp"
        return $false
    }

    Log "OK" "Deployed $image to $ContainerApp"
    return $true
}

function Test-StagingHealth {
    Log "INFO" "Waiting for staging health..."
    for ($i = 0; $i -lt 6; $i++) {
        Start-Sleep -Seconds 10
        try {
            $resp = Invoke-WebRequest -Uri "$STAGING_URL/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            if ($resp.StatusCode -eq 200) {
                Log "OK" "Staging /health returns 200 after $((($i + 1) * 10))s"
                # Check version header
                $ver = $resp.Headers["X-Product-Version"]
                if ($ver) { Log "INFO" "X-Product-Version: $ver" }
                return $true
            }
        } catch {}
        Log "INFO" "  Waiting... ($((($i + 1) * 10))s / 60s)"
    }
    Log "WARN" "Staging did not become healthy within 60s"
    return $false
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

Log "PHASE" "═══ Agent Red Staging Build & Deploy ═══"
Log "INFO" "Target: $Target | DryRun: $DryRun | SkipBuild: $SkipBuild | SkipDeploy: $SkipDeploy"

# ─── API Gateway ──────────────────────────────────────────────────────────────
if ($Target -in @("api", "both")) {
    Log "PHASE" "─── API Gateway: $ApiVersion ───"

    if (-not $SkipBuild) {
        $ctx = "$env:TEMP\agentred-api-build-$(Get-Date -Format 'yyyyMMddHHmmss')"
        Log "INFO" "Creating build context..."
        New-BuildContext -ContextDir $ctx -DockerfileName "Dockerfile"

        $ok = Invoke-AcrBuild -ImageName $API_IMAGE_NAME -ImageVersion $ApiVersion -ContextDir $ctx
        Remove-BuildContext $ctx

        if (-not $ok) {
            Write-Error "API gateway build failed"
            exit 1
        }
    } else {
        Log "WARN" "Skipping API gateway build (--SkipBuild)"
    }

    if (-not $SkipDeploy) {
        $envVars = @{
            "DISABLE_RATE_LIMITING" = "true"
        }
        $ok = Deploy-ToStaging -ContainerApp $API_CONTAINER_APP `
            -ImageName $API_IMAGE_NAME -ImageVersion $ApiVersion `
            -EnvVars $envVars
        if (-not $ok) {
            Write-Error "API gateway deploy failed"
            exit 1
        }
        Test-StagingHealth | Out-Null
    }
}

# ─── Test Host ────────────────────────────────────────────────────────────────
if ($Target -in @("testhost", "both")) {
    Log "PHASE" "─── Test Host: $TestHostVersion ───"

    if (-not $SkipBuild) {
        $ctx = "$env:TEMP\agentred-testhost-build-$(Get-Date -Format 'yyyyMMddHHmmss')"
        Log "INFO" "Creating build context..."
        New-BuildContext -ContextDir $ctx -DockerfileName "Dockerfile.test" -IncludeTests

        $ok = Invoke-AcrBuild -ImageName $TESTHOST_IMAGE_NAME -ImageVersion $TestHostVersion -ContextDir $ctx
        Remove-BuildContext $ctx

        if (-not $ok) {
            Write-Error "Test host build failed"
            exit 1
        }
    } else {
        Log "WARN" "Skipping test host build (--SkipBuild)"
    }

    if (-not $SkipDeploy) {
        $ok = Deploy-ToStaging -ContainerApp $TESTHOST_CONTAINER_APP `
            -ImageName $TESTHOST_IMAGE_NAME -ImageVersion $TestHostVersion
        if (-not $ok) {
            Write-Error "Test host deploy failed"
            exit 1
        }
    }
}

# ─── Summary ──────────────────────────────────────────────────────────────────
Log "PHASE" ""
Log "PHASE" "═══ Complete ═══"
if ($Target -in @("api", "both")) {
    Log "OK" "API Gateway: ${ACR_LOGIN_SERVER}/${API_IMAGE_NAME}:${ApiVersion}"
}
if ($Target -in @("testhost", "both")) {
    Log "OK" "Test Host:   ${ACR_LOGIN_SERVER}/${TESTHOST_IMAGE_NAME}:${TestHostVersion}"
}
Log "INFO" "Staging URL: $STAGING_URL"
