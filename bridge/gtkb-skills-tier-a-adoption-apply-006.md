NO-GO

# GT-KB Tier A Adoption Apply - Revised-2 Proposal Review

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-skills-tier-a-adoption-apply-005.md`
**Prior review:** `bridge/gtkb-skills-tier-a-adoption-apply-004.md`
**Index entry reviewed:** `bridge/INDEX.md` entry `Document: gtkb-skills-tier-a-adoption-apply`

## Verdict

NO-GO on REVISED-2 Apply implementation.

The revision correctly addresses the prior A2 worktree-root problem by materializing all nine A2 files before the planner/apply phase. However, it still assumes that ignored `.claude` artifacts and rollback receipts are committed by the GT-KB payload flow. Current Agent Red `.gitignore` and GT-KB implementation contradict that assumption.

Two blocker issues remain:

1. The 19 A1 `[ADD]` files are ignored by `.gitignore`, so GT-KB's `git add -A` payload commit will not stage them.
2. The receipt path is ignored by `.gitignore`, so GT-KB resolves filesystem receipt mode, not tracked receipt mode. The proposed HEAD/HEAD~1/HEAD~2 topology is therefore wrong.

## Finding 1 - The 19 A1 ADD files are ignored and will not be payload-committed

**Severity:** Blocker

### Claim

The revised proposal classifies the 19 A1 missing-file adds as git-tracked payload changes, but every one of those paths is currently ignored by Agent Red's `.gitignore`. GT-KB copies the files on disk, then commits with `git add -A`; it does not force-add ignored files.

### Evidence

- The proposal expects 19 `[ADD]` actions in the apply output at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:245` through `:250`.
- The post-implementation adoption summary classifies `A1 missing-file add | 19 | yes (payload)` at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:390` through `:399`.
- The rollback proof expects those 23 payload-managed rows, including the 19 adds, to appear in revert status at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:401`.
- Agent Red `.gitignore` ignores the `.claude` subtree except for a narrow set of re-included files. See `.gitignore:187` through `:195`:

```text
.claude/*
!.claude/settings.json
!.claude/hooks/
.claude/hooks/*
!.claude/hooks/poller-freshness.py
!.claude/hooks/credential-scan.py
!.claude/rules/
.claude/rules/*
!.claude/rules/bridge-essential.md
```

- `git check-ignore -v` against the 19 expected A1 add paths reports all 19 ignored. Representative full command result:

```text
IGNORED .claude/hooks/intake-classifier.py :: .gitignore:190:.claude/hooks/*
IGNORED .claude/hooks/scanner-safe-writer.py :: .gitignore:190:.claude/hooks/*
IGNORED .claude/hooks/_delib_common.py :: .gitignore:190:.claude/hooks/*
IGNORED .claude/hooks/turn-marker.py :: .gitignore:190:.claude/hooks/*
IGNORED .claude/hooks/delib-preflight-gate.py :: .gitignore:190:.claude/hooks/*
IGNORED .claude/hooks/owner-decision-capture.py :: .gitignore:190:.claude/hooks/*
IGNORED .claude/hooks/gov09-capture.py :: .gitignore:190:.claude/hooks/*
IGNORED .claude/rules/prime-builder.md :: .gitignore:194:.claude/rules/*
IGNORED .claude/rules/bridge-poller-canonical.md :: .gitignore:194:.claude/rules/*
IGNORED .claude/rules/prime-bridge-collaboration-protocol.md :: .gitignore:194:.claude/rules/*
IGNORED .claude/rules/report-depth.md :: .gitignore:194:.claude/rules/*
IGNORED .claude/rules/canonical-terminology.md :: .gitignore:194:.claude/rules/*
IGNORED .claude/rules/canonical-terminology.toml :: .gitignore:194:.claude/rules/*
IGNORED .claude/skills/decision-capture/SKILL.md :: .gitignore:187:.claude/*
IGNORED .claude/skills/decision-capture/helpers/record_decision.py :: .gitignore:187:.claude/*
IGNORED .claude/skills/bridge-propose/SKILL.md :: .gitignore:187:.claude/*
IGNORED .claude/skills/bridge-propose/helpers/write_bridge.py :: .gitignore:187:.claude/*
IGNORED .claude/skills/spec-intake/SKILL.md :: .gitignore:187:.claude/*
IGNORED .claude/skills/spec-intake/helpers/spec_intake.py :: .gitignore:187:.claude/*
```

- GT-KB's payload commit stages with plain `git add -A`, with no `-f` and no per-path force-add. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:562` through `:575`.
- GT-KB's file action execution copies templates to disk for `add` actions, then leaves staging to `_commit_payload()`. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:843` through `:861`.

### Risk / impact

If Prime executes the plan as written, the 19 A1 files will be materialized as ignored runtime files in the worktree, but they will not be present in the payload commit or merge commit. The proposal's "git-committed changes = 25" summary is therefore false; the payload commit would capture `.claude/settings.json` and `.gitignore` changes, not the 19 ignored A1 files.

The rollback proof is also wrong. A `git revert -m 1 <merge_commit>` cannot list the 19 ignored files as `D` because they were never in the merge commit. `git status --porcelain` can still appear clean because ignored runtime files are hidden, so the current verification gates can mask the failure.

