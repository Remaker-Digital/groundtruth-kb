# Pre-Flight Deployment Checklist

**Type:** Repeatable Procedure (see `docs/operations/REPEATABLE-PROCEDURES.md`)
**Last verified:** —
**Last corrected:** 2026-02-26 — Initial creation (S102)

---

## Purpose

Standard checklist executed for **every** production (or staging) deployment. Verifies source integrity, build correctness, post-deploy platform health, and — critically — that a new customer tenant can be provisioned, configured, and serve AI-powered conversations with zero defects.

Five phases execute in sequence. Any FAIL in Phases A–C blocks the deployment or triggers rollback. Phase D failures indicate the deployment is live but tenant provisioning is defective — no new customers should be onboarded until resolved.

**Automation:** `python scripts/pre_flight_checklist.py --env production --new-version X.Y.Z`

---

## Variables

| Variable | Value |
|----------|-------|
| `TARGET_ENVIRONMENT` | `staging` or `production` |
| `NEW_VERSION` | Expected product version (e.g., `1.59.1`) — must match `PRODUCT_VERSION` in `src/multi_tenant/api_versioning.py` |
| `PROJECT_ROOT` | `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement` |
| `ACR_NAME` | `acragentredeastus` |
| `ACR_LOGIN_SERVER` | `acragentredeastus.azurecr.io` |
| `IMAGE_REPO` | `api-gateway` |
| `RESOURCE_GROUP` | `Agent-Red` |

### Environment-Dependent Values

