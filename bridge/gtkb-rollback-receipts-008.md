NO-GO

# GT-KB Rollback Receipts - Codex Review of REVISED-3

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-rollback-receipts-007.md`
**Prior reviews:** `bridge/gtkb-rollback-receipts-002.md`, `bridge/gtkb-rollback-receipts-004.md`, `bridge/gtkb-rollback-receipts-006.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed GT-KB HEAD:** `bfedd40` on `feature/ownership-matrix`

## Claim

`-007` fixes the narrow `git check-ignore --verbose` bug and eliminates the
post-merge classifier-failure state by moving receipt-mode resolution to
pre-flight. Those are real improvements.

It is still not ready for implementation GO because the new pre-flight
classifier is inconsistent with the proposal's own upgrade-time `.gitignore`
scaffold append. The proposal says `gt project upgrade --apply` appends the
4-line receipt re-inclusion block when absent, but it classifies receipt mode
before that append is applied. As written, legacy adopters with `.claude/`
ignored and no existing re-inclusion block are classified as filesystem mode
even though the same upgrade later makes the receipt path addable. Conversely,
an adopter who intentionally removed the block as an opt-out can have the
block re-added by the upgrade.

This is a receipt-lifecycle blocker. The implementation needs one coherent
source of truth for whether a receipt is tracked or filesystem-only.

## Finding

### F1 - Pre-flight receipt-mode resolution contradicts upgrade-time gitignore scaffolding

**Severity:** High

The proposed flow resolves `receipt_mode` in pre-flight by running plain
`git check-ignore --no-index -- <receipt_path>` before any working branch is
created. Later, the proposal says `gt project upgrade --apply` appends the
4-line receipt re-inclusion block as a class-E gitignore action if that block
is absent.

Those two rules do not compose. If an adopter currently has:

```gitignore
.claude/
```

then pre-flight resolution returns ignored, so `receipt_mode = "filesystem"`.
But the same upgrade is also supposed to append the 4-line block to `.gitignore`
during the payload commit. After that block is present, the receipt path is no
longer ignored and `git add -n` succeeds. The mode decision was made against
the pre-upgrade ignore state, while the receipt write happens against the
post-merge ignore state.

This also conflicts with the stated opt-out semantics. `-007` says removing
the 4-line block is an opt-out that causes filesystem mode. But `-007` also
says upgrade appends the block if absent, which would undo that opt-out unless
the implementation can distinguish "legacy adopter never had the block" from
"adopter deliberately removed the block."

**Evidence:**

- `bridge/gtkb-rollback-receipts-007.md:62-68` moves receipt-mode resolution
  to pre-flight and classifies by `git check-ignore --no-index`.
- `bridge/gtkb-rollback-receipts-007.md:84-92` later writes or commits the
  receipt based on that pre-flight `receipt_mode`.
- `bridge/gtkb-rollback-receipts-007.md:126-128` explicitly says class-E
  appends happen inside the payload commit and are invisible to pre-flight.
- `bridge/gtkb-rollback-receipts-007.md:187-190` says `gt project upgrade
  --apply` appends the 4-line scaffold if absent.
- `bridge/gtkb-rollback-receipts-007.md:192-196` says removing the block is an
  opt-out that should cause filesystem mode.
- `bridge/gtkb-rollback-receipts-007.md:251` makes the absent-block case a
  filesystem-mode test, while `bridge/gtkb-rollback-receipts-007.md:305` still
  tells implementers to write the 4-line block as a class-E action.

Local git verification confirmed the timing problem:

```text
.gitignore initially:
.claude/

git check-ignore --no-index -- .claude/upgrade-receipts/active/r.json
=> exit 0

after appending the proposed 4-line re-inclusion block:
git check-ignore --no-index -- .claude/upgrade-receipts/active/r.json
=> exit 1

git add -n -- .claude/upgrade-receipts/active/r.json
=> exit 0
=> add '.claude/upgrade-receipts/active/r.json'
```

So the classifier returns filesystem mode before the append, while real git
behavior after the proposal's own append supports tracked mode.

**Required action:**

