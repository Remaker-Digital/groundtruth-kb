# Agent Red Customer Experience — 1.0 Launch Checklist

This checklist covers every action required to go from "code complete" to "live on
Shopify App Store + Stripe direct". Items marked **[OWNER]** require the owner's
manual action; items marked **[AUTO]** are automated by the platform.

---

## Pre-Launch: Azure Container App Environment Variables

**[OWNER]** Set the following environment variables on the `agent-red-api-gateway`
Container App. These are required for Shopify JWT verification and the chat
pipeline's Azure OpenAI integration.

```bash
az containerapp update \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --set-env-vars \
    SHOPIFY_API_KEY=<from Shopify Partners dashboard> \
    SHOPIFY_API_SECRET=<from Shopify Partners dashboard> \
    AZURE_OPENAI_ENDPOINT=https://aoai-agentred-eastus2.openai.azure.com/ \
    AZURE_OPENAI_API_KEY=<from kv-agentred-eastus2>
```

**Verification:** After update, visit
`https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io/health`
and confirm HTTP 200.

---

## Pre-Launch: Remaker Digital Storefront (Tenant #1)

### Step 1: Create Shopify Storefront **[OWNER]**

Create a Shopify storefront for Remaker Digital (or use the existing
`blanco-9939.myshopify.com` dev store). Install the "Agent Red Customer
Experience" app from the Shopify Partners dashboard.

### Step 2: Provision Tenant **[OWNER]**

Run from the project root with `.env.local` configured:

```bash
python scripts/provision_tenant_one.py
```

This creates the `remaker-digital-001` tenant in Cosmos DB with Starter tier
defaults, a widget key (`pk_live_...`), and an admin API key.

### Step 3: Seed Knowledge Base **[OWNER]**

```bash
python scripts/seed_knowledge_base.py --load --tenant-id remaker-digital-001
```

Creates 32 KB articles covering Agent Red pricing, features, setup guides, and
FAQ. The script is idempotent — safe to run multiple times.

### Step 4: Embed Knowledge Base **[OWNER]**

```bash
python scripts/embed_knowledge_base.py --embed --tenant-id remaker-digital-001
```

Generates vector embeddings (text-embedding-3-large, 3072d) for all KB entries.
Includes rate-limit-aware retry logic (0.5s inter-entry delay, 65s wait on 429).

### Step 5: Verify Chat Pipeline **[OWNER]**

```bash
# Start a conversation
curl -s -X POST \
  https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io/api/chat/conversations \
  -H "X-Widget-Key: <widget_key_from_step_2>" \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"test-launch"}' | jq .

# Send a message (use conversation_id from response above)
curl -s -X POST \
  https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io/api/chat/message \
  -H "X-Widget-Key: <widget_key>" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"<id>","content":"What is your pricing?"}' | jq .
```

**Expected:** Response includes specific pricing data ($149/$399/$999).

---

## Pre-Launch: Creative Assets **[OWNER/DESIGNER]**

These assets are required for the Shopify App Store listing and cannot be
generated programmatically.

| Asset | Specification | Status |
|-------|---------------|--------|
| App icon | 1200 x 1200 PNG, no text, no rounded corners, no transparency | Pending |
| Key benefit image 1 | 1600 x 1200 PNG — "Persistent Customer Memory" | Pending |
| Key benefit image 2 | 1600 x 1200 PNG — "4-21x Cheaper Than Competitors" | Pending |
| Key benefit image 3 | 1600 x 1200 PNG — "Hybrid AI Knowledge Search" | Pending |
| Desktop screenshot | Actual product, 1600 x 900 minimum | Pending |
| Mobile screenshot | Actual product, 750 x 1334 minimum | Pending |

Reference: `docs/shopify/APP-STORE-LISTING.md` for full specifications.

---

## Shopify App Store Submission

### Step 6: Update GDPR Webhook URLs **[OWNER]**

Edit `shopify.app.toml` and replace the placeholder `app.agentred.com` URLs
with the production API Gateway FQDN:

```toml
[webhooks]
api_version = "2024-10"

  [webhooks.privacy_compliance]
  customer_data_request_url = "https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io/api/shopify/gdpr/customers-data-request"
  customer_deletion_url = "https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io/api/shopify/gdpr/customers-redact"
  shop_deletion_url = "https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io/api/shopify/gdpr/shop-redact"
```

Then deploy:

```bash
shopify app deploy
```

### Step 7: Configure Pricing in Partners Dashboard **[OWNER]**

In the Shopify Partners dashboard, set the app pricing to match Agent Red's
tier structure:

| Tier | Monthly | Annual |
|------|---------|--------|
| Starter | $149/month | $1,490/year |
| Professional | $399/month | $3,990/year |
| Enterprise | $999/month | $9,990/year |

Enable the 14-day free trial for all tiers.

### Step 8: Submit for Review **[OWNER]**

1. Go to Shopify Partners → Apps → Agent Red Customer Experience
2. Click "Submit for review"
3. Fill in the testing instructions (reference `docs/shopify/APP-STORE-LISTING.md`)
4. Provide test credentials if needed
5. Expected review time: 3-7 business days

---

## Stripe Direct Channel

### Step 9: Enable Stripe Live Mode **[OWNER]**

1. In Stripe Dashboard, switch from Test Mode to Live Mode
2. Create live-mode Products and Prices matching `config/stripe_product_ids.json`
   (or use `scripts/stripe/create_product_catalog.py` against live keys)
3. Update `.env` / Container App env vars with live Stripe keys
4. Verify tax settings: origin address (Delaware), automatic_tax enabled,
   tax code `txcd_10103001` (SaaS — Business Use)

### Step 10: Connect Rewardful **[OWNER]**

1. Sign up for Rewardful Starter plan ($49/month)
2. Connect to live Stripe account (OAuth — requires admin permissions)
3. Configure commission: 20% recurring, 60-day cookie, 12-month duration
4. Rewardful `client_reference_id` is already coded into Checkout Sessions

---

## What Is Automated After Launch

| Process | Trigger | Details |
|---------|---------|---------|
| Tenant provisioning | Stripe webhook `checkout.session.completed` | Creates tenant in Cosmos DB |
| Usage metering | Each billable conversation | 3-tier: included → packs → overage |
| Trial expiry | 14 days after creation | trial_management.py sends alerts |
| Data retention | Daily cron 03:00 UTC | data_retention.py enforces tier limits |
| Archival | Daily cron 04:00 UTC | archival_pipeline.py → Azure Blob |
| Certificate renewal | Azure managed | Automatic TLS |
| Health monitoring | Every 30s | Dockerfile HEALTHCHECK + /health endpoint |
| Auto-scaling | KEDA rules | Container Apps scale 2-10 based on load |
| Night scaling | Cron (if enabled) | Non-critical containers → 0 replicas 22:00-06:00 UTC |

---

## Post-Launch Verification

After both channels are live, verify:

- [ ] Shopify storefront: widget visible, chat returns KB-aware responses
- [ ] Shopify embedded admin: accessible from Shopify Admin → Apps
- [ ] Standalone admin: accessible at `/admin/standalone/` with password
- [ ] Stripe Checkout: complete a test purchase, verify tenant provisioned
- [ ] Trial signup: verify 14-day trial tier, conversation limit enforced
- [ ] Usage metering: verify usage counters increment in dashboard
- [ ] Billing alerts: verify 80%/100% threshold notifications in admin dashboard

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
