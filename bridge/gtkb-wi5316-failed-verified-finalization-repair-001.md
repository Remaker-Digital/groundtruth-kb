NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; owner-directed repo-wide finalization repair
author_metadata_source: explicit current Codex session metadata

# Implementation Proposal - WI-5316 failed VERIFIED finalization repair

bridge_kind: prime_proposal
Document: gtkb-wi5316-failed-verified-finalization-repair
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

Original Work Item: WI-5316 (already resolved by bridge-verified backlog reconciler; do not cite as active implementation authority)
Original Bridge Thread: gtkb-wi5316-frozen-modernization-rc-contract

target_paths: ['bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md', 'independent-progress-assessments/WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md']

implementation_scope: bridge-finalization-repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair failed terminal VERIFIED finalization residue for the frozen modernization release-candidate contract thread.

The original thread is latest `VERIFIED` at `bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md`, but the repo-wide per-thread finalization planner still reports its reviewed implementation paths as dirty or untracked. The terminal verdict file therefore appears to be a failed file-only finalization artifact rather than a valid governed finalization commit.

This child repair is intentionally narrow: archive the exact failed verdict bytes, remove only the failed untracked terminal verdict file, restore the original thread to latest `NEW` at `bridge/gtkb-wi5316-frozen-modernization-rc-contract-007.md`, and allow Loyal Opposition to reissue terminal `VERIFIED` through `.claude/skills/verify/helpers/write_verdict.py --finalize-verified` with the original reviewed implementation paths.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-WORK-TREE-HYGIENE-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` already define the required behavior: preserve per-thread provenance, avoid broad commits, retain exact artifact evidence, and route implementation mutation through GO plus implementation-start authority. No new or revised requirement is needed before this bounded repair.

## In-Root Placement Evidence

Both declared target paths are under `E:\GT-KB`: `bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md` and `independent-progress-assessments/WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md`. No out-of-root file is read as authority or written as an artifact.

## Failed Verdict Identity

- Failed terminal verdict: `bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md`
- First token: `VERIFIED`
- Size: `4721` bytes
- SHA-256: `6E890E22F3F57A59E89560610D5FD61E56EBB0B88BF37592B2AC900AAA0DB55B`
- Archive target: `independent-progress-assessments/WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md`
- Original implementation target paths awaiting real finalization:
- `config/governance/modernization-release-candidate.json`
- `platform_tests/scripts/test_modernization_release_candidate.py`
- `scripts/check_modernization_release_candidate.py`


## Proposed Repair Steps

1. After independent `GO`, acquire a `go_implementation` claim for this repair thread and create an implementation-start packet for exactly the two declared `target_paths`.
2. Recompute and record the failed verdict size and SHA-256 before mutation; they must match the values above.
3. Copy `bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md` byte-for-byte to `independent-progress-assessments/WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md`.
4. Verify the archive has the same byte length and SHA-256 as the failed verdict.
5. Remove only `bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md` from the worktree.
6. Verify `gt bridge show gtkb-wi5316-frozen-modernization-rc-contract --json --compact` now reports latest `NEW` at `bridge/gtkb-wi5316-frozen-modernization-rc-contract-007.md`.
7. File the implementation report for this repair thread. Do not mutate, stage, commit, restore, or rewrite any original implementation path.

## Out of Scope

- No source, test, configuration, database, dispatcher, harness-state, PAUTH, or backlog mutation.
- No broad bridge-chain commit, `git add -A`, stash/drop cleanup, reset, checkout, or history rewrite.
- No attempt by Prime Builder to author or re-author `VERIFIED` on the original thread.
- No finalization of the original implementation paths in this repair thread.

## Specification Links
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`


## Prior Deliberations

- `bridge/gtkb-wi5027-worktree-finalization-triage-004.md` - resolved precedent: do not bulk-commit ambiguous bridge/source sprawl; classify and preserve per-thread ownership.
- `bridge/gtkb-wi5116-per-thread-finalization-repair-001.md` through `-004.md` - current planner/runbook precedent for terminal VERIFIED repair classification.
- `bridge/gtkb-wi5321-wi5299-failed-verified-finalization-repair-*` - same bounded failed-verdict archive/remove/reissue pattern for a file-only terminal VERIFIED finalization artifact.
- `bridge/gtkb-wi5351-failed-verified-finalization-repair-*`, `bridge/gtkb-wi5345-failed-verified-finalization-repair-*`, and `bridge/gtkb-wi5211-failed-verified-finalization-repair-*` - sibling repair proposals filed under `WI-5370` because the original WIs were already resolved while their finalization artifacts remained dirty.

## Owner Decisions / Input

- Owner directive in this Codex task: `owner-directive:2026-07-16 keep working until the repo-wide uncommitted-file sprawl problem has been resolved`.
- `WI-5370` is the live umbrella work item created for resolved-WI failed VERIFIED finalization residue under `PROJECT-GTKB-TREE-STABILIZATION`.
- This proposal does not require a new owner decision because it requests no destructive cleanup and no source implementation mutation; it preserves the failed terminal artifact before removing only the untracked failed finalizer file.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Before/after scoped `git status --short -- <failed-verdict> <archive>` plus planner rerun showing the original thread no longer has a failed terminal verdict file. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show` proves this repair thread follows NEW -> GO -> NEW/VERIFIED lifecycle and the original thread reverts only by removing the failed untracked terminal file. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Archive SHA-256/size matches the failed verdict exactly; no claim is made over original source bytes. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Original thread must later be independently reissued through the governed finalizer; this repair does not author VERIFIED. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation-start packet must authorize exactly the two target paths before mutation. |

## Acceptance Criteria

- Failed terminal verdict is preserved byte-for-byte at the declared archive path.
- Only the failed terminal verdict file is removed from `bridge/`.
- The original thread latest status becomes `NEW` at its prior post-implementation report.
- No original source/test/config target path is mutated by this repair.
- A future independent Loyal Opposition reviewer can reissue `VERIFIED` through the canonical finalizer with the original implementation target paths.

## Files Expected To Change

- `bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md`
- `independent-progress-assessments/WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md`


## Recommended Commit Type

`fix`
