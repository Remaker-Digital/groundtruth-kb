NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3215 Superadmin Contact Gate Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3215-superadmin-contact-gate-coverage
Version: 001 (NEW)
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3215

target_paths: ["applications/Agent_Red/src/integrations/provisioning.py", "applications/Agent_Red/src/multi_tenant/trial_management.py", "applications/Agent_Red/src/multi_tenant/repositories/tenant.py", "applications/Agent_Red/src/app/background.py", "applications/Agent_Red/tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py", "applications/Agent_Red/tests/unit/test_contactless_tenant_scanner_spec1882.py"]

## Claim

WI-3215 should repair the live `SPEC-1882` superadmin contact gate and add deterministic coverage against production Agent Red paths.

`SPEC-1882` requires tenant creation to be blocked when neither superadministrator email nor phone is provided; `provision_tenant()` must reject `None` or empty contact values with the specified error; the rule applies across billing channels; contact is required for login credential delivery; test tenancies should use `info@remakerdigital.com`; and existing tenants without valid contact are automatically deactivated.

Current repository inspection shows partial implementation plus live gaps:

- `applications/Agent_Red/src/integrations/provisioning.py` rejects contactless `provision_tenant()` calls, but the guard is a truthiness check and existing deterministic tests only cover `BillingChannel.MANUAL`.
- `applications/Agent_Red/src/integrations/provisioning.py` still allows contactless `provision_trial_tenant()` calls, which create `BillingChannel.TRIAL` tenants.
- `applications/Agent_Red/src/multi_tenant/trial_management.py` `TrialManagementService.provision_trial()` still accepts `customer_email=None` and has no phone alternative.
- No live source path was found that automatically deactivates existing active tenants whose `customer_email` and `customer_phone` are both missing or empty.
- Existing `applications/Agent_Red/tests/multi_tenant/test_tenant_display_name.py` includes a small SPEC-1882 section, but it does not prove all production creation paths, all relevant billing channels, no-write failure behavior, trial provisioning behavior, exact error text, automatic deactivation, or canonical test-tenancy contact usage for the new SPEC-1882 coverage.

This proposal treats WI-3215 as a bounded source repair plus test-addition item. It does not rewrite unrelated historical test fixtures, change credential delivery mechanics, add SMS delivery, change tenant identity semantics, create new work items, or mutate formal GT-KB artifacts.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1882` gives enough implementation detail for a bounded repair: enforce a non-empty superadmin email or phone before tenant creation, apply the rule to the paid and trial tenant-creation surfaces, preserve the exact failure text, and automatically deactivate already-active tenant documents that still lack both contact channels.

The phrase "All test tenancies must use info@remakerdigital.com" is applied here to new and modified SPEC-1882 tests. A repository-wide rewrite of unrelated historical test emails would be broad, risky churn and is outside this bounded WI unless separately authorized. This proposal therefore creates deterministic evidence with `info@remakerdigital.com` without expanding project membership or adding new WIs.

No new owner clarification is required because the proposal implements and tests the production clauses already present in `SPEC-1882` and keeps historical-test cleanup out of the implementation surface.

## In-Root Placement Evidence

All implementation targets are under the GT-KB root and the in-root Agent Red reference adopter subtree:

- `E:\GT-KB\applications\Agent_Red\src\integrations\provisioning.py`
- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\trial_management.py`
- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\repositories\tenant.py`
- `E:\GT-KB\applications\Agent_Red\src\app\background.py`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_superadmin_contact_requirement_spec1882.py`
- `E:\GT-KB\applications\Agent_Red\tests\unit\test_contactless_tenant_scanner_spec1882.py`

Read-only verification may inspect existing adjacent in-root files:

- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\cosmos_schema.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\shopify_billing.py`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_tenant_display_name.py`
- `E:\GT-KB\applications\Agent_Red\tests\integrations\test_provisioning_webhooks.py`
- `E:\GT-KB\applications\Agent_Red\tests\integrations\test_spa_provisioning.py`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_trial_management.py`
- `E:\GT-KB\applications\Agent_Red\tests\unit\test_trial_scanner.py`

## Specification Links

- `SPEC-1882` - Direct requirement for the superadmin contact hard provisioning gate, all-channel tenant-creation enforcement, canonical test-tenancy contact, and automatic deactivation of existing tenants without valid contact.
- `GOV-10` - Test artifacts must exercise live exposed project paths; this proposal replaces phantom-only evidence with production provisioning, trial, repository, and background-scanner coverage.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native tests must validate live code paths rather than phantom or stale assertion rows.
- `GOV-12` - Work-item remediation must create or map test evidence.
- `GOV-13` - Test visibility and phase governance; the new tests create live spec-to-test evidence for the WI.
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

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3215`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0712` - POR Step 16.B methodology review classifying phantom-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements.
- `gt deliberations list --work-item-id WI-3215 --limit 20 --json` returned `[]`; no WI-linked deliberation entries exist for `WI-3215`.
- `gt deliberations list --spec-id SPEC-1882 --limit 20 --json` returned records for unrelated GT-KB deploy-FQDN work. Those records appear to be cross-project spec-id reuse noise, not Agent Red superadmin-contact authority, so they are intentionally excluded from this proposal's normative basis.
- `gt bridge threads --wi WI-3215 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt backlog show WI-3215 --json` shows open/backlogged `WI-3215`, source spec `SPEC-1882`, project `AGENT-RED-TEST-COVERAGE-GAPS`, and the description says phantom-only evidence was rejected under `DELIB-0712`/`DELIB-0713`.
- `gt spec show SPEC-1882 --json` shows title "Superadmin Contact Requirement - hard provisioning gate", status `implemented`, and the requirement text for contact-gated tenant creation, all billing channels, canonical test tenancy contact, and automatic deactivation of existing contactless tenants.
- `applications/Agent_Red/src/integrations/provisioning.py` checks `if not customer_email and not customer_phone` in `provision_tenant()` and raises the specified error text.
- `applications/Agent_Red/src/integrations/provisioning.py` `provision_trial_tenant()` creates `BillingChannel.TRIAL` tenants and currently accepts `customer_email=None`.
- `applications/Agent_Red/src/multi_tenant/trial_management.py` `TrialManagementService.provision_trial()` creates trial tenants and currently accepts `customer_email=None`.
- `applications/Agent_Red/src/multi_tenant/repositories/tenant.py` has background-query helpers for expired/expiring trial and access-expiry scans, but no helper for active tenants missing both `customer_email` and `customer_phone`.
- `applications/Agent_Red/src/app/background.py` registers periodic scanners for trial expiry, access expiry, vectorization, and website refresh, but no scanner for SPEC-1882 contactless tenant deactivation.
- `rg -n "info@remakerdigital\\.com" applications\Agent_Red\src applications\Agent_Red\tests` returned no matches.
- `applications/Agent_Red/tests/multi_tenant/test_tenant_display_name.py` covers two manual-channel rejection cases and two acceptance cases, but does not cover all production creation paths or automatic deactivation.
- `applications/Agent_Red/src/integrations/shopify_billing.py` extracts `shop.email` before calling `provision_tenant()`, so a missing Shopify owner email will now flow into the contact gate; this proposal will cover that all-channel gate at the provisioning service layer, not the external Shopify API itself.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3215-superadmin-contact-gate-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `work_items: ["WI-3215"]`
- `warnings.missing_parent_dirs: ["tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py", "tests/unit/test_contactless_tenant_scanner_spec1882.py"]` (known conservative target-path over-harvest from shortened path mentions; declared `target_paths` are rooted under `applications/Agent_Red/`)
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3215-superadmin-contact-gate-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. In `applications/Agent_Red/src/integrations/provisioning.py`, factor a small contact-normalization/hard-gate helper that strips string values, treats `None`, `""`, and whitespace-only values as absent, returns normalized email/phone values, and raises the exact `SPEC-1882` error when both are absent.
2. Apply that helper to `provision_tenant()` before any repository write or lookup so Stripe, Shopify, manual, and any future caller using the channel-agnostic function hit the same gate.
3. Apply the same requirement to `provision_trial_tenant()` and add an optional `customer_phone` argument so trial creation also supports the email-or-phone rule instead of email-only behavior.
4. In `applications/Agent_Red/src/multi_tenant/trial_management.py`, apply the same contact gate to `TrialManagementService.provision_trial()` before the tenant document is constructed or persisted; add optional `customer_phone` handling if needed to preserve the email-or-phone contract.
5. In `applications/Agent_Red/src/multi_tenant/repositories/tenant.py`, add a cross-partition helper that returns active tenants whose `customer_email` and `customer_phone` are both missing, null, or empty.
6. In `applications/Agent_Red/src/app/background.py`, add and register a SPEC-1882 background scanner using the existing scanner pattern; it should periodically find contactless active tenants and patch them to `deactivated` with `updated_at`, `deactivated_at`, and a non-secret reason marker.
7. Add `applications/Agent_Red/tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py` covering the normalized hard gate, exact error text, no repository writes on rejection, Stripe/Shopify/manual enforcement through `provision_tenant()`, trial function enforcement, phone-only acceptance, and canonical `info@remakerdigital.com` test-tenancy contact for new SPEC-1882 evidence.
8. Add `applications/Agent_Red/tests/unit/test_contactless_tenant_scanner_spec1882.py` covering repository query shape and background scanner behavior: contactless active tenants are deactivated, tenants with email or phone are not selected, and scanner registration adds startup/shutdown handlers.
9. Do not rewrite unrelated historical test fixtures, change email/SMS credential delivery, change Shopify GraphQL fields, add new tenant identity channels, change release/deployment state, create new work items, or mutate formal artifacts.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1882` | New deterministic tests verify normalized contact gating, exact error text, no-write failure behavior, paid-channel enforcement, trial creation enforcement, phone-only acceptance, canonical test-tenancy contact usage, repository selection of contactless active tenants, and automatic background deactivation. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against live provisioning, trial, repository, and background scanner paths instead of phantom-only evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3215-superadmin-contact-gate-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check`, `ruff format --check`, targeted pytest, adjacent pytest, and whitespace diff checks on touched files. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py applications/Agent_Red/tests/unit/test_contactless_tenant_scanner_spec1882.py -q --tb=short
python -m pytest applications/Agent_Red/tests/multi_tenant/test_tenant_display_name.py applications/Agent_Red/tests/integrations/test_provisioning_webhooks.py applications/Agent_Red/tests/integrations/test_spa_provisioning.py applications/Agent_Red/tests/multi_tenant/test_trial_management.py applications/Agent_Red/tests/unit/test_trial_scanner.py applications/Agent_Red/tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py applications/Agent_Red/tests/unit/test_contactless_tenant_scanner_spec1882.py -q --tb=short
python -m ruff check applications/Agent_Red/src/integrations/provisioning.py applications/Agent_Red/src/multi_tenant/trial_management.py applications/Agent_Red/src/multi_tenant/repositories/tenant.py applications/Agent_Red/src/app/background.py applications/Agent_Red/tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py applications/Agent_Red/tests/unit/test_contactless_tenant_scanner_spec1882.py
python -m ruff format --check applications/Agent_Red/src/integrations/provisioning.py applications/Agent_Red/src/multi_tenant/trial_management.py applications/Agent_Red/src/multi_tenant/repositories/tenant.py applications/Agent_Red/src/app/background.py applications/Agent_Red/tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py applications/Agent_Red/tests/unit/test_contactless_tenant_scanner_spec1882.py
git diff --check -- applications/Agent_Red/src/integrations/provisioning.py applications/Agent_Red/src/multi_tenant/trial_management.py applications/Agent_Red/src/multi_tenant/repositories/tenant.py applications/Agent_Red/src/app/background.py applications/Agent_Red/tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py applications/Agent_Red/tests/unit/test_contactless_tenant_scanner_spec1882.py
```

