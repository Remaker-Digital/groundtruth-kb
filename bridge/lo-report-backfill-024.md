# NO-GO: WI-3162 LO Report Backfill Post-Implementation Verification v3

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/lo-report-backfill-023.md`
**Prior NO-GO:** `bridge/lo-report-backfill-022.md`
**Verdict:** NO-GO

## Claim

The v3 implementation fixes the basic apply-mode gap from the prior review:
it now upserts deliberations, checks SPEC/WI existence before primary fields,
and has tests for first-run creation, idempotent same-content reruns,
changed-source detection, and relation links.

It is still not verifiable because the changed-source path remains
non-auditable after the first changed import. A changed file creates a second
current deliberation row for the same `source_ref`, but later classification
and relation linking query by `source_ref` alone and use an arbitrary first
row. The result is that a rerun of already-imported changed content is reported
as `same_source_changed_content` again instead of `skipped`, and additional
SPEC/WI relation links are attached to the older deliberation row rather than
the changed-content row.

## Evidence

- Agent Red verification commands:
  - `python -m pytest tests/unit/test_lo_report_backfill.py -q --tb=short` ->
    `51 passed in 1.37s`
  - `python -m ruff check scripts/backfill_lo_reports.py tests/unit/test_lo_report_backfill.py --no-cache` ->
    `All checks passed!`
  - `python -m ruff format --check scripts/backfill_lo_reports.py tests/unit/test_lo_report_backfill.py --no-cache` ->
    `2 files already formatted`
  - `python scripts/backfill_lo_reports.py` ->
    648 reports, `go=117`, `no_go=186`, `owner_decision=0`,
    `informational=345`, 46 conflict warnings, 71 total warnings,
    452 reports with no SPEC/WI IDs, 8 pre-redaction AR keys,
    0 post-redaction survivors, and 71 redactions.
- GroundTruth KB verification commands:
  - `python -m pytest tests/test_deliberations.py -q --tb=short` ->
    `58 passed, 11 skipped in 3.84s`
  - `python -m ruff check .` -> `All checks passed!`
  - `python -m ruff format --check .` -> `50 files already formatted`
- GroundTruth redaction patterns for all five Agent Red key families exist at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3130-3136`.
- The implementation checks SPEC/WI existence before setting primary fields at
  `scripts/backfill_lo_reports.py:492`, `scripts/backfill_lo_reports.py:500`,
  and `scripts/backfill_lo_reports.py:514-515`.
- The changed-source classifier queries only one row by `source_ref` at
  `scripts/backfill_lo_reports.py:520`. It does not check all current rows for
  a matching `content_hash`.
- The relation-link lookup also queries only one row by `source_ref` at
  `scripts/backfill_lo_reports.py:560`, then links additional existing IDs at
  `scripts/backfill_lo_reports.py:566` and
  `scripts/backfill_lo_reports.py:569`.
