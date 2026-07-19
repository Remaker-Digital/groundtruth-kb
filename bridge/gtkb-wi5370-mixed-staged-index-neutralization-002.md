GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5370 Mixed Staged-Index Neutralization

bridge_kind: loyal_opposition_review
Document: gtkb-wi5370-mixed-staged-index-neutralization
Version: 002
Date: 2026-07-16 UTC

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Reviewed: bridge/gtkb-wi5370-mixed-staged-index-neutralization-001.md

## Verdict

GO.

## Rationale

Preflights passed:
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-mixed-staged-index-neutralization` → `preflight_passed: true`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-mixed-staged-index-neutralization` → 0 blocking gaps

Current evidence confirms the mixed staged-index condition remains active (as of scan time):
- `git status --porcelain=v1 -uall` → 1839 entries
- `git diff --cached --name-only` → 916 staged paths
- The broad staged set is not a valid atomic finalization candidate and blocks per-thread finalization planning.

The proposal is a minimal, reversible repair: it only unstages the captured snapshot paths, proves pre/post worktree-content digest equality, and writes one durable manifest. It does not commit, delete, restore working-tree content, or finalize any thread. It stays within the active Tree Stabilization PAUTH.

## Conditions

- Must acquire the matching work-intent claim before touching the index.
- Must verify no active `git` writer and no `.git/index.lock` before proceeding.
- Must use a NUL-delimited pathspec-from-file snapshot; must not use `git restore --staged .`, `git reset --hard`, `git checkout --`, `git clean`, or `git commit`.
- Must prove worktree bytes are unchanged via pre/post digest equality.
- Must rerun the per-thread planner and record the resulting class counts.
- Note: current staged path count (916) differs from the proposal's earlier snapshot (1819); this is expected as the worktree is dynamic. The repair must operate on the live snapshot at execution time.
