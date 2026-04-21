GO

# GT-KB Tier A Adoption Apply - Revised-4 Proposal Review

**Status:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-skills-tier-a-adoption-apply-009.md`
**Prior review:** `bridge/gtkb-skills-tier-a-adoption-apply-008.md`
**Index entry reviewed:** `bridge/INDEX.md` entry `Document: gtkb-skills-tier-a-adoption-apply`

## Verdict

GO on REVISED-4 Apply implementation.

The proposal now has one coherent persistence model:

- committed on `e1-apply`: `.gitignore` policy expansion, 19 A1 governance artifacts, 6 A2 adopt-overwrite artifacts, settings merge, `.claude/hooks/*.log` gitignore append, and tracked rollback receipt;
- runtime-only in the worktree: 3 A2 reject-keep-local files (`assertion-check.py`, `destructive-gate.py`, `scheduler.py`), sourced from the main Agent Red workspace and deliberately left ignored.

The earlier blockers are addressed by putting the `.gitignore` policy commit before A2 materialization and before `gt project upgrade --apply`, proving the ignore surface with a 3-way `git check-ignore` gate, and proving tracked receipt mode before apply.

## Evidence

### 1. The latest proposal supplies the missing executable `.gitignore` step

`bridge/gtkb-skills-tier-a-adoption-apply-009.md:16` states the core design fix: a new `A.0` `.gitignore` policy commit before materialization or apply.

`bridge/gtkb-skills-tier-a-adoption-apply-009.md:121` through `bridge/gtkb-skills-tier-a-adoption-apply-009.md:171` provides the exact replacement block. It re-includes:

- all 19 A1 hook/rule/skill paths;
- all 6 A2 adopt-overwrite paths;
- `.claude/upgrade-receipts/**`;
- not the 3 reject-keep-local paths.

`bridge/gtkb-skills-tier-a-adoption-apply-009.md:174` through `bridge/gtkb-skills-tier-a-adoption-apply-009.md:183` provides the targeted edit, diff capture, `git add .gitignore`, and commit command.

Current Agent Red `develop` still has the narrow pre-Apply block at `.gitignore:187` through `.gitignore:195`, so the proposed A.0 policy commit is a real required precondition, not already-satisfied state.

### 2. The staged-file model now matches GT-KB implementation behavior

GT-KB stages payload changes with plain `git add -A`, not force-add. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:562` through `:570`. That means the proposal must make committed artifacts non-ignored before apply. REVISED-4 does that in `A.0`.

GT-KB missing-file repair skips files that already exist on disk. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:151` through `:172`. That supports the proposal's A2 materialization strategy: materialize all nine A2 files before the planner/apply phase so they do not appear as `add` actions.

GT-KB `UpgradeAction` exposes the target path as `.file`. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:48` through `:71`. The proposal's A.3 validation script correctly checks `a.file`, not the older mistaken `a.target`.

The GT-KB registry contains the relevant A1/A2 managed artifacts and the one gitignore pattern:

- A2 examples: `hook.assertion-check`, `hook.spec-classifier`, `hook.destructive-gate`, `hook.credential-scan`, `hook.scheduler` at `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\managed-artifacts.toml:29`, `:41`, `:65`, `:77`, and `:89`;
- A1 examples: governance hooks at `:53`, `:101`, `:202`, `:214`, `:226`, `:238`, and `:250`; governance rules at `:266`, `:290`, `:302`, `:314`, `:366`, and `:378`; skills at `:394`, `:406`, `:418`, `:430`, `:442`, and `:454`;
- gitignore pattern `.claude/hooks/*.log` at `:674` through `:676`.

### 3. Receipt topology now matches GT-KB implementation

GT-KB resolves receipt mode before applying file actions at `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:704` through `:759`.

`resolve_receipt_mode()` treats `git check-ignore` exit 0 as filesystem mode, exit 1 as tracked mode, and any other exit as an error. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\rollback.py:94` through `:128`.

Tracked receipts are committed after the merge by `write_receipt()`. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\rollback.py:131` through `:166`. `execute_upgrade()` then emits `RECEIPT tracked @ ...` at `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:797` through `:799`.

The GT-KB receipt docs confirm that adopter `.gitignore` state is authoritative and apply does not mutate `.gitignore` for receipt tracking. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\upgrade-receipts.md:45` through `:56`.

REVISED-4 aligns with that by adding the receipt re-inclusion before receipt mode is resolved and requiring `resolve_receipt_mode()` to return `mode='tracked'` at `bridge/gtkb-skills-tier-a-adoption-apply-009.md:299` through `:310`.

### 4. The execution target is currently available

Non-mutating availability checks:

```text
git branch --list e1-apply
<no output>

Test-Path '..\agent-red-e1-apply'
False
```

I did not create the proposed worktree during review. This scan's write scope remains limited to this bridge review file and the `bridge/INDEX.md` coordination update.

## Findings

No blocking findings remain.

## GO Conditions

Prime may implement `bridge/gtkb-skills-tier-a-adoption-apply-009.md` subject to these conditions, all of which are already expressed in the proposal:

1. Execute only in the new `../agent-red-e1-apply` worktree on branch `e1-apply`; do not mutate the main Agent Red workspace.
2. Land A.0 before A2 materialization and before `gt project upgrade --apply`.
3. Treat A.0.1 as a hard gate. Any A1/AO/RKL/receipt ignore-state failure or `FAIL CHECK-IGNORE-ERROR` requires STOP and a revised bridge.
4. Treat `resolve_receipt_mode() != tracked` as a hard gate.
5. After A2 materialization and A2 commit, the re-planner must show `A2 mutating violations 0` and counts `add=19, merge-event-hooks=3, append-gitignore=1`.
6. Apply stdout must include `RECEIPT tracked @`; if it reports filesystem receipt mode, STOP.
7. Payload proof must show the payload commit contains the 19 A1 files plus `.claude/settings.json` and `.gitignore`.
8. Rollback dry-run proof must show 19 `D` rows and 2 `M` rows, no A2 or receipt entries in plain status, and exactly three RKL `!!` rows in `--ignored` status.
9. Post-implementation report must include the evidence listed in `-009` §Post-Impl Report Contents, especially the ignore-state proof, receipt JSON, payload file list, rollback dry-run outputs, and main-workspace non-mutation SHA proof.

## Residual Risk

The three reject-keep-local files remain runtime-only artifacts. That is now an explicit owner-persistence decision rather than an accidental gap. The post-implementation report must make that limitation visible because recreating or deleting the worktree will require re-materializing those three files from the main workspace before repeating Apply.

## Decision Needed

No new owner decision is needed for implementation. If Mike rejects the committed-artifact persistence model or wants the three reject-keep-local files promoted into git history, that is a policy change and should be filed as a new revision before Apply runs.
