# Release Plan — v1.57.0 Beta

**Type:** Operational Plan
**Created:** 2026-02-23 (Session 77)
**Status:** ACTIVE — current framework for all work
**Release version:** v1.57.0 (beta) → v1.58.0 (next)

---

## Terminology

| Term | Definition |
|------|-----------|
| **Beta (Prime)** | The production environment serving beta customers. Runs a pinned release image. No untested code is deployed here. |
| **Staging** | A parallel production environment (isolated Container App, Cosmos DB database, Key Vault) used to validate the next release and prove non-disruptive upgrade before applying it to Beta (Prime). |
| **v1.57.0** | The release candidate that passes the Master Test Plan and is deployed to beta customers. |
| **v1.58.0** | The next release, developed on `main` after v1.57.0 is tagged. Incorporates beta feedback and enhancements. |

---

## Environments

### Beta (Prime) Production

| Resource | Value |
|----------|-------|
| Container App | `agent-red-api-gateway` (existing) |
| FQDN | `agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |
| Cosmos DB | `cosmos-agentred-eastus` / database: `agentred` |
| Key Vault | `kv-agentred-eastus` |
| ACR | `acragentredeastus.azurecr.io` |
| Image | `api-gateway:v1.57.0` (pinned at release freeze) |
| Tenants | `remaker-digital-001` + 2 beta customer tenants |

### Staging (Parallel)

| Resource | Value |
|----------|-------|
| Container App | `agent-red-staging` (NEW — to be provisioned) |
| FQDN | TBD (assigned at provisioning) |
| Cosmos DB | `cosmos-agentred-eastus` / database: `agentred-staging` (NEW — same account, isolated database) |
| Key Vault | `kv-agentred-staging` (NEW) |
| ACR | `acragentredeastus.azurecr.io` (shared) |
| Image | Current development build from `main` |
| Tenants | `staging-001` (seeded for upgrade testing) |

---

## Release Steps

### Step 1 — Master Test Plan Execution

**Objective:** Achieve 100% PASS on the Master Test Plan v2.0.

**Preconditions:**
- Resolve all pre-existing test failures (activation_service unit test, T1-11 regression)
- No CONDITIONAL PASS accepted
- No pre-existing failures accepted

**Procedure:** Execute `docs/MASTER-TEST-PLAN-1.0.md` v2.0 — all 15 phases in order.

| Phase | Procedure | Tests | Gate |
|-------|-----------|-------|------|
| 1 | Pre-flight checks | 4 | All 4 pass |
| 2 | Unit & Integration (thermal-safe) | ~4,791 | 0 failures (excluding deselected) |
| 3 | Production Regression (MC + T0 + T1 + T2) | 86 | 0 failures |
| 4 | External URL Reachability | 37 | All reachable |
| 5 | Tenant Isolation | 30 | 0 cross-tenant access |
| 6 | API Security | 45 | 0 failures |
| 7 | Rate Limiting | 20 | All tiers enforced |
| 8 | Data Integrity | 25 | 0 corruption |
| 9 | Resilience & Failover | 29 + 6 SKIP | 0 failures in active |
| 10 | Load Testing | SLA validation | All SLAs met |
| 11 | Conversation Quality | 25 | Pilot VERDICT = PASS, pipeline errors ≤ 2 |
| 12 | UI Regression | 917 | 0 FAIL |
| 13 | SPA Provisioning + Critical Path | 25 | 25/25 PASS (CP.P1–P4 provisioning pre-test + CP.1–CP.21) |
| 14 | Upgrade Verification | 35 | All assertions pass |
| 15 | Manual Verification | 8 | All confirmed |

**Completion criterion:** Master Test Plan Execution Results document records 100% PASS across all 15 phases.

---

### Step 2 — Release Freeze (Tag-and-Branch-Forward)

**Objective:** Pin the release and enable forward development on `main`.

**Branching model:** Model A (tag-and-branch-forward). No long-lived development branches.

**Procedure:**
1. Verify `main` HEAD passed Step 1
2. Tag: `git tag v1.57.0-rc1` (or `v1.57.0` if no further RCs)
3. ACR build: `az acr build --registry acragentredeastus --image api-gateway:v1.57.0 . --no-logs`
4. Verify image exists: `az acr repository show-tags --name acragentredeastus --repository api-gateway --output table`
5. Development continues on `main` toward v1.58.0

**Hotfix policy:** If a critical bug is found in the beta release during Step 4:
- Create `hotfix/v1.57.x` branch from the `v1.57.0` tag
- Fix, test, tag `v1.57.1`, build new image, deploy to Beta (Prime)
- Cherry-pick the fix into `main`

---

### Step 2.5 — Provisioning Smoke Test

**Objective:** Verify the full merchant onboarding journey works end-to-end before provisioning real beta customers.

**Procedure:**
1. Open Provider Console (`/admin/provider`) — verify HTTP 200
2. Create tenant via SPA API (`POST /api/superadmin/tenants`):
   - Required fields (camelCase): `merchantName`, `superadminEmail`, `tier`
   - Optional: `merchantUrl`, `expiresAt`
   - Note: `tenant_id` is auto-generated (UUID) — not user-specified
   - Record returned `tenantId`, `superadminApiKey`, `widgetKey`
3. Verify tenant appears in SPA directory (`GET /api/superadmin/tenants/summary`)
4. Verify standalone admin accessible (`/admin/standalone/` → HTTP 200)
5. Activate configuration: the SPA provisioning auto-creates preferences but does NOT set `activated_at`. The chat pipeline requires activation. To activate:
   a. `POST /api/config/reset` (creates draft from tier defaults, includes widget_key)
   b. `PUT /api/config` with `{"fields": {"brand_name": "..."}}` (set mandatory fields)
   c. `POST /api/config/draft/activate` (may return 500 on first activation due to suggestion engine bootstrap — verify config state shows `"state": "active"`)
6. Verify chat pipeline: `POST /api/chat/conversations` with `X-Widget-Key` header → expect HTTP 201
7. Verify customer identity collection: check that AI response includes email request (requires SSE stream monitoring or widget UI test)
8. Record result: PASS or list of defects found

**Known issues (procedure defects corrected 2026-02-23):**
- API uses camelCase field names (`merchantName`, `superadminEmail`) not snake_case
- Tenant ID is auto-generated UUID, not user-specified
- SPA provisioning does not set `activated_at` — manual activation flow required
- First activation may return 500 but activation succeeds (check config state)
- Tenant deletion endpoint does not exist — smoke test tenants persist (harmless)

**Completion criterion:** Steps 1-6 pass. Step 7 validated via widget UI if available. Any blocking defects must be fixed and re-tested before proceeding.

---

### Step 3 — Beta Tenant Provisioning

**Objective:** Provision standalone tenants for 2 beta customers via SPA.

**Provisioning pathway:** SPA manual provisioning via Provider Console (`POST /api/superadmin/tenants`).

**Per-customer procedure:**
1. Create tenant via Provider Console "Create Tenant" modal:
   - Tenant ID: `{customer-slug}` (e.g., `beta-acme-001`)
   - Business name: Customer's business name
   - Billing channel: `manual` (or `trial`)
   - Tier: As agreed with customer
   - Superadmin email: Customer's email address
2. Verify welcome email sent to customer
3. Record tenant ID, FQDN, and creation timestamp
4. Confirm customer can log in and sees the onboarding wizard

**What beta customers experience:**
- Empty tenant — no synthetic data
- Onboarding wizard on first login
- They configure brand voice, knowledge base, team members themselves
- Widget key generated on first activation

**Completion criterion:** Both beta customers have active tenants and have confirmed they can log in.

---

### Step 4 — Beta Feedback

**Objective:** Collect feedback from beta customers and develop enhancements for v1.58.0.

**Process:**
- Gather feedback through agreed channels (email, calls, issue tracker)
- Triage feedback into:
  - **Bug fixes** — fix on `main`, may hotfix to v1.57.x if critical
  - **Enhancements** — develop on `main` for v1.58.0
  - **Deferred** — document for future releases
- All changes are applied to `main` (toward v1.58.0)
- Beta (Prime) remains on pinned v1.57.0 (or hotfixed v1.57.x) image

**Completion criterion:** Feedback collected and triaged. All critical bugs addressed. Enhancement scope for v1.58.0 defined.

---

### Step 5 — Parallel Staging Environment + Next Release Validation

**Objective:** Stand up an isolated staging environment to validate v1.58.0 and prove non-disruptive upgrade.

**Infrastructure provisioning:**
1. Create Cosmos DB database `agentred-staging` (same serverless account, isolated data)
2. Create Key Vault `kv-agentred-staging` with staging-specific secrets
3. Create Container App `agent-red-staging` in the same Container Apps environment
4. Configure staging Container App with staging Cosmos DB and Key Vault
5. Seed staging tenant: `python scripts/seed_tenant.py` (targeting staging environment)

**Validation workflow:**
1. Deploy v1.57.0 image to staging → verify baseline functionality
2. Run Master Test Plan against staging → confirm baseline PASS
3. Build v1.58.0-rc1 from `main`
4. Execute full Upgrade Verification Procedure against staging (v1.57.0 → v1.58.0-rc1)
5. All 35 assertions must pass — proving the upgrade preserves data, keys, and configuration

**Completion criterion:** Upgrade Verification Procedure passes on staging. v1.58.0 is proven non-disruptive.

---

### Step 5.5 — Multi-Tenant Upgrade Verification Procedure Update

**Objective:** Extend the Upgrade Verification Procedure to verify all tenants, not just one.

**Changes to `docs/operations/upgrade-verification-procedure.md`:**
- Phase A: Capture pre-deployment snapshots for **all active tenants** (iterate `GET /api/superadmin/tenants`)
- Phase C assertions C.2–C.12: Run **per-tenant** (config, conversations, KB articles, team members, keys)
- Phase C assertions C.13–C.35: Run **once** (platform-level: regression, superadmin endpoints, unit test gate)
- Add variable `TENANT_IDS` (list of all active tenant IDs to verify)

**Completion criterion:** Updated procedure documented and reviewed. Tested against staging with ≥ 2 tenants.

---

### Step 6 — Non-Disruptive Upgrade to Beta (Prime)

**Objective:** Deploy v1.58.0 to the beta production environment. All keys, configuration, and data for all 3 tenants (owner + 2 beta customers) are preserved. Zero disruption to service.

**Preconditions:**
- Step 5 PASS (upgrade proven on staging)
- Step 5.5 PASS (multi-tenant procedure updated and tested)
- v1.58.0 image built and tagged in ACR

**Procedure:**
1. Execute Phase A (pre-deployment snapshot) for all 3 tenants on Beta (Prime)
2. Deploy v1.58.0 image to Beta (Prime) Container App
3. Wait for health: `GET /health` and `GET /ready` return 200
4. Execute Phase C (post-deployment verification) for all 3 tenants
5. Verify all 35 × N assertions pass (where N = number of tenants for per-tenant assertions)

**Rollback:** If any assertion fails, immediately execute `scripts/deploy/rollback.ps1` to revert to v1.57.x image.

**Completion criterion:** All tenants verified. No data loss. No key invalidation. No configuration changes. Both beta customers experience zero disruption.

---

## Success Criteria Summary

| Step | Gate | Blocking? |
|------|------|-----------|
| 1 | Master Test Plan 100% PASS | Yes — blocks all subsequent steps |
| 2 | Tag + image exist in ACR | Yes — blocks Step 3 |
| 2.5 | Provisioning smoke test PASS | Yes — blocks Step 3 |
| 3 | Both beta tenants active, customers can log in | Yes — blocks Step 4 |
| 4 | Feedback triaged, critical bugs addressed | No — Step 5 can begin in parallel |
| 5 | Upgrade Verification PASS on staging | Yes — blocks Step 6 |
| 5.5 | Multi-tenant procedure tested on staging | Yes — blocks Step 6 |
| 6 | All tenants verified post-upgrade | Release complete |

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
