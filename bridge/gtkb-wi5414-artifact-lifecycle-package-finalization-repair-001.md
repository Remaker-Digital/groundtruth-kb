NEW
::init gtkb lo
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Restore the falsely closed WI-5347 artifact-lifecycle package residue

bridge_kind: prime_proposal
Document: gtkb-wi5414-artifact-lifecycle-package-finalization-repair
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5414

target_paths: ["groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py", "groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Fresh exact-byte finalization proposal after WI-5415 and WI-5457 reached independently VERIFIED commits; no semantic source change is proposed.

Work item description: Commit 42a252ab finalized only scripts/check_artifact_decontamination.py and platform_tests/scripts/test_modernization_artifact_decontamination.py from WI-5347. HEAD still lacks the implementation package, while the current worktree has exactly two untracked carriers: artifact_lifecycle/decontamination.py and artifact_lifecycle/__init__.py. Independently review and finalize the package bytes as the missing WI-5142/WI-5347 baseline residue, keeping WI-5406's later timeout hunk and unrelated project/check loader changes outside the transaction.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5414` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py`, `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py`.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - auto-linked governing or work-item specification.
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
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666387` - Loyal Opposition Verdict - GO - WI-5172 REVISED adopt evaluator + declare two generated skill-adapter MANIFESTs
- `DELIB-202666774` - WI-5370 Sprawl Reconciliation - Owner Decisions and Findings
- `DELIB-202666154` - WI-5200..5202 Narrow Harness Repair — Loyal Opposition Post-Implementation Verification
- `DELIB-202666275` - WI-5266 supplemental freshness dependency exception
- `DELIB-202666605` - LO Review - WI-5370 Finalizer Classification Invalid Terminal Verdict Reissue (Corrected GO)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5414`.

## Proposed Scope

- Finalize exactly the two pre-existing artifact_lifecycle package files without semantic edits; preserve SHA-256 A5AC3E15AE09D7485751E8329295717188B26F4026134983D671678BAA788DB3 for decontamination.py and BBEFD5CD37787094DFF954B01300447CEF171206CF0A776CE8EF72CFBCBA2A2D for __init__.py.
- Exclude gates.py, registry-discovery code, checker/tests, bridge/dispatcher/TAFE/harness configuration, groundtruth.db, Git operations, and all unrelated worktree content.

## Cross-Harness Disposition

- **Claude**: Not applicable: shared platform Python package only; no Claude projection or configuration changes.
- **Codex**: Not applicable: shared platform Python package only; no Codex projection or configuration changes.
- **Cursor**: Not applicable: shared platform Python package only; no Cursor projection or configuration changes.
- **Antigravity**: Not applicable: shared platform Python package only; no Antigravity projection or configuration changes.
- **Ollama**: Not applicable: shared platform Python package only; no Ollama projection or configuration changes.
- **OpenRouter**: Not applicable: shared platform Python package only; no OpenRouter projection or configuration changes.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5414; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Commit 42a252ab finalized only scripts/check_artifact_decontamination.py and platform_tests/scripts/test_modernization_artifact_decontamination.py from WI-5347. HEAD still lacks the implementation package, while the current worktree has exactly two untracked carriers: artifact_lifecycle/decontamination.py and artifact_lifecycle/__init__.py. Independently review and finalize the package bytes as the missing WI-5142/WI-5347 baseline residue, keeping WI-5406's later timeout hunk and unrelated project/check loader changes outside the transaction.",
  "after_behavior": "Fresh exact-byte finalization proposal after WI-5415 and WI-5457 reached independently VERIFIED commits; no semantic source change is proposed.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5414",
    "project": "PROJECT-GTKB-TREE-STABILIZATION",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py",
      "groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py"
    ],
    "linked_specifications": [
      "ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001"
    ]
  },
  "expected_result": {
    "summary": "Fresh exact-byte finalization proposal after WI-5415 and WI-5457 reached independently VERIFIED commits; no semantic source change is proposed.",
    "scope": [
      "Finalize exactly the two pre-existing artifact_lifecycle package files without semantic edits; preserve SHA-256 A5AC3E15AE09D7485751E8329295717188B26F4026134983D671678BAA788DB3 for decontamination.py and BBEFD5CD37787094DFF954B01300447CEF171206CF0A776CE8EF72CFBCBA2A2D for __init__.py.",
      "Exclude gates.py, registry-discovery code, checker/tests, bridge/dispatcher/TAFE/harness configuration, groundtruth.db, Git operations, and all unrelated worktree content."
    ],
    "acceptance_criteria": [
      "Both target files retain their recorded SHA-256 values and remain the only implementation targets.",
      "The combined artifact-lifecycle lane passes 25/25, including the frozen decontamination contract and doctor-registry dynamic-import contract.",
      "Ruff check, Ruff format check, py_compile, applicability, ADR/DCL, target-coverage, clause, and whitespace preflights pass before the implementation report."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
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
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Run platform_tests/scripts/test_modernization_artifact_decontamination.py and platform_tests/scripts/test_doctor_registry_dynamic_import_contract.py; require 25/25 pass with target hashes unchanged. |

## Acceptance Criteria

- Both target files retain their recorded SHA-256 values and remain the only implementation targets.
- The combined artifact-lifecycle lane passes 25/25, including the frozen decontamination contract and doctor-registry dynamic-import contract.
- Ruff check, Ruff format check, py_compile, applicability, ADR/DCL, target-coverage, clause, and whitespace preflights pass before the implementation report.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py`
- `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py`

## Recommended Commit Type

`feat`
