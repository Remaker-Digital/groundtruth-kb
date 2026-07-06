REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T01-44-20Z-prime-builder-A-492a96
author_model: GPT-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex headless bridge auto-dispatch; resolved role prime-builder; dispatch id 2026-07-06T01-44-20Z-prime-builder-A-492a96
author_metadata_source: codex-dispatch-explicit-runtime-envelope

# Implementation Proposal REVISED - Backup safety before destructive cleanup

bridge_kind: prime_proposal
Document: gtkb-wi99a602-backup-safety-before-cleanup
Version: 003 (REVISED after NO-GO 002)
Date: 2026-07-06 UTC
Responds to: bridge/gtkb-wi99a602-backup-safety-before-cleanup-002.md
Original proposal: bridge/gtkb-wi99a602-backup-safety-before-cleanup-001.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-ARTIFACT-ESSENTIALITY-PROJECTION-20260701
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-AUTO-SPEC-INTAKE-99A602
Related Work Item: WI-AUTO-SPEC-INTAKE-97538B

target_paths: ["groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py", "platform_tests/scripts/test_worktree_finalization_triage.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

This revision narrows `SPEC-INTAKE-99a602` follow-on implementation to the residual `auto_resolve.py` planning gap identified by Loyal Opposition in `-002`.

The already VERIFIED sibling thread `gtkb-artifact-essentiality-emergency-guardrails-reproposal` implemented the strays/registry surface for `SPEC-INTAKE-97538b` and mapped `SPEC-INTAKE-99a602` to passing registered-artifact preservation tests. This proposal does not reopen that verified path set. It hardens the separate WI-4979/WI-5027 report-only auto-resolve planner so a registered essential local artifact is classified for preservation before scratch/runtime-name heuristics can bucket it as junk or regenerated runtime state.

## Revision Claim

Prime Builder accepts the NO-GO findings in `bridge/gtkb-wi99a602-backup-safety-before-cleanup-002.md` and re-scopes the requested implementation accordingly:

- remove `config/registry/sot-artifacts.toml` from target scope;
- remove `groundtruth-kb/src/groundtruth_kb/hygiene/strays.py` from target scope;
- preserve the VERIFIED sibling thread as existing coverage;
- implement only the residual registry-first preservation check in `groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py`;
- add a focused regression test in `platform_tests/scripts/test_worktree_finalization_triage.py`.

No protected source or test mutation is authorized until Loyal Opposition records `GO` on this revised proposal and Prime Builder obtains the implementation-start packet.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-99a602` and `SPEC-INTAKE-97538b` state the owner requirement that cleanup and cleanup-planning surfaces must not treat ignored/untracked Git state as non-essentiality proof. The active PAUTH authorizes bounded reliability-fix implementation for this work item family, and the `-002` NO-GO identifies the precise residual implementation gap.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py`
- `platform_tests/scripts/test_worktree_finalization_triage.py`

No live dependency, artifact, or implementation path outside the project root is required.

## Already Verified Coverage

The sibling thread `bridge/gtkb-artifact-essentiality-emergency-guardrails-reproposal-008.md` is latest `VERIFIED` and covers the registry/strays implementation substance for the companion requirement family. Its verified path set includes:

- `groundtruth-kb/src/groundtruth_kb/hygiene/strays.py`
- `scripts/hygiene/stray_detector.py`
- related inventory, CLI, and strays tests

Its spec-to-test mapping explicitly maps:

- `SPEC-INTAKE-97538b` to registered artifact preservation tests; and
- `SPEC-INTAKE-99a602` to candidate-only dry-run behavior where registered artifacts return `preserve_registered_artifact` and no destructive cleanup runs.

This proposal therefore treats the strays/registry surface as already verified. The remaining WI-99A602 scope is defensive hardening of the separate report-only finalization triage planner.

## Finding Responses

### P1 - Stale premise / unacknowledged overlap with VERIFIED sibling

Response: closed in this revision. The proposal now cites the sibling `VERIFIED` thread and the owner-approved by-reference waiver. It explicitly distinguishes already VERIFIED strays/registry behavior from the remaining `auto_resolve.py` gap.

### P1 - Over-broad target_paths

Response: closed in this revision. `target_paths` is narrowed to:

- `groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py`
- `platform_tests/scripts/test_worktree_finalization_triage.py`

No registry TOML, `groundtruth.db`, strays source, stray detector source, or already verified test path is in implementation scope.

### P2 - Genuine residual gap is real but unnamed

Response: closed in this revision. The residual gap is now the named implementation target. `auto_resolve.classify_entry` currently checks bridge files, scratch markers, harness runtime projections, and protected paths, but it has no SoT registry preservation short-circuit. The implementation should load active SoT artifact records from `config/registry/sot-artifacts.toml`, match dirty paths against registered storage paths, and classify registered artifacts for preservation before scratch/runtime heuristics run.

The change remains report-only. It must not add staging, deletion, ignore mutation, cleanup, pruning, or other actuator behavior.

### P2 - Verification-record tension unaddressed

Response: closed in this revision by disposition choice (a) from `-002`: scope to the `auto_resolve.py` residual gap and note that the strays surface is already VERIFIED. `SPEC-INTAKE-99a602` remains open for this follow-on hardening only. After this narrowed implementation is verified, Prime Builder may separately reconcile WI/spec lifecycle closure or promotion through the normal governed path.

## Proposed Scope

Implement registry-first preservation in the report-only auto-resolve planner:

- Add a small SoT-registry loader in `auto_resolve.py` using the existing registry parser surface from `groundtruth_kb.project.sot_registry`.
- Match dirty relative paths against active registry record storage paths using normalized POSIX-style paths.
- In `classify_entry`, run the registry match after bridge-chain handling and before scratch/runtime/protected/manual heuristics.
- For registered matches, return a preservation bucket and candidate action that cannot map to destructive cleanup, untracked deletion, auto-ignore, or scratch deletion.
- Preserve existing report-only and forbidden-operation semantics.
- Add a test fixture registry under a temporary repo and assert an ignored/untracked registered artifact that looks scratch-like or runtime-like is classified for preservation, not `scratch_junk` or `harness_runtime_projection`.

## Out Of Scope

- Editing `config/registry/sot-artifacts.toml`.
- Editing `groundtruth.db`.
- Editing `groundtruth-kb/src/groundtruth_kb/hygiene/strays.py`.
- Editing `scripts/hygiene/stray_detector.py`.
- Retesting or re-implementing the already VERIFIED strays/registry implementation.
- Enabling live cleanup actuators, deletion, staging, ignore mutation, stash, prune, or broad status mutation.
- Changing credential lifecycle, backup implementation, deployment, release state, or dispatcher routing.

## Specification Links

- `SPEC-INTAKE-99a602` - cleanup/storage-reclamation must not proceed from Git ignored/untracked status alone while reliable backup coverage is uncertain; preservation rules for essential local/non-committed artifacts are required.
- `SPEC-INTAKE-97538b` - tracked artifact list is canonical for cleanup essentiality; Git tracked, ignored, or untracked state cannot decide that a file is unnecessary.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - cleanup classification must use current SoT evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Prime Builder may author `REVISED` after latest `NO-GO`; implementation still requires later `GO`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation authority is bounded to the active PAUTH/project/work item.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge GO or implementation-start authorization.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal carries PAUTH, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal cites concrete governing specs before implementation review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation report must map linked specs to executed test evidence before verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - cleanup-risk requirements and follow-on lifecycle choices are preserved as governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation decisions and residual gaps are handled through durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - distinguishes already verified coverage, residual work, future closure, and no-op dispositions.

## Prior Deliberations

- `INTAKE-b44907bd` / `SPEC-INTAKE-99a602` - owner requirement: no reliable GT-KB backup before destructive cleanup; ignored/untracked status is insufficient.
- `INTAKE-eb0bbcad` / `SPEC-INTAKE-97538b` - owner requirement: tracked artifact list is canonical for cleanup essentiality.
- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` - owner emergency authorization for registry-first cleanup guardrails.
- `DELIB-20260703-ARTIFACT-ESSENTIALITY-BY-REFERENCE-WAIVER` - owner-approved by-reference finalization waiver for the sibling verified thread.
- `bridge/gtkb-artifact-essentiality-emergency-guardrails-reproposal-008.md` - `VERIFIED` sibling thread that already covers the strays/registry implementation surface and maps `SPEC-INTAKE-99a602` to passing preservation evidence.
- `bridge/gtkb-wi99a602-backup-safety-before-cleanup-002.md` - Loyal Opposition NO-GO that narrows this thread to the `auto_resolve.py` residual gap.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-ARTIFACT-ESSENTIALITY-PROJECTION-20260701` - active authorization covering this reliability-fix work item family.
- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` - owner approval for registry-first cleanup guardrails.
- `DELIB-20260703-ARTIFACT-ESSENTIALITY-BY-REFERENCE-WAIVER` - owner waiver that closed the sibling thread by reference.

No new owner decision is required for this revision because the residual implementation target is inside the existing PAUTH and the `-002` NO-GO explicitly routes it back to Prime Builder for revision.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-INTAKE-99a602` | Add a focused auto-resolve test proving an ignored/untracked registered essential artifact is preserved before any scratch/runtime cleanup bucket can apply. |
| `SPEC-INTAKE-97538b` | The same test must use a temporary `config/registry/sot-artifacts.toml` record as the canonical essentiality source. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Test and implementation should load the current registry file from the inspected root, not cached Git status or hard-coded path lists. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm latest status is `GO` before implementation and file a post-implementation report after source/test changes. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run `scripts/implementation_authorization.py begin --bridge-id gtkb-wi99a602-backup-safety-before-cleanup` after `GO` and stay within target paths. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Confirm no protected source/test mutation occurred before `GO` and implementation-start evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability preflight confirms metadata and target paths are present. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight confirms `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must include exact test and ruff command outputs. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Implementation report must preserve the already-verified sibling coverage and any remaining lifecycle disposition. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Any new residual gap discovered during implementation must become a bridge/backlog artifact, not scratch memory. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verification report must separate already verified coverage, implemented residual hardening, and any future closure/promotion step. |

## Proposed Test Commands

After `GO` and implementation-start authorization, run:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_worktree_finalization_triage.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py platform_tests/scripts/test_worktree_finalization_triage.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py platform_tests/scripts/test_worktree_finalization_triage.py
```

## Pre-Filing Preflight Subsection

This revision is filed through `.codex/skills/bridge/helpers/revise_bridge.py file`, which runs:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi99a602-backup-safety-before-cleanup --content-file <candidate> --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi99a602-backup-safety-before-cleanup --content-file <candidate>
```

Expected result before live write:

- applicability preflight: pass; `missing_required_specs: []`; `missing_advisory_specs: []`
- clause preflight: pass; blocking gaps: 0
- credential scan: no credential-shaped content

## Acceptance Criteria

- `auto_resolve.classify_entry` preserves registered active SoT artifacts before scratch/runtime/protected/manual heuristics.
- A registered ignored/untracked artifact cannot be classified as `scratch_junk`, `harness_runtime_projection`, `auto_ignore`, or `auto_drop_byte_identical`.
- Report-only semantics remain intact: no live cleanup actuator is enabled.
- Existing worktree finalization triage tests continue to pass.
- The implementation report carries forward the sibling VERIFIED coverage and the exact focused test/ruff outputs.

## Risk And Rollback

Risk is low-to-moderate because the implementation changes planning classification for dirty paths. The intended bias is conservative preservation, so false positives should route more paths to manual/preserve handling rather than destructive action.

Rollback is a revert of the two target files after implementation. Bridge files remain append-only audit artifacts and must not be edited or deleted.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py`
- `platform_tests/scripts/test_worktree_finalization_triage.py`

## Recommended Commit Type

`fix`
