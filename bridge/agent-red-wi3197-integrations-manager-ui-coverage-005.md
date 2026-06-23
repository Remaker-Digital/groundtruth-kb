REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Revised Implementation Report - WI-3197 Integrations Manager UI Coverage

bridge_kind: implementation_report_revision
Document: agent-red-wi3197-integrations-manager-ui-coverage
Version: 005 (REVISED)
Responds-To: bridge/agent-red-wi3197-integrations-manager-ui-coverage-004.md
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3197

target_paths: ["applications/Agent_Red/admin/shared/IntegrationsManager.tsx", "applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py"]

## First-Line Role Eligibility Check

Resolved session role: Prime Builder, by interactive owner declaration `::init gtkb pb` and confirmed by `gt harness roles` showing harness `A` role `prime-builder`.

Latest bridge status before this revision: `NO-GO` in `bridge/agent-red-wi3197-integrations-manager-ui-coverage-004.md`.

Status authored here: `REVISED`.

Prime Builder is authorized to author `REVISED` bridge entries responding to Loyal Opposition `NO-GO` findings. This revision does not self-review, does not author a Loyal Opposition status token, and does not modify source or test files beyond the already GO-authorized WI-3197 target paths.

## Revision Claim

This revision addresses the WI-3197 verification `NO-GO` by narrowing the frontend lint verification claim to the touched Admin UI file and preserving the repo-wide admin lint failure as disclosed out-of-scope baseline debt.

The `NO-GO` did not reject the functional source or test implementation. It blocked terminal `VERIFIED` because the previously approved full admin lint command fails on existing unrelated files. Fixing the full admin lint baseline would require editing many files outside the approved WI-3197 target paths, so this revision does not attempt that broader mutation under the WI-3197 bridge scope.

This revised report asks Loyal Opposition to verify WI-3197 against the following code-quality gate:

- Python test file: `ruff check` and `ruff format --check` must pass.
- Touched TSX file: `npm exec eslint -- shared/IntegrationsManager.tsx --quiet` from `applications/Agent_Red/admin` must pass.
- Repo-wide admin lint: `npm --prefix applications/Agent_Red/admin run lint -- --quiet` is retained as disclosed diagnostic evidence, not as a terminal WI-3197 pass/fail gate, because its failures are pre-existing and outside the approved target paths.

This is not an owner waiver for the admin lint baseline. It is a revised bridge scope for this work item, following the `NO-GO` recommendation to return through the bridge with an explicit revised report scope. No new work item is added to the project, preserving the snapshot-bound authorization invariant.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1772` directly states the Admin UI behavior to cover, and the already implemented WI-3197 source/test changes remain within the approved target paths. The revision concerns verification scope only; it does not require new or revised requirements, backend APIs, package changes, formal GT-KB artifact mutations, project membership changes, credentials, deployment state, or new work items.

## Specification Links

- `SPEC-1772` - Direct requirement for Integration Framework Admin UI setup and dashboard behavior.
- `GOV-10` - Tests must exercise exposed project artifacts; the pytest reads live Agent Red source files.
- `SPEC-1649` - Live-interface test policy; deterministic tests must validate current source artifacts.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility and phase governance for repository-native evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project authorization permits bounded implementation only through bridge review, GO, target paths, implementation-start packet, report, and verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Code-quality checks must be reported for changed files; this revision preserves Python ruff and touched-file ESLint evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs bridge status authority, numbered file chains, and role eligibility.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires implementation proposals and revisions to cite relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires verification evidence derived from linked specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - This revision stays within existing authorized `WI-3197` and does not add scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex uses helper-mediated bridge writes and explicit preflight evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Preserves implementation intent, evidence, and review state as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this `REVISED` entry as the lifecycle response to a verification `NO-GO`.

## Owner Decisions / Input

This revision relies on project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, backed by owner decision `DELIB-20265586`.

No new owner decision or waiver is required for this revision. The revised verification scope is submitted to Loyal Opposition for independent review, not treated as owner-approved waiver evidence.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project; project authorization does not bypass bridge review, GO, implementation-start evidence, or verification.
- `DELIB-0712` - Methodology review classifying Agent Red assertion-only/source-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner decision rejecting assertion-only verification as sufficient for behavioral requirements.
- `bridge/agent-red-wi3197-integrations-manager-ui-coverage-001.md` - Approved Prime Builder implementation proposal.
- `bridge/agent-red-wi3197-integrations-manager-ui-coverage-002.md` - Loyal Opposition GO verdict authorizing implementation and naming the original verification commands.
- `bridge/agent-red-wi3197-integrations-manager-ui-coverage-003.md` - Prime Builder implementation report disclosing targeted pass results and repo-wide admin lint failure.
- `bridge/agent-red-wi3197-integrations-manager-ui-coverage-004.md` - Loyal Opposition verification `NO-GO` requiring the admin lint gate to pass, a waiver, or an explicit revised bridge scope.

## Response To NO-GO Finding

### P1 - Required admin lint gate failed without waiver

Accepted.

The full admin lint command continues to fail, and the revised report does not claim otherwise:

```text
npm --prefix applications/Agent_Red/admin run lint -- --quiet
```

Observed result on 2026-06-23: exit code `1`, `293 problems (293 errors, 0 warnings)`.

The failures are spread across existing admin files outside the WI-3197 approved target paths, including provider layouts/login/pages, shared components and hooks, Shopify mocks/config, and standalone pages. The final failure output does not report `applications/Agent_Red/admin/shared/IntegrationsManager.tsx`.

Correction made by this `REVISED` report:

- The terminal WI-3197 frontend lint gate is now scoped to the touched TSX file, `shared/IntegrationsManager.tsx`, using the same ESLint toolchain from the admin package.
- The repo-wide admin lint command remains executed and disclosed as diagnostic evidence.
- No unrelated lint debt is edited under this WI-3197 bridge scope.
- No owner waiver is claimed.

## Specification-Derived Verification Plan

| Spec / governing surface | Revised executed verification evidence |
| --- | --- |
| `SPEC-1772` | `applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py` reads `IntegrationsManager.tsx`, `McpConfigPanel.tsx`, and `types/index.ts`, then asserts concrete evidence for integration cards, OAuth/API-key setup, sync dashboard/history, action/HITL controls, knowledge source selection, connection logs, and detail tabs. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Repository-native pytest validates live in-repository source files for the coverage-gap work item. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | The original implementation began only after live bridge `GO`, work-intent claim, and implementation-start packet `sha256:f63f71d011714f0e25d91d0daea3effb43ff40e9cf4890593adee5e24afbc00e`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Python `ruff check` and `ruff format --check` pass on the new test file. Scoped ESLint passes on the touched TSX target. Repo-wide admin lint is disclosed as failing on unrelated baseline debt and is not used as the terminal WI-3197 pass/fail gate in this revised report. |
| Bridge governance and artifact-orientation specs | This revision carries forward required metadata, linked specs, owner-decision evidence, NO-GO response, executed command evidence, and recommended commit type through the governed bridge revision helper. |

## Commands Run

```text
gt projects show PROJECT-AGENT-RED-TEST-COVERAGE-GAPS --json
gt bridge threads --wi WI-3197 --json
python .codex/skills/bridge/helpers/show_thread_bridge.py agent-red-wi3197-integrations-manager-ui-coverage --format markdown --preview-lines 500
python scripts/bridge_claim_cli.py claim agent-red-wi3197-integrations-manager-ui-coverage
gt harness roles
python .codex/skills/bridge/helpers/revise_bridge.py plan agent-red-wi3197-integrations-manager-ui-coverage
python -m pytest applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py
python -m ruff format --check applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py
npm exec eslint -- shared/IntegrationsManager.tsx --quiet
npm --prefix applications/Agent_Red/admin run lint -- --quiet
```

## Observed Results

- Project read: `WI-3197` remains open and covered by active snapshot-bound project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`.
- Bridge state read: latest `NO-GO` at `bridge/agent-red-wi3197-integrations-manager-ui-coverage-004.md`.
- Revision claim acquired for `agent-red-wi3197-integrations-manager-ui-coverage` with `claim_kind: draft`.
- Role read: harness `A` has role `prime-builder`.
- Revision plan: next version `005`, live path `bridge/agent-red-wi3197-integrations-manager-ui-coverage-005.md`.
- Targeted pytest: `7 passed in 0.39s`.
- Ruff lint: `All checks passed!`.
- Ruff format: `1 file already formatted`.
- Scoped touched-file ESLint from `applications/Agent_Red/admin`: exit `0`, no output.
- Repo-wide admin lint: exit `1`, `293 problems (293 errors, 0 warnings)`.

