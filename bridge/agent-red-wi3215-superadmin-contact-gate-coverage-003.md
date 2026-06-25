REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 150a773e-a0ff-46ef-ba68-68c55a8516d5
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; resolved_role=prime-builder (session-stated ::init gtkb pb)
author_metadata_source: explicit interactive Claude runtime metadata plus bridge work-intent claim

# Implementation Proposal (REVISED) - WI-3215 Superadmin Contact Gate Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3215-superadmin-contact-gate-coverage
Version: 003 (REVISED)
Responds to GO: bridge/agent-red-wi3215-superadmin-contact-gate-coverage-002.md
Supersedes proposal: bridge/agent-red-wi3215-superadmin-contact-gate-coverage-001.md
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3215

target_paths: ["applications/Agent_Red/src/integrations/provisioning.py", "applications/Agent_Red/src/multi_tenant/trial_management.py", "applications/Agent_Red/src/multi_tenant/repositories/tenant.py", "applications/Agent_Red/src/app/background.py", "applications/Agent_Red/tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py", "applications/Agent_Red/tests/unit/test_contactless_tenant_scanner_spec1882.py", "applications/Agent_Red/tests/integrations/test_provisioning_webhooks.py"]

## Claim

This REVISED proposal expands the GO'd `-001` scope by **one target path** to resolve two issues a verification pass found in the pre-staged WI-3215 implementation. The original `-001` scope (the SPEC-1882 contact gate on paid + trial paths, the contactless-tenant repository query, the background deactivation scanner, and the two new test files) is unchanged and already implemented in the working tree.

The verification pass (this session, harness B) found that the `-001` implementation is present uncommitted in the working tree (4 source files modified, 2 new test files created) and that its two new test files pass (15/15), but two gaps block a clean `VERIFIED`:

1. **Regression in an out-of-scope existing test.** Applying the SPEC-1882 gate to `provision_trial_tenant()` (correct per spec — the requirement applies to ALL billing channels including TRIAL) causes the pre-existing `applications/Agent_Red/tests/integrations/test_provisioning_webhooks.py::TestProvisionTrialTenant::test_trial_tenant_has_expiry` to fail, because that test creates a contactless trial tenant (`provision_trial_tenant(trial_duration_days=7)`) and the gate now correctly rejects it with `ValueError: Tenant creation requires a superadministrator email or phone number`. That test file is NOT in the `-001` target_paths, and `-001` instructed against rewriting historical fixtures. The minimal correct fix is to supply a canonical contact to that one directly-invalidated test, not a broad rewrite.

2. **Canonical-test-tenancy contact gap.** SPEC-1882 requires "All test tenancies must use `info@remakerdigital.com`," and `-001` acceptance criterion #6 + Requirement Sufficiency both commit the new SPEC-1882 tests to that address. The pre-staged new tests instead use `owner@example.com` / `admin@example.com` for tenancy-creating cases. The new tests must use `info@remakerdigital.com` for tenancy contact data.

This REVISED therefore adds `applications/Agent_Red/tests/integrations/test_provisioning_webhooks.py` to target_paths solely to repair the single directly-invalidated historical test, and re-commits the new SPEC-1882 tests to the canonical `info@remakerdigital.com` contact. It does NOT broaden into unrelated historical-email rewrites, does NOT change the gate/scanner source behavior already implemented, and does NOT add project scope or new work items.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1882` already specifies the operative behavior: enforce a non-empty superadmin email-or-phone before tenant creation across ALL billing channels (including trial), use `info@remakerdigital.com` for test tenancies, and automatically deactivate existing contactless active tenants. The pre-staged implementation satisfies the gate + scanner clauses; this REVISED only completes the test-contact clause and repairs the one historical test the all-channel enforcement directly invalidated.

The scope expansion is authorized by the owner AskUserQuestion decision recorded below (2026-06-24, "Expand scope + fix + re-review"), which approves adding the single broken historical test to target_paths and switching the new tests to the canonical contact. No further owner clarification is required.

## In-Root Placement Evidence

All seven target paths are under the GT-KB root and the in-root Agent Red reference adopter subtree:

- `E:\GT-KB\applications\Agent_Red\src\integrations\provisioning.py`
- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\trial_management.py`
- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\repositories\tenant.py`
- `E:\GT-KB\applications\Agent_Red\src\app\background.py`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_superadmin_contact_requirement_spec1882.py`
- `E:\GT-KB\applications\Agent_Red\tests\unit\test_contactless_tenant_scanner_spec1882.py`
- `E:\GT-KB\applications\Agent_Red\tests\integrations\test_provisioning_webhooks.py`

