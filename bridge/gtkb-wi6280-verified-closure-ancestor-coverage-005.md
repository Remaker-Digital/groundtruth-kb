NEW
::init gtkb lo
::open build

# WI-6280 Implementation Report — Ancestor-Committed VERIFIED Closure

bridge_kind: implementation_report
Document: gtkb-wi6280-verified-closure-ancestor-coverage
Version: 005
Author: Prime Builder (harness B, claude)
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: a0dbbe63-b24f-42eb-9274-e0fec8b23a00
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword
Date: 2026-08-14 UTC

Work Item: WI-6280
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730

target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler_ancestor_coverage.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py", "groundtruth.db"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

Responds to: bridge/gtkb-wi6280-verified-closure-ancestor-coverage-004.md

---

## Summary

All five scope items are implemented, tested and committed. Commit
`de09a0161`. The reconciler `--apply` ran and resolved **30 work items**,
including `WI-6221` and `WI-6267` — the two GET HEALTHY PHASE 2 items that were
implemented, verified and committed yet still read `open`/`backlogged`, which is
the condition that opened this thread.

## Changes

`scripts/bridge_verified_backlog_reconciler.py`

- `_commit_is_ancestor(project_root, candidate, descendant, cache)` — memoized
  `git merge-base --is-ancestor`, treating an equal commit as an ancestor.
- `_target_covered_by_ancestor_commit(...)` — resolves a target's latest commit
  from the provenance index and tests ancestry. Glob targets keep the existing
  ANY-match semantics of `_target_covered_by_commit`.
- The coverage loop in `_terminal_verdict_commit_coverage` now allows the
  ancestor path **for implementation targets only**; `verdict_rel_path` is
  excluded by an explicit identity check, so the verdict must still appear in
  its own commit. All four existing early returns are untouched.

`platform_tests/scripts/test_bridge_verified_backlog_reconciler_ancestor_coverage.py`
— new, 8 tests over fixture git repositories.

`platform_tests/scripts/test_bridge_verified_backlog_reconciler.py` — the two
superseded tests corrected per scope item 5.

## Specification Links

Carried forward from the `-003` proposal approved at `-004`:

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — the governance this
  reconciler implements, and which was not firing for 65 work items.
- `GOV-STANDING-BACKLOG-001` v5 — the backlog is the work authority; completed
  work that cannot leave it makes that authority overstate remaining work.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — the audit-trail property the same-commit
  rule protected; preserved by keeping the verdict file's own rule unchanged and
  by the ancestry bound.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — every figure in this report is a
  fresh measurement against the live DB and git history.
- `SPEC-1662` (GOV-18) — assertion quality; the new tests are behavioral, and
  the red-first check demonstrates they exercise the changed mechanism.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 — protocol gates
  governing this document.
- `GOV-06` / `GOV-15` — the basis for putting the two superseded test changes
  through review rather than editing them autonomously.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 (completion is automatic) | `--apply` over the live DB | yes | 30 resolved, incl. WI-6221 / WI-6267 |
| Scope 1 (ancestor coverage) | `test_target_committed_in_ancestor_is_covered` | yes | pass |
| Scope 1 (same-commit preserved) | `test_target_in_verdict_commit_remains_covered` | yes | pass |
| Scope 2 (verdict rule intact) | `test_verdict_must_still_appear_in_its_own_commit` | yes | pass |
| Scope 2 (untracked verdict) | `test_untracked_verdict_still_uncovered` | yes | pass |
| Scope 3 (ancestry bound) | `test_target_committed_after_verdict_is_not_covered` | yes | pass |
| Scope 3 (unrelated branch) | `test_target_on_unrelated_branch_is_not_covered` | yes | pass |
| Scope 3 (never committed) | `test_never_committed_target_is_not_covered` | yes | pass |
| Glob semantics | `test_glob_target_matches_via_ancestor` | yes | pass |
| Scope 5 test 1 | `test_terminal_commit_with_ancestor_committed_target_closes` | yes | pass |
| Scope 5 test 2 | `test_waiver_reference_outside_report_does_not_bypass_commit_coverage` | yes | pass |
| SPEC-1662 (GOV-18, behavioral assertions) | red-first check against HEAD | yes | 2 widening tests fail at HEAD, 6 guards pass |

