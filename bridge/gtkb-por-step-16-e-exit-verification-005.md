REVISED
Responds-to: bridge/gtkb-por-step-16-e-exit-verification-004.md

# gtkb-por-step-16-e-exit-verification — POR Step 16.E Exit Verification Remediation Plan

bridge_kind: prime_proposal
Document: gtkb-por-step-16-e-exit-verification
Version: 005
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-20 UTC

author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: cb447a9a-62e4-4fbe-8f6f-ef77dee8e1d3
author_model: Gemini 2.5 Flash
author_model_version: gemini-2.5-flash
author_model_configuration: Antigravity IDE session

Project Authorization: PAUTH-PROJECT-POR-SPEC-HYGIENE-EXIT-VERIFICATION
Project: PROJECT-POR-SPEC-HYGIENE
Work Item: WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION-16-A-B-C-COMPLETE

target_paths: ["scripts/remediate_por_step_16e.py", "platform_tests/scripts/test_remediate_por_step_16e.py", "scripts/por_step_16_exit_verification.py", "groundtruth.db", ".groundtruth/remediation-manifest.json"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This revised proposal details the remediation plan to satisfy the exit criteria of POR Step 16.E.
Currently, the exit verification gate fails due to 2,189 orphan test records in the database, and 84 implemented/verified specifications without test linkages.

We propose:
1. Enacting a row-by-row machine-readable disposition manifest `.groundtruth/remediation-manifest.json` which maps each of the 2,189 orphan tests and waives the 48 specs.
2. Implementing a database remediation script `scripts/remediate_por_step_16e.py` that executes a manifest-driven class-based disposition:
   - **Adopt (69 tests)**: Identify the 69 tests in Class B that name a candidate specification ID in their metadata and adopt them by inserting a new test version linking them to the spec ID.
   - **Retire (2,120 tests)**: Retire the remaining 2,120 visual, layout, and adopter tests that belong to the legacy reference adopter application (Agent Red) by deleting them from the `tests` table in `groundtruth.db` (Class B remainder: 1,634; Class C: 481; Class D: 5).
   - **Covered Specs (36 specs)**: Map the 36 specifications that have existing spec-derived tests in the codebase (as discovered in `scratch/found_test_mappings.json`) by inserting new test rows linked to these specs.
3. Registering an owner waiver under `DELIB-20265456` for the remaining 48 specifications that lack test files in the platform codebase.
4. Modifying `scripts/por_step_16_exit_verification.py` to read `.groundtruth/remediation-manifest.json` and exclude the 48 waived specifications from the count of untested specifications, allowing the gate to pass.
5. Implementing regression tests in `platform_tests/scripts/test_remediate_por_step_16e.py` verifying dry-run safety, boundary checks, and post-remediation success.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — The bridge protocol and CLI command execution.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Specification linkage requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Bounded metadata headers.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verification requires tests.
- `GOV-STANDING-BACKLOG-001` — Backlog management.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — Release readiness; orphan tests block readiness.
- `GOV-ARTIFACT-APPROVAL-001` — Bulk-mutation governance.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — The in-root application placement isolation boundary.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — Modeling project memory as a durable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Artifact lifecycle triggers, thresholds, and states.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — Artifact-oriented governance as the default project interpretation stance.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` — Batch-5 authorization including this WI.
- `DELIB-0822` — POR 16.D Phase 1 complete, which corrected the 2,322-test empty-spec orphan baseline.
- `DELIB-0823` — POR 16.D Phase 2 complete, which classified the 2,189 orphan baseline into Class B (1,703), C (481), and D (5).
- `DELIB-2313` — POR 16.D Phase 2 verification.
- `DELIB-20265448` — Version 002 NO-GO review.
- `DELIB-20265451` — Version 004 NO-GO review.
- `DELIB-20265456` — Owner waiver and bulk test deletion approval deliberation.

## Owner Decisions / Input

- `DELIB-20265456` — The owner approved waiving the spec-derived test coverage requirements for the 48 specifications listed in the manifest (uncovered section) and approved the bulk deletion of the 2,120 stale legacy test rows.

## Requirement Sufficiency

Existing requirements sufficient — The work item details specify the exit criteria for Step 16.E: untested-spec count <= 6 and orphan-test count <= 100.

## Spec-Derived Verification Plan

| Behavior | Test |
|---|---|
| Dry-run mode performs no writes | `test_remediate_dry_run_does_not_mutate` in `platform_tests/scripts/test_remediate_por_step_16e.py` |
| Remediation script adopts 69, retires 2,120, and links 36 specs | `test_remediate_apply_lifecycle` in `platform_tests/scripts/test_remediate_por_step_16e.py` |
| Boundary check fails closed on out-of-manifest orphan tests | `test_remediate_fails_on_unmapped_orphans` in `platform_tests/scripts/test_remediate_por_step_16e.py` |
| Exit verification CLI exits 0 post-remediation | `python scripts/por_step_16_exit_verification.py` |

## Risk / Rollback

Risk: Mutating database test records might dirty the test-audit history.
Rollback: A SQLite backup of `groundtruth.db` is captured as `groundtruth.db.pre-remediate.bak` before the mutation. The changes can be rolled back by restoring the database file from `groundtruth.db.pre-remediate.bak`.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-por-step-16-e-exit-verification`; no prior version is deleted or rewritten (append-only).

## Recommended Commit Type

feat

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
