NEW

# GT-KB Tier A Adoption - Current Main Integration Proposal

## Status

NEW - Loyal Opposition review requested.

## Claim

Prime Builder should supersede any direct merge of the verified `e1-apply`
branch with a fresh current-`main` integration path.

The prior `e1-apply` worktree remains useful evidence for the apply mechanism,
but it is based at `34905dc3` while the active Agent Red workspace is on
`main` at `707c2679`. A direct merge would delete later Agent Red governance,
Codex parity, and release-gate artifacts.

## Evidence

- `bridge/gtkb-skills-tier-a-adoption-apply-014.md` verified the original
  `e1-apply` branch and reported no blocking findings.
- `git -C E:/Claude-Playground/CLAUDE-PROJECTS/agent-red-e1-apply status
  --porcelain=v1 -b` returned only `## e1-apply`.
- `git merge-base main e1-apply` returned
  `34905dc35f664fc6f051345656a3c0cd26a41709`.
- Current workspace:
  - branch: `main`
  - head: `707c2679d8b2378e8b29ad7b09ecc1d1a96a6bfc`
  - `python -m groundtruth_kb --version` -> `gt, version 0.6.1`
- Current dry-run command:
  - `python -m groundtruth_kb project upgrade --dry-run --dir . --ignore-inflight-bridges`
  - Result: 45 actions total.
  - Mutating surface: 13 managed-file `ADD` rows, 4 event-hook merges into
    `.claude/settings.json`, and 4 `.gitignore` appends.
- Direct diff evidence:
  - `git diff --name-status main..e1-apply -- .claude .gitignore groundtruth.toml`
    shows deletions of current tracked artifacts including
    `.claude/hooks/formal-artifact-approval-gate.py`,
    `.claude/rules/codex-review-gate.md`,
    `.claude/skills/release-candidate-gate/SKILL.md`, and `.codex/hooks.json`.
  - The same scoped diff reports 60 files changed, 1605 insertions, and 4333
    deletions.
- Current workspace is dirty, so applying scaffold changes in-place would mix
  managed adoption writes with unrelated in-progress work.

## Scope In

1. Create a fresh integration branch or worktree from the current integration
   base after Loyal Opposition GO.
2. Re-run GT-KB v0.6.1 dry-run in that clean worktree.
3. Recompute the managed-file reconciliation surface against current `main`,
   not against the old `e1-apply` base.
4. Preserve later Agent Red-owned governance artifacts unless the refreshed
   reconciliation explicitly classifies them and the bridge review approves the
   disposition.
5. Apply the current missing managed hooks/rules, event-hook settings merges,
   and `.gitignore` appends only after the refreshed reconciliation is clean.
6. Preserve receipt and rollback evidence equivalent to the original verified
   apply thread.

## Scope Out

1. No direct merge of `e1-apply` into `main`.
2. No `gt project upgrade --apply` in the dirty current workspace.
3. No deletion of current Agent Red-owned `.claude` skills, rules, hooks, or
   Codex parity files unless a later reviewed bridge explicitly approves it.
4. No production deployment, credential lifecycle action, or release promotion.
5. No formal GOV, SPEC, PB, ADR, DCL, or Deliberation Archive mutation under
   this proposal.

## Proposed Implementation Plan

1. Create a clean integration worktree from current `main`, for example:

   ```powershell
   git worktree add ../agent-red-tier-a-main-apply -b gtkb-tier-a-main-apply main
   ```

2. In that worktree, run:

   ```powershell
   python -m groundtruth_kb project upgrade --dry-run --dir . --ignore-inflight-bridges
   ```

3. Run a full current-base managed-file reconciliation, including file-artifact
   rows that dry-run does not show when an existing file diverges.
4. Classify each row as:
   - managed add
   - settings merge
   - gitignore append
   - adopt-overwrite candidate
   - reject-keep-local / project-owned overlay
   - blocked pending owner decision
5. If no blocked rows remain, execute the current-base apply plan in the clean
   worktree. Prefer the GT-KB upgrade command if it preserves current-main
   artifacts; otherwise use a structured manual copy/merge plan and record why
   the package command is not safe for this base.
6. File the next numbered bridge report with the exact diff, receipt/rollback
   evidence, and verification results.

## Verification Plan

Required before requesting VERIFIED:

1. `python -m groundtruth_kb --version`
2. `python -m groundtruth_kb project upgrade --dry-run --dir . --ignore-inflight-bridges`
3. Current-base managed-file reconciliation table, including divergent existing
   files omitted by dry-run.
4. `git diff --name-status` proving no current Agent Red-owned governance or
   Codex parity artifact was deleted unexpectedly.
5. `.claude/settings.json` event-hook count/order validation.
6. `git check-ignore` probes for managed hooks, rules, skills, receipt files,
   bytecode, `groundtruth.db`, and `.groundtruth/`.
7. `python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short`
8. `python scripts/check_codex_hook_parity.py --project-root .`
9. `python scripts/release_candidate_gate.py --skip-frontend`
10. Clean-tree proof in the integration worktree after validation.
11. Rollback proof or receipt proof equivalent to the verified `e1-apply`
    thread.

## Loyal Opposition Review Questions

1. Is the stale `e1-apply` branch correctly treated as evidence, not as a direct
   merge candidate?
2. Are the proposed current-base preconditions sufficient to protect later
   Agent Red governance and Codex parity artifacts?
3. Should this proposal require an explicit owner decision before any
   adopt-overwrite row touches an existing current-main artifact?

## Decision Needed From Owner

None at proposal time. Owner input may become necessary if the refreshed
current-base reconciliation exposes a real conflict between GT-KB managed
templates and Agent Red-owned governance artifacts.
