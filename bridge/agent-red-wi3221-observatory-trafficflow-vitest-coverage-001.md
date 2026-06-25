NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 4e30eeba-5f51-4cad-89fd-793ac8f59e98
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: Claude Code interactive; role=prime-builder; output_style=explanatory
author_metadata_source: interactive Claude runtime envelope plus hand-authored bridge proposal

# Implementation Proposal - WI-3221 Pipeline Observatory Traffic Flow Vitest Coverage + Admin Harness

bridge_kind: prime_proposal
Document: agent-red-wi3221-observatory-trafficflow-vitest-coverage
Version: 001 (NEW)
Date: 2026-06-25 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3221

target_paths: ["applications/Agent_Red/admin/provider/package.json", "applications/Agent_Red/admin/provider/package-lock.json", "applications/Agent_Red/admin/provider/vitest.config.ts", "applications/Agent_Red/admin/provider/tests/setup.ts", "applications/Agent_Red/admin/provider/tests/PipelineObservatory.trafficflow.test.tsx", "applications/Agent_Red/admin/provider/pages/PipelineObservatory.tsx"]

## Claim

WI-3221 should add deterministic component-test coverage for `SPEC-1585`
"Pipeline Observatory: Traffic Flow visual topology tab" and, as the foundational
member of the frontend cluster, stand up the Vitest + React Testing Library
harness the `admin/provider` app currently lacks.

`SPEC-1585` is implemented in
`applications/Agent_Red/admin/provider/pages/PipelineObservatory.tsx`
(`TrafficFlowTab`, which fetches `/api/superadmin/pipeline/topology` and renders
the total-conversations summary, per-agent node cards with invocation counts, and
the agent-to-agent edge table). Its mapped tests `TEST-2771`/`TEST-2772` are
`e2e`-type and `stale`, and the `admin/provider` app has **no live frontend test
harness** (its `package.json` has no `vitest`/`@testing-library` devDependencies
and no `test` script; the only Observatory test is the Python backend API test
`tests/multi_tenant/test_pipeline_observatory_api.py`).

Per the owner decision in this session (AskUserQuestion, 2026-06-25): the frontend
cluster (WI-3221-3224) uses **Vitest component tests**, and the retired-spec tabs
(SPEC-1586/1587) are covered anyway because the code still ships. This proposal is
the cluster's foundational slice: it establishes the reusable harness plus the
Traffic Flow coverage; the sibling tabs (WI-3222/3223) and the deployment modal
(WI-3224) build on the same harness in follow-on threads.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1585` specifies the Traffic Flow tab behavior (topology fetch, agent nodes,
invocation counts, edge transitions), and the live `TrafficFlowTab` realizes it.
The owner AskUserQuestion decision authorizes the Vitest harness model. No further
owner clarification is required to write the harness + the Traffic Flow test.

## Owner Decisions / Input

This proposal is governed by two owner decisions:

1. Project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`
   (owner decision `DELIB-20265586`, 2026-06-23), whose allowed mutation classes
   include `scaffold_update`, `test_addition`, and `source` — the three classes
   this proposal exercises — and whose snapshot includes `WI-3221`.
2. The 2026-06-25 in-session AskUserQuestion decision selecting **Vitest component
   tests** as the frontend test model and **cover the retired-spec tabs anyway**.
   This proposal implements the harness that decision requires.

No additional owner decision is required to proceed.

## In-Root Placement Evidence

All target paths are in-root Agent Red application files under
`E:\GT-KB\applications\Agent_Red\` per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`:

- `applications/Agent_Red/admin/provider/package.json` (+ `package-lock.json`)
- `applications/Agent_Red/admin/provider/vitest.config.ts` (new)
- `applications/Agent_Red/admin/provider/tests/setup.ts` (new)
- `applications/Agent_Red/admin/provider/tests/PipelineObservatory.trafficflow.test.tsx` (new)
- `applications/Agent_Red/admin/provider/pages/PipelineObservatory.tsx` (minimal `export` addition)

## Specification Links

