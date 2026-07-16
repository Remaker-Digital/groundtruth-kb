NEW

# Defect-Fix Proposal - Recognize governed reference-adopter release helpers

bridge_kind: prime_proposal
Document: gtkb-wi5290-isolation-backstop-deploy-disposition
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-15 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5290

target_paths: ["scripts/isolation_program_backstop.py", "platform_tests/scripts/test_isolation_program_backstop.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the release isolation backstop without undoing the approved Agent Red
build-context topology. The checker currently reports five violations in
`scripts/deploy/build-context.ps1` and
`scripts/deploy/build-and-deploy-staging.ps1` because both intentionally copy
`applications/Agent_Red/docs-site/docs` into the release build context.
Commit `99dd193a2e8c827e95dc4ef791ace80002847be6` deliberately restored those
paths as the scoped WI-4761 corrective after commit `22b79825` incorrectly
changed them to a root-level docs path.

The implementation will add two exact path-level allowlist entries to the
checker and a regression test proving that only those named helpers are
allowed. It will not add a `scripts/deploy/**` exemption, mutate either
deployment script, change application placement, or weaken the scanner for any
other source file.

## Baseline And Scope

- HEAD at proposal preparation:
  `6d9a906cedb56002921ce04be65de3413d151dff`.
- Both targets are tracked and byte-clean:
  - `scripts/isolation_program_backstop.py`:
    `c2167f62b688b4efd3897eaf5e27df0b96e173e3`.
  - `platform_tests/scripts/test_isolation_program_backstop.py`:
    `c119baca2a2b2bee4d991ce843a8e0ca6eb9b3d7`.
- `python scripts/isolation_program_backstop.py --json` currently exits 1
  with exactly five violations, all in the two named deployment helpers.
- The deployment helper bytes, Dockerfile, Agent Red files, bridge/TAFE,
  harness state, credentials, external systems, and concurrent worktree paths
  are read-only inputs.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red is the in-root
  reference adopter at `applications/Agent_Red`; a release build-context
  helper may intentionally copy its documentation while ordinary platform
  source remains isolated.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - The repair preserves the
  known-good WI-4761 deployment paths and keeps unrelated isolation violations
  fail-closed.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - The
  backstop remains a release-gate mechanical control, with an exact positive
  and negative test for the exception boundary.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - The two allowed paths,
  their reason, and the sibling-path rejection are explicit and testable.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected source and test mutation
  requires independent GO, matching claim, and implementation-start authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal
  links the exact exception boundary and verification to governing contracts.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, PAUTH,
  work item, and target paths are explicit above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent VERIFIED
  must rerun the focused tests and the live backstop.
- `GOV-STANDING-BACKLOG-001` - WI-5290 durably records this release blocker.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The false positive is preserved
  as a governed work item, proposal, implementation report, and verdict.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Commit history, tests, proposal,
  report, and verdict provide the durable evidence graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The red release gate triggers a
  bounded defect repair rather than an unreviewed allowlist expansion.

## Prior Deliberations

- `DELIB-0877` - The application-isolation program selected an asymmetric
  model: application sessions cannot mutate GT-KB product artifacts, while
  GT-KB release engineering may validate and package the reference adopter.
- `DELIB-0834` - Agent Red is a fully conformant reference application
  sustained by GT-KB, not an ad hoc exception outside platform governance.
- `DELIB-202666274` - The owner authorized all required modernization blocker
  repairs while preserving bridge, independent-review, implementation-start,
  and mechanical-operation gates.

## Owner Decisions / Input

No additional product decision is required. The approved WI-4761 corrective
commit already establishes the canonical deployment paths, and the current
project-level modernization authorization covers this bounded blocker repair.
This proposal does not authorize staging, commit, push, deployment, release,
credentials, dispatcher, TAFE, harness, routing, role, or external-system
mutation.

## Requirement Sufficiency

Existing requirements sufficient.

The application-placement ADR defines the reference adopter location, the
non-impairment contract prohibits breaking known-good release behavior, and the
backstop already uses exact file-level reasons for legitimate platform-owned
cross-scope helpers. No new product requirement or deployment behavior is
needed; the checker lacks only the narrow disposition and regression boundary.

## Proposed Scope

1. Add exact `ALLOWED_REFERENCE_PATTERNS` entries for
   `scripts/deploy/build-context.ps1` and
   `scripts/deploy/build-and-deploy-staging.ps1`, using a reason that names
   their reference-adopter release build-context role.
2. Add a focused test fixture containing those two exact helper paths plus a
   different `scripts/deploy/other.ps1` path.
3. Prove the two named helpers are reported as allowed and the sibling helper
   remains a violation.
4. Preserve deployment helper bytes and every non-target file byte-for-byte.
5. Run the live backstop, focused tests, Ruff, and format checks.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5290, DELIB-0834, DELIB-0877, DELIB-202666274, and corrective commit 99dd193a2e8c827e95dc4ef791ace80002847be6",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/isolation_program_backstop.py",
  "before_behavior": "The release gate rejects five intentional references in two governed build-context helpers.",
  "after_behavior": "The two exact helpers are classified as allowed while every other deployment helper remains subject to the isolation violation check.",
  "self_descriptive_naming": "The allowlist reason names the reference-adopter release build-context purpose and the regression test names the exact-path boundary.",
  "obsolete_guidance_disposition": "The mistaken root-level docs-path interpretation from commit 22b79825 remains superseded by the approved WI-4761 corrective; no current deployment guidance is retired.",
  "history_preservation": "The deployment scripts and their approved corrective commit remain unchanged; WI-5290 records why the checker disposition is valid.",
  "baseline": {
    "head": "6d9a906cedb56002921ce04be65de3413d151dff",
    "checker_blob": "c2167f62b688b4efd3897eaf5e27df0b96e173e3",
    "test_blob": "c119baca2a2b2bee4d991ce843a8e0ca6eb9b3d7",
    "live_violations": 5,
    "violating_files": 2
  },
  "expected_result": {
    "live_violations": 0,
    "exact_allowed_helper_paths": 2,
    "broad_deploy_globs_added": 0,
    "deployment_script_changes": 0
  },
  "essential_context_preservation": "The scanner continues to examine platform-owned scripts and to reject application references in every non-allowlisted deployment helper.",
  "hard_invariants": [
    "no scripts/deploy/** or other broad exemption",
    "no deployment script or Dockerfile mutation",
    "no change to application placement",
    "no exception for arbitrary sibling helpers",
    "no target outside the two clean tracked files",
    "frozen modernization acceptance scope unchanged"
  ],
  "fail_closed_conditions": [
    "a non-allowlisted deployment helper becomes allowed",
    "either canonical helper remains a violation",
    "the live backstop reports any unexpected violation",
    "focused tests, Ruff, or format checks fail"
  ],
  "rollback": "Remove only the two WI-5290 allowlist entries and their focused regression test, then rerun the live backstop."
}
```

## Spec-Derived Verification Plan

| Specification | Verification and expected result |
|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Inspect the diff and Git history to prove application placement and deployment helpers are unchanged. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `python scripts/isolation_program_backstop.py` exits zero with the approved WI-4761 paths intact. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | The focused test proves both exact allowed paths and an unauthorized sibling in one deterministic scan. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Allowed-reference output carries the named reason and violation output identifies the sibling path exactly. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability and ADR/DCL clause preflights pass with zero blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reruns the live checker, focused pytest, Ruff, and format checks before VERIFIED. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify valid GO, matching claim, and implementation-start packet before either target is edited. |

Exact implementation verification commands:

```text
python scripts/isolation_program_backstop.py
python -m pytest platform_tests/scripts/test_isolation_program_backstop.py -q --tb=short
python -m ruff check scripts/isolation_program_backstop.py platform_tests/scripts/test_isolation_program_backstop.py
python -m ruff format --check scripts/isolation_program_backstop.py platform_tests/scripts/test_isolation_program_backstop.py
```

## Acceptance Criteria

1. The live backstop exits zero with both approved deployment helpers
   unchanged.
2. Exactly the two named deployment helper paths receive the
   reference-adopter release build-context reason.
3. A different file under `scripts/deploy/` containing the same reference
   remains a violation.
4. No broad deploy-directory exception, deployment behavior change,
   application-placement change, credential access, or external operation.
5. Both targets pass focused pytest, Ruff, and format checks.
6. The implementation report records exact commands and counts for independent
   Loyal Opposition verification.

## Risk / Rollback

The primary risk is accidentally turning a narrow disposition into a directory
exemption. Exact filenames and a sibling negative test contain that risk.
Rollback removes only the two allowlist tuples and the focused test; deployment
files remain untouched throughout.

## Bridge Filing

This proposal is filed as the first append-only numbered bridge file,
`bridge/gtkb-wi5290-isolation-backstop-deploy-disposition-001.md`; no prior
version is deleted or rewritten. Dispatcher/TAFE state plus the numbered bridge
files remain the governed workflow surfaces.

## Recommended Commit Type

`fix` - the change corrects a release-gate false positive while preserving the
approved isolation and deployment behavior. Any eventual commit remains
separately mechanically authorized.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
