NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3197 Integrations Manager UI Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3197-integrations-manager-ui-coverage
Version: 001 (NEW)
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3197

target_paths: ["applications/Agent_Red/admin/shared/IntegrationsManager.tsx", "applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py"]

## Claim

WI-3197 should be implemented as a narrow source+test remediation for `SPEC-1772`.

Current `applications/Agent_Red/admin/shared/IntegrationsManager.tsx` already contains substantial SPEC-1772 UI structure:

- integration cards render status labels, last-sync text, sync-error text, and ticket/article/contact counts;
- disconnected OAuth integrations show setup guidance before activation;
- enabled Stripe integrations render `McpConfigPanel`, whose existing implementation provides the API-key form and connection test button;
- the detail panel includes config, sync, actions, and logs tabs;
- the sync tab has a `Sync Now` button and count summaries;
- the actions tab names HITL policy configuration; and
- the logs tab names connection logs and the integration-events API.

The same source does not currently expose the `SPEC-1772` source-selection clause for folder/page browsing in `IntegrationsManager.tsx`, and the imported detail-support types (`SyncEvent`, `ActionConfigItem`, `ConnectionLogEntry`) are not yet used to render sync-history errors, HITL policy controls, or connection-log details. This proposal keeps the remediation inside the named source component and adds deterministic Python source-level coverage for the resulting UI surface.

