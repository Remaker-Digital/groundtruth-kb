NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3214 Tenant Display Name Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3214-tenant-display-name-coverage
Version: 001 (NEW)
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3214

target_paths: ["applications/Agent_Red/src/multi_tenant/superadmin_api/_tenants.py", "applications/Agent_Red/tests/multi_tenant/test_tenant_display_name_spec1881.py"]

## Claim

WI-3214 should repair the live `SPEC-1881` tenant display-name path and add deterministic coverage that exercises the production Agent Red surfaces instead of relying on phantom-only evidence.

`SPEC-1881` requires a human-readable tenant identifier for the SPA: `TenantDocument.display_name`; non-empty, unique display names for newly provisioned or operator-updated tenants; default provisioning names in `{customer_email}-001` or `{customer_phone}-001` ordinal form; a SPA admin API path for setting a custom name; SPA tenant lists that show `display_name` instead of raw `tenant_id`; UUID availability for detail/debug; and ascending/descending sorting for tenant-list columns.

Current repository inspection shows partial implementation plus one reachable defect:

- `applications/Agent_Red/src/multi_tenant/cosmos_schema.py` declares `TenantDocument.display_name`.
- `applications/Agent_Red/src/integrations/provisioning.py` has `_generate_display_name()` and writes `display_name` during new tenant provisioning.
- `applications/Agent_Red/src/multi_tenant/superadmin_api/_tenants.py` declares `TenantSummaryItem.display_name`, but `list_all_tenants()` does not select `c.display_name`, so the API response cannot reliably populate the SPA's friendly tenant label from Cosmos.
- No custom display-name update endpoint is present in `applications/Agent_Red/src/multi_tenant/superadmin_api/_tenants.py`; current tenant endpoints cover tier, create, resend welcome email, expiry, and rate limit.
- Existing tests in `applications/Agent_Red/tests/multi_tenant/test_tenant_display_name.py` verify schema presence and basic provisioning defaults, but do not prove ordinal conflict handling, API query projection, list response propagation, custom-name update behavior, or deterministic SPA display/sort wiring.

