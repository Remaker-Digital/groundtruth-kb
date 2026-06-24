REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Revised Implementation Proposal - WI-3199 Zendesk Integration Adapter Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3199-zendesk-integration-adapter-coverage
Version: 003 (REVISED)
Responds-To: bridge/agent-red-wi3199-zendesk-integration-adapter-coverage-002.md
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3199

target_paths: ["applications/Agent_Red/src/integrations/zendesk/adapter.py", "applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py"]

## Claim

WI-3199 should be revised from test-only coverage to a narrow source+test remediation for `SPEC-1775`.

The `GO` verdict at `bridge/agent-red-wi3199-zendesk-integration-adapter-coverage-002.md` approved only `applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py` and explicitly required Prime Builder to stop and return through the bridge if the new test exposed a source gap. Read-only source inspection and a minimal dispatch repro exposed a live adapter signature mismatch:

- `applications/Agent_Red/src/integrations/adapters.py:216` defines the customer lookup protocol as accepting both `email` and `customer_id` keyword arguments.
- `applications/Agent_Red/src/integrations/action_executor.py:357` routes `ActionType.CUSTOMER_LOOKUP` by calling `adapter.lookup_customer(tid, email=..., customer_id=...)`.
- `applications/Agent_Red/src/integrations/zendesk/adapter.py:489` implements `lookup_customer(self, tenant_id, *, email=None)` without the `customer_id` keyword.
- A direct read-only dispatch check raised `TypeError ZendeskAdapter.lookup_customer() got an unexpected keyword argument 'customer_id'`.

This revision keeps the fix inside the Zendesk adapter plus the spec-mapped test file. It does not authorize shared `ActionExecutor` edits, generated artifacts, deployment state, release tagging, formal GT-KB artifact mutation, project membership changes, credentials, or new work items.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1775` directly requires Zendesk "customer lookup by email". The shared integration action surface already routes customer lookup actions through `ActionExecutor`, and the live protocol shape already allows `customer_id` as an optional keyword. The source gap is not ambiguous: the Zendesk adapter must accept the shared lookup signature while continuing to implement the Zendesk requirement as email-based lookup. No owner clarification or new requirement is needed.

## In-Root Placement Evidence

Implementation targets are under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\src\integrations\zendesk\adapter.py`
- `E:\GT-KB\applications\Agent_Red\tests\integrations\test_zendesk_spec1775.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\src\integrations\adapters.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\action_executor.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\zendesk\manifest.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\manifest.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\models.py`

## Specification Links

