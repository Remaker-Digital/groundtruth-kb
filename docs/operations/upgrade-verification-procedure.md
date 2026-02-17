# Non-Disruptive Upgrade Verification

**Type:** Repeatable Procedure (see `docs/operations/REPEATABLE-PROCEDURES.md`)
**Last verified:** 2026-02-16
**Last corrected:** 2026-02-16 — Created (S26)

---

## Purpose

Verifies that a production deployment preserves all existing tenant data. This procedure wraps the existing deployment script (`scripts/deploy/upgrade.ps1`) with pre-deployment and post-deployment verification gates that ensure no data is lost during the upgrade.

This is distinct from **Initialization** (which destroys all data). A non-disruptive upgrade must leave every article, conversation, configuration value, team member, and customer profile intact.

---

## When to Execute

- Every production deployment to a tenant with live data.
- Any deployment where data preservation is required.

For test deployments to a clean tenant, use the **Initialization** procedure instead (`docs/operations/initialization-procedure.md`).

---

## Variables

| Variable | Value |
|----------|-------|
| `TENANT_ID` | `remaker-digital-001` |
| `FQDN` | `agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |
| `API_KEY` | Current superadmin API key (from Key Vault `ADMIN-PREVIEW-API-KEY`) |
| `NEW_VERSION` | Version being deployed (e.g. `1.34.0`) |
| `PREVIOUS_VERSION` | Version currently running (from `GET /ready` → `version` field) |

---

## Procedure

### Phase A: Pre-Deployment Snapshot

Before deploying, capture the current state of all tenant data. Record each value — these become the expected values for post-deployment verification.

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

Execute the standard deployment procedure:

```powershell
.\scripts\deploy\upgrade.ps1
```

Or manual equivalent:
1. Bump `PRODUCT_VERSION` in `src/multi_tenant/api_versioning.py`
2. Build both admin SPAs (`npm run build` in `admin/standalone` and `admin/shopify`)
3. ACR build: `az acr build --registry {ACR} --image api-gateway:v{NEW_VERSION} .`
4. Update container app: `az containerapp update ...`
5. Wait for health: `GET /health` and `GET /ready` return 200

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
| C.11 | Widget key still valid | `POST /api/chat/conversations` with widget key returns 200 (if tenant was active) or 403 (if tenant was inactive — same as before) |
| C.12 | API key still authenticates | `GET /api/config` with `{API_KEY}` returns 200 |
| C.13 | Regression tests pass | `python -m pytest tests/regression/ -q` — all pass |
| C.14 | Superadmin API functional | `GET /api/superadmin/tenants` with SPA API key returns 200 with `total >= 1` |

### Phase D: Failure Response

If any assertion in Phase C fails:

1. **Data loss detected** — Do NOT proceed. Roll back immediately:
   ```powershell
   .\scripts\deploy\rollback.ps1
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

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
