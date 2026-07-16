NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5
author_model_version: Codex Desktop 2026-07-15
author_model_configuration: Interactive Codex Prime Builder; transcript role override

# Implementation Proposal - Run modernization shadow evaluation and calibrate activation thresholds

bridge_kind: prime_proposal
Document: gtkb-modernization-wi5163-shadow-evaluation
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5163-SHADOW-EVALUATION-20260715
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5163

target_paths: ["scripts/collect_modernization_semantic_evidence.py", "scripts/check_modernization_scope_semantics.py", "platform_tests/scripts/test_collect_modernization_semantic_evidence.py", "platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py", "platform_tests/scripts/test_modernization_scope_semantics.py", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/shadow-six-activities-primary-harnesses/**", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/activation-thresholds/**", ".gtkb-state/modernization-release-candidate/semantic-evidence/command-runs/zero-tolerance-hard-invariants/**"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Add a passive deterministic WI-5163 evaluator for genuine TAFE/bridge observations across six activities and applicable harnesses. MOD-AS10 requires complete provenance-bound coverage; MOD-AS11 produces recommendations only after baseline and zero-tolerance evidence. No routing, direct contact, synthesis, activation, or external mutation.

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"DELIB-20260715-WI5163-SHADOW-EVALUATION-PROPOSAL-AUTHORIZATION","canonical_authority":"GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"TAFE/bridge telemetry to collect_modernization_semantic_evidence status/collect","before_behavior":"AS10 has only a coarse incomplete-observation blocker.","after_behavior":"AS10 reports a typed six-activity harness matrix and accepts only genuine bound evidence.","self_descriptive_naming":"Frozen MOD-AS10 and MOD-AS11 receipt names identify purpose and lifecycle.","obsolete_guidance_disposition":"Add no alternate route; reject manual or direct-harness evidence.","history_preservation":"Keep bridge versions and receipt issue directories append-only.","baseline":{"source":"pre-modernization-baseline receipt","state":"AS10 blocked"},"expected_result":{"AS10":"complete matrix receipt","AS11":"non-activating threshold recommendation"},"rollback":{"instructions":"restore scoped collector/checker behavior via a governed change","verification":"rerun focused fail-closed tests"},"hard_invariants":["zero-tolerance suite passes","missing authority cannot pass"],"fail_closed_conditions":["missing cell","invalid session provenance","stale head or scope","synthetic or direct-contact evidence"],"essential_context_preservation":"Preserve activity profiles, harness applicability, session and bridge provenance, baseline, head, scope digest, and hard invariants."}
```


Work item description: Run report-only and shadow evaluation across six activities and applicable harnesses using the fresh-worker corpus, compare against baseline, and present evidence-calibrated thresholds for owner decision while preserving zero-tolerance hard invariants. No implementation may begin until applicable formal authority, bounded PAUTH, bridge GO, exact target paths, and implementation-start evidence exist.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5163` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/collect_modernization_semantic_evidence.py`, `scripts/check_modernization_scope_semantics.py`, `platform_tests/scripts/test_collect_modernization_semantic_evidence.py`, `platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py`, `platform_tests/scripts/test_modernization_scope_semantics.py`, `.gtkb-state/modernization-release-candidate/semantic-evidence/issues/shadow-six-activities-primary-harnesses/**`, `.gtkb-state/modernization-release-candidate/semantic-evidence/issues/activation-thresholds/**`, `.gtkb-state/modernization-release-candidate/semantic-evidence/command-runs/zero-tolerance-hard-invariants/**`.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` - auto-linked governing or work-item specification.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` - auto-linked governing or work-item specification.
- `DCL-ACTIVITY-CONTEXT-MANIFEST-001` - auto-linked governing or work-item specification.
- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` - auto-linked governing or work-item specification.
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260715-WI5163-SHADOW-EVALUATION-PROPOSAL-AUTHORIZATION` - Authorize bounded WI-5163 shadow-evaluation PAUTH and proposal
- `DELIB-20260710-FIRST-STABILIZATION-BATCH-APPROVAL` - First stabilization batch approved
- `DELIB-20260710-GTKB-MODERNIZATION-ASSURANCE-CHARTER` - Approve GT-KB Modernization Worker Intuitiveness and Program Assurance charter
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-0-RECONCILIATION` - GT-KB Platform Modernization Gate 0 reconciliation inventory
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-ASSURANCE-INVARIANT-PLAN` - GT-KB Platform Modernization Gate 1 assurance and hard-invariant plan

## Owner Decisions / Input

- `DELIB-20260715-WI5163-SHADOW-EVALUATION-PROPOSAL-AUTHORIZATION` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5163-SHADOW-EVALUATION-20260715` - active project authorization covering `WI-5163`.

## Proposed Scope

- Report the canonical ops, deliberation, build, test, spec, and project matrix for the applicable registry/waiver-derived harness set from genuine TAFE telemetry, bridge provenance, and session envelopes.
- Stay passive: report missing cells as BLOCKED; never route, invoke, contact, enable, or configure a harness, and never infer missing activity or mode evidence.
- Issue AS10 only for complete current-head provenance-bound coverage. Issue AS11 only after baseline, AS10, and zero-tolerance evidence; recommend thresholds without activation or WI-5164 scope.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Test baseline, hard-invariant, fail-closed, rollback, and non-activation behavior. |
| `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` | Test the exact six activities and reject inference. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ACTIVITY-CONTEXT-MANIFEST-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` | Accept genuine schema-valid telemetry; reject partial or unbound records. |
| `ADR-CROSS-HARNESS-PARITY-001` | Test registry/waiver-derived applicable harness coverage. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Test every receipt input is mechanically evaluable. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Block AS10/AS11 until WI-5152 through WI-5155 evidence is current. |

## Acceptance Criteria

- Read-only status emits the exact matrix, evidence refs, and typed gaps without mutation.
- AS10 binds every required cell to canonical telemetry/session hashes, current HEAD, and scope digest.
- Invalid, stale, incomplete, manual, direct-contact, synthetic, or backfilled inputs cannot pass.
- AS11 requires baseline, AS10, and zero-tolerance PASS and remains non-activating.
- Focused positive and negative tests pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/collect_modernization_semantic_evidence.py`
- `scripts/check_modernization_scope_semantics.py`
- `platform_tests/scripts/test_collect_modernization_semantic_evidence.py`
- `platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py`
- `platform_tests/scripts/test_modernization_scope_semantics.py`
- `.gtkb-state/modernization-release-candidate/semantic-evidence/issues/shadow-six-activities-primary-harnesses/**`
- `.gtkb-state/modernization-release-candidate/semantic-evidence/issues/activation-thresholds/**`
- `.gtkb-state/modernization-release-candidate/semantic-evidence/command-runs/zero-tolerance-hard-invariants/**`

## Recommended Commit Type

`feat`
