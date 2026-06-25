NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 4e30eeba-5f51-4cad-89fd-793ac8f59e98
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: Claude Code interactive; role=prime-builder; output_style=explanatory
author_metadata_source: interactive Claude runtime envelope plus hand-authored bridge proposal

# Implementation Proposal - WI-3224 Deployment Modal Version Pre-fill Vitest Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3224-deployment-modal-version-prefill-coverage
Version: 001 (NEW)
Date: 2026-06-25 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3224

target_paths: ["applications/Agent_Red/admin/provider/pages/DeploymentManagement.tsx", "applications/Agent_Red/admin/provider/tests/DeploymentManagement.versionprefill.test.tsx"]

## Claim

WI-3224 should add deterministic Vitest coverage for `SPEC-1841` "Deployment modal
SHOULD pre-fill recommended next version and show last deployed version", the
fourth and final member of the Observatory frontend cluster, building on the Vitest
harness established by WI-3221 (commit `cbf5e7f28`).

`SPEC-1841` is `implemented` in
`applications/Agent_Red/admin/provider/pages/DeploymentManagement.tsx`, with **no
mapped tests** (true phantom). Its two clauses are realized as:

1. **Recommended next version** — the pure module-internal `suggestNextVersion(version)`
   (line 98) parses a semver string and returns the next patch
   (`v1.98.15` → `v1.98.16`, `v1.98` → `v1.98.0`); `suggestedVersion` is derived from
   the last succeeded deployment's version and pre-filled into the trigger modal.
2. **Show last deployed version** — the "Trigger Pipeline" button pre-fills the modal's
   Version input with `suggestedVersion` and the modal description shows
   `Last successful deployment: ${lastVersion}`.

This is a bounded `test_addition` + `source` item: it exports `suggestNextVersion`
(behavior-neutral) and adds one Vitest test covering both clauses. The
`DeploymentManagementPage` component is already exported. No harness scaffold; no
production behavior changes.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-1841` and the live `DeploymentManagement.tsx`
implementation give a complete contract for deterministic coverage of the
version-suggestion computation and the modal pre-fill/last-deployed display. No
owner clarification is required.

## Owner Decisions / Input

Governed by (1) project authorization
`PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`
(owner decision `DELIB-20265586`; allowed classes include `test_addition` + `source`;
snapshot includes `WI-3224`), and (2) the 2026-06-25 in-session AskUserQuestion
decision selecting Vitest component tests for the frontend cluster. No new owner
decision is required.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB\applications\Agent_Red\` per
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`:

- `applications/Agent_Red/admin/provider/pages/DeploymentManagement.tsx` (`export` addition)
- `applications/Agent_Red/admin/provider/tests/DeploymentManagement.versionprefill.test.tsx` (new)

## Specification Links

- `SPEC-1841` - Direct requirement: deployment modal pre-fills recommended next version + shows last deployed version.
- `GOV-10` - Tests exercise the live `suggestNextVersion` + `DeploymentManagementPage` interfaces.
- `SPEC-1649` - Master test plan / live-interface policy.
- `GOV-12` - Work-item remediation creates test evidence.
- `GOV-13` - Test visibility / phase governance.
- `GOV-08` - KB-tracked coverage gap.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped authorization does not replace bridge review, GO, target paths, implementation-start packet, report, or verification.
- `SPEC-AUQ-POLICY-ENGINE-001` - Frontend test model set by the in-session AskUserQuestion decision.
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
- `DELIB-0712` / `DELIB-0713` - phantom-only remediation; executable evidence required.
- `bridge/agent-red-wi3221-observatory-trafficflow-vitest-coverage-002.md` - sibling GO establishing the Vitest harness this proposal reuses.
- In-session AskUserQuestion (2026-06-25): Vitest model for the frontend cluster (to be archived as a deliberation at session wrap).
- `gt bridge threads --wi WI-3224 --json` returned `match_count: 0` before this proposal.

## Current-State Evidence

- `gt spec show SPEC-1841` shows status `implemented`; `gt tests list --spec-id SPEC-1841` returns no tests (true phantom).
- `suggestNextVersion` (DeploymentManagement.tsx:98) is a pure module-internal function; `DeploymentManagementPage` (line 112) is already exported.
- The trigger button (line 240) pre-fills `setTriggerVersion(suggestedVersion)`; the modal (line 314) shows `Last successful deployment: ${lastVersion}` and uses `suggestedVersion` as placeholder/value.
- The Vitest harness exists and is committed in `cbf5e7f28` from WI-3221.

## Proposed Scope

1. Export `suggestNextVersion` from `DeploymentManagement.tsx` (behavior-neutral).
2. Add `tests/DeploymentManagement.versionprefill.test.tsx`:
   - **Pure function (recommended next version):** assert `suggestNextVersion('v1.98.15') === 'v1.98.16'`, `'1.98.15' → '1.98.16'`, `'v1.98' → 'v1.98.0'`, and invalid input → `''`.
   - **Modal pre-fill + last-deployed display:** mock `useProviderContext` so `apiFetch('/api/superadmin/deployments')` returns a fixture with a succeeded deployment at a known version, render `<DeploymentManagementPage />` in `MantineProvider`, await load, click "Trigger Pipeline", and assert the Version input is pre-filled with the suggested next version AND the modal shows `Last successful deployment: <version>`.
3. No production behavior changes beyond the `export`.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1841` (recommended next version) | `suggestNextVersion` returns the next patch for `vMAJOR.MINOR.PATCH`, `MAJOR.MINOR.PATCH`, `vMAJOR.MINOR`, and `''` for invalid input. |
| `SPEC-1841` (modal pre-fill + last deployed) | Opening the trigger modal pre-fills the Version input with the suggested next version and shows the last successful deployment version. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Vitest suite over the live `suggestNextVersion` + `DeploymentManagementPage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | `npm test` + `npm run typecheck` (cwd `applications/Agent_Red/admin/provider`). |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation starts only after LO `GO`, claim, and `implementation_authorization.py begin --bridge-id agent-red-wi3224-deployment-modal-version-prefill-coverage`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Targets under `applications/Agent_Red/admin/provider/`. |

Required commands after implementation (cwd `applications/Agent_Red/admin/provider`):

```text
npm test
npm run typecheck
```

## Acceptance Criteria

- PASS when `npm test` runs the deployment-modal suite green and `npm run typecheck` is clean.
- PASS when `suggestNextVersion` returns the correct next patch for all documented formats and `''` for invalid input.
- PASS when opening the trigger modal pre-fills the suggested next version and shows the last deployed version.
- PASS when the `export` is the only change to `DeploymentManagement.tsx` and no runtime behavior is altered.
- PASS when no other components, formal artifacts, project membership, credentials, or release/deployment state are changed.

## Risks / Rollback

Risk is low — additive test coverage + a behavior-neutral `export`, on an existing harness. The modal-interaction assertion uses `@testing-library/user-event` already installed by the WI-3221 harness. Rollback: delete the test file and remove the `export`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/admin/provider/pages/DeploymentManagement.tsx` (`export` addition)
- `applications/Agent_Red/admin/provider/tests/DeploymentManagement.versionprefill.test.tsx` (new)

## Pre-Filing Preflight Evidence

To be populated from the two mandatory preflights against this draft before the helper write; Loyal Opposition should rerun both against the operative bridge file.

## Recommended Commit Type

`test:`
