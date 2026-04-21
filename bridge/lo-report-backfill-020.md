# NO-GO: WI-3162 LO Report Backfill Post-Implementation Verification

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/lo-report-backfill-019.md`
**Prior GO:** `bridge/lo-report-backfill-018.md`
**Verdict:** NO-GO

## Claim

The implementation verifies the parser-focused portion of the v9 proposal and
the GroundTruth redaction prerequisite, but it does not implement the backfill
write path. `--apply` instantiates `KnowledgeDB` and scans the report corpus,
yet never calls the deliberation upsert API or the SPEC/WI relation helpers.

This blocks verification because the work item's primary purpose is to backfill
LO reports into the deliberation archive, not only to classify them in a dry
run.

## Evidence

- `scripts/backfill_lo_reports.py:365-373` imports and instantiates
  `KnowledgeDB` only in apply mode.
- `scripts/backfill_lo_reports.py:378-478` iterates the 648 report files,
  extracts outcomes and SPEC/WI IDs, counts warnings, performs redaction
  checks, and prints a summary. There is no call in this loop to insert or
  upsert a deliberation.
- Repository search confirmed the absence of write/link calls:
  `rg -n "upsert_deliberation_source|insert_deliberation|link_deliberation_spec|link_deliberation_work_item|KnowledgeDB\\(" scripts/backfill_lo_reports.py tests/unit/test_lo_report_backfill.py`
  returned only `scripts/backfill_lo_reports.py:373: db = KnowledgeDB(db_path)`.
- The Agent Red shim documents that `KnowledgeDB()` defaults to
  `tools/knowledge-db/knowledge.db` at `tools/knowledge-db/db.py:40-47` and
  subclasses the GroundTruth implementation at `tools/knowledge-db/db.py:78-94`.
- The required GroundTruth APIs exist:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3254`
  defines `upsert_deliberation_source()`,
  `:3374` defines `link_deliberation_spec()`, and `:3384` defines
  `link_deliberation_work_item()`.
- `scripts/backfill_lo_reports.py` also does not extract/store title, summary,
  session ID, normalized `source_ref`, source metadata, `changed_by`, or
  `change_reason`; search for those insertion fields only found local title
  text used for parser scan windows and artifact ordering.
- `tests/unit/test_lo_report_backfill.py:1-5` describes the suite as parser
  and ID extraction tests. The 41 tests do not exercise apply mode, temp-DB
  upsert behavior, idempotent reruns, or SPEC/WI relation linking.
- Verification commands run in Agent Red:
  - `python -m pytest tests/unit/test_lo_report_backfill.py -q --tb=short` ->
    `41 passed in 0.23s`
  - `python -m ruff check scripts/backfill_lo_reports.py tests/unit/test_lo_report_backfill.py --no-cache` ->
    `All checks passed!`
  - `python -m ruff format --check scripts/backfill_lo_reports.py tests/unit/test_lo_report_backfill.py --no-cache` ->
    `2 files already formatted`
  - `python scripts/backfill_lo_reports.py` reproduced the report's dry-run
    distribution: 648 reports, `go=117`, `no_go=186`, `owner_decision=0`,
    `informational=345`, 46 conflict warnings, 71 total warnings, 452 missing
    SPEC/WI IDs, and 8 pre-redaction AR keys.
- Verification commands run in GroundTruth KB:
  - `python -m pytest tests/test_deliberations.py -q --tb=short` ->
    `58 passed, 11 skipped in 7.52s`
  - `python -m ruff check .` -> `All checks passed!`
  - `python -m ruff format --check .` -> `50 files already formatted`
  - `git rev-parse --short HEAD` -> `6aa8ce2`
  - `git status --short` -> no output.
