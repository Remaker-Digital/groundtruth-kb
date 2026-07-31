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

# Implementation Proposal - Restore the artifact-decontamination dynamic-import contract residue

bridge_kind: prime_proposal
Document: gtkb-wi5423-artifact-dynamic-import-contract-finalization-repair
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5423

target_paths: ["groundtruth-kb/src/groundtruth_kb/gates.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Fresh exact-hunk finalization proposal after WI-5415 and WI-5457 reached independently VERIFIED commits; no semantic source change is proposed.

Work item description: Commit 42a252ab finalized the artifact-decontamination checker and frozen tests but omitted the four-line __gtkb_dynamic_import_contract__ declaration in groundtruth-kb/src/groundtruth_kb/gates.py. Against committed gates.py, the checker classifies _import_gate as an unresolved non-literal import; the current worktree declaration correctly records the owner-configured plugin boundary and runtime type-validation rationale. Independently review and finalize only that exact declaration hunk as WI-5142/WI-5347 residue. Exclude the artifact_lifecycle package, checker/tests, other gates.py behavior, dispatcher/harness state, groundtruth.db, and unrelated worktree content.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5423` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/gates.py`.

## Specification Links

- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - auto-linked governing or work-item specification.
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

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-5-EXECUTION-ENTRY-PACKET` - Gate 1.5 WI-5158 pilot execution entry packet
- `DELIB-20265684` - Loyal Opposition Verdict: VERIFIED finalization tolerates unrelated staged files
- `DELIB-202665701` - WI-4979 Work-Tree Hygiene Slice E - Auto-Resolve Actuator - Loyal Opposition Review
- `DELIB-20265762` - Loyal Opposition NO-GO Verification Verdict - WI-4723 VERIFIED finalization index-lock retry
- `DELIB-20263060` - Loyal Opposition Review - `/gtkb-propose` Scaffold Validation Gap Disposition

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5423`.

## Proposed Scope

- Finalize only the existing four-line __gtkb_dynamic_import_contract__ declaration for _import_gate in gates.py without semantic edits; current whole-file SHA-256 is DD86E9600570D7168614F231BB2A7DBBC8D8A319CB3AB4F6B0DDBCB676014864.
- The exact hunk identity is SHA-256 36965E770D3156EC1FD9E2DE3AE2BA7682127C71FC762B53EFF5337C6AFB343F, computed from git diff --no-ext-diff --no-color --unified=0 for the target path, lines joined with LF, trailing CR/LF trimmed, one LF appended, UTF-8 without BOM.
- Exclude every other path, any future gates.py hunk, the artifact_lifecycle package, checker/tests, bridge/dispatcher/TAFE/harness configuration, groundtruth.db, Git operations, and unrelated worktree content.

## Cross-Harness Disposition

- **Claude**: Not applicable: shared gates runtime metadata only; no Claude projection or configuration changes.
- **Codex**: Not applicable: shared gates runtime metadata only; no Codex projection or configuration changes.
- **Cursor**: Not applicable: shared gates runtime metadata only; no Cursor projection or configuration changes.
- **Antigravity**: Not applicable: shared gates runtime metadata only; no Antigravity projection or configuration changes.
- **Ollama**: Not applicable: shared gates runtime metadata only; no Ollama projection or configuration changes.
- **OpenRouter**: Not applicable: shared gates runtime metadata only; no OpenRouter projection or configuration changes.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5423; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Commit 42a252ab finalized the artifact-decontamination checker and frozen tests but omitted the four-line __gtkb_dynamic_import_contract__ declaration in groundtruth-kb/src/groundtruth_kb/gates.py. Against committed gates.py, the checker classifies _import_gate as an unresolved non-literal import; the current worktree declaration correctly records the owner-configured plugin boundary and runtime type-validation rationale. Independently review and finalize only that exact declaration hunk as WI-5142/WI-5347 residue. Exclude the artifact_lifecycle package, checker/tests, other gates.py behavior, dispatcher/harness state, groundtruth.db, and unrelated worktree content.",
  "after_behavior": "Fresh exact-hunk finalization proposal after WI-5415 and WI-5457 reached independently VERIFIED commits; no semantic source change is proposed.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5423",
    "project": "PROJECT-GTKB-TREE-STABILIZATION",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/gates.py"
    ],
    "linked_specifications": [
      "DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001",
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
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"
    ]
  },
  "expected_result": {
    "summary": "Fresh exact-hunk finalization proposal after WI-5415 and WI-5457 reached independently VERIFIED commits; no semantic source change is proposed.",
    "scope": [
      "Finalize only the existing four-line __gtkb_dynamic_import_contract__ declaration for _import_gate in gates.py without semantic edits; current whole-file SHA-256 is DD86E9600570D7168614F231BB2A7DBBC8D8A319CB3AB4F6B0DDBCB676014864.",
      "The exact hunk identity is SHA-256 36965E770D3156EC1FD9E2DE3AE2BA7682127C71FC762B53EFF5337C6AFB343F, computed from git diff --no-ext-diff --no-color --unified=0 for the target path, lines joined with LF, trailing CR/LF trimmed, one LF appended, UTF-8 without BOM.",
      "Exclude every other path, any future gates.py hunk, the artifact_lifecycle package, checker/tests, bridge/dispatcher/TAFE/harness configuration, groundtruth.db, Git operations, and unrelated worktree content."
    ],
    "acceptance_criteria": [
      "The target whole-file and normalized-hunk hashes remain exactly as recorded, and finalization stages only that four-line declaration.",
      "The combined artifact-lifecycle lane passes 25/25, proving _import_gate is declared with a nonempty rationale and no unresolved dynamic-import regression is introduced.",
      "Ruff check, Ruff format check, py_compile, applicability, ADR/DCL, target-coverage, clause, whitespace, and final staged-hunk identity checks pass before the implementation report and again before any separately authorized commit."
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
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Run platform_tests/scripts/test_modernization_artifact_decontamination.py and platform_tests/scripts/test_doctor_registry_dynamic_import_contract.py; require 25/25 pass plus exact whole-file and normalized-hunk hashes. |
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

- The target whole-file and normalized-hunk hashes remain exactly as recorded, and finalization stages only that four-line declaration.
- The combined artifact-lifecycle lane passes 25/25, proving _import_gate is declared with a nonempty rationale and no unresolved dynamic-import regression is introduced.
- Ruff check, Ruff format check, py_compile, applicability, ADR/DCL, target-coverage, clause, whitespace, and final staged-hunk identity checks pass before the implementation report and again before any separately authorized commit.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/gates.py`

## Recommended Commit Type

`feat`
