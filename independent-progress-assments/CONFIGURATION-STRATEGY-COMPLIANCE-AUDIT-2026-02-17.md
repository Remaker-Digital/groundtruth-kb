# Configuration Strategy Compliance Audit

Date: 2026-02-17  
Project: Agent Red Customer Engagement  
Audit scope: Hardcoded configuration/secrets policy compliance across tracked repository files and local project configuration context

## Policy Under Audit

1. No hardcoded variables for keys, passwords, usernames, transient URIs, etc.  
2. Development/testing variables must come from `.env.local`.  
3. Production variables must be stored in a secure, redundant, multi-tenant configuration/management store.

## Executive Verdict

The project is **partially compliant**.

- `Implemented`: Strong baseline exists for `.env.local` in dev/test and secure runtime services (Key Vault + Cosmos-backed tenant config).
- `Not fully implemented`: Multiple hardcoded transient URIs, environment defaults, tenant-specific values, and operational constants remain in tracked files.
- `Not fully implemented`: Production runtime configuration is still materially dependent on Container App/Terraform environment variables, not exclusively a multi-tenant config database.

## Method

- Searched tracked source, infrastructure, scripts, tests, extensions, and docs for hardcoded config patterns.
- Verified ignore policy and tracking status for local secret files.
- Reviewed runtime configuration architecture in:
  - `src/multi_tenant/cosmos_client.py`
  - `src/multi_tenant/tenant_secret_service.py`
  - `src/multi_tenant/repository.py`
  - `src/multi_tenant/tenant_config_processor.py`
  - `infrastructure/terraform/main.tf`

## Confirmed Implementations (Compliant Elements)

1. Local secret files are protected from git tracking.
- `.env.local` ignored: `.gitignore:7`
- `.claude/` ignored: `.gitignore:164`

2. Dev/test workflows frequently load `.env.local`.
- Examples: `scripts/test_chat_battery.py`, `scripts/test_e2e_conversation_flows.py`, `scripts/test_admin_ui_validation.py`, `tests/regression/conftest.py`

3. Tenant secrets are handled via Key Vault abstraction.
- `src/multi_tenant/tenant_secret_service.py` (Key Vault-backed tenant secret service)

4. Tenant configuration is persisted in Cosmos repositories.
- `PreferencesRepository`: `src/multi_tenant/repository.py` (versioned tenant config)
- `PlatformConfigRepository`: `src/multi_tenant/repository.py`
- Config processor wired to repositories: `src/multi_tenant/tenant_config_processor.py`

5. Core data access enforces tenant scoping in repositories.
- `TenantScopedRepository` model: `src/multi_tenant/repository.py`

## Deviations from Strategy

## A) Hardcoded transient URIs/endpoints in runtime code

1. Widget runtime default API URL is hardcoded to a production hostname.
- `widget/src/index.ts:78`

2. Standalone admin dev proxy hardcodes production API gateway URL.
- `admin/standalone/vite.config.ts:36`
- `admin/standalone/vite.config.ts:41`

3. NATS runtime fallback uses hardcoded endpoint/IP-style default.
- `src/multi_tenant/nats_isolation.py:85`

4. AGNTCY transport fallback endpoints and namespace defaults are hardcoded.
- `src/multi_tenant/agntcy_sdk_integration.py:38`
- `src/multi_tenant/agntcy_sdk_integration.py:42`
- `src/agents/containers/agent_app.py:35`
- `src/agents/containers/agent_app.py:38`

## B) Hardcoded tenant/user/environment constants in operational scripts

1. Seed/provision scripts embed specific shop domain and customer email.
- `scripts/seed_tenant.py:169`
- `scripts/seed_tenant.py:170`
- `scripts/provision_tenant_one.py:59`
- `scripts/provision_tenant_one.py:60`

2. Seed script hardcodes FQDN.
- `scripts/seed_tenant.py:175`

3. Deployment/rollback scripts hardcode production URL.
- `scripts/deploy/upgrade.ps1:44`
- `scripts/deploy/rollback.ps1:26`
- `scripts/deploy/cosmos-pitr-restore.ps1:54`
- `scripts/deploy/restore-api-gateway.ps1:192`

4. Test/validation scripts use hardcoded production URL fallbacks (despite `.env.local` loading).
- `scripts/test_chat_battery.py:39`
- `scripts/test_chat_quality_metrics.py:81`
- `scripts/test_admin_ui_validation.py:67`
- `scripts/test_e2e_conversation_flows.py:46`
- `tests/regression/conftest.py:46`

