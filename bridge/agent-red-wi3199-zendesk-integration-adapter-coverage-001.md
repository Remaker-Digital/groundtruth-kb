NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3199 Zendesk Integration Adapter Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3199-zendesk-integration-adapter-coverage
Version: 001 (NEW)
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3199

target_paths: ["applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py"]

## Claim

WI-3199 should be implemented as a narrow test-only backfill for `SPEC-1775`.

Current Agent Red source already contains a full Zendesk helpdesk adapter under `applications/Agent_Red/src/integrations/zendesk/`, plus action-executor routing that maps draft replies to internal-note storage. Existing integration tests cover many behaviors, but the open coverage-gap work item exists because previous assertion-only evidence was rejected under `DELIB-0712` and `DELIB-0713`. This proposal adds one deterministic, spec-mapped pytest that makes the SPEC-1775 coverage explicit without changing runtime code.

This proposal does not authorize source edits, existing-test rewrites, generated artifacts, deployment state, release tagging, formal GT-KB artifact mutation, project membership changes, credentials, or new work items. If the new test exposes a current source gap, Prime Builder should stop and return through the bridge with a revised source+test proposal rather than broadening target paths under this NEW proposal.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1775` directly states the testable Zendesk adapter behavior: OAuth2 auth and scopes, ticket/article/contact sources, reply/draft/note/status/tag/assign/create destinations, customer lookup, ticket-created/updated webhooks with HMAC-SHA256 signature header, status mapping, REST v2 cursor pagination, and 700 req/min limit. `WI-3199` asks for deterministic test evidence for that existing requirement; no owner clarification is needed to add a mapped regression test.

## In-Root Placement Evidence

The implementation target is under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\tests\integrations\test_zendesk_spec1775.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\src\integrations\zendesk\adapter.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\zendesk\manifest.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\action_executor.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\manifest.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\models.py`

## Specification Links

- `SPEC-1775` - Direct historical requirement text and source spec for the Zendesk full helpdesk adapter.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live Zendesk adapter, manifest, and action-executor surfaces are the exposed artifacts under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest evidence must validate live code rather than rely on manual inspection or stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native pytest mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, GO, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies the baseline Python lint and formatting checks to the new test file.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use the governed bridge helper path and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3199`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project; confirms project-level implementation authorization does not replace bridge proposal review, LO `GO`, implementation-start packets, specification-derived verification, or the ACID-invariant for new project items.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements, treating delta-prime specs as untested.
- `gt bridge threads --wi WI-3199 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.
- `gt deliberations search "WI-3199 SPEC-1775 Zendesk Integration Full Helpdesk Adapter"` returned broad bridge/project results but no WI-3199-specific blocking prior decision.

## Current-State Evidence

- MemBase `SPEC-1775` title: "Zendesk Integration - Full Helpdesk Adapter".
- MemBase `SPEC-1775` description requires OAuth2 auth; scopes `read`, `write`, `tickets:read`, `tickets:write`; sources for tickets with history, Guide articles, and requester contacts; destinations for public reply, draft, internal note, status update, tag, assign, and create; customer lookup by email; `ticket.created` / `ticket.updated` webhooks; HMAC-SHA256 `x-zendesk-webhook-signature`; status mapping; REST v2 cursor pagination; and 700 req/min.
- `gt bridge threads --wi WI-3199 --json` currently returns `match_count: 0`.
- `applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py` does not currently exist.
- `applications/Agent_Red/src/integrations/zendesk/manifest.py` declares OAuth2, the four required scopes, the Zendesk helpdesk source/destination/action/webhook capabilities, hybrid sync, 700 RPM, and HMAC-SHA256 signature metadata.
- `applications/Agent_Red/src/integrations/zendesk/adapter.py` declares the status maps, REST v2 request base, cursor pagination for tickets, Guide article methods, requester/contact normalization, customer lookup, webhook registration, HMAC verification, and HTTP error mapping.
- `applications/Agent_Red/src/integrations/action_executor.py` routes public replies, reply drafts, internal notes, status updates, tag additions, ticket assignment, and ticket creation through adapter methods; reply drafts are stored as internal notes.

## Pre-Filing Preflight Evidence

Applicability preflight:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3199-zendesk-integration-adapter-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.
- warning only: parser harvested prose/command fragments such as bare `tests/integrations/test_zendesk_spec1775.py`; the declared target path remains the in-root `applications/Agent_Red/...` path above.

Clause preflight:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3199-zendesk-integration-adapter-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- must_apply: `4`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py`.
2. In the new pytest, import the live Zendesk manifest, adapter constants/helpers, normalized models, and action-executor action types.
3. Assert the manifest exposes the required OAuth2 auth configuration, scopes, source/destination/action/webhook capabilities, hybrid sync strategy, 700 RPM limit, and HMAC-SHA256 signature metadata.
4. Assert the adapter exposes the required Zendesk-to-normalized and normalized-to-Zendesk status mappings.
5. Assert adapter request behavior uses REST v2 paths and cursor pagination for tickets, and imports/normalizes requester contacts and Guide articles.
6. Assert webhook signature verification uses `x-zendesk-webhook-signature` HMAC-SHA256 semantics.
7. Assert `ActionExecutor` action routing represents the required destinations, including public reply, draft-as-internal-note, internal note, status update, tag add, assign, and create.
8. Keep implementation test-only unless the test exposes a current source gap; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1775` | New pytest imports live Zendesk adapter/manifest/action-executor surfaces and asserts OAuth2/scopes, source/destination/action/webhook capabilities, status mapping, REST v2 cursor pagination, 700 RPM, HMAC signature verification, customer lookup, and destination routing including draft/internal note behavior. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic Zendesk spec-mapping test file. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3199-zendesk-integration-adapter-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py
python -m ruff format --check applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py
```

## Acceptance Criteria

- PASS when the new pytest verifies OAuth2 auth and required Zendesk OAuth scopes.
- PASS when the new pytest verifies source capabilities for tickets, articles, and contacts.
- PASS when the new pytest verifies destination/action coverage for public reply, draft, internal note, status update, tag, assign, create, and customer lookup.
- PASS when the new pytest verifies ticket-created/updated webhook metadata and HMAC-SHA256 signature verification.
- PASS when the new pytest verifies the required Zendesk status mapping in both directions.
- PASS when the new pytest verifies REST v2 request path usage, ticket cursor pagination, Guide article access, and 700 req/min rate limit metadata.
- PASS when the targeted pytest and ruff commands all pass.
- PASS when no source edits, existing-test rewrites, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is low. The proposal adds one deterministic test module and does not alter runtime behavior. The main risk is that the test may reveal a real source gap in the historical adapter; if that happens, Prime Builder will stop and revise rather than widening this proposal.

Rollback is to delete `applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/integrations/test_zendesk_spec1775.py`

## Recommended Commit Type

`test:`
