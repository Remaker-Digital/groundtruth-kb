# Build & Deploy to Staging/Production

**Type:** Repeatable Procedure (see `docs/operations/REPEATABLE-PROCEDURES.md`)
**Last verified:** 2026-02-25
**Last corrected:** 2026-02-25 — Initial creation after stale admin dist incident (S94)

---

## Canonical Production Approval Path (S251 OM-1, updated S271)

> **The canonical production deployment command is `scripts/deploy_pipeline.py --env production`.**
>
> `scripts/release_pipeline.py` now delegates to `deploy_pipeline.py` for all
> production deployments. Helper scripts (`deploy_orchestrator.py`, `deploy_ui.py`,
> `deploy.py`) are smoke tools for rapid staging iteration only. Their exit codes
> MUST NOT be used as the basis for production promotion decisions.

## Purpose

Builds all application artifacts, creates a container image, and deploys to the target environment. This procedure ensures **no stale or missing build artifacts** are packaged into the Docker image by enforcing verification gates after every build step.

This procedure is **build-focused** — it covers the artifact compilation and deployment steps that must succeed before upgrade verification (`upgrade-verification-procedure.md`) can begin.

---

## When to Execute

- Before any staging or production deployment.
- After any change to `src/`, `admin/`, or `widget/` source code.
- When the `scripts/deploy/upgrade.ps1` script is not being used (e.g., manual staging deploys).

---

## Variables

| Variable | Value |
|----------|-------|
| `TARGET_ENVIRONMENT` | **`staging`** or **`production`** |
| `NEW_VERSION` | Release candidate tag (e.g., `v1.58.1-rc3`) |
| `PROJECT_ROOT` | `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement` |
| `ACR_NAME` | `acragentredeastus` |
| `ACR_LOGIN_SERVER` | `acragentredeastus.azurecr.io` |
| `IMAGE_REPO` | `api-gateway` |

### Environment-Dependent Values

| Parameter | `staging` | `production` |
|-----------|-----------|--------------|
| `CONTAINER_APP` | `agent-red-staging` | `agent-red-api-gateway` |
| `RESOURCE_GROUP` | `Agent-Red` | `Agent-Red` |
| `TARGET_URL` | `https://agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` | `https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |

---

## Preconditions

```
[ ] Azure CLI authenticated              — az account show
[ ] ACR accessible                       — az acr show --name $ACR_NAME
[ ] Node.js 18+ available                — node --version
[ ] npm available                        — npm --version
[ ] Python 3.12+ available               — python --version
[ ] Working directory is $PROJECT_ROOT   — pwd
[ ] All tests passing                    — .\scripts\run-tests-thermal-safe.ps1 -SkipLive → OVERALL: PASS
[ ] No uncommitted src/ changes          — git diff --stat src/ admin/ widget/ → empty
```

**Rule:** If any precondition fails, the procedure does not start.

---

## Phase 0: Protected Behavior Regression Gate

**This phase runs BEFORE any build.** It verifies that all protected behaviors documented in `docs/PROTECTED-BEHAVIORS.md` still exist in the codebase. If any assertion fails, the build is BLOCKED until the regression is investigated and resolved.

### Step 0.1: Run Regression Assertions

```
ACTION:    Execute each grep assertion from PROTECTED-BEHAVIORS.md:

           grep -c "injectWidget" admin/standalone/layouts/StandaloneLayout.tsx        → ≥1  (PB-001)
           grep -c "icon-master.svg" admin/standalone/index.html                       → ≥1  (PB-002)
           grep -c "icon-master.svg" admin/provider/index.html                         → ≥1  (PB-003)
           grep -c "Save your configuration first" src/multi_tenant/activation_service.py → ≥2  (PB-010)
           grep -c "isProOrHigher" admin/standalone/pages/MemoryPrivacy.tsx             → ≥1  (PB-011)
           grep -c "send_team_invite_alert" src/multi_tenant/admin_team_api.py          → ≥1  (PB-020)
           grep -c "admin_url" src/multi_tenant/alert_delivery.py                      → ≥2  (PB-021)
           grep -c "resend-invite" src/multi_tenant/admin_team_api.py                  → ≥1  (PB-022)
           grep -c "find_superadmin_email" src/chat/pipeline/critic_escalation.py       → ≥1  (PB-023)
           grep -c "recipient_emails" src/multi_tenant/alert_delivery.py               → ≥3  (PB-023)
           grep -c "VITE_API_URL" docs/operations/build-deploy-procedure.md            → ≥1  (PB-030)