### Required action

Revise the Apply plan to decide whether A1 missing files are intended to be committed artifacts or runtime-only worktree artifacts.

If they are intended to be committed, the plan must make them non-ignored before `gt project upgrade --apply` stages the payload, or use a GT-KB mechanism that force-adds the managed A1 files. The proposal must include evidence that `git check-ignore` reports the 19 A1 paths as not ignored at apply time, or that the implementation stages them despite ignore rules.

If they are intended to remain runtime-only, the proposal must reclassify the adoption summary, rollback proof, integration story, and verification gates accordingly. It must not claim the 19 A1 files are payload-committed.

## Finding 2 - Receipt mode resolves to filesystem, not tracked, so the proposed topology is wrong

**Severity:** Blocker

### Claim

The proposal expects a tracked receipt commit at `HEAD`, with the payload merge at `HEAD~1`. Current Agent Red `.gitignore` ignores `.claude/upgrade-receipts/active/*.json`, and GT-KB resolves receipt mode before any apply-time `.gitignore` mutation. The actual mode is filesystem, so no receipt commit is created.

### Evidence

- The proposal says commits include "the 23-action payload merge + the tracked-mode receipt" at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:62`.
- It expects `RECEIPT tracked @ <sha>` in apply output at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:245` through `:250`.
- It defines post-apply topology as `HEAD = receipt commit`, `HEAD~1 = merge commit`, and `HEAD~2 = adopt-overwrite commit` at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:252` through `:255`.
- It later lists a separate receipt commit in the commit plan at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:371` through `:380`.
- It requires receipt verification against `HEAD~1` at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:427` through `:429`.
- Current `.gitignore` ignores the receipt path through the same `.claude/*` rule:

```text
git check-ignore -v .claude/upgrade-receipts/active/probe.json
.gitignore:187:.claude/*    .claude/upgrade-receipts/active/probe.json
```

- GT-KB `resolve_receipt_mode()` treats an ignored receipt path as filesystem mode. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\rollback.py:94` through `:128`.
- Live resolution against the current Agent Red checkout returned:

```text
filesystem
receipt path is covered by .gitignore - filesystem mode
```

- GT-KB resolves receipt mode before creating the payload branch or applying any actions. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:753` through `:762`.
- In filesystem mode, `write_receipt()` writes the JSON file and returns without staging or committing. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\rollback.py:131` through `:152`.

### Risk / impact

The apply output will report `RECEIPT filesystem at ...`, not `RECEIPT tracked @ ...`. There will be no post-merge receipt commit. After apply, `HEAD` will be the merge commit, not a receipt commit; `HEAD~1` will be the merge's first parent, not the merge commit. The proposed capture commands and verification gates will therefore either fail or record the wrong SHAs.

This also affects rollback validation. The proposal's intended `MERGE_COMMIT=$(cat /tmp/e1-apply-merge.txt)` would read `HEAD~1`, which is not the merge commit in filesystem mode. A revert using that SHA would validate the wrong object.

### Required action

Revise the Apply plan to choose one receipt mode and make the topology match it.

If tracked receipts are required, the plan must add the documented receipt re-inclusion block to `.gitignore` before `gt project upgrade --apply` calls `resolve_receipt_mode()`, then prove with `git check-ignore --no-index` and `resolve_receipt_mode()` output that the receipt path is not ignored.

If filesystem receipts are acceptable, update the apply stdout expectation, commit plan, topology captures, receipt verification, and rollback command to use `HEAD` as the merge commit and to treat the receipt file as uncommitted filesystem evidence.

## Non-Blocking Observations

- The revised A2 materialization approach is directionally correct: GT-KB's missing-file planner uses `Path.exists()` and skips existing files, while same-version managed-file drift remains gated off. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:151` through `:178` and `:637` through `:701`.
- I did not create the proposed `../agent-red-e1-apply` worktree during this review because this scan's allowed write scope is limited to the new bridge review file and the targeted `bridge/INDEX.md` coordination update.

## Required Revision Checklist

- [ ] Decide whether the 19 A1 missing files are committed artifacts or runtime-only artifacts.
- [ ] If committed, make the 19 A1 paths stageable before `gt project upgrade --apply` runs, and prove they are not ignored or are force-staged.
- [ ] If runtime-only, update adoption summary, rollback proof, verification gates, and integration story so they do not claim payload commits include those files.
- [ ] Decide whether rollback receipts are tracked or filesystem.
- [ ] If tracked, add/prove the receipt-path `.gitignore` re-inclusion before `resolve_receipt_mode()` runs.
- [ ] If filesystem, update HEAD/HEAD~1/HEAD~2 topology and rollback commands accordingly.
- [ ] Add a verification command that shows ignored runtime artifacts explicitly, e.g. `git status --porcelain --ignored` or targeted `test -f` plus SHA evidence, because plain `git status --porcelain` hides the files at issue.

## Decision Needed

Owner/Prime must decide the intended persistence boundary for `.claude` managed artifacts in Agent Red: git-committed adoption versus runtime-only materialization. The current proposal mixes the two models and therefore cannot be safely executed as written.
