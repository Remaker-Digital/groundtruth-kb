# Tenant Initialization

**Type:** Repeatable Procedure (see `docs/operations/REPEATABLE-PROCEDURES.md`)
**Last verified:** 2026-02-16
**Last corrected:** 2026-02-16 — I.3 field name `status`→`state`; I.8 accepts 401 or 403 (first execution)

---

## Purpose

Initialization provisions a clean tenant with **zero pre-existing data**. After initialization, the tenant contains:

- Tenant document (active, professional tier)
- Draft preferences document (all merchant-configurable fields empty)
- Team members (superadmin + 2 escalation agents)
- Platform config (4 tier_defaults documents)
- API key + widget key (freshly generated)

The tenant does **not** contain:

- Knowledge base articles (0 articles)
- Conversations (0 conversations)
- Customer profiles or memory vectors
- Any configuration values from a prior tenant state

Initialization is a **destructive** operation. It deletes all existing data in the tenant partition before provisioning fresh documents.

---

## When to Execute

1. **Before UI testing** — Every test deployment concludes with Initialization to ensure a clean baseline.
2. **After a test build is pushed to production** — Always run Initialization before functional testing.
3. **When tenant state is unknown or contaminated** — Run Initialization to return to a known-good state.

Initialization is **not** used for production upgrades that must preserve data. See `docs/operations/upgrade-verification-procedure.md` for non-disruptive upgrades.

---

## Variables

| Variable | Value |
|----------|-------|
| `TENANT_ID` | `remaker-digital-001` |
| `SHOP_DOMAIN` | `blanco-9939.myshopify.com` |
| `FQDN` | `agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |
| `KEY_VAULT` | `kv-agentred-eastus` |
| `CONTAINER_APP` | `agent-red-api-gateway` |
| `RESOURCE_GROUP` | `Agent-Red` |
| `ADMIN_URL` | `https://{FQDN}/admin/standalone` |

---

## Pre-conditions

- Azure CLI authenticated (`az login`)
- `.env.local` contains valid `COSMOS_DB_ENDPOINT`, `COSMOS_DB_KEY`, `COSMOS_DB_DATABASE`
- CLI user has "Key Vault Secrets Officer" role on `{KEY_VAULT}`

---

## Procedure

### Step 1: Execute seed script

```powershell
python scripts/seed_tenant.py --execute
```

This runs 7 phases:
1. **Containers** — Ensures 10 Cosmos DB containers exist with correct indexes
0. **Clean** — Deletes ALL existing documents in the `{TENANT_ID}` partition (conversations, articles, preferences, team, memory — everything)
2. **Tenant** — Creates TenantDocument (active, professional) with fresh API key + widget key
3. **Preferences** — Creates draft PreferencesDocument with all merchant fields empty
6. **Platform** — Creates 4 tier_defaults documents
7. **Demo data** — Skipped (no `--demo` flag)
4. **Team** — Creates 3 team members (superadmin + 2 escalation agents) with API key hashes

**Capture the output.** The summary (Phase 8) prints:
- `ADMIN_PREVIEW_API_KEY` (superadmin key)
- `WIDGET_KEY` (publishable widget key)
- Per-user API keys for each team member

### Step 2: Update Key Vault

```powershell
az keyvault secret set --vault-name {KEY_VAULT} --name ADMIN-PREVIEW-API-KEY --value "<superadmin key from Step 1>"
```

### Step 3: Restart container revision

```powershell
az containerapp revision restart --name {CONTAINER_APP} --resource-group {RESOURCE_GROUP} --revision <current_revision>
```

To find the current revision:
```powershell
az containerapp revision list --name {CONTAINER_APP} --resource-group {RESOURCE_GROUP} --query "[?properties.active].name" -o tsv
```

### Step 4: Wait for revision to become healthy

```powershell
# Poll health endpoint (allow up to 2 minutes for cold start)
curl https://{FQDN}/health
curl https://{FQDN}/ready
```

Both must return HTTP 200.

### Step 5: Verify authentication

```powershell
curl -H "X-Api-Key: <superadmin key>" https://{FQDN}/api/config
```

Must return HTTP 200 with tenant configuration JSON.

---

## Post-conditions (Verification Gate)

All of the following must be true after initialization:

| # | Assertion | How to verify |
|---|-----------|---------------|
| I.1 | Health endpoints return 200 | `GET /health`, `GET /ready` |
| I.2 | Superadmin API key authenticates | `GET /api/config` with `X-Api-Key` header |
| I.3 | Tenant state is `active` | Response from I.2 → `state: "active"` |
| I.4 | 0 conversations | `GET /api/admin/conversations` returns `total_count: 0` |
| I.5 | 0 knowledge base articles | `GET /api/admin/knowledge` returns `total_count: 0` |
| I.6 | All merchant config fields empty | `GET /api/config?state=draft` — brand_name, brand_voice, custom_instructions, return_policy, shipping_info, escalation_keywords, escalation_email, greeting_message, farewell_message, warranty_info, support_hours, custom_policies, widget_greeting_message all empty or null |
| I.7 | Configuration badge is Pending | `GET /api/config/activation-status` — `is_configured: false` |
| I.8 | Widget gate rejects conversations | `POST /api/chat/conversations` returns 401 or 403 (tenant not activated, widget key not bound to an active config) |
| I.9 | 3 team members exist | `GET /api/admin/team` — superadmin + 2 escalation agents |
| I.10 | Widget key matches seed output | Compare `WIDGET_KEY` from Step 1 with Key Vault value |

If any assertion fails, classify per Section 3 of `REPEATABLE-PROCEDURES.md`:
- **Procedure defect:** Fix this document before continuing.
- **Environment transient:** Retry the failing step.

---

## Known Failure Modes

| Symptom | Classification | Resolution |
|---------|----------------|------------|
| Key regeneration invalidates existing keys | By design | Every run generates new keys — complete Steps 2-3 |
| Admin UI broken after initialization (no tier badge) | Procedure defect (if Steps 2-3 skipped) | Complete Steps 2-5 |
| `az keyvault secret set` returns 403 | Environment (RBAC) | Assign "Key Vault Secrets Officer" to CLI user |
| Health endpoint returns 503 after restart | Environment transient | Wait 2 minutes for cold start, retry |
| I.3 assertion used `status` instead of `state` | Procedure defect (corrected 2026-02-16) | Field is `state` in config response, not `status` |
| I.8 returns 401 instead of 403 | Procedure defect (corrected 2026-02-16) | Unactivated tenant returns 401 (no widget auth context); 403 only when explicitly deactivated |

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