EXPECTED:  ALL assertions pass (counts meet or exceed thresholds).

ON FAIL:   STOP. Do not proceed to Phase 1.
           Identify which PB-NNN failed. Read the entry in PROTECTED-BEHAVIORS.md
           for context. A failed assertion means a protected behavior was removed —
           this is a regression that must be investigated before building.

           DO NOT fix by removing the assertion. Fix by restoring the behavior.
```

---

## Phase 1: Build Artifacts

All 4 build targets must be built fresh before every ACR build. **Do not skip any target**, even if you believe it hasn't changed — the Dockerfile copies whatever is on disk, and `.gitignore`'d dist directories may be stale from a prior session.

### Step 1.0: Clear Baked-In API URL

**This step prevents the admin SPAs from hardcoding a specific API endpoint.**

Vite bakes `import.meta.env.VITE_API_URL` into the JS bundle at build time. The local `.env.local` files contain the production FQDN (used for dev-server proxying), but Docker-deployed SPAs must use **same-origin relative URLs** so they auto-adapt to whatever host serves them.

```
ACTION:    For each admin SPA, write an empty VITE_API_URL override:
           echo "VITE_API_URL=" > $PROJECT_ROOT/admin/standalone/.env.local
           echo "VITE_API_URL=" > $PROJECT_ROOT/admin/shopify/.env.local
           echo "VITE_API_URL=" > $PROJECT_ROOT/admin/provider/.env.local

EXPECTED:  Each .env.local contains only "VITE_API_URL="

VERIFY:    cat $PROJECT_ROOT/admin/standalone/.env.local → "VITE_API_URL="

NOTE:      The prebuild hook (sync-admin-env.ps1) will overwrite these if you use
           `npm run build`. Steps 1.1–1.3 use `npx tsc && npx vite build` to bypass
           the sync hook. After Phase 1 completes, restore the original .env.local
           files by running: scripts/sync-admin-env.ps1