This proposal does not authorize backend APIs, generated frontend bundles, package dependency changes, deployment state, release tagging, formal GT-KB artifact mutation, project membership changes, credentials, or new work items.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1772` states the target Admin UI behavior directly and names `admin/shared/IntegrationsManager.tsx` as the source surface. `WI-3197` exists because prior assertion-only evidence was rejected under `DELIB-0712` and `DELIB-0713`. The source gap is small enough to remediate under the existing spec: make the existing detail panel render the already-specified source selection, sync-history, action-configuration, and connection-log details, then add deterministic tests mapped to every SPEC-1772 clause.

## In-Root Placement Evidence

The implementation targets are under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\admin\shared\IntegrationsManager.tsx`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_integrations_manager_spec1772.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\admin\shared\McpConfigPanel.tsx`
- `E:\GT-KB\applications\Agent_Red\admin\shared\types\index.ts`

## Specification Links

- `SPEC-1772` - Direct historical requirement text and source spec for Integration Framework Admin UI setup and dashboard behavior in `IntegrationsManager.tsx`.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live Admin UI source files are the exposed artifacts under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native tests must validate the source artifacts rather than rely on manual inspection or stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native pytest mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, GO, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies baseline lint/format checks to the new Python test and repo-native admin linting to the TSX source change where available.
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

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3197`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project; confirms project-level implementation authorization does not replace bridge proposal review, LO `GO`, implementation-start packets, specification-derived verification, or the ACID-invariant for new project items.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements, treating delta-prime specs as untested.
- `gt bridge threads --wi WI-3197 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.
- `gt deliberations search "WI-3197 SPEC-1772 IntegrationsManager source selection folder page browser"` returned broad bridge/project results but no WI-3197-specific blocking prior decision.

## Current-State Evidence

- MemBase `SPEC-1772` title: "Integration Framework - Admin UI Setup & Dashboard".
- MemBase `SPEC-1772` description requires: integration cards with real-time status, last sync, article/ticket counts; OAuth setup wizard and API-key inline form with test button; sync dashboard with timing, counts, errors, and Sync Now button; action configuration with HITL toggles; source selection with folder/page browser for knowledge integrations; connection logs with error details; and an integration detail page combining config, sync, actions, and logs.
- `gt bridge threads --wi WI-3197 --json` currently returns `match_count: 0`.
- `applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py` does not currently exist.
- `IntegrationsManager.tsx` currently imports `McpConfigPanel` and renders it for enabled Stripe integrations, while `McpConfigPanel.tsx` contains the existing API-key input/save and connection-test UI.
- `IntegrationsManager.tsx` currently defines detail tabs `config`, `sync`, `actions`, and `logs`, and renders `View Details` / `Hide Details` for connected integrations.
- `IntegrationsManager.tsx` currently has card-level last-sync/count/error fields and a sync-tab `Sync Now` call to `/api/admin/integrations/{integration.type}/sync`.
- `IntegrationsManager.tsx` does not currently render a source-selection folder/page browser for knowledge integrations.

## Pre-Filing Preflight Evidence

Applicability preflight:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3197-integrations-manager-ui-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.
- warning only: parser harvested prose/command fragments such as bare `tests/multi_tenant/test_integrations_manager_spec1772.py` and `config/sync/actions/logs`; the declared target paths remain the in-root `applications/Agent_Red/...` paths above.

Clause preflight:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3197-integrations-manager-ui-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- must_apply: `4`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Update `applications/Agent_Red/admin/shared/IntegrationsManager.tsx` only where needed to make the existing detail panel render the missing or currently-placeholder SPEC-1772 details:
   - retain integration cards with status labels, last sync, sync errors, and ticket/article/contact counts;
   - keep disconnected OAuth setup guidance and Stripe `McpConfigPanel` delegation for API-key form/test-button behavior;
   - render sync-history rows when present, including timestamp/timing, item counts, success/error status, and error messages;
   - render action configuration rows with visible HITL policy controls/toggles when action config is present;
   - render a source-selection area for knowledge integrations with folder and page browser controls; and
   - render connection-log rows with timestamp, severity, message, and error details when present, while preserving the integration-events API guidance.
2. Add `applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py`.
3. In the new pytest, read `IntegrationsManager.tsx`, `McpConfigPanel.tsx`, and the shared integration types source as text and assert the Admin UI source exposes each SPEC-1772 clause through concrete TSX/text/API evidence.
4. Keep the implementation inside the two target paths. If satisfying the requirement requires backend API, package, generated bundle, or formal artifact changes, stop and return through the bridge with a revised proposal.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1772` | New pytest verifies `IntegrationsManager.tsx` exposes integration-card status/count fields, OAuth activation guidance, Stripe `McpConfigPanel` delegation plus `McpConfigPanel.tsx` API-key/test-button evidence, sync dashboard evidence including `Sync Now`, timing/count/error details, action/HITL controls, knowledge source selection folder/page browser controls, connection logs with error details, and a detail panel combining config/sync/actions/logs. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic source-level test file and run admin frontend lint against the changed TSX source where available. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3197-integrations-manager-ui-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new Python test file; run the admin frontend lint script for the TSX source change. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py
python -m ruff format --check applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py
npm --prefix applications/Agent_Red/admin run lint -- --quiet
```

## Acceptance Criteria

- PASS when integration cards expose status labels plus last-sync, sync-error, ticket-count, article-count, and contact-count evidence.
- PASS when OAuth setup guidance and API-key form/test-button behavior are covered through `IntegrationsManager.tsx` plus its `McpConfigPanel.tsx` child surface.
- PASS when the sync tab exposes `Sync Now`, last-sync/timing evidence, counts, and sync-history error details.
- PASS when the actions tab exposes HITL policy controls/toggles for action configuration.
- PASS when knowledge integrations expose source selection with folder and page browser controls.
- PASS when connection logs expose timestamp, severity, message, and error details plus the integration-events API.
- PASS when the detail panel combines config, sync, actions, and logs tabs and remains reachable from connected integration cards.
- PASS when the targeted pytest, ruff, and admin lint commands pass.
- PASS when no backend APIs, generated bundles, package dependency files, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is moderate-low. The source change touches a shared Admin UI component, but the proposed behavior is additive inside existing cards/detail-panel tabs and uses optional detail arrays already represented in shared types. Source-level tests reduce regression risk without requiring browser orchestration.

Rollback is to revert `applications/Agent_Red/admin/shared/IntegrationsManager.tsx` and delete `applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/admin/shared/IntegrationsManager.tsx`
- `applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py`

## Recommended Commit Type

`fix:`
