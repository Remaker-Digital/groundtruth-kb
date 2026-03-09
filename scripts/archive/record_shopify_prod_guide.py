"""
Record DOC-141: Shopify Production Deployment Guide in Knowledge DB.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
sys.path.insert(0, "tools/knowledge-db")
import db

kdb = db.KnowledgeDB()

GUIDE_CONTENT = r"""# Shopify Production Deployment Guide

**Purpose:** Step-by-step procedure for switching the Shopify embedded app from staging to production when deploying a new build.

**When to use:** After deploying a new production build to Azure Container Apps, when the Shopify app needs to connect to the production environment (remaker-digital-001).

---

## Prerequisites

- New production Docker image built and pushed to ACR (`acragentredeastus.azurecr.io`)
- Production Container App revision deployed and healthy
- Production health endpoint responding: `https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/health`

## Environment Reference

| Item | Production | Staging |
|------|-----------|---------|
| **FQDN** | `agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` | `agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |
| **Tenant ID** | `remaker-digital-001` | `staging-001` / `staging-002` / `remaker-digital-001` |
| **Shop domain** | `blanco-9939.myshopify.com` | `blanco-9939.myshopify.com` |
| **Cosmos DB** | `agentred` database | `agentred-staging` database |
| **Shopify App URL** | `https://{PROD_FQDN}/admin/shopify` | `https://{STAGING_FQDN}/admin/shopify` |

---

## Step 1: Verify shopify.app.toml Points to Production

**File:** `shopify.app.toml` (project root)

Verify ALL URLs use the **production** FQDN. The file should contain:

```toml
application_url = "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/admin/shopify"

[auth]
redirect_urls = [
  "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/api/shopify/billing/confirm"
]

[webhooks.privacy_compliance]
customer_data_request_url = "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/api/shopify/gdpr/customers-data-request"
customer_deletion_url = "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/api/shopify/gdpr/customers-redact"
shop_deletion_url = "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/api/shopify/gdpr/shop-redact"
```

**If URLs point to staging:** Replace all occurrences of `agent-red-staging` with `agent-red-api-gateway`.

---

## Step 2: Deploy Shopify App Configuration

Run the Shopify CLI to push the updated TOML to the Partner Dashboard:

```bash
npx shopify app deploy
```

This updates the Shopify Partner Dashboard with:
- App URL (where the iframe loads from)
- Auth redirect URLs (billing confirmation callback)
- GDPR webhook URLs (mandatory for Shopify apps)

**Alternative (manual):** If CLI deploy is unavailable, update these URLs manually in the Shopify Partner Dashboard at https://partners.shopify.com → Apps → Agent Red Customer Experience → Configuration.

---

## Step 3: Verify Cosmos DB Shop Domain Mapping

The production Cosmos DB must have the shop domain `blanco-9939.myshopify.com` mapped to the `remaker-digital-001` tenant.

**How tenant lookup works:**
1. Shopify iframe loads with `?shop=blanco-9939.myshopify.com`
2. SPA calls `GET /api/tenants/lookup?shop=blanco-9939.myshopify.com`
3. Server queries Cosmos: `SELECT * FROM c WHERE c.shopify_shop_domain = 'blanco-9939.myshopify.com'`
4. Returns tenant_id, tier, status, billing_channel

**Verify the mapping exists:**

```python
# Quick check via Python
import asyncio
from azure.cosmos.aio import CosmosClient

async def check():
    client = CosmosClient(COSMOS_URL, credential=CREDENTIAL)
    db = client.get_database_client("agentred")
    container = db.get_container_client("tenants")
    async for item in container.query_items(
        query="SELECT c.tenant_id, c.shopify_shop_domain, c.status, c.tier FROM c WHERE c.shopify_shop_domain = 'blanco-9939.myshopify.com'",
        enable_cross_partition_query=True
    ):
        print(item)
    await client.close()

asyncio.run(check())
```

**If mapping is missing:** Run the seed script to create/update the tenant:

```bash
python scripts/seed_tenant.py --env production
```

Or patch the existing tenant document to add `shopify_shop_domain`:

```python
operations = [{"op": "add", "path": "/shopify_shop_domain", "value": "blanco-9939.myshopify.com"}]
await container.patch_item(item="remaker-digital-001", partition_key="remaker-digital-001", patch_operations=operations)
```

---

## Step 4: Verify .env.production Files (Usually No Action Needed)

All three admin SPAs should have empty `VITE_API_URL` in their `.env.production` files. This was fixed in S143 and should not need changing.

```
# admin/shopify/.env.production
VITE_API_URL=

# admin/standalone/.env.production
VITE_API_URL=

# admin/provider/.env.production
VITE_API_URL=
```

**Why empty:** The SPAs are served from the same FastAPI server as the API. Empty `VITE_API_URL` means all `fetch()` calls use relative paths (same-origin). This works correctly in BOTH production and staging because the SPA is always co-located with the API.

**IMPORTANT:** If `VITE_API_URL` is set to a specific URL, the SPA will send all API requests to that URL regardless of which server is hosting the SPA. This was the root cause of the S143 blank-page bug.

---

