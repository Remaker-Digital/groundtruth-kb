# Workflow 2: Embedded Admin Dashboard

> **Audience:** UX Designer, Product Owner
> **Environment:** Shopify admin (admin.shopify.com/store/blanco-9939)
> **Last Updated:** 2026-02-04

---

## Purpose

This workflow documents how a merchant accesses and uses the Agent Red admin dashboard from within their Shopify admin panel. The admin SPA is embedded inside a Shopify iframe using Polaris + App Bridge.

---

## Step 1: Finding the App in Shopify Admin

**URL:** `https://admin.shopify.com/store/blanco-9939/settings/apps`

**What the merchant sees:**
- Shopify admin sidebar (left) with standard navigation: Home, Orders, Products, Customers, Marketing, Discounts, Content, Markets, Finance, Analytics
- **Settings > Apps** page showing installed apps
- **"Agent Red Customer Experience"** listed with the AR monogram icon
- Tabs: "Installed" (active) and "Uninstalled"

**Screenshot reference:** `ss_1276a3pas` — Apps settings page

**How to get here:**
1. Log in to Shopify admin
2. Click **Settings** (bottom-left)
3. Click **Apps** in the settings sidebar

**UX Notes:**
- The app appears in the standard Shopify apps list
- AR monogram icon helps identify the app at a glance

---

## Step 2: App Installation Details

**URL:** `https://admin.shopify.com/store/blanco-9939/settings/apps/app_installations/app/agent-red-customer-experience`

**What the merchant sees:**
- **App header:** "Agent Red Customer Experience" by Remaker Digital
- **"Open app" button** (top-right, blue) — navigates to the embedded admin dashboard
- **About this app:** Warning that app is not listed in the Shopify App Store (expected for development apps)
- **App history:** Timeline showing "App installed" on February 2 at 3:01 PM
- **Privacy details:** Data access scopes organized by category:
  - Customers: Contact information (name, email, phone), Location (physical address, geolocation, IP), Device information (browser and OS)
  - Store owner information (below fold)

**Screenshot reference:** `ss_05775d6vc` — App installation details

**How to get here:**
1. From Settings > Apps, click on "Agent Red Customer Experience"

**UX Notes:**
- The "Open app" button is the primary entry point to the admin dashboard
- Privacy details show exactly what data the app can access — important for GDPR compliance
- "Not listed in App Store" warning will be removed after App Store submission

---

## Step 3: Embedded Admin Dashboard

**URL:** `https://admin.shopify.com/store/blanco-9939/apps/agent-red-customer-experience/admin/shopify`

**What the merchant sees:**
- **Shopify chrome:** Standard Shopify admin header with search, notifications, and store name
- **App header:** "Agent Red Customer Experience" with AR monogram logo and three-dot menu
- **Navigation breadcrumb:** "← Agent Red ..." in the top bar
- **Left sidebar:** Standard Shopify nav items plus "Agent Red Customer Exp..." under Apps section
- **Dashboard page title:** "Dashboard"

### Analytics Overview Card
- **Refresh button** (top-right of card)
- **Four stat cards** with color-coded top borders:
  - **TOTAL CONVERSATIONS** (blue border) — Shows "0" (no conversations yet)
  - **AVG RESPONSE TIME** (orange border) — Shows "- -" with "Above P95 target" note
  - **RESOLUTION RATE** (green border) — Shows "- -"
  - **ESCALATION RATE** (red border) — Shows "- -"

### CSAT Card
- Shows "- -" with "No ratings yet" message
- Will display customer satisfaction scores once conversations are processed

### Intent Breakdown Card
- Shows "No intent data" with a bar chart icon
- Message: "Intent breakdown will appear once conversations are processed"
- Will show distribution of customer intents (17 categories) once active

**Screenshot reference:** `ss_92402dg2w` — Embedded admin dashboard

**How to get here:**
1. From the app installation page, click **"Open app"**
2. OR from the Shopify admin sidebar, click **"Agent Red Customer Exp..."** under Apps

**UX Notes:**
- The dashboard renders inside the Shopify admin iframe using Polaris components
- All stat cards handle null/zero data gracefully (showing "0", "--", or descriptive messages)
- Color-coded borders provide quick visual differentiation between metrics
- "Above P95 target" on response time is a proactive SLA indicator
- The dashboard will populate automatically as conversations flow through the system
- Error boundaries protect against render crashes — if any component fails, it shows an error message with a "Try Again" button instead of a blank page

---

## Current State & Known Limitations

### What Works
- Polaris Frame renders correctly inside Shopify iframe
- Dashboard page loads with all shared components (AnalyticsOverview + UsageDashboard)
- All stat cards display safely with zero/null data
- Error Boundary catches render crashes gracefully
- Navigation between Shopify admin and Agent Red app works seamlessly

### Prerequisites for Full Functionality
1. **SHOPIFY_API_KEY + SHOPIFY_API_SECRET** must be set as env vars on the API Gateway Container App (WI #198b) — required for tenant lookup via Shopify session tokens
2. **Tenant provisioning** — the store must be registered as a tenant in Cosmos DB
3. **Knowledge base seeding** — articles loaded for AI to reference
4. **At least one customer conversation** — needed for analytics data to appear

### Expected Admin Pages (Post-Provisioning)
Once the store is fully provisioned as a tenant, the following admin pages will be available:

| Page | Purpose |
|------|---------|
| Dashboard | Analytics overview, conversation stats, intent breakdown |
| Inbox | Conversation list, message threading, agent assignment |
| Knowledge Base | Article CRUD, category management |
| Configuration | AI persona, escalation rules, response policies |
| Widget | Widget appearance, behavior, targeting rules |
| Billing | Plan management, usage tracking, Stripe portal |
| Settings | Account settings, team management |

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