- `SPEC-1775` - Direct requirement for the Zendesk full helpdesk adapter, including OAuth2, scopes, ticket/article/contact sources, destinations, customer lookup by email, webhooks, HMAC-SHA256 signature verification, status mapping, REST v2 cursor pagination, and 700 req/min.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live Zendesk adapter, manifest, and action-executor surfaces are the exposed artifacts under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest evidence must validate live code rather than stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility and phase governance; repository-native pytest mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies Python lint and formatting checks to the changed source and new test file.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires implementation proposals and revisions to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this revision uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use governed bridge helper paths and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this `REVISED` proposal as a lifecycle response to a discovered source gap.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3199`.

No waiver is requested. This revision asks Loyal Opposition to review a narrowed source+test scope before any source mutation.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project; confirms project-level implementation authorization does not replace bridge proposal review, LO `GO`, implementation-start packets, specification-derived verification, or the ACID-invariant for new project items.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements, treating delta-prime specs as untested.
- `bridge/agent-red-wi3199-zendesk-integration-adapter-coverage-001.md` - Original test-only implementation proposal.
- `bridge/agent-red-wi3199-zendesk-integration-adapter-coverage-002.md` - Loyal Opposition `GO` for test-only implementation, with an explicit condition to stop and revise if the new test exposed a source gap.
- `gt deliberations search "WI-3199 SPEC-1775 Zendesk Integration Full Helpdesk Adapter"` previously returned broad bridge/project records but no WI-3199-specific blocking prior decision.

## Current-State Evidence

- `gt bridge threads --wi WI-3199 --json` shows the current thread latest status is `GO` at `bridge/agent-red-wi3199-zendesk-integration-adapter-coverage-002.md`.
- `applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py` does not currently exist.
- `gt spec show SPEC-1775 --json` reports requirement text covering OAuth2, required scopes, ticket/article/contact sources, reply/draft/note/status/tag/assign/create destinations, customer lookup by email, ticket-created/updated webhooks, HMAC-SHA256 `x-zendesk-webhook-signature`, status mapping, REST v2 cursor pagination, and 700 req/min.
- `applications/Agent_Red/src/integrations/zendesk/manifest.py` declares OAuth2, scopes `read`, `write`, `tickets:read`, `tickets:write`, source/destination/action/webhook capabilities, hybrid sync, 700 RPM, and HMAC-SHA256 signature metadata.
- `applications/Agent_Red/src/integrations/zendesk/adapter.py` declares REST v2 request behavior, status maps, cursor pagination, Guide article methods, requester/contact normalization, customer lookup, webhook registration, and HMAC verification.
- `applications/Agent_Red/src/integrations/action_executor.py` routes public replies, reply drafts as internal notes, internal notes, status updates, tag additions, ticket assignment, ticket creation, article search, and customer lookup.
- Read-only repro from `applications/Agent_Red`: construct `ZendeskAdapter`, build an `AIAction` with `ActionType.CUSTOMER_LOOKUP` and an email parameter, then call `ActionExecutor._dispatch(adapter, action)`.

Observed result:

```text
TypeError ZendeskAdapter.lookup_customer() got an unexpected keyword argument 'customer_id'
```

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/agent-red-wi3199-zendesk-integration-adapter-coverage-003.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.
- warning only: parser-harvested bare path fragments such as `tests/integrations/test_zendesk_spec1775.py`; declared target paths remain the in-root `applications/Agent_Red/...` paths above.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/agent-red-wi3199-zendesk-integration-adapter-coverage-003.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Update `applications/Agent_Red/src/integrations/zendesk/adapter.py` narrowly:
   - make `ZendeskAdapter.lookup_customer` accept the shared lookup signature `email` plus optional `customer_id`;
   - preserve `SPEC-1775` email-based Zendesk user lookup behavior;
   - return no result for unsupported ID-only lookup rather than raising a signature `TypeError`;
   - do not change REST endpoint choices, auth behavior, status mapping, ticket/article methods, webhook verification, or error mapping.
2. Add `applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py`.
3. In the new pytest, import live Zendesk manifest, adapter constants/helpers, normalized models, and action-executor action types.
4. Assert manifest evidence for OAuth2, required scopes, source/destination/action/webhook capabilities, hybrid sync strategy, 700 RPM, and HMAC-SHA256 signature metadata.
5. Assert adapter evidence for Zendesk-to-normalized and normalized-to-Zendesk status mappings.
6. Assert adapter request behavior uses REST v2 paths and cursor pagination for tickets, Guide article access, requester/contact normalization, and customer lookup by email.
7. Assert webhook signature verification uses the configured Zendesk signature header with HMAC-SHA256 semantics.
8. Assert `ActionExecutor` destination/action routing represents public reply, draft-as-internal-note, internal note, status update, tag add, assign, create, article search, and customer lookup by email without the current signature `TypeError`.
9. Keep implementation inside the two target paths. If satisfying the requirement requires shared executor, registry, manifest, package, generated artifact, or formal artifact changes, stop and return through the bridge again.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1775` | New pytest imports live Zendesk adapter/manifest/action-executor surfaces and asserts OAuth2/scopes, ticket/article/contact sources, reply/draft/note/status/tag/assign/create destinations, customer lookup by email through the executor, ticket-created/updated webhook metadata, HMAC signature verification, status mapping, REST v2 cursor pagination, and 700 req/min metadata. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic Zendesk spec-mapping test file, using live in-repository source modules. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3199-zendesk-integration-adapter-coverage` on this revised scope. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the changed source and new test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py -q --tb=short
python -m ruff check applications/Agent_Red/src/integrations/zendesk/adapter.py applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py
python -m ruff format --check applications/Agent_Red/src/integrations/zendesk/adapter.py applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py
```

## Acceptance Criteria

- PASS when `ZendeskAdapter.lookup_customer` accepts the shared `email` plus optional `customer_id` signature and does not raise `TypeError` when routed through `ActionExecutor`.
- PASS when customer lookup remains email-based for Zendesk and uses `/api/v2/users/search.json`.
- PASS when the new pytest verifies OAuth2 auth and required Zendesk OAuth scopes.
- PASS when the new pytest verifies source capabilities for tickets, articles, and contacts.
- PASS when the new pytest verifies destination/action coverage for public reply, draft, internal note, status update, tag, assign, create, article search, and customer lookup.
- PASS when the new pytest verifies ticket-created/updated webhook metadata and HMAC-SHA256 signature verification.
- PASS when the new pytest verifies the required Zendesk status mapping in both directions.
- PASS when the new pytest verifies REST v2 request path usage, ticket cursor pagination, Guide article access, and 700 req/min rate-limit metadata.
- PASS when targeted pytest and ruff commands all pass.
- PASS when no shared executor edits, existing-test rewrites, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is low-to-moderate. The source change is intentionally limited to making the Zendesk adapter conform to the already used customer-lookup call signature while preserving email-based behavior required by `SPEC-1775`. The main risk is that the new spec-mapped test identifies an additional source gap outside these target paths; if so, Prime Builder will stop and return through the bridge rather than broadening implementation scope.

Rollback is to revert `applications/Agent_Red/src/integrations/zendesk/adapter.py` and delete `applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py`. Bridge audit files remain append-only and should not be deleted.

## Files Expected To Change

- `applications/Agent_Red/src/integrations/zendesk/adapter.py`
- `applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py`

## Recommended Commit Type

`fix:`
