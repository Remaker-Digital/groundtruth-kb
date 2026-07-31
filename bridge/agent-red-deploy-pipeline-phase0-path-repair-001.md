NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f19c2-f6f6-7c81-8c25-00f7e8a75bf9
author_model: GPT-5
author_model_version: GPT-5 Codex desktop
author_model_configuration: default
author_metadata_source: explicit-codex-runtime

# Implementation Proposal - Resolve deploy pipeline Phase 0 environment validation failure

bridge_kind: prime_proposal
Document: agent-red-deploy-pipeline-phase0-path-repair
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-DEPLOY-PIPELINE-AGENT-RED-DEPLOY-PIPELINE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-DEPLOY-PIPELINE
Work Item: WI-3172

target_paths: ["applications/Agent_Red/scripts/deploy_pipeline.py", "applications/Agent_Red/scripts/deploy_config.py", "applications/Agent_Red/scripts/deploy.py", "applications/Agent_Red/tests/unit/test_deploy_pipeline_production.py", "applications/Agent_Red/tests/unit/helpers/run_mocked_pipeline.py"]

implementation_scope: source,test_addition,scaffold_update
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
external_deployment_in_scope: false

## Summary

File a bounded implementation proposal for `WI-3172`, the sole open work item in `PROJECT-AGENT-RED-DEPLOY-PIPELINE`. Current evidence shows the Agent Red production deploy-pipeline tests are failing before they can validate the Phase 0 approval gate because app-local deploy scripts expected under `applications/Agent_Red/scripts/` are missing while tracked deploy scripts remain at root-level `scripts/`.

This proposal asks Loyal Opposition to approve an app-local path repair for the Agent Red deploy pipeline, preserving the no-deployment boundary. It does not authorize a real staging or production deployment, credential lifecycle work, destructive cleanup, or any external-system mutation.

## Claim

Prime Builder proposes a narrow Agent Red deploy-pipeline repair so `WI-3172` can advance from a recorded Phase 0 production approval-gate failure to live mocked/dry-run verification evidence. The implementation will align the deploy pipeline with the Agent Red application root and keep the bridge, project authorization, implementation-start, and spec-derived verification gates intact.

## Requirement Sufficiency

Existing requirements sufficient: yes.

