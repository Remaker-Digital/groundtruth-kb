#!/usr/bin/env python3
"""
Update GitHub wiki pages for Agent Red.
S158: Comprehensive update — v1.80.0 features, SPA Operations Guide, Provider Console rewrite.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pathlib

WIKI = pathlib.Path("C:/Users/micha/AppData/Local/Temp/agent-red.wiki")


def write_wiki(name: str, content: str) -> None:
    path = WIKI / name
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"  Written: {name} ({len(content):,} bytes)")


# ---------------------------------------------------------------------------
# 1. Home.md
# ---------------------------------------------------------------------------
def write_home():
    write_wiki(
        "Home.md",
        r"""# Agent Red Customer Experience

**AI-powered customer service for Shopify** -- a commercial SaaS product built on the [AGNTCY](https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service) open-source customer service platform.

| Attribute | Value |
|-----------|-------|
| **Owner** | Remaker Digital (DBA of VanDusen & Palmeter, LLC) |
| **Status** | All 19 cycles DEPLOYED. v1.80.0 PRODUCTION. v1.80.0 STAGING. Quality hardening IN PROGRESS. |
| **Production Version** | v1.80.0 (2026-03-08, ACR ca4q) |
| **Staging Version** | v1.80.0 (ACR ca4q, 3 tenants, `agent-red-staging`) |
| **Production** | API Gateway (Azure Container Apps, East US) |
| **Storefront** | [blanco-9939.myshopify.com](https://blanco-9939.myshopify.com) (tenant #1) |
| **Documentation** | [agentredcx.com](https://agentredcx.com) |

## Quick Links

- [[Architecture]] -- 7-agent AI pipeline (6 customer + 1 admin Co-Pilot), AGNTCY integration, Azure infrastructure
- [[Co-Pilot Agent]] -- Admin-facing AI assistant for merchant configuration (v1.80.0)
- [[AGNTCY-Platform-Adoption]] -- Phases 1-3+5+6 complete: MCP client, Stripe, Shopify, OTel tracing, PII tokenization
- [[Admin-UI]] -- Multi-surface admin (Shopify Polaris, Standalone Mantine, Provider SPA) with Save-Activate model
- [[Provider-Console]] -- 20-page platform operations dashboard with alerting, incidents, MFA, user management
- [[SPA-Operations-Guide]] -- **NEW** Step-by-step guide for SPA operators (tenant management, monitoring, reporting)
- [[Deployment]] -- ACR build, initialization, upgrade/rollback procedures
- [[Changelog]] -- Release history from v1.0.0 through v1.80.0
- [[Save and Activate]] -- Two-phase commit model for configuration changes
- [[API Reference]] -- All API route groups with endpoint counts
- [[Testing Strategy]] -- 5,984 offline + 936 live E2E tests
- [[Test Coverage]] -- Quality metrics dashboard with assertion coverage and traceability
- [[Conversation-Quality]] -- Golden dataset, quality pilot, evaluation framework
- [[Knowledge-Automation]] -- Storefront ingestion, industry templates, config suggestions, onboarding wizard
- [[Production Infrastructure]]
- [[Shopify Integration]]
- [[Pricing & Tiers]]

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Models** | Azure OpenAI: GPT-4o (responses + Co-Pilot), GPT-4o-mini (classification, critic, escalation), text-embedding-3-large (vectors) |
| **Backend** | Python 3.14+ / FastAPI, 23+ routers, ~140+ routes, 9 middleware layers |
| **Agent Framework** | AGNTCY SDK (AgentRedBaseAgent extending BaseAgentProtocol), A2A protocol |
| **MCP Integration** | `mcp` SDK v1.26.0 (HTTP transport), Shopify Storefront + Stripe MCP servers |
| **Database** | Azure Cosmos DB (Serverless, NoSQL, DiskANN vector search, 20 containers incl. admin_documentation_vectors + pii_token_mappings + platform_admins) |
| **Infrastructure** | Azure Container Apps, NATS (event bus), Key Vault (secrets), Container Registry |
| **Chat Widget** | Preact + TypeScript (~17KB gzip), Shadow DOM, SSE streaming, admin mode for Co-Pilot |
| **Admin (Shopify)** | Polaris 12 + App Bridge (embedded) |
| **Admin (Standalone)** | Mantine v7 + React (API key auth) |
| **Admin (Provider)** | Mantine v7 + React + Recharts (superadmin multi-tenant) |
| **Knowledge DB** | Append-only SQLite (1,878 specs, 8,819 tests, 1,093 WIs), read-only web UI |
| **IaC** | Terraform (Azure) |

## Project Metrics (2026-03-08)

| Metric | Value |
|--------|-------|
| Offline tests | 5,984 passed, 1 known fail |
| Live E2E | 936 tests across 3 admin consoles (Standalone 576, Provider 264, Shopify 96) |
| Testable elements | 520 inventoried across 12 subsystems |
| Live config pipeline | 26/26 PASS |
| Load test | 4,859 requests, 0 failures (progressive load testing) |
| Quality evaluation | 25 scenarios, 4.40/5.0 average |
| Specifications | 1,878 (1,345 implemented, 313 verified, 60 specified, 159 retired) |
| Work items | 1,093 (16 open, 978 resolved, 35 verified, 56 wont_fix) |
| Test artifacts | 8,819 |
| KB documents | 145 |
| Operational procedures | 13 |
| Assertion coverage | 99.7% (1,862/1,868) |
| Assertion pass rate | 100% |
| Test traceability | 100% (8,819/8,819) |
| AGNTCY Phases | 1-3+5+6 complete (Phase 4 skip) |

## Current Phase: Quality Hardening + Beta Deployment

Production is running v1.80.0 (SPA Multi-Admin Hierarchy + Login Notifications + Emergency Key Recovery + Tenant Account Recovery). All quality gates at ceiling. SPA platform admin key seeded in Key Vault.

**Release Plan status:**
- Steps 1-3: COMPLETE (Master Test Plan, release freeze, beta tenant provisioning)
- Step 4: IN PROGRESS (beta feedback collection)
- Step 5: VERIFIED (staging v1.62.0-rc2, multi-tenant upgrade 70/70 PASS)
- Steps 5.5-6: COMPLETE (v1.62.0 deployed to production, S125; upgraded through v1.80.0)

**Recent milestones (S157-S158):**
- **S158**: SPA Multi-Admin Hierarchy (SPEC-1675), Login Notification Emails (SPEC-1676), Emergency Key Recovery (SPEC-1678), Tenant Account Recovery (SPEC-1677), deployed v1.80.0 to production, comprehensive documentation update to agentredcx.com
- **S157**: SPA Console Authentication Isolation (SPEC-1667/1668), SPA key regeneration (SPEC-1669), platform admin rate limit exemption, human-readable tenant IDs, progressive load testing (4,859 requests, 0 failures), deployed v1.79.2 to production
- **S156**: CORS middleware ordering fix (429s include CORS headers), widget HTTP retry with exponential backoff, deployed v1.76.0 backend + widget v23
- SPEC-1652 Quality Cycle COMPLETE -- 520 elements inventoried, 576 standalone + 264 provider + 96 Shopify live E2E tests
- Quality metrics at ceiling -- assertion coverage 99.7%, pass rate 100%, traceability 100%

---

*&copy; 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last updated: 2026-03-08*
""",
    )


# ---------------------------------------------------------------------------
# 2. Changelog.md — prepend v1.80.0 entry
# ---------------------------------------------------------------------------
def write_changelog():
    existing = (WIKI / "Changelog.md").read_text(encoding="utf-8")
    # Find the first "## v1.79" entry and insert before it
    marker = "## v1.79.2"
    new_entry = r"""## v1.80.0 PRODUCTION (2026-03-08, Session 158) -- SPA MULTI-ADMIN + SECURITY HARDENING

**ACR Image:** ca4q. Production + Staging.

### SPA Multi-Admin Hierarchy (SPEC-1675)
- Multiple platform admin users with superadmin/operator roles
- Superadmin: full access including user management (create/deactivate operators)
- Operator: full access to SPA features except user management
- `require_spa_superadmin()` guard for user management endpoints
- `platform_admin_role` field on TenantContext (populated by middleware)
- User Management page in Provider console: table listing admins, role badges, last login tracking
- `POST /api/superadmin/platform-admin/users` — create operator (returns API key once)
- `DELETE /api/superadmin/platform-admin/users/{admin_id}` — deactivate operator
- `GET /api/superadmin/platform-admin/users` — list all platform admins

### Login Notification Emails (SPEC-1676)
- Non-blocking email notification on every SPA auth success
- Contains: timestamp, IP address, user agent string
- Configurable notification address per admin (defaults to admin's email)
- `PUT /api/superadmin/platform-admin/users/notification-email` — set notification address
- Uses Azure Communication Services email delivery
- Login never blocked by email failure (fire-and-forget pattern)

### Emergency Key Recovery with Backup Codes (SPEC-1678)
- 8 single-use hex recovery codes (SHA-256 hashed in Cosmos)
- `POST /api/superadmin/platform-admin/users/backup-codes` — generate codes (shown once)
- Unauthenticated recovery: `POST /api/auth/spa-recovery/recover`
- Rate limited: 3 attempts per 15 min per IP
- Constant-time response prevents account enumeration
- New key delivered via email (never in API response)
- Audit trail via `SECURITY_EVENT` logging

### Tenant Account Recovery (SPEC-1677)
- SPA can activate a recovery email address for any tenant
- `POST /api/superadmin/tenant-recovery/activate` — set recovery email
- `POST /api/superadmin/tenant-recovery/send-auth-link` — send one-time auth link
- Token: 15-minute TTL, single-use, stored in `verification_tokens` collection
- Recovery session grants tenant superadmin access
- `GET /api/superadmin/tenant-recovery/status/{tenant_id}` — check recovery address status

### Documentation Site Update
- 10 pages updated on [agentredcx.com](https://agentredcx.com): setup wizard, KB optimization, URL import, quick actions tuning, escalation tuning, inbox management, team management, security guide, integrations (5 platforms with full setup guides), widget installation (7 platforms)
- 3 pages completely rewritten: Securing Agent Red, Integrations, Widget Installation

---

"""
    if marker in existing:
        updated = existing.replace(marker, new_entry + marker)
    else:
        # fallback: insert after header
        updated = existing.replace("---\n\n##", "---\n\n" + new_entry + "##", 1)

    write_wiki("Changelog.md", updated)


# ---------------------------------------------------------------------------
# 3. Project-Status.md — update version + add S158
# ---------------------------------------------------------------------------
def write_project_status():
    existing = (WIKI / "Project-Status.md").read_text(encoding="utf-8")
    # Update version references
    updated = (
        existing.replace("> Last updated: 2026-03-08 (S157)", "> Last updated: 2026-03-08 (S158)")
        .replace("v1.79.2 (ACR ca4n, revision 0000093, deployed 2026-03-08)", "v1.80.0 (ACR ca4q, deployed 2026-03-08)")
        .replace("v1.79.2 (ACR ca4n, 3 tenants, scales to zero)", "v1.80.0 (ACR ca4q, 3 tenants, scales to zero)")
    )
    write_wiki("Project-Status.md", updated)


# ---------------------------------------------------------------------------
# 4. Provider-Console.md — complete rewrite with 20 pages
# ---------------------------------------------------------------------------
def write_provider_console():
    write_wiki(
        "Provider-Console.md",
        r"""# Provider Console

> Last updated: 2026-03-08 (S158, v1.80.0 production)

The Provider Console is a single-page application (SPA) for **platform administrators** managing multiple Agent Red tenants. It is distinct from the Standalone Admin (merchant-facing) and Shopify Admin (merchant-facing). The Provider Console is used by the platform operator (Remaker Digital) and its team for multi-tenant monitoring, incident management, alerting, compliance oversight, and user management.

**Important:** The Provider Console is an internal operations tool. It is NOT documented on the public documentation site (agentredcx.com) — only in this private wiki and in the product documentation at [[SPA-Operations-Guide]].

## Access

- **URL:** `/admin/provider/`
- **Auth:** API key (`ar_spa_plat_` prefix) → optional MFA/TOTP challenge → 8-hour JWT session
- **Storage:** `sessionStorage` (`agentred_provider_key`, `agentred_provider_mfa_token`)
- **Roles:** Superadmin (full access + user management) or Operator (full access, no user management)

## Architecture

| Component | Technology |
|-----------|-----------|
| **Framework** | React 18 + Mantine v7 |
| **Charts** | Recharts (lazy-loaded) |
| **Build** | Vite 6 (974KB / ~280KB gzip) |
| **Auth** | Three-state: `login` → `mfa_challenge` → `authenticated` |
| **Backend** | Superadmin API (`src/multi_tenant/superadmin_api.py`) — 40+ endpoints |
| **API convention** | All responses use camelCase field names |

### Three Admin Surfaces

Agent Red has **three** admin interfaces, each serving a different audience:

| Surface | Audience | Technology | Auth |
|---------|----------|-----------|------|
| **Shopify Embedded Admin** | Merchants using Shopify | Polaris 12 + App Bridge | Shopify session |
| **Standalone Admin** | Merchants not on Shopify | Mantine v7 + React | API key or magic link |
| **Provider Console (SPA)** | Platform administrators | Mantine v7 + React + Recharts | API key → MFA → JWT |

The Standalone Admin and Provider Console share Mantine v7 as their UI framework, but they are separate builds with different routes, authentication, and capabilities. The Provider Console has cross-tenant visibility; the Standalone Admin is single-tenant.

## Pages (20 total)

### Overview Group (2 pages)

| Page | Route | Purpose |
|------|-------|---------|
| **Health Dashboard** | `/` | Infrastructure health (NATS, Key Vault, circuit breakers), tenant distribution by status/tier, recent deployments |
| **Tenant Directory** | `/tenants` | Paginated tenant list with filters (status/tier/billing channel), tenant provisioning, expiry management, welcome email resend |

### Operations Group (10 pages)

| Page | Route | Purpose |
|------|-------|---------|
| **Deployments** | `/deployments` | Deployment event log (deploy/rollback type, actor, timestamp, JSON payload) |
| **Queue Health** | `/queues` | NATS queue depth per tenant, message/byte counts, consumer health badges |
| **Integration Health** | `/integrations` | Circuit breaker states per downstream service, MCP connection gauges |
| **Status Page** | `/status` | Incident CRUD (create, update, resolve), severity badges, timeline view |
| **Alerts** | `/alerts` | Alert rule CRUD (5 types), history with acknowledge, "Evaluate Now" trigger |
| **Support Diagnostics** | `/diagnostics` | Per-tenant deep dive: config state, AI config, KB stats, team, conversations, errors |
| **Co-Pilot Knowledge** | `/copilot-knowledge` | Document CRUD, batch ingestion, URL import, schedule, hybrid search tuning |
| **Pipeline Observatory** | `/pipeline` | Traffic flow with 7 agent nodes, agent metrics (P50/P95/P99), tenant comparison |
| **Contact Messages** | `/contact-messages` | Inbound support messages with topic/status filters, detail modal, CSV export |
| **Service Messages** | `/service-messages` | Broadcast emails to filtered tenant sets with preview and BCC delivery |

### Compliance & Security Group (6 pages)

| Page | Route | Purpose |
|------|-------|---------|
| **Compliance** | `/compliance` | PII scrubbing adoption, grace period tracking, DSAR request counts |
| **Secrets** | `/secrets` | Key Vault secret inventory per tenant, secret type breakdown, disabled secret detection |
| **Billing** | `/billing` | Billing health per tenant, reconciliation status, webhook success rate |
| **Cost Analytics** | `/costs` | Platform-wide and per-tenant cost breakdown (AI cost + DB cost), cost-per-conversation |
| **SLA Trends** | `/sla` | Uptime %, P50/P95/P99 latency trends, error budget gauges per tier |
| **Abuse Detection** | `/abuse` | Risk scoring (0-100), 5 signal types, high-risk tenant table, flag/unflag actions |

### Account Group (2 pages)

| Page | Route | Purpose |
|------|-------|---------|
| **User Management** | `/users` | Platform admin CRUD (superadmin creates/deactivates operators), backup code generation, notification email config |
| **MFA Settings** | `/mfa` | TOTP enrollment (QR code + backup codes), disable with TOTP verification |

## SPA User Hierarchy (SPEC-1675)

v1.80.0 introduced multi-admin support for the Provider Console:

| Role | Access | Can manage users? |
|------|--------|-------------------|
| **Superadmin** | Full access to all SPA features including user management | Yes — can create and deactivate operators |
| **Operator** | Full access to SPA features except user management | No — cannot create or remove other admins |

The superadmin account is created automatically when Agent Red is provisioned. Additional operator accounts are created by the superadmin via the User Management page.

### Key lifecycle operations

- **Create operator:** Superadmin enters email + display name → system generates API key → key shown once in modal with copy button
- **Deactivate operator:** Superadmin clicks Remove → confirmation modal → API key immediately invalidated
- **Self-service:** All admins can set their own notification email and generate backup recovery codes
- **Cannot delete:** The superadmin account cannot be deleted. Admins cannot delete their own account.

## Login Notification Emails (SPEC-1676)

Every SPA login triggers a non-blocking email notification containing:
- Timestamp of the login
- IP address of the login source
- User agent (browser/client information)

Notifications are sent to the admin's configured notification email address (or their account email if not configured). Login is never blocked by email delivery failure.

## Emergency Key Recovery (SPEC-1678)

If an admin loses their API key, they can recover access using backup codes:

1. Generate backup codes from the User Management page (8 single-use codes, shown once)
2. On the login page, click "Lost access? Use a backup code"
3. Enter email + backup code → system generates new API key and emails it
4. Rate limited: 3 attempts per 15 min per IP
5. Response is always the same generic message (prevents account enumeration)

## Tenant Account Recovery (SPEC-1677)

SPA operators can help tenants recover access:

1. Navigate to Tenant Directory → select tenant → "Set Recovery Address"
2. Enter the merchant's recovery email address
3. When the tenant contacts support: click "Send Auth Link" → one-time link sent to recovery email
4. Link expires after 15 minutes, single-use
5. Tenant clicks link → authenticated into their admin console with superadmin access

## Alerting Engine

5-minute background evaluation loop with 6 metric collectors:

| Rule Type | Trigger |
|-----------|---------|
| `queue_depth` | Queue exceeds depth threshold |
| `secret_expiry` | Key Vault secret within expiry window |
| `circuit_breaker` | External service circuit breaker trips |
| `sla_breach` | Error budget drops below threshold |
| `incident` | New incident or severity escalation |

**Severity auto-derivation:**
- `circuit_breaker >= 2 trips = critical`
- `sla <5% error budget = critical`
- `>= 2x threshold = critical`

Cooldown enforcement prevents alert fatigue — each rule type has a configurable cooldown period during which re-firing is suppressed.

## Incident Management

**Lifecycle:** Open → Update (investigating/identified/monitoring) → Resolved

| Feature | Detail |
|---------|--------|
| **Affected services** | API, Widget, NATS, Key Vault, MCP, Admin Console, Cosmos DB |
| **Severity levels** | Critical, Major, Minor |
| **TTL** | 365-day TTL on incident documents |
| **Public API** | `GET /api/status` (no auth) — returns `overall_status` + `active_incidents` |
| **Timeline** | Each incident tracks a timeline of status updates with messages |

## MFA/TOTP

Two-factor authentication protects Provider Console access:

| Component | Detail |
|-----------|--------|
| **TOTP seed** | Stored in Key Vault (`user-{member_id}-totp-seed`) |
| **Session token** | JWT HS256, 8-hour lifetime, `type="mfa_session"` |
| **Backup codes** | 10 codes, 8 characters each, SHA-256 hashed, single-use |
| **QR setup** | Standard TOTP QR code for authenticator app enrollment |
| **Enrollment** | 3-step wizard: QR scan → save backup codes → verify TOTP code |
| **Disable** | Requires valid TOTP code to disable (prevents unauthorized removal) |
| **Brute-force mitigation** | Rate limiting on verification attempts |

## Backend API

The Provider Console is backed by the Superadmin API (`src/multi_tenant/superadmin_api.py`) which provides 40+ endpoints covering:

- Tenant lifecycle management (list, create, update status, tier override, expiry management)
- Health aggregation (system health, integration health, queue health)
- Deployment history
- Alert rule CRUD + evaluation
- Incident lifecycle (create, update, resolve)
- Compliance scoring
- Secret posture
- Billing health
- SLA metrics
- Cost analytics
- Abuse detection and flagging
- MFA management (setup, verify, disable, backup codes)
- Platform admin user management (SPEC-1675)
- Emergency key recovery (SPEC-1678)
- Tenant account recovery (SPEC-1677)
- Contact message management + CSV export
- Service message broadcast
- Co-Pilot knowledge management + batch ingestion
- Pipeline observability (traffic, agent metrics, tenant comparison)
- Support diagnostics per tenant

All endpoints require SPA authentication (`ar_spa_` key prefix). User management endpoints additionally require superadmin role.

## Null-Safety Pattern

A critical implementation pattern across all Provider Console pages: every API response field that could be null or undefined must use defensive null coalescing:

```typescript
Object.entries(field ?? {})  // Always guard against null/undefined
```

This is because aggregate API responses may have empty objects for tenants with no data. 8 pages required null-safety fixes during Provider Console Phase 2 hardening (S83).

## Implementation History

| Phase | Session/Cycle | Deliverables |
|-------|--------------|-------------|
| Phase 1 | Cycle 7 (S39), v1.42.0 | Scaffold, login, 5 data pages (Health, Tenants, Deployments, Queue, Integrations) |
| Phase 2 | Cycle 9 (S40-41), v1.43.0 | 4 additional pages, incidents, alerting, MFA, grouped sidebar navigation |
| Phase 3-4 | Cycle 12 (S42-46), v1.46.0 | Support diagnostics, cost analytics, abuse detection, contact/service messages, Co-Pilot knowledge, pipeline observatory |
| Hardening | S83, v1.57.5 | 7 null-safety fixes, NATS false alarm fixes, SPA logo catch-all |
| camelCase fix | S59, v1.51.0 | 6 pages corrected to match API camelCase response format |
| SPA Auth Isolation | S157, v1.79.0 | SPEC-1667/1668: separate `platform_admins` collection, `ar_spa_` key prefix, router-level guards |
| Multi-Admin + Security | S158, v1.80.0 | SPEC-1675/1676/1677/1678: user hierarchy, login notifications, backup codes, tenant recovery |

---

*&copy; 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
""",
    )


# ---------------------------------------------------------------------------
# 5. SPA-Operations-Guide.md — NEW: novice-friendly SPA operator guide
# ---------------------------------------------------------------------------
def write_spa_operations_guide():
    write_wiki(
        "SPA-Operations-Guide.md",
        r"""# SPA Operations Guide

> A step-by-step guide for platform administrators (SPA operators) managing the Agent Red Provider Console.

This guide is written for someone who is new to the Provider Console. It covers the most common tasks: creating and managing tenants, generating reports, monitoring for outages, monitoring for abuse, tracking costs, and managing SPA user accounts.

## Getting started

### Logging in

1. Open the Provider Console at `/admin/provider/`.
2. Enter your SPA API key (starts with `ar_spa_plat_`).
3. If MFA is enabled, enter the 6-digit TOTP code from your authenticator app.
4. You are now in an authenticated session that lasts 8 hours.

**If you lost your API key:** Click "Lost access? Use a backup code" on the login page. Enter your email and one of your backup codes. A new API key will be sent to your email.

### Understanding the sidebar

The sidebar is organized into 4 groups with 20 pages total:

| Group | Pages | Purpose |
|-------|-------|---------|
| **Overview** | Health Dashboard, Tenant Directory | System health and tenant management |
| **Operations** | 10 pages | Day-to-day monitoring and incident management |
| **Compliance & Security** | 6 pages | Security posture, billing, costs, abuse |
| **Account** | User Management, MFA Settings | Your account and team accounts |

---

## Creating and managing tenants

### Provisioning a new tenant

1. Navigate to **Tenant Directory** in the sidebar.
2. Click **Add Tenant** (top right).
3. Fill in the form:
   - **Merchant Name** — the store or business name
   - **Merchant URL** — the store's website URL
   - **Superadmin Email** — the merchant's primary email (receives welcome email + API keys)
   - **Tier** — Starter, Professional, or Enterprise
   - **Expiry** (optional) — set a trial or subscription end date
4. Click **Create**.
5. A modal appears with the tenant's **API key** and **widget key**. Copy both immediately — they are only shown once.
6. The system sends a welcome email to the merchant with their credentials.

### Viewing tenant details

The Tenant Directory shows a table with all tenants. Each row displays:
- **Tenant name** — human-readable identifier (derived from email domain)
- **Status** — Active, Provisioning, Trial Expired, Past Due, Grace Period, or Deactivated
- **Tier** — Starter, Professional, or Enterprise
- **Billing channel** — How the tenant is billed
- **Email** — merchant's primary email
- **Created** — when the tenant was provisioned
- **Expiry** — subscription end date (color-coded: red if 7 days or fewer, orange if 30 days or fewer)

### Filtering tenants

Use the filter bar above the table:
- **Status** dropdown — filter by Active, Trial Expired, Past Due, etc.
- **Tier** dropdown — filter by Starter, Professional, Enterprise
- **Billing Channel** dropdown — filter by billing type

### Managing subscription expiry

Click the three-dot menu on any tenant row to access:
- **Set Expiry** — opens a date picker to set a specific expiry date
- **Extend 30 Days** — adds 30 days from today (quick extension)
- **Remove Expiry** — removes the expiry entirely (makes the subscription indefinite)

### Resending the welcome email

If a merchant lost their welcome email, click the three-dot menu on their row and select **Resend Welcome Email**.

### Running diagnostics on a tenant

If a merchant reports issues, use **Support Diagnostics** (Operations group):
1. Enter the tenant ID in the search box.
2. Click **Run Diagnostics**.
3. Review the results: configuration state, AI config completeness, knowledge base stats, team members, recent conversation counts, integration connectivity.
4. Click **Load Errors** to see recent error events.

---

## Generating reports

### Cost report

Navigate to **Cost Analytics** (Compliance & Security group):
1. Select a time range: 7, 30, 90, or 365 days.
2. View platform-wide totals: Total Platform Cost, Total Conversations, Avg Cost per Tenant, Avg Cost per Conversation.
3. Review the per-tier breakdown (Starter / Professional / Enterprise costs).
4. The tenant table shows per-tenant details: conversation count, token usage (input/output), article accesses, AI cost, DB cost, total cost, per-conversation cost, and share of platform total.

### SLA report

Navigate to **SLA Trends** (Compliance & Security group):
1. Select a time range: 1 day, 7 days, 30 days, or 90 days.
2. View the **Uptime** chart (domain: 99-100%, green line with 99.9% reference line).
3. View **Response Latency** chart with P50/P95/P99 lines.
4. Review **Error Budget** gauges per tier — shows allowed vs actual downtime in minutes and whether the budget is within limits or exceeded.
5. View **Request Volume** chart showing traffic patterns over time.

### Pipeline performance report

Navigate to **Pipeline Observatory** (Operations group):
1. **Traffic Flow** tab: Select time range (1h/24h/7d/30d). View total conversations and per-agent metrics (invocations, avg latency, tokens, cost). Review agent-to-agent transitions showing volume and drop-off rates.
2. **Agent Metrics** tab: Detailed per-agent cards with P50/P95/P99 latency, error rate, and token usage.
3. **Tenant Comparison** tab: Sortable table comparing all tenants by conversations, latency, error rate, escalation rate, token usage, cost, and estimated RU.

### Contact message export

Navigate to **Contact Messages** (Operations group):
1. Filter by topic (support, feature request, billing, bug report, general) and status (new, read, resolved, archived).
2. Click **Export CSV** to download matching messages as a spreadsheet.

---

## Monitoring for outages

### Daily health check routine

1. **Start with the Health Dashboard** (the default page when you log in):
   - Check NATS status: should show "Connected" (green). "Disconnected" = event bus is down.
   - Check Key Vault status: should show "Healthy". "Degraded" = secret retrieval may fail.
   - Check Circuit Breakers: all should be "Closed". "Open" breakers mean a downstream service is failing.

2. **Check Integration Health** (Operations group):
   - The banner should show "All Systems Healthy" (green).
   - Review circuit breaker cards: Closed (green) = normal, Half Open (yellow) = recovering, Open (red) = failing.
   - Check MCP Integration gauges: the ring should be mostly filled (green = connected).

3. **Check Queue Health** (Operations group):
   - Message count cards: green (<100), orange (100-1000), red (>1000).
   - Per-tenant health badges: "Healthy", "Elevated" (warning), or "Critical" (intervention needed).

### When something goes wrong

If you see unhealthy indicators:

1. **Create an incident** on the **Status Page** (Operations group):
   - Click **Create Incident**.
   - Enter a title and description.
   - Select severity: Critical (full outage), Major (degraded service), Minor (minor impact).
   - Select affected services (API, Widget, NATS, Key Vault, MCP, Admin Console, Cosmos DB).
   - Click **Create**.

2. **Add status updates** as you investigate:
   - Click **Add Update** on the incident.
   - Select the current status: Investigating → Identified → Monitoring → Resolved.
   - Add a message describing what you found or what was done.

3. **Resolve the incident** when the issue is fixed:
   - Click **Resolve** on the incident card.

### Setting up proactive alerts

Navigate to **Alerts** (Operations group):

1. Click **New Rule**.
2. Fill in the form:
   - **Name** — descriptive name (e.g., "High queue depth")
   - **Rule Type** — queue_depth, secret_expiry, circuit_breaker, sla_breach, or incident
   - **Condition** — metric, operator, and threshold (e.g., queue_depth > 1000)
   - **Cooldown** — minutes between re-fires (prevents alert fatigue)
   - **Runbook URL** (optional) — link to resolution instructions
3. Click **Save**.

The system evaluates all alert rules every 5 minutes. When a rule fires, it appears in the **History** tab with severity badge and triggered value. Click **Acknowledge** to mark an alert as seen.

You can also click **Evaluate Now** to trigger immediate evaluation of all rules.

---

## Monitoring for abuse

Navigate to **Abuse Detection** (Compliance & Security group):

### Understanding the dashboard

The dashboard shows 3 summary cards:
- **Tenants Scanned** — total tenants analyzed
- **Flagged** — tenants currently under investigation
- **High-Risk** — tenants with risk scores above threshold

Below the summary, you see breakdowns for 5 signal types:
- **rate_anomaly** — unusual request rate patterns
- **volume_spike** — sudden increase in conversation volume
- **widget_abuse** — suspicious widget usage patterns
- **token_exhaustion** — excessive AI token consumption
- **error_rate** — abnormally high error rates

### Identifying at-risk tenants

The high-risk tenant table shows:
- **Tenant** — human-readable name
- **Risk Score** — 0 to 100 (green <30, orange 30-70, red >70)
- **Signals** — severity badges for detected issues (critical/high/medium/low)
- **Flagged** — whether the tenant is currently flagged for investigation

### Taking action

- Click **Flag** on a tenant row to mark them for investigation.
- Click **Unflag** to remove the investigation marker.
- Click **Rescan** to trigger a fresh analysis of all tenants.

### What to look for

| Signal | Possible cause | Action |
|--------|---------------|--------|
| Rate anomaly | Bot traffic, misconfigured widget | Check widget installation, consider rate limit adjustment |
| Volume spike | Marketing campaign, viral content, attack | Verify with merchant, monitor for sustained abuse |
| Widget abuse | Automated testing, scraping | Review tenant's widget configuration |
| Token exhaustion | Long conversations, knowledge base issues | Check KB quality, conversation turn limits |
| Error rate | Integration failures, configuration issues | Run Support Diagnostics on the tenant |

---

## Monitoring for cost changes

Navigate to **Cost Analytics** (Compliance & Security group):

### Tracking platform costs

1. Select **30 days** to see monthly trends (or 7/90/365 for other windows).
2. The top 4 cards show platform-wide totals: Total Platform Cost, Total Conversations, Avg Cost per Tenant, Avg Cost per Conversation.
3. The tier breakdown shows cost distribution across Starter / Professional / Enterprise tiers.

### Identifying cost outliers

In the per-tenant table, look for:
- **High total cost** — tenants consuming disproportionate resources
- **High per-conversation cost** — tenants with expensive conversations (may indicate KB quality issues or excessive token usage)
- **High share %** — tenants representing a large fraction of platform cost

Sort the table by any column to identify outliers (click column headers).

### Cost optimization signals

| Indicator | Possible cause | Action |
|-----------|---------------|--------|
| High input tokens | Large knowledge base articles being retrieved | Optimize KB: shorter, more focused articles |
| High output tokens | Verbose AI responses | Adjust brand voice instructions |
| High article accesses | Poor article relevance scoring | Improve article titles, check for duplicate/conflicting articles |
| High DB cost relative to AI cost | Many conversations with low token usage | Normal for high-volume, simple query workloads |

---

## Managing SPA user accounts

Navigate to **User Management** (Account group).

> Note: Only superadmins can create and deactivate operators. Operators can manage their own notification email and backup codes but cannot manage other accounts.

### Viewing current accounts

The users table shows:
- **Display Name** — operator's name
- **Email** — account email
- **Role** — Superadmin (red badge) or Operator (blue badge)
- **Backup Codes Remaining** — number of unused recovery codes
- **Last Login** — most recent authentication timestamp
- **Remove** button — visible only to superadmins, and only on operator rows

### Adding a new operator

1. Click **Add Operator** (superadmin only).
2. Enter the operator's **email address** and **display name**.
3. Click **Create**.
4. A modal shows the new operator's **API key** — copy it immediately. It is only shown once.
5. Send the key securely to the new operator (use a password manager, encrypted message, or in-person handoff — never plain email).

### Removing an operator

1. Find the operator in the users table.
2. Click **Remove**.
3. A confirmation modal warns that the operator's API key will stop working immediately.
4. Click **Deactivate** to confirm.
5. The operator can no longer log in.

### Setting your notification email

1. In the notification email card at the top of the page, click **Edit** (pencil icon).
2. Enter the email where you want login notifications sent (e.g., a shared security inbox).
3. Click **Save**.

Every time you (or anyone) log in with your API key, a notification email is sent to this address with the login timestamp, IP address, and browser information.

### Generating backup codes

1. Click **Generate Backup Codes**.
2. A modal shows 8 recovery codes in a numbered list.
3. Click **Copy All** to copy them to your clipboard.
4. **Save these codes in a secure location** (password manager or printed in a safe). They cannot be retrieved again.
5. Each code is single-use — after using one to recover your API key, it is consumed.

### Setting up MFA

Navigate to **MFA Settings** (Account group):

1. Click **Enable MFA**.
2. **Step 1:** Scan the QR code with your authenticator app (Google Authenticator, Authy, 1Password). Or click the manual entry option and type the secret key.
3. **Step 2:** Save the 10 backup codes displayed in a 2-column grid. Click **Download as .txt** to save them as a file.
4. **Step 3:** Enter the 6-digit code from your authenticator app to verify.
5. MFA is now active. Every future login requires your API key + TOTP code.

To disable MFA: Click **Disable MFA** and enter a valid TOTP code to confirm.

---

## Sending service messages to merchants

Navigate to **Service Messages** (Operations group):

1. Enter a **Subject** (max 200 characters).
2. Enter a **Body** (HTML supported, max 10,000 characters).
3. Filter recipients by **Tenant Status** and/or **Subscription Tier** (multi-select).
4. Click **Preview Recipients** — a table shows matching tenants with email, tier, and status.
5. Review the recipient list and unique email count.
6. Click **Send Service Message** — a confirmation modal shows the recipient count and subject.
7. Confirm to send. Messages are delivered via BCC.
8. The result banner shows success count or lists any delivery errors.

Click **Reset** to clear the form and start over.

---

## Helping a merchant who is locked out

If a merchant contacts you because they cannot log in:

### Option 1: Resend welcome email

1. Go to **Tenant Directory**.
2. Find the merchant's tenant row.
3. Click the three-dot menu → **Resend Welcome Email**.

### Option 2: Set up account recovery

1. Go to **Tenant Directory**.
2. Find the merchant's tenant → click **Set Recovery Address** (in the three-dot menu or tenant detail).
3. Enter the merchant's recovery email address and save.
4. Click **Send Auth Link** — a one-time authentication link is sent to the recovery email.
5. Tell the merchant to check their email and click the link within 15 minutes.
6. The link grants superadmin access to their admin console, where they can regenerate API keys for their team.

---

## Daily operator checklist

| Time | Task | Page |
|------|------|------|
| **Morning** | Check Health Dashboard for red indicators | Health Dashboard |
| **Morning** | Review alert history for overnight fires | Alerts (History tab) |
| **Morning** | Check for new contact messages | Contact Messages |
| **Morning** | Review abuse detection for newly flagged tenants | Abuse Detection |
| **Midday** | Check queue health for elevated/critical tenants | Queue Health |
| **Midday** | Review any active incidents and update status | Status Page |
| **End of day** | Check cost analytics for anomalies | Cost Analytics |
| **Weekly** | Review SLA trends and error budgets | SLA Trends |
| **Weekly** | Review compliance dashboard for adoption metrics | Compliance |
| **Weekly** | Check secret posture for expiring secrets | Secrets |

---

*&copy; 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last updated: 2026-03-08*
""",
    )


# ---------------------------------------------------------------------------
# 6. _Sidebar.md — add new pages
# ---------------------------------------------------------------------------
def write_sidebar():
    write_wiki(
        "_Sidebar.md",
        r"""**[[Home]]**

---

### Status & Tracking
- [[Project Status]]
- [[Specifications]]
- [[Release Plan]]
- [[Changelog]]
- [[Defect Log]]

### Architecture
- [[Architecture Overview]]
- [[AGNTCY Platform Adoption]]
- [[Co-Pilot Agent]]
- [[Knowledge Database]]
- [[Save and Activate]]
- [[Production Infrastructure]]
- [[Provider Console]]
- [[Scaling Analysis]]
- [[Persistent Customer Memory]]
- [[RAG Infrastructure]]
- [[Configuration System]]
- [[API Reference]]

### Provider Console (SPA)
- [[Provider Console]]
- [[SPA Operations Guide]]

### Operations
- [[Repeatable Procedures]]
- [[Deployment Guide]]
- [[Upgrade Procedures]]
- [[Azure Deployment Guide]]
- [[Operations Deployment Runbook]]
- [[Operations Release Management]]

### Quality Assurance
- [[Testing Strategy]]
- [[Test Coverage]]
- [[Conversation Quality]]
- [[QA UI Test Results]]
- [[QA Comprehensive Test Plan]]

### Shopify
- [[Shopify Integration]]
- [[Shopify App Store Listing]]
- [[Shopify App Review Preflight Checklist]]

### Product
- [[Pricing & Tiers]]
- [[Brand Guidelines]]
- [[Design Reference Guide]]

### Specifications
- [[Chat Widget Specification]]
- [[Admin Dashboard Specification]]
- [[Docs Billable Conversation Spec]]

### UX/Design
- [[UX Specialist Access]]
- [[Workflow Storefront Overview]]
- [[Workflow Embedded Admin Dashboard]]
- [[Workflow Widget Activation]]

### Research
- [[Architecture E Commerce Platform Evaluation]]
- [[Architecture AI Personalization Research]]
- [[Architecture Master Plan Review]]
- [[Architecture UI UX Decisions]]
- [[Architecture RAG Gap Analysis]]
- [[Research UI UX Competitive Analysis]]

### Legal
- [[Legal Terms of Service]]
- [[Legal Privacy Policy]]
- [[Legal Service Level Agreement]]
- [[Legal Data Processing Agreement]]

### Website Content
- [[Website Homepage]]
- [[Website Features]]
- [[Website Pricing]]
- [[Website Integrations]]
- [[Website About]]
- [[Website Contact]]
""",
    )


# ---------------------------------------------------------------------------
# 7. Test-Coverage.md — update version
# ---------------------------------------------------------------------------
def write_test_coverage():
    existing = (WIKI / "Test-Coverage.md").read_text(encoding="utf-8")
    # Update versions
    updated = existing
    for old, new in [
        ("v1.79.2", "v1.80.0"),
    ]:
        # Only update in header/summary areas, not in detailed changelog-like entries
        pass  # Version references in Test-Coverage are generic test counts, not version-specific
    write_wiki("Test-Coverage.md", updated)


# ---------------------------------------------------------------------------
# 8. Defect-Log.md — add S158 entry
# ---------------------------------------------------------------------------
def write_defect_log():
    existing = (WIKI / "Defect-Log.md").read_text(encoding="utf-8")
    # S158 had no defect fixes — it was feature work. No changes needed.
    write_wiki("Defect-Log.md", existing)


# ---------------------------------------------------------------------------
# 9. Testing-Strategy.md — no changes needed (test strategy is stable)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Updating Agent Red wiki pages...")
    print()

    print("1. Home.md")
    write_home()

    print("2. Changelog.md")
    write_changelog()

    print("3. Project-Status.md")
    write_project_status()

    print("4. Provider-Console.md (full rewrite)")
    write_provider_console()

    print("5. SPA-Operations-Guide.md (NEW)")
    write_spa_operations_guide()

    print("6. _Sidebar.md")
    write_sidebar()

    print("7. Test-Coverage.md")
    write_test_coverage()

    print("8. Defect-Log.md")
    write_defect_log()

    print()
    print("All wiki pages updated successfully.")
    print("Next: cd to wiki repo and git add/commit/push")


if __name__ == "__main__":
    main()
