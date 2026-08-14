REVISED
::init gtkb lo
::open build

# WI-6280 — Widen VERIFIED closure coverage to ancestor commits (scope widened for superseded tests)

bridge_kind: prime_proposal
Document: gtkb-wi6280-verified-closure-ancestor-coverage
Version: 003
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

This proposal DOES mutate MemBase: scope item 4 runs the reconciler with
`--apply`. `groundtruth.db` is declared in `target_paths` accordingly.

Responds to: bridge/gtkb-wi6280-verified-closure-ancestor-coverage-002.md

---

## Why This Revision Exists

`-002` recorded **GO** with no conditions. Implementation proceeded and the code
change plus its eight new tests are complete and green. The regression floor then
surfaced a scope gap that neither the proposal nor the review anticipated:

**Two existing tests in `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`
encode the same-commit rule the owner decision supersedes.** They pass at `HEAD`
and fail with the change. That module is not in the `-001` `target_paths`, so
correcting them is outside the approved scope.

This revision adds that one path and states exactly what will change inside it.
Nothing else moves: the code change, the ancestry bound, the new test module and
the apply step are all as approved.

Causation was established rather than assumed. Running the four candidate
failures against the `HEAD` copy of the reconciler with the working copy
restored afterwards:

```
=== AT HEAD (without the change) ===
FAILED ... test_bridge_reconciliation_skill.py::test_canonical_skill_exists_with_frontmatter
FAILED ... test_slice8_memory_reconciliation.py::test_memory_md_is_index_template
2 failed, 2 passed
```

So the two skill/memory failures are **pre-existing** and unrelated, and the two
reconciler failures are **caused by this change**.

## The Two Superseded Tests, and Why They Differ

They share a fixture shape — implementation committed first, verdict committed
second — but they are not the same kind of test, and the correct treatment
differs.

### 1. `test_terminal_commit_omitting_approved_target_fails_closed`

Directly encodes the superseded rule. It commits `scripts/impl.py`, then commits
the bridge thread alone, and asserts:

```python
assert row["action"] == "skip"
assert row["reason"] == "missing_implementation_commit_coverage"
assert evidence["commit_coverage"]["missing_paths"] == ["scripts/impl.py"]
```

That is precisely the scenario the owner AUQ authorized closing. **Proposed
change:** flip the expectation to `action == "resolve"`, `closure_reason ==
"genuinely_closable"`, and `missing_paths == []`, and rename to
`test_terminal_commit_with_ancestor_committed_target_closes` so the name states
the new rule. The test remains a real assertion; only the governed expectation
moves.

### 2. `test_waiver_reference_outside_report_does_not_bypass_commit_coverage`

**Its subject is not the same-commit rule.** It asserts that a
`## Owner Decisions / Input` waiver reference sitting in the *proposal* rather
than the *report* does not bypass coverage. The split-commit shape is only the
vehicle it uses to make coverage fail in the first place. With coverage now
legitimately satisfied, the vehicle stops working and the test no longer isolates
its own property.

**Proposed change:** keep the property, replace the vehicle. Point
`target_paths` at a path that was never committed at all, so coverage still
fails for an unrelated reason, and re-assert that the out-of-report waiver does
not rescue it. The waiver-scoping guarantee is preserved exactly; only the way
the test induces a coverage failure changes.

This distinction is the substantive content of this revision. Deleting test 2, or
flipping it the way test 1 flips, would silently drop a live guarantee about
waiver scoping — a real loss disguised as a green suite.

## Scope

Scope items 1-4 are unchanged from `-001` and are already implemented:

1. Widen target-path coverage to ancestors in `_terminal_verdict_commit_coverage`.
2. The verdict file's own same-commit rule does not change.
3. Ancestry, not mere presence, via `git merge-base --is-ancestor`, memoized.
4. Run `bridge_verified_backlog_reconciler.py --apply` and record the resolved set.

New in this revision:

5. **Correct the two superseded tests** in
   `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py` exactly as
   described above — one expectation flip with a rename, one vehicle
   replacement preserving the asserted property. No other test in that module is
   touched; no test is deleted.

## Implementation Status At Time Of Filing

Complete and green, pending scope item 5:

- `_commit_is_ancestor` and `_target_covered_by_ancestor_commit` added; the
  coverage loop now allows an ancestor commit for implementation targets only.
