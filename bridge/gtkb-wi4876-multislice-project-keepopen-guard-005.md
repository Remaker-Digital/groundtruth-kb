REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T07-45-40Z-prime-builder-A-97ab62
author_model: GPT-5.5
author_model_version: gpt-5.5
author_model_configuration: auto-dispatched Prime Builder revision; workspace-write sandbox; approval_policy=never; model_reasoning_effort=xhigh
author_metadata_source: dispatcher-session-envelope

# Revised Implementation Proposal - Multi-slice project keep-open guard

bridge_kind: prime_proposal
Document: gtkb-wi4876-multislice-project-keepopen-guard
Version: 005
Date: 2026-07-06 UTC

Responds to NO-GO: bridge/gtkb-wi4876-multislice-project-keepopen-guard-004.md
Supersedes target scope from: bridge/gtkb-wi4876-multislice-project-keepopen-guard-001.md

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4876

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/project_verified_completion_scanner.py", "groundtruth-kb/tests/test_project_artifacts.py", "platform_tests/scripts/test_project_authorization.py", "platform_tests/scripts/test_projects_cli.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", "platform_tests/hooks/test_project_completion_surface.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

## Summary

This revision corrects the target-path blocker confirmed in version 004. The prior approved proposal named `groundtruth-kb/src/groundtruth_kb/cli_projects.py`, but that file does not exist in the current checkout. The live implementation surface is the project lifecycle service, the existing `gt projects` CLI group in `cli.py`, and the read-only project completion scanner that surfaces authorization-readiness state.

The implementation remains the same behavioral fix: multi-slice project authorizations need an explicit plan-incomplete keep-open election so interim slice completion can complete its authorization without retiring the parent project before remaining slices are planned or executed.

## Requirement Sufficiency

Existing requirements sufficient. WI-4876 records the multi-slice auto-retirement trap, `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` defines the automatic retirement rule and keep-open/guard constraints, and the active Harness Parity Phase 2 PAUTH includes WI-4876.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`. The revision removes the nonexistent `groundtruth-kb/src/groundtruth_kb/cli_projects.py` target and does not introduce any out-of-root dependency.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation and target-path scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass bridge GO, work-intent, or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow and numbered-file audit state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - constrains all active GT-KB artifacts and implementation paths to the project root.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification linkage before implementation GO.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived implementation evidence before VERIFIED.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - governs project authorization completion, project retirement, plan-incomplete guards, and keep-open elections.
- `GOV-STANDING-BACKLOG-001` - requires project/backlog state to remain the durable authority for unfinished slices.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - advisory context for preserving this blocker as a durable bridge revision.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory context for blocked/revised lifecycle handling.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - advisory context for preserving project-relevant decisions, blockers, and work-item evidence.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner authorized Harness Parity Phase 2 implementation and the PAUTH covering WI-4876.
- `bridge/gtkb-wi4876-multislice-project-keepopen-guard-001.md` - initial implementation proposal.
- `bridge/gtkb-wi4876-multislice-project-keepopen-guard-002.md` - Loyal Opposition GO with detailed keep-open guard design.
- `bridge/gtkb-wi4876-multislice-project-keepopen-guard-003.md` - Prime Builder blocker report showing the target-path mismatch.
- `bridge/gtkb-wi4876-multislice-project-keepopen-guard-004.md` - Loyal Opposition NO-GO returning the thread for revised scope.

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active owner-authorized project implementation record covering WI-4876.
- No new owner decision is required for this revision. The change is a mechanical scope correction after NO-GO, not a new policy choice.

## Findings Addressed

### Target-path mismatch from version 004

Response: corrected. This revision adds the live implementation files `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` and `groundtruth-kb/src/groundtruth_kb/cli.py`, removes the nonexistent `groundtruth-kb/src/groundtruth_kb/cli_projects.py`, and adds the scanner/test files required to keep service, CLI, hook, and read-only readiness surfaces aligned.

### Implementation report could not claim source-level testing

Response: corrected by returning the thread to proposal state. This revision does not claim implementation. It defines the source/test envelope and the spec-derived commands that a later implementation report must run after LO records GO and Prime creates an implementation-start packet.

## Scope Changes

The revised implementation scope is:

- Add a `gt projects authorize --plan-incomplete` option, or an equivalent explicit keep-open option with the same durable semantics.
- Thread the option into `ProjectLifecycleService.authorize_project`.
- When selected, create an active project artifact link with `relationship="plan_incomplete"`, `artifact_type="completion_guard"`, and `artifact_ref=f"{authorization_id}-keepopen"`.
- Keep active `plan_incomplete` links whose `artifact_type` is `bridge_thread` as hard blockers for authorization completion.
- Treat active `plan_incomplete` links whose `artifact_type` is `completion_guard` as keep-open guards, not completion blockers.
- When completing an authorization with its own keep-open guard, complete the authorization, suppress project retirement for that completion, and then append an inactive/superseded version of the guard link so a later final authorization can retire the project normally.
- Keep existing single-slice behavior unchanged when no plan-incomplete option is present.
- Align `scripts/project_verified_completion_scanner.py` with the lifecycle service so read-only readiness surfaces do not contradict the mutation path.
- Update affected service, CLI, scanner, and hook tests.

Out of scope:

- Formal specification mutation.
- Broad project/backlog status mutation.
- Credential lifecycle work.
- Production deployment.
- Creating a new `cli_projects.py` module as part of this slice.

## Pre-Filing Preflight Subsection

Prime Builder pre-filing checks for this candidate revision:

- `groundtruth-kb/.venv/Scripts/gt.exe harness roles` - confirmed harness `A` resolves to `prime-builder`.
- `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi4876-multislice-project-keepopen-guard --json --compact` - confirmed latest status `NO-GO` at version 004 before drafting.
- `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status --json` - confirmed dispatcher routing selects `prime-builder:A`.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py status gtkb-wi4876-multislice-project-keepopen-guard` - confirmed this dispatch holds the draft work-intent claim.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4876-multislice-project-keepopen-guard --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4876-multislice-project-keepopen-guard-005.md` - candidate preflight must pass with `missing_required_specs: []`.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4876-multislice-project-keepopen-guard --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4876-multislice-project-keepopen-guard-005.md` - candidate clause preflight must exit 0 with no blocking gaps.

