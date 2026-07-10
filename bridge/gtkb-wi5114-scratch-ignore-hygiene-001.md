NEW

# WI-5114: Normalize the Scratch Ignore Contract

bridge_kind: prime_proposal
Document: gtkb-wi5114-scratch-ignore-hygiene
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-10 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; resolved Prime Builder role

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-FIRST-WAVE-20260710
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5114

target_paths: [".gitignore", "platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py"]

implementation_scope: repository metadata and focused test addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Commit `fac6e892` introduced the intended WI-5114 scratch ignores for
`.harness-tmp`, `work_area`, `.loyal-opposition`, and bridge plus verification helper
scratch. The behavior is currently correct: focused regression testing and
direct `git check-ignore` probes both pass without deleting any local files.

The committed diff is not verification-clean, however. `git diff-tree --check
fac6e892^ fac6e892 -- .gitignore` reports CRLF whitespace on every changed hunk.
This proposal preserves the already-correct ignore coverage, normalizes the
tracked `.gitignore` content to the repository's LF form, and adds a focused
contract test covering the WI-5114 roots and helper scratch patterns. It does
not delete ignored, untracked, or runtime-state files.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - repository hygiene is report-first and
  non-destructive; ignore rules may remove scratch from status scans but do not
  authorize deleting the underlying files.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge proposal and its post-GO report
  remain the durable workflow record for this protected repository change.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the work stays inside the
  active tree-stabilization project's bounded authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the existing commit is
  not treated as a bridge bypass; the corrective mutation still requires GO,
  implementation-start authorization, reporting, and independent verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  links the applicable governance requirements before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - focused tests and
  whitespace checks provide executed verification for each linked behavior.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the corrected source, focused test,
  report, and terminal verification remain attributable governed artifacts.

## Prior Deliberations

- `DELIB-20260710-FIRST-STABILIZATION-BATCH-APPROVAL` - explicit owner
  approval for WI-5114's non-destructive stabilization scope.
- `DELIB-20260710-BACKLOG-DRIVE-AUTHORIZATION` - bounded first-wave project
  authorization and the continuing independent-LO workflow.

## Owner Decisions / Input

The owner explicitly approved this work in
`DELIB-20260710-FIRST-STABILIZATION-BATCH-APPROVAL`. The decision excludes
untracked-file deletion, destructive bulk cleanup, runtime-state deletion, and
committing unrelated dirty files.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-WORK-TREE-HYGIENE-001` supplies the
non-destructive hygiene boundary and the bridge and project requirements supply the
implementation and verification gates; no new or revised requirement is needed.

## Spec-Derived Verification Plan

| Governing surface | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py -q --tb=short --basetemp .harness-tmp/wi5114` | Representative pytest, work-area, LO, and helper scratch paths are ignored while no cleanup command is executed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Applicability and clause preflights plus the implementation-start packet | Proposal, GO, target-path scope, and reporting sequence remain intact. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused test plus `git diff --check -- .gitignore` and `git diff-tree --check HEAD^ HEAD -- .gitignore` after the scoped commit | Tests pass and the corrected commit has no whitespace errors. |

## Risk / Rollback

The risk is unintentionally broadening ignore coverage or changing a tracked
rule's meaning while normalizing line endings. The focused contract test names
only the approved scratch classes, and the implementation keeps all other
ignore rules byte-for-byte equivalent. Rollback is one scoped revert of the
`.gitignore` normalization and its test; local scratch files are never touched.

## Bridge Filing

Filing creates the next append-only numbered bridge file for this document; no
prior version is deleted or rewritten. The governed writer publishes the file
and its dispatcher/TAFE state, which remain the live workflow record.

## Recommended Commit Type

`fix` - this corrects the verification-breaking line-ending defect in the
existing WI-5114 repository-hygiene change while preserving its behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
