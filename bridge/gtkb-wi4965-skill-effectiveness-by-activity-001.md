NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Phase 3 gap 03: skill discoverability and effectiveness by activity

bridge_kind: prime_proposal
Document: gtkb-wi4965-skill-effectiveness-by-activity
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4965-BATCH-C-20260705
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4965

target_paths: ["scripts/harness_skill_effectiveness.py", "platform_tests/scripts/test_harness_skill_effectiveness.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-SKILL-EFFECTIVENESS-*.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement a deterministic, read-only skill effectiveness audit for Phase 3 harness equivalence. The audit should compare generated skill projections, harness capability registry entries, and activity-envelope evidence to show whether specialized activities have discoverable and actually-used skills across each harness lane.

The work item scope is limited to WI-4965. It does not authorize per-harness skill edits, hook changes, provider changes, credential work, or direct mutation of generated runtime state.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4965` and preserves the project authorization, bridge review, and spec-derived verification gates.

## Requirement Sufficiency

Existing requirements are sufficient. The active Batch C PAUTH covers source, test, CLI/helper, config, and governance-evidence work for WI-4965, while the bridge remains the implementation-start gate for protected mutations.

## In-Root Placement Evidence

All proposed target paths are inside `E:\GT-KB`: `scripts/harness_skill_effectiveness.py`, `platform_tests/scripts/test_harness_skill_effectiveness.py`, and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-SKILL-EFFECTIVENESS-*.md`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - confirms implementation authority is project-bounded and evidence-backed.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass bridge proposal review or later GO.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge status filing.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing spec links before implementation review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation reports to map specs to executed verification.
- `ADR-CROSS-HARNESS-PARITY-001` - requires behavioral equivalence or typed waivers across harnesses.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - prevents assuming all harnesses expose identical skill or hook mechanics.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - routes durable evidence into governed artifacts instead of scratch state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps findings and follow-on decisions artifact-backed.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires clear disposition of new gaps, waivers, supersession, or follow-on work.

## Prior Deliberations

- `DELIB-202665197` - authorized the Harness Equivalence Phase 3 umbrella and child WI creation.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner-directed Batch C continuation authorization.
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ENFORCEMENT-GAP` - source context for cross-harness parity enforcement.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` - prior parity implementation authorization context.
- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - prior envelope-sharding closure and reuse context.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch C continuation.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4965-BATCH-C-20260705` - active authorization covering WI-4965.

## Proposed Scope

- Add a read-only helper that loads the generated skill projection and harness capability registry, then maps specialized activity envelopes to expected skills.
- Classify each harness/activity pair as covered, missing, weakly-evidenced, not applicable, or typed-waived, with evidence references.
- Emit a compact markdown evidence report for the Phase 3 backlog and bridge review surfaces.
- Add focused platform tests for parsing, mapping, classification, report rendering, and typed-waiver handling.

## Cross-Harness Disposition

The implementation reads cross-harness manifests and capability projections but does not change harness-specific skill files, hooks, or provider routes. Any unequal behavior must be reported as evidence, a typed waiver, or a follow-on work item candidate; it must not be hidden in code defaults.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm implementation report cites the active WI-4965 PAUTH and does not exceed target paths. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Confirm implementation starts only after GO and files a post-implementation report for LO verification. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use `gt bridge show gtkb-wi4965-skill-effectiveness-by-activity --json --compact` to confirm lifecycle state. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm required project linkage metadata is present. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run targeted tests and include exact command output in the implementation report. |
| `ADR-CROSS-HARNESS-PARITY-001` | Test that all configured harness lanes receive a classification or typed waiver. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Test that missing hook-native skill evidence is classified instead of assumed equivalent. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Confirm the report preserves evidence references and follow-on dispositions. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Confirm actionable gaps are represented as report dispositions rather than scratch notes. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm the report distinguishes new work, waiver, supersession, and no-op cases. |

## Acceptance Criteria

- The helper can run read-only and produce a compact Phase 3 skill-effectiveness report.
- The report includes activity-envelope rows for proposal, review, verification, bridge reconciliation, project/backlog, SoT query, session wrap, and harness parity activities.
- Each harness/activity row has evidence, status, and a typed waiver or follow-on disposition when coverage is incomplete.
- Tests cover registry/projection parsing, activity mapping, missing evidence, typed waivers, and markdown output.

## Risks / Rollback

Risk is moderate because the audit can influence later harness parity work. Mitigation is read-only implementation, explicit evidence references, and typed-waiver reporting.

Rollback is a revert of the helper, tests, and generated report. Bridge files and PAUTH records are append-only audit artifacts and must not be deleted.

## Files Expected To Change

- `scripts/harness_skill_effectiveness.py`
- `platform_tests/scripts/test_harness_skill_effectiveness.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-SKILL-EFFECTIVENESS-*.md`

## Recommended Commit Type

`feat`
