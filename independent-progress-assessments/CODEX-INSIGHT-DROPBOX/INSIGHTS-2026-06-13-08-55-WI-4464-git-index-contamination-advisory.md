---
Specs: GOV-STANDING-BACKLOG-001, GOV-FILE-BRIDGE-AUTHORITY-001
WIs: WI-4464, WI-4443
Bridge: none
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-13 UTC
---

# WI-4464 Advisory: Shared Git Index Contamination Remains Live

## Claim

WI-4464 is still a live P1 git-workflow risk. The project has already recorded
one wrong-files commit and one orphaned concurrent-session commit from shared
index and shared-branch operations. The current worktree again shows unrelated
workstreams staged together, including bridge queue state, bridge files, hook
configuration, and an unrelated lint script. That state is enough to make a
plain `git commit` unsafe.

This report is advisory only. It does not implement git tooling, alter hooks,
resolve WI-4464, or request owner approval. It narrows the next Prime Builder
implementation proposal.

## Evidence

- Live MemBase query on 2026-06-13 returned `WI-4464` as `priority=P1`,
  `stage=backlogged`, `resolution_status=open`, `approval_state=unapproved`,
  with the change reason explicitly marking it as a strategic
  self-improvement candidate, not implementation approval.
- `memory/recovery-2026-06-11-fab20-commit-collision.md:45` records the
  mislabeled `772a186b` commit. Lines 58-59 record the `git reset HEAD~1`
  sequence that orphaned the concurrent Codex commit. Lines 121-126 preserve
  the durable lesson: commit with explicit pathspec, and do not reset on the
  shared branch while another session can commit.
- `memory/handoff-2026-06-11-pb-fab21-fable-program.md:123-126` repeats the
  same concurrency lesson and names `bridge/INDEX.md` plus `current.json` as
  shared single-slot surfaces.
- Live `git diff --cached --name-status` during this LO run showed six staged
  paths from multiple workstreams: `.claude/settings.json`, `.codex/hooks.json`,
  `bridge/INDEX.md`, `bridge/gtkb-tafe-subproject-prefix-reconciliation-003.md`,
  `platform_tests/scripts/test_advisory_grilling_gate_lint.py`, and
  `scripts/advisory_grilling_gate_lint.py`.
- Live `git diff --name-status` showed sixteen additional unstaged modified
  paths, including TAFE reconciliation code/tests, implementation-start-gate
  code/tests, inventory files, harness registry projection, and memory/rule
  surfaces. Several active `work_intent_claims` also existed at the time of the
  scan, including `gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening`,
  `gtkb-role-resolution-r1-r5-assertion-enforcement`,
  `gtkb-tafe-stage-attempt-telemetry`, and
  `gtkb-tafe-subproject-prefix-reconciliation`.

## Finding P1: Commit Safety Depends On Operator Memory

### Observation

The current repo state has unrelated staged paths before this advisory was
authored. The staged set mixes bridge workflow files, hook configuration, and a
new advisory lint script. The unstaged set simultaneously contains unrelated
implementation changes in source, tests, inventory, harness registry, and memory
surfaces.

### Deficiency Rationale

The historical failure and the current staged set have the same failure
mechanic: the Git index is a shared mutable surface across concurrent harness
work. A plain `git commit` commits the index, not the agent's intended logical
work unit. When hooks or other sessions stage files between tool calls, the
agent can produce a correct commit message with incorrect contents. A later
`git reset` on the shared branch then compounds the problem because `HEAD~1`
may refer to another session's commit, not the commit the operator intended to
undo.

This is not only a training problem. The repo already documents that the index
is not stable across tool calls, and the live state shows mixed staged content
again.

### Proposed Solution

Prime Builder should implement a small commit-safety layer before doing any
larger git-workflow redesign:

1. Add a repo-local safe commit helper that requires an explicit path list,
   snapshots `HEAD` before commit, prints the staged and pathspec-selected
   files, and refuses to proceed when unrelated files are staged unless the
   caller supplies an explicit allow flag.
2. Add a non-mutating pre-commit or wrapper check that warns on plain commits
   when the staged set contains `bridge/INDEX.md` or `bridge/*.md` plus files
   outside the declared pathspec.
3. Add a reset guard or documented recovery helper that warns when `HEAD` moved
   since the operator's last observed SHA, and directs recovery through reflog
   inspection rather than blind `git reset HEAD~1`.
4. Keep hook auto-staging changes out of the first slice. First make commit
   intent explicit and observable; then decide whether bridge auto-staging
   should be scoped or retired.

### Option Rationale

The wrapper/check-first option is the least disruptive path. It preserves
existing bridge and governance hooks while reducing wrong-files commits
immediately. Disabling auto-staging may be cleaner eventually, but it risks
breaking current bridge evidence flows and needs a broader hook review.
Moving all harnesses to separate worktrees would isolate the index more
strongly, but it is operationally larger and would interact with bridge,
MemBase, and ignored-local-state surfaces. A first slice that enforces explicit
commit intent is reversible and testable.

## Prime Builder Implementation Context

| Element | Guidance |
|---|---|
| Objective | Prevent wrong-files commits and unsafe shared-branch resets during concurrent harness work. |
| Preconditions | File a bridge proposal for WI-4464 before source/config changes. Preserve existing staged and unstaged work; do not normalize the current tree as part of the implementation. |
| Evidence paths | `memory/recovery-2026-06-11-fab20-commit-collision.md:45`, `:58-59`, `:121-126`; `memory/handoff-2026-06-11-pb-fab21-fable-program.md:123-126`; live `git diff --cached --name-status`. |
| File touchpoints | Likely `scripts/` for a safe commit helper, `.githooks/pre-commit` or adjacent hook config for advisory checks, and `platform_tests/scripts/` for tests. Exact paths should be proposed through the bridge. |
| Implementation sequence | Start with read-only detection and tests, then add the helper, then add the advisory guard, then document the operator flow. Leave auto-staging redesign for a follow-on unless the first slice proves it unnecessary. |
| Verification steps | Unit tests for mixed-index detection, pathspec-required behavior, bridge-file mixed-stage warnings, and stale-HEAD reset warning. Add a temp-repo integration test if existing test utilities support it. |
| Rollback notes | Remove the helper/guard and revert docs. No MemBase mutation is required for the first slice. |
| Open decisions | None for this advisory. Owner approval would be needed only if Prime Builder wants to resolve WI-4464 or mutate formal governance artifacts. |

## Commands Executed

```text
python .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
```

Observed result: bridge scanner functioning; one LO-actionable `NEW` existed,
but it was authored by Codex harness A and therefore skipped under the bridge
separation rule.

```text
git status --short --branch
git diff --cached --name-status
git diff --name-status
git diff --cached --stat
git diff --stat
```

Observed result: branch `develop` was ahead of origin and dirty; six paths were
already staged before this report, and sixteen additional paths were unstaged.
This report did not stage or commit those paths.

```text
SQLite read of current_work_items and work_intent_claims from groundtruth.db
```

Observed result: `WI-4464` remains open P1/unapproved; concurrent
work-intent claims were active for several bridge threads.

## Owner Action Required

None.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
