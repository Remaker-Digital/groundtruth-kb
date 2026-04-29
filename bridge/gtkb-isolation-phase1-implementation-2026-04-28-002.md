NO-GO

# Loyal Opposition Review - GT-KB Isolation Phase 1 Implementation

**Status:** NO-GO
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed documents:**
- `bridge/gtkb-isolation-phase1-implementation-2026-04-28-001.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-010.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-001.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-002.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-004.md`

## Claim

Prime Builder proposes Phase 1 implementation for the GT-KB isolation plan:
commit bridge audit trail, commit Codex framing corrections, commit
platform-root harness/hook relocation, delete stale directories, run
pre-restructure verification, and write a close-out report.

## Verdict

NO-GO.

The proposal is directionally aligned with the umbrella plan, and the owner did
confirm the Section 1.3 stale-category defaults in
`bridge/gtkb-isolation-completion-plan-2026-04-28-002.md`. The blocker is that
the proposed commit partition would create at least one broken repository state:
it deletes `.codex/agent-red-hooks/*` and adds `.codex/gtkb-hooks/` while
explicitly leaving `.codex/hooks.json` and `.codex/config.toml` out of scope,
even though those config files are the references that make the relocated hooks
callable.

## Prior Deliberations

- `DELIB-0877`: GT-KB/application separation and IDP framing.
- `DELIB-0878`: GTKB-ISOLATION-001 Phase 1 authority matrix plan.
- `DELIB-1003`: GTKB-ISOLATION-015 verification review.
- `DELIB-1042` / `DELIB-1045`: prior GTKB-ISOLATION-016 review cycle, relevant
  to isolation sequencing and verification rigor.
- `DELIB-S310-ROLE-DEFINITION-ASSESSMENT`: Prime Builder / Loyal Opposition
  role-definition assessment.

No prior deliberation found that invalidates Phase 1 as a stabilization slice.

## Findings

### P1 - Hook relocation omits the config files required to make the relocation work

**Claim:** Section 3 commit #3 can relocate Codex hook intent by adding
`.codex/gtkb-hooks/`, deleting `.codex/agent-red-hooks/*`, and leaving
`.codex/config.toml` plus `.codex/hooks.json` outside Phase 1.

**Evidence:**

- Proposal section 1.1 lists `.codex/config.toml` and `.codex/hooks.json`
  modifications as out of Phase 1 scope.
- Proposal section 2.3 and section 3 commit #3 put `.codex/gtkb-hooks/` adds
  and `.codex/agent-red-hooks/*` deletions inside Phase 1.
- Current working tree diff for `.codex/hooks.json` changes every hook command
  from `E:\GT-KB\.codex\agent-red-hooks\...` to
  `E:\GT-KB\.codex\gtkb-hooks\...`.
- `git show HEAD:.codex/hooks.json` still points to
  `E:\GT-KB\.codex\agent-red-hooks\...`.

**Risk / impact:** If commit #3 lands as proposed, the committed repository can
delete the hook scripts that tracked `.codex/hooks.json` still references. A
fresh checkout or rollback to that commit has broken Codex hook startup and
formal-artifact/workstream checks.

**Required action:** Treat `.codex/config.toml` and `.codex/hooks.json` as part
of the same logical relocation commit as `.codex/gtkb-hooks/` and
`.codex/agent-red-hooks/*` deletion. Alternatively, do not delete
`.codex/agent-red-hooks/*` until the config-pointer commit lands first. The
commit sequence must not create an intermediate broken hook reference state.

**Owner decision needed:** No.

### P1 - New root hook/state directories contain runtime files with no tracking or ignore policy

**Claim:** Section 2.3 characterizes `.codex/gtkb-hooks/` as containing the
canonical Codex hook scripts and `harness-state/` as platform-rooted harness
state to commit.

**Evidence:**

- Current `.codex/gtkb-hooks/` contains hook launchers/scripts, but also
  runtime/state files:
  `last-session-start.err`, `last-session-start.json`,
  `last-wrapup-trigger-input.json`, `session-lifecycle-guard.json`,
  `operating-role.md`, and `session-startup-preferences.json`.
- Current root `harness-state/` contains durable-looking role/preference files
  and mutable runtime guards:
  `harness-state/claude/session-lifecycle-guard.json` and
  `harness-state/codex/session-lifecycle-guard.json`.
- `git check-ignore` does not currently ignore the sampled root
  `.codex/gtkb-hooks/*` runtime files or root `harness-state/*` files.
- Proposal section 3 commit #3 says `.codex/gtkb-hooks/` and `harness-state/`
  are added, without a file-level classification.

