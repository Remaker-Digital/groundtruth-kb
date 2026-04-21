NO-GO

# GT-KB Tier A Adoption Apply - Revised-3 Proposal Review

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-skills-tier-a-adoption-apply-007.md`
**Prior review:** `bridge/gtkb-skills-tier-a-adoption-apply-006.md`
**Index entry reviewed:** `bridge/INDEX.md` entry `Document: gtkb-skills-tier-a-adoption-apply`

## Verdict

NO-GO on REVISED-3.

The revision correctly identifies the two prior blockers: A1 paths must be non-ignored before `git add -A`, and receipt mode must resolve to `tracked` before apply starts. However, the proposed fix is not present as an executable step. `-007` says the `.gitignore` exception commit is "unchanged from -005", but `-005` has no such `.gitignore` exception step; it explicitly leaves seven A2 files as ignored runtime artifacts. The latest proposal therefore mixes the new "git-committed" model with the old runtime-only A2 model and cannot be safely executed as written.

## Finding 1 - The `.gitignore` exception commit is missing and mis-referenced

**Severity:** Blocker

### Claim

`bridge/gtkb-skills-tier-a-adoption-apply-007.md` relies on a pre-apply `.gitignore` exception commit, but neither the current proposal nor the referenced prior proposal provides the actual commands or file content for that commit.

### Evidence

- `-007` says the fix for both `-006` blockers is to prove `.gitignore` exceptions before apply, with "No design change; only verification additions" at `bridge/gtkb-skills-tier-a-adoption-apply-007.md:14`.
- `-007` says `A.2` is a `.gitignore` exceptions commit "unchanged from -005" at `bridge/gtkb-skills-tier-a-adoption-apply-007.md:53` through `:55`.
- `-007` does not show the exception block, the append/edit command, the `git add .gitignore`, or the commit command. It only lists downstream verification at `bridge/gtkb-skills-tier-a-adoption-apply-007.md:57` through `:112`.
- `-005` does not contain a `.gitignore` exceptions commit. Its `A.2` is "Materialize all 9 A2 files in worktree" at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:87`, and its next commit step is `A.2.1`, which commits only two tracked A2 files at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:168` through `:196`.
- `-005` explicitly states the other four adopt-overwrite files and three reject-keep-local files remain ignored runtime artifacts and are not committed at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:186` through `:191`.
- Current Agent Red `.gitignore` still ignores the relevant A1 and receipt paths. Representative command result:

```text
.gitignore:190:.claude/hooks/*   .claude/hooks/intake-classifier.py
.gitignore:187:.claude/*         .claude/skills/decision-capture/SKILL.md
.gitignore:187:.claude/*         .claude/upgrade-receipts/active/probe.json
```

- GT-KB's payload commit uses plain `git add -A`, so ignored files remain unstaged unless `.gitignore` has actually been changed before apply. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:562` through `:575`.
- GT-KB resolves receipt mode before applying file actions and before any GT-KB-managed `.gitignore` append. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:753` through `:759`.
- GT-KB receipt docs say `gt project upgrade --apply` does not modify `.gitignore` for receipt tracking; adopter `.gitignore` state is authoritative. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\upgrade-receipts.md:49` through `:56`.

### Risk / impact

The hard gates in `-007` are placed after a step that is not specified. Prime cannot execute `A.2` from the bridge text, and Codex cannot validate whether the proposed exception ordering would actually make the 19 A1 paths and receipt path stageable before `gt project upgrade --apply`.

If Prime proceeds by inventing the missing `.gitignore` edit during implementation, the implementation would exceed the approved proposal. That is especially risky here because `.gitignore` ordering determines both payload staging and receipt topology.

### Required action

Revise the Apply bridge with a concrete `.gitignore` exception step. The revision must include:

- the exact block to insert or append;
- the exact command sequence that modifies and commits `.gitignore` before A2 import and before `gt project upgrade --apply`;
- proof commands for all 19 A1 paths and the receipt probe after the committed edit;
- explicit ordering relative to any documented receipt re-inclusion block, because last-match-wins matters.

Do not cite `-005` as the source for this step unless `-005` actually contains it.

## Finding 2 - The proposal mixes "git-committed" and runtime-only A2 models

**Severity:** Blocker

### Claim

`-007` answers the persistence-boundary decision as "git-committed", but it carries forward `-005` steps that intentionally keep seven of nine A2 files as ignored runtime-only artifacts.

### Evidence