This proposal adds the missing backend source path and a focused deterministic Python test file. It does not expand into a broader tenant-directory redesign, multi-field search/filter work, CSV export, row drill-down behavior, deployment modal work, live E2E assertions, or formal artifact mutation.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1881` is concrete enough for this bounded repair: it names the document field, default ordinal generation, uniqueness, custom-name SPA admin API behavior, tenant-list display preference, UUID debug availability, and sortable table behavior. The implementation can preserve nullable `display_name` on the Pydantic document model for legacy/migration compatibility while enforcing non-empty values for new provisioning defaults and operator custom-name updates.

No new owner clarification is required because the proposal only makes the already-specified display-name path reachable and covered. It does not change project scope, tenant identity semantics, release state, or any formal GT-KB artifact.

## In-Root Placement Evidence

All implementation targets are under the GT-KB root and the in-root Agent Red reference adopter subtree:

- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\superadmin_api\_tenants.py`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_tenant_display_name_spec1881.py`

Read-only verification may inspect existing adjacent in-root files:

- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\cosmos_schema.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\provisioning.py`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_tenant_display_name.py`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_superadmin_api.py`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_superadmin_api_endpoints.py`
- `E:\GT-KB\applications\Agent_Red\admin\provider\hooks\useTenantDirectory.ts`
- `E:\GT-KB\applications\Agent_Red\admin\provider\pages\TenantDirectory.tsx`
- `E:\GT-KB\applications\Agent_Red\admin\provider\components\TenantName.tsx`
- `E:\GT-KB\applications\Agent_Red\admin\provider\package.json`

## Specification Links

- `SPEC-1881` - Direct tenant display-name requirement for document storage, unique ordinal defaulting, custom-name SPA admin API behavior, tenant-list display, UUID detail/debug availability, and sortable list columns.
- `GOV-10` - Test artifacts must exercise live exposed project paths; this proposal moves WI-3214 from phantom-only evidence to production provisioning/API/static-SPA verification.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native tests must validate live code paths rather than phantom or stale assertion rows.
- `GOV-12` - Work-item remediation must create or map test evidence.
- `GOV-13` - Test visibility and phase governance; the new test file creates live spec-to-test evidence for the WI.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies changed-file hygiene; Python coverage will use targeted pytest plus ruff check and ruff format checks on touched Python files.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner decisions are cited from existing AUQ-backed project authorization; this proposal requests no new owner decision.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red reference adopter work stays under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use governed bridge helper paths and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3214`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0712` - POR Step 16.B methodology review classifying phantom-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements.
- `gt deliberations list --work-item-id WI-3214 --limit 20 --json` returned `[]`; no WI-linked deliberation entries exist for `WI-3214`.
- `gt deliberations list --spec-id SPEC-1881 --limit 20 --json` returned `[]`; no spec-linked deliberation entries were found for `SPEC-1881`.
- `gt bridge threads --wi WI-3214 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt backlog show WI-3214 --json` shows open/backlogged `WI-3214`, source spec `SPEC-1881`, project `AGENT-RED-TEST-COVERAGE-GAPS`, and the description says phantom-only evidence was rejected under `DELIB-0712`/`DELIB-0713`.
- `gt spec show SPEC-1881 --json` shows title "Tenant Display Name - human-readable tenant identifier for SPA", status `implemented`, and a requirement for `display_name`, non-empty/unique names, ordinal defaults, custom-name SPA admin API behavior, tenant-list display, UUID detail/debug availability, and sortable tenant-list columns.
- `applications/Agent_Red/src/multi_tenant/cosmos_schema.py` declares `TenantDocument.display_name` with default `None` for existing-document compatibility.
- `applications/Agent_Red/src/integrations/provisioning.py` implements `_generate_display_name(contact)` and writes the generated value into new tenant documents.
- `applications/Agent_Red/src/multi_tenant/superadmin_api/_tenants.py` `TenantSummaryItem` includes `display_name`, but `list_all_tenants()` currently selects `c.tenant_id, c.status, c.tier, c.billing_channel, c.customer_email, c.shopify_shop_domain, c.created_at, c.updated_at, c.deactivated_at, c.consent_status, c.expires_at` and omits `c.display_name`.
- `rg` over `applications/Agent_Red/src/multi_tenant/superadmin_api/_tenants.py` finds no display-name update endpoint; the existing tenant-specific mutation endpoints are tier, expiry, and rate-limit.
- `applications/Agent_Red/tests/multi_tenant/test_tenant_display_name.py` exists, but it does not exercise `_generate_display_name()` ordinal conflict handling and does not call `list_all_tenants()`.
- `applications/Agent_Red/admin/provider/hooks/useTenantDirectory.ts` consumes `t.displayName` and falls back to `tenantId`.
- `applications/Agent_Red/admin/provider/pages/TenantDirectory.tsx` defaults sorting to `displayName`, renders sortable headers for Tenant, Status, Tier, Channel, Email, Created, and Expires, and passes display-name information to `TenantName`.
- `applications/Agent_Red/admin/provider/components/TenantName.tsx` renders the human-readable name while keeping the raw UUID available through tooltip behavior.
- `applications/Agent_Red/admin/provider/package.json` exposes `typecheck` and `build`, but no native unit-test script for provider admin React components.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3214-tenant-display-name-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `warnings.missing_parent_dirs: ["tests/multi_tenant/test_tenant_display_name_spec1881.py"]` (known conservative target-path over-harvest from shortened path mentions; declared `target_paths` are rooted under `applications/Agent_Red/`)
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3214-tenant-display-name-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. In `applications/Agent_Red/src/multi_tenant/superadmin_api/_tenants.py`, include `c.display_name` in the `list_all_tenants()` data query so the existing `TenantSummaryItem.display_name` field is populated from Cosmos.
2. In `applications/Agent_Red/src/multi_tenant/superadmin_api/_tenants.py`, add a small request/response model and `PATCH /tenants/{tenant_id}/display-name` handler that strips operator input, rejects empty custom names, checks cross-tenant uniqueness, patches `/display_name` plus `/updated_at`, and records best-effort audit evidence using existing superadmin API patterns.
3. Add `applications/Agent_Red/tests/multi_tenant/test_tenant_display_name_spec1881.py`.
4. In the new test file, prove `_generate_display_name()` increments from `-001` to `-002` when the first candidate already exists by using a fake repository that exercises the production helper.
5. In the new test file, prove `list_all_tenants()` selects `c.display_name` and propagates a friendly display name into `TenantDirectoryResponse.tenants[0].display_name`.
6. In the new test file, prove the custom display-name handler patches a trimmed non-empty value, rejects blank input through the request model, and rejects a duplicate display name owned by another tenant.
7. In the new test file, add static source assertions over the provider admin SPA files to verify displayName fallback, default display-name sorting, sortable visible columns, and UUID detail/debug availability via `TenantName` tooltip behavior, because the provider admin package currently has no native unit-test script.
8. Do not change formal artifacts, project membership, release/deployment state, tenant identity semantics, tenant search/filter/export/drill-down behavior, or live E2E tests.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1881` | New deterministic tests verify ordinal uniqueness, API list projection/response propagation, custom-name non-empty/unique update behavior, SPA display-name fallback, sortable visible columns, and UUID debug availability through the existing `TenantName` source. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against live production paths instead of phantom-only evidence; provider SPA assertions read current source because there is no provider-admin unit-test runner. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3214-tenant-display-name-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check`, `ruff format --check`, targeted pytest, adjacent pytest, provider admin typecheck, and whitespace diff checks on touched files. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/multi_tenant/test_tenant_display_name_spec1881.py -q --tb=short
python -m pytest applications/Agent_Red/tests/multi_tenant/test_tenant_display_name.py applications/Agent_Red/tests/multi_tenant/test_superadmin_api.py applications/Agent_Red/tests/multi_tenant/test_superadmin_api_endpoints.py applications/Agent_Red/tests/multi_tenant/test_tenant_display_name_spec1881.py -q --tb=short
npm --prefix applications/Agent_Red/admin/provider run typecheck
python -m ruff check applications/Agent_Red/src/multi_tenant/superadmin_api/_tenants.py applications/Agent_Red/tests/multi_tenant/test_tenant_display_name_spec1881.py
python -m ruff format --check applications/Agent_Red/src/multi_tenant/superadmin_api/_tenants.py applications/Agent_Red/tests/multi_tenant/test_tenant_display_name_spec1881.py
git diff --check -- applications/Agent_Red/src/multi_tenant/superadmin_api/_tenants.py applications/Agent_Red/tests/multi_tenant/test_tenant_display_name_spec1881.py
```