- `platform_tests/scripts/test_bridge_verified_backlog_reconciler_ancestor_coverage.py`:
  **8 passed**.
- Red-first evidence: against the `HEAD` reconciler, the two positive-widening
  tests fail and the six guard tests pass — confirming the new tests exercise the
  changed mechanism rather than co-occurring with it.
- `ruff check`: All checks passed. `ruff format --check`: 2 files already
  formatted.
- Regression floor across 13 reconciler/reconciliation modules: 100 passed,
  10 failed — 8 pre-existing, 2 the superseded tests above.

## Spec-Derived Verification Plan

Carried from `-001`, plus:

| Requirement | Test | Expected |
|---|---|---|
| Scope 5, test 1 | `test_terminal_commit_with_ancestor_committed_target_closes` | the split-commit shape now resolves; `missing_paths == []` |
| Scope 5, test 2 | `test_waiver_reference_outside_report_does_not_bypass_commit_coverage` | still skips, via a never-committed target; the waiver-scoping property is unchanged |
| No silent deletion | full module count | the module's test count does not decrease |
| Regression floor | 13 reconciler/reconciliation modules | only the 8 pre-existing failures remain, enumerated with HEAD-comparison evidence |

## Specification Links

Unchanged from `-001`:
`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`, `GOV-STANDING-BACKLOG-001` v5,
`GOV-FILE-BRIDGE-AUTHORITY-001` v4, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5,
`SPEC-1662` (GOV-18),
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1,
`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1.

Additionally relevant to scope item 5:

- `GOV-06` — spec-first correction: the specification (here, the owner AUQ
  settling the mechanism conflict) changes first, and the test follows. The tests
  are not being "fixed" to make a suite green; they encode a rule that no longer
  holds.
- `GOV-15` — test fix approval gate: this revision is the approval request for
  those test changes rather than an autonomous edit, which is why the work stopped
  at the scope boundary instead of proceeding.

## Requirement Sufficiency

Existing requirements sufficient. The owner AUQ recorded in `-001` settles which
mechanism yields; scope item 5 propagates that settlement into the tests that
still assert the losing side. No new requirement surface.

## Owner Decisions / Input

- **AskUserQuestion, 2026-08-14, "Coverage rule"** — owner selected "Widen
  coverage to earlier commits". Unchanged; this revision does not reopen it.
- No new owner decision is requested. Scope item 5 follows mechanically from that
  decision: the two tests assert the rule the owner set aside. Per `GOV-15` the
  test changes are put through review rather than made autonomously.
- Owner standing directive this session: when blocked by a defect or omission,
  work around it or use fast-track authorization and record an ADVISORY for a
  future worker. Applied here by filing this narrow revision rather than editing
  outside `target_paths`; the scope gap itself is recorded in the findings above
  so a future reader sees why the module needed adding.

## Prior Deliberations

- `bridge/gtkb-wi6280-verified-closure-ancestor-coverage-002.md` — the
  unconditional GO this revises, including its confirmation that the two governed
  mechanisms genuinely conflict.
- `DELIB-20266278` — owner authorization of the auto-finalization sweep whose
  verdict-only invariant is one side of that conflict.
- `WI-6280` — carries the full 65-item measurement.
- `WI-6221` / `WI-6267` — the worked examples, both VERIFIED and committed.
- No prior deliberation was found on whether the reconciler's own test module
  should encode the same-commit rule; it appears to have been written alongside
  the rule without the split-commit case being considered separately.

## Cross-Harness Disposition

Unchanged: `scripts/bridge_verified_backlog_reconciler.py` and its test module are
shared project surfaces, not per-harness ones. Typed disposition:
`not-a-harness-surface`.

## Risk / Rollback

The added risk in this revision is confined to scope item 5: changing existing
test expectations can hide a regression. Two controls bound it — the property in
test 2 is preserved rather than dropped (with its vehicle changed and stated), and
a count assertion prevents silent deletion. The eight new tests in the companion
module independently pin both directions of the new rule, so the module's
guarantees do not rest on the edited tests alone.

Rollback is reverting one function and two test edits.

## Recommended Commit Type

`fix` — repairs a governed behavior that is specified but not firing, with
regression tests, plus the test corrections the same settlement requires.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
