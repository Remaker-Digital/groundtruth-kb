NEW
::init gtkb lo
::open build

# WI-6280 — Widen VERIFIED closure coverage to ancestor commits

bridge_kind: prime_proposal
Document: gtkb-wi6280-verified-closure-ancestor-coverage
Version: 001
Author: Prime Builder (harness B, claude)
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: a49752e4-5a9f-4290-bceb-910693b5271f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword
Date: 2026-08-14 UTC

Work Item: WI-6280
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730

target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler_ancestor_coverage.py", "groundtruth.db"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

This proposal DOES mutate MemBase: scope item 4 runs the reconciler with
`--apply`, which resolves eligible work items. `groundtruth.db` is declared in
`target_paths` accordingly.

---

## Summary

65 work items whose bridge threads are terminal `VERIFIED` cannot auto-resolve,
because `_terminal_verdict_commit_coverage` requires the implementation
`target_paths` to appear in the **same commit** as the terminal verdict. Work
committed before the verdict — which is the normal shape, and the shape the
owner-authorized auto-finalization sweep mandates — never satisfies it.

This proposal widens the coverage rule to accept implementation paths committed
in an **ancestor** of the verdict commit, then applies the reconciler.

## Problem

`scripts/bridge_verified_backlog_reconciler.py` line 445:

```python
missing = [path for path in (verdict_rel_path, *target_paths)
           if not _target_covered_by_commit(path, changed_paths)]
```

`changed_paths` is the changed-path set of the single commit that last touched
the verdict file. Every implementation path is tested against that one commit.

Two governed mechanisms disagree about whether that is achievable:

1. `.claude/rules/file-bridge-protocol.md` § "Mandatory VERIFIED
   Commit-Finalization Gate" requires one transaction containing "the verified
   implementation/report paths; and the new `VERIFIED` verdict artifact".
2. `.claude/rules/auto-finalization-sweep.md` (WI-4889, owner-authorized
   `DELIB-20266278`) states invariant "**Verdict-file only** — the sweep commits
   only `bridge/*.md` files; it never stages source or test files", and gates
   eligibility on the implementation being **already committed** separately.

A thread finalized under (2) can never satisfy (1)'s coverage check, and commit
history does not change, so the block is permanent.

### Measured

`bridge_verified_backlog_reconciler.py --dry-run`, live DB, 2026-08-14:
399 candidates; 14 resolve. Skip reasons: `linked_bridge_not_verified` 304,
**`missing_implementation_commit_coverage` 65**, `no_related_bridge_threads` 11,
`missing_parent_evidence` 3, `no_action_verified` 2.

### Worked example

`WI-6221`, thread `gtkb-wi6221-tool-use-is-a-test-directive`, terminal
`VERIFIED`, parent evidence present, all four versions matched.

- `0e770e89d` "finalize … VERIFIED chain" — the four bridge files, nothing else.
- `33e387a78` — `.harness-baseline-configuration/rules/governance-principles.md`
  and `.goose/rules/governance-principles.md`, the implementation.

Coverage reports `covered: false` with those two paths as `missing_paths`.
`WI-6267` fails identically. Both are implemented, verified and committed, and
both read as `open` / `backlogged`.

Only 2 commits in history match the sweep's finalization message pattern, so the
sweep is the clearest governed instance of this shape, not its only source; any
workflow committing implementation before the verdict produces it.

## Scope

1. **Widen target-path coverage to ancestors.** In
   `_terminal_verdict_commit_coverage`, an implementation `target_path` is
   covered when EITHER it appears in the verdict commit's `changed_paths` (today's
   rule, unchanged) OR it is tracked and the commit that last touched it is an
   **ancestor of, or equal to, the verdict commit**.

2. **The verdict file's own rule does not change.** `verdict_rel_path` must still
   appear in the verdict commit. The existing `uncommitted_or_untracked`,
   `no_containing_commit` and `commit_inspection_failed` early returns are
   untouched.

3. **Ancestry, not mere presence.** A path whose latest commit is NOT an ancestor
   of the verdict commit — i.e. committed after verification, or on an unrelated
   branch — remains uncovered. This is the load-bearing constraint: accepting
   any committed path would admit work the verification never saw. Implemented
   via `git merge-base --is-ancestor <path_commit> <verdict_commit>`, results
   memoized per (path_commit, verdict_commit) pair.

4. **Apply.** After the tests are green, run
   `bridge_verified_backlog_reconciler.py --apply` and record the resolved set in
   the implementation report.

Out of scope: the `by_reference_waiver` path (line 523) is left exactly as-is;
`--repair-overbroad`; the `linked_bridge_not_verified` class (304 items, a
different question); any change to either governed rule's text.

## Project Re-Homing Disclosure

`WI-6280` was first created under `PROJECT-GTKB-GET-HEALTHY-PHASE-2`, because
that is the program the defect blocks. It is filed here under
`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` instead, and the reviewer should
scrutinise that move rather than take it as given.

Grounds: the subject matter is the bridge protocol's VERIFIED-closure path
(`bridge_verified_backlog_reconciler.py` implementing
`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`), not Phase-2 baseline or
projection work. The three sibling defects found in the same investigation --
`WI-6277`, `WI-6278`, `WI-6279` -- were filed to this project on the same
grounds earlier today. Phase 2 is the *victim* of the defect, not its scope.