- `SPEC-1585` - Direct requirement: Pipeline Observatory Traffic Flow tab (topology
  render, agent nodes, invocation counts, edge transitions).
- `GOV-10` - Test artifacts must exercise live project interfaces; this adds an
  executable component test over the live `TrafficFlowTab` instead of stale e2e
  evidence.
- `SPEC-1649` - Master test plan / live-interface policy.
- `GOV-12` - Work-item remediation must create or map test evidence.
- `GOV-13` - Test visibility and phase governance.
- `GOV-08` - Canonical MemBase behavior; the WI's coverage gap is KB-tracked.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner
  authorization does not replace bridge review, `GO`, target paths,
  implementation-start packet, report, or verification.
- `SPEC-AUQ-POLICY-ENGINE-001` - The frontend test model is set by the in-session
  AskUserQuestion decision; no further owner decision is required.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires citing all
  relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires verification to map
  linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project/PAUTH/WI
  metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red application files live
  under `applications/Agent_Red/`; this target set honors that boundary.
- `GOV-STANDING-BACKLOG-001` - Uses the existing authorized WI; no project-scope change.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and
  review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this proposal as a lifecycle
  artifact for the work item.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red
  test-coverage-gap project.
- `DELIB-0712` / `DELIB-0713` - γ' phantom/stale-evidence remediation; executable
  evidence required.
- In-session AskUserQuestion (2026-06-25): frontend cluster uses Vitest component
  tests; retired-spec tabs covered anyway. (To be archived as a deliberation
  during session wrap.)
