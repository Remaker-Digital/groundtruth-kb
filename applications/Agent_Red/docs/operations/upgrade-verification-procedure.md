# Non-Disruptive Upgrade Verification

**Type:** Repeatable Procedure (see `docs/operations/REPEATABLE-PROCEDURES.md`)
**Last verified:** 2026-02-18
**Last corrected:** 2026-02-24 — Parameterized for staging + production (TARGET_ENVIRONMENT variable, environment lookup table, staging deploy/rollback instructions)

---

## Purpose

Verifies that a deployment preserves all existing tenant data on the target environment. This procedure wraps the deployment with pre-deployment and post-deployment verification gates that ensure no data is lost during the upgrade.

This procedure is **environment-agnostic** — it works against both **production** (Beta Prime) and **staging** by setting the `TARGET_ENVIRONMENT` variable. The verification logic is identical; only the connection parameters change.

This is distinct from **Initialization** (which destroys all data). A non-disruptive upgrade must leave every article, conversation, configuration value, team member, and customer profile intact.

---

## When to Execute

- **Staging:** Before deploying a new version to production — prove the upgrade is non-disruptive on staging first (Release Plan Step 5).
- **Production:** Every production deployment to a tenant with live data (Release Plan Step 6).
- Any deployment where data preservation is required.

For test deployments to a clean tenant, use the **Initialization** procedure instead (`docs/operations/initialization-procedure.md`).

---

## Variables

### Environment Selector

| Variable | Value |
|----------|-------|
| `TARGET_ENVIRONMENT` | **`production`** or **`staging`** — determines all environment-dependent values below |
| `NEW_VERSION` | Version being deployed (e.g. `1.58.0`) |
| `PREVIOUS_VERSION` | Version currently running (from `GET /ready` → `version` field) |

### Environment-Dependent Values

Select the column matching `TARGET_ENVIRONMENT`. Use these values for all `{VARIABLE}` references throughout the procedure.

| Variable | Production | Staging |
|----------|-----------|---------|
| `FQDN` | `agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` | `agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |
| `CONTAINER_APP` | `agent-red-api-gateway` | `agent-red-staging` |
| `TENANT_ID` | `remaker-digital-001` | `staging-001` |
| `API_KEY` | Superadmin key from `kv-agentred-eastus` → `ADMIN-PREVIEW-API-KEY` | Superadmin key from `kv-agentred-staging` → `ADMIN-PREVIEW-API-KEY` |
| `SPA_API_KEY` | Container App env var `SUPERADMIN_PREVIEW_API_KEY` on `agent-red-api-gateway` | Container App env var `SUPERADMIN_PREVIEW_API_KEY` on `agent-red-staging` |
| `WIDGET_KEY` | Current widget key for `remaker-digital-001` (from preferences doc or Key Vault) | Current widget key for `staging-001` (from preferences doc or Key Vault) |
| `KEY_VAULT` | `kv-agentred-eastus` | `kv-agentred-staging` |
| `RESOURCE_GROUP` | `Agent-Red` | `Agent-Red` |
| `ACR` | `acragentredeastus` | `acragentredeastus` (shared) |

---

## Procedure

### Phase A: Pre-Deployment Snapshot

Before deploying, capture the current state of all tenant data. Record each value — these become the expected values for post-deployment verification.

> **Note:** All API calls in Phases A and C use relative paths. Prefix every call with `https://{FQDN}`. Authenticate tenant endpoints (A.2–A.11, C.2–C.12) with `{API_KEY}` and superadmin endpoints (C.14–C.25) with `{SPA_API_KEY}`.

| # | Data Point | API Call | Record |
|---|-----------|----------|--------|
| A.1 | Current version | `GET /ready` → `version` | `{PREVIOUS_VERSION}` |
| A.2 | Tenant status | `GET /api/config` → `status` | |
| A.3 | Configuration state | `GET /api/config/activation-status` → `is_active`, `is_configured`, `has_pending_changes`, `active_version` | |
| A.4 | Total conversations | `GET /api/admin/conversations?limit=1` → `total_count` | |
| A.5 | Conversation status breakdown | `GET /api/admin/analytics/summary` → `status_breakdown` | |
| A.6 | Total KB articles | `GET /api/admin/knowledge?limit=1` → `total_count` | |
| A.7 | Team member count | `GET /api/admin/team` → count of members | |
| A.8 | Team member names + roles | `GET /api/admin/team` → list of `{name, role}` | |
| A.9 | Draft config values | `GET /api/config?state=draft` → all merchant fields | |
| A.10 | Active config values | `GET /api/config` → all merchant fields | |
| A.11 | Widget key hash exists | `GET /api/config/activation-status` → confirms widget_key presence | |

Store these values in a temporary file or note for comparison in Phase C.

### Phase B: Deploy

**If `TARGET_ENVIRONMENT` = `production`:** Execute the standard deployment script:

```powershell
.\scripts\deploy\upgrade.ps1 -Version "v{NEW_VERSION}"
```

**If `TARGET_ENVIRONMENT` = `staging`:** The upgrade script targets production by default. For staging, use the manual equivalent below with staging values.