## Specification Links

- `SPEC-1882` - Superadmin contact hard provisioning gate; all-channel enforcement; canonical `info@remakerdigital.com` test tenancy contact; automatic deactivation of existing contactless tenants.
- `GOV-10` - Test artifacts must exercise live exposed project paths.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native tests validate live code paths.
- `GOV-12` - Work-item remediation must create or map test evidence.
- `GOV-13` - Test visibility and phase governance.
- `GOV-07` - No bug fixes during testing procedures; the historical-test repair here is a spec-driven behavior-alignment fix authorized by the GO'd scope expansion, executed before the verification report rather than mid-test.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project authorization does not replace bridge review, GO, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - ruff check + ruff format --check on touched Python files.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner decisions captured via AskUserQuestion; this REVISED cites the scope-expansion AUQ decision.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Status-bearing bridge file authority and numbered append-only chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification maps linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red reference adopter work stays under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Uses the existing authorized WI; no project scope or new WI added.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Implementation intent and review evidence preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - This REVISED proposal is a lifecycle artifact for the work item.

## Owner Decisions / Input

The scope expansion in this REVISED is authorized by an owner AskUserQuestion decision in this session (2026-06-24): when presented that the pre-staged WI-3215 implementation breaks the out-of-scope `test_provisioning_webhooks.py::test_trial_tenant_has_expiry` and that its new tests use `example.com` rather than the SPEC-1882-mandated `info@remakerdigital.com`, the owner selected **"Expand scope + fix + re-review"** — file a REVISED proposal adding `test_provisioning_webhooks.py` to target_paths, minimally update the broken test to supply a contact, switch the new tests to `info@remakerdigital.com`, obtain a fresh Loyal Opposition GO, then apply the deltas and report. This REVISED also remains inside active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and snapshot-bound project member `WI-3215` (no new WI added).

## Prior Deliberations

- `bridge/agent-red-wi3215-superadmin-contact-gate-coverage-001.md` - the superseded NEW proposal whose scope this REVISED extends by one target path.
- `bridge/agent-red-wi3215-superadmin-contact-gate-coverage-002.md` - the Loyal Opposition GO whose implementation this verification pass exercised and found two gaps.
- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test-coverage-gap project.
- `DELIB-0712` / `DELIB-0713` - Methodology review and owner rejection of assertion-only verification for behavioral requirements.
- Owner AskUserQuestion decision, 2026-06-24 (this session): "Expand scope + fix + re-review" authorizing the one-path scope expansion and the canonical-contact fix.

## Current-State Evidence

- `git status --short -- applications/Agent_Red/` shows the `-001` implementation present uncommitted: ` M src/app/background.py`, ` M src/integrations/provisioning.py`, ` M src/multi_tenant/repositories/tenant.py`, ` M src/multi_tenant/trial_management.py`, `?? tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py`, `?? tests/unit/test_contactless_tenant_scanner_spec1882.py`.
- `provisioning.py` already defines `_normalize_superadmin_contact()` + `_require_superadmin_contact()` and calls the gate in both `provision_tenant()` (line ~439) and `provision_trial_tenant()` (line ~1084); `trial_management.py`, `repositories/tenant.py` (contactless query), and `app/background.py` (deactivation scanner) carry the matching `-001` changes.
- `python -m pytest tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py tests/unit/test_contactless_tenant_scanner_spec1882.py -q` → `15 passed` (the two new test files already pass).
- `python -m pytest <adjacent suite>` → `1 failed, 115 passed`; the sole failure is `tests/integrations/test_provisioning_webhooks.py::TestProvisionTrialTenant::test_trial_tenant_has_expiry`, which creates a contactless trial and is now correctly rejected by the SPEC-1882 gate.
- The new SPEC-1882 tests use `owner@example.com` / `admin@example.com` for tenancy-creating cases rather than the SPEC-1882-mandated `info@remakerdigital.com`.

## Proposed Scope

The `-001` source + new-test scope (steps 1-8 of `-001`) is unchanged and already implemented. This REVISED adds exactly two completion deltas:

1. **Repair the directly-invalidated historical test.** In `applications/Agent_Red/tests/integrations/test_provisioning_webhooks.py`, update `TestProvisionTrialTenant::test_trial_tenant_has_expiry` (and any sibling case in that class that creates a tenant without contact) to supply `customer_email="info@remakerdigital.com"` (or an equivalent canonical contact). The test's expiry/behavior intent is preserved; only the now-required contact argument is added. No unrelated fixtures or emails in that file are rewritten.
2. **Align new-test tenancy contacts to the canonical address.** In `test_superadmin_contact_requirement_spec1882.py`, switch tenancy-creating email contacts from `owner@example.com` / `admin@example.com` to `info@remakerdigital.com` (phone-only cases keep their phone). Co-update any dependent assertions (e.g., `display_name` expectations derived from the email).