## Step 5: Rebuild Admin SPAs and Docker Image

If any `.env.production` or source files changed:

```bash
# Build all 3 admin SPAs
cd admin/shopify && npm run build && cd ../..
cd admin/standalone && npm run build && cd ../..
cd admin/provider && npm run build && cd ../..

# Build and push Docker image
docker build -t acragentredeastus.azurecr.io/api-gateway:v{VERSION} .
docker push acragentredeastus.azurecr.io/api-gateway:v{VERSION}
```

**Note:** The Dockerfile copies pre-built `dist/` folders. The build uses `.env.production` (empty VITE_API_URL), not `.env.local`.

---

## Step 6: Deploy to Production Container App

```bash
az containerapp update \
  --name agent-red-api-gateway \
  --resource-group rg-agentred-eastus \
  --image acragentredeastus.azurecr.io/api-gateway:v{VERSION}
```

---

## Step 7: Verification Checklist

After deployment, verify the Shopify integration works end-to-end:

### 7a. Health Check
```bash
curl https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/health
# Expected: 200 OK
```

### 7b. Tenant Lookup API
```bash
curl "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/api/tenants/lookup?shop=blanco-9939.myshopify.com"
# Expected: {"found": true, "tenant_id": "remaker-digital-001", ...}
```

### 7c. Shopify Admin Iframe (Manual)
1. Open Shopify admin: https://blanco-9939.myshopify.com/admin
2. Navigate to Apps → Agent Red Customer Experience
3. Verify the app loads (not blank page)
4. Verify Dashboard page shows content within 30 seconds
5. Check browser DevTools Network tab: all API requests should go to the PRODUCTION FQDN
6. Navigate through all 7 pages: Dashboard, Inbox, Configuration, Knowledge Base, Widget, Billing, Settings

### 7d. Run Real-Rendering Tests (Optional but Recommended)
```bash
# Update test file constants to point to production:
# STAGING_FQDN → production FQDN
# Then run:
pytest tests/e2e_live/shopify/test_shopify_real_rendering.py -v --timeout=600
```

### 7e. Chrome MCP Validation (Optional)
Use Chrome MCP to connect to the real Shopify admin and verify all 7 pages render correctly inside the iframe, as done in S144.

---

## Troubleshooting

### Blank page in Shopify admin
1. **Check iframe src:** DevTools → Elements → find `<iframe>`. The `src` should point to production FQDN, not staging.
2. **Check network tab:** Filter for `/api/tenants/lookup`. If this request goes to the wrong server, `shopify.app.toml` was not deployed correctly.
3. **Check Cosmos mapping:** If lookup returns `{"found": false}`, the `shopify_shop_domain` field is missing from the tenant document in production Cosmos.

### S142/S143 regression (requests hit wrong server)
- The Shopify Partner Dashboard App URL determines where the iframe points
- `shopify app deploy` pushes `shopify.app.toml` URLs to the Partner Dashboard
- If the deploy didn't take effect, manually update in Partner Dashboard
- In extreme cases, uninstall and reinstall the app from the Shopify admin

### idToken() timeout (5s delay then fallback)
- Normal behavior when testing outside the Shopify admin iframe
- Inside the real Shopify admin, idToken() should resolve in <100ms
- If consistently slow inside Shopify admin, check App Bridge CDN loading

### Rate limiting (429 on API calls)
- Admin rate limit is 500 RPM per tenant (all tiers)
- Template 429 is the admin rate limiter, NOT Azure OpenAI TPM
- Wait and retry, or check if another process is consuming the rate limit budget

---

## Key Shopify App Credentials

| Credential | Value |
|-----------|-------|
| **App client_id** | `4c6cf726cd1f9f5389caf48f78af9735` |
| **API key** | `4c6cf726cd1f9f5389caf48f78af9735` |
| **API secret** | Stored in `.env.local` as `SHOPIFY_API_SECRET` |
| **Access token** | Stored in `.env.local` as `SHOPIFY_ACCESS_TOKEN` |
| **Store URL** | `blanco-9939.myshopify.com` |

---

## Reverting to Staging (for Testing)

To switch back to staging for testing:

1. Edit `shopify.app.toml`: replace `agent-red-api-gateway` with `agent-red-staging` in ALL URLs
2. Run `npx shopify app deploy`
3. Verify in Shopify Partner Dashboard that the App URL changed
4. May need to wait or clear browser cache for the change to take effect in the Shopify admin iframe

**S142 lesson:** Changing the App URL in Partner Dashboard does NOT always propagate immediately. The merchant may need to:
- Hard refresh the Shopify admin page
- Clear browser cache
- In extreme cases, uninstall and reinstall the app
"""

result = kdb.insert_document(
    id="DOC-141",
    title="Shopify Production Deployment Guide",
    category="operations",
    status="active",
    changed_by="S144",
    change_reason="S144: Owner requested guide for switching Shopify app from staging to production",
    content=GUIDE_CONTENT,
    tags=["shopify", "deployment", "production", "guide", "partner-dashboard", "cosmos"],
    source_path="tools/knowledge-db/knowledge.db",
)

print(f"Document recorded: {result['id']} v{result['version']}")
kdb.close()