## C) IaC defaults include environment-specific concrete values

1. Terraform variable defaults include concrete infrastructure endpoints.
- `infrastructure/terraform/variables.tf:78`
- `infrastructure/terraform/variables.tf:94`
- `infrastructure/terraform/variables.tf:157`

2. Terraform monitoring default includes a specific email username.
- `infrastructure/terraform/monitoring.tf:30`

3. Restore manifest embeds subscription/resource IDs and endpoint values.
- `scripts/deploy/api-gateway-restore.yaml:2`
- `scripts/deploy/api-gateway-restore.yaml:37`
- `scripts/deploy/api-gateway-restore.yaml:41`
- `scripts/deploy/api-gateway-restore.yaml:49`
- `scripts/deploy/api-gateway-restore.yaml:59`

## D) Documentation/procedure drift with policy contradictions

1. Repeatable procedures include a concrete widget key fallback.
- `docs/operations/REPEATABLE-PROCEDURES.md:317`
- `docs/operations/REPEATABLE-PROCEDURES.md:320`

This conflicts with the same document’s own stated rule against hardcoded transient values.

## E) Production config source-of-truth mismatch (architecture-level)

Observed production runtime pattern:

- Container App env vars are injected via Terraform: `infrastructure/terraform/main.tf` (`local.shared_env`, container `env` blocks).
- Some secrets are in Key Vault/secret refs, but many critical runtime variables are still env-level.

Result:

- Production configuration is **not exclusively** in a multi-tenant config/management database.
- Multi-tenant config is used for tenant preferences and platform config, but not as sole source for all production runtime variables.

## Risk Assessment

1. Hardcoded endpoints increase environment drift and accidental production coupling.
2. Tenant-specific constants in scripts raise operational and data-handling risk.
3. Mixed config sources increase misconfiguration risk and complicate incident recovery.
4. Documentation hardcoded keys can normalize unsafe copy/paste behavior.

## Recommended Remediation Plan

## Priority 0 (Immediate)

1. Remove concrete key fallback from procedures.
- Replace with `${WIDGET_KEY}` only in `docs/operations/REPEATABLE-PROCEDURES.md`.

2. Remove hardcoded runtime production URL fallbacks.
- `widget/src/index.ts`
- `admin/standalone/vite.config.ts` (use `VITE_API_URL` or local dev default only)
- Script/test URL fallbacks should fail-fast if env is missing.

3. Parameterize tenant-specific constants in seed/provision scripts.
- Accept CLI args or env vars for shop domain/email/FQDN.

## Priority 1 (Near-term)

1. Eliminate hardcoded transport fallbacks.
- `src/multi_tenant/nats_isolation.py`
- `src/multi_tenant/agntcy_sdk_integration.py`
- `src/agents/containers/agent_app.py`

2. Move Terraform concrete defaults to `.tfvars` templates or required vars.
- Keep examples generic; avoid personal email defaults.

3. Add CI guardrails.
- Secret scanning + policy regex checks for hardcoded URLs/keys in runtime paths.
- Block merges introducing `*.azurecontainerapps.io`, `pk_live_`, `sk_*` in non-test contexts.

## Priority 2 (Strategic architecture alignment)

1. Define explicit config domains:
- Platform runtime config (env/infra)
- Tenant operational config (Cosmos)
- Sensitive secrets (Key Vault)

2. If policy requires DB-centric production config, introduce provider control-plane config service and migrate non-secret mutable runtime settings from env vars into managed config tables with versioning/audit/rollout.

3. Keep immutable infra coordinates in IaC, but prohibit embedding tenant-specific or transient operational values in source.

## Compliance Decision

1. Strategy (1) “no hardcoded variables”: **Not compliant** (multiple deviations listed).
2. Strategy (2) “dev/test via `.env.local`”: **Mostly compliant**, but undermined by hardcoded fallback values.
3. Strategy (3) “production vars in secure redundant multi-tenant config DB”: **Partially compliant** (tenant config/secrets architecture exists, but env/Terraform remains primary for many production runtime values).

## Notes

- No tracked evidence of `.env.local` or `.claude/settings.local.json` being committed.
- This audit focused on repository content and accessible local project files, not external cloud runtime state validation.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
