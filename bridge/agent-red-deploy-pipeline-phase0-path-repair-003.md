NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f19c2-f6f6-7c81-8c25-00f7e8a75bf9
author_model: GPT-5
author_model_version: GPT-5 Codex desktop
author_model_configuration: default
author_metadata_source: explicit-codex-runtime

# GT-KB Bridge Implementation Report - agent-red-deploy-pipeline-phase0-path-repair - 003

bridge_kind: implementation_report
Document: agent-red-deploy-pipeline-phase0-path-repair
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/agent-red-deploy-pipeline-phase0-path-repair-002.md
Approved proposal: bridge/agent-red-deploy-pipeline-phase0-path-repair-001.md
Recommended commit type: fix

## Implementation Claim

Prime Builder implemented the GO-approved Agent Red deploy-pipeline path repair for `WI-3172`.

The implementation restores the deploy pipeline as app-local scripts under `applications/Agent_Red/scripts/`, updates the app-local deploy pipeline to run from the Agent Red application root, preserves the GOV-16 production approval gate before external checks, and keeps dry-run/mocked verification paths free of Azure, ACR, Docker, and live HTTP side effects.

No real staging or production deployment was performed. No credential lifecycle work was performed. No root-level deploy scripts were modified.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority and numbered file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete implementation proposal/report spec links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target path metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - bounded project implementation authorization.
- `SPEC-1615` - scripted deploy pipeline behavior, dry-run/mocked execution, diagnostics, and Phase 0 validation context.
- `GOV-16` - no autonomous staging or production deployments without immediate owner approval.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - adopter applications live under `applications/<name>/`.
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - Agent Red lifecycle surfaces are scoped to `applications/Agent_Red/`.
- `DCL-APP-ROOT-MINIMIZATION-001` - app-root artifacts are registry-accounted and minimized.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED requires linked-spec-derived passing evidence.

## Owner Decisions / Input

No new owner decision was required by this implementation report.

Carried-forward owner/project evidence:

- `PAUTH-PROJECT-AGENT-RED-DEPLOY-PIPELINE-AGENT-RED-DEPLOY-PIPELINE-BOUNDED-IMPLEMENTATION-2026-06-23` - active project authorization covering `WI-3172`.
- `DELIB-20265586` - owner decision backing the active project authorization.

## Prior Deliberations

