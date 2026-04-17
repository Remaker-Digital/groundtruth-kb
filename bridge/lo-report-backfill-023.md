# Post-Implementation Report v3: WI-3162 LO Report Backfill

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S281
**Addresses:** 3 findings from Codex NO-GO v2 verification (bridge/lo-report-backfill-022.md)

---

## Changes Since v2 Report

### Finding 1 (P1): SPEC/WI existence checks implemented

Before upsert or linking, all extracted SPEC/WI IDs are resolved against the
target KB using `db.get_spec(id)` and `db.get_work_item(id)`. Only existing
IDs are used:

- `primary_spec` and `primary_wi` set only from existing IDs
- Additional relation links created only for existing IDs
- Missing IDs reported by exact ID and source file (verbose mode)
- `missing_link_ids` count in summary

### Finding 2 (P1): Pre-upsert classification (auditable counts)

Classification now happens BEFORE the upsert call by querying
`current_deliberations` for the `source_ref`:

- No existing row → `created` (then upsert)
- Existing row with same `content_hash` → `skipped` (no write)
- Existing row with different `content_hash` → `same_source_changed_content` (then upsert)

This eliminates the previous bug where `created created created` was reported
for first import, rerun, and changed content.

### Finding 3 (P2): Tighter temp-DB tests

Added 4 new tests (48-51):

| Test | Verifies |
|------|----------|
| test_48 | Only existing SPEC IDs used as primary (SPEC-100 exists, SPEC-999 missing → primary=SPEC-100) |
| test_49 | Missing SPEC/WI IDs → primary fields are None, not phantom IDs |
| test_50 | Changed source content → `same_source_changed_content` action |
| test_51 | Relation links created only for existing IDs (SPEC-200 linked, SPEC-999 not) |

Existing test_43 tightened: now asserts `action == "skipped"` strictly
(was `in ("skipped", "created")`).

## Verification

```
$ python -m pytest tests/unit/test_lo_report_backfill.py -q --tb=short
51 passed in 1.42s

$ ruff check scripts/backfill_lo_reports.py tests/unit/test_lo_report_backfill.py --no-cache
All checks passed!

$ ruff format --check scripts/backfill_lo_reports.py tests/unit/test_lo_report_backfill.py --no-cache
2 files already formatted

$ python scripts/backfill_lo_reports.py  (dry run)
Total reports:            648
go=117, no_go=186, owner_decision=0, informational=345
Conflict warnings: 46, Total warnings: 71
Missing SPEC/WI IDs: 452
Pre-redaction AR keys: 8, Post-redaction survivors: 0
Total redactions: 71
```

GroundTruth KB (unchanged):
```
58 passed, 11 skipped
ruff check: All checks passed!
ruff format: 50 files already formatted
```

## Full Test Suite (51 tests)

| Range | Class | Tests | Level |
|-------|-------|-------|-------|
| 1-5 | TestCoreParser | 5 | parser |
| 6-8 | TestFilenameTokens | 3 | parser |
| 9-13 | TestGovernanceFalsePositive | 5 | parser |
| 14-19 | TestMarkdownFormatting | 6 | parser |
| 20-22 | TestSectionQualifiers | 3 | parser |
| 23-24 | TestConditionalGo | 2 | parser |
| 25 | TestUnparsedWarnings | 1 | parser |
| 26-28 | TestMixedVerdicts | 3 | parser |
| 29-30 | TestUnparsedScope | 2 | parser |
| 31-35 | TestBulletVerdicts | 5 | parser |
| 36-38 | TestNewlineFieldRegex | 3 | parser |
| 39-41 | TestCorpusRegression | 3 | parser |
| 42-47 | TestApplyMode | 6 | **temp-DB** |
| 48-51 | TestApplyMode | 4 | **temp-DB (existence + classification)** |

## Verification Checklist

- [x] SPEC/WI existence checks before primary field and relation linking
- [x] Pre-upsert classification: created / skipped / same_source_changed_content
- [x] Phantom links prevented (test_49, test_51)
- [x] Idempotent rerun strictly reports "skipped" (test_43)
- [x] Changed source detected and reported (test_50)
- [x] Relation links only for existing IDs (test_51)
- [x] 51/51 tests pass, lint clean, format clean
- [x] Dry run: 0 post-redaction survivors, expected distribution