## Acceptance Criteria

- PASS when `list_all_tenants()` selects `c.display_name`.
- PASS when the tenant directory response includes and serializes a friendly display name from the live API query path.
- PASS when `_generate_display_name()` deterministic coverage proves ordinal conflict behavior.
- PASS when the custom display-name SPA admin API handler strips and persists a non-empty display name.
- PASS when empty custom display-name input is rejected.
- PASS when a duplicate custom display name owned by another tenant is rejected.
- PASS when provider admin source checks prove display-name fallback, sortable visible columns, and UUID detail/debug availability remain wired.
- PASS when targeted pytest, adjacent pytest, provider admin typecheck, ruff check, ruff format check, and diff whitespace checks pass.
- PASS when no formal artifacts, project membership, new work items, credentials, deployment state, release tags, tenant identity semantics, or unrelated tenant-directory features are changed.

## Risks / Rollback

Risk is moderate. The listing-query fix is low-risk and repairs a field already present in the response model, but the custom-name endpoint adds a new platform-admin mutation surface and uniqueness check. The proposal contains the risk by using the existing tenant repository, existing router, existing audit-event patterns, and deterministic tests around validation, conflict handling, and patch operations.

Rollback is to remove the `c.display_name` projection from `list_all_tenants()`, remove the display-name request/response/handler additions, and delete the new `test_tenant_display_name_spec1881.py` file. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/src/multi_tenant/superadmin_api/_tenants.py`
- `applications/Agent_Red/tests/multi_tenant/test_tenant_display_name_spec1881.py`

## Recommended Commit Type

`fix:`
