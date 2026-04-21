GO

# GT-KB Phase 4D Broad Exception Review - Loyal Opposition Re-Review

**Review date:** 2026-04-16
**Reviewed proposal:** `bridge/gtkb-phase4d-broad-exception-review-003.md`
**Prior review:** `bridge/gtkb-phase4d-broad-exception-review-002.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `8efcbb1`

## Verdict

GO, with implementation conditions below. The revised proposal fixes the two
blocking defects from `-002`: the current broad-exception inventory is complete
for the integration working tree, and the expected post-implementation counts
now reconcile.

This is approval to implement the Phase 4D plan. It is not post-implementation
verification.

## Prior Deliberations

No prior deliberations found for the specific GroundTruth-KB Phase 4D
broad-exception proposal. The relevant bridge history is this thread:

- `bridge/gtkb-phase4d-broad-exception-review-001.md` - original proposal
- `bridge/gtkb-phase4d-broad-exception-review-002.md` - NO-GO for incomplete
  inventory and inconsistent counts
- `bridge/gtkb-phase4d-broad-exception-review-003.md` - revised proposal

Relevant non-DELIB context remains the Phase 4A/4B baseline:

- `groundtruth-kb/docs/reports/phase-4b-plan.md` lists broad exception sites
  as 31 baseline sites with 3 "needs review" sites.
- `bridge/gtkb-audit-baseline-007.md` cites 31 broad exception sites and notes
  that `bridge/` was the largest quality gap, consistent with DELIB-0633's
  general bridge-runtime assessment.

## Evidence Checked

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `bridge/INDEX.md` entry for
  `gtkb-phase4d-broad-exception-review`.
- Read all referenced thread files:
  `bridge/gtkb-phase4d-broad-exception-review-001.md`,
  `bridge/gtkb-phase4d-broad-exception-review-002.md`, and
  `bridge/gtkb-phase4d-broad-exception-review-003.md`.
- `git rev-parse --short HEAD` in `groundtruth-kb` returned `8efcbb1`.
- `git status --short` in `groundtruth-kb` showed an integration working tree,
  not clean HEAD: modified `src/groundtruth_kb/bridge/launcher.py`,
  `src/groundtruth_kb/bridge/poller.py`, `src/groundtruth_kb/bridge/worker.py`,
  `src/groundtruth_kb/cli.py`, `src/groundtruth_kb/db.py`; untracked
  `src/groundtruth_kb/_logging.py` and logging tests.
- Working-tree AST scan over `src/groundtruth_kb` returned:
  `total=32`, `reraise=7`, `non_reraise=25`, `marked=0`.
- Working-tree `rg -n "except\s+(BaseException|Exception)|except\s*:" src/groundtruth_kb`
  found the 32 sites covered by the revised proposal, including
  `src/groundtruth_kb/_logging.py:101`.
- Tracked `HEAD` grep returned 31 sites; `_logging.py` is not tracked at
  `HEAD`. This matches the proposal's caveat that the count is 31 without 4C
  and 32 with 4C.

## Findings

### Cleared - Inventory now accounts for the working tree

**Claim:** The revised proposal states 32 broad exception sites: 7 re-raise
cleanup handlers and 25 non-reraising catches.

**Evidence:** The AST scan against the current working tree returned exactly
`total=32`, `reraise=7`, `non_reraise=25`. The 32 includes
`src/groundtruth_kb/_logging.py:101`, which is currently untracked and therefore
comes from the in-flight 4C integration state, not committed `HEAD`.

**Risk/impact:** The prior NO-GO risk is resolved. The implementation plan now
has a complete action for each broad handler in the integration tree.

**Required action:** At implementation time, Prime must run the marker inventory
against the actual final tree being committed. If 4D lands before 4C, the tree
should have 31 starting sites and no `_logging.py` action. If 4C is included or
lands first, `_logging.py:101` must be annotated and covered by the gate.

### Cleared - Counts now reconcile

**Claim:** The revised proposal expects 2 narrowed handlers, 1 removed handler,
22 annotated non-reraising handlers, and 7 exempt re-raise cleanup handlers.

**Evidence:** Starting from the working-tree inventory of 32:

- `db.py` quality score handler narrowed to `sqlite3.IntegrityError`
- `bridge/launcher.py` Windows PID handler narrowed to
  `(OSError, AttributeError, ImportError)`
- `bridge/launcher.py` Unix redundant broad handler removed
- 22 remaining non-reraising broad handlers annotated
- 7 `db.py` transaction cleanup handlers exempt because they contain bare
  re-raises

That leaves 29 broad `except Exception` handlers after implementation:
22 annotated non-reraising catches plus 7 re-raise cleanup catches.

**Risk/impact:** The prior ambiguity is resolved. Acceptance can be checked by
AST and by the proposed regression tests.

**Required action:** Keep the implementation acceptance countable. The marker
test or its failure output should make the final numbers auditable:
22 annotated non-reraising broad catches, 7 exempt re-raise catches, and zero
unannotated non-reraising broad catches when 4C is included.

### Condition - Make the marker gate match the stated contract

**Claim:** The revised proposal says the CI gate checks whether the handler body
contains a bare `raise`, then checks the source line for
`# intentional-catch:` on non-reraising broad handlers.

**Evidence:** `bridge/gtkb-phase4d-broad-exception-review-003.md` describes the
gate as:

- AST walk for `Exception` / `BaseException`
- bare `raise` in the handler body means exempt
- non-reraising handler source line must contain `# intentional-catch:`

**Risk/impact:** A too-loose exemption such as "any bare raise anywhere under
the handler AST" could exempt a future conditional or nested pattern that still
swallows broad exceptions on another path. A marker-placement mismatch could
also fail a correct implementation if comments are added on the line above
while the test checks only the `except` line.

**Required action:** Implement the gate with one of these explicit contracts:

1. marker must be on the `except Exception...` line, and implementation uses
   that placement everywhere; or
2. the gate intentionally supports a documented adjacent-line marker.

For the re-raise exemption, prefer a narrow rule that recognizes the current
cleanup shape, such as a top-level bare `raise` in the handler body after
cleanup. Do not exempt arbitrary nested or conditional bare raises without an
`intentional-catch` marker.

## Required Implementation Conditions

1. Run the broad-exception inventory against the exact final implementation
   tree, not just committed `HEAD` if 4C changes are still staged/untracked.
2. Include `_logging.py:101` in Phase 4D only if the 4C logging file is part of
   the final implementation tree. Otherwise, let the future 4C merge satisfy
   the same marker gate before landing.
3. Add the four proposed tests:
   `test_broad_exceptions_are_annotated`,
   `test_narrowed_db_persist_quality_scores`,
   `test_pid_is_running_narrowed_windows`, and
   `test_pid_is_running_unix_no_broad_catch`.
4. Ensure `test_exception_markers.py` fails with file:line evidence for any
   unannotated non-reraising broad handler.
5. Run the repo-native verification gates after implementation:
   `python -m pytest -q --tb=short`, `python -m ruff check .`,
   `python -m ruff format --check .`, and the existing mypy strict gate.

## GroundTruth-KB Vision Filter

GO is warranted under the GroundTruth-KB vision. The revised plan moves broad
exception governance out of manual review and into a CI-enforced AST check,
reducing the owner's role to decisions about policy exceptions rather than
routine exception-site reconciliation.

## Owner Decision Needed

None.

