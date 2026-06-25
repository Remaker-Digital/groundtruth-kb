NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 4e30eeba-5f51-4cad-89fd-793ac8f59e98
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: Claude Code interactive; role=prime-builder; output_style=explanatory
author_metadata_source: interactive Claude runtime envelope plus hand-authored bridge proposal

# Implementation Proposal - WI-3223 Pipeline Observatory Tenant Comparison Vitest Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3223-observatory-tenants-vitest-coverage
Version: 001 (NEW)
Date: 2026-06-25 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3223

target_paths: ["applications/Agent_Red/admin/provider/pages/PipelineObservatory.tsx", "applications/Agent_Red/admin/provider/tests/PipelineObservatory.tenants.test.tsx"]

## Claim

WI-3223 should add deterministic Vitest component coverage for `SPEC-1587`
"Pipeline Observatory: Tenant Comparison sortable/filterable table tab", the third
member of the Observatory frontend cluster, building on the Vitest harness
established by WI-3221 (commit `cbf5e7f28`).

`SPEC-1587` is **retired**, but its `TenantComparisonTab`
(`applications/Agent_Red/admin/provider/pages/PipelineObservatory.tsx:410`) still
ships, fetching `/api/superadmin/pipeline/tenants` and rendering a Sort-By select,
a "Total Tenants" card, and a sortable tenant table (tenant, tier, conversations,
billable, latency, error rate, escalation, tokens, cost, est. RU). Its mapped tests
`TEST-2775`/`TEST-2776`/`TEST-2777` are `e2e`/`stale`. Per the in-session owner
AskUserQuestion decision (2026-06-25), the retired-spec tabs are covered anyway.

**Live-state note (verify-against-canonical discipline):** the live component
implements only the sortable table (`TEST-2775`). The search/filter input
(`TEST-2776`) and CSV export (`TEST-2777`) that the retired SPEC-1587 originally
specified are **not present** in the live `TenantComparisonTab` (dropped with spec
retirement). This proposal therefore scopes coverage to the live sortable-table +
sort + empty-state + error behavior, and does not invent coverage for the absent
features.

This is a bounded `test_addition` + `source` item: it exports `TenantComparisonTab`
(behavior-neutral) and adds one Vitest test. No harness scaffold; no production
behavior changes.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-1587` (retired) plus the live
`TenantComparisonTab` give a complete render contract for the implemented sortable
table; the owner AskUserQuestion decision authorizes covering the retired-spec tab.
No further owner clarification is required.

## Owner Decisions / Input

Governed by (1) project authorization
`PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`
(owner decision `DELIB-20265586`; allowed classes include `test_addition` + `source`;
snapshot includes `WI-3223`), and (2) the 2026-06-25 in-session AskUserQuestion
decision (Vitest model + cover retired-spec tabs). No new owner decision is required.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB\applications\Agent_Red\` per
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`:

- `applications/Agent_Red/admin/provider/pages/PipelineObservatory.tsx` (`export` addition)
- `applications/Agent_Red/admin/provider/tests/PipelineObservatory.tenants.test.tsx` (new)

## Specification Links

- `SPEC-1587` - Direct (retired) requirement: Pipeline Observatory Tenant Comparison tab; covered anyway per owner decision because the tab code still ships. Live coverage scoped to the implemented sortable table.
- `GOV-10` - Tests exercise the live `TenantComparisonTab` component interface.
- `SPEC-1649` - Master test plan / live-interface policy.
- `GOV-12` - Work-item remediation creates test evidence.
- `GOV-13` - Test visibility / phase governance.
- `GOV-08` - KB-tracked coverage gap.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped authorization does not replace bridge review, GO, target paths, implementation-start packet, report, or verification.
- `SPEC-AUQ-POLICY-ENGINE-001` - Frontend test model + retired-tab coverage set by the in-session AskUserQuestion decision.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Frontend quality gates: `npm test` + `npm run typecheck`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Status-bearing bridge file authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification maps linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project/PAUTH/WI metadata present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Targets under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Uses the existing authorized WI; no project-scope change.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Durable bridge/test evidence preserved.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization (PAUTH).
- `DELIB-0712` / `DELIB-0713` - phantom/stale-evidence remediation; deterministic evidence required.
- `bridge/agent-red-wi3221-observatory-trafficflow-vitest-coverage-002.md` - sibling GO establishing the Vitest harness this proposal reuses.
- In-session AskUserQuestion (2026-06-25): Vitest model + cover retired-spec tabs (to be archived as a deliberation at session wrap).
- `gt bridge threads --wi WI-3223 --json` returned `match_count: 0` before this proposal.

## Current-State Evidence

- `gt spec show SPEC-1587` shows status `retired`; mapped tests `TEST-2775`/`TEST-2776`/`TEST-2777` are `e2e`/`stale`.
- `TenantComparisonTab` (PipelineObservatory.tsx:410) renders the Sort-By select, the "Total Tenants" card, and the tenant table; it has no search/filter input or CSV-export button.
- The Vitest harness exists and is committed in `cbf5e7f28` from WI-3221.

## Proposed Scope

1. Export `TenantComparisonTab` from `PipelineObservatory.tsx` (behavior-neutral).
2. Add `tests/PipelineObservatory.tenants.test.tsx`: mock `useProviderContext` to drive the tenants fetch from a fixture (`{ tenants: [...], total: N, sortBy }`), render `<TenantComparisonTab />` in `MantineProvider`, and assert the total-tenants value, a tenant row's displayName + conversation count + cost, and the Sort-By select label; assert the empty-state ("No tenant data available") when `tenants` is empty; and the `onNotify(..., 'error')` path on a non-ok fetch.
3. No harness scaffold; no coverage of absent search/CSV features; no production behavior changes.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1587` (sortable table, TEST-2775) | `TenantComparisonTab` renders total + a tenant row (displayName, conversations, cost) + the Sort-By select from a mocked fixture. |
| `SPEC-1587` (empty + failure) | Empty `tenants` shows "No tenant data available"; non-ok fetch invokes `onNotify(..., 'error')`. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Vitest component suite over the live `TenantComparisonTab`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | `npm test` + `npm run typecheck` (cwd `applications/Agent_Red/admin/provider`). |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation starts only after LO `GO`, claim, and `implementation_authorization.py begin --bridge-id agent-red-wi3223-observatory-tenants-vitest-coverage`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Targets under `applications/Agent_Red/admin/provider/`. |

Required commands after implementation (cwd `applications/Agent_Red/admin/provider`):

```text
npm test
npm run typecheck
```

## Acceptance Criteria

- PASS when `npm test` runs the Tenant Comparison suite green and `npm run typecheck` is clean.
- PASS when `TenantComparisonTab` renders the total, a tenant row, and the Sort-By select.
- PASS when an empty tenant set shows the empty-state and a non-ok fetch invokes the error path.
- PASS when the `export` is the only change to `PipelineObservatory.tsx` and no runtime behavior is altered.
- PASS when no other tabs, formal artifacts, project membership, credentials, or release/deployment state are changed.

## Risks / Rollback

Risk is low — additive test coverage + a behavior-neutral `export`, on an existing harness. Rollback: delete the test file and remove the `export`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/admin/provider/pages/PipelineObservatory.tsx` (`export` addition)
- `applications/Agent_Red/admin/provider/tests/PipelineObservatory.tenants.test.tsx` (new)

## Pre-Filing Preflight Evidence

To be populated from the two mandatory preflights against this draft before the helper write; Loyal Opposition should rerun both against the operative bridge file.

## Recommended Commit Type

`test:`