The `revise_bridge.py file` helper will re-run both candidate preflights immediately before writing the live versioned bridge file.

## Specification-Derived Verification Plan

| Spec / governing surface | Required verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4876-multislice-project-keepopen-guard` after GO, then target-path preflight over every changed path. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation report must show the GO-derived packet and no out-of-scope mutation. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Append-only bridge chain proceeds `NO-GO` to `REVISED` to LO verdict; no source change before GO. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target-path preflight and tests use only paths under `E:\GT-KB`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal and implementation report carry PAUTH/project/WI metadata. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | LO review runs applicability and clause preflights on this revised proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries the test table and observed command output. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | Service and hook tests prove plan-incomplete completion guards keep interim projects active while preserving normal final/single-slice retirement. |
| `GOV-STANDING-BACKLOG-001` | Tests prove unfinished project state is not silently retired by interim slice completion. |

Targeted implementation commands expected after GO:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_artifacts.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_verified_completion_scanner.py platform_tests/hooks/test_project_completion_surface.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py scripts/project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_verified_completion_scanner.py platform_tests/hooks/test_project_completion_surface.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py scripts/project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_verified_completion_scanner.py platform_tests/hooks/test_project_completion_surface.py
```

## Acceptance Criteria

- `gt projects authorize --plan-incomplete` or the chosen equivalent creates an active completion guard tied to the authorization id.
- Completing an authorization with its own completion guard completes the authorization, leaves the project active, and deactivates that guard.
- A later final authorization without a plan-incomplete guard can still retire the project when all normal completion criteria are met.
- Active `bridge_thread` plan-incomplete guards still block completion.
- Existing single-slice authorization completion and retirement behavior remains unchanged.
- Scanner and hook readiness surfaces agree with the lifecycle service.

## Risk And Rollback

Risk is moderate because project lifecycle automation is shared by hooks, CLI commands, and backlog status surfaces. The implementation should keep the behavior opt-in through explicit plan-incomplete election and should preserve all existing defaults. Rollback is a source/test revert plus a follow-up bridge report if LO finds the behavior diverges from the acceptance criteria.
