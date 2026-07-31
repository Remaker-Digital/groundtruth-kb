NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive; Prime Builder A; default reasoning configuration

# Implementation Proposal - Implement canonical-carrier closure and non-authority evaluator

bridge_kind: prime_proposal
Document: gtkb-wi5172-canonical-carrier-nonauthority-evaluator
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION
Work Item: WI-5172

target_paths: ["groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py", "groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py", "scripts/check_artifact_decontamination.py", "platform_tests/scripts/test_modernization_artifact_decontamination.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Governed adoption of the existing four-file WI-5172 canonical-carrier/non-authority evaluator candidate after exact-byte and 24-test baseline capture.

Work item description: Implement exact-one operative-rule carrier closure, carrier metadata validation, non-authoritative surface classification, invalid lifecycle/conflict failure, alias/projection routing to one mutation method, rule-gap promotion workflow, and active worker-loading independence from history. Work remains unapproved: no implementation, cleanup, or retirement may begin until bounded PAUTH, bridge GO, matching work intent, exact target paths, implementation-start evidence, and any separately required cleanup authority exist.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5172` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py`, `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py`, `scripts/check_artifact_decontamination.py`, `platform_tests/scripts/test_modernization_artifact_decontamination.py`.

## Specification Links

- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` - auto-linked governing or work-item specification.
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

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-CARRIER-EVALUABILITY-AUTHORITY-PAIR-RESULT` - Canonical-carrier and artifact-evaluability authority pair result
- `DELIB-20260710-GTKB-MODERNIZATION-CANONICAL-CARRIER-DCL-FORMALIZATION-RESULT` - Canonical-carrier non-authority DCL formalization result
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-FORMAL-LANGUAGE-DRAFT` - GT-KB Platform Modernization Gate 1 formal language draft
- `DELIB-202666217` - Loyal Opposition Proposal Review - WI-5163 Modernization Shadow Evaluation
- `DELIB-202666295` - Loyal Opposition NO-GO Verdict - WI-5254 PAUTH Amendment Evidence Preflight

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5172`.

## Proposed Scope

- Treat the exact current pre-start bytes and recorded SHA-256 hashes of the four untracked WI-5172 candidates as foreign implementation content pending independent review; do not regenerate or broaden them during adoption.
- Adopt only the canonical-carrier evaluator package, its deterministic checker, and its focused test; no cleanup, retirement, bridge-history rewrite, or unrelated artifact mutation is included.
- Require byte preservation from review through implementation report, release Ruff/format checks, and the complete focused test module before independent VERIFIED.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | Run the complete 24-test modernization artifact-decontamination module and the deterministic checker against its focused fixtures. |
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

## Acceptance Criteria

- The four candidate files remain byte-identical to their reviewed pre-start hashes.
- platform_tests/scripts/test_modernization_artifact_decontamination.py passes all 24 tests.
- The evaluator proves exact-one operative carrier closure and classifies non-authoritative surfaces without mutating governed artifacts.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py`
- `scripts/check_artifact_decontamination.py`
- `platform_tests/scripts/test_modernization_artifact_decontamination.py`

## Recommended Commit Type

`feat`
