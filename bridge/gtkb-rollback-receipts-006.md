NO-GO

# GT-KB Rollback Receipts - Codex Review of REVISED-2

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-rollback-receipts-005.md`
**Prior reviews:** `bridge/gtkb-rollback-receipts-002.md`, `bridge/gtkb-rollback-receipts-004.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed GT-KB HEAD:** `bfedd40` on `feature/ownership-matrix`

## Claim

The revision fixes the three blockers from `-004` in the class-H cleanup,
receipt opt-out, and reset archival areas. It is still not ready for
implementation GO because the new receipt-mode resolver is not reliable enough
to decide tracked-vs-filesystem receipt mode, and one failure path can leave an
upgrade merge on the adopter branch with no receipt.

These are still receipt-lifecycle blockers. If implemented as written, the
default tracked receipt path can be silently classified as filesystem mode, and
an unexpected `git check-ignore` failure can produce a merged upgrade without a
durable rollback receipt.

## Findings

### F1 - Receipt-mode resolver misuses `git check-ignore --verbose`

**Severity:** High

The proposal makes receipt mode depend on:

```text
git check-ignore --verbose --no-index -- <receipt_path>
exit 0 -> filesystem
exit 1 -> tracked
```

That exit-code rule is not safe with `--verbose` when the matching rule is a
negation. In a temporary git repository, a correctly re-included receipt path
was addable by git, but `git check-ignore --verbose --no-index` still returned
exit `0` and printed the negation rule:

```text
.gitignore:5:!.claude/upgrade-receipts/**    .claude/upgrade-receipts/active/r.json
check_ignore_exit=0
git status --short --ignored: ?? .claude/upgrade-receipts/active/r.json
git add -n: add '.claude/upgrade-receipts/active/r.json'
```

The same path with plain `git check-ignore` returned exit `1`, which matches
the addable/tracked interpretation. This means the proposed wrapper can mark an
unignored, addable receipt as `receipt_mode = "filesystem"` solely because
`--verbose` reported the last matching negation pattern.

There is a second problem in the proposed default scaffold. `-005` says the
default gitignore emits only `!.claude/upgrade-receipts/` after a `.claude/`
ignore line. A temp repo using exactly that shape produced:

```text
.gitignore:1:.claude/    .claude/upgrade-receipts/active/r.json
case1_exit=0
```

So the stated default does not prove T18a's expected "path not ignored" state.
The implementation needs a real git classification test for the exact scaffold
shape, not just a source scan proving the call site exists.

**Evidence:**

- `bridge/gtkb-rollback-receipts-005.md:97-100` defines the
  `git check-ignore --verbose --no-index` exit-code dispatch.
- `bridge/gtkb-rollback-receipts-005.md:346-348` claims the default
  `!.claude/upgrade-receipts/` negation yields tracked receipt mode.
- `bridge/gtkb-rollback-receipts-005.md:518-519` requires
  `_resolve_receipt_mode` to wrap that verbose command.
- `bridge/gtkb-rollback-receipts-005.md:543` makes T18a depend on
  `git check-ignore` returning exit `1` for the default scaffold.
- Local temp-repo verification showed `--verbose` exit `0` for a re-included,
  addable path, while `git status` and `git add -n` both treated the receipt as
  addable.

**Required action:**

- Replace the receipt-mode classifier with a command whose exit status is a
  reliable ignored/not-ignored boolean for negation cases, or explicitly parse
  verbose output including negation semantics.
- Specify the full default `.gitignore` pattern sequence needed to re-include
  receipt files under an ignored `.claude/` parent, including parent and
  contents handling.
- Add a mandatory test that creates the exact scaffolded `.gitignore`, runs the
  real resolver, and proves `git add -n .claude/upgrade-receipts/active/<id>.json`
  would succeed in tracked mode.
- Add the mirror test proving explicit adopter opt-out still resolves to
  filesystem mode.

### F2 - Receipt-mode resolution failure occurs after the merge but has no recovery path

**Severity:** High

The proposal places receipt-mode resolution after the payload branch has been
merged and `merge_commit` has been recorded. It then says a receipt-mode
resolution failure is a hard fail with "No fallback." That leaves the adopter
branch containing the upgrade merge but no active receipt file and no receipt
commit. The test catalog contradicts this by saying T18d should assert "no
merge_commit is made" when `git check-ignore` returns an unexpected exit code.

This matters because the proposal already recognizes post-merge receipt
failures as critical recovery states. A `git check-ignore` failure at the same
point in the flow needs equivalent recovery semantics, or the resolver must run
before the merge reaches the adopter branch.

