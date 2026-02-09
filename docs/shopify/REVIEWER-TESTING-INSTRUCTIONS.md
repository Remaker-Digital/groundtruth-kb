# Agent Red Customer Experience — Reviewer Testing Instructions

**For:** Shopify App Store Review Team
**App:** Agent Red Customer Experience
**Version:** 1.0.0
**Date:** 2026-02-08

---

## Quick Start

1. **Install** the app on any development store
2. The app will redirect to the **embedded admin dashboard** inside Shopify
3. Complete the **Setup Wizard** (takes ~2 minutes)
4. Navigate to your **online store** to see the **chat widget** in the bottom-right corner
5. Click the widget and **send a message** — the AI will respond in real-time via streaming

---

## Step-by-Step Walkthrough

### 1. Installation

1. From the app listing, click **"Add app"**
2. Accept the OAuth permissions (read_orders, read_products, read_customers, read_inventory)
3. The app installs and redirects to the embedded admin at `/admin/shopify`

**Expected result:** Embedded admin dashboard loads inside Shopify Admin iframe with the Agent Red navigation sidebar.

### 2. Setup Wizard (Onboarding)

1. Click **"Setup"** in the navigation
2. Complete each step of the wizard:
   - **Store info:** Auto-detected from your Shopify store
   - **AI persona:** Choose a tone (friendly, professional, casual)
   - **Response style:** Set response length preference
   - **Escalation rules:** Configure when to hand off to a human
   - **Knowledge base:** Add a few product FAQs or use the sample data
   - **Widget appearance:** Choose colors, position, greeting message
   - **Review:** Confirm settings
3. Click **"Go Live"**

**Expected result:** Wizard completes, dashboard shows active status.

### 3. Chat Widget on Storefront

1. Navigate to your development store's **online store** (front-end)
2. Look for the **chat launcher button** in the bottom-right corner
3. Click to open the chat panel
4. Type a message (e.g., "What products do you sell?")
5. The AI responds with streaming text (tokens appear as they are generated)

**Expected result:** Widget opens, AI responds based on knowledge base content. Response streams in real-time.

### 4. Embedded Admin Features

Navigate through each section of the admin:

| Section | What to Test |
|---------|-------------|
| **Dashboard** | View conversation stats, daily volume chart |
| **Inbox** | See conversation list, click to view message thread |
| **Knowledge Base** | Add/edit/delete articles, upload a document (PDF, DOCX, CSV) |
| **Analytics** | View intent breakdown, conversation gaps |
| **Configuration** | Modify AI persona, escalation rules, response style |
| **Widget** | Customize appearance (colors, position, greeting), see live preview |
| **Billing** | View current plan, usage metrics, conversation allowance |
| **Team** | Invite team members (email), assign roles |

### 5. Billing

1. Navigate to **Billing** in the admin
2. The app uses the **Shopify Billing API** for subscriptions
3. Subscription plans available: Starter ($149/mo), Professional ($399/mo), Enterprise ($999/mo)
4. Usage-based conversation charges via `appUsageRecordCreate`

**To test plan changes:**
1. Subscribe to Starter plan
2. Navigate back to Billing → change to Professional plan
3. The app handles the upgrade via `appSubscriptionCreate` with prorated billing

### 6. GDPR Compliance

The app implements all three mandatory GDPR webhooks:
- `POST /api/shopify/gdpr/customers-data-request` — exports customer data
- `POST /api/shopify/gdpr/customers-redact` — deletes customer data
- `POST /api/shopify/gdpr/shop-redact` — deletes shop data (48hr after uninstall)

All webhooks verify HMAC-SHA256 signatures. Invalid signatures return 401.

### 7. Uninstall

1. Go to **Settings → Apps** in Shopify Admin
2. Click the "..." menu next to Agent Red → **Uninstall**
3. The `shop/redact` webhook fires after the mandatory 48-hour grace period

**Expected result:** App uninstalls cleanly. No residual UI elements on the storefront.

---

## Test Credentials

| Credential | Value |
|-----------|-------|
| **Demo store** | blanco-9939.myshopify.com |
| **API Gateway** | agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io |
| **App health check** | `GET /health` → 200 OK |

No additional third-party credentials are required. The app uses Azure OpenAI (Anthropic-hosted) for AI responses — no external API keys needed from the reviewer.

---

## Technical Notes

- **Framework:** FastAPI (Python) + React (admin) + Preact (widget)
- **AI Model:** Azure OpenAI GPT-4o (response generation), GPT-4o-mini (classification)
- **Database:** Azure Cosmos DB (Serverless, multi-tenant)
- **Widget delivery:** Shopify Theme App Extension (app embed block)
- **Admin delivery:** Embedded SPA via App Bridge + Polaris
- **Auth:** Shopify session tokens (JWT HS256) — no cookies, works in incognito
- **API:** GraphQL Admin API only (no REST)
- **Widget bundle:** ~17KB gzip (Preact IIFE, Shadow DOM isolation)

---

## Known Limitations (v1.0)

- **Test Mode** configuration preview is not yet functional (post-launch feature)
- **Period filtering** (daily/weekly/monthly) on dashboard stats is visual-only
- Integration connectors (Zendesk, Mailchimp, GA4) show "Coming soon" status

---

## Support

For questions during review:
- **Email:** mike@remakerdigital.com
- **Response time:** Within 4 business hours

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
