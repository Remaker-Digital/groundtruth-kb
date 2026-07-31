NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Phase 3 gap 04: CLI compactness and source-of-truth size controls

bridge_kind: prime_proposal
Document: gtkb-wi4966-cli-compactness-sot-size-controls
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4966-BATCH-C-20260705
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4966

target_paths: ["scripts/sot_compactness_audit.py", "platform_tests/scripts/test_sot_compactness_audit.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-SOT-COMPACTNESS-*.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement a deterministic compactness audit for large source-of-truth surfaces used in harness equivalence work. The audit should identify whether routine CLI reads default to compact/current/actionable output for MemBase, Deliberation Archive, dispatcher state, transcript inventories, advisory-router output, and other large SoT classes, while linking existing envelope-sharding compact query work instead of duplicating it.

The work item scope is limited to WI-4966. It does not authorize broad CLI rewrites or replacement of existing compact query implementations.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4966` that turns oversized SoT risk into measurable compactness evidence and targeted follow-on dispositions.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-INTAKE-46594e` and `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` establish the token-load concern; the Batch C PAUTH defines the permitted implementation boundary.

## In-Root Placement Evidence

All proposed target paths are inside `E:\GT-KB`: `scripts/sot_compactness_audit.py`, `platform_tests/scripts/test_sot_compactness_audit.py`, and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-SOT-COMPACTNESS-*.md`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - confirms implementation authority is project-bounded and evidence-backed.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass bridge proposal review or later GO.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge status filing.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing spec links before implementation review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation reports to map specs to executed verification.
- `SPEC-INTAKE-46594e` - oversized startup context and unsharded surfaces are known token-load risks.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - requires startup/session surfaces to control context load.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - routes compactness findings into governed evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps follow-on action boundaries artifact-backed.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires dispositions for new compactness gaps, supersession, or no-op coverage.

## Prior Deliberations

- `DELIB-202665197` - authorized Harness Equivalence Phase 3 child work.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner-directed Batch C continuation authorization.
- `DELIB-202665119` - prior compact query mode review context for oversized SoT and transcript surfaces.
- `DELIB-202665127` - session/activity envelope sharding taxonomy and global baseline context.
- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - envelope-sharding closure/reuse context.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch C continuation.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4966-BATCH-C-20260705` - active authorization covering WI-4966.

## Proposed Scope

- Add a read-only compactness audit helper with a declarative registry of large SoT classes and expected routine read behavior.
- Verify whether each surface has a compact/current/actionable route, an archival/full route with explicit justification, or an identified gap.
- Link existing envelope-sharding compact query work as prior coverage where applicable.
- Emit a compact markdown report with per-surface status, evidence command, expected default, and follow-on disposition.
- Add focused tests for registry validation, command classification, report rendering, and duplicate-coverage detection.

## Cross-Harness Disposition

The helper supports harness-equivalence work by preventing one harness from loading larger routine context than another. It does not change harness startup envelopes directly; it reports compactness gaps and makes later changes bridge-governed.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm implementation report cites the active WI-4966 PAUTH and stays within target paths. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Confirm no protected implementation starts before GO. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use `gt bridge show gtkb-wi4966-cli-compactness-sot-size-controls --json --compact` to confirm lifecycle state. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm project linkage metadata is present. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run targeted tests and include exact command output in the implementation report. |
| `SPEC-INTAKE-46594e` | Test that oversized surfaces require compact defaults or explicit archival classification. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | Test that routine startup/session surfaces are classified against compact-read expectations. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Confirm the report preserves durable evidence and follow-on disposition. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Confirm gaps are report-backed and not left as transient notes. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm duplicate coverage, new gaps, and superseded surfaces are separated. |

## Acceptance Criteria

- The helper produces a compactness report covering MemBase, Deliberation Archive, dispatcher state, transcript inventories, advisory-router output, bridge state, project authorizations, and known envelope-sharding surfaces.
- The report links existing compact query work instead of proposing duplicate implementation where coverage already exists.
- Each uncovered large SoT class gets a concrete follow-on disposition.
- Tests cover the registry, compact/default classification, archival/full classification, duplicate-coverage detection, and markdown output.

## Risks / Rollback

Risk is moderate because compactness findings can drive later CLI work. Mitigation is read-only auditing and explicit separation between evidence, duplicates, and follow-on implementation candidates.

Rollback is a revert of the helper, tests, and generated report. Bridge files and PAUTH records are append-only audit artifacts and must not be deleted.

## Files Expected To Change

- `scripts/sot_compactness_audit.py`
- `platform_tests/scripts/test_sot_compactness_audit.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-SOT-COMPACTNESS-*.md`

## Recommended Commit Type

`feat`