**Manual equivalent** (works for both environments — substitute `{CONTAINER_APP}` from the environment table):

1. Bump `PRODUCT_VERSION` in `src/multi_tenant/api_versioning.py`
2. Build all 3 admin SPAs (`npm run build` in `admin/standalone`, `admin/shopify`, and `admin/provider`)
3. ACR build: `az acr build --registry {ACR} --image api-gateway:v{NEW_VERSION} . --no-logs`
4. Update container app:
   ```powershell
   az containerapp update `
       --name {CONTAINER_APP} `
       --resource-group {RESOURCE_GROUP} `
       --image acragentredeastus.azurecr.io/api-gateway:v{NEW_VERSION}
   ```
5. Wait for health: `GET https://{FQDN}/health` and `GET https://{FQDN}/ready` return 200

### Phase C: Post-Deployment Verification

Compare every value from Phase A against the current state. **All values must match exactly** (except version, which should be `{NEW_VERSION}`).

| # | Assertion | Verify |
|---|-----------|--------|
| C.1 | Version updated | `GET /ready` → `version` = `{NEW_VERSION}` |
| C.2 | Tenant status unchanged | Same as A.2 |
| C.3 | Configuration state unchanged | Same as A.3 (is_active, is_configured, has_pending_changes, active_version) |
| C.4 | Conversation count unchanged | Same as A.4 |
| C.5 | Conversation status breakdown unchanged | Same as A.5 |
| C.6 | KB article count unchanged | Same as A.6 |
| C.7 | Team member count unchanged | Same as A.7 |
| C.8 | Team member names + roles unchanged | Same as A.8 |
| C.9 | Draft config values unchanged | Same as A.9 |
| C.10 | Active config values unchanged | Same as A.10 |
| C.11 | Widget key still valid | `POST https://{FQDN}/api/chat/conversations` with `{WIDGET_KEY}` returns 200/201 (if tenant was active) or 403 (if tenant was inactive — same as before) |
| C.12 | API key still authenticates | `GET https://{FQDN}/api/config` with `{API_KEY}` returns 200 |
| C.13 | Regression tests pass | `python -m pytest tests/regression/ -q` — all pass |
| C.14 | Superadmin API functional | `GET /api/superadmin/tenants` with SPA API key returns 200 with `total >= 1` |
| C.15 | Public status API functional | `GET /api/status` (no auth) returns 200 with `overall_status` field |
| C.16 | Provider admin SPA served | `GET /admin/provider/` returns 200 with `text/html` content type |
| C.17 | Incident endpoints functional | `GET /api/superadmin/incidents` with SPA API key returns 200 |
| C.18 | Alert endpoints functional | `GET /api/superadmin/alerts/rules` with SPA API key returns 200 |
| C.19 | MFA endpoint functional | `GET /api/superadmin/mfa/status` with SPA API key returns 200 |
| C.20 | Magic link request endpoint | `POST /api/auth/magic-link/request` (no auth) with `{"email":"test@test.com"}` returns 200 |
| C.21 | Analytics period filtering | `GET /api/analytics/summary?since=...&until=...` with API key returns 200 with summary data |
| C.22 | Archive endpoint functional | `POST /api/admin/conversations/{id}/archive` with API key returns 200 or 404 (valid auth response) |
| C.23 | Support diagnostics functional | `GET /api/superadmin/diagnostics/{TENANT_ID}` with SPA API key returns 200 with `tenantId` field |
| C.24 | Cost analytics functional | `GET /api/superadmin/costs?days=30` with SPA API key returns 200 with `totalPlatformCost` field |
| C.25 | Abuse detection functional | `GET /api/superadmin/abuse/signals` with SPA API key returns 200 with `totalTenantsScanned` field |
| C.26 | Avatar upload endpoint functional | `POST /api/admin/avatar/upload` with API key and a small PNG file returns 200 with `success` = true and `avatar_url` starting with `data:image/png;base64,` |
| C.27 | Tier listing endpoint functional | `GET /api/billing/tiers` with API key returns 200 with `current_tier` field and `tiers` array of length 3 |
| C.28 | Add-on listing endpoint functional | `GET /api/billing/addons` with API key returns 200 with `addons` array and `total` >= 4 |
| C.29 | Memory stats endpoint functional | `GET /api/admin/memory/stats` with API key returns 200 with `total_vectors` and `memory_enabled` fields |
| C.30 | Config locking endpoint functional | `GET /api/admin/config/lock/status` with API key returns 200 with `etag` field |
| C.31 | FCR metric in analytics | `GET /api/analytics/summary` with API key returns 200; response includes `fcr_rate` or `first_contact_resolution` field (may be null if no conversations yet) |
| C.32 | Tier upgrade preview functional | `GET /api/billing/upgrade/preview?target_tier=professional` with API key returns 200 with `direction` field, or 400 if already on professional tier |
| C.33 | Unit test count gate | `python -m pytest tests/ --co -q 2>&1 | tail -1` shows >= 4000 tests collected |
| C.34 | Evaluation framework loads | `python -c "from evaluation.pilots.quality_pilot import load_dataset; print(len(load_dataset()))"` prints >= 20 |
| C.35 | Critic rule integrity | `python -c "from src.multi_tenant.system_prompt_builder import _PLATFORM_BASE, AgentRole; p=_PLATFORM_BASE[AgentRole.CRITIC_SUPERVISOR]; assert '(a)' in p and '(b)' in p and '(c)' in p; print('OK')"` prints OK |

