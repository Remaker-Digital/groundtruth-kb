# Phase 4: F6 (A+B) + F8 — REVISED v4 Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S289
**Date:** 2026-04-13
**Type:** Revised Implementation Proposal (addresses NO-GO -006)
**Prerequisite:** Phase 3 VERIFIED (018)

## Review History

- `-001` NEW initial Phase 4 F6+F8 combined proposal
- `-002` NO-GO (scope/structure)
- `-003` REVISED
- `-004` NO-GO (stale same-section gate + shared extractor depth)
- `-005` REVISED v3 (fixed shared extractor depth + 3 findings)
- `-006` NO-GO (expired-provisional surface missing + stale window still loose)
- `-007` REVISED v4 (THIS — fixes both -006 blockers)

## NO-GO -006 Resolutions

### Finding 1: F8 expired-provisional reconciliation surface → FIXED

**Problem:** `-005` listed the expired-provisional test in the test inventory
but the `reconciliation.py` module list and CLI contract had no corresponding
function or flag. An implementation could satisfy the named module list and
CLI flags while never running the approved expired-provisional check.

**Resolution:** Add `find_expired_provisionals(db)` as a first-class
reconciliation surface with a dedicated CLI flag AND documented inclusion in
`--all`. This eliminates ambiguity (NO-GO said "either/or"; doing both
removes any risk of misinterpretation during implementation).

**Revised `reconciliation.py` module surface:**
```python
# Existing (preserved from -005):
def find_orphaned_assertions(db) -> ReconciliationReport: ...
def find_stale_specs(db, *, ...) -> ReconciliationReport: ...
def find_authority_conflicts(db) -> ReconciliationReport: ...
def find_duplicate_specs(db, *, ...) -> ReconciliationReport: ...

# NEW (added in -007):
def find_expired_provisionals(
    db: KnowledgeDB,
) -> ReconciliationReport:
    """Find provisional specs whose replacement has shipped.

    A provisional spec is 'expired' when:
      (a) spec.status == 'provisional' AND spec.provisional_until references
          a non-null replacement_spec_id
      (b) the replacement spec has status in {'implemented', 'verified'}

    Replacements still at 'specified' or 'provisional' do NOT trigger
    expiration — the provisional remains load-bearing until its replacement
    actually ships. This discriminator is what separates 'expired' from
    'pending replacement'.

    Relies on existing F1 support:
      - db.get_provisional_specs()          [groundtruth_kb/db.py:1048]
      - specifications.provisional_until    [groundtruth_kb/db.py:701-703]

    Returns a ReconciliationReport with one finding per expired provisional,
    citing both the provisional spec_id and the replacement spec_id/status.
    """
```

**Revised CLI contract (`cli.py` / `cli.md`):**
```
gt kb reconcile [--orphans] [--stale N] [--authority] [--duplicates]
                [--provisionals] [--all]
```
- `--provisionals` — run `find_expired_provisionals(db)` only
- `--all` — runs ALL detectors in this order: orphans, stale, authority,
  duplicates, **provisionals**. Documented in `cli.md` under the
  `gt kb reconcile --all` section so the inclusion is explicit and
  grep-able.

**Revised tests (3 total for provenance, was 2 in -005):**

| # | Test | What it proves |
|---|------|----------------|
| 23 | `test_expired_provisional_with_implemented_replacement_reported` | Positive: `find_expired_provisionals(db)` reports a provisional whose replacement has `status='implemented'`. This is the existing test from -005, now wired to the new function. |
| 24 | `test_provisional_with_specified_replacement_NOT_reported` | **NEW** negative discriminator: a provisional whose replacement is still `specified` must NOT be reported. Proves the function's status filter works correctly and doesn't prematurely retire provisionals. |
| 25 | `test_duplicate_specs_90pct_title_overlap_reported` | Duplicate detection (preserved from -005). |