- GroundTruth `upsert_deliberation_source()` is explicitly keyed on
  `(source_ref, content_hash)` at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3254-3287`;
  changed content for the same `source_ref` creates a new `DELIB-*` row.
- Focused temp-DB probe with existing `SPEC-100`, `SPEC-200`, `WI-100`, and
  `WI-200`, plus missing `SPEC-999` and `WI-999`, produced:

```text
PROBE_ACTIONS created skipped same_source_changed_content same_source_changed_content
PROBE_DELIBS [
  {'rowid': 1, 'id': 'DELIB-0001', 'outcome': 'go', 'spec_id': 'SPEC-100', 'work_item_id': 'WI-100', ...},
  {'rowid': 2, 'id': 'DELIB-0002', 'outcome': 'no_go', 'spec_id': 'SPEC-100', 'work_item_id': 'WI-100', ...}
]
PROBE_SPEC_LINKS [{'deliberation_id': 'DELIB-0001', 'spec_id': 'SPEC-200'}]
PROBE_WI_LINKS [{'deliberation_id': 'DELIB-0001', 'work_item_id': 'WI-200'}]
```

- The probe proves the fourth run, which used the same changed content as the
  third run, was still reported as `same_source_changed_content` instead of
  `skipped`.
- The probe also proves the changed-content deliberation `DELIB-0002` did not
  receive the additional `SPEC-200` / `WI-200` relation links; the links were
  attached only to the older `DELIB-0001`.
- Existing tests do not catch this:
  `tests/unit/test_lo_report_backfill.py:620` verifies only the first changed
  run, and `tests/unit/test_lo_report_backfill.py:650` verifies relation links
  only for a first import.
- Dry-run missing-ID reporting is still not an existence check:
  `scripts/backfill_lo_reports.py:429` loads the KB only in apply mode, while
  `scripts/backfill_lo_reports.py:447` increments `Missing SPEC/WI IDs` only
  when a report contains no IDs at all.

## Findings

### P1 - Changed-source reruns are still misclassified

The pre-upsert classifier looks at a single arbitrary current row for the
`source_ref`. After a changed-content import, there are at least two current
rows for that same `source_ref`: the original content hash and the changed
content hash. A rerun of the changed content should be idempotent, but the
probe shows it is counted as `same_source_changed_content` again.

**Risk/impact:** Apply-mode summaries remain non-auditable. Operators cannot
trust `Changed source` counts to mean new changed-source rows were created,
and repeated safe reruns look like repeated source changes.

**Required action:** Classify against all current rows for the `source_ref`.
If any row has the current `content_hash`, report `skipped` and avoid the
write. If no matching hash exists but at least one row exists for the
`source_ref`, report `same_source_changed_content`. If no row exists, report
`created`.

### P1 - Relation links can attach to the wrong deliberation after changed content

After upsert, the script retrieves the deliberation ID with
`SELECT id FROM current_deliberations WHERE source_ref = ?`. Once multiple
current rows share the same `source_ref`, that lookup can return the older row.
The probe shows relation links for `SPEC-200` and `WI-200` were created only
for `DELIB-0001`, while the changed-content row `DELIB-0002` had no additional
relation links.

**Risk/impact:** Changed-source deliberations can lose the traceability links
that make the backfill useful. `get_deliberations_for_spec()` and
`get_deliberations_for_work_item()` may surface the old deliberation but miss
the later changed-content deliberation.

**Required action:** Use the `dict` returned by `db.upsert_deliberation_source()`
as the authoritative deliberation row for linking, or query by both
`source_ref` and `content_hash`. Do not query by `source_ref` alone after
upsert.

### P2 - Tests do not cover changed-content idempotency or changed-row links

The new tests are useful but stop one step short of the failure mode. They
assert the first changed-content run is detected, but they do not rerun that
same changed content and require a `skipped` result. They also assert relation
links on a first import, not on the changed-source row returned by the upsert.

**Risk/impact:** The suite can stay green while apply-mode summaries and
changed-source traceability remain wrong.

**Required action:** Add temp-DB tests that:

1. run original content, rerun original content, change content, then rerun the
   changed content and assert actions are
   `created`, `skipped`, `same_source_changed_content`, `skipped`;
2. assert the changed-content deliberation row receives additional existing
   SPEC/WI relation links;
3. assert missing referenced IDs are counted but never stored or linked in the
   changed-source case.

### P2 - Dry-run missing-ID reporting is still ambiguous

Dry run reports `Missing SPEC/WI IDs`, but that count means reports with no
artifact IDs, not referenced IDs missing from the target KB. Exact missing
referenced IDs are checked only in apply mode.

**Risk/impact:** The dry-run summary can be misread as the no-phantom-link
report required by prior reviews. Operators cannot review missing referenced
IDs before applying writes.

**Required action:** Either load the Agent Red KB during dry run and perform
the same existence checks without writing, or rename the current dry-run count
to `Reports with no SPEC/WI IDs` and add a separate `Missing referenced
SPEC/WI IDs` count when a KB path is available.

## Required Conditions For VERIFIED

1. Fix changed-source classification to check all current rows for
   `source_ref` and treat matching content hashes as idempotent skips.
2. Link additional SPEC/WI IDs using the upsert-returned deliberation ID, or a
   lookup constrained by both `source_ref` and `content_hash`.
3. Add temp-DB coverage for rerunning changed content and for relation links on
   the changed-content deliberation row.
4. Clarify or fix dry-run missing-ID reporting so no-IDs and missing referenced
   IDs are not conflated.
5. Re-run Agent Red unit tests, lint, format, dry run, and a focused temp-DB
   apply probe showing `created skipped same_source_changed_content skipped`
   and relation links on the changed-content row.

## Decision Needed From Owner

No owner decision is needed. This is an apply-mode correctness issue against
the previously approved backfill contract.
