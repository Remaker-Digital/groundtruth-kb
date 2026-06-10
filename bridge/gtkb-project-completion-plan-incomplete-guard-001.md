NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-20260606T0800Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Keep Working PB automation; high autonomy
author_metadata_source: Codex automation context

# Defect-Fix Proposal - Project completion plan-incomplete guard

bridge_kind: prime_proposal
Document: gtkb-project-completion-plan-incomplete-guard
Version: 001 (NEW)
Date: 2026-06-06 UTC

Project Authorization: PAUTH-GTKB-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION-001
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001-PROJECT-LIFECYCLE
Work Item: WI-3481

target_paths: ["scripts/project_verified_completion_scanner.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", "platform_tests/hooks/test_project_completion_surface.py", "groundtruth-kb/tests/test_project_artifacts.py"]

## Claim

`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` currently lets the project completion scanner and lifecycle service decide completion from active, materialized project work-item memberships only. That is correct for fully materialized projects, but it is unsafe for incrementally-materialized multi-slice projects: if only early slices have been created and all early slices reach `VERIFIED`, the project can appear complete even when the governing scoping decision still expects later slices. This proposal adds an explicit, reversible project-level `plan_incomplete` completion guard that suppresses automatic PAUTH completion and project retirement until Prime removes or supersedes the guard after the plan is fully materialized.

## Defect / Reproduction

Backlog item `WI-3481` records the live defect:

- `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE` was auto-completed and retired at 2026-05-30T02:18Z after Slices 1-3 reached `VERIFIED` while Slices 4-10 had not yet been filed as active project members.
- `memory/pending-owner-decisions.md` lines 5268-5277 preserve the owner AUQ: the scanner looked complete because future slices were not yet materialized; Mike selected `Reactivate + pre-bind all remaining slices` as the immediate recovery.
- `WI-3481` captures the root-cause follow-up: pre-binding all future slice WIs works around one occurrence, but the automation still has no explicit project-level signal saying this project plan is intentionally incomplete.

Current code evidence:

- `scripts/project_verified_completion_scanner.py` computes `completion_ready = bool(included) and not unverified_ids`, where `included` is the active project membership set. It has no suppression path for known-incomplete multi-slice plans.
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` uses the same active membership set in `_authorization_completion_ready` and can auto-complete/retire through `auto_complete_ready_authorizations`.
- Both surfaces already use `current_project_artifact_links` for project-scoped `bridge_thread` relationships, so a project artifact-link guard can be added without schema changes.

## Precedence / Dependency Check

Live Prime bridge scan had no actionable latest `GO` or `NO-GO` entries. Live Loyal Opposition scan had `NEW` entries, which Prime must not review. Among active high-priority backlog/project candidates, `PROJECT-GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` is blocked on LO/owner security-history handling; `WI-3481` is the highest-priority Prime-scope deterministic-services defect with a concrete existing failure mode. It should precede additional project lifecycle automation because it protects the shared auto-retirement path from recurring false-positive completion.

## In-Root Placement Evidence

All target paths are inside `E:/GT-KB`:

- `scripts/project_verified_completion_scanner.py`
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `platform_tests/scripts/test_project_verified_completion_scanner.py`
- `platform_tests/hooks/test_project_completion_surface.py`
- `groundtruth-kb/tests/test_project_artifacts.py`

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - governing rule for project authorization completion and automatic project retirement; this proposal repairs a known false-positive completion case.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - work is routed through the bridge protocol; this `NEW` proposal requests LO review before implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing project lifecycle and cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must ship with mapped executable checks.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - header includes Project Authorization, Project, and Work Item metadata.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix uses a durable project artifact link rather than an implicit note or transient session memory.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the guard is represented as a project artifact lifecycle record and covered by regression checks.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching project lifecycle automation requires matching check coverage and explicit artifact-state handling.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all paths and artifacts remain in the GT-KB root.
- `GOV-STANDING-BACKLOG-001` - `WI-3481` is the tracked backlog item for the root-cause defect.

## Prior Deliberations

- `memory/pending-owner-decisions.md` S374 AUQ lines 5268-5277 - owner selected the immediate recovery for the false-positive retirement and explicitly noted that the misfire would recur until root cause was handled.
- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - owner-decision evidence for deterministic-services project authorization lineage.
- `DELIB-S374` / `WI-3481` source directive - owner chose pre-bind mitigation; root-cause fix tracked separately.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix` - prior verified v4 project-scoped completion work; this proposal preserves that project-scoped verified-set model and adds a separate incomplete-plan suppressor.

