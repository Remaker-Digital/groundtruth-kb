NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Phase 3 gap 06: activity and result envelope equivalence evidence

bridge_kind: prime_proposal
Document: gtkb-wi4968-envelope-equivalence-evidence
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4968-BATCH-C-20260705
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4968

target_paths: ["scripts/harness_envelope_equivalence.py", "platform_tests/scripts/test_harness_envelope_equivalence.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-ENVELOPE-EQUIVALENCE-*.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement a read-only evidence helper that compares activity, result, and session-envelope behavior across harness lanes using WI-4950 as the baseline. The output must show equivalent behavior where present and typed waivers where a harness legitimately exposes a different result envelope, without reopening verified envelope-sharding work.

The work item scope is limited to WI-4968. It does not authorize changes to envelope schemas, dispatcher routing, or already VERIFIED envelope-sharding implementation.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4968` that turns envelope-equivalence assumptions into repeatable evidence.

## Requirement Sufficiency

Existing requirements are sufficient. The Batch C PAUTH, `ADR-CROSS-HARNESS-PARITY-001`, `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001`, and `DCL-DISPATCH-ENVELOPE-SCHEMA-001` define the comparison boundary.

## In-Root Placement Evidence

All proposed target paths are inside `E:\GT-KB`: `scripts/harness_envelope_equivalence.py`, `platform_tests/scripts/test_harness_envelope_equivalence.py`, and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-ENVELOPE-EQUIVALENCE-*.md`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - confirms implementation authority is project-bounded and evidence-backed.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass bridge proposal review or later GO.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge status filing.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing spec links before implementation review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation reports to map specs to executed verification.
- `ADR-CROSS-HARNESS-PARITY-001` - requires equivalent behavior or typed waivers across harnesses.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` - governs dispatch envelope structure and separation of session/activity/result concerns.
- `DCL-DISPATCH-ENVELOPE-SCHEMA-001` - governs required envelope fields and schema expectations.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - routes evidence into durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps findings and follow-on actions artifact-backed.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - separates new gaps, waivers, supersession, and no-op coverage.

## Prior Deliberations

- `DELIB-202665197` - authorized Harness Equivalence Phase 3 child work.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner-directed Batch C continuation authorization.
- `DELIB-202665127` - session/activity envelope sharding taxonomy and global baseline.
- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - instruction to complete and retire envelope-sharding child work.
- `DELIB-202665120` - prior verified envelope-sharding context.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch C continuation.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4968-BATCH-C-20260705` - active authorization covering WI-4968.

## Proposed Scope

- Add a read-only helper that loads WI-4950 baseline expectations and current harness/result evidence.
- Classify each harness lane as equivalent, equivalent-with-limits, typed-waived, missing evidence, or superseded by verified envelope-sharding work.
- Emit a compact markdown report with evidence references and explicit non-duplication notes for already verified envelope-sharding slices.
- Add focused tests for baseline parsing, envelope comparison, typed-waiver classification, supersession handling, and report output.

## Cross-Harness Disposition

The implementation compares behavior across all applicable harness lanes. It must not normalize differences by mutating schemas or provider routes in this slice; discrepancies become typed waivers or follow-on work candidates.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm implementation report cites the active WI-4968 PAUTH and stays within target paths. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Confirm no protected implementation starts before GO. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use `gt bridge show gtkb-wi4968-envelope-equivalence-evidence --json --compact` to confirm lifecycle state. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm project linkage metadata is present. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run targeted tests and include exact command output in the implementation report. |
| `ADR-CROSS-HARNESS-PARITY-001` | Test that every applicable harness lane is equivalent, typed-waived, or missing-evidence classified. |
| `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` | Test that session, activity, and result envelope concerns remain separately classified. |
| `DCL-DISPATCH-ENVELOPE-SCHEMA-001` | Test required envelope-field classification and missing-field reporting. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Confirm evidence and follow-on dispositions are preserved in the report. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Confirm discrepancies are artifact-backed and not transient. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm the report separates new work, typed waiver, superseded, and no-op coverage. |

## Acceptance Criteria

- The helper produces a compact envelope-equivalence report using WI-4950 as baseline evidence.
- Each applicable harness lane is classified for activity, result, and session-envelope behavior.
- Verified envelope-sharding work is linked as existing coverage instead of reopened.
- Tests cover baseline loading, comparison logic, typed waivers, missing evidence, supersession, and markdown output.

## Risks / Rollback

Risk is moderate because equivalence evidence can shape later release gating. Mitigation is read-only comparison and explicit preservation of verified envelope-sharding boundaries.

Rollback is a revert of the helper, tests, and generated report. Bridge files and PAUTH records are append-only audit artifacts and must not be deleted.

## Files Expected To Change

- `scripts/harness_envelope_equivalence.py`
- `platform_tests/scripts/test_harness_envelope_equivalence.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-ENVELOPE-EQUIVALENCE-*.md`

## Recommended Commit Type

`feat`