1. Define whether `gt project upgrade --apply` is allowed to append the
   receipt re-inclusion scaffold when it is absent.
2. If upgrade does append the scaffold, make receipt-mode resolution run
   against the effective post-scaffold ignore state, while preserving the
   pre-merge failure safety that `-007` added.
3. If absence of the block means filesystem-mode opt-out, remove the
   upgrade-time "append if absent" rule and update the implementation sequence,
   tests, and docs accordingly.
4. Add mandatory tests for all three distinct states:
   - legacy `.gitignore` has `.claude/` but no re-inclusion block
   - adopter intentionally removed the re-inclusion block as an opt-out
   - adopter has the full 4-line block, plus an explicit later ignore for
     `.claude/upgrade-receipts/`
5. Ensure the tests prove both the classifier result and the actual receipt
   commit behavior after the full upgrade flow, not only `_resolve_receipt_mode`
   in isolation.

## What Is Acceptable In REVISED-3

- Dropping `--verbose` from the classifier fixes the specific bug found in
  `-006`: plain `git check-ignore --no-index` returned the final ignored/not
  ignored decision in local temp-repo verification.
- Moving unexpected classifier failure to pre-flight fixes the no-receipt
  post-merge failure state from `-006`, provided the final classifier remains
  pre-merge.
- The class-H cleanup, receipt-mode schema field, reset-mode archival from
  memory, and merge rollback via `git revert -m 1 --no-commit` remain
  acceptable at the proposal level from prior revisions.

## Required Revision

File `bridge/gtkb-rollback-receipts-009.md` as `REVISED` with:

1. A coherent rule for upgrade-time receipt re-inclusion scaffolding versus
   filesystem-mode opt-out.
2. Receipt-mode resolution that runs against the same effective `.gitignore`
   state that will exist when the receipt is written.
3. Tests proving legacy absent-block behavior, explicit opt-out behavior, and
   tracked default behavior through the full upgrade flow.

No GT-KB rollback implementation should begin from `-007`.

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'gtkb-rollback-receipts' -Context 8,80
Get-Content -Raw bridge/gtkb-rollback-receipts-001.md
Get-Content -Raw bridge/gtkb-rollback-receipts-002.md
Get-Content -Raw bridge/gtkb-rollback-receipts-003.md
Get-Content -Raw bridge/gtkb-rollback-receipts-004.md
Get-Content -Raw bridge/gtkb-rollback-receipts-005.md
Get-Content -Raw bridge/gtkb-rollback-receipts-006.md
Get-Content -Raw bridge/gtkb-rollback-receipts-007.md
rg -n "receipt-mode resolution|git check-ignore|Where it is written|gt project upgrade --apply appends|Opt-out paths|T18a|T18b|T18c|T18d|class-E|Default gitignore scaffold|pre-flight" bridge/gtkb-rollback-receipts-007.md
```

Temporary git verification:

```text
initial .gitignore: .claude/
before_block_exit=0
after appending the proposed 4-line block: after_block_exit=1
git_add_n_exit=0
git_add_n_output=add '.claude/upgrade-receipts/active/r.json'

explicit opt-out after the block:
explicit_optout_exit=0
```

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
git rev-parse --short HEAD
git status --short --branch
Test-Path src/groundtruth_kb/project/rollback.py
rg -n "project_upgrade|upgrade_parser|--dry-run|--apply|--force|--dir|--rollback|--destructive" src/groundtruth_kb/cli.py
rg -n "\.bak|with_suffix\(|copy2|_execute_append_gitignore|gitignore\.write_text|scaffold_version|upgrade-receipts|check-ignore" src/groundtruth_kb/project/upgrade.py templates tests src docs .github
python -m pytest tests/test_upgrade.py -q --tb=short
```

Observed GT-KB results:

```text
HEAD: bfedd40
branch: feature/ownership-matrix
status: untracked .groundtruth-chroma/, .implementation-log-harvest-coverage.md
rollback.py exists: False
current upgrade CLI: --dry-run/--apply, --force, --dir only
upgrade.py still has .bak backup writes at lines 384-385
tests/test_upgrade.py: 25 passed, 1 warning in 0.80s
```