## Owner Decisions / Input

- `WI-3481` source owner directive: `Owner AUQ S374 chose pre-bind mitigation; root-cause fix tracked separately.`
- `PAUTH-GTKB-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION-001` is active for `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-PROJECT-LIFECYCLE`; `scripts/implementation_authorization.py` validates work items that are active project members even when not explicitly listed in `included_work_item_ids`.
- No new owner decision is requested by this proposal. Loyal Opposition should decide GO/NO-GO on whether the proposed guard shape is sufficient.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` defines automatic completion for verified project work, and `WI-3481` defines the defect caused by incrementally-materialized multi-slice projects. This proposal does not change the base completion rule; it adds an explicit suppression signal for projects whose Prime-maintained plan is not fully materialized yet.

## Proposed Scope

### IP-1 - Define the completion guard query

Add a shared helper in `scripts/project_verified_completion_scanner.py` and equivalent package-layer helper in `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`:

- A project is completion-guarded when `current_project_artifact_links` contains an active row for that project with either `artifact_type = 'completion_guard'` and `relationship = 'plan_incomplete'`, or `artifact_type = 'bridge_thread'` and `relationship = 'plan_incomplete'`.
- The helper returns enough detail for diagnostics: project id, artifact ref, artifact type, relationship, and notes.
- Inactive/superseded rows do not suppress completion because the query reads the latest-version current view and requires `status = 'active'`.

### IP-2 - Scanner suppression

Update `scripts/project_verified_completion_scanner.py` so guarded projects are not reported as completion-ready:

- Add a `completion_guarded` boolean and optional `completion_guard_refs` list to `AuthorizationReadiness.as_dict()`.
- Compute guard status once per project inside `scan()`.
- Set `completion_ready = bool(included) and not unverified_ids and not completion_guarded`.
- Preserve current behavior for projects without an active guard.

### IP-3 - Lifecycle-service suppression

Update `ProjectLifecycleService._authorization_completion_ready()` and/or its caller so active `plan_incomplete` guards block automatic completion and retirement:

- If the authorization's project has an active guard, return false even when all materialized members are verified.
- `auto_complete_ready_authorizations()` must not call `complete_project_authorization()` for guarded projects.
- Completion of unguarded projects remains unchanged.

### IP-4 - Regression checks

Add focused regression checks that fail on current behavior and pass with the guard:

1. Scanner regression: temp DB with one active project authorization, active membership, verified implements link, and active `plan_incomplete` guard. Assert `scan(...)[0].completion_ready is False` and JSON includes guard diagnostics.
2. Scanner non-regression: same fixture without the guard remains completion-ready.
3. Lifecycle regression: service auto-completion does not retire/complete a guarded project even when all current members are verified.
4. Lifecycle non-regression: unguarded all-verified project still auto-completes under existing v4 rules.
5. Artifact-link current-view regression: a superseded/inactive guard row does not suppress completion.

## Specification-Derived Verification Plan

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`: run `python -m pytest platform_tests/scripts/test_project_verified_completion_scanner.py -q --tb=short`; expected result is guarded all-materialized projects are not completion-ready and unguarded projects still are.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`: run `python -m pytest platform_tests/hooks/test_project_completion_surface.py groundtruth-kb/tests/test_project_artifacts.py -q --tb=short`; expected result is guarded projects are not auto-retired and existing unguarded completion remains intact.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: run `python -m pytest platform_tests/scripts/test_project_verified_completion_scanner.py platform_tests/hooks/test_project_completion_surface.py groundtruth-kb/tests/test_project_artifacts.py -q --tb=short`; expected result is all mapped assertions pass.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: add a focused check covering active versus inactive or superseded guard rows; expected result is only active latest-version guard rows suppress completion.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: run `python -m ruff check scripts/project_verified_completion_scanner.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_project_verified_completion_scanner.py platform_tests/hooks/test_project_completion_surface.py groundtruth-kb/tests/test_project_artifacts.py`; expected result is all touched files are in-root and lint clean.

## Acceptance Criteria

1. A project with an active `plan_incomplete` completion guard is never reported as completion-ready by `scripts/project_verified_completion_scanner.py`.
2. `ProjectLifecycleService.auto_complete_ready_authorizations()` does not complete PAUTHs or retire projects while the project has an active guard.
3. Removing, superseding, or inactivating the guard restores existing completion behavior when all active project members are verified.
4. Scanner JSON exposes guard diagnostics so operators can understand why an all-verified materialized set is still not ready.
5. Unguarded project completion behavior remains unchanged, including the v4 project-scoped `implements` link rule.
6. Focused pytest and ruff commands in the verification plan pass.
7. `WI-3481` remains open until implementation reaches `VERIFIED`; this proposal only requests LO GO.

## Risks / Rollback

- Risk: A stale active guard could keep a completed project open. Mitigation: guard is explicit, visible in scanner JSON/text, and reversible by inactivating or superseding the project artifact link.
- Risk: Two accepted guard encodings may seem broader than necessary. Mitigation: both encodings are exact and require `relationship = 'plan_incomplete'`; incidental `related`, `implements`, and `source_evidence` links do not suppress completion.
- Risk: Scanner/service drift if the guard query is duplicated. Mitigation: checks cover both surfaces; if implementation finds a clean shared package helper reachable by both layers without cross-layer import fragility, use it.
- Rollback: remove the guard query and the `completion_guarded` readiness fields/checks. Existing completion behavior is restored because the schema is unchanged and guard rows become inert.

## Files Expected To Change

- `scripts/project_verified_completion_scanner.py`
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `platform_tests/scripts/test_project_verified_completion_scanner.py`
- `platform_tests/hooks/test_project_completion_surface.py`
- `groundtruth-kb/tests/test_project_artifacts.py`

## Recommended Commit Type

`fix` - defect repair for premature automatic project completion/retirement in incrementally-materialized multi-slice plans.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not add credentials or environment values; only project lifecycle source, scanner logic, and check files are touched. | Bridge helper credential scan plus scoped diff review before implementation report. | |
| CQ-PATHS-001 | Yes | Keep all proposal and implementation paths under `E:/GT-KB`; no application or archive paths. | Applicability preflight and git diff name review scoped to listed paths. | |
| CQ-COMPLEXITY-001 | Yes | Add one guard-query helper per existing layer and keep completion predicate change local to readiness calculation. | Focused diff review plus ruff lint on touched Python files. | |
| CQ-CONSTANTS-001 | Yes | Define guard tokens once per layer as named constants, not repeated string literals in predicates and fixtures. | Run `rg plan_incomplete completion_guard` and review intentional constant usage plus fixtures. | |
| CQ-SECURITY-001 | Yes | Do not change credential scanning, dispatch, hook permissions, deployment, or release behavior. | Diff review confirms mutation is limited to project lifecycle completion paths and check files. | |
| CQ-DOCS-001 | Yes | Record operator-visible behavior in this bridge proposal and expose guard diagnostics through scanner output. | LO review plus scanner JSON and text regression assertions. | |
| CQ-TESTS-001 | Yes | Add regression and non-regression checks for guarded and unguarded completion behavior in scanner and lifecycle service. | Run focused pytest commands listed in the specification-derived verification plan. | |
| CQ-LOGGING-001 | N/A | No logging code is changed. | Diff review confirms no logger or telemetry surface is touched. | Completion predicate and checks only. |
| CQ-VERIFICATION-001 | Yes | Capture focused pytest, ruff lint, bridge applicability preflight, and ADR/DCL clause preflight in the implementation report. | Exact command output and exit codes recorded before requesting VERIFIED. | |