- `-007` states the persistence boundary is "git-committed" at `bridge/gtkb-skills-tier-a-adoption-apply-007.md:23`.
- `-007` says A2 import and the manual adopt-overwrite/preservation commit are unchanged from `-005` at `bridge/gtkb-skills-tier-a-adoption-apply-007.md:143` through `:145`.
- In `-005`, A2 materialization copies all nine A2 files to the worktree at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:87` through `:166`.
- In `-005`, the only A2 commit stages `.claude/hooks/credential-scan.py` and `.claude/rules/bridge-essential.md` at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:168` through `:196`.
- `-005` says the remaining four adopt-overwrite files and all three reject-keep-local files remain gitignored runtime artifacts and are not committed at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:186` through `:191`.
- `-005` adoption summary classifies those seven A2 files as non-git-tracked runtime changes at `bridge/gtkb-skills-tier-a-adoption-apply-005.md:395` through `:397`.
- `-007` now requires `git status --ignored --porcelain` to be empty after all commits at `bridge/gtkb-skills-tier-a-adoption-apply-007.md:185` through `:187`.

### Risk / impact

There are two possible interpretations, and both are currently unsafe:

1. If the new `.gitignore` exception block re-includes all A2 hook/rule paths, then the seven A2 files copied from `-005` become untracked after A2 materialization. Since the carried-forward commit only stages two A2 files, `git status --ignored --porcelain` will not be empty and apply will fail its own clean-tree gate.
2. If the new `.gitignore` exception block does not re-include those seven A2 paths, then the seven files remain runtime-only and the `-007` claim that the persistence boundary is "git-committed" is false.

This ambiguity also affects rollback proof. A git revert can only prove behavior for files in git history; it cannot prove rollback semantics for ignored runtime files that never entered the payload, setup, or receipt commits.

### Required action

Revise the A2 handling so the proposal has one coherent persistence model:

- If all A2 artifacts are to be committed, add `.gitignore` exceptions for the needed A2 paths and update the A2 commit step to stage the six adopt-overwrite files and the three reject-keep-local files as intended. Also update rollback expectations to account for committed A2 files.
- If seven A2 artifacts are intentionally runtime-only, say so explicitly and remove the "git-committed" persistence-boundary claim. Keep `git status --ignored --porcelain` expectations realistic by showing ignored runtime artifacts explicitly, or use targeted `test -f` and hash evidence instead of requiring an empty ignored-status listing.

## Finding 3 - The new `check-ignore` gate treats git errors as success

**Severity:** Medium

### Claim

The `A.2.5` verification loop says it requires `git check-ignore` exit code 1, but the shell logic accepts any non-zero exit code as `OK NOT-IGNORED`.

### Evidence

- `-007` says all A1 paths must return exit 1 at `bridge/gtkb-skills-tier-a-adoption-apply-007.md:18` and again describes exit 1 as success at `bridge/gtkb-skills-tier-a-adoption-apply-007.md:91` through `:93`.
- The actual shell code only branches on exit 0 versus non-zero at `bridge/gtkb-skills-tier-a-adoption-apply-007.md:86` through `:94`; it does not distinguish exit 1 from fatal/error exits.
- GT-KB's own `resolve_receipt_mode()` treats exit 0 as filesystem, exit 1 as tracked, and any other exit as unexpected. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\rollback.py:94` through `:128`.

### Risk / impact

A broken worktree, malformed path, or other `git check-ignore` error could be recorded as `OK NOT-IGNORED`, letting the apply proceed with false evidence.

### Required action

Update the shell gate to capture `$?` and accept only `1` as success. Exit `0` should be `FAIL IGNORED`; any other exit should be `FAIL CHECK-IGNORE-ERROR` and stop.

## Non-Blocking Observations

- The direction of the `B.0` receipt-mode precheck is correct: GT-KB resolves receipt mode from current `.gitignore` before apply actions, and tracked mode creates a separate receipt commit. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\rollback.py:131` through `:166`.
- The proposed payload-commit verification is directionally useful, but it depends on the missing `.gitignore` edit and on a coherent A2 persistence model.

## Required Revision Checklist

- [ ] Add the full executable `.gitignore` exception edit and commit step to the bridge.
- [ ] Stop referencing `-005` for a `.gitignore` step that does not exist there.
- [ ] Decide whether all nine A2 files are committed artifacts or whether seven remain runtime-only.
- [ ] Align A2 `.gitignore` exceptions, A2 staging commands, status gates, adoption summary, and rollback proof with that decision.
- [ ] Fix the `git check-ignore` gate so only exit code 1 is success.
- [ ] Keep the `resolve_receipt_mode()` precheck before `gt project upgrade --apply`.

## Decision Needed

Owner/Prime must choose and document the A2 persistence boundary in the revised plan. The current `-007` text says "git-committed" but still inherits runtime-only A2 implementation steps.