### Phase D: Failure Response

If any assertion in Phase C fails:

1. **Data loss detected** — Do NOT proceed. Roll back immediately:

   **If `TARGET_ENVIRONMENT` = `production`:**
   ```powershell
   .\scripts\deploy\rollback.ps1 -Version "v{PREVIOUS_VERSION}"
   ```

   **If `TARGET_ENVIRONMENT` = `staging`** (rollback script targets production; use manual rollback):
   ```powershell
   az containerapp update `
       --name {CONTAINER_APP} `
       --resource-group {RESOURCE_GROUP} `
       --image acragentredeastus.azurecr.io/api-gateway:v{PREVIOUS_VERSION}
   ```

2. After rollback, re-run Phase C assertions against `{PREVIOUS_VERSION}` to confirm data is intact.
3. Investigate root cause before re-attempting deployment.

---

## Known Failure Modes

| Symptom | Classification | Resolution |
|---------|----------------|------------|
| Version unchanged after deploy | Environment transient | Verify ACR build succeeded; check revision is active |
| Conversation count decreased | Data loss — ROLLBACK | Investigate Cosmos DB partition; likely a code bug in startup |
| API key returns 401 | Environment transient | Key Vault secret may need revision restart; check key hash in tenant doc |
| Regression tests fail | Code defect | Fix code, do not deploy until tests pass |
| /api/status returns 401 | Code defect | Verify `/api/status` is in AUTH_EXEMPT_PREFIXES (hotfix1 pattern) |
| Superadmin endpoint returns 500 with `enable_cross_partition_query` | Code defect | Remove deprecated kwarg from repository (hotfix2 pattern — SDK 4.14+ removed it) |
| MFA endpoint returns 500 with `team_member` attribute error | Code defect | Endpoint must fetch full member doc via TeamMemberRepository.read(), not use ctx.team_member (hotfix3 pattern) |
| Magic link request returns 401 | Code defect | Verify `/api/auth/magic-link` is in AUTH_EXEMPT_PREFIXES in auth.py |
| X-Session-Token returns 401 | Code defect | Verify middleware imports `verify_magic_link_session_token` and checks header |
| Diagnostics endpoint returns 500 with `KnowledgeRepository` | Code defect | Import is `KnowledgeBaseRepository` not `KnowledgeRepository` — fix the import in cost_analytics.py |
| Cost analytics returns import error | Code defect | Verify `cost_analytics.py` registered in routers.py and `KnowledgeBaseRepository` import is correct |
| Abuse detection missing auth | Code defect | Verify router has `dependencies=[Depends(require_role(TeamMemberRole.SUPERADMIN))]` |
| Avatar upload returns 500 on save | Environment transient | Config processor not wired — verify `configure_avatar_service()` called during startup |
| Tier listing returns empty tiers | Code defect | Verify `TIER_FEATURES` dict in tier_upgrade.py has all 3 tiers (starter, professional, enterprise) |
| Add-on checkout returns 500 with `load_catalog` | Environment transient | Stripe catalog file (`config/stripe_product_ids.json`) missing or malformed; endpoint should return `success: false` with message |
| Memory stats returns 503 | Environment transient | Memory repo not configured — verify `configure_memory_dashboard()` called during startup; returns zeros gracefully if no repo |
| Config lock returns 503 | Environment transient | Preferences repo not configured — verify `configure_config_locking()` called during startup |
| Tier upgrade returns 500 with Stripe error | Environment transient | Stripe API key not set; endpoint catches this and returns `success: false` with informative message |
| FCR metric missing from analytics | Code defect | Verify `fcr_rate` computed in analytics summary; returns null if no resolved conversations exist |
| Unit test count below 4000 | Code defect | Coverage regression — verify no test files were deleted; run `pytest --co -q` to count |
| Evaluation dataset fails to load | Code defect | Verify `evaluation/datasets/response_quality.json` exists and has valid JSON with >= 20 scenarios |
| Critic rule missing sub-rules | Code defect | Verify rule #7 in `system_prompt_builder.py` has three sub-rules (a), (b), (c) for jailbreak coverage |
| Staging Container App cold start (min replicas=0) | Environment transient | Staging scales to zero when idle. First request after idle may take 30-60s. Wait for health before running Phase C. |
| Staging tenant not found (404) | Procedure defect | Staging tenant `staging-001` must be seeded and activated before running procedure. Use `seed_tenant.py` targeting staging, then activate via API. |
| Wrong environment targeted | Procedure defect | Verify `TARGET_ENVIRONMENT` is set correctly before starting. Check `FQDN` in browser to confirm you are hitting the intended environment. |

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
