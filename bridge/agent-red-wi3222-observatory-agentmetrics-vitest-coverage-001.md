NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 4e30eeba-5f51-4cad-89fd-793ac8f59e98
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: Claude Code interactive; role=prime-builder; output_style=explanatory
author_metadata_source: interactive Claude runtime envelope plus hand-authored bridge proposal

# Implementation Proposal - WI-3222 Pipeline Observatory Agent Metrics Vitest Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3222-observatory-agentmetrics-vitest-coverage
Version: 001 (NEW)
Date: 2026-06-25 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3222

target_paths: ["applications/Agent_Red/admin/provider/pages/PipelineObservatory.tsx", "applications/Agent_Red/admin/provider/tests/PipelineObservatory.agentmetrics.test.tsx"]

## Claim

WI-3222 should add deterministic Vitest component coverage for `SPEC-1586`
"Pipeline Observatory: Agent Metrics performance cards tab", the second member of
the Observatory frontend cluster, building on the Vitest + React Testing Library
harness established and committed by the sibling WI-3221 thread
(`agent-red-wi3221-observatory-trafficflow-vitest-coverage`, commit `cbf5e7f28`).

`SPEC-1586` is **retired**, but its `AgentMetricsTab`
(`applications/Agent_Red/admin/provider/pages/PipelineObservatory.tsx:314`) still
ships in the live component (fetching `/api/superadmin/pipeline/topology` and
rendering per-agent performance cards: invocation count, avg cost, P50/P95/P99
latency percentiles, token usage, error-rate badge). Its mapped tests
`TEST-2773`/`TEST-2774` are `e2e`-type and `stale`. Per the in-session owner
AskUserQuestion decision (2026-06-25), the retired-spec tabs are **covered anyway**
because the code is still live.

This is a bounded `test_addition` + `source` item: it adds one Vitest test module
and exports `AgentMetricsTab` (behavior-neutral) for isolated rendering. No harness
scaffold is needed — WI-3221 already installed it. No production behavior changes.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-1586` (retired) plus the live
`AgentMetricsTab` give a complete render contract for deterministic coverage, and
the owner AskUserQuestion decision authorizes covering the retired-spec tab. No
further owner clarification is required.

## Owner Decisions / Input

Governed by two owner decisions: (1) project authorization
`PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`
(owner decision `DELIB-20265586`), whose allowed mutation classes include
`test_addition` and `source` and whose snapshot includes `WI-3222`; and (2) the
2026-06-25 in-session AskUserQuestion decision to use Vitest component tests and to
cover the retired-spec tabs (SPEC-1586/1587) anyway. No new owner decision is required.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB\applications\Agent_Red\` per
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`:

- `applications/Agent_Red/admin/provider/pages/PipelineObservatory.tsx` (`export` addition)
- `applications/Agent_Red/admin/provider/tests/PipelineObservatory.agentmetrics.test.tsx` (new)

## Specification Links

- `SPEC-1586` - Direct (retired) requirement: Pipeline Observatory Agent Metrics tab; covered anyway per owner decision because the tab code still ships.
- `GOV-10` - Tests exercise the live `AgentMetricsTab` component interface.
- `SPEC-1649` - Master test plan / live-interface policy.
- `GOV-12` - Work-item remediation creates test evidence.
- `GOV-13` - Test visibility / phase governance.
- `GOV-08` - KB-tracked coverage gap.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped authorization does not replace bridge review, GO, target paths, implementation-start packet, report, or verification.
- `SPEC-AUQ-POLICY-ENGINE-001` - Frontend test model + retired-tab coverage set by the in-session AskUserQuestion decision.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Frontend quality gates: `npm test` (vitest) + `npm run typecheck` (tsc).
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
- `gt bridge threads --wi WI-3222 --json` returned `match_count: 0` before this proposal.

## Current-State Evidence

- `gt spec show SPEC-1586` shows status `retired`; mapped tests `TEST-2773`/`TEST-2774` are `e2e`/`stale`.
- `AgentMetricsTab` (PipelineObservatory.tsx:314) is a module-internal function consuming `useProviderContext` and rendering per-agent cards from the topology response.
- The Vitest harness (`vitest.config.ts`, `tests/setup.ts`, devDeps) exists and is committed in `cbf5e7f28` from WI-3221.

## Proposed Scope

1. Export `AgentMetricsTab` from `PipelineObservatory.tsx` (behavior-neutral, mirrors the WI-3221 `TrafficFlowTab` export).
2. Add `tests/PipelineObservatory.agentmetrics.test.tsx`: mock `useProviderContext` (via `vi.hoisted` + `vi.mock`) to drive the topology fetch from a fixture, render `<AgentMetricsTab />` in `MantineProvider`, and assert an agent card renders its invocation count, error-rate percentage, and a latency-percentile value; assert the `onNotify('Failed to load agent metrics', 'error')` path on a non-ok fetch.
3. No harness scaffold, no other tabs, no production behavior changes.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1586` (Agent Metrics cards) | `AgentMetricsTab` renders invocation count, error-rate %, and a latency percentile from a mocked topology fixture. |
| `SPEC-1586` (failure path) | Non-ok fetch invokes `onNotify('Failed to load agent metrics', 'error')` and shows "Unable to load agent metrics". |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Vitest component suite over the live `AgentMetricsTab`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | `npm test` + `npm run typecheck` (cwd `applications/Agent_Red/admin/provider`). |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation starts only after LO `GO`, claim, and `implementation_authorization.py begin --bridge-id agent-red-wi3222-observatory-agentmetrics-vitest-coverage`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Targets under `applications/Agent_Red/admin/provider/`. |

Required commands after implementation (cwd `applications/Agent_Red/admin/provider`):

```text
npm test
npm run typecheck
```

## Acceptance Criteria

- PASS when `npm test` runs the Agent Metrics suite green and `npm run typecheck` is clean.
- PASS when `AgentMetricsTab` renders an agent card's invocation count, error-rate %, and a latency percentile.
- PASS when a non-ok fetch invokes the error notification path.
- PASS when the `export` is the only change to `PipelineObservatory.tsx` and no runtime behavior is altered.
- PASS when no other tabs, formal artifacts, project membership, credentials, or release/deployment state are changed.

## Risks / Rollback

Risk is low — additive test coverage + a behavior-neutral `export`, on an existing harness. Rollback: delete the test file and remove the `export`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/admin/provider/pages/PipelineObservatory.tsx` (`export` addition)
- `applications/Agent_Red/admin/provider/tests/PipelineObservatory.agentmetrics.test.tsx` (new)

## Pre-Filing Preflight Evidence

To be populated from the two mandatory preflights against this draft before the helper write; Loyal Opposition should rerun both against the operative bridge file.

## Recommended Commit Type

`test:`
