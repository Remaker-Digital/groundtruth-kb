# Tenant Initialization

**Type:** Repeatable Procedure (see `docs/operations/REPEATABLE-PROCEDURES.md`)
**Last verified:** 2026-02-23
**Last corrected:** 2026-02-23 — Added known failure modes for seed script widget key defect and Container App env var auth precedence (S82). Previous: 2026-02-21 — Added Step 5.5 (config activation), Step 6 (KB seeding), corrected chat endpoint path, updated I.4/I.5/I.8 for post-activation state, added known failure mode for activate endpoint 500

---

## Purpose

Initialization provisions a clean tenant with **zero pre-existing data**. After initialization, the tenant contains:

- Tenant document (active, tier per `SEED_TIER` env var — default: professional)
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
# Default (professional tier, shopify billing):
python scripts/seed_tenant.py --execute

# Override tier and billing channel via env vars:
# SEED_TIER=trial SEED_BILLING_CHANNEL=shopify python scripts/seed_tenant.py --execute
# Valid tiers: trial, starter, professional, enterprise
# Valid billing channels: shopify, stripe, trial
```

This runs 7 phases:
1. **Containers** — Ensures 10 Cosmos DB containers exist with correct indexes
0. **Clean** — Deletes ALL existing documents in the `{TENANT_ID}` partition (conversations, articles, preferences, team, memory — everything)
2. **Tenant** — Creates TenantDocument (active, tier per `SEED_TIER`) with fresh API key + widget key
3. **Preferences** — Creates draft PreferencesDocument with all merchant fields empty
6. **Platform** — Creates 4 tier_defaults documents
7. **Demo data** — Skipped (no `--demo` flag)
4. **Team** — Creates 1 team member (superadmin only) with API key hash

**Capture the output.** The summary (Phase 8) prints:
- `ADMIN_PREVIEW_API_KEY` (superadmin key)
- `WIDGET_KEY` (publishable widget key)
- Superadmin per-user API key

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

### Step 5.5: Configure and activate tenant

After seed, the tenant is in DRAFT state with empty mandatory fields. The chat pipeline will reject widget-key conversations until configuration is saved. Save minimal config to activate:

```powershell
# Save mandatory config fields (snake_case, wrapped in "fields" key)
curl -X PUT "https://{FQDN}/api/config" `
  -H "X-API-Key: <superadmin key>" `
  -H "Content-Type: application/json" `
  -d '{"fields": {"brand_name": "Remaker Digital", "brand_voice": "professional and technical", "formality_level": "balanced"}}'
```

**Expected:** HTTP 200 with `"success": true, "state": "draft"`.

**Important:** On a fresh seed, the PUT effectively activates the config (the seed document has `is_current=true`, which the backward-compat query in `get_active` recognizes). A separate `POST /api/config/draft/activate` is **not required** and may return 500 on a fresh seed due to state ambiguity. Verify activation status:

```powershell
curl -H "X-API-Key: <superadmin key>" https://{FQDN}/api/config/activation-status
```

**Expected:** `"is_active": true, "is_configured": true`.

### Step 6: Seed knowledge base articles (optional)

If the tenant requires KB articles for quality testing or operational verification:

```powershell
$env:QUALITY_API_KEY = "<superadmin key>"
python evaluation/seed_quality_kb.py --execute --clean
```

**Expected:** 12 KB articles seeded (shipping, returns, payment, order tracking, order modifications, complaint handling, response times, privacy, 3 products, technology). The `--clean` flag deletes any existing articles first.

**Note:** The `QUALITY_API_KEY` env var MUST be set to the new superadmin key from Step 1. The hardcoded fallback in the script goes stale after every re-seed.

### Step 7: Verify chat pipeline

```powershell
curl -X POST "https://{FQDN}/api/chat/conversations" `
  -H "X-Widget-Key: <widget key>" `
  -H "Content-Type: application/json" `
  -d '{}'