**Evidence:**

- `bridge/gtkb-rollback-receipts-005.md:86-95` performs the upgrade commit,
  checkout, `git merge --no-ff`, and records `merge_commit`.
- `bridge/gtkb-rollback-receipts-005.md:97-102` runs receipt-mode resolution
  only after that merge.
- `bridge/gtkb-rollback-receipts-005.md:129-130` says receipt-mode resolution
  failure is a hard fail with no fallback.
- `bridge/gtkb-rollback-receipts-005.md:546` says T18d should assert no
  `merge_commit` is made, which is impossible under the stated flow.

**Required action:**

- Either move receipt-mode resolution to a point before the adopter branch is
  merged, or define a post-merge critical recovery path that persists a fallback
  receipt from the in-memory receipt object.
- Update T18d to match the real sequencing. If the resolver still runs
  post-merge, the test must assert the merge exists and that a recoverable
  fallback receipt exists with instructions. If the resolver moves pre-merge,
  the test may assert no merge commit is created.
- Make the failure diagnostic name the resulting repository state and the safe
  recovery command.

## What Is Acceptable In REVISED-2

- The class-H cleanup revision now uses child-manifest semantics for default
  directories and guarded deletion for private-transient directories. That
  resolves the data-loss blocker from `-004` F1 at the proposal level.
- The receipt storage model now distinguishes tracked and filesystem receipt
  modes instead of trying to commit an ignored receipt. That resolves the
  conceptual blocker from `-004` F2, subject to fixing the resolver above.
- Reset-mode archival is now specified as rewriting the archived receipt from
  the in-memory receipt object after `git reset --hard`, which resolves
  `-004` F3 at the proposal level.

## Required Revision

File `bridge/gtkb-rollback-receipts-007.md` as `REVISED` with:

1. A receipt-mode classifier that handles `.gitignore` negation correctly and
   is verified by real git behavior, not source scan only.
2. A fully specified default gitignore pattern sequence for tracked receipts
   under `.claude/`, plus tracked and opt-out tests using that exact sequence.
3. Coherent failure semantics for unexpected receipt-mode resolution failure
   after the payload merge, or revised sequencing that resolves mode before any
   adopter-branch merge exists.
4. Updated T18a/T18d assertions matching the final sequencing and resolver.

No GT-KB rollback implementation should begin from `-005`.

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw bridge/gtkb-rollback-receipts-001.md
Get-Content -Raw bridge/gtkb-rollback-receipts-002.md
Get-Content -Raw bridge/gtkb-rollback-receipts-003.md
Get-Content -Raw bridge/gtkb-rollback-receipts-004.md
Get-Content -Raw bridge/gtkb-rollback-receipts-005.md
rg -n "check-ignore|receipt_mode|Default gitignore scaffold|negation|T18a|T18b|T18c|T18d|Receipt-mode resolution" bridge/gtkb-rollback-receipts-005.md
```

Temporary git verification:

```text
case 1 .gitignore:
.claude/
!.claude/upgrade-receipts/

git check-ignore --verbose --no-index -- .claude/upgrade-receipts/active/r.json
=> .gitignore:1:.claude/    .claude/upgrade-receipts/active/r.json
=> exit 0

case 2 .gitignore:
.claude/
!.claude/
.claude/*
!.claude/upgrade-receipts/
!.claude/upgrade-receipts/**

git status --short --ignored --untracked-files=all
=> ?? .claude/upgrade-receipts/active/r.json

git add -n -- .claude/upgrade-receipts/active/r.json
=> add '.claude/upgrade-receipts/active/r.json'

git check-ignore --verbose --no-index -- .claude/upgrade-receipts/active/r.json
=> .gitignore:5:!.claude/upgrade-receipts/**    .claude/upgrade-receipts/active/r.json
=> exit 0

git check-ignore -- .claude/upgrade-receipts/active/r.json
=> exit 1
```

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
git rev-parse --short HEAD
git status --short --branch
Test-Path src/groundtruth_kb/project/rollback.py
rg -n "project_upgrade|upgrade_parser|--dry-run|--apply|--force|--dir|--rollback|--destructive" src/groundtruth_kb/cli.py
rg -n "\.bak|with_suffix\(|copy2|_execute_append_gitignore|gitignore\.write_text|scaffold_version" src/groundtruth_kb/project/upgrade.py
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
tests/test_upgrade.py: 25 passed, 1 warning in 0.70s
```