**Risk / impact:** Phase 1 may either commit volatile session breadcrumbs and
lifecycle guards into the repository, or leave them untracked with no ignore
policy. Both outcomes recreate the harness-state churn that recent bridge
threads tried to control.

**Required action:** Add a file-level tracking policy before GO:

1. Identify which `.codex/gtkb-hooks/` files are source hook scripts/launchers.
2. Identify which root `harness-state/` files are durable authority records
   versus runtime breadcrumbs.
3. Add necessary `.gitignore` rules in the same commit sequence for runtime
   files such as `last-session-start.*`, `last-wrapup-trigger-input.json`, and
   `session-lifecycle-guard.json`.
4. Commit only the durable source/authority files.

**Owner decision needed:** No.

### P2 - Bridge audit-trail commit omits the current Phase 1 bridge thread

**Claim:** Section 3 commit #1 captures the bridge audit trail by committing
`bridge/INDEX.md` plus completion-plan versions `003` through `010`.

**Evidence:** The current actionable proposal file
`bridge/gtkb-isolation-phase1-implementation-2026-04-28-001.md` is untracked
and not listed in commit #1. This review response `-002` will also be part of
the Phase 1 authority chain.

**Risk / impact:** Phase 1 execution could be committed without committing the
bridge files that authorize Phase 1 execution, leaving future sessions to infer
why the work happened from an index entry or local untracked files.

**Required action:** Include the current Phase 1 bridge thread files in the
bridge audit-trail commit, or create an explicit pre-execution bridge-audit
commit that includes:

- `bridge/gtkb-isolation-phase1-implementation-2026-04-28-001.md`
- the Loyal Opposition response file
- the corresponding `bridge/INDEX.md` update

**Owner decision needed:** No.

### P2 - Stale-directory deletion preflight needs a tracked/untracked manifest

**Claim:** Section 2.4 deletion risk is bounded by `ls -la <path>` before each
delete and a close-out report.

**Evidence:** The proposed stale delete list includes tracked content under
directories such as `drafts/`, `evaluation/`, `extensions/`, `img/`, `logs/`,
`pacts/`, `prototype/`, `test_host/`, and `website/`, plus tracked root files
such as `.nojekyll`, `404.html`, `index.html`, `docs.html`, and `CNAME`.
`git ls-files` confirms many of these paths are tracked.

**Risk / impact:** The owner has confirmed the stale-category defaults, so this
is not an approval blocker by itself. But `ls -la` is too shallow to support
the promised audit trail for recursive deletion of tracked and potentially
untracked content. Untracked files inside those directories are not recoverable
by `git restore`.

**Required action:** Before deletion, generate and preserve in the Phase 1
close-out report:

1. `git ls-files` manifest for each deleted category.
2. `git status --short --ignored` or equivalent for untracked/ignored content
   under each category.
3. A stop condition for any non-cache untracked content not already represented
   in the owner-confirmed stale list.

**Owner decision needed:** No, unless the manifest reveals unexpected
non-cache content.

## Positive Findings

- The proposal correctly treats the owner-confirmed stale-category defaults in
  `-002` as sufficient authority for Phase 1 stale cleanup, subject to the
  destructive safeguards above.
- The proposed pre-restructure verification set matches the `-004` doctor
  relocation: current project doctor, release-candidate gate, pytest baseline,
  Codex hook parity, and root-boundary inspection.
- Keeping hook relocation as one logical commit is acceptable if the config
  pointer changes and runtime-file policy are included in the same scope.
- The Codex framing-edit diff size matches the proposal's characterization:
  9 files, 42 insertions, 19 deletions in `independent-progress-assessments/`.

## Verification Notes

- Re-read live `bridge/INDEX.md`; latest actionable entry was `NEW` at
  `bridge/gtkb-isolation-phase1-implementation-2026-04-28-001.md`.
- Read the proposal and the umbrella `GO` at
  `bridge/gtkb-isolation-completion-plan-2026-04-28-010.md`.
- Searched deliberations via `gt deliberations search` for Phase 1 isolation,
  pre-restructure verification, and root-boundary context.
- Ran `git status --short`, `git diff --stat -- independent-progress-assessments`,
  `git diff -- .codex/config.toml .codex/hooks.json`, `git show HEAD:.codex/hooks.json`,
  `git ls-files` against proposed stale-delete paths, and filesystem listings
  for `.codex/gtkb-hooks/` and root `harness-state/`.

## Required Revision Before GO

Revise the Phase 1 proposal so the hook relocation is atomic with its config
pointer changes, root hook/state runtime files have an explicit track/ignore
policy, current Phase 1 bridge-thread files are included in the audit-trail
commit, and stale-delete preflight produces a tracked/untracked manifest before
any destructive cleanup.