- `bridge/agent-red-deploy-pipeline-phase0-path-repair-001.md` - approved implementation proposal carried forward.
- `bridge/agent-red-deploy-pipeline-phase0-path-repair-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `DELIB-20265219`, `DELIB-20265220`, and `DELIB-20265227` - Agent Red Readiness Program and app-isolation governance foundation.

## Implementation Details

- Added `applications/Agent_Red/scripts/deploy_pipeline.py` from the existing deploy-pipeline implementation, then patched the app-local copy for app-root imports, app-local scaling compatibility, dry-run external-check skipping, missing CLI fail-soft behavior, and app-local defect-reporter fail-soft behavior.
- Added `applications/Agent_Red/scripts/deploy_config.py` from the existing deploy config, then patched the app-local copy with an app-local env loader instead of the root-only `scripts._env` dependency.
- Added `applications/Agent_Red/scripts/deploy.py` from the existing smoke deploy implementation, then patched the app-local copy to carry the scaling taxonomy/enforcement helpers locally instead of importing root-only `scripts/lib`.
- Updated `applications/Agent_Red/tests/unit/test_deploy_pipeline_production.py` so the upgrade verification source check uses app-root first, then the existing root fallback pattern already used by the scaling tests.
- Updated `applications/Agent_Red/tests/unit/helpers/run_mocked_pipeline.py` so fully mocked subprocess paths also mock `phase_15_enforce_scaling`, preventing unintended real scaling commands during mocked success/failure CLI tests.

## GO Conditions Status

- Condition 1, no real deployment: satisfied. No `az acr build`, `az containerapp update`, live deploy command, credential update, or external-system mutation was run.
- Condition 2, root-level deploy script disposition: satisfied. `scripts/deploy_pipeline.py`, `scripts/deploy_config.py`, and `scripts/deploy.py` were retained unchanged as pre-existing root-hosted compatibility/reference copies. The Agent Red app-local copies now satisfy the app-root test/runtime surface for this slice. Full retirement or wrapper conversion for the root copies is outside this GO target set and should be handled by a separate bridge item if desired.
- Condition 3, spec-derived test evidence: satisfied by the final commands below.
- Condition 4, advisory-spec gaps: assessed. The advisory artifact-oriented governance specs did not require additional artifact mutation for this narrow source/test implementation; the implementation report records the residual follow-up consideration explicitly.
- Condition 5, parent directory warning: satisfied. `applications/Agent_Red/scripts/`, `applications/Agent_Red/tests/unit/`, and `applications/Agent_Red/tests/unit/helpers/` exist. The earlier preflight warning trimmed the `applications/Agent_Red/` prefix in its display, but the actual parent directories are present.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report is the Prime Builder `NEW` post-implementation report after latest `GO`; Prime Builder did not author `GO`, `NO-GO`, or `VERIFIED`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward all linked governing specs from the approved proposal and maps each to executed evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | The approved proposal and implementation-start packet carried Project Authorization, Project, Work Item, and inline JSON target paths for `WI-3172`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation was bounded to the active PAUTH for `PROJECT-AGENT-RED-DEPLOY-PIPELINE`; no out-of-project or external-deployment work occurred. |
| `SPEC-1615` | `python -m pytest applications/Agent_Red/tests/unit/test_deploy_pipeline_production.py applications/Agent_Red/tests/unit/test_deploy_scaling.py applications/Agent_Red/tests/unit/test_deploy_pipeline_scaling.py -q --tb=short` passed 47 tests, covering deploy-pipeline dry-run/mocked execution, success/failure paths, rollback fields, and scaling parity. |
| `GOV-16` | Production without approval remains blocked before external checks; approved dry-run paths confirm `Owner approval: CONFIRMED (GOV-16)` without live deployment. Covered by the 47-test command. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | New deploy runtime surfaces are under `applications/Agent_Red/scripts/`; tests resolve app-local paths first. |
| `ADR-APPLICATION-ISOLATION-CONTRACT-001` | Agent Red deploy-pipeline runtime/test surfaces now resolve under `applications/Agent_Red/` for this slice. Root-level deploy scripts were not mutated and are documented as retained compatibility/reference copies pending any separate retirement decision. |
| `DCL-APP-ROOT-MINIMIZATION-001` | No new Agent Red top-level artifact was introduced. The existing `scripts` top-level artifact is already registered in `applications/Agent_Red/.gtkb-app-isolation.json` as bucket `A`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Final executed tests and Ruff checks are recorded below; Loyal Opposition should withhold VERIFIED only if additional linked-spec evidence is required. |

## Commands Run

- `python -m pytest applications/Agent_Red/tests/unit/test_deploy_pipeline_production.py applications/Agent_Red/tests/unit/test_deploy_scaling.py applications/Agent_Red/tests/unit/test_deploy_pipeline_scaling.py -q --tb=short`
- `python -m ruff check applications/Agent_Red/scripts/deploy_pipeline.py applications/Agent_Red/scripts/deploy_config.py applications/Agent_Red/scripts/deploy.py applications/Agent_Red/tests/unit/test_deploy_pipeline_production.py applications/Agent_Red/tests/unit/helpers/run_mocked_pipeline.py`
- `python -m ruff format --check applications/Agent_Red/scripts/deploy_pipeline.py applications/Agent_Red/scripts/deploy_config.py applications/Agent_Red/scripts/deploy.py applications/Agent_Red/tests/unit/test_deploy_pipeline_production.py applications/Agent_Red/tests/unit/helpers/run_mocked_pipeline.py`

## Observed Results

- Pytest: `47 passed in 5.48s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `5 files already formatted`.

## Files Changed

- `applications/Agent_Red/scripts/deploy_pipeline.py`
- `applications/Agent_Red/scripts/deploy_config.py`
- `applications/Agent_Red/scripts/deploy.py`
- `applications/Agent_Red/tests/unit/test_deploy_pipeline_production.py`
- `applications/Agent_Red/tests/unit/helpers/run_mocked_pipeline.py`
- `bridge/agent-red-deploy-pipeline-phase0-path-repair-001.md`
- `bridge/agent-red-deploy-pipeline-phase0-path-repair-002.md`

## Recommended Commit Type

- Recommended commit type: `fix`
- Diff-stat justification: fixes an Agent Red deploy-pipeline path failure and adds app-local deploy runtime files required by existing tests.

## Acceptance Criteria Status

- [x] `applications/Agent_Red/tests/unit/test_deploy_pipeline_production.py` no longer fails because app-local deploy scripts or deploy config are missing.
- [x] Production without immediate approval remains blocked before any deploy action.
- [x] Mocked/dry-run approved production path reaches expected success behavior without requiring owner or agent interaction during execution.
- [x] Implementation evidence states that no real deployment or external-system mutation was performed.
- [x] `WI-3172` is ready for Loyal Opposition verification after this report.

## Risk And Rollback

Residual risk: `upgrade_verification.py` and root support helpers were not moved into the Agent Red app root in this slice because they were outside the approved target paths. The production deploy-pipeline source check now uses an app-root-first, root-fallback lookup for that source, and the app-local pipeline has an import fallback so tests and dry-run paths do not crash. A future bridge item should decide whether to migrate, wrap, or formally retain root-level deploy support helpers.

Rollback: remove the three app-local deploy script files and revert the two touched production test/helper files. Bridge proposal, GO, and report files remain append-only audit artifacts.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and the final command evidence above.
2. Return `VERIFIED` if the report and implementation satisfy the approved proposal, otherwise return `NO-GO` with findings.
