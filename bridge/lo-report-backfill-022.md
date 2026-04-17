# NO-GO: WI-3162 LO Report Backfill Post-Implementation Verification v2

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/lo-report-backfill-021.md`
**Prior NO-GO:** `bridge/lo-report-backfill-020.md`
**Verdict:** NO-GO

## Claim

The v2 implementation adds the previously missing apply-mode upsert call,
storage-boundary redaction simulation, and a larger test suite. The core
backfill is still not verifiable because two required safety conditions remain
unmet:

1. referenced SPEC/WI IDs are not checked for existence before being stored or
   linked, so the script can create phantom traceability;
2. apply-mode create/skip/changed-source reporting is still inaccurate, so
   reruns and changed-source imports are not auditable.

The GroundTruth redaction prerequisite and the parser-focused checks pass.

## Evidence

- `scripts/backfill_lo_reports.py:487-500` now calls
  `db.upsert_deliberation_source()` with `source_type="lo_review"` and the
  extracted metadata.
- `scripts/backfill_lo_reports.py:459-475` runs redaction simulation in dry-run
  and apply mode and counts post-redaction survivors.
- `scripts/backfill_lo_reports.py:484-500` sets `primary_spec` and
  `primary_wi` directly from extracted IDs, without verifying that those IDs
  exist in the KB.
- `scripts/backfill_lo_reports.py:522-536` calls
  `db.link_deliberation_spec()` and `db.link_deliberation_work_item()` for
  additional IDs and treats exceptions as missing IDs.
- GroundTruth link helpers do not raise on missing artifacts:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3374-3390`
  inserts relation rows directly with `INSERT OR REPLACE`; there is no
  existence check or foreign-key constraint against current specs/work items.
- `scripts/backfill_lo_reports.py:447-450` increments
  `Missing SPEC/WI IDs` only when a report has no IDs at all. It does not
  report referenced IDs that are absent from the KB.
- `scripts/backfill_lo_reports.py:503-520` infers `created`, `skipped`, and
  `changed_source` after `upsert_deliberation_source()` returns. GroundTruth's
  `upsert_deliberation_source()` returns an existing row only when
  `(source_ref, content_hash)` matches; otherwise it creates a new deliberation
  ID (`groundtruth-kb\src\groundtruth_kb\db.py:3267-3293`).
- Temp-DB probe with zero specs and zero work items:

```text
PROBE_ACTIONS created created created
PROBE_COUNTS delibs= 2 specs= 0 wis= 0 spec_links= 2 wi_links= 2
PROBE_DELIBS [
  {'id': 'DELIB-0001', 'version': 1, 'spec_id': 'SPEC-999', 'work_item_id': 'WI-999', ...},
  {'id': 'DELIB-0002', 'version': 1, 'spec_id': 'SPEC-999', 'work_item_id': 'WI-999', ...}
]
PROBE_SPEC_LINKS [
  {'deliberation_id': 'DELIB-0001', 'spec_id': 'SPEC-998'},
  {'deliberation_id': 'DELIB-0002', 'spec_id': 'SPEC-998'}
]
PROBE_WI_LINKS [
  {'deliberation_id': 'DELIB-0001', 'work_item_id': 'WI-998'},
  {'deliberation_id': 'DELIB-0002', 'work_item_id': 'WI-998'}
]
```

- The same probe showed each apply run printed `Created: 1`,
  `Skipped (idempotent): 0`, `Changed source: 0`, and `Missing link IDs: 0`,
  including the same-content rerun and the changed-content same-source run.
- `tests/unit/test_lo_report_backfill.py:471-494` names the idempotency test
  as a skip test but allows either `"skipped"` or `"created"`, so the current
  bug still passes.
- `tests/unit/test_lo_report_backfill.py:449-570` covers create, loose
  idempotency, source_ref shape, dry-run no-write, session ID, and redaction,
  but does not assert existing-ID-only primary links, relation table links,
  missing-ID reporting, changed-source classification, or exact rerun counts.
- Agent Red verification commands:
  - `python -m pytest tests/unit/test_lo_report_backfill.py -q --tb=short` ->
    `47 passed in 0.92s`
  - `python -m ruff check scripts/backfill_lo_reports.py tests/unit/test_lo_report_backfill.py --no-cache` ->
    `All checks passed!`
  - `python -m ruff format --check scripts/backfill_lo_reports.py tests/unit/test_lo_report_backfill.py --no-cache` ->
    `2 files already formatted`
  - `python scripts/backfill_lo_reports.py` dry-run summary matched the report:
    648 reports, `go=117`, `no_go=186`, `owner_decision=0`,
    `informational=345`, 46 conflict warnings, 71 total warnings,
    452 `Missing SPEC/WI IDs`, 8 pre-redaction AR keys, 0 post-redaction
    survivors, and 71 redactions.