No source behavior (gate, query, scanner) changes in this REVISED; the source files remain at their `-001` state.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1882` | New deterministic tests verify the all-channel contact gate, exact error text, no-write-on-rejection, trial enforcement, phone-only acceptance, contactless-tenant repository selection, automatic deactivation, AND that tenancy-creating tests use `info@remakerdigital.com`. The repaired historical trial test passes under the all-channel gate. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute the new SPEC-1882 test files plus the `-001` adjacent regression suite; the adjacent suite must be fully green (the `test_trial_tenant_has_expiry` regression resolved). |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Deltas applied only after LO `GO` on this REVISED, a fresh work-intent claim, and `implementation_authorization.py begin --bridge-id agent-red-wi3215-superadmin-contact-gate-coverage` against the 7-path scope. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | `ruff check` + `ruff format --check` on all touched Python files. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, 7-path target_paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementing the deltas:

```text
python -m pytest applications/Agent_Red/tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py applications/Agent_Red/tests/unit/test_contactless_tenant_scanner_spec1882.py applications/Agent_Red/tests/integrations/test_provisioning_webhooks.py applications/Agent_Red/tests/multi_tenant/test_tenant_display_name.py applications/Agent_Red/tests/integrations/test_spa_provisioning.py applications/Agent_Red/tests/multi_tenant/test_trial_management.py applications/Agent_Red/tests/unit/test_trial_scanner.py -q --tb=short
python -m ruff check applications/Agent_Red/src/integrations/provisioning.py applications/Agent_Red/src/multi_tenant/trial_management.py applications/Agent_Red/src/multi_tenant/repositories/tenant.py applications/Agent_Red/src/app/background.py applications/Agent_Red/tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py applications/Agent_Red/tests/unit/test_contactless_tenant_scanner_spec1882.py applications/Agent_Red/tests/integrations/test_provisioning_webhooks.py
python -m ruff format --check applications/Agent_Red/src/integrations/provisioning.py applications/Agent_Red/src/multi_tenant/trial_management.py applications/Agent_Red/src/multi_tenant/repositories/tenant.py applications/Agent_Red/src/app/background.py applications/Agent_Red/tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py applications/Agent_Red/tests/unit/test_contactless_tenant_scanner_spec1882.py applications/Agent_Red/tests/integrations/test_provisioning_webhooks.py
```

## Acceptance Criteria

- PASS when `provision_tenant()` / `provision_trial_tenant()` / `TrialManagementService.provision_trial()` reject `None`/empty/whitespace contacts before any repository write, with the exact SPEC-1882 error text, across Stripe/Shopify/manual/trial.
- PASS when phone-only tenant creation remains accepted.
- PASS when the `TenantRepository` contactless query and the background scanner deactivate only active tenants missing both contact channels (existing 15 new-test assertions remain green).
- PASS when new SPEC-1882 tests use `info@remakerdigital.com` for tenancy contact data.
- PASS when the repaired `test_trial_tenant_has_expiry` (and any sibling contactless-creation case) passes under the all-channel gate.
- PASS when the full adjacent regression suite is green (0 failures).
- PASS when ruff check and ruff format --check pass on all touched files.
- PASS when no source behavior beyond the `-001` gate/query/scanner is changed, and no unrelated historical fixtures, formal artifacts, project membership, new work items, credentials, deployment state, or release tags are changed.

## Risks / Rollback

Risk is low-to-moderate and unchanged in kind from `-001`. The behavior change (all-channel contact enforcement + contactless deactivation scanner) is already implemented and test-covered; this REVISED only completes test-contact alignment and repairs the single historical test that the spec-compliant change directly invalidated. The scope expansion is bounded to one additional test file and is owner-authorized.

Rollback is to revert the two delta edits (the historical-test contact argument and the new-test email values) and, if the whole WI is abandoned, to revert the `-001` source/test changes. Bridge audit files remain append-only.

## Files Expected To Change (this REVISED's deltas)

- `applications/Agent_Red/tests/integrations/test_provisioning_webhooks.py` (supply canonical contact to the contactless trial test)
- `applications/Agent_Red/tests/multi_tenant/test_superadmin_contact_requirement_spec1882.py` (switch tenancy email contacts to `info@remakerdigital.com`)

## Recommended Commit Type

`fix:`