## Acceptance Criteria

- PASS when `provision_tenant()` rejects `None`, empty, and whitespace-only contact values before repository writes.
- PASS when the rejection error contains `Tenant creation requires a superadministrator email or phone number`.
- PASS when Stripe, Shopify, and manual calls through `provision_tenant()` all hit the same contact gate.
- PASS when phone-only tenant creation remains accepted.
- PASS when `provision_trial_tenant()` and `TrialManagementService.provision_trial()` reject contactless trial creation before persistence.
- PASS when new SPEC-1882 tests use `info@remakerdigital.com` for test-tenancy contact data.
- PASS when `TenantRepository` exposes a live query for active tenants missing both contact channels.
- PASS when the background scanner deactivates contactless active tenants and is registered in the background task handler set.
- PASS when targeted pytest, adjacent pytest, ruff check, ruff format check, and diff whitespace checks pass.
- PASS when no formal artifacts, project membership, new work items, credentials, deployment state, release tags, unrelated fixture rewrites, or tenant identity semantics are changed.

## Risks / Rollback

Risk is moderate. This proposal tightens tenant creation behavior on trial paths and adds a new automatic deactivation scanner for existing contactless tenants. That is a behavior change, but it directly follows `SPEC-1882` and is bounded by deterministic tests. The background scanner should patch only active tenants missing both `customer_email` and `customer_phone`; tenants with either contact channel must remain untouched.

Rollback is to remove the contact-normalization helper applications, remove the trial contact gate additions, remove the contactless-tenant repository query, remove the background scanner registration, and delete the two new test files. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/src/integrations/provisioning.py`
- `applications/Agent_Red/src/multi_tenant/trial_management.py`
- `applications/Agent_Red/src/multi_tenant/repositories/tenant.py`
- `applications/Agent_Red/src/app/background.py`
- `applications/Agent_Red/tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py`
- `applications/Agent_Red/tests/unit/test_contactless_tenant_scanner_spec1882.py`

## Recommended Commit Type

`fix:`