- GroundTruth verification commands:
  - `python -m pytest tests/test_deliberations.py -q --tb=short` ->
    `58 passed, 11 skipped in 3.92s`
  - `python -m ruff check .` -> `All checks passed!`
  - `python -m ruff format --check .` -> `50 files already formatted`
- Additional owner-reported scanner fixes checked out:
  `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:70-74`
  filters only latest `GO` and `NO-GO`, and
  `Get-ScheduledTask -TaskName AgentRedFileBridgeIndexScan-Claude` reported
  `Hidden=True`.

## Findings

### P1 - SPEC/WI existence checks are still missing

The script stores the first extracted SPEC/WI as primary metadata and links
additional IDs without checking whether those artifacts exist in the Agent Red
KB. Catching exceptions is not sufficient because the GroundTruth relation
helpers do not validate artifact existence.

The temp-DB probe proves this is not hypothetical: with zero specs and zero work
items, apply mode still stored `SPEC-999` and `WI-999` as primary fields,
created relation rows for `SPEC-998` and `WI-998`, and reported zero missing
link IDs.

**Risk/impact:** The backfill can pollute deliberation traceability with IDs
that are not real current KB artifacts. That defeats the earlier no-phantom-link
condition and can make future `get_deliberations_for_spec()` /
`get_deliberations_for_work_item()` queries look authoritative when they are
only string matches from old reports.

**Required action:** Before upsert/linking, resolve extracted IDs against the
target KB. Only set `spec_id` and `work_item_id` when the ID exists. Link only
existing additional IDs. Report missing referenced IDs by exact ID and source
file; do not rely on link-helper exceptions.

### P1 - Apply summary counts are not auditable

The action classifier runs after the upsert and uses the returned row's hash and
version to decide whether a row was created, skipped, or changed. That cannot
distinguish a new row from an existing same-content row when both are version
1. It also cannot identify same-source changed content because
`upsert_deliberation_source()` creates a new `DELIB-*` row for a different
content hash.

The temp-DB probe produced `created created created` for first import,
same-content rerun, and changed-content same-source import. The apply summaries
reported `Changed source: 0` even though the current deliberation table ended
with two rows for the same `source_ref`.

**Risk/impact:** Operators cannot tell whether `--apply` actually created new
rows, skipped idempotent rows, or added changed-source duplicates. A rerun can
look like new work, and changed source content can be missed entirely.

**Required action:** Classify each file before writing by querying existing
current deliberations for `source_ref`. If none exist, count create. If the
same `content_hash` exists, count skip and avoid relinking. If the same
`source_ref` exists with a different hash, count `same_source_changed_content`
before upsert and report it separately.

### P2 - Apply-mode tests still allow the bugs

The new tests prove that a row can be inserted and that redaction happens, but
they do not enforce the previously required apply-mode contract. The
idempotency test explicitly permits the wrong result, and there are no tests for
existing-ID-only linking, missing-ID reporting, relation table rows, or
changed-source counts.

**Risk/impact:** The suite can stay green while the backfill continues to
create phantom links and inaccurate apply summaries.

**Required action:** Add temp-DB tests that:

1. create known current spec/work-item rows and prove only those are used as
   primary/relation links;
2. reference missing SPEC/WI IDs and prove they are reported but not stored or
   linked;
3. assert same-content reruns return/report `skipped`, not `created`;
4. assert same-source changed content returns/reports
   `same_source_changed_content`;
5. assert relation table rows are created only for existing additional IDs.

## Required Conditions For VERIFIED

1. Implement explicit SPEC/WI existence checks against the target Agent Red KB
   before setting primary IDs or relation links.
2. Replace exception-based missing-link counting with exact missing referenced
   ID reporting.
3. Rework create/skip/same-source-changed classification so apply summaries are
   based on pre-upsert state and are auditable on reruns.
4. Tighten the temp-DB tests to fail on the current `created created created`
   and phantom-link behavior.
5. Re-run the Agent Red unit/lint/format checks, the 648-report dry run, and a
   temp-DB apply probe that demonstrates existing-only links and accurate
   rerun/change-source counts.

## Decision Needed From Owner

No owner decision is needed. This is still an implementation correctness issue
against the approved backfill conditions, not a policy trade-off.
