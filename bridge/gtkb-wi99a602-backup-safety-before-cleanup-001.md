NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Backup safety before destructive cleanup

bridge_kind: prime_proposal
Document: gtkb-wi99a602-backup-safety-before-cleanup
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-ARTIFACT-ESSENTIALITY-PROJECTION-20260701
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-AUTO-SPEC-INTAKE-99A602

target_paths: ["config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/hygiene/strays.py", "groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py", "platform_tests/scripts/test_check_sot_registry_completeness.py", "platform_tests/scripts/test_worktree_finalization_triage.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Summary

Implement `SPEC-INTAKE-99a602`: cleanup/storage reclamation must not proceed from Git ignored/untracked status alone while reliable backup coverage is uncertain. The implementation should use the tracked SoT artifact registry and explicit preservation rules for essential local and non-committed artifacts before any cleanup classifier can mark paths safe.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-INTAKE-99a602` states the owner requirement, and the active PAUTH authorizes registry-first cleanup essentiality guardrails plus the required registry projection sync while forbidding destructive cleanup, broad file deletion, credential lifecycle, deployment, force-push, and secret-value disclosure.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `SPEC-INTAKE-99a602` - owner requirement that cleanup is high risk until backup/snapshot coverage is reliable and preservation rules are explicit.
- `SPEC-INTAKE-97538b` - companion artifact-essentiality requirement cited by the active PAUTH.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - requires current SoT evidence before cleanup classifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete spec links in the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.

## Prior Deliberations

- `INTAKE-b44907bd` - confirmed the backup-before-cleanup requirement.
- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` - owner approval for registry-first cleanup guardrails.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-ARTIFACT-ESSENTIALITY-PROJECTION-20260701` - active authorization covering this WI and projection sync.

## Proposed Scope

- Register essential local/non-committed artifacts in the SoT artifact registry or companion projection as needed.
- Remove Git-status-only essentiality assumptions from cleanup/stray classifiers.
- Make cleanup classifiers preserve registered essential artifacts by default.
- Add focused tests proving ignored/untracked status is insufficient to classify a path as safe for destructive cleanup.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-INTAKE-99a602` | Tests show cleanup safety requires registry/preservation evidence, not ignored/untracked state alone. |
| `SPEC-INTAKE-97538b` | Tests show registered essential artifacts are preserved by cleanup classifiers. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Registry completeness tests validate current SoT-backed artifact records. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm live bridge lifecycle state before implementation and after report filing. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Confirm no protected mutation occurs before GO and implementation-start. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Include exact targeted pytest output in the implementation report. |

## Acceptance Criteria

- Cleanup/stray classification never treats Git ignored/untracked state as sufficient proof of non-essentiality.
- Essential local artifacts have explicit registry-backed preservation behavior.
- Tests cover essential ignored artifacts, non-essential scratch artifacts, projection sync, and no broad deletion behavior.

## Risks / Rollback

Risk is moderate because cleanup guardrails affect future automation. Rollback is a revert of source/config/test changes; bridge files and PAUTH records remain append-only.

## Files Expected To Change

- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/hygiene/strays.py`
- `groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py`
- `platform_tests/scripts/test_check_sot_registry_completeness.py`
- `platform_tests/scripts/test_worktree_finalization_triage.py`

## Recommended Commit Type

`fix`
