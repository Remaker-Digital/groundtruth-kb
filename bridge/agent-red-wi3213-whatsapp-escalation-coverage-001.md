NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3213 WhatsApp Escalation Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3213-whatsapp-escalation-coverage
Version: 001 (NEW)
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3213

target_paths: ["applications/Agent_Red/src/multi_tenant/cosmos_schema.py", "applications/Agent_Red/src/multi_tenant/config/field_mapping.py", "applications/Agent_Red/src/chat/pipeline/orchestrator.py", "applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py", "applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py", "applications/Agent_Red/widget/tests/whatsapp-escalation-link.test.tsx"]

## Claim

WI-3213 should finish the bounded `SPEC-1880` v0 deep-link feature and add deterministic coverage against the live Agent Red paths that currently make the feature unreachable or weakly evidenced.

`SPEC-1880` requires a professional-plus WhatsApp escalation option using a merchant-configured WhatsApp number and a `wa.me/{merchant_phone}?text={context}` deep link. The current repository has partial implementation, but prior Loyal Opposition reviews and the current code inspection show three live gaps:

- `applications/Agent_Red/src/multi_tenant/schema/fields.yaml` defines `whatsapp_business_phone`, but `applications/Agent_Red/src/multi_tenant/config/field_mapping.py` does not include the field in `_PREFS_DIRECT_FIELDS`.
- `applications/Agent_Red/src/multi_tenant/cosmos_schema.py` does not declare `whatsapp_business_phone` on `PreferencesDocument`.
- `applications/Agent_Red/src/chat/pipeline/orchestrator.py` appends a raw WhatsApp URL, while `applications/Agent_Red/widget/src/components/MessageBubble.tsx` only converts markdown `[text](url)` links into anchors.

Existing tests at `applications/Agent_Red/tests/chat/test_whatsapp_escalation.py` only check local string formatting and regex behavior; they do not call the production config mapping, production WhatsApp link generation, or the widget renderer. This proposal adds narrow source fixes and tests that exercise the real feature path without expanding into future full WhatsApp channel integration, provider onboarding, templates, webhooks, ACS/Meta API work, phone identity linkage, or escalation state-machine changes.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1880` is concrete enough for this bounded v0 repair: merchant configures a WhatsApp number in tenant settings, professional-plus tenants receive a WhatsApp option on escalation, the link uses `wa.me/{merchant_phone}?text={context}`, and no WhatsApp API integration is required. The prior reviews (`DELIB-0514`, `DELIB-0547`) explicitly identify the missing source and test coverage needed to make that bounded feature real.

No new owner clarification is needed because this proposal does not implement future real-channel WhatsApp integration or change the product contract beyond making the already-specified deep-link feature persist, render as a clickable widget link, and receive production-path tests.

## In-Root Placement Evidence

All implementation targets are under the GT-KB root and the in-root Agent Red reference adopter subtree:

- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\cosmos_schema.py`
- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\config\field_mapping.py`
- `E:\GT-KB\applications\Agent_Red\src\chat\pipeline\orchestrator.py`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_whatsapp_config_spec1880.py`
- `E:\GT-KB\applications\Agent_Red\tests\chat\test_whatsapp_escalation_spec1880.py`
- `E:\GT-KB\applications\Agent_Red\widget\tests\whatsapp-escalation-link.test.tsx`

Read-only verification may inspect existing adjacent in-root files:

- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\schema\fields.yaml`
- `E:\GT-KB\applications\Agent_Red\widget\src\components\MessageBubble.tsx`
- `E:\GT-KB\applications\Agent_Red\widget\tests\structured-answer-blocks.test.tsx`

## Specification Links

- `SPEC-1880` - Direct requirement for a professional-plus WhatsApp escalation deep-link to a merchant-configured WhatsApp number.
- `GOV-10` - Test artifacts must exercise live exposed project paths; this proposal replaces string-only evidence with production mapping, production link-generation, and widget-render coverage.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native tests must validate live code paths rather than phantom or stale assertion rows.
- `GOV-12` - Work-item remediation must create or map test evidence.
- `GOV-13` - Test visibility and phase governance; the new tests create live spec-to-test evidence for the WI.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies changed-file hygiene; Python coverage will use targeted pytest plus ruff check and ruff format checks on touched Python files, and widget coverage will use the local Vitest lane.
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

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3213`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0712` - POR Step 16.B methodology review classifying phantom-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements.
- `DELIB-0515` - SPEC-1880 proposal review recommended revising scope to match the real execution path: config mapping, post-response escalation rendering, widget click/button rendering, and production-path tests.
- `DELIB-0514` - SPEC-1880 implementation review found that `whatsapp_business_phone` is accepted by the schema registry but dropped before persistence, the widget requirement is not satisfied by raw URL text, and the existing tests are shallow.
- `DELIB-0547` - WhatsApp Integration and Documentation Evaluation concluded the current work is incomplete even as a simple deep-link feature and recommended completing the v0 deep-link explicitly before future real-channel integration.
- `gt deliberations list --work-item-id WI-3213 --limit 10 --json` returned `[]`; no WI-linked deliberation entries exist for `WI-3213`.
- `gt bridge threads --wi WI-3213 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt backlog show WI-3213 --json` shows open/backlogged `WI-3213`, source spec `SPEC-1880`, project `AGENT-RED-TEST-COVERAGE-GAPS`, and the description says phantom-only evidence was rejected under `DELIB-0712`/`DELIB-0713`.
- `gt spec show SPEC-1880 --json` shows title "WhatsApp Escalation Channel: Deep-Link to Merchant WhatsApp", status `implemented`, and a requirement for escalation to offer a WhatsApp option using `wa.me/{merchant_phone}?text={context}`, merchant tenant-setting configuration, no API integration, and professional-plus tier.
- `applications/Agent_Red/src/multi_tenant/schema/fields.yaml` contains `whatsapp_business_phone`.
- `applications/Agent_Red/src/multi_tenant/config/field_mapping.py` `_PREFS_DIRECT_FIELDS` does not currently contain `whatsapp_business_phone`, so the standard config-to-preferences mapping does not persist it.
- `applications/Agent_Red/src/multi_tenant/cosmos_schema.py` `PreferencesDocument` does not currently declare `whatsapp_business_phone`.
- `applications/Agent_Red/src/chat/pipeline/orchestrator.py` currently appends the WhatsApp notice as raw URL text after escalation side effects complete.
- `applications/Agent_Red/widget/src/components/MessageBubble.tsx` currently converts markdown `[text](url)` syntax into clickable anchors, not raw URL text.
- `applications/Agent_Red/tests/chat/test_whatsapp_escalation.py` exists but checks hand-built strings and regexes only.
- `applications/Agent_Red/widget/package.json` exposes `test` as `vitest run` and `typecheck` as `tsc --noEmit`; existing widget tests import `MessageBubble` through `@testing-library/preact`.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3213-whatsapp-escalation-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `warnings.missing_parent_dirs: ["tests/chat/test_whatsapp_escalation_spec1880.py", "tests/multi_tenant/test_whatsapp_config_spec1880.py", "tests/whatsapp-escalation-link.test.tsx"]` (known conservative target-path over-harvest from shortened path mentions; declared `target_paths` are rooted under `applications/Agent_Red/`)
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3213-whatsapp-escalation-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `whatsapp_business_phone: str | None` to `PreferencesDocument` in `applications/Agent_Red/src/multi_tenant/cosmos_schema.py`.
2. Add `whatsapp_business_phone` to `_PREFS_DIRECT_FIELDS` in `applications/Agent_Red/src/multi_tenant/config/field_mapping.py`.
3. In `applications/Agent_Red/src/chat/pipeline/orchestrator.py`, factor the current inline WhatsApp link logic into a small production helper and use it from the post-response escalation branch.
4. Format the WhatsApp escalation notice as a markdown link, such as `[Open WhatsApp](https://wa.me/...)`, so the existing widget renderer produces a clickable anchor.
5. Add `applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py` proving the field exists on `PreferencesDocument`, is included in `_PREFS_DIRECT_FIELDS`, and survives `_config_to_preferences` plus `_preferences_to_config`.
6. Add `applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py` proving the production helper emits a URL-encoded `wa.me` markdown link for professional/enterprise tenants with a configured number, strips the leading plus for the URL path, includes conversation context, and suppresses the link for starter tenants or missing phone configuration.
7. Add `applications/Agent_Red/widget/tests/whatsapp-escalation-link.test.tsx` proving `MessageBubble` renders the markdown WhatsApp notice as a clickable anchor whose `href` targets `https://wa.me/...`.
8. Do not implement ACS, Meta, WhatsApp Business API, webhooks, templates, opt-in capture, phone identity linkage, admin inbox phone display, escalation state-machine expansion, or provider onboarding. Those are outside this bounded WI.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1880` | New Python and widget tests verify tenant config persistence for `whatsapp_business_phone`, professional-plus WhatsApp deep-link generation, `wa.me` URL context encoding, starter/missing-phone suppression, and clickable widget rendering. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest and Vitest against live source paths instead of string-only phantom evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3213-whatsapp-escalation-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check`, `ruff format --check`, Vitest, widget typecheck if needed, and whitespace diff checks on touched files. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py -q --tb=short
python -m pytest applications/Agent_Red/tests/chat/test_whatsapp_escalation.py applications/Agent_Red/tests/multi_tenant/test_config_yaml_schema.py applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py -q --tb=short
npm --prefix applications/Agent_Red/widget test -- whatsapp-escalation-link.test.tsx
npm --prefix applications/Agent_Red/widget run typecheck
python -m ruff check applications/Agent_Red/src/multi_tenant/cosmos_schema.py applications/Agent_Red/src/multi_tenant/config/field_mapping.py applications/Agent_Red/src/chat/pipeline/orchestrator.py applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py
python -m ruff format --check applications/Agent_Red/src/multi_tenant/cosmos_schema.py applications/Agent_Red/src/multi_tenant/config/field_mapping.py applications/Agent_Red/src/chat/pipeline/orchestrator.py applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py
git diff --check -- applications/Agent_Red/src/multi_tenant/cosmos_schema.py applications/Agent_Red/src/multi_tenant/config/field_mapping.py applications/Agent_Red/src/chat/pipeline/orchestrator.py applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py applications/Agent_Red/widget/tests/whatsapp-escalation-link.test.tsx
```

## Acceptance Criteria

- PASS when `whatsapp_business_phone` is declared on `PreferencesDocument`.
- PASS when `whatsapp_business_phone` is in `_PREFS_DIRECT_FIELDS`.
- PASS when config-to-preferences and preferences-to-config round-trip coverage preserves the field.
- PASS when the production WhatsApp link helper emits a markdown link to `https://wa.me/...` with URL-encoded conversation context for professional and enterprise tenants with a configured phone.
- PASS when starter tenants and missing-phone configurations do not receive a WhatsApp link.
- PASS when the widget `MessageBubble` renders the WhatsApp markdown notice as a clickable anchor with the expected `href`.
- PASS when targeted pytest, adjacent pytest, Vitest, widget typecheck, ruff check, ruff format check, and diff whitespace checks pass.
- PASS when no formal artifacts, project membership, new work items, credentials, deployment state, release tags, provider integrations, phone identity features, or full WhatsApp channel surfaces are changed.

## Risks / Rollback

Risk is moderate-low. The source changes complete a narrow v0 deep-link path already named by `SPEC-1880`, but they touch the tenant config persistence model and the chat stream text emitted to customers. The proposed tests keep the change bounded and avoid external WhatsApp/ACS/Meta dependencies.

Rollback is to remove `whatsapp_business_phone` from `PreferencesDocument` and `_PREFS_DIRECT_FIELDS`, restore the orchestrator's prior WhatsApp notice behavior, and delete the three new test files. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/src/multi_tenant/cosmos_schema.py`
- `applications/Agent_Red/src/multi_tenant/config/field_mapping.py`
- `applications/Agent_Red/src/chat/pipeline/orchestrator.py`
- `applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py`
- `applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py`
- `applications/Agent_Red/widget/tests/whatsapp-escalation-link.test.tsx`

## Recommended Commit Type

`fix:`