- GroundTruth redaction patterns for all five Agent Red key families exist at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3130-3136`.
  Direct redaction probe over the two report files containing AR-key-shaped
  values found `pre=8`, `post=0`.

## Findings

### P1 - Apply mode does not backfill deliberations

The script never calls `db.upsert_deliberation_source()`, so apply mode cannot
create deliberation rows. This is the core deliverable from the proposal and
from the prior GO conditions.

**Risk/impact:** Running `python scripts/backfill_lo_reports.py --apply` can
appear to complete successfully while importing zero LO reports. That produces
a false-success backfill and leaves the deliberation archive empty or unchanged.

**Required action:** Implement the write path in apply mode:

1. Build stable repo-relative POSIX `source_ref` values for each report.
2. Extract title, summary, session ID, outcome, primary SPEC/WI IDs, and
   content.
3. Call `db.upsert_deliberation_source(source_type="lo_review", source_ref=...,
   content=..., title=..., summary=..., outcome=..., spec_id=...,
   work_item_id=..., origin_project=..., origin_repo=..., changed_by=...,
   change_reason=...)`.
4. Report create/skip/same-source-changed-content counts so reruns are
   auditable.

### P1 - SPEC/WI relation linking is not implemented

The script extracts ordered SPEC/WI IDs, but it never checks whether those IDs
exist in the KB and never calls `link_deliberation_spec()` or
`link_deliberation_work_item()` for additional IDs.

**Risk/impact:** Even if insertion were added, the import would still miss the
traceability value that justified the backfill: `get_deliberations_for_spec()`
and `get_deliberations_for_work_item()` would not reliably surface historical
LO evidence for referenced artifacts.

**Required action:** After each successful upsert, link all existing referenced
SPEC/WI IDs. Use the first deterministic ID as the primary field and relation
links for the rest. Report missing IDs separately and do not create phantom
links silently.

### P2 - Dry-run redaction reporting does not prove post-redaction survivors

Dry run reports only `Pre-redaction AR keys: 8` and says they will be redacted
before storage. In `scripts/backfill_lo_reports.py:404-421`, GroundTruth
`redact_content()` is only called when `apply=True`; dry run estimates
redactions from the survivor count instead of checking the storage-boundary
redaction function.

**Risk/impact:** The reviewed safety condition required dry-run survivor
visibility before writing. The current dry run cannot prove zero post-redaction
AR-key survivors, and apply-mode survivor summary logic at
`scripts/backfill_lo_reports.py:453-456` counts reports with pre-redaction
survivors and any warning, not actual post-redaction survivor counts.

**Required action:** In dry-run mode, import the Agent Red `KnowledgeDB` shim
and call `db.redact_content()` for survivor simulation without writing. Report
pre-redaction key count, redaction count, and post-redaction survivor count.
Track post-redaction survivor count explicitly instead of deriving it from
generic warnings.

### P2 - Apply-mode behavior lacks temp-DB/idempotency tests

The tests cover parser and ID extraction behavior, but not the write path,
idempotent reruns, relation linking, or dry-run/apply summary counts.

**Risk/impact:** The current regression suite passed while the main write path
was absent. Future changes could still pass parser tests while failing to
populate the deliberation archive.

**Required action:** Add tests using a temporary database that verify:

1. apply mode creates deliberation rows with `source_type="lo_review"` and
   normalized `source_ref`;
2. rerunning same content skips or returns the same deliberation;
3. changed content for the same source is reported as changed-source content;
4. primary SPEC/WI IDs and relation links are created for existing IDs;
5. missing IDs are reported but not linked;
6. dry-run does not write rows but does simulate redaction and survivor counts.

## Required Conditions For VERIFIED

1. Implement apply-mode deliberation upsert using the Agent Red project KB shim.
2. Implement SPEC/WI existence checks and relation linking.
3. Add dry-run and apply summary counts for create/skip/changed-source,
   links, missing IDs, redactions, and post-redaction survivors.
4. Add temp-DB tests for upsert, idempotency, linking, missing IDs, and dry-run
   no-write behavior.
5. Re-run the Agent Red unit/lint/format checks and a dry run over the
   648-file corpus.
6. Re-run the GroundTruth deliberation tests and ruff checks after any further
   storage-boundary changes.

## Decision Needed From Owner

No owner decision is needed. This is an implementation completeness failure
against the approved proposal, not a policy trade-off.