```

**Expected:** HTTP 201 with `conversation_id` in response. This confirms the widget key authenticates and the chat pipeline is operational.

---

## Post-conditions (Verification Gate)

All of the following must be true after initialization:

| # | Assertion | How to verify |
|---|-----------|---------------|
| I.1 | Health endpoints return 200 | `GET /health`, `GET /ready` |
| I.2 | Superadmin API key authenticates | `GET /api/config` with `X-Api-Key` header → 200 |
| I.3 | Tenant state is `active` | `GET /api/config/activation-status` → `"is_active": true` |
| I.4 | 0 conversations (1-2 if Step 7 executed) | `GET /api/admin/conversations` — `totalCount: 0` (or 1-2 if Step 7 verification was run) |
| I.5 | KB articles match seeding | `GET /api/admin/knowledge` — `totalCount: 0` if Step 6 was skipped, `totalCount: 12` if Step 6 was executed |
| I.6 | Mandatory config fields populated | `GET /api/config` → `brand_name`, `brand_voice` non-empty (after Step 5.5) |
| I.7 | Configuration badge is Active | `GET /api/config/activation-status` → `"is_configured": true` (after Step 5.5) |
| I.8 | Widget gate accepts conversations | `POST /api/chat/conversations` with `X-Widget-Key` header + body `{}` → 201 (after Step 5.5) |
| I.9 | 1 team member exists (superadmin only) | `GET /api/admin/team` — exactly 1 member with role `superadmin` |
| I.10 | Widget key matches seed output | Compare widget key from Step 1 output with `.env.local` `PREVIEW_WIDGET_KEY` value |

If any assertion fails, classify per Section 3 of `REPEATABLE-PROCEDURES.md`:
- **Procedure defect:** Fix this document before continuing.
- **Environment transient:** Retry the failing step.

---

## Variant: Page 0 UI Testing (unactivated tenant)

When testing the **first-time activation flow** (Page 0 tests 0.1–0.17), the tenant must remain in unactivated state. Execute Steps 1–4 only, then **skip Steps 5.5–7**. Navigate to the admin UI to verify the fresh unactivated state: empty config fields, Pending badge, OnboardingWizard modal, and widget gate returning 403.

After Page 0/0A/0B tests complete, resume with Step 5.5 (configure + activate), Step 6 (KB seeding), and Step 7 (chat pipeline verification) before proceeding to Pages 1–9.

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
| `POST /api/config/draft/activate` returns 500 on fresh seed | By design (corrected 2026-02-21) | The seed document has `is_current=True` + `config_state="draft"`, causing `get_active` backward-compat query to match it as active. `PUT /api/config` patches this document directly, effectively auto-activating. A separate activate call is not needed and may fail. Use `GET /api/config/activation-status` to verify `is_active: true` instead. |
| Chat endpoint `/api/chat` returns 401 "Widget key auth only for /api/chat/ endpoints" | Procedure defect (corrected 2026-02-21) | The correct endpoint for creating conversations is `POST /api/chat/conversations` (not `/api/chat`). Body must be `{}` (empty JSON). Widget key goes in `X-Widget-Key` header. |
| `seed_quality_kb.py` fails with auth error | Environment (stale API key) | The hardcoded `QUALITY_API_KEY` fallback in the script goes stale after every re-seed. Must set `QUALITY_API_KEY` env var to the new superadmin key before running. |
| `PUT /api/config` with camelCase fields returns 200 but fields ignored | By design | Config fields use snake_case (`brand_name`, not `brandName`). camelCase fields are silently ignored with "Unknown field — ignored" warnings. Fields must be wrapped in `{"fields": {...}}` body. |
| Widget key from seed returns 401 (I.8/Step 7 fails) | Product defect (confirmed 2026-02-23, S82) | `seed_tenant.py` generates a widget key and writes it to PreferencesDocument but does NOT hash it to TenantDocument.widget_key_hash. Auth middleware checks the hash. **Workaround:** After seed, rotate the widget key via `POST /api/keys/rotate-widget-key` (requires superadmin auth). The rotation endpoint performs the correct dual-write. Then update `.env.local` PREVIEW_WIDGET_KEY with the new key. |
| Superadmin key from seed returns 401 | Environment (Container App env var) | The Container App env var `SUPERADMIN_PREVIEW_API_KEY` is checked BEFORE Cosmos DB team_members lookup. After re-seed, the new Cosmos-stored key doesn't match this env var. **Workaround:** Use the old env var key (it still works). The env var survives re-seeds. To use the new seed-generated key instead, update the Container App env var and restart the revision. |

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
