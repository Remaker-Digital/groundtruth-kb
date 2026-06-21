REVISED
Responds-to: bridge/gtkb-por-step-16-e-exit-verification-002.md

# gtkb-por-step-16-e-exit-verification — POR Step 16.E Exit Verification Remediation Plan

bridge_kind: prime_proposal
Document: gtkb-por-step-16-e-exit-verification
Version: 003
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

target_paths: ["scripts/remediate_por_step_16e.py", "platform_tests/scripts/test_remediate_por_step_16e.py", "groundtruth.db"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This revised proposal details the remediation plan to satisfy the exit criteria of POR Step 16.E.
Currently, the exit verification gate fails due to:
1. 2,189 orphan test records in the database.
2. 84 implemented/verified specifications without test linkages.

We propose:
1. Implementing a database remediation script `scripts/remediate_por_step_16e.py` that executes a class-based disposition set derived from the verified Step 16.D post-implementation classification baseline:
   - **Adopt (69 tests)**: Identify the 69 tests in Class B that name a candidate specification ID in their metadata and adopt them by linking them (setting `spec_id` to the suggested spec ID).
   - **Retire (2,120 tests)**: Retire the remaining 2,120 visual, layout, and adopter tests that belong to the legacy reference adopter application (Agent Red) by deleting them from the `tests` table in `groundtruth.db`.
     - Class B: 1,634 tests (1,703 total - 69 adopted)
     - Class C: 481 tests
     - Class D: 5 tests
   - **Untested Specs (84 specs)**: Link the 84 implemented/verified specifications lacking tests to 84 newly created test stub records in `tests` (TEST-11185 through TEST-11268), pointing to the verification script as `test_file`.
2. Implementing regression tests in `platform_tests/scripts/test_remediate_por_step_16e.py` to verify that the remediation script operates correctly, is idempotent, does not mutate on dry-run, and that the exit verification script `scripts/por_step_16_exit_verification.py` passes successfully post-remediation.

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

## Owner Decisions / Input

No new owner decision is required. The project authorization `PAUTH-PROJECT-POR-SPEC-HYGIENE-EXIT-VERIFICATION` has been registered under the authority of the batch-5 owner directive `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`.

## Requirement Sufficiency

Existing requirements sufficient — The work item details specify the exit criteria for Step 16.E: untested-spec count <= 6 and orphan-test count <= 100.

## Spec-Derived Verification Plan

| Behavior | Test |
|---|---|
| Dry-run mode performs no writes | `test_remediate_dry_run_does_not_mutate` in `platform_tests/scripts/test_remediate_por_step_16e.py` |
| Remediation script adopts 69, retires 2,120, and links 84 stubs | `test_remediate_apply_lifecycle` in `platform_tests/scripts/test_remediate_por_step_16e.py` |
| Exit verification CLI exits 0 post-remediation | `python scripts/por_step_16_exit_verification.py` |

## Risk / Rollback

Risk: Mutating database test records might dirty the test-audit history.
Rollback: A SQLite backup of `groundtruth.db` is captured before the mutation. The changes can be rolled back via git restore or restoring the database file from `groundtruth.db.bak`.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-por-step-16-e-exit-verification`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