```

### Step 1.1: Build Standalone Admin SPA

```
ACTION:    cd $PROJECT_ROOT/admin/standalone && npx tsc && npx vite build
EXPECTED:  "✓ built in" message, exit code 0
VERIFY:    ls $PROJECT_ROOT/admin/standalone/dist/index.html
           ls $PROJECT_ROOT/admin/standalone/dist/assets/*.js
           grep -c "orangeglacier" $PROJECT_ROOT/admin/standalone/dist/assets/*.js → 0
ON FAIL:   Check for TypeScript or import errors. Fix before proceeding.
           If grep finds "orangeglacier", Step 1.0 was not applied — re-run it.
```

### Step 1.2: Build Shopify Admin SPA

```
ACTION:    cd $PROJECT_ROOT/admin/shopify && npx tsc && npx vite build
EXPECTED:  "✓ built in" message, exit code 0
VERIFY:    ls $PROJECT_ROOT/admin/shopify/dist/index.html
           ls $PROJECT_ROOT/admin/shopify/dist/assets/*.js
ON FAIL:   Check for TypeScript or import errors. Fix before proceeding.
```

### Step 1.3: Build Provider Admin SPA

```
ACTION:    cd $PROJECT_ROOT/admin/provider && npx tsc && npx vite build
EXPECTED:  "✓ built in" message, exit code 0
VERIFY:    ls $PROJECT_ROOT/admin/provider/dist/index.html
           ls $PROJECT_ROOT/admin/provider/dist/assets/*.js
ON FAIL:   Check for TypeScript or import errors. Fix before proceeding.
```

### Step 1.4: Build Widget Bundle

```
ACTION:    cd $PROJECT_ROOT/widget && npm run build
EXPECTED:  "✓ built in" message, exit code 0
VERIFY:    ls $PROJECT_ROOT/widget/dist/agent-red-widget.iife.js
ON FAIL:   Check for TypeScript or import errors. Fix before proceeding.
```

### Step 1.5: Build Freshness Gate

**This is the critical gate that prevents stale artifact deployment.**

```
ACTION:    Verify all 4 dist directories were modified within the last 5 minutes:
           stat $PROJECT_ROOT/admin/standalone/dist/index.html
           stat $PROJECT_ROOT/admin/shopify/dist/index.html
           stat $PROJECT_ROOT/admin/provider/dist/index.html
           stat $PROJECT_ROOT/widget/dist/agent-red-widget.iife.js

EXPECTED:  All 4 timestamps are within 5 minutes of the current time.

VERIFY:    PowerShell one-liner:
           @(
             "admin/standalone/dist/index.html",
             "admin/shopify/dist/index.html",
             "admin/provider/dist/index.html",
             "widget/dist/agent-red-widget.iife.js"
           ) | ForEach-Object {
             $f = Get-Item "$PROJECT_ROOT/$_"
             $age = (Get-Date) - $f.LastWriteTime
             if ($age.TotalMinutes -gt 5) {
               Write-Error "STALE: $_ is $($age.TotalMinutes.ToString('F0')) minutes old"
             } else {
               Write-Host "FRESH: $_ ($($age.TotalMinutes.ToString('F1')) min)" -ForegroundColor Green
             }
           }

ON FAIL:   Re-run the build step for the stale artifact. DO NOT proceed with a stale dist.
```

---

## Phase 2: ACR Build

### Step 2.1: Build Docker Image

```
ACTION:    cd $PROJECT_ROOT
           az acr build --registry $ACR_NAME --image $IMAGE_REPO:$NEW_VERSION --no-logs --file Dockerfile .
EXPECTED:  JSON output with "status": "Succeeded" and "provisioningState": "Succeeded"
VERIFY:    az acr task list-runs --registry $ACR_NAME --top 1 -o table
           Confirm run status is "Succeeded" and image tag matches $NEW_VERSION
ON FAIL:   Check ACR portal for build logs. Common issue: --no-logs hides errors.
           Run without --no-logs on Linux/WSL to see full output. On Windows, the
           charmap crash is cosmetic — check ACR run status to verify.
```

### Step 2.2: Verify Image in Registry

```
ACTION:    az acr repository show-tags --name $ACR_NAME --repository $IMAGE_REPO --orderby time_desc --top 3 -o table
EXPECTED:  $NEW_VERSION appears as the most recent tag
VERIFY:    Tag name matches exactly
ON FAIL:   If tag is missing, the build failed silently. Re-run Step 2.1.
```

---

## Phase 3: Deploy

### Step 3.1: Deploy to Target Environment

```
ACTION:    az containerapp update \
             --name $CONTAINER_APP \
             --resource-group $RESOURCE_GROUP \
             --image $ACR_LOGIN_SERVER/$IMAGE_REPO:$NEW_VERSION
EXPECTED:  JSON output with updated image reference
VERIFY:    az containerapp show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP \
             --query "properties.template.containers[0].image" -o tsv
           → Should show "$ACR_LOGIN_SERVER/$IMAGE_REPO:$NEW_VERSION"
ON FAIL:   Check Container App logs: az containerapp logs show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --tail 50

NOTE:      If redeploying the same tag (e.g., after rebuilding with fresh dists), add
           --set-env-vars "DEPLOY_TIMESTAMP=$(date +%s)" to force a new revision.
```

### Step 3.2: Wait for Startup

```
ACTION:    Wait 45-60 seconds for:
           - Container cold start (~10s if scaling from zero)
           - NATS connection initialization (~30-60s)
EXPECTED:  Health endpoint responds after wait period
VERIFY:    curl $TARGET_URL/health → {"status":"healthy","product_version":"..."}
ON FAIL:   If 404 after 90s:
           - Check container logs for startup errors
           - Verify image contains correct code: az containerapp logs show ...
           - Common cause: stale admin dist (see Phase 1 freshness gate)
```

---

## Phase 4: Post-Deploy Verification

### Step 4.1: Health Check

```
ACTION:    curl $TARGET_URL/health
EXPECTED:  HTTP 200, product_version matches the expected version from api_versioning.py
VERIFY:    JSON field "product_version" == expected value
ON FAIL:   If product_version is wrong, the old image may still be serving. Wait 30s and retry.
```

### Step 4.2: API Route Verification

```
ACTION:    curl -s -o /dev/null -w "%{http_code}" $TARGET_URL/api/status
EXPECTED:  HTTP 200 (public endpoint, no auth required)
VERIFY:    Status code is 200, not 404
ON FAIL:   If 404, the API routes are not loading. Check container logs for import errors.
           Common cause: stale admin dist causing SPA catch-all route to shadow API routes.
```

### Step 4.3: Admin SPA Verification

```
ACTION:    curl -s -o /dev/null -w "%{http_code}" $TARGET_URL/admin/standalone/
EXPECTED:  HTTP 200
VERIFY:    Status code is 200
ON FAIL:   Admin dist may not have been copied into the image. Verify Dockerfile COPY step.
```

### Step 4.4: Authenticated API Verification

```
ACTION:    curl -s -w "\nHTTP %{http_code}" $TARGET_URL/api/config -H "X-API-Key: $ADMIN_API_KEY"
EXPECTED:  HTTP 200 with tenant config JSON
VERIFY:    Response contains "tenant_id" field and status code is 200 (not 401, 404, or 500)
ON FAIL:   If 401: API key may be invalid or tenant not seeded. Verify key against Cosmos DB.
           If 404: Routes not registered — see Step 4.2 failure branch.
           If 500: Check container logs for runtime errors.
```

---

## Postconditions

```
[ ] Health returns 200 with correct product_version
[ ] /api/status returns 200
[ ] /admin/standalone/ returns 200
[ ] Authenticated admin API call returns 200
[ ] Container logs show no ERROR-level messages during startup
```

---

## Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| Stale admin dist → API routes return 404 | **Procedure defect** (S94, 2026-02-25) | Admin SPA JS bundles must be rebuilt before every ACR build. Phase 1 freshness gate catches this. Root cause: Dockerfile `COPY admin/*/dist/` picks up whatever is on disk. |
| `az acr build` UnicodeEncodeError on Windows | Environment (Windows encoding) | Use `--no-logs` flag. Build succeeds server-side. Verify via `az acr task list-runs`. |
| Same image tag doesn't trigger new revision | Environment (Container Apps behavior) | Add `--set-env-vars "DEPLOY_TIMESTAMP=..."` to force revision update when tag is reused. |
| Cold start timeout (scale-from-zero) | Environment transient | Staging min replicas = 0. First request after idle takes ~10s. NATS adds 30-60s. Wait 90s total before declaring failure. |
| Widget key validation fails after deploy | Environment transient | Cosmos DB data persists across deploys. If keys fail, verify tenant documents exist. May need re-seed. |
| `npm run build` fails with TypeScript errors | Procedure defect (if code compiles locally) | Ensure `node_modules` are installed. Run `npm install` in the failing admin dir. |

---

## Cross-Procedure Dependencies

- **Follows:** Unit Test Suite procedure (all tests must pass before building)
- **Precedes:** Non-Disruptive Upgrade Verification procedure (must deploy before verifying data integrity)
- **Precedes:** Production Regression Suite (must deploy before running live regression tests)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
