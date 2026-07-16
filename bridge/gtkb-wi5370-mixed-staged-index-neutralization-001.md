NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript role ::init gtkb pb; owner-directed repo-wide finalization repair
author_metadata_source: explicit current Codex session metadata and transcript role declaration

# Implementation Proposal - WI-5370 mixed staged-index neutralization

bridge_kind: prime_proposal
Document: gtkb-wi5370-mixed-staged-index-neutralization
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

target_paths: [".git/index", "independent-progress-assessments/WI-5370-staged-index-neutralization-manifest.json"]

implementation_scope: git-index metadata neutralization plus durable evidence manifest
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Neutralize the current mixed-provenance staged Git index without changing any working-tree file bytes, so the repo-wide finalization repair planner can return to per-thread classification and finalization.

The current repository state has a broad staged transaction of 1819 paths spanning bridge chains, source, tests, harness state, generated projections, scratch files, and deletes. That staged set is not a valid GT-KB atomic finalization candidate. It blocks the per-thread finalization-repair planner because terminal bridge verdicts now appear as tracked/staged modifications instead of independently attributable untracked or dirty per-thread artifacts.

This proposal authorizes only an index-only neutralization run: snapshot the staged path list, prove no live Git writer is active, unstage exactly the snapshot paths with a pathspec file, verify no working-tree content hashes changed, write one durable evidence manifest, and then rerun the per-thread planner. It does not authorize committing, deleting, reverting, restoring working-tree content, or finalizing any thread.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-WORK-TREE-HYGIENE-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` already require preserving per-thread provenance, refusing broad commits, using governed bridge authority for repair work, and staying inside the active Tree Stabilization PAUTH. No new requirement is needed for an index-only repair that preserves all file bytes and restores the ordinary planner input shape.

## In-Root Placement Evidence

All declared target paths are under `E:/GT-KB`: `.git/index` is the repository-local Git metadata file being neutralized, and `independent-progress-assessments/WI-5370-staged-index-neutralization-manifest.json` is the durable evidence manifest. No out-of-root file is read or written as authority.

## Current Evidence

- `git log -5 --oneline` shows HEAD latest `b1750002 fix(gtkb): WI-5116 per-thread finalization repair VERIFIED`; no later corrective commit has landed.
- `git status --porcelain=v1 -uall` currently reports `A=1524`, `D=66`, `M=228`, `MM=1`, `??=14`, total `1833` porcelain entries.
- `git diff --cached --name-only` reports `1819` staged paths.
- Cached top-level path counts include `harness-state=849`, `bridge=563`, `platform_tests=101`, `groundtruth-kb=64`, `scripts=48`, `.goose=41`, `.claude=24`, `.codex=21`, `.api-harness=13`, `.agent=12`, and `config=9`.
- `git diff --cached --stat --shortstat` reports `1819 files changed, 197639 insertions(+), 34299 deletions(-)`.
- `python scripts/per_thread_finalization_repair.py --format json --exclude-wi WI-5320 --exclude-wi WI-5328 --exclude-wi WI-5330` reports zero `terminal_verified_repair_candidate` entries and `mixed_provenance_stop=32`, with several terminal repair threads blocked by staged/tracked terminal verdict state.

## Proposed Repair Steps

1. After independent `GO`, acquire a work-intent claim for `gtkb-wi5370-mixed-staged-index-neutralization`.
2. Verify no live Git writer is active by inspecting `git.exe` process command lines. Read-only status/diff/log processes may exist; active `add`, `commit`, `restore`, `reset`, `checkout`, or index-lock writer processes must cause STOP.
3. Verify `.git/index.lock` does not exist. If it exists, STOP.
4. Snapshot staged paths using a NUL-delimited pathspec file under ignored runtime state, and compute a SHA-256 over the exact NUL-delimited staged path payload.
5. Compute a pre-run worktree-content digest for every staged path that currently exists in the working tree. Deleted working-tree paths are recorded as deleted markers, not restored.
6. Run `git restore --staged --pathspec-from-file=<snapshot> --pathspec-file-nul` to unstage exactly the snapshot paths. Do not use `git restore --staged .`, `git reset --hard`, `git checkout --`, `git clean`, `git add -A`, or `git commit`.
7. Compute the same post-run worktree-content digest for the same paths and require it to match the pre-run digest exactly.
8. Rerun `git status --porcelain=v1 -uall` and `python scripts/per_thread_finalization_repair.py --format json --exclude-wi WI-5320 --exclude-wi WI-5328 --exclude-wi WI-5330`.
9. Write `independent-progress-assessments/WI-5370-staged-index-neutralization-manifest.json` with the command transcript summary, staged path count, staged path payload hash, pre/post worktree digest hash, status class counts before/after, and STOP evidence if any check fails.
10. File an implementation report for this bridge thread. Do not stage or commit anything as part of this repair.

## Out of Scope

- No worktree file content restoration, deletion, checkout, reset, clean, or stash operation.
- No source/test/config/database/harness-state edits.
- No bridge verdict authoring by Prime Builder beyond the Prime implementation report for this repair.
- No finalization of any terminal VERIFIED thread.
- No broad commit, no `git add -A`, no sweep commit, no push, no release, and no dispatcher-state mutation.
- No mutation of the WI-5320/WI-5328/WI-5330 dispatcher-starvation handoff program.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`

