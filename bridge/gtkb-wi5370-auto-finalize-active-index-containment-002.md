REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Revised Implementation Proposal - WI-5370 Active Auto-Finalizer Index/Lock Containment

bridge_kind: prime_proposal
Document: gtkb-wi5370-auto-finalize-active-index-containment
Version: 002
Supersedes: bridge/gtkb-wi5370-auto-finalize-active-index-containment-001.md
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Intent: bounded active automation containment and stale index-lock neutralization

target_paths: [".git/index", ".git/index.lock", "scripts/auto_finalize_sweep.py", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py", ".claude/rules/auto-finalization-sweep.md", "independent-progress-assessments/WI-5370-auto-finalize-active-index-containment-manifest.json"]

implementation_scope: git-index metadata | git-lock metadata | hook automation guard | focused tests | governance runbook
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

## Revision Reason

Version 001 covered stopping a live `auto_finalize_sweep.py` process and neutralizing a mixed staged index, but it assumed `.git/index.lock` would disappear after the writer exited. Fresh evidence now shows a zero-byte `.git/index.lock` left behind after repeated auto-finalizer launches. This revision adds an explicit stale-lock repair path and makes the no-writer proof a hard precondition before any lock deletion.

## First-Line Role Eligibility Check

- Active transcript-defined role: Prime Builder via `::init gtkb pb`.
- Status authored here: `REVISED`, a Prime Builder proposal status.
- This proposal does not author `GO`, `NO-GO`, or `VERIFIED`, does not delete the lock, and does not unstage anything before independent review.

## Current Evidence

- `bridge/gtkb-wi5370-auto-finalize-active-index-containment-001.md` remains latest `NEW` and unreviewed as of the revision.
- The auto-finalizer relaunched from the Claude hook path after v001 was filed: observed command line `pythonw "$CLAUDE_PROJECT_DIR/scripts/auto_finalize_sweep.py"` and child `C:\Python314\pythonw.exe E:/GT-KB/scripts/auto_finalize_sweep.py`.
- `.gtkb-state/auto-finalize-sweep/sweep.jsonl` records new `planner_error` entries at `2026-07-17T00:44:09Z` and `2026-07-17T00:44:53Z` after the relaunch.
- `.git/index.lock` currently exists, is zero bytes, and was observed with creation and last-write time `2026-07-16 17:40:33` local.
- The currently staged set remains only `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md`.
- Process inspection found no visible `auto_finalize_sweep.py` process after the relaunch, but other repo activity exists; therefore stale-lock deletion must require two fresh no-writer checks immediately before mutation.

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
- `bridge/gtkb-wi5027-worktree-finalization-triage-001.md` through `-004.md` - resolved precedent for read-only classification before any cleanup and fail-closed handling of ambiguous dirty work.
- `bridge/gtkb-wi5116-per-thread-finalization-repair-001.md` through `-004.md` - current per-thread planner/runbook.
- `bridge/gtkb-wi5370-mixed-staged-index-neutralization-001.md` through `-005.md` - governed staged-index neutralization precedent; it was a no-op because the staged index was empty at execution time, but it established the manifest pattern.
- `bridge/gtkb-wi5370-auto-finalize-sweep-invalid-body-guard-001.md` through `-003.md` - current source/test/rule slice that guards the sweep against invalid terminal bodies.

## Requirement Sufficiency

Existing requirements are sufficient. The defect is operational containment of a repo-local finalization automation that is holding or leaving Git index metadata inconsistent with the per-thread finalization protocol. No new product requirement is introduced.

## Proposed Implementation Steps

1. Immediately before mutation, run two process snapshots at least five seconds apart and STOP if any `auto_finalize_sweep.py`, `git add`, `git commit`, `git update-index`, `git reset`, `git restore`, or other index-writing process is active in `E:\GT-KB`.
2. If a confirmed live `auto_finalize_sweep.py` process tree still exists, stop only that exact process tree and record process IDs/command lines in the manifest. Do not stop dispatcher, bridge review workers, tests, or unrelated processes.
3. Recheck `.git/index.lock`. If absent, record that no lock deletion was needed. If present, require: no writer processes in both snapshots, zero-byte lock, unchanged lock metadata across the snapshots, and lock age greater than sixty seconds.
4. If the stale-lock criteria pass, remove only `.git/index.lock` and record pre/post metadata in `independent-progress-assessments/WI-5370-auto-finalize-active-index-containment-manifest.json`. If any criterion fails, STOP without deletion.
5. Snapshot the staged index with `git diff --cached --name-only -z` after the lock condition is resolved. Require every staged path to be a bridge verdict file that the auto-finalizer staged. STOP if any source/config/database/harness path is staged.
6. If the staged set passes, unstage exactly the captured NUL-delimited paths with a pathspec-from-file operation. Do not unstage anything not in the captured snapshot.
7. Patch `scripts/auto_finalize_sweep.py` so a sweep refuses to start when the real index is pre-staged or `.git/index.lock` already exists, and audit-log the skip instead of running Git mutations.
8. Add focused coverage in `platform_tests/hooks/test_auto_finalize_verified_verdicts.py` for pre-existing staged index and pre-existing index-lock skip behavior.
9. Update `.claude/rules/auto-finalization-sweep.md` to state the clean-index/no-lock precondition.
10. File an implementation report with the process snapshots, lock metadata, staged snapshot hash, post-status evidence, focused test results, and dry-run planner output.

## Explicit Non-Goals

- Do not delete, move, or edit any working-tree source file except the listed auto-finalizer source, test, rule, and manifest paths after GO.
- Do not run a broad sweep commit, `git add -A`, `git reset`, `git clean`, or `git checkout`.
- Do not delete `.git/index.lock` if a writer exists or if the lock metadata changes during the no-writer proof window.
- Do not touch the concurrent WI-5320/WI-5328/WI-5330 dispatcher-starvation program.
- Do not stop dispatcher daemons, LO workers, test runs, or bridge-backlog reconcilers unless a future proposal specifically authorizes that operation.
- Do not finalize WI-5318 or any other terminal verdict as part of this containment slice.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Manifest records exact process snapshots, lock metadata, staged path snapshot, and post-repair status; no unrelated paths are changed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This revised proposal is Prime-authored and waits for independent GO before any mutation. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Manifest preserves exact evidence for process/lock/index decisions rather than collapsing state into a broad cleanup. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused tests prove the auto-finalizer skips when the real index is pre-staged or locked. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The proposal declares exact target paths and governing spec links. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH, project, work item, and target path metadata remain explicit. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start must authorize exactly the declared target paths before protected file edits. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The manifest and report preserve why stale Git metadata was touched and how rollback/verification work. |

## Acceptance Criteria

- If `.git/index.lock` is removed, the report proves no index writer existed in two snapshots and that the removed lock was stale by the declared criteria.
- The staged index is empty after exact pathspec neutralization, or the report explains why the staged set was already empty.
- `scripts/auto_finalize_sweep.py` refuses to mutate when the real index is pre-staged or locked.
- Focused tests pass for the new no-lock/clean-index preconditions and existing invalid-body skip behavior.
- No source/config/database/harness path outside the declared target list is staged, unstaged, deleted, or committed.

## Risk And Rollback

Risk is concentrated in Git metadata. The stale-lock deletion is allowed only when two no-writer snapshots and stable zero-byte lock metadata prove the lock is residue. Rollback for lock deletion is not byte-restoration; instead, the manifest preserves exact pre-removal metadata and the operation is validated by subsequent read-only Git status and tests. Script/rule/test edits can be reverted by a governed follow-up if LO verification fails.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
