NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Whole-file reformat detector for source edits

bridge_kind: prime_proposal
Document: gtkb-wi4824-whole-file-reformat-detector
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4824

target_paths: [".editorconfig", "scripts/check_whole_file_reformat.py", "platform_tests/scripts/test_check_whole_file_reformat.py", "platform_tests/scripts/test_commit_foreign_verdict_bundling_guard.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Add a detector for whole-file whitespace/reformat churn where the whitespace-ignored diff is tiny compared with the raw diff. This proposal will be filed as `bridge/gtkb-wi4824-whole-file-reformat-detector-001.md`, an append-only numbered bridge file.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4824 records the source-edit churn class, and the active Harness Parity Phase 2 PAUTH includes WI-4824.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - source-edit discipline must hold across harnesses.
- `GOV-WORK-TREE-HYGIENE-001` - worktree hygiene should distinguish real changes from review-polluting churn.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner authorized Harness Parity Phase 2 implementation.

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active authorization covering WI-4824.

## Proposed Scope

- Add a read-only/pre-commit-capable detector that compares raw diff size to whitespace-ignored diff size.
- Add or align editor config only where it reduces future cross-harness churn.
- Add tests for acceptable formatting, suspicious whole-file churn, binary/generated exclusions, and threshold configuration.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Tests classify churn without deleting or reverting files. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Tests use harness-neutral diff inputs. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm live bridge lifecycle and append-only numbered file chain. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report includes exact targeted test output. |

## Acceptance Criteria

- Suspicious whole-file reformat churn is flagged with path, raw diff size, whitespace-ignored diff size, and threshold reason.
- Legitimate small edits and generated artifacts are not falsely blocked.
- No broad cleanup, revert, or formatting command is performed by this slice.

## Risks / Rollback

Risk is moderate because false positives can block useful edits. Mitigation is thresholded warning/fail modes and tests. Rollback is a revert of detector/config/tests.

## Files Expected To Change

- `.editorconfig`
- `scripts/check_whole_file_reformat.py`
- `platform_tests/scripts/test_check_whole_file_reformat.py`
- `platform_tests/scripts/test_commit_foreign_verdict_bundling_guard.py`

## Recommended Commit Type

`feat`