| Parameter | `staging` | `production` |
|-----------|-----------|--------------|
| `TARGET_FQDN` | `agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` | `agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |
| `CONTAINER_APP` | `agent-red-staging` | `agent-red-api-gateway` |

### Credentials (from `.env.local` — never hardcoded)

| Variable | Source |
|----------|--------|
| `SUPERADMIN_PREVIEW_API_KEY` | `.env.local` — SPA superadmin key for tenant provisioning |
| `PREVIEW_WIDGET_KEY` | `.env.local` — existing tenant widget key for Phase C |
| `AGENTRED_API_KEY` | `.env.local` — existing tenant admin key for regression tests |

---

## Preconditions

```
[ ] Azure CLI authenticated              — az account show
[ ] ACR accessible                       — az acr show --name acragentredeastus
[ ] Python 3.12+ available               — python --version
[ ] httpx installed (Phase D SSE)        — python -c "import httpx"
[ ] Node.js 18+ available                — node --version
[ ] npm available                        — npm --version
[ ] Target environment reachable         — curl https://$TARGET_FQDN/health → 200
[ ] SUPERADMIN_PREVIEW_API_KEY set       — grep SUPERADMIN_PREVIEW_API_KEY .env.local
[ ] PREVIEW_WIDGET_KEY set               — grep PREVIEW_WIDGET_KEY .env.local
[ ] AGENTRED_API_KEY set                 — grep AGENTRED_API_KEY .env.local
[ ] No uncommitted src/ changes          — git diff --stat src/ admin/ widget/ → empty
[ ] Results directory exists             — mkdir -p scripts/pre-flight-results/
```

**Rule:** If any precondition fails, the procedure does not start.

---

## Phase A — Pre-Build Verification

Source-level checks that run locally before any build or deploy.

### Step A.1: Version Bump Confirmed

- **Action:** `python -c "from src.multi_tenant.api_versioning import PRODUCT_VERSION; print(PRODUCT_VERSION)"`
- **Expected:** Output matches `$NEW_VERSION`
- **Verify:** String equality comparison
- **On Fail:** Update `src/multi_tenant/api_versioning.py` PRODUCT_VERSION. Do not build until it matches.

### Step A.2: Protected Behaviors Regression Gate

- **Action:** Execute all 11 `grep -c` assertions from `docs/PROTECTED-BEHAVIORS.md`:
  ```
  grep -c "injectWidget" admin/standalone/layouts/StandaloneLayout.tsx        ≥1  (PB-001)
  grep -c "icon-master.svg" admin/standalone/index.html                       ≥1  (PB-002)
  grep -c "icon-master.svg" admin/provider/index.html                         ≥1  (PB-003)
  grep -c "Save your configuration first" src/multi_tenant/activation_service.py ≥2  (PB-010)
  grep -c "isProOrHigher" admin/standalone/pages/MemoryPrivacy.tsx            ≥1  (PB-011)
  grep -c "send_team_invite_alert" src/multi_tenant/admin_team_api.py         ≥1  (PB-020)
  grep -c "admin_url" src/multi_tenant/alert_delivery.py                     ≥2  (PB-021)
  grep -c "resend-invite" src/multi_tenant/admin_team_api.py                  ≥1  (PB-022)
  grep -c "find_superadmin_email" src/chat/pipeline/critic_escalation.py      ≥1  (PB-023a)
  grep -c "recipient_emails" src/multi_tenant/alert_delivery.py              ≥3  (PB-023b)
  grep -c "VITE_API_URL" docs/operations/build-deploy-procedure.md           ≥1  (PB-030)
  ```
- **Expected:** All 11 assertions pass (count ≥ threshold)
- **Verify:** All grep exit codes 0 with counts meeting thresholds
- **On Fail:** STOP. A protected behavior has been removed. Restore it before building.

### Step A.3: No Uncommitted Changes

- **Action:** `git diff --stat src/ admin/ widget/`
- **Expected:** Empty output
- **Verify:** Exit code 0 with no output lines
- **On Fail:** Commit or stash changes. Do not deploy uncommitted code.

### Step A.4: Unit/Integration Tests Pass

- **Action:** `.\scripts\run-tests-thermal-safe.ps1 -Workers 4 -CoolDown 30 -SkipLive`
- **Expected:** `OVERALL: PASS`, 0 failures, pass count ≥ 4,500
- **Verify:** Exit code 0; stdout contains "OVERALL: PASS"
- **On Fail:** Fix failing tests. Do not proceed until 0 failures.

### Step A.5: TypeScript Lint

- **Action:** `cd admin && npx eslint --ext .tsx,.ts shared/ standalone/ provider/ shopify/ --max-warnings 50`
- **Expected:** Exit code 0, warnings ≤ 50
- **Verify:** Exit code 0
- **On Fail:** Fix TypeScript errors. Warnings ≤ 50 are acceptable.

---

## Phase B — Build & Deploy

Builds all artifacts, creates ACR image, deploys to target environment.

**Pre-Phase B:** Capture upgrade verification snapshot before deploying:
```
python scripts/upgrade_verification.py phase-a --env $TARGET_ENVIRONMENT
```

### Step B.1: Build All 4 Dist Directories

- **Action:** Clear `VITE_API_URL=` in each admin SPA `.env.local`, then build:
  ```
  cd admin/standalone && npx tsc && npx vite build
  cd admin/shopify && npx tsc && npx vite build
  cd admin/provider && npx tsc && npx vite build
  cd widget && npm run build
  ```
- **Expected:** All 4 produce fresh dist directories
- **Verify:** `grep -c "orangeglacier" admin/standalone/dist/assets/*.js` → 0 (no baked FQDN)
- **On Fail:** Fix build errors. Check that `VITE_API_URL` is empty.

### Step B.2: Artifact Freshness Gate

- **Action:** Check modification time of all 4 dist entry points:
  - `admin/standalone/dist/index.html`
  - `admin/shopify/dist/index.html`
  - `admin/provider/dist/index.html`
  - `widget/dist/agent-red-widget.iife.js`
- **Expected:** All modified within last 5 minutes
- **Verify:** Timestamp comparison
- **On Fail:** Re-run the stale build. NEVER deploy with a stale dist.

### Step B.3: ACR Image Build

- **Action:** `az acr build --registry $ACR_NAME --image $IMAGE_REPO:v$NEW_VERSION --no-logs --file Dockerfile .`
- **Expected:** ACR run Succeeded
- **Verify:** `az acr task list-runs --registry $ACR_NAME --top 1 --query "[0].status" -o tsv` → "Succeeded"
- **On Fail:** Check Dockerfile, requirements.txt, or build context. The `--no-logs` flag avoids Windows charmap crash.

### Step B.4: Deploy Revision

- **Action:**
  ```
  az containerapp update --name $CONTAINER_APP --resource-group $RESOURCE_GROUP \
    --image $ACR_LOGIN_SERVER/$IMAGE_REPO:v$NEW_VERSION
  ```
- **Expected:** JSON output with updated image reference
- **Verify:** `az containerapp show ... --query "properties.template.containers[0].image" -o tsv` → matches expected
- **On Fail:** Check Azure CLI output. Verify the image tag exists in ACR.

### Step B.5: Health Wait Loop

- **Action:** Poll `GET /health` and `GET /ready` every 10 seconds for up to 90 seconds (180 seconds for staging cold start)
- **Expected:** `/health` returns 200 within timeout. `/ready` may show `nats.connected: false` for 30-60s (NATS lazy init) — this is WARN, not FAIL.
- **Verify:** `GET /health` → HTTP 200, `status: "healthy"`
- **On Fail:** If `/health` never returns 200 after timeout → ROLLBACK immediately via `scripts/deploy/rollback.ps1`.

---

## Phase C — Post-Deploy Platform Verification

Validates the deployed version is functional and existing data is preserved.

### Step C.1: Version Header Matches

- **Action:** `GET /health` → read `X-Product-Version` response header
- **Expected:** Header value == `$NEW_VERSION`
- **On Fail:** Wrong version deployed. Check which image is running.

### Step C.2: Health Endpoint Healthy

- **Action:** `GET /health`
- **Expected:** HTTP 200, body `status == "healthy"`, `product_version == $NEW_VERSION`

### Step C.3: Ready Endpoint Ready

- **Action:** `GET /ready`
- **Expected:** HTTP 200, `status == "ready"`. If `nats.connected: false` with all other subsystems healthy → WARN (known NATS lazy init).
- **On Fail:** If HTTP ≠ 200, check container logs for startup errors.

### Steps C.4–C.6: Admin SPAs Return 200

- **Action:** `GET /admin/standalone/`, `GET /admin/shopify/`, `GET /admin/provider/`
- **Expected:** HTTP 200, Content-Type contains `text/html`
- **On Fail:** Stale dist or missing SPA build. Check Phase B.1.

### Step C.7: Widget.js Accessible

- **Action:** `GET /widget.js`
- **Expected:** HTTP 200, response body > 1,000 bytes
- **On Fail:** Widget dist not built or not included in Docker image.

### Step C.8: OpenAPI Spec Accessible

- **Action:** `GET /openapi.json`
- **Expected:** HTTP 200

### Step C.9: Security Headers Present

- **Action:** `GET /health` → inspect response headers
- **Expected:** `x-content-type-options: nosniff` present, `x-frame-options` present, `strict-transport-security` present (HTTPS)

### Step C.10: Existing Tenant Data Preserved

- **Action:** `python scripts/upgrade_verification.py phase-c --env $TARGET_ENVIRONMENT --snapshot scripts/upgrade-results/phase_a_{TENANT_ID}.json --new-version $NEW_VERSION`
- **Expected:** 35 PASS, 0 FAIL (C.13, C.26, C.33-C.35 are SKIP — count as PASS)
- **On Fail:** Data loss or regression detected. **ROLLBACK IMMEDIATELY** via `scripts/deploy/rollback.ps1`.

### Step C.11: Tier 0 Regression Tests

- **Action:** `PROD_URL=https://$TARGET_FQDN WIDGET_KEY=$PREVIEW_WIDGET_KEY AGENTRED_API_KEY=$AGENTRED_API_KEY python -m pytest tests/regression/test_upgrade_regression.py -x -q -m tier0 --tb=short`
- **Expected:** 17 passed, 0 failed
- **On Fail:** **ROLLBACK IMMEDIATELY.** Tier 0 failures indicate broken core functionality.

### Step C.12: Tier 1 Regression Tests

- **Action:** `PROD_URL=https://$TARGET_FQDN WIDGET_KEY=$PREVIEW_WIDGET_KEY AGENTRED_API_KEY=$AGENTRED_API_KEY python -m pytest tests/regression/test_upgrade_regression.py -x -q -m tier1 --tb=short`
- **Expected:** ≥ 20 passed, 0 failed
- **On Fail:** Flag for investigation. Deployment is live but has a functional regression.

---

## Phase D — Live Tenant Provisioning Verification ★

The concluding end-to-end verification. Creates a real tenant and exercises every critical customer workflow. This phase proves that a new customer can be successfully onboarded.

**Smoke tenant email:** `preflight-smoke-{YYYY-MM-DD}@preflight.internal`

### Step D.1: Create Smoke-Test Tenant

- **Action:** `POST /api/superadmin/tenants` with SPA superadmin key (`$SUPERADMIN_PREVIEW_API_KEY`)
  ```json
  {
    "merchantName": "Preflight Smoke YYYY-MM-DD",
    "superadminEmail": "preflight-smoke-YYYY-MM-DD@preflight.internal",
    "tier": "starter"
  }
  ```
- **Expected:** HTTP 201, response contains `tenantId`, `superadminApiKey`, `widgetKey`
- **Capture:** Save all three values — they are the only credentials for this tenant.
- **On Fail:** If 400 "already exists" — a same-day smoke tenant exists. Use `--phase D` with a time suffix or use the existing tenant credentials from that day's results file.

### Step D.2: Tenant Appears in Directory

- **Action:** `GET /api/superadmin/tenants` with SPA superadmin key
- **Expected:** HTTP 200, response includes the new `tenantId` from D.1

### Step D.3: Superadmin Key Authenticates

- **Action:** `GET /api/config` with `X-API-Key: {superadminApiKey from D.1}`
- **Expected:** HTTP 200, response contains `tenant_id` matching the new tenant

### Step D.4: Identity Correct

- **Action:** `GET /api/admin/team/whoami` with new tenant's superadmin key
- **Expected:** HTTP 200, `role` == `superadmin` (case-insensitive)

### Step D.5: Clean Initial State

- **Action:** `GET /api/admin/conversations?limit=1` and `GET /api/admin/knowledge?limit=1` with new tenant's superadmin key
- **Expected:** `totalCount == 0` for both endpoints

### Step D.6: Create Draft Configuration

- **Action:**
  1. `POST /api/config/reset` with new tenant's superadmin key (creates draft from tier defaults)
  2. `PUT /api/config` with body:
     ```json
     {"fields": {"brand_name": "Preflight Smoke Test", "brand_voice": "Professional and helpful"}}
     ```
- **Expected:** Both return HTTP 200

### Step D.7: Activate Configuration

- **Action:** `POST /api/config/draft/activate` with new tenant's superadmin key
- **Expected:** HTTP 200. **NOTE:** HTTP 500 is a known behavior on first activation — proceed to D.8 regardless of status code.
- **Verify:** Do not rely on this response — always verify via D.8.

### Step D.8: Activation Verified

- **Action:** `GET /api/config/activation-status` with new tenant's superadmin key
- **Expected:** HTTP 200, `is_active: true`, `is_configured: true`
- **On Fail:** If `is_active: false` after reset+config+activate sequence → product defect in activation pipeline.

### Step D.9: Widget Key Works

- **Action:** `POST /api/chat/conversations` with `X-Widget-Key: {widgetKey from D.1}`, body `{}`
- **Expected:** HTTP 201, response contains `conversation_id`
- **On Fail:** HTTP 401 → widget key dual-write failed in provisioning. HTTP 403 → config not activated. HTTP 503 → SKIP (NATS not warmed).

### Step D.10: AI Pipeline Produces Response

- **Action:**
  1. `POST /api/chat/message` with widget key, body `{"conversation_id": "{conv_id}", "content": "Hello, what products do you offer?"}`
  2. `GET /api/chat/stream/{conv_id}?widget_key={widgetKey}` as SSE stream (httpx streaming, 30s timeout)
- **Expected:** SSE stream contains at least one `event: token` and one `event: done` within 30 seconds
- **On Fail:** HTTP 503 → SKIP (NATS not warmed, retry with `--phase D`). No token events within 30s → AI pipeline failure.

### Step D.11: Conversation Appears in Admin Inbox

- **Action:** `GET /api/admin/conversations` with new tenant's superadmin key
- **Expected:** HTTP 200, `totalCount >= 1`

### Step D.12: Create KB Entry

- **Action:** `POST /api/admin/knowledge` with new tenant's superadmin key, body:
  ```json
  {
    "title": "Preflight Test Article",
    "content": "This is a preflight smoke test knowledge base article for deployment verification.",
    "entry_type": "faq",
    "status": "published"
  }
  ```
- **Expected:** HTTP 201 (or 200)

### Step D.13: KB Entry Visible

- **Action:** `GET /api/admin/knowledge` with new tenant's superadmin key
- **Expected:** HTTP 200, `total >= 1` (or `totalCount >= 1`)

### Step D.14: Create Team Member (Escalation Agent)

- **Action:** `POST /api/admin/team` with new tenant's superadmin key, body:
  ```json
  {
    "email": "escalation-test@preflight.internal",
    "displayName": "Preflight Agent",
    "role": "escalation_agent"
  }
  ```
- **Expected:** HTTP 201, response contains `userApiKey` (or `api_key`)
- **Capture:** Save the escalation agent's API key for D.15–D.16.

### Step D.15: RBAC Blocks Non-Admin

- **Action:** `GET /api/config` with `X-API-Key: {escalation agent key from D.14}`
- **Expected:** HTTP 403 (path `/api/config` is in admin-only prefixes)
- **On Fail:** RBAC enforcement broken — the `enforce_rbac` middleware is not blocking non-admin roles.

### Step D.16: RBAC Allows Inbox Access

- **Action:** `GET /api/admin/conversations` with `X-API-Key: {escalation agent key from D.14}`
- **Expected:** HTTP 200 (path `/api/admin/conversations` is open to all roles)
- **On Fail:** RBAC enforcement too aggressive — blocking legitimate access for escalation agents.

### Step D.17: Admin SPA Routes Accessible

- **Action:** `GET /admin/standalone/` and `GET /admin/provider/` (no auth required — SPA is static)
- **Expected:** HTTP 200, Content-Type `text/html` for both

### Step D.18: Phase D Summary

- **Action:** Print/log summary table of all D.1–D.17 results
- **Expected:** 17/17 PASS (D.10 may be SKIP if NATS unavailable)
- **Minimum for PASS:** D.1–D.9 and D.11–D.17 all PASS. D.10 may be SKIP.

---

## Phase E — Verdict

| Condition | Verdict | Action |
|-----------|---------|--------|
| All A, B, C, D pass | **DEPLOYMENT VERIFIED** | Record results. Update `Last verified` date in this procedure. |
| Phase C assertion fails | **ROLLBACK REQUIRED** | Execute `scripts/deploy/rollback.ps1 -Version {previous}` immediately. |
| Phase D assertion fails | **ROLLBACK REQUIRED** | Widget/chat critical-path failure. Execute `scripts/deploy/rollback.ps1 -Version {previous}` immediately. The chat widget is core product surface — a broken widget is a failed deployment (S251 OM-3). |
| Phase A or B fails | **DEPLOYMENT BLOCKED** | Fix the issue. Re-run from Phase A. |

---

## Postconditions

After a successful DEPLOYMENT VERIFIED verdict:

1. Results JSON saved to `scripts/pre-flight-results/preflight-{env}-{date}-{time}.json`
2. Smoke tenant (`preflight-smoke-{date}@preflight.internal`) exists in the environment — persists indefinitely (no delete endpoint)
3. All existing tenant data unchanged from pre-deploy snapshot
4. Product version header reports `$NEW_VERSION` on all responses
5. Update this procedure's `Last verified` date

---

## Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| A.2 grep assertion count below threshold | Procedure defect (regression) | A protected behavior was removed. Restore it. Never fix by removing the assertion. |
| B.3 `az acr build` UnicodeEncodeError | Environment (Windows charmap) | Use `--no-logs` flag. Cosmetic — check ACR portal for actual build status. |
| B.5 NATS not ready after 90s | Environment transient | `/health` 200 + `/ready` NATS false is expected during lazy init. Log WARN, continue. Re-check after 60s. |
| C.10 Phase C data comparison fails | Product defect (data loss) | **ROLLBACK IMMEDIATELY.** Tenant data must be identical to Phase A snapshot. |
| D.1 returns 400 "already exists" | Procedure (same-day rerun) | A smoke tenant with today's date already exists. Append time suffix or reuse existing credentials. |
| D.1 returns 403 | Procedure (wrong SPA key) | Only `remaker-digital-001` superadmin can provision tenants. Check `.env.local SUPERADMIN_PREVIEW_API_KEY`. |
| D.7 returns 500 on activation | By design (known) | Do not treat as failure. Check D.8 activation-status instead. |
| D.9 widget key returns 401 | Product defect | SPA provisioning should dual-write widget key. Investigate `provisioning.py:auto_provision_widget_key()`. |
| D.10 SSE returns 503 | Environment transient | NATS not warmed. Wait 60s, rerun `--phase D`. |
| D.10 httpx not installed | Environment (missing dep) | `pip install httpx`. Required for SSE streaming verification. |
| Staging cold start timeout | Environment transient | Staging min replicas = 0. Extend health wait to 180s. |
| Smoke tenants accumulate | By design | No tenant delete endpoint. Use deterministic email pattern to identify them. |
| Same ACR tag exists | Procedure (redeployment) | Set `DEPLOY_TIMESTAMP` env var to force new revision even with same image tag. |

---

## Cross-Procedure Dependencies

- **Incorporates:** Build & Deploy procedure (`build-deploy-procedure.md`) — Phase B
- **Incorporates:** Protected Behaviors registry (`PROTECTED-BEHAVIORS.md`) — Phase A.2
- **Incorporates:** Upgrade Verification procedure — Phase C.10 calls `upgrade_verification.py phase-c`
- **Requires pre-step:** `upgrade_verification.py phase-a` must be run before Phase B deploy
- **Follows:** Unit Test Suite (Phase A.4 executes it)
- **Precedes:** All other post-deploy verification procedures (this is the first post-deploy gate)

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
