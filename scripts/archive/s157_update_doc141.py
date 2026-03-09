"""S157: Update DOC-141 with production deployment record."""
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
import sys
sys.path.insert(0, 'tools/knowledge-db')
import db

CONTENT = """# Shopify Production Deployment Guide

**Purpose:** Step-by-step procedure for switching the Shopify embedded app from staging to production when deploying a new build.

**When to use:** After deploying a new production build to Azure Container Apps, when the Shopify app needs to connect to the production environment.

---

## Deployment History

| Date | Version | ACR Run | Revision | Widget | Session | Notes |
|------|---------|---------|----------|--------|---------|-------|
| 2026-03-01 | v1.62.0 | ca3n | 0000090 | v20 | S125 | Co-Pilot + AGNTCY Phase 2/5/6 |
| 2026-03-07 | v1.77.0 | ca4j | 0000091 | v24 | S157 | Test mode removal + tenant names + production URL switch |

---

## Prerequisites

- New production Docker image built and pushed to ACR (acragentredeastus.azurecr.io)
- Production Container App revision deployed and healthy
- Production health endpoint responding

## Environment Reference

| Item | Production | Staging |
|------|-----------|---------|
| FQDN | agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io | agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io |
| Cosmos DB | agentred database | agentred-staging database |
| Container App | agent-red-api-gateway | agent-red-staging |
| Resource Group | Agent-Red | Agent-Red |

---

## Files That Change Between Environments

Only **2 files** need modification when switching between staging and production:

### 1. shopify.app.toml (5 URLs)
All URLs must match the target environment FQDN:
- application_url (line 9)
- redirect_urls[0] (line 17)
- customer_data_request_url (line 27)
- customer_deletion_url (line 28)
- shop_deletion_url (line 29)

### 2. extensions/agent-red-chat/blocks/agent-red-chat.liquid (1 URL)
The api_url setting default must match the target environment FQDN (line 86 default value).

### Files That Do NOT Need Changing
- admin/*/.env.production -- All 3 use empty VITE_API_URL= (same-origin). Works for both environments.
- Dockerfile -- Environment-agnostic. Uses .env.production during build.
- Widget source (widget/src/) -- Reads API URL from data-api-url attribute at runtime.

---

## Deployment Steps

### Step 1: Switch URLs in shopify.app.toml
Replace all occurrences of the source FQDN with the target FQDN.
- Staging to Production: Replace agent-red-staging with agent-red-api-gateway in all 5 URLs.
- Production to Staging: Replace agent-red-api-gateway with agent-red-staging in all 5 URLs.

### Step 2: Switch Default API URL in agent-red-chat.liquid
Update the api_url setting default value to match the target FQDN.

### Step 3: Build Docker Image (if code changed)
Use az acr build with --no-logs to avoid Windows cp1252 Unicode crash.

### Step 4: Deploy Container App
az containerapp update with --image flag.

### Step 5: Deploy Shopify Extension
npx shopify app deploy --force
This pushes both the TOML config (URLs) and the widget extension (JS + Liquid) to Shopify CDN.

### Step 6: Rebuild Admin SPAs (only if admin source changed)
Build all 3 admin SPAs. Only needed if admin TypeScript/React source was modified.
The SPAs are environment-agnostic via same-origin pattern.

---

## Verification Checklist

### 7a. Health Check
Verify /health returns 200 with correct product_version.

### 7b. Admin Console HTTP 200
Verify /admin/standalone/, /admin/shopify/, /admin/provider/ all return HTTP 200.

### 7c. Shopify Admin Iframe (Manual)
1. Open Shopify admin
2. Navigate to Apps > Agent Red Customer Experience
3. Verify the app loads within 30s
4. Check DevTools Network tab: all API requests go to production FQDN

### 7d. Storefront Widget
1. Open storefront
2. Verify chat launcher button appears
3. Click to open, verify chat panel renders

---

## Known Issues (S157)

### Production Cosmos DB Has No Seeded API Keys
**Status:** Pre-existing (since at least v1.62.0).
**Impact:** Cannot use X-API-Key header for API authentication in production. Magic link email auth works.
**Root cause:** Production tenants use UUID-based IDs from SPA provisioning, not slug-based IDs.
No tenant was ever seeded via seed_tenant.py with proper API key hashes.
**Key Vault keys are orphaned:** Keys in Key Vault (superadmin-api-key, remaker-digital-001-superadmin-key) don't correspond to any hashed keys in production Cosmos.
**Fix:** Run seed_tenant.py --env production to create a properly seeded tenant, or manually patch an existing tenant with API key hashes.

---

## Reverting to Staging

1. Edit shopify.app.toml: replace agent-red-api-gateway with agent-red-staging in ALL 5 URLs
2. Edit agent-red-chat.liquid: replace production FQDN with staging FQDN in api_url default
3. Run npx shopify app deploy --force
4. May need to clear browser cache for the change to take effect

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

kdb = db.KnowledgeDB()
kdb.update_document(
    'DOC-141',
    'Claude',
    'S157: Add deployment history table, document 2-file environment switch, known Cosmos API key issue',
    title='Shopify Production Deployment Guide',
    content=CONTENT,
    doc_type='operational_guide',
    session_id='S157'
)
print('DOC-141 updated to v3')
kdb.close()