## Prior Deliberations

- `bridge/gtkb-wi5027-worktree-finalization-triage-004.md` - resolved precedent for this failure class: do not bulk-commit ambiguous bridge/source sprawl; classify and preserve per-thread ownership.
- `bridge/gtkb-wi5116-per-thread-finalization-repair-001.md` through `-004.md` - current planner/runbook precedent; the planner now fails closed because the staged index makes terminal verdict ownership ambiguous.
- `docs/procedures/per-thread-finalization-repair.md` - live runbook requiring one-thread-at-a-time finalization and STOP on mixed provenance.
- `.claude/hooks/destructive-gate.py` - recognizes `git restore --staged .` as destructive-adjacent; this proposal therefore uses a pathspec-from-file snapshot instead of a dot pathspec and requires explicit evidence that worktree bytes are unchanged.

## Owner Decisions / Input

- Owner directive in Codex task `019f6bf6-3e6d-7761-be14-fb894a0e84d2`: keep working until the repo-wide uncommitted-file sprawl problem is resolved.
- Owner correction in the same task: role authority is transcript-defined for this interactive Prime Builder session and is not derived from `gt harness roles`. This proposal relies on the transcript `::init gtkb pb` role declaration for Prime status authority.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Manifest records staged path count/hash and proves pre/post worktree-content digest equality for every staged path that exists in the worktree. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge chain shows NEW -> GO -> implementation report -> LO verdict; Prime does not author GO/NO-GO/VERIFIED. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Manifest preserves exact staged path payload hash and command evidence instead of collapsing the staged set into a broad commit. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | After neutralization, rerun the per-thread finalization planner and record class counts; safe per-thread candidates, if any, remain separate follow-on actions. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Work begins only after GO and work-intent claim; implementation report records the claim/session and no protected worktree content mutation. |

## Acceptance Criteria

- The staged path list is captured before any index mutation and the capture hash is recorded.
- The index is neutralized only for the captured staged paths, preserving any later concurrent staging that was not in the snapshot.
- The worktree-content digest before and after the operation matches exactly.
- `git diff --cached --name-only` is empty after the operation, unless the manifest records residual staged paths from a concurrent writer and stops without further repair.
- The per-thread finalization planner is rerun after neutralization and no longer treats staged/tracked terminal verdicts as the reason for mixed-provenance STOP.
- No project source, test, config, database, harness-state, or bridge implementation payload is committed or reverted by this repair.

## Files Expected To Change

- `.git/index`
- `independent-progress-assessments/WI-5370-staged-index-neutralization-manifest.json`

## Recommended Commit Type

`fix`