`SPEC-1615` defines the automated build/deploy pipeline and its autonomous scripted behavior. `GOV-16` defines the no-autonomous-deployment approval gate. `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-APPLICATION-ISOLATION-CONTRACT-001`, and `DCL-APP-ROOT-MINIMIZATION-001` define Agent Red application placement and lifecycle isolation. `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` define the bridge proposal filing envelope. `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and the active PAUTH cited above provide bounded project authorization for `WI-3172`, but do not bypass Loyal Opposition review or implementation-start authorization.

## Current Evidence

- `python -m groundtruth_kb.cli backlog list --json --project AGENT-RED-DEPLOY-PIPELINE --all` shows one open member item: `WI-3172`.
- `python -m groundtruth_kb.cli projects authorizations PROJECT-AGENT-RED-DEPLOY-PIPELINE --json` shows the cited PAUTH is active and includes `WI-3172`.
- `python -m groundtruth_kb.cli bridge threads --wi WI-3172` reports zero existing bridge threads for `WI-3172`, so there is no prior `GO` implementation thread to continue.
- `python -m pytest applications/Agent_Red/tests/unit/test_deploy_pipeline_production.py -q --tb=short` collected 30 tests and failed 27, with the common blocker that `applications/Agent_Red/scripts/deploy_pipeline.py` and `applications/Agent_Red/scripts/deploy_config.py` are missing.
- `rg --files | rg "(^|/)scripts/(deploy|deploy_pipeline|deploy_config)\.py$|deploy_pipeline\.py$|deploy_config\.py$|deploy\.py$"` finds deploy scripts at root-level `scripts/deploy_pipeline.py`, `scripts/deploy_config.py`, and `scripts/deploy.py`, not under the Agent Red app root.
- `applications/Agent_Red/.gtkb-app-isolation.json` lists top-level `scripts` as bucket `A` with purpose `Agent Red application-local operational and development scripts.`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - authorizes Prime Builder to write `NEW` proposal status while preserving role-correct bridge authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires implementation proposals to carry concrete linked specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target-path metadata in bridge proposals.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - allows active project authorization to be cited while preserving bridge review, implementation-start, verification, and deployment gates.
- `SPEC-1615` - owns the scripted build/deploy pipeline behavior, dry-run/mocked execution expectations, diagnostics, and Phase 0 environment validation context.
- `GOV-16` - forbids autonomous staging or production deployments and requires explicit owner approval immediately before any real deployment.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires GT-KB adopter applications to live under `applications/<name>/`.
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - requires Agent Red lifecycle surfaces to be scoped to `applications/Agent_Red/` when they govern the Agent Red application.
- `DCL-APP-ROOT-MINIMIZATION-001` - constrains Agent Red app-root artifacts and registry justification for app-local scripts.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires linked-spec-derived tests and execution evidence before any VERIFIED verdict.

## Prior Deliberations

- `DELIB-20265586` - owner decision backing the active project authorization for `PROJECT-AGENT-RED-DEPLOY-PIPELINE` and `WI-3172`.
- `DELIB-20265219`, `DELIB-20265220`, and `DELIB-20265227` - owner decisions establishing the Agent Red Readiness Program, Phase 1 scoping, and the Agent Red application-isolation governance foundation.
- `bridge/gtkb-ar-readiness-phase-1-1-governance-foundation-003.md` and `bridge/gtkb-ar-readiness-phase-1-1-governance-foundation-004.md` - approved and verified Agent Red application-isolation governance foundation for the cited ADR/DCL.
- `bridge/por-step16c-stream-c-beta-triage-002.md`, `bridge/por-step16c-stream-c-beta-triage-003.md`, and `bridge/por-step16c-stream-c-beta-triage-004.md` - prior deploy-pipeline beta triage and verification context, including SPEC-1615 / TEST-2941 linkage and deploy pipeline evidence before the current app-root path mismatch.

## Owner Decisions / Input

- `PAUTH-PROJECT-AGENT-RED-DEPLOY-PIPELINE-AGENT-RED-DEPLOY-PIPELINE-BOUNDED-IMPLEMENTATION-2026-06-23` - active bounded project authorization covering `WI-3172`.
- No new owner input is required to file this proposal. A separate immediate owner approval remains required before any real staging or production deployment, per `GOV-16`; that approval is explicitly out of scope for this proposal.

## Proposed Scope

- Restore or adapt the Agent Red deploy pipeline as application-local scripts under `applications/Agent_Red/scripts/`, using the existing root-level deploy scripts as source-reference material only unless the approved implementation proves a root compatibility edit is necessary.
- Preserve the Phase 0 production approval gate: production execution without `DEPLOY_APPROVED=1` or `--approved` must fail before any deployment action; approved mocked/dry-run paths may proceed.
- Keep the implementation bounded to local source/test repair and mocked/dry-run validation. Do not run `az acr build`, `az containerapp update`, live deploy commands, credential updates, or external-system mutations.
- Update app-local tests/helpers only when needed to reflect the canonical app-local script location or to add spec-derived assertions for the repaired behavior.
- If implementation discovers root-level deploy scripts still serve a platform-owned compatibility role, preserve them and document any follow-up cleanup as separate bridge/backlog work instead of broadening this slice.

## Out Of Scope

- Real staging or production deployment.
- Rotating, creating, requesting, or modifying credentials.
- Retiring root-level deploy scripts unless explicitly approved in a later proposal.
- Modifying GT-KB platform bridge, dispatcher, MemBase schema, or release governance.
- Closing `WI-3172` without implementation-report and Loyal Opposition verification evidence.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify this filed artifact is a Prime Builder `NEW` proposal and no Loyal Opposition status was authored by Prime Builder. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Verify this proposal carries concrete Specification Links and target paths before any implementation-start action. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run bridge applicability preflight against the filed thread and confirm Project Authorization, Project, Work Item, and inline-JSON target_paths are present. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Include this proposal, implementation-start packet, and active PAUTH in the implementation report; verify no out-of-project or external-deployment work occurred. |
| `SPEC-1615` | Run `python -m pytest applications/Agent_Red/tests/unit/test_deploy_pipeline_production.py -q --tb=short`; if scaling coverage is touched, also run `python -m pytest applications/Agent_Red/tests/unit/test_deploy_pipeline_scaling.py applications/Agent_Red/tests/unit/test_deploy_scaling.py -q --tb=short`. Evidence must show mocked/dry-run success and Phase 0 diagnostics execute without interactive owner/agent intervention. |
| `GOV-16` | Verify production without approval remains blocked before any deploy action and production with explicit mocked/dry-run approval can proceed only in tests. Do not execute any real deployment command. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify Agent Red deploy-pipeline files remain under `applications/Agent_Red/`. |
| `ADR-APPLICATION-ISOLATION-CONTRACT-001` | Verify Agent Red deploy-pipeline runtime/test surfaces resolve under `applications/Agent_Red/` and do not silently depend on GT-KB platform lifecycle paths for application execution. |
| `DCL-APP-ROOT-MINIMIZATION-001` | Verify `applications/Agent_Red/.gtkb-app-isolation.json` already accounts for the `scripts` top-level artifact and no new unregistered app-root top-level artifact is introduced. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must cite the linked specs and executed tests; Loyal Opposition must withhold VERIFIED if any linked spec lacks derived passing evidence. |

## Acceptance Criteria

- `applications/Agent_Red/tests/unit/test_deploy_pipeline_production.py` no longer fails because app-local deploy scripts or deploy config are missing.
- Production without immediate approval remains blocked before any deploy action.
- Mocked/dry-run approved production path reaches the expected success behavior without requiring owner or agent interaction during execution.
- The implementation report includes command evidence, linked-spec coverage, and a clear statement that no real deployment or external-system mutation was performed.
- `WI-3172` is ready for Loyal Opposition verification after the implementation report, with any remaining non-blocking cleanup routed to follow-up work instead of hidden in this slice.

## Risks / Rollback

Risk is moderate because deploy-pipeline code is operationally sensitive even when only tests and dry-run paths are exercised. The main risks are duplicating root-level scripts without clarifying lifecycle ownership, accidentally weakening the GOV-16 approval gate, or expanding from local repair into deployment behavior.

Rollback is a revert of app-local script/test changes from this slice. Bridge files, project authorization records, and implementation reports are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `applications/Agent_Red/scripts/deploy_pipeline.py`
- `applications/Agent_Red/scripts/deploy_config.py`
- `applications/Agent_Red/scripts/deploy.py`
- `applications/Agent_Red/tests/unit/test_deploy_pipeline_production.py`
- `applications/Agent_Red/tests/unit/helpers/run_mocked_pipeline.py`

## Recommended Commit Type

`fix`