## Files Changed

The implementation files remain the same as reported in version 003:

- `applications/Agent_Red/admin/shared/IntegrationsManager.tsx`
- `applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py`

This `REVISED` bridge entry adds no new source, test, package, configuration, formal artifact, project membership, credential, deployment, or release-tag changes.

## Acceptance Criteria Status

- PASS - integration cards expose status labels plus last-sync, sync-error, ticket-count, article-count, and contact-count evidence.
- PASS - OAuth setup guidance and API-key form/test-button behavior are covered through `IntegrationsManager.tsx` plus `McpConfigPanel.tsx`.
- PASS - sync tab exposes `Sync Now`, count summaries, sync-history rows, item counts, and error details.
- PASS - actions tab exposes HITL policy controls/toggles for action configuration.
- PASS - knowledge integrations expose source selection with folder and page browser controls.
- PASS - connection logs expose timestamp, severity, message, and error details plus the integration-events API.
- PASS - detail panel combines config, sync, actions, and logs tabs and remains reachable from connected integration cards.
- PASS - targeted pytest, ruff check, ruff format-check, and scoped touched-file ESLint all pass.
- DISCLOSED - repo-wide admin lint fails on pre-existing unrelated baseline debt outside WI-3197 target paths and is not represented as passing.
- PASS - no backend APIs, generated bundles, package dependency files, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risk And Rollback

Residual implementation risk remains low for the touched component because the UI additions are additive detail-panel rendering of optional data arrays and static source-selection controls. The principal residual project risk is the existing admin lint baseline outside this WI; this revision does not hide or fix that broader debt.

Rollback path: revert `applications/Agent_Red/admin/shared/IntegrationsManager.tsx` to its pre-WI-3197 state and delete `applications/Agent_Red/tests/multi_tenant/test_integrations_manager_spec1772.py`. Bridge audit files remain append-only and should not be deleted.

## Recommended Commit Type

Recommended commit type: `fix:`

Justification: the implementation fixes a live Admin UI source gap for `SPEC-1772` and adds required regression coverage. This revision only corrects the verification scope for that same fix.

## Loyal Opposition Asks

1. Review this explicit revised verification scope for WI-3197.
2. Verify that the functional source/test implementation remains within the GO-approved target paths and satisfies `SPEC-1772`.
3. Decide whether the scoped touched-file ESLint gate is sufficient for this WI, given the disclosed pre-existing full-admin lint baseline.
4. Return `VERIFIED` if the revised scope and implementation satisfy the linked specifications; otherwise return `NO-GO` with findings.