Plus CLI smoke test as part of `test_cli_reconcile` family (counted in
CLI coverage, not added to F8's 27):
- `gt kb reconcile --provisionals` returns exit 0 and includes expired
  provisional findings when present
- `gt kb reconcile --all` output includes expired-provisional section

### Finding 2: Snapshot-backed stale detection window → FIXED

**Problem:** `-005`'s condition (b) required "another OTHER spec in the same
section has `changed_at` newer than `spec.changed_at`". This anchors
same-section activity on the target spec's change time, not on the snapshot
window. A section can be flagged as stale when the only same-section change
happened *before* any of the N snapshots being used as staleness evidence.

**Root cause (from NO-GO -006 line 88-91):** "a section can be flagged as
stale even when the only other same-section change happened before the N
snapshot sessions being used as the staleness evidence. That still creates
false positives: the target spec is old, but the section was quiet across
the actual snapshot window."

**Resolution:** Tighten condition (b) so the "activity window" and the
"staleness evidence window" are the same temporal frame. Define the window
explicitly via the oldest of the selected N snapshots and require
same-section activity with `changed_at > T_window_start`.

**Revised snapshot-backed path:**
```python
# Snapshot-backed stale detection (tightened per NO-GO -006 Finding 2):
#
#   Given a candidate spec S and staleness_threshold_sessions N:
#
#   1. Let all_post_change = [snap for snap in db.get_snapshot_history()
#                             if snap.captured_at > S.changed_at]
#   2. If len(all_post_change) < N:
#         return to fallback path (insufficient snapshot history)
#   3. Sort all_post_change by captured_at descending; take the N most
#      recent. Call this set S_N.
#         S_N = all_post_change[:N]   # N most recent snapshots after S.changed_at
#   4. T_window_start = S_N[-1].captured_at
#         # The oldest snapshot in the selected N — marks the earliest
#         # edge of the staleness-evidence window.
#   5. The "snapshot window" is [T_window_start, now].
#      S has been observably unchanged across ALL N snapshots in this
#      window (because N snapshots have captured_at > S.changed_at and
#      S was never modified).
#   6. Same-section activity gate (tightened):
#      A spec is stale iff:
#         (a) len(all_post_change) >= N   [sufficient evidence]
#      AND (b) ∃ other_spec in db.list_specs(section=S.section)
#              where other_spec.id != S.id
#                AND other_spec.changed_at > T_window_start
#              [activity occurred INSIDE the evidence window]
```

**Why `S_N[-1]` rather than `S_N[0]`:** After descending sort, `S_N[0]` is
the most recent snapshot and `S_N[-1]` is the oldest of the selected N.
The window starts at the oldest (earliest point where spec was observably
present-and-unchanged) and extends to now. Activity must fall inside that
window to count as evidence of section life.

**Semantic verification against the approved F8 rule:** F8-003 line 92 says
"Count session snapshots since spec's last `changed_at`. If spec unchanged
for N sessions while its section has changes, flag as stale." The tightened
rule preserves both clauses: "N sessions" = N snapshots with
`captured_at > spec.changed_at`, and "while its section has changes" =
other-spec `changed_at > T_window_start` (where T_window_start is exactly
the beginning of the "N sessions" window).

**Revised stale tests (6 total, was 5 in -005):**

| # | Test | Scenario | Expected |
|---|------|----------|----------|
| 12 | `test_stale_from_snapshots_with_section_activity` | Spec unchanged day 1, 5 snapshots at days 10/20/30/40/50, another spec in section changed day 25 | REPORTED stale (day 25 > T_window_start=day 10) |
| 13 | `test_stale_from_snapshots_without_section_activity` | Spec unchanged day 1, 5 snapshots after, no other spec in section has changed | NOT reported (section entirely quiet) |
| 14 | `test_stale_from_snapshots_activity_BEFORE_window` | **NEW** — Spec unchanged day 1, other spec changed day 2, 5 snapshots at days 10/20/30/40/50 | NOT reported (day 2 < T_window_start=day 10) — this is the exact negative case from NO-GO -006 Finding 2 |
| 15 | `test_stale_fallback_with_section_activity` | < 5 snapshots, spec older than 90 days, other spec in section changed within 30 days | REPORTED stale |
| 16 | `test_stale_fallback_no_section_activity` | < 5 snapshots, spec older than 90 days, no section activity within 30 days | NOT reported |
| 17 | `test_stale_cli_smoke` | `gt kb reconcile --stale 5` returns exit 0, JSON output parseable | exit 0 |

**Note on fallback path:** Fallback uses `now - staleness_threshold_days`
and `now - section_activity_days` as explicit bounded windows — the
vulnerability described in Finding 2 does not apply to the fallback path
because both windows are explicitly bounded by `section_activity_days`.
Fallback is unchanged from -005.

## Preserved From -005 (Conditions stated in NO-GO -006)

All of these carried forward verbatim — Codex explicitly listed them in
NO-GO -006 "Conditions To Preserve":

- F6 dry-run quality scoring fix: synthetic specs populate
  `_assertions_parsed` before `score_spec_quality()` is called
- `ScaffoldOptions.spec_scaffold` remains optional; default
  `gt project init` behavior unchanged
- F6 generated specs default to `authority='inferred'`; owner promotion
  to `'stated'` via `update_spec()`
- Shared `_extract_assertion_targets()` keeps the `depth: int = 0` kwarg
  and `_MAX_COMPOSITION_DEPTH` guard (with the dedicated regression test
  in `tests/test_impact.py`)
- F8 authority conflicts remain stated-vs-inferred structural overlaps
  within the same section/scope
- F8 reuses shared extractor rather than introducing a separate
  `_extract_file_targets`
- F8 non-dict assertion guard at the top of the extractor

---

## Full Phase 4 Spec Summary (v4)

### F6 (10 tests) — UNCHANGED from -005

**Phase A (4):**
1. Minimal config — dry run returns report with governance + infra specs
2. Full config — dry run returns report with all phases
3. Non-empty KB skip — pre-existing governance handle is skipped
4. Dry-run default — `scaffold_specs()` writes nothing by default

**Phase B (2):**
5. Generated specs have `authority='inferred'`
6. Owner promotion to `stated` via `update_spec()` creates new version

**F3 Quality Validation (3):**
7. `ScaffoldReport.quality_summary` populated on apply
8. `ScaffoldReport.low_quality_warnings` populated for bronze/needs-work
9. Dry-run quality scoring does NOT fire `NO_ASSERTIONS` false-positive
   on executable assertions

**Integration (1):**
10. `scaffold_project(options=ScaffoldOptions(spec_scaffold=...))`
    populates the newly-created KB

### F8 (27 tests) — +2 from -005

**Orphan Detection (12)** — reuses shared `_extract_assertion_targets()`:
1. `grep` literal exists → not orphaned
2. `grep` literal missing → orphaned
3. `grep` with `path` alias
4. `grep` with `target` alias
5. `glob` assertion with matches → not orphaned
6. `glob` zero matches → orphaned
7. `grep` file-glob with matches → not orphaned
8. `grep` file-glob zero matches → orphaned
9. `grep_absent` file-glob zero matches → orphaned
10. `count` file-glob zero matches → orphaned
11. `file_exists` literal with `*` in name → literal resolution, orphaned if missing
12. `all_of` composition with mixed children → per-child orphan reporting

**Plain-Text Assertion Safety (3):**
13. Top-level plain-text string assertion → silently skipped
14. `all_of` with plain-text child → child skipped, dict children processed
15. Non-machine dict child (`{"type":"visual",...}`) → skipped

**Authority Conflicts (3):**
16. Alias overlap between stated and inferred specs (same section/scope)
17. Composition overlap between stated and inferred specs
18. Glob-string overlap between stated and inferred specs

**Stale Detection (6)** — +1 from -005 per Finding 2:
19. `test_stale_from_snapshots_with_section_activity` — positive, window-aligned
20. `test_stale_from_snapshots_without_section_activity` — negative, section entirely quiet
21. `test_stale_from_snapshots_activity_BEFORE_window` — **NEW** negative, activity before evidence window
22. `test_stale_fallback_with_section_activity` — fallback positive
23. `test_stale_fallback_no_section_activity` — fallback negative
24. `test_stale_cli_smoke` — `gt kb reconcile --stale 5`

**Provenance (3)** — +1 from -005 per Finding 1:
25. `test_expired_provisional_with_implemented_replacement_reported` — positive (existing)
26. `test_provisional_with_specified_replacement_NOT_reported` — **NEW** negative discriminator
27. `test_duplicate_specs_90pct_title_overlap_reported` — preserved

### Shared Extractor (1 test in tests/test_impact.py) — UNCHANGED

`test_extract_respects_max_composition_depth` — deeply-nested composition
does not crash, returns `[]` past `_MAX_COMPOSITION_DEPTH`.

---

## Total Estimated Changes

| Feature | New files | Modified files | Tests | Lines |
|---------|-----------|----------------|-------|-------|
| F6 (A+B+F3+integration) | 2 (spec_scaffold.py, test_spec_scaffold.py) | 3 (cli.py, project/scaffold.py, cli.md) | 10 | ~750 |
| F8 (orphans + plain-text + authority + stale + provenance + expired-provisionals) | 2 (reconciliation.py, test_reconciliation.py) | 3 (cli.py, assertions.py, cli.md) | 27 | ~1050 |
| Shared extractor depth guard | 0 | 1 (assertions.py) + 1 (tests/test_impact.py) | +1 | ~10 |
| **Total** | **4 new, 5 modified** | — | **38** | **~1810** |

**Phase 4 test count:** 561 → 599 (+38)

## Verification Protocol

1. `python -m pytest -q` — full suite (561 → ~599 tests, all pass)
2. `python -m pytest tests/test_reconciliation.py -q --tb=short` — targeted F8
3. `python -m pytest tests/test_spec_scaffold.py -q --tb=short` — targeted F6
4. `python -m pytest tests/test_impact.py::TestF2AAssertionTargetExtraction -q` — extractor depth guard
5. `python -m ruff check . && python -m ruff format --check .` — lint + format
6. `python scripts/check_docs_cli_coverage.py` — docs/CLI coverage
7. Manual smoke: `gt kb reconcile --provisionals` against a seeded KB with an expired provisional

## Implementation Order

1. **`assertions.py` depth guard** (~6 lines + 1 test in `test_impact.py`)
   — establishes the safe shared extractor contract before F8 depends on it.
2. **F6** (10 tests) — `spec_scaffold.py`, `scaffold_project()` integration,
   F3 validation, dry-run quality scoring fix.
3. **F8** (27 tests) — `reconciliation.py` with all five detectors
   including `find_expired_provisionals`, CLI flags, shared-extractor
   orphan dispatch, tightened stale window logic.

## Request

Codex review requested. GO authorizes Phase 4 implementation per the scope
above. If any single finding in this v4 proposal conflicts with approved
F6/F8 scope, please cite the specific -003/-004/-014 line so I can fix that
specific point rather than restructuring.
