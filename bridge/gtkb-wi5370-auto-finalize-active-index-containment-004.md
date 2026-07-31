REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Revised Implementation Proposal - WI-5370 Metadata-Only Active Index/Lock Containment

bridge_kind: prime_proposal
Document: gtkb-wi5370-auto-finalize-active-index-containment
Version: 004
Supersedes: bridge/gtkb-wi5370-auto-finalize-active-index-containment-003.md
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Intent: bounded stale index-lock and staged-index metadata neutralization

target_paths: [".git/index", ".git/index.lock", "independent-progress-assessments/WI-5370-auto-finalize-active-index-containment-manifest.json"]

implementation_scope: git-index metadata | git-lock metadata | governance evidence manifest
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: chore

## Revision Reason

The version-003 GO correctly approved the broader containment concept, but implementation-start failed closed because `gtkb-wi5370-auto-finalize-sweep-invalid-body-guard` has a non-terminal implementation report claiming `.claude/rules/auto-finalization-sweep.md`. This revision narrows the immediate repair to the Git metadata residue only: stale `.git/index.lock`, the single auto-staged bridge verdict path, and the evidence manifest.

The source/rule/test clean-index/no-lock guard remains necessary, but it must wait for `gtkb-wi5370-auto-finalize-sweep-invalid-body-guard` to reach terminal status or otherwise release its shared target paths. This metadata-only phase prevents the stale lock and contaminated staged index from blocking or confusing that follow-on work.

## First-Line Role Eligibility Check

- Active transcript-defined role: Prime Builder via `::init gtkb pb`.
- Status authored here: `REVISED`, a Prime Builder proposal status.
- This revision does not author `GO`, `NO-GO`, or `VERIFIED` and does not mutate Git metadata before independent review.

## Current Evidence

- Version-003 GO exists but implementation-start failed with: `Peer implementation report conflict: bridge 'gtkb-wi5370-auto-finalize-sweep-invalid-body-guard' has a non-terminal implementation report that claims dirty path '.claude/rules/auto-finalization-sweep.md'.`
- `.git/index.lock` exists, is zero bytes, and has stable creation/last-write time `2026-07-16 17:40:33` local across repeated snapshots.
- `git diff --cached --name-only` reports exactly one staged path: `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md`.
- Recent process snapshots show no visible `auto_finalize_sweep.py` process, but concurrent repo activity exists; therefore no-writer snapshots remain mandatory immediately before mutation.
- The auto-finalizer source/rule/test guard is deliberately excluded from this revision to avoid the active peer-report conflict.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-202666332` - owner-authorized tree stabilization must preserve per-thread finalization provenance and avoid broad commits.
- `bridge/gtkb-wi5027-worktree-finalization-triage-001.md` through `-004.md` - resolved precedent for read-only classification before cleanup and fail-closed ambiguity handling.
- `bridge/gtkb-wi5370-mixed-staged-index-neutralization-001.md` through `-005.md` - governed staged-index neutralization precedent and manifest pattern.
- `bridge/gtkb-wi5370-auto-finalize-active-index-containment-001.md` through `-003.md` - broader containment proposal and GO; this revision narrows the executable phase after implementation-start exposed a peer target conflict.
- `bridge/gtkb-wi5370-auto-finalize-sweep-invalid-body-guard-001.md` through `-003.md` - non-terminal peer report that currently owns shared auto-finalizer source/rule/test paths.

## Requirement Sufficiency

Existing requirements are sufficient. The change is metadata containment and evidence preservation for a dirty Git state created by repository-local automation. No new product behavior or governance rule is introduced.

## Proposed Implementation Steps

1. Acquire a fresh GO implementation claim and run implementation-start for exactly `.git/index`, `.git/index.lock`, and the manifest path.
2. Run two process snapshots at least five seconds apart immediately before mutation. STOP if any `auto_finalize_sweep.py`, `git add`, `git commit`, `git update-index`, `git reset`, `git restore`, or other index-writing process is active in `E:\GT-KB`.
3. If `.git/index.lock` is absent, record no lock deletion. If present, require zero-byte size, unchanged metadata across both snapshots, no writer processes in both snapshots, and age greater than sixty seconds.
4. If the stale-lock criteria pass, remove only `.git/index.lock` and record pre/post metadata in `independent-progress-assessments/WI-5370-auto-finalize-active-index-containment-manifest.json`. STOP if any criterion fails.
5. Snapshot the staged index with `git diff --cached --name-only -z` after the lock condition is resolved. Require every staged path to be a bridge verdict file that the auto-finalizer staged. STOP if any source/config/database/harness path is staged.
6. If the staged set passes, unstage exactly the captured NUL-delimited paths with `git restore --staged --pathspec-from-file=<snapshot> --pathspec-file-nul`. Do not unstage anything not in the captured snapshot.
7. Record post-operation `.git/index.lock` absence, staged-index emptiness, and unchanged working-tree bytes for the unstaged verdict path in the manifest.
8. File an implementation report with process snapshots, lock metadata, staged snapshot hash, exact command evidence, and a fresh planner summary.

## Explicit Non-Goals

- Do not modify `scripts/auto_finalize_sweep.py`, `platform_tests/hooks/test_auto_finalize_verified_verdicts.py`, or `.claude/rules/auto-finalization-sweep.md` in this narrowed phase.
- Do not stage, commit, delete, or edit any working-tree source/config/database/harness file.
- Do not run a broad sweep commit, `git add -A`, `git reset`, `git clean`, or `git checkout`.
- Do not delete `.git/index.lock` if a writer exists or if lock metadata changes during the no-writer proof window.
- Do not stop dispatcher daemons, LO workers, test runs, bridge-backlog reconcilers, or unrelated processes.
- Do not finalize WI-5318 or any other terminal verdict as part of this metadata containment slice.
- Do not touch the concurrent WI-5320/WI-5328/WI-5330 dispatcher-starvation program.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Manifest records two no-writer snapshots, lock metadata, staged path snapshot, exact unstage operation, and post-repair status. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This revision waits for independent GO before any metadata mutation and does not author Loyal Opposition statuses. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Manifest preserves exact evidence for process/lock/index decisions rather than collapsing state into a broad cleanup. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Verification requires post-run planner summary proving direct finalization candidates are not fabricated by metadata cleanup. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The revision declares exact target paths and governing spec links. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH, project, work item, and target path metadata remain explicit. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start must authorize exactly the metadata target set before mutation. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The manifest and report preserve why stale Git metadata was touched and how the broader guard remains separate. |

## Acceptance Criteria

- `.git/index.lock` is absent after the operation, or the report explains why deletion was not needed.
- If the lock is removed, the report proves no index writer existed in two snapshots and that the removed lock was stale by the declared criteria.
- The staged index is empty after exact pathspec neutralization, or the report explains why the staged set was already empty.
- The working-tree bytes of `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md` are unchanged by the unstage operation.
- No source/config/database/harness path is staged, unstaged, deleted, or committed.

## Risk And Rollback

Risk is limited to Git metadata. Stale-lock deletion is allowed only when two no-writer snapshots and stable zero-byte lock metadata prove the lock is residue. Staged-index rollback is the pre-operation staged snapshot recorded in the manifest; because the operation only unstages, working-tree bytes remain available unchanged. The broader source/rule/test guard remains deferred to a separate terminal review path.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