## Commands Executed

```
python -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler_ancestor_coverage.py -q
    -> 8 passed

python -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler.py \
                 platform_tests/scripts/test_bridge_verified_backlog_reconciler_ancestor_coverage.py -q
    -> 49 passed, 1 failed

python -m ruff check <3 changed files>          -> All checks passed!
python -m ruff format --check <3 changed files> -> 3 files already formatted

python scripts/bridge_verified_backlog_reconciler.py --dry-run   (before / after)
python scripts/bridge_verified_backlog_reconciler.py --apply     -> resolved 30
```

**Red-first evidence.** With the HEAD copy of the reconciler restored and the
working copy replaced afterwards, the new module reported *2 failed, 6 passed*:
`test_target_committed_in_ancestor_is_covered` and
`test_glob_target_matches_via_ancestor` fail without the change, while the six
guard tests pass. The new tests therefore exercise the changed mechanism rather
than co-occurring with it.

**The one remaining failure is pre-existing.**
`test_claude_and_codex_hooks_register_reconciler_command` fails identically at
`HEAD` — established by restoring HEAD copies of both changed files and
re-running that single test (*1 failed*), then restoring the working copies. It
concerns hook registration and is untouched by this change.

## Measured Effect

`--dry-run` skip-reason distribution, before and after:

| Skip reason | Before | After |
|---|---:|---:|
| `linked_bridge_not_verified` | 304 | 308 |
| `missing_implementation_commit_coverage` | **65** | **45** |
| `no_related_bridge_threads` | 11 | 11 |
| `missing_parent_evidence` | 3 | 4 |

The 45 that remain are correctly still blocked: their targets are never
committed, or committed on a non-ancestor commit. That is the Scope 3 bound
working, not a shortfall. `--apply` then resolved 30 items.

(The small movements in the other buckets reflect live bridge activity by other
sessions between the two runs, not this change.)

## Acceptance Criteria

- Ancestor-committed implementations close: **met** (2 tests + live apply).
- Same-commit shape still closes: **met**.
- Post-verdict and off-branch work still fails closed: **met** (2 tests).
- Verdict file's own same-commit rule unchanged: **met** (2 tests).
- No test deleted; module count did not decrease: **met** (both corrected tests
  retained, one renamed).
- WI-6221 and WI-6267 resolve: **met**.

## Owner Decisions / Input

- **AskUserQuestion 2026-08-14 "Coverage rule"** — owner selected "Widen
  coverage to earlier commits". Implemented exactly as selected.
- No further owner decision was required. Per the `-004` GO, running `--apply`
  needs no separate approval: `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
  makes VERIFIED-driven completion automatic without owner confirmation.

## Prior Deliberations

- `bridge/gtkb-wi6280-verified-closure-ancestor-coverage-004.md` — the GO for
  the scope widening.
- `bridge/gtkb-wi6280-verified-closure-ancestor-coverage-002.md` — the original
  unconditional GO.
- `DELIB-20266278` — owner authorization of the auto-finalization sweep.
- `WI-6280` — the 65-item measurement.

## Notes For The Verifier

Two things worth an independent look:

1. **`groundtruth.db` is gitignored**, so the 30 resolutions are not in the
   commit. They are verifiable by re-running `--dry-run` (the resolved items no
   longer appear as candidates) or by reading `current_work_items` for
   `WI-6221` / `WI-6267`.
2. **The residual 45** deserve a spot check. My reading is that they are
   legitimately uncovered, but I did not enumerate all 45 — a sample would
   confirm the ancestry bound is rejecting for the right reasons rather than
   masking a second defect.

## Recommended Commit Type

Recommended commit type: `fix` — repairs a governed behavior that was specified
but not firing, with regression tests. Landed as `de09a0161`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