- `gt bridge threads --wi WI-3221 --json` returned `match_count: 0` before this
  proposal; no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt spec show SPEC-1585` shows status `implemented` and the Traffic Flow tab
  requirement; mapped tests `TEST-2771`/`TEST-2772` are `e2e`/`stale`.
- `applications/Agent_Red/admin/provider/package.json` has devDependencies
  `@vitejs/plugin-react`, `vite`, `typescript`, and type packages only — no
  `vitest`, no `@testing-library/*`, no test runner, and no `test` script.
- `applications/Agent_Red/widget/package.json` proves Vitest is used in Agent Red
  (`vitest`, `@testing-library/jest-dom`, `happy-dom`, `test: vitest run`), but the
  widget is Preact (`@testing-library/preact`); `admin/provider` is React 18, so
  the harness mirrors the Vitest *runner* with a React binding
  (`@testing-library/react`).
- `TrafficFlowTab` (PipelineObservatory.tsx:162) consumes `useProviderContext()`
  for `apiFetch`/`onNotify` and renders Mantine components; it is a module-internal
  function (not exported), so isolated testing needs a minimal `export` addition.

## Proposed Scope

1. **Harness scaffold (`scaffold_update`):**
   - `package.json`: add devDependencies `vitest`, `@testing-library/react`,
     `@testing-library/jest-dom`, `@testing-library/user-event`, `happy-dom`
     (versions aligned with the widget's Vitest where shared), and a
     `"test": "vitest run"` + `"test:watch": "vitest"` script.
   - `package-lock.json`: regenerated by `npm install` for the added devDeps.
   - `vitest.config.ts`: `@vitejs/plugin-react`, `test.environment = "happy-dom"`,
     `test.globals = true`, `test.setupFiles = ["./tests/setup.ts"]`, and the same
     `@shared` alias as `vite.config.ts`.
   - `tests/setup.ts`: import `@testing-library/jest-dom`; install the
     `window.matchMedia`, `ResizeObserver`, and `scrollIntoView` shims Mantine
     requires under happy-dom.
2. **Testability (`source`):** add `export` to `TrafficFlowTab` in
   `PipelineObservatory.tsx` (no runtime/behavior change; widens the module's test
   surface only).
3. **Traffic Flow test (`test_addition`):**
   `tests/PipelineObservatory.trafficflow.test.tsx` mocks `useProviderContext`
   (via `vi.mock('../layouts/ProviderLayout')`) to supply an `apiFetch` returning a
   deterministic topology fixture (nodes with invocation counts, edges with
   volumes, `totalConversations`), renders `<TrafficFlowTab />` inside a
   `MantineProvider`, awaits the async load, and asserts: the total-conversations
   value renders, an agent node card renders its invocation count (TEST-2771
   topology render), and the edge table renders transition volumes (TEST-2772
   invocation counts on edges). A second case asserts the error/`onNotify` path on
   a non-ok fetch.
4. Do not change application runtime behavior, other tabs, formal artifacts,
   project membership, release/deployment state, or credentials.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1585` (Traffic Flow render) | `TrafficFlowTab` renders total conversations + agent node invocation counts from a mocked topology fixture. |
| `SPEC-1585` (edge transitions / invocation counts) | Edge table renders transition volumes; non-ok fetch triggers `onNotify` error. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Vitest component test over the live `TrafficFlowTab` (cwd `applications/Agent_Red/admin/provider`). |
| Harness (`scaffold_update`) | `npm install` succeeds; `npm test` runs the new suite green; `npm run typecheck` clean. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation starts only after LO `GO`, work-intent claim, and `implementation_authorization.py begin --bridge-id agent-red-wi3221-observatory-trafficflow-vitest-coverage`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All targets under `applications/Agent_Red/`. |

Required commands after implementation (cwd `applications/Agent_Red/admin/provider`):

```text
npm install
npm test
npm run typecheck
```

## Acceptance Criteria

- PASS when the new Vitest harness installs and `npm test` runs the Traffic Flow
  suite green.
- PASS when `TrafficFlowTab` renders the mocked total-conversations value, an
  agent node invocation count, and the edge-table transition volumes.
- PASS when a non-ok topology fetch invokes the `onNotify` error path.
- PASS when `npm run typecheck` is clean.
- PASS when the `export` addition is the only change to `PipelineObservatory.tsx`
  and no runtime behavior is altered.
- PASS when no application runtime behavior, other tabs, formal artifacts, project
  membership, new work items, credentials, release tags, or deployment state are
  changed.

## Risks / Rollback

Risk is moderate (new harness). The principal risks are Mantine rendering under
happy-dom (mitigated by the `matchMedia`/`ResizeObserver`/`scrollIntoView` shims
in `tests/setup.ts`) and devDependency version drift (mitigated by aligning with
the widget's proven Vitest versions). The `export` addition is behavior-neutral.

Rollback: revert `package.json`/`package-lock.json`, delete `vitest.config.ts`,
`tests/setup.ts`, and the test file, and remove the `export` keyword. Bridge audit
files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/admin/provider/package.json`
- `applications/Agent_Red/admin/provider/package-lock.json`
- `applications/Agent_Red/admin/provider/vitest.config.ts` (new)
- `applications/Agent_Red/admin/provider/tests/setup.ts` (new)
- `applications/Agent_Red/admin/provider/tests/PipelineObservatory.trafficflow.test.tsx` (new)
- `applications/Agent_Red/admin/provider/pages/PipelineObservatory.tsx` (`export` addition)

## Pre-Filing Preflight Evidence

Both mandatory preflights were run against this draft (`--content-file`) before
filing. Loyal Opposition should rerun both against the operative bridge file.

Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs: []`. The `work_items` extraction lists WI-3221 plus the
sibling ids mentioned in prose (WI-3222/3224/3221-3224); the authoritative
`Work Item:` header is WI-3221.

Expected warning `missing parent directories: .../admin/provider/tests/...`: the
`tests/` directory does not exist yet because **creating it is part of the harness
scaffold this proposal authorizes**. The parent `admin/provider/` exists.
Non-blocking (`preflight_passed: true`).

Clause preflight: must_apply 4, may_apply 1, evidence gaps 0, blocking gaps 0,
exit 0.

Phantom-spec sweep: all cited ids (the proven governance battery plus `SPEC-1585`)
confirmed present in the live `specifications` table.

## Recommended Commit Type

`test:` (the change is test-coverage plus its enabling harness; the only source
edit is a behavior-neutral `export`).
