NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Project PAUTH auto-completion ignores current bridge verification state

bridge_kind: prime_proposal
Document: gtkb-project-pauth-autocomplete-verified-gate
Version: 001
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4384

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "platform_tests/scripts/test_project_authorization.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The project-lifecycle auto-completion path in `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` completes a project-scoped PAUTH (and retires its project) based solely on work-item VERIFIED-*coverage*, without requiring the project's current *addressing* bridge thread to itself be VERIFIED. Completion can therefore precede Loyal Opposition verification of the report thread that the GO authorized, which contradicts the bridge protocol's GO/VERIFIED discipline.

## Defect / Reproduction

Observed incident (origin of WI-4384): during Ollama Phase 2+ compatibility subproject completion-coverage reconciliation, six project-scoped `implements` links made all nine gating work items VERIFIED-covered. The lifecycle auto-completion path completed `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-PHASE-2-COMPLETION-COVERAGE-RECONCILIATION` and retired `PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-PHASE-2-COMPLETION` at `2026-06-06T04:23:40Z` while `bridge/gtkb-ollama-phase2-subproject-completion-coverage-005.md` was still `NEW` (awaiting LO verification).

Reproduction (logical): construct a project whose gating (membership-linked) work items are all VERIFIED-covered, but whose current `implements`-linked addressing bridge thread is at `NEW`/`REVISED` (not `VERIFIED`). The current readiness predicate (`PROJECT-GTKB-RELIABILITY-FIXES`-observed: `_is_authorization_completion_ready` / `auto_complete_ready_authorizations`) treats the authorization as completion-ready and completes/retires it. Expected: completion is withheld until the addressing thread reaches `VERIFIED`.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, `platform_tests/scripts/test_project_authorization.py`.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - governing authority for VERIFIED-driven project completion/retirement; the defect completes a PAUTH whose addressing thread is not yet VERIFIED, violating the spec's intent that completion is driven by verification evidence.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected behavior that project authorization must not bypass the bridge; auto-completing before the addressing thread is VERIFIED is a de-facto bridge bypass at the completion boundary.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - PAUTH envelope/lifecycle semantics; completion is an envelope state transition that must respect the verification gate.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge `VERIFIED` is the authoritative terminal signal; completion logic must read that signal before retiring a project.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives tests from the cited specs (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `GOV-STANDING-BACKLOG-001` - WI-4384 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform lifecycle module (`groundtruth-kb/src/...`) and platform tests; no application-placement boundary is crossed and no adopter/application surface is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix preserves the durable artifact lifecycle (PAUTH completion, project retirement) by keeping it consistent with bridge verification evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - completion-state transitions remain artifact-backed (bridge `VERIFIED`) rather than inferred from coverage alone.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the auto-completion trigger with the verification lifecycle state that should gate it.

## Prior Deliberations

- `DELIB-20264443` - LO Verification, Ollama Phase 2+ Compatibility Subproject Completion Coverage - the verification thread whose pre-VERIFIED window the auto-completion raced.
- `DELIB-20264394` - LO Verification, Ollama Project Completion Coverage Reconciliation - sibling reconciliation context for the same incident.
- `DELIB-20264442` - LO Review, Ollama Phase 2+ Compatibility Subproject Completion Coverage REVISED - the GO whose constraint the premature completion contradicted.
- `DELIB-20265457` - Owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (this WI is in scope).

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-4384 is origin=defect, single-concern, introduces no new public surface and no new/revised spec, and is bounded to ~1 source file + 1 test (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active project membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for all open PROJECT-GTKB-RELIABILITY-FIXES work items, pipeline-repair and P1/P2 first; WI-4384 is P1.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` already establishes that completion/retirement is driven by verification evidence; this fix enforces that contract at the auto-completion boundary by adding an addressing-thread VERIFIED gate. No new or revised requirement/specification is introduced.

## Proposed Scope

1. In `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, tighten the authorization completion-readiness predicate so an authorization is NOT completion-ready when its project holds an active `implements`-linked addressing bridge thread whose latest status is not `VERIFIED`. The check reuses the existing bridge latest-status reader (`groundtruth_kb.bridge.versioned_files.status_from_bridge_file` / the `_verified_thread_work_items` scan already imported in this module) so no new bridge-reading surface is introduced.
   - Scope the gate to projects that actually have an active `implements` addressing thread: a project with no addressing thread is unaffected (avoids over-tightening / regressions for membership-only completions).
   - The gate withholds completion (returns not-ready) rather than raising, so `auto_complete_ready_authorizations` simply skips the authorization until the addressing thread is VERIFIED.
2. Add regression tests in `platform_tests/scripts/test_project_authorization.py` (see verification plan).

This is the defect-removal path. The WI's alternative ("model/display that automatic completion can precede report verification") is a behavior/contract change requiring a new requirement and is explicitly out of scope for this fast-lane defect fix.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (completion is verification-driven) | `test_autocomplete_withheld_when_addressing_thread_not_verified` | A PAUTH whose gating WIs are all VERIFIED-covered but whose active `implements` thread is `NEW` is NOT completed/retired by `auto_complete_ready_authorizations`. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (no false-negative regression) | `test_autocomplete_proceeds_when_addressing_thread_verified` | The same PAUTH IS completed once the addressing thread reaches `VERIFIED`. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` (no bridge bypass) | `test_autocomplete_membership_only_project_unaffected` | A project with no active `implements` addressing thread retains prior completion behavior (gate does not over-reach). |

Execution commands:
- `python -m pytest platform_tests/scripts/test_project_authorization.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_project_authorization.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_project_authorization.py`

## Acceptance Criteria

1. `auto_complete_ready_authorizations` does not complete/retire an authorization whose project has an active `implements`-linked bridge thread that is not `VERIFIED`.
2. Completion proceeds unchanged when the addressing thread is `VERIFIED`, and for projects with no addressing thread (no regression).
3. The three derived tests pass; `ruff check` and `ruff format --check` are clean on the changed files.

## Risks / Rollback

- Risk: over-tightening could strand legitimately-complete projects that never had an addressing thread. Mitigation: the gate fires only when an active `implements` addressing thread exists and is non-VERIFIED.
- Risk: a project with multiple addressing threads where one is stale. Mitigation: the gate withholds completion if ANY active `implements` thread is non-VERIFIED, which is the conservative/correct posture for this defect.
- Rollback: revert the predicate change in `lifecycle.py`; the change is a single guarded condition plus tests, fully reversible with no migration.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `platform_tests/scripts/test_project_authorization.py`

## Recommended Commit Type

`fix`