Material consequence, stated plainly: the Phase-2 authorization
(`PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814B`) is include-listed and does not
name `WI-6280`, so filing there would have required an owner authorization
amendment. This project's authorization is list-free whole-project, so no
amendment is needed. That difference makes the re-home *convenient*, which is
exactly why it is disclosed: if the reviewer judges the work to be Phase-2
scope, the correct path is an owner-approved include-list amendment, not this
filing, and this proposal should be NO-GO'd on that ground.

Membership was created via `gt projects add-item` with the same rationale
recorded as the change reason.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — the governance this
  reconciler implements, and which is currently not firing for 65 items.
- `GOV-STANDING-BACKLOG-001` v5 — the backlog is the work authority; completed
  work that cannot leave it makes the authority overstate remaining work.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — the audit-trail property the same-commit
  rule was protecting; the ancestry constraint preserves it.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — every figure above is a fresh
  measurement against the live DB and git history, cited by commit SHA.
- `SPEC-1662` (GOV-18) — the new assertions are behavioral.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 — protocol gates
  governing this document.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
already requires automatic VERIFIED-driven completion; this restores the
behavior it specifies. No new requirement surface is created. The owner decision
below settles which of two existing mechanisms yields, and creates no new rule.

## Spec-Derived Verification Plan

| Requirement | Test | Expected |
|---|---|---|
| Scope 1 — ancestor coverage | `test_target_committed_in_ancestor_is_covered` | fixture repo: implementation in commit A, verdict in descendant commit B → `covered: true` |
| Scope 1 — same-commit still works | `test_target_in_verdict_commit_remains_covered` | today's shape is unaffected → `covered: true` |
| Scope 2 — verdict rule intact | `test_verdict_absent_from_its_commit_is_not_covered` | `verdict_state` still reports the omission; not silently widened |
| Scope 2 — untracked verdict | `test_untracked_verdict_still_uncovered` | `uncommitted_or_untracked` early return preserved |
| Scope 3 — ancestry enforced | `test_target_committed_after_verdict_is_not_covered` | implementation on a commit that is NOT an ancestor → `covered: false`, path in `missing_paths` |
| Scope 3 — unrelated branch | `test_target_on_unrelated_branch_is_not_covered` | non-ancestor sibling commit → `covered: false` |
| Never-committed path | `test_never_committed_target_is_not_covered` | absent from history → `covered: false` |
| Live effect | `--dry-run` before and after | `missing_implementation_commit_coverage` count falls from 65; WI-6221 and WI-6267 move to `resolve` |
| Regression floor | full `test_bridge_verified_backlog_reconciler*.py` module set, run in full | green; any pre-existing failures shown identical at `HEAD` |

Fixture git repositories are used for the behavioral rows; the live repo is used
only for the before/after dry-run comparison.

## Owner Decisions / Input

- **AskUserQuestion, 2026-08-14, "Coverage rule".** Presented as a conflict
  between two governed mechanisms with four options. Owner selected **"Widen
  coverage to earlier commits"**: accept implementation committed in any earlier
  commit reachable from the verdict commit; paths must still be committed;
  same-commit atomicity is dropped. This proposal implements exactly that
  selection.
- The owner explicitly rejected, by selecting otherwise: treating the sweep as
  non-conforming (which would re-open the WI-4871 treadmill it exists to drain),
  and sanctioning the `by_reference_waiver` path as the route.
- Owner goal directive this session: complete GET HEALTHY PHASE 2 implemented,
  tested and committed. This thread is the blocker for showing that program
  complete, since two of its finished items cannot leave the backlog.
- No further owner decision is required to implement.

## Prior Deliberations

- `DELIB-20266278` — owner authorization of the treadmill-drain program and the
  auto-finalization sweep whose verdict-only invariant is one side of this
  conflict.
- `WI-4889` — the sweep's implementation work item.
- `WI-4871` — the untracked-VERIFIED durability guard the sweep drains; relevant
  because option (b) would have re-opened it.
- `WI-6280` — this work item, carrying the full measurement and the three
  candidate directions.
- `WI-6221` / `WI-6267` — the two Phase-2 items demonstrating the failure, both
  VERIFIED and committed today.
- No prior deliberation was found proposing an ancestry-based coverage rule; the
  same-commit requirement appears to have been adopted without the split-commit
  case being considered.

## Cross-Harness Disposition

`scripts/bridge_verified_backlog_reconciler.py` is a shared project script, not
a per-harness surface: no harness configuration, hook registration, or projected
copy is touched, and no harness-specific behavior is introduced. No projection or
waiver is required. Typed disposition: `not-a-harness-surface`.

## Risk / Rollback

The change **loosens** a gate, so the risk is admitting a work item that should
not close. The ancestry constraint is what bounds it: a path committed after
verification, or on an unrelated branch, stays uncovered, and two tests pin that
directly. The verdict file's own same-commit requirement is untouched, so the
"a verdict exists and is committed" invariant is unchanged.

Residual risk accepted: implementation committed in an ancestor is trusted as the
work the verdict verified, on the strength of the verdict's own `target_paths`
declaration. That is the same trust the same-commit rule placed in the
declaration; only the commit boundary moves.

Scope item 4 mutates MemBase across up to 65 rows. MemBase is append-only, so
rollback is a compensating new version per affected row rather than a delete;
the applied set is enumerated in the implementation report so any subset can be
reversed. `--repair-overbroad` also exists as a reconciler-native audit path and
is unaffected by this change.

Rollback of the code is reverting one function.

## Recommended Commit Type

`fix` — repairs a governed behavior that is specified but not firing, with
regression tests. No new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
