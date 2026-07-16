NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; owner-directed repo-wide finalization repair; role authority from transcript ::init gtkb pb

# WI-5370 Proposal - WI-5299 Reissued Finalizer Failure Repair

bridge_kind: prime_proposal
Document: gtkb-wi5299-reissued-finalizer-failure-repair
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
target_paths: ["bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md", "independent-progress-assessments/WI-5299-deterministic-scratch-ignore-closure-004.reissued-finalizer-failure.md"]
Recommended commit type: chore:

implementation_scope: bridge-finalization-repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Problem Statement

WI-5321 repaired the first failed WI-5299 file-only VERIFIED artifact by
archiving the untracked `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md`
bytes and removing that bridge copy, returning WI-5299 to latest report 003
`NEW` for independent re-verification. Loyal Opposition then reissued a new
WI-5299 version 004 as an untracked `VERIFIED` bridge file, but the new file is
again not an atomic `write_verdict.py --finalize-verified` transaction.

Current observed reissued file evidence:

- Path: `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md`
- First token: `VERIFIED`
- Size: `2381` bytes
- SHA-256: `59EC58B71F0E9C2FCC14D6FA4A77B92A3AA2AD93DDCC70A94CE700FC60DFD5D2`
- Git blob: `ca8df9a91c4fcf046ff8a761088f97f6f4258c06`
- It does not contain `## Commit Finalization Evidence`.
- The auto-finalization sweep dry run skips it because the WI-5299 report and
  verdict chain do not form an eligible already-clean verdict-only transaction.
- The finalizer helper would also require a helper-compliant VERIFIED body with
  required evidence sections before creating the atomic source/test/report/verdict
  commit.

Leaving this second failed `-004` in place keeps WI-5299 terminal in bridge
state while its implementation source/test paths remain dirty, so the original
WI-5299 implementation cannot be re-reviewed through the required finalizer path.

## Requirement Sufficiency

Existing requirements sufficient. This proposal applies the established
per-thread failed-finalizer repair pattern to a concrete repeated WI-5299
failed reissue. No new or revised product, governance, bridge, or test
requirement is needed before implementation; the existing bridge authority,
worktree hygiene, VERIFIED finalization, project-authorization, and artifact
lifecycle requirements already determine the safe action.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

No new owner decision is requested. This proposal relies on the owner-directed
repo-wide sprawl-repair goal for WI-5370 plus the active Tree Stabilization
project authorization `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE`.
That PAUTH allows governed bridge/governance-evidence work while preserving the
normal independent GO, matching claim, implementation-start, report, and
independent verification gates. It forbids mechanical deletion beyond the exact
approved bridge artifact, broad Git capture, Git history rewrite, push, release,
deployment, credential lifecycle action, dispatcher mutation, and unrelated
worktree cleanup.

## Proposed Scope

Perform only the following two-path failed-transaction repair:

1. Copy `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md` to
   `independent-progress-assessments/WI-5299-deterministic-scratch-ignore-closure-004.reissued-finalizer-failure.md`.
2. Verify archive size, SHA-256, and Git blob hash match the source file.
3. Remove only the untracked bridge copy
   `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md` after the
   archive is verified.
4. Confirm `gt bridge show gtkb-wi5299-deterministic-scratch-ignore-closure --json --compact`
   returns latest path `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-003.md`
   and latest status `NEW`.
5. File an implementation report with the exact command and hash evidence.

## Explicit Non-Scope

This proposal does not authorize staging, committing, editing, deleting, or
rewriting `.gitignore`, `platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py`,
`bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-001.md`,
`bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-002.md`,
`bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-003.md`, Git history,
Git index state, dispatcher state, PAUTH records, credentials, release state,
or any unrelated worktree path.

The subsequent WI-5299 final VERIFIED transaction must be performed separately
by Loyal Opposition through `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
with a helper-compliant verdict body and an include set covering the verified
WI-5299 implementation/report/predecessor chain as required by the helper.

## Acceptance Criteria

- The archive path exists and has size `2381` bytes.
- The archive SHA-256 is `59EC58B71F0E9C2FCC14D6FA4A77B92A3AA2AD93DDCC70A94CE700FC60DFD5D2`.
- The archive Git blob hash is `ca8df9a91c4fcf046ff8a761088f97f6f4258c06`.
- `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md` does not exist after the archive verification.
- The WI-5299 bridge chain resolves to latest version 003 `NEW` after removal.
- No source, test, configuration, dispatcher, PAUTH, credential, release, Git history, or unrelated path is mutated.

## Specification-Derived Verification Plan

| Specification | Planned evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show gtkb-wi5299-deterministic-scratch-ignore-closure --json --compact` before and after removal proves the failed terminal file is archived and the original thread returns to report 003 `NEW`. |
| `GOV-WORK-TREE-HYGIENE-001` | `git status --ignored --short --untracked-files=all -- bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md independent-progress-assessments/WI-5299-deterministic-scratch-ignore-closure-004.reissued-finalizer-failure.md` proves the exact path effects. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Hash, blob, and bridge-state evidence proves this repair preserves evidence and enables a later helper-finalized WI-5299 VERIFIED transaction. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start validation must authorize exactly the two declared target paths after LO GO. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Archive path plus implementation report preserve why the invalid terminal artifact was removed. |

## Verification Commands

- `Get-FileHash -Algorithm SHA256 bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md`
- `git hash-object bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md`
- `Get-FileHash -Algorithm SHA256 independent-progress-assessments/WI-5299-deterministic-scratch-ignore-closure-004.reissued-finalizer-failure.md`
- `git hash-object independent-progress-assessments/WI-5299-deterministic-scratch-ignore-closure-004.reissued-finalizer-failure.md`
- `Test-Path bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md`
- `gt bridge show gtkb-wi5299-deterministic-scratch-ignore-closure --json --compact`
- `git status --ignored --short --untracked-files=all -- bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md independent-progress-assessments/WI-5299-deterministic-scratch-ignore-closure-004.reissued-finalizer-failure.md`

## Prior Deliberations

- `DELIB-202666332` - owner authorized exact local finalization repair of independently VERIFIED scopes while forbidding broad or unrelated capture.
- `DELIB-202666274` - project implementation authority preserves bridge, implementation-start, independent verification, and mechanical gates.
- `bridge/gtkb-wi5321-wi5299-failed-verified-finalization-repair-001.md` through `-008.md` - first failed WI-5299 file-only finalizer repair and verification.
- `docs/procedures/per-thread-finalization-repair.md` - current per-thread finalization repair runbook.
- `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-003.md` - original WI-5299 implementation report that must become latest again before valid finalizer reissue.

## Risk And Rollback

The main risk is losing evidence from the second failed `-004` file. The archive
hash and blob checks prevent that. If removal is later deemed premature, restore
the bridge file from the archive bytes and verify the same SHA-256 and Git blob
hash. Because the source bridge file is untracked, removal is not a Git history
rewrite, but it still must not occur until the archive is verified.

## Requested Loyal Opposition Review

Please verify whether this exact two-path archive/remove repair is authorized
and sufficient. If approving, issue `GO` only for the two declared `target_paths`
and explicitly preserve the non-scope boundaries above.
